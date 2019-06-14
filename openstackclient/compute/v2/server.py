#   Copyright 2012-2013 OpenStack Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Compute v2 Server action implementations"""

import argparse
import getpass
import io
import logging
import os

from novaclient import api_versions
from novaclient.v2 import servers
from openstack import exceptions as sdk_exceptions
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import timeutils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common as network_common


LOG = logging.getLogger(__name__)


def _format_servers_list_networks(networks):
    """Return a formatted string of a server's networks

    :param networks: a Server.networks field
    :rtype: a string of formatted network addresses
    """
    output = []
    for (network, addresses) in networks.items():
        if not addresses:
            continue
        addresses_csv = ', '.join(addresses)
        group = "%s=%s" % (network, addresses_csv)
        output.append(group)
    return '; '.join(output)


def _format_servers_list_power_state(state):
    """Return a formatted string of a server's power state

    :param state: the power state number of a server
    :rtype: a string mapped to the power state number
    """
    power_states = [
        'NOSTATE',      # 0x00
        'Running',      # 0x01
        '',             # 0x02
        'Paused',       # 0x03
        'Shutdown',     # 0x04
        '',             # 0x05
        'Crashed',      # 0x06
        'Suspended'     # 0x07
    ]

    try:
        return power_states[state]
    except Exception:
        return 'N/A'


def _get_ip_address(addresses, address_type, ip_address_family):
    # Old style addresses
    if address_type in addresses:
        for addy in addresses[address_type]:
            if int(addy['version']) in ip_address_family:
                return addy['addr']

    # New style addresses
    new_address_type = address_type
    if address_type == 'public':
        new_address_type = 'floating'
    if address_type == 'private':
        new_address_type = 'fixed'
    for network in addresses:
        for addy in addresses[network]:
            # Case where it is list of strings
            if isinstance(addy, six.string_types):
                if new_address_type == 'fixed':
                    return addresses[network][0]
                else:
                    return addresses[network][-1]
            # Case where it is a dict
            if 'OS-EXT-IPS:type' not in addy:
                continue
            if addy['OS-EXT-IPS:type'] == new_address_type:
                if int(addy['version']) in ip_address_family:
                    return addy['addr']
    msg = _("ERROR: No %(type)s IP version %(family)s address found")
    raise exceptions.CommandError(
        msg % {"type": address_type,
               "family": ip_address_family}
    )


def _prefix_checked_value(prefix):
    def func(value):
        if ',' in value or '=' in value:
            msg = _("Invalid argument %s, "
                    "characters ',' and '=' are not allowed") % value
            raise argparse.ArgumentTypeError(msg)
        return prefix + value
    return func


def _prep_server_detail(compute_client, image_client, server, refresh=True):
    """Prepare the detailed server dict for printing

    :param compute_client: a compute client instance
    :param image_client: an image client instance
    :param server: a Server resource
    :param refresh: Flag indicating if ``server`` is already the latest version
                    or if it needs to be refreshed, for example when showing
                    the latest details of a server after creating it.
    :rtype: a dict of server details
    """
    info = server.to_dict()
    if refresh:
        server = utils.find_resource(compute_client.servers, info['id'])
        info.update(server.to_dict())

    # Convert the image blob to a name
    image_info = info.get('image', {})
    if image_info:
        image_id = image_info.get('id', '')
        try:
            image = utils.find_resource(image_client.images, image_id)
            info['image'] = "%s (%s)" % (image.name, image_id)
        except Exception:
            info['image'] = image_id

    # Convert the flavor blob to a name
    flavor_info = info.get('flavor', {})
    # Microversion 2.47 puts the embedded flavor into the server response
    # body but omits the id, so if not present we just expose the flavor
    # dict in the server output.
    if 'id' in flavor_info:
        flavor_id = flavor_info.get('id', '')
        try:
            flavor = utils.find_resource(compute_client.flavors, flavor_id)
            info['flavor'] = "%s (%s)" % (flavor.name, flavor_id)
        except Exception:
            info['flavor'] = flavor_id
    else:
        info['flavor'] = utils.format_dict(flavor_info)

    if 'os-extended-volumes:volumes_attached' in info:
        info.update(
            {
                'volumes_attached': utils.format_list_of_dicts(
                    info.pop('os-extended-volumes:volumes_attached'))
            }
        )
    if 'security_groups' in info:
        info.update(
            {
                'security_groups': utils.format_list_of_dicts(
                    info.pop('security_groups'))
            }
        )
    # NOTE(dtroyer): novaclient splits these into separate entries...
    # Format addresses in a useful way
    info['addresses'] = _format_servers_list_networks(server.networks)

    # Map 'metadata' field to 'properties'
    info.update(
        {'properties': utils.format_dict(info.pop('metadata'))}
    )

    # Migrate tenant_id to project_id naming
    if 'tenant_id' in info:
        info['project_id'] = info.pop('tenant_id')

    # Map power state num to meaningful string
    if 'OS-EXT-STS:power_state' in info:
        info['OS-EXT-STS:power_state'] = _format_servers_list_power_state(
            info['OS-EXT-STS:power_state'])

    # Remove values that are long and not too useful
    info.pop('links', None)

    return info


class AddFixedIP(command.Command):
    _description = _("Add fixed IP address to server")

    def get_parser(self, prog_name):
        parser = super(AddFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to receive the fixed IP address (name or ID)"),
        )
        parser.add_argument(
            "network",
            metavar="<network>",
            help=_(
                "Network to allocate the fixed IP address from (name or ID)"
            ),
        )
        parser.add_argument(
            "--fixed-ip-address",
            metavar="<ip-address>",
            help=_("Requested fixed IP address"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        network = compute_client.api.network_find(parsed_args.network)

        server.interface_attach(
            port_id=None,
            net_id=network['id'],
            fixed_ip=parsed_args.fixed_ip_address,
        )


class AddFloatingIP(network_common.NetworkAndComputeCommand):
    _description = _("Add floating IP address to server")

    def update_parser_common(self, parser):
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to receive the floating IP address (name or ID)"),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Floating IP address to assign to the first available "
                   "server port (IP only)"),
        )
        parser.add_argument(
            "--fixed-ip-address",
            metavar="<ip-address>",
            help=_(
                "Fixed IP address to associate with this floating IP address. "
                "The first server port containing the fixed IP address will "
                "be used"
            ),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        compute_client = self.app.client_manager.compute

        attrs = {}
        obj = client.find_ip(
            parsed_args.ip_address,
            ignore_missing=False,
        )
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        ports = list(client.ports(device_id=server.id))
        # If the fixed IP address was specified, we need to find the
        # corresponding port.
        if parsed_args.fixed_ip_address:
            fip_address = parsed_args.fixed_ip_address
            attrs['fixed_ip_address'] = fip_address
            for port in ports:
                for ip in port.fixed_ips:
                    if ip['ip_address'] == fip_address:
                        attrs['port_id'] = port.id
                        break
                else:
                    continue
                break
            if 'port_id' not in attrs:
                msg = _('No port found for fixed IP address %s')
                raise exceptions.CommandError(msg % fip_address)
            client.update_ip(obj, **attrs)
        else:
            # It's possible that one or more ports are not connected to a
            # router and thus could fail association with a floating IP.
            # Try each port until one succeeds. If none succeed, re-raise the
            # last exception.
            error = None
            for port in ports:
                attrs['port_id'] = port.id
                try:
                    client.update_ip(obj, **attrs)
                except sdk_exceptions.NotFoundException as exp:
                    # 404 ExternalGatewayForFloatingIPNotFound from neutron
                    LOG.info('Skipped port %s because it is not attached to '
                             'an external gateway', port.id)
                    error = exp
                    continue
                else:
                    error = None
                    break
            if error:
                raise error

    def take_action_compute(self, client, parsed_args):
        client.api.floating_ip_add(
            parsed_args.server,
            parsed_args.ip_address,
            fixed_address=parsed_args.fixed_ip_address,
        )


class AddPort(command.Command):
    _description = _("Add port to server")

    def get_parser(self, prog_name):
        parser = super(AddPort, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to add the port to (name or ID)"),
        )
        parser.add_argument(
            "port",
            metavar="<port>",
            help=_("Port to add to the server (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            port_id = network_client.find_port(
                parsed_args.port, ignore_missing=False).id
        else:
            port_id = parsed_args.port

        server.interface_attach(port_id=port_id, net_id=None, fixed_ip=None)


class AddNetwork(command.Command):
    _description = _("Add network to server")

    def get_parser(self, prog_name):
        parser = super(AddNetwork, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to add the network to (name or ID)"),
        )
        parser.add_argument(
            "network",
            metavar="<network>",
            help=_("Network to add to the server (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            net_id = network_client.find_network(
                parsed_args.network, ignore_missing=False).id
        else:
            net_id = parsed_args.network

        server.interface_attach(port_id=None, net_id=net_id, fixed_ip=None)


class AddServerSecurityGroup(command.Command):
    _description = _("Add security group to server")

    def get_parser(self, prog_name):
        parser = super(AddServerSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Security group to add (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        security_group = compute_client.api.security_group_find(
            parsed_args.group,
        )

        server.add_security_group(security_group['id'])


class AddServerVolume(command.Command):
    _description = _(
        "Add volume to server. "
        "Specify ``--os-compute-api-version 2.20`` or higher to add a volume "
        "to a server with status ``SHELVED`` or ``SHELVED_OFFLOADED``.")

    def get_parser(self, prog_name):
        parser = super(AddServerVolume, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to add (name or ID)'),
        )
        parser.add_argument(
            '--device',
            metavar='<device>',
            help=_('Server internal device name for volume'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        volume = utils.find_resource(
            volume_client.volumes,
            parsed_args.volume,
        )

        compute_client.volumes.create_server_volume(
            server.id,
            volume.id,
            parsed_args.device,
        )


class CreateServer(command.ShowOne):
    _description = _("Create a new server")

    def get_parser(self, prog_name):
        parser = super(CreateServer, self).get_parser(prog_name)
        parser.add_argument(
            'server_name',
            metavar='<server-name>',
            help=_('New server name'),
        )
        disk_group = parser.add_mutually_exclusive_group(
            required=True,
        )
        disk_group.add_argument(
            '--image',
            metavar='<image>',
            help=_('Create server boot disk from this image (name or ID)'),
        )
        disk_group.add_argument(
            '--image-property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_("Image property to be matched"),
        )
        disk_group.add_argument(
            '--volume',
            metavar='<volume>',
            help=_('Create server using this volume as the boot disk (name '
                   'or ID).\n'
                   'This option automatically creates a block device mapping '
                   'with a boot index of 0. On many hypervisors (libvirt/kvm '
                   'for example) this will be device vda. Do not create a '
                   'duplicate mapping using --block-device-mapping for this '
                   'volume.'),
        )
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            required=True,
            help=_('Create server with this flavor (name or ID)'),
        )
        parser.add_argument(
            '--security-group',
            metavar='<security-group>',
            action='append',
            default=[],
            help=_('Security group to assign to this server (name or ID) '
                   '(repeat option to set multiple groups)'),
        )
        parser.add_argument(
            '--key-name',
            metavar='<key-name>',
            help=_('Keypair to inject into this server (optional extension)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on this server '
                   '(repeat option to set multiple values)'),
        )
        parser.add_argument(
            '--file',
            metavar='<dest-filename=source-filename>',
            action='append',
            default=[],
            help=_('File to inject into image before boot '
                   '(repeat option to set multiple files)'),
        )
        parser.add_argument(
            '--user-data',
            metavar='<user-data>',
            help=_('User data file to serve from the metadata server'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set description for the server (supported by '
                   '--os-compute-api-version 2.19 or above)'),
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<zone-name>',
            help=_('Select an availability zone for the server'),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_('Requested host to create servers. Admin only '
                   'by default. (supported by --os-compute-api-version 2.74 '
                   'or above)'),
        )
        parser.add_argument(
            '--hypervisor-hostname',
            metavar='<hypervisor-hostname>',
            help=_('Requested hypervisor hostname to create servers. Admin '
                   'only by default. (supported by --os-compute-api-version '
                   '2.74 or above)'),
        )
        parser.add_argument(
            '--boot-from-volume',
            metavar='<volume-size>',
            type=int,
            help=_('When used in conjunction with the ``--image`` or '
                   '``--image-property`` option, this option automatically '
                   'creates a block device mapping with a boot index of 0 '
                   'and tells the compute service to create a volume of the '
                   'given size (in GB) from the specified image and use it '
                   'as the root disk of the server. The root volume will not '
                   'be deleted when the server is deleted. This option is '
                   'mutually exclusive with the ``--volume`` option.')
        )
        parser.add_argument(
            '--block-device-mapping',
            metavar='<dev-name=mapping>',
            action=parseractions.KeyValueAction,
            default={},
            # NOTE(RuiChen): Add '\n' at the end of line to put each item in
            #                the separated line, avoid the help message looks
            #                messy, see _SmartHelpFormatter in cliff.
            help=_('Create a block device on the server.\n'
                   'Block device mapping in the format\n'
                   '<dev-name>=<id>:<type>:<size(GB)>:<delete-on-terminate>\n'
                   '<dev-name>: block device name, like: vdb, xvdc '
                   '(required)\n'
                   '<id>: Name or ID of the volume, volume snapshot or image '
                   '(required)\n'
                   '<type>: volume, snapshot or image; default: volume '
                   '(optional)\n'
                   '<size(GB)>: volume size if create from image or snapshot '
                   '(optional)\n'
                   '<delete-on-terminate>: true or false; default: false '
                   '(optional)\n'
                   '(optional extension)'),
        )
        parser.add_argument(
            '--nic',
            metavar="<net-id=net-uuid,v4-fixed-ip=ip-addr,v6-fixed-ip=ip-addr,"
                    "port-id=port-uuid,auto,none>",
            action='append',
            help=_("Create a NIC on the server. "
                   "Specify option multiple times to create multiple NICs. "
                   "Either net-id or port-id must be provided, but not both. "
                   "net-id: attach NIC to network with this UUID, "
                   "port-id: attach NIC to port with this UUID, "
                   "v4-fixed-ip: IPv4 fixed address for NIC (optional), "
                   "v6-fixed-ip: IPv6 fixed address for NIC (optional), "
                   "none: (v2.37+) no network is attached, "
                   "auto: (v2.37+) the compute service will automatically "
                   "allocate a network. Specifying a --nic of auto or none "
                   "cannot be used with any other --nic value."),
        )
        parser.add_argument(
            '--network',
            metavar="<network>",
            action='append',
            dest='nic',
            type=_prefix_checked_value('net-id='),
            help=_("Create a NIC on the server and connect it to network. "
                   "Specify option multiple times to create multiple NICs. "
                   "This is a wrapper for the '--nic net-id=<network>' "
                   "parameter that provides simple syntax for the standard "
                   "use case of connecting a new server to a given network. "
                   "For more advanced use cases, refer to the '--nic' "
                   "parameter."),
        )
        parser.add_argument(
            '--port',
            metavar="<port>",
            action='append',
            dest='nic',
            type=_prefix_checked_value('port-id='),
            help=_("Create a NIC on the server and connect it to port. "
                   "Specify option multiple times to create multiple NICs. "
                   "This is a wrapper for the '--nic port-id=<port>' "
                   "parameter that provides simple syntax for the standard "
                   "use case of connecting a new server to a given port. For "
                   "more advanced use cases, refer to the '--nic' parameter."),
        )
        parser.add_argument(
            '--hint',
            metavar='<key=value>',
            action='append',
            default=[],
            help=_('Hints for the scheduler (optional extension)'),
        )
        parser.add_argument(
            '--config-drive',
            metavar='<config-drive-volume>|True',
            default=False,
            help=_('Use specified volume as the config drive, '
                   'or \'True\' to use an ephemeral drive'),
        )
        parser.add_argument(
            '--min',
            metavar='<count>',
            type=int,
            default=1,
            help=_('Minimum number of servers to launch (default=1)'),
        )
        parser.add_argument(
            '--max',
            metavar='<count>',
            type=int,
            default=1,
            help=_('Maximum number of servers to launch (default=1)'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for build to complete'),
        )
        return parser

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stdout.write('\rProgress: %s' % progress)
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume
        image_client = self.app.client_manager.image

        # Lookup parsed_args.image
        image = None
        if parsed_args.image:
            image = utils.find_resource(
                image_client.images,
                parsed_args.image,
            )

        if not image and parsed_args.image_property:
            def emit_duplicated_warning(img, image_property):
                img_uuid_list = [str(image.id) for image in img]
                LOG.warning(_('Multiple matching images: %(img_uuid_list)s\n'
                              'Using image: %(chosen_one)s') %
                            {'img_uuid_list': img_uuid_list,
                             'chosen_one': img_uuid_list[0]})

            def _match_image(image_api, wanted_properties):
                image_list = image_api.image_list()
                images_matched = []
                for img in image_list:
                    img_dict = {}
                    # exclude any unhashable entries
                    for key, value in img.items():
                        try:
                            set([key, value])
                        except TypeError:
                            pass
                        else:
                            img_dict[key] = value
                    if all(k in img_dict and img_dict[k] == v
                           for k, v in wanted_properties.items()):
                        images_matched.append(img)
                    else:
                        return []
                return images_matched

            images = _match_image(image_client.api, parsed_args.image_property)
            if len(images) > 1:
                emit_duplicated_warning(images,
                                        parsed_args.image_property)
            if images:
                image = images[0]
            else:
                raise exceptions.CommandError(_("No images match the "
                                                "property expected by "
                                                "--image-property"))

        # Lookup parsed_args.volume
        volume = None
        if parsed_args.volume:
            # --volume and --boot-from-volume are mutually exclusive.
            if parsed_args.boot_from_volume:
                raise exceptions.CommandError(
                    _('--volume is not allowed with --boot-from-volume'))
            volume = utils.find_resource(
                volume_client.volumes,
                parsed_args.volume,
            ).id

        # Lookup parsed_args.flavor
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)

        files = {}
        for f in parsed_args.file:
            dst, src = f.split('=', 1)
            try:
                files[dst] = io.open(src, 'rb')
            except IOError as e:
                msg = _("Can't open '%(source)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {"source": src,
                           "exception": e}
                )

        if parsed_args.min > parsed_args.max:
            msg = _("min instances should be <= max instances")
            raise exceptions.CommandError(msg)
        if parsed_args.min < 1:
            msg = _("min instances should be > 0")
            raise exceptions.CommandError(msg)
        if parsed_args.max < 1:
            msg = _("max instances should be > 0")
            raise exceptions.CommandError(msg)

        userdata = None
        if parsed_args.user_data:
            try:
                userdata = io.open(parsed_args.user_data)
            except IOError as e:
                msg = _("Can't open '%(data)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {"data": parsed_args.user_data,
                           "exception": e}
                )

        if parsed_args.description:
            if compute_client.api_version < api_versions.APIVersion("2.19"):
                msg = _("Description is not supported for "
                        "--os-compute-api-version less than 2.19")
                raise exceptions.CommandError(msg)

        block_device_mapping_v2 = []
        if volume:
            block_device_mapping_v2 = [{'uuid': volume,
                                        'boot_index': '0',
                                        'source_type': 'volume',
                                        'destination_type': 'volume'
                                        }]
        elif parsed_args.boot_from_volume:
            # Tell nova to create a root volume from the image provided.
            block_device_mapping_v2 = [{
                'uuid': image.id,
                'boot_index': '0',
                'source_type': 'image',
                'destination_type': 'volume',
                'volume_size': parsed_args.boot_from_volume
            }]
            # If booting from volume we do not pass an image to compute.
            image = None

        boot_args = [parsed_args.server_name, image, flavor]

        # Handle block device by device name order, like: vdb -> vdc -> vdd
        for dev_name in sorted(six.iterkeys(parsed_args.block_device_mapping)):
            dev_map = parsed_args.block_device_mapping[dev_name]
            dev_map = dev_map.split(':')
            if dev_map[0]:
                mapping = {'device_name': dev_name}
                # 1. decide source and destination type
                if (len(dev_map) > 1 and
                        dev_map[1] in ('volume', 'snapshot', 'image')):
                    mapping['source_type'] = dev_map[1]
                else:
                    mapping['source_type'] = 'volume'
                mapping['destination_type'] = 'volume'
                # 2. check target exist, update target uuid according by
                #    source type
                if mapping['source_type'] == 'volume':
                    volume_id = utils.find_resource(
                        volume_client.volumes, dev_map[0]).id
                    mapping['uuid'] = volume_id
                elif mapping['source_type'] == 'snapshot':
                    snapshot_id = utils.find_resource(
                        volume_client.volume_snapshots, dev_map[0]).id
                    mapping['uuid'] = snapshot_id
                elif mapping['source_type'] == 'image':
                    # NOTE(mriedem): In case --image is specified with the same
                    # image, that becomes the root disk for the server. If the
                    # block device is specified with a root device name, e.g.
                    # vda, then the compute API will likely fail complaining
                    # that there is a conflict. So if using the same image ID,
                    # which doesn't really make sense but it's allowed, the
                    # device name would need to be a non-root device, e.g. vdb.
                    # Otherwise if the block device image is different from the
                    # one specified by --image, then the compute service will
                    # create a volume from the image and attach it to the
                    # server as a non-root volume.
                    image_id = utils.find_resource(
                        image_client.images, dev_map[0]).id
                    mapping['uuid'] = image_id
                # 3. append size and delete_on_termination if exist
                if len(dev_map) > 2 and dev_map[2]:
                    mapping['volume_size'] = dev_map[2]
                if len(dev_map) > 3 and dev_map[3]:
                    mapping['delete_on_termination'] = dev_map[3]
            else:
                msg = _("Volume, volume snapshot or image (name or ID) must "
                        "be specified if --block-device-mapping is specified")
                raise exceptions.CommandError(msg)
            block_device_mapping_v2.append(mapping)

        nics = []
        auto_or_none = False
        if parsed_args.nic is None:
            parsed_args.nic = []
        for nic_str in parsed_args.nic:
            # Handle the special auto/none cases
            if nic_str in ('auto', 'none'):
                auto_or_none = True
                nics.append(nic_str)
            else:
                nic_info = {"net-id": "", "v4-fixed-ip": "",
                            "v6-fixed-ip": "", "port-id": ""}
                for kv_str in nic_str.split(","):
                    k, sep, v = kv_str.partition("=")
                    if k in nic_info and v:
                        nic_info[k] = v
                    else:
                        msg = (_("Invalid nic argument '%s'. Nic arguments "
                                 "must be of the form --nic <net-id=net-uuid"
                                 ",v4-fixed-ip=ip-addr,v6-fixed-ip=ip-addr,"
                                 "port-id=port-uuid>."))
                        raise exceptions.CommandError(msg % k)
                if bool(nic_info["net-id"]) == bool(nic_info["port-id"]):
                    msg = _("either network or port should be specified "
                            "but not both")
                    raise exceptions.CommandError(msg)
                if self.app.client_manager.is_network_endpoint_enabled():
                    network_client = self.app.client_manager.network
                    if nic_info["net-id"]:
                        net = network_client.find_network(
                            nic_info["net-id"], ignore_missing=False)
                        nic_info["net-id"] = net.id
                    if nic_info["port-id"]:
                        port = network_client.find_port(
                            nic_info["port-id"], ignore_missing=False)
                        nic_info["port-id"] = port.id
                else:
                    if nic_info["net-id"]:
                        nic_info["net-id"] = compute_client.api.network_find(
                            nic_info["net-id"]
                        )['id']
                    if nic_info["port-id"]:
                        msg = _("can't create server with port specified "
                                "since network endpoint not enabled")
                        raise exceptions.CommandError(msg)
                nics.append(nic_info)

        if nics:
            if auto_or_none:
                if len(nics) > 1:
                    msg = _('Specifying a --nic of auto or none cannot '
                            'be used with any other --nic, --network '
                            'or --port value.')
                    raise exceptions.CommandError(msg)
                nics = nics[0]
        else:
            # Compute API version >= 2.37 requires a value, so default to
            # 'auto' to maintain legacy behavior if a nic wasn't specified.
            if compute_client.api_version >= api_versions.APIVersion('2.37'):
                nics = 'auto'
            else:
                # Default to empty list if nothing was specified, let nova
                # side to decide the default behavior.
                nics = []

        # Check security group exist and convert ID to name
        security_group_names = []
        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            for each_sg in parsed_args.security_group:
                sg = network_client.find_security_group(each_sg,
                                                        ignore_missing=False)
                # Use security group ID to avoid multiple security group have
                # same name in neutron networking backend
                security_group_names.append(sg.id)
        else:
            # Handle nova-network case
            for each_sg in parsed_args.security_group:
                sg = compute_client.api.security_group_find(each_sg)
                security_group_names.append(sg['name'])

        hints = {}
        for hint in parsed_args.hint:
            key, _sep, value = hint.partition('=')
            # NOTE(vish): multiple copies of the same hint will
            #             result in a list of values
            if key in hints:
                if isinstance(hints[key], six.string_types):
                    hints[key] = [hints[key]]
                hints[key] += [value]
            else:
                hints[key] = value

        # What does a non-boolean value for config-drive do?
        # --config-drive argument is either a volume id or
        # 'True' (or '1') to use an ephemeral volume
        if str(parsed_args.config_drive).lower() in ("true", "1"):
            config_drive = True
        elif str(parsed_args.config_drive).lower() in ("false", "0",
                                                       "", "none"):
            config_drive = None
        else:
            config_drive = parsed_args.config_drive

        boot_kwargs = dict(
            meta=parsed_args.property,
            files=files,
            reservation_id=None,
            min_count=parsed_args.min,
            max_count=parsed_args.max,
            security_groups=security_group_names,
            userdata=userdata,
            key_name=parsed_args.key_name,
            availability_zone=parsed_args.availability_zone,
            block_device_mapping_v2=block_device_mapping_v2,
            nics=nics,
            scheduler_hints=hints,
            config_drive=config_drive)

        if parsed_args.description:
            boot_kwargs['description'] = parsed_args.description

        if parsed_args.host:
            if compute_client.api_version < api_versions.APIVersion("2.74"):
                msg = _("Specifying --host is not supported for "
                        "--os-compute-api-version less than 2.74")
                raise exceptions.CommandError(msg)
            boot_kwargs['host'] = parsed_args.host

        if parsed_args.hypervisor_hostname:
            if compute_client.api_version < api_versions.APIVersion("2.74"):
                msg = _("Specifying --hypervisor-hostname is not supported "
                        "for --os-compute-api-version less than 2.74")
                raise exceptions.CommandError(msg)
            boot_kwargs['hypervisor_hostname'] = (
                parsed_args.hypervisor_hostname)

        LOG.debug('boot_args: %s', boot_args)
        LOG.debug('boot_kwargs: %s', boot_kwargs)

        # Wrap the call to catch exceptions in order to close files
        try:
            server = compute_client.servers.create(*boot_args, **boot_kwargs)
        finally:
            # Clean up open files - make sure they are not strings
            for f in files:
                if hasattr(f, 'close'):
                    f.close()
            if hasattr(userdata, 'close'):
                userdata.close()

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                self.app.stdout.write('\n')
            else:
                LOG.error(_('Error creating server: %s'),
                          parsed_args.server_name)
                self.app.stdout.write(_('Error creating server\n'))
                raise SystemExit

        details = _prep_server_detail(compute_client, image_client, server)
        return zip(*sorted(six.iteritems(details)))


class CreateServerDump(command.Command):
    """Create a dump file in server(s)

    Trigger crash dump in server(s) with features like kdump in Linux.
    It will create a dump file in the server(s) dumping the server(s)'
    memory, and also crash the server(s). OSC sees the dump file
    (server dump) as a kind of resource.

    This command requires ``--os-compute-api-version`` 2.17 or greater.
    """

    def get_parser(self, prog_name):
        parser = super(CreateServerDump, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to create dump file (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).trigger_crash_dump()


class DeleteServer(command.Command):
    _description = _("Delete server(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs="+",
            help=_('Server(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for delete to complete'),
        )
        return parser

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stdout.write('\rProgress: %s' % progress)
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            server_obj = utils.find_resource(
                compute_client.servers, server)
            compute_client.servers.delete(server_obj.id)
            if parsed_args.wait:
                if not utils.wait_for_delete(compute_client.servers,
                                             server_obj.id,
                                             callback=_show_progress):
                    LOG.error(_('Error deleting server: %s'),
                              server_obj.id)
                    self.app.stdout.write(_('Error deleting server\n'))
                    raise SystemExit


class ListServer(command.Lister):
    _description = _("List servers")

    def get_parser(self, prog_name):
        parser = super(ListServer, self).get_parser(prog_name)
        parser.add_argument(
            '--reservation-id',
            metavar='<reservation-id>',
            help=_('Only return instances that match the reservation'),
        )
        parser.add_argument(
            '--ip',
            metavar='<ip-address-regex>',
            help=_('Regular expression to match IP addresses'),
        )
        parser.add_argument(
            '--ip6',
            metavar='<ip-address-regex>',
            help=_('Regular expression to match IPv6 addresses. Note '
                   'that this option only applies for non-admin users '
                   'when using ``--os-compute-api-version`` 2.5 or greater.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name-regex>',
            help=_('Regular expression to match names'),
        )
        parser.add_argument(
            '--instance-name',
            metavar='<server-name>',
            help=_('Regular expression to match instance name (admin only)'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            # FIXME(dhellmann): Add choices?
            help=_('Search by server status'),
        )
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            help=_('Search by flavor (name or ID)'),
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_('Search by image (name or ID)'),
        )
        parser.add_argument(
            '--host',
            metavar='<hostname>',
            help=_('Search by hostname'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=bool(int(os.environ.get("ALL_PROJECTS", 0))),
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Search by project (admin only) (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Search by user (admin only) (name or ID)'),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        name_lookup_group = parser.add_mutually_exclusive_group()
        name_lookup_group.add_argument(
            '-n', '--no-name-lookup',
            action='store_true',
            default=False,
            help=_('Skip flavor and image name lookup.'
                   'Mutually exclusive with "--name-lookup-one-by-one"'
                   ' option.'),
        )
        name_lookup_group.add_argument(
            '--name-lookup-one-by-one',
            action='store_true',
            default=False,
            help=_('When looking up flavor and image names, look them up'
                   'one by one as needed instead of all together (default). '
                   'Mutually exclusive with "--no-name-lookup|-n" option.'),
        )
        parser.add_argument(
            '--marker',
            metavar='<server>',
            default=None,
            help=_('The last server of the previous page. Display '
                   'list of servers after marker. Display all servers if not '
                   'specified. (name or ID)')
        )
        parser.add_argument(
            '--limit',
            metavar='<num-servers>',
            type=int,
            default=None,
            help=_("Maximum number of servers to display. If limit equals -1, "
                   "all servers will be displayed. If limit is greater than "
                   "'osapi_max_limit' option of Nova API, "
                   "'osapi_max_limit' will be used instead."),
        )
        parser.add_argument(
            '--deleted',
            action="store_true",
            default=False,
            help=_('Only display deleted servers (Admin only).')
        )
        parser.add_argument(
            '--changes-before',
            metavar='<changes-before>',
            default=None,
            help=_("List only servers changed before a certain point of time. "
                   "The provided time should be an ISO 8061 formatted time "
                   "(e.g., 2016-03-05T06:27:59Z). "
                   "(Supported by API versions '2.66' - '2.latest')")
        )
        parser.add_argument(
            '--changes-since',
            metavar='<changes-since>',
            default=None,
            help=_("List only servers changed after a certain point of time."
                   " The provided time should be an ISO 8061 formatted time"
                   " (e.g., 2016-03-04T06:27:59Z).")
        )
        lock_group = parser.add_mutually_exclusive_group()
        lock_group.add_argument(
            '--locked',
            action='store_true',
            default=False,
            help=_('Only display locked servers. '
                   'Requires ``--os-compute-api-version`` 2.73 or greater.'),
        )
        lock_group.add_argument(
            '--unlocked',
            action='store_true',
            default=False,
            help=_('Only display unlocked servers. '
                   'Requires ``--os-compute-api-version`` 2.73 or greater.'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            parsed_args.all_projects = True

        user_id = None
        if parsed_args.user:
            user_id = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id

        # Nova only supports list servers searching by flavor ID. So if a
        # flavor name is given, map it to ID.
        flavor_id = None
        if parsed_args.flavor:
            flavor_id = utils.find_resource(compute_client.flavors,
                                            parsed_args.flavor).id

        # Nova only supports list servers searching by image ID. So if a
        # image name is given, map it to ID.
        image_id = None
        if parsed_args.image:
            image_id = utils.find_resource(image_client.images,
                                           parsed_args.image).id

        search_opts = {
            'reservation_id': parsed_args.reservation_id,
            'ip': parsed_args.ip,
            'ip6': parsed_args.ip6,
            'name': parsed_args.name,
            'instance_name': parsed_args.instance_name,
            'status': parsed_args.status,
            'flavor': flavor_id,
            'image': image_id,
            'host': parsed_args.host,
            'tenant_id': project_id,
            'all_tenants': parsed_args.all_projects,
            'user_id': user_id,
            'deleted': parsed_args.deleted,
            'changes-before': parsed_args.changes_before,
            'changes-since': parsed_args.changes_since,
        }
        support_locked = (compute_client.api_version >=
                          api_versions.APIVersion('2.73'))
        if not support_locked and (parsed_args.locked or parsed_args.unlocked):
            msg = _('--os-compute-api-version 2.73 or greater is required to '
                    'use the (un)locked filter option.')
            raise exceptions.CommandError(msg)
        elif support_locked:
            # Only from 2.73.
            if parsed_args.locked:
                search_opts['locked'] = True
            if parsed_args.unlocked:
                search_opts['locked'] = False
        LOG.debug('search options: %s', search_opts)

        if search_opts['changes-before']:
            if compute_client.api_version < api_versions.APIVersion('2.66'):
                msg = _('--os-compute-api-version 2.66 or later is required')
                raise exceptions.CommandError(msg)

            try:
                timeutils.parse_isotime(search_opts['changes-before'])
            except ValueError:
                raise exceptions.CommandError(
                    _('Invalid changes-before value: %s') %
                    search_opts['changes-before']
                )

        if search_opts['changes-since']:
            try:
                timeutils.parse_isotime(search_opts['changes-since'])
            except ValueError:
                raise exceptions.CommandError(
                    _('Invalid changes-since value: %s') %
                    search_opts['changes-since']
                )

        if parsed_args.long:
            columns = (
                'ID',
                'Name',
                'Status',
                'OS-EXT-STS:task_state',
                'OS-EXT-STS:power_state',
                'Networks',
                'Image Name',
                'Image ID',
                'Flavor Name',
                'Flavor ID',
                'OS-EXT-AZ:availability_zone',
                'OS-EXT-SRV-ATTR:host',
                'Metadata',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Task State',
                'Power State',
                'Networks',
                'Image Name',
                'Image ID',
                'Flavor Name',
                'Flavor ID',
                'Availability Zone',
                'Host',
                'Properties',
            )
            mixed_case_fields = [
                'OS-EXT-STS:task_state',
                'OS-EXT-STS:power_state',
                'OS-EXT-AZ:availability_zone',
                'OS-EXT-SRV-ATTR:host',
            ]
        else:
            if parsed_args.no_name_lookup:
                columns = (
                    'ID',
                    'Name',
                    'Status',
                    'Networks',
                    'Image ID',
                    'Flavor ID',
                )
            else:
                columns = (
                    'ID',
                    'Name',
                    'Status',
                    'Networks',
                    'Image Name',
                    'Flavor Name',
                )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Networks',
                'Image',
                'Flavor',
            )
            mixed_case_fields = []

        marker_id = None
        if parsed_args.marker:
            marker_id = utils.find_resource(compute_client.servers,
                                            parsed_args.marker).id

        data = compute_client.servers.list(search_opts=search_opts,
                                           marker=marker_id,
                                           limit=parsed_args.limit)

        images = {}
        flavors = {}
        if data and not parsed_args.no_name_lookup:
            # Create a dict that maps image_id to image object.
            # Needed so that we can display the "Image Name" column.
            # "Image Name" is not crucial, so we swallow any exceptions.
            # The 'image' attribute can be an empty string if the server was
            # booted from a volume.
            if parsed_args.name_lookup_one_by_one or image_id:
                for i_id in set(filter(lambda x: x is not None,
                                       (s.image.get('id') for s in data
                                        if s.image))):
                    try:
                        images[i_id] = image_client.images.get(i_id)
                    except Exception:
                        pass
            else:
                try:
                    images_list = image_client.images.list()
                    for i in images_list:
                        images[i.id] = i
                except Exception:
                    pass

            # Create a dict that maps flavor_id to flavor object.
            # Needed so that we can display the "Flavor Name" column.
            # "Flavor Name" is not crucial, so we swallow any exceptions.
            if parsed_args.name_lookup_one_by_one or flavor_id:
                for f_id in set(filter(lambda x: x is not None,
                                       (s.flavor.get('id') for s in data))):
                    try:
                        flavors[f_id] = compute_client.flavors.get(f_id)
                    except Exception:
                        pass
            else:
                try:
                    flavors_list = compute_client.flavors.list(is_public=None)
                    for i in flavors_list:
                        flavors[i.id] = i
                except Exception:
                    pass

        # Populate image_name, image_id, flavor_name and flavor_id attributes
        # of server objects so that we can display those columns.
        for s in data:
            if compute_client.api_version >= api_versions.APIVersion('2.69'):
                # NOTE(tssurya): From 2.69, we will have the keys 'flavor'
                # and 'image' missing in the server response during
                # infrastructure failure situations.
                # For those servers with partial constructs we just skip the
                # processing of the image and flavor informations.
                if not hasattr(s, 'image') or not hasattr(s, 'flavor'):
                    continue
            if 'id' in s.image:
                image = images.get(s.image['id'])
                if image:
                    s.image_name = image.name
                s.image_id = s.image['id']
            else:
                s.image_name = ''
                s.image_id = ''
            if 'id' in s.flavor:
                flavor = flavors.get(s.flavor['id'])
                if flavor:
                    s.flavor_name = flavor.name
                s.flavor_id = s.flavor['id']
            else:
                # TODO(mriedem): Fix this for microversion >= 2.47 where the
                # flavor is embedded in the server response without the id.
                # We likely need to drop the Flavor ID column in that case if
                # --long is specified.
                s.flavor_name = ''
                s.flavor_id = ''

        table = (column_headers,
                 (utils.get_item_properties(
                     s, columns,
                     mixed_case_fields=mixed_case_fields,
                     formatters={
                         'OS-EXT-STS:power_state':
                             _format_servers_list_power_state,
                         'Networks': _format_servers_list_networks,
                         'Metadata': utils.format_dict,
                     },
                 ) for s in data))
        return table


class LockServer(command.Command):

    _description = _("Lock server(s). A non-admin user will not be able to "
                     "execute actions")

    def get_parser(self, prog_name):
        parser = super(LockServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to lock (name or ID)'),
        )
        parser.add_argument(
            '--reason',
            metavar='<reason>',
            default=None,
            help=_("Reason for locking the server(s). Requires "
                   "``--os-compute-api-version`` 2.73 or greater.")
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        support_reason = compute_client.api_version >= api_versions.APIVersion(
            '2.73')
        if not support_reason and parsed_args.reason:
            msg = _('--os-compute-api-version 2.73 or greater is required to '
                    'use the --reason option.')
            raise exceptions.CommandError(msg)
        for server in parsed_args.server:
            serv = utils.find_resource(compute_client.servers, server)
            (serv.lock(reason=parsed_args.reason) if support_reason
                else serv.lock())


# FIXME(dtroyer): Here is what I want, how with argparse/cliff?
# server migrate [--wait] \
#   [--live <hostname>
#     [--shared-migration | --block-migration]
#     [--disk-overcommit | --no-disk-overcommit]]
#   <server>
#
# live_parser = parser.add_argument_group(title='Live migration options')
# then adding the groups doesn't seem to work

class MigrateServer(command.Command):
    _description = _("Migrate server to different host")

    def get_parser(self, prog_name):
        parser = super(MigrateServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--live-migration',
            dest='live_migration',
            action='store_true',
            help=_('Live migrate the server. Use the ``--host`` option to '
                   'specify a target host for the migration which will be '
                   'validated by the scheduler.'),
        )
        # The --live and --host options are mutually exclusive ways of asking
        # for a target host during a live migration.
        host_group = parser.add_mutually_exclusive_group()
        # TODO(mriedem): Remove --live in the next major version bump after
        #  the Train release.
        host_group.add_argument(
            '--live',
            metavar='<hostname>',
            help=_('**Deprecated** This option is problematic in that it '
                   'requires a host and prior to compute API version 2.30, '
                   'specifying a host during live migration will bypass '
                   'validation by the scheduler which could result in '
                   'failures to actually migrate the server to the specified '
                   'host or over-subscribe the host. Use the '
                   '``--live-migration`` option instead. If both this option '
                   'and ``--live-migration`` are used, ``--live-migration`` '
                   'takes priority.'),
        )
        host_group.add_argument(
            '--host',
            metavar='<hostname>',
            help=_('Migrate the server to the specified host. Requires '
                   '``--os-compute-api-version`` 2.30 or greater when used '
                   'with the ``--live-migration`` option, otherwise requires '
                   '``--os-compute-api-version`` 2.56 or greater.'),
        )
        migration_group = parser.add_mutually_exclusive_group()
        migration_group.add_argument(
            '--shared-migration',
            dest='block_migration',
            action='store_false',
            default=False,
            help=_('Perform a shared live migration (default)'),
        )
        migration_group.add_argument(
            '--block-migration',
            dest='block_migration',
            action='store_true',
            help=_('Perform a block live migration'),
        )
        disk_group = parser.add_mutually_exclusive_group()
        disk_group.add_argument(
            '--disk-overcommit',
            action='store_true',
            default=False,
            help=_('Allow disk over-commit on the destination host'),
        )
        disk_group.add_argument(
            '--no-disk-overcommit',
            dest='disk_overcommit',
            action='store_false',
            default=False,
            help=_('Do not over-commit disk on the'
                   ' destination host (default)'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for migrate to complete'),
        )
        return parser

    def _log_warning_for_live(self, parsed_args):
        if parsed_args.live:
            # NOTE(mriedem): The --live option requires a host and if
            # --os-compute-api-version is less than 2.30 it will forcefully
            # bypass the scheduler which is dangerous.
            self.log.warning(_(
                'The --live option has been deprecated. Please use the '
                '--live-migration option instead.'))

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stdout.write('\rProgress: %s' % progress)
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        # Check for live migration.
        if parsed_args.live or parsed_args.live_migration:
            # Always log a warning if --live is used.
            self._log_warning_for_live(parsed_args)
            kwargs = {
                'block_migration': parsed_args.block_migration
            }
            # Prefer --live-migration over --live if both are specified.
            if parsed_args.live_migration:
                # Technically we could pass a non-None host with
                # --os-compute-api-version < 2.30 but that is the same thing
                # as the --live option bypassing the scheduler which we don't
                # want to support, so if the user is using --live-migration
                # and --host, we want to enforce that they are using version
                # 2.30 or greater.
                if (parsed_args.host and
                        compute_client.api_version <
                        api_versions.APIVersion('2.30')):
                    raise exceptions.CommandError(
                        '--os-compute-api-version 2.30 or greater is required '
                        'when using --host')
                # The host parameter is required in the API even if None.
                kwargs['host'] = parsed_args.host
            else:
                kwargs['host'] = parsed_args.live

            if compute_client.api_version < api_versions.APIVersion('2.25'):
                kwargs['disk_over_commit'] = parsed_args.disk_overcommit
            server.live_migrate(**kwargs)
        else:
            if parsed_args.block_migration or parsed_args.disk_overcommit:
                raise exceptions.CommandError(
                    "--live-migration must be specified if "
                    "--block-migration or --disk-overcommit is "
                    "specified")
            if parsed_args.host:
                if (compute_client.api_version <
                        api_versions.APIVersion('2.56')):
                    msg = _(
                        '--os-compute-api-version 2.56 or greater is '
                        'required to use --host without --live-migration.'
                    )
                    raise exceptions.CommandError(msg)

            kwargs = {'host': parsed_args.host} if parsed_args.host else {}
            server.migrate(**kwargs)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                success_status=['active', 'verify_resize'],
                callback=_show_progress,
            ):
                self.app.stdout.write(_('Complete\n'))
            else:
                LOG.error(_('Error migrating server: %s'),
                          server.id)
                self.app.stdout.write(_('Error migrating server\n'))
                raise SystemExit


class PauseServer(command.Command):
    _description = _("Pause server(s)")

    def get_parser(self, prog_name):
        parser = super(PauseServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to pause (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server
            ).pause()


class RebootServer(command.Command):
    _description = _("Perform a hard or soft server reboot")

    def get_parser(self, prog_name):
        parser = super(RebootServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--hard',
            dest='reboot_type',
            action='store_const',
            const=servers.REBOOT_HARD,
            default=servers.REBOOT_SOFT,
            help=_('Perform a hard reboot'),
        )
        group.add_argument(
            '--soft',
            dest='reboot_type',
            action='store_const',
            const=servers.REBOOT_SOFT,
            default=servers.REBOOT_SOFT,
            help=_('Perform a soft reboot'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for reboot to complete'),
        )
        return parser

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stdout.write('\rProgress: %s' % progress)
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers, parsed_args.server)
        server.reboot(parsed_args.reboot_type)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                self.app.stdout.write(_('Complete\n'))
            else:
                LOG.error(_('Error rebooting server: %s'),
                          server.id)
                self.app.stdout.write(_('Error rebooting server\n'))
                raise SystemExit


class RebuildServer(command.ShowOne):
    _description = _("Rebuild server")

    def get_parser(self, prog_name):
        parser = super(RebuildServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_('Recreate server from the specified image (name or ID).'
                   ' Defaults to the currently used one.'),
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_("Set the password on the rebuilt instance"),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a property on the rebuilt instance '
                   '(repeat option to set multiple values)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New description for the server (supported by '
                   '--os-compute-api-version 2.19 or above'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for rebuild to complete'),
        )
        key_group = parser.add_mutually_exclusive_group()
        key_group.add_argument(
            '--key-name',
            metavar='<key-name>',
            help=_("Set the key name of key pair on the rebuilt instance."
                   " Cannot be specified with the '--key-unset' option."
                   " (Supported by API versions '2.54' - '2.latest')"),
        )
        key_group.add_argument(
            '--key-unset',
            action='store_true',
            default=False,
            help=_("Unset the key name of key pair on the rebuilt instance."
                   " Cannot be specified with the '--key-name' option."
                   " (Supported by API versions '2.54' - '2.latest')"),
        )
        return parser

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stdout.write('\rProgress: %s' % progress)
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        # If parsed_args.image is not set, default to the currently used one.
        image_id = parsed_args.image or server.to_dict().get(
            'image', {}).get('id')
        image = utils.find_resource(image_client.images, image_id)

        kwargs = {}
        if parsed_args.property:
            kwargs['meta'] = parsed_args.property
        if parsed_args.description:
            if server.api_version < api_versions.APIVersion("2.19"):
                msg = _("Description is not supported for "
                        "--os-compute-api-version less than 2.19")
                raise exceptions.CommandError(msg)
            kwargs['description'] = parsed_args.description

        if parsed_args.key_name or parsed_args.key_unset:
            if compute_client.api_version < api_versions.APIVersion('2.54'):
                msg = _('--os-compute-api-version 2.54 or later is required')
                raise exceptions.CommandError(msg)

        if parsed_args.key_unset:
            kwargs['key_name'] = None
        if parsed_args.key_name:
            kwargs['key_name'] = parsed_args.key_name

        server = server.rebuild(image, parsed_args.password, **kwargs)
        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                self.app.stdout.write(_('Complete\n'))
            else:
                LOG.error(_('Error rebuilding server: %s'),
                          server.id)
                self.app.stdout.write(_('Error rebuilding server\n'))
                raise SystemExit

        details = _prep_server_detail(compute_client, image_client, server,
                                      refresh=False)
        return zip(*sorted(six.iteritems(details)))


class RemoveFixedIP(command.Command):
    _description = _("Remove fixed IP address from server")

    def get_parser(self, prog_name):
        parser = super(RemoveFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to remove the fixed IP address from (name or ID)"),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Fixed IP address to remove from the server (IP only)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_fixed_ip(parsed_args.ip_address)


class RemoveFloatingIP(network_common.NetworkAndComputeCommand):
    _description = _("Remove floating IP address from server")

    def update_parser_common(self, parser):
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_(
                "Server to remove the floating IP address from (name or ID)"
            ),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Floating IP address to remove from server (IP only)"),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        attrs = {}
        obj = client.find_ip(
            parsed_args.ip_address,
            ignore_missing=False,
        )
        attrs['port_id'] = None

        client.update_ip(obj, **attrs)

    def take_action_compute(self, client, parsed_args):
        client.api.floating_ip_remove(
            parsed_args.server,
            parsed_args.ip_address,
        )


class RemovePort(command.Command):
    _description = _("Remove port from server")

    def get_parser(self, prog_name):
        parser = super(RemovePort, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to remove the port from (name or ID)"),
        )
        parser.add_argument(
            "port",
            metavar="<port>",
            help=_("Port to remove from the server (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            port_id = network_client.find_port(
                parsed_args.port, ignore_missing=False).id
        else:
            port_id = parsed_args.port

        server.interface_detach(port_id)


class RemoveNetwork(command.Command):
    _description = _("Remove all ports of a network from server")

    def get_parser(self, prog_name):
        parser = super(RemoveNetwork, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to remove the port from (name or ID)"),
        )
        parser.add_argument(
            "network",
            metavar="<network>",
            help=_("Network to remove from the server (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            net_id = network_client.find_network(
                parsed_args.network, ignore_missing=False).id
        else:
            net_id = parsed_args.network

        for inf in server.interface_list():
            if inf.net_id == net_id:
                server.interface_detach(inf.port_id)


class RemoveServerSecurityGroup(command.Command):
    _description = _("Remove security group from server")

    def get_parser(self, prog_name):
        parser = super(RemoveServerSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Name or ID of server to use'),
        )
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Name or ID of security group to remove from server'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        security_group = compute_client.api.security_group_find(
            parsed_args.group,
        )

        server.remove_security_group(security_group['id'])


class RemoveServerVolume(command.Command):
    _description = _(
        "Remove volume from server. "
        "Specify ``--os-compute-api-version 2.20`` or higher to remove a "
        "volume from a server with status ``SHELVED`` or "
        "``SHELVED_OFFLOADED``.")

    def get_parser(self, prog_name):
        parser = super(RemoveServerVolume, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to remove (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        volume = utils.find_resource(
            volume_client.volumes,
            parsed_args.volume,
        )

        compute_client.volumes.delete_server_volume(
            server.id,
            volume.id,
        )


class RescueServer(command.Command):
    _description = _("Put server in rescue mode")

    def get_parser(self, prog_name):
        parser = super(RescueServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_('Image (name or ID) to use for the rescue mode.'
                   ' Defaults to the currently used one.'),
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_("Set the password on the rescued instance"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        image = None
        if parsed_args.image:
            image = utils.find_resource(
                image_client.images,
                parsed_args.image,
            )

        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).rescue(image=image,
                 password=parsed_args.password)


class ResizeServer(command.Command):
    _description = _("""Scale server to a new flavor.

A resize operation is implemented by creating a new server and copying the
contents of the original disk into a new one. It is also a two-step process for
the user: the first is to perform the resize, the second is to either confirm
(verify) success and release the old server, or to declare a revert to release
the new server and restart the old one.""")

    def get_parser(self, prog_name):
        parser = super(ResizeServer, self).get_parser(prog_name)
        phase_group = parser.add_mutually_exclusive_group()
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        phase_group.add_argument(
            '--flavor',
            metavar='<flavor>',
            help=_('Resize server to specified flavor'),
        )
        phase_group.add_argument(
            '--confirm',
            action="store_true",
            help=_('Confirm server resize is complete'),
        )
        phase_group.add_argument(
            '--revert',
            action="store_true",
            help=_('Restore server state before resize'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for resize to complete'),
        )
        return parser

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stdout.write('\rProgress: %s' % progress)
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        if parsed_args.flavor:
            flavor = utils.find_resource(
                compute_client.flavors,
                parsed_args.flavor,
            )
            compute_client.servers.resize(server, flavor)
            if parsed_args.wait:
                if utils.wait_for_status(
                    compute_client.servers.get,
                    server.id,
                    success_status=['active', 'verify_resize'],
                    callback=_show_progress,
                ):
                    self.app.stdout.write(_('Complete\n'))
                else:
                    LOG.error(_('Error resizing server: %s'),
                              server.id)
                    self.app.stdout.write(_('Error resizing server\n'))
                    raise SystemExit
        elif parsed_args.confirm:
            self.log.warning(_(
                "The --confirm option has been deprecated. Please use the "
                "'openstack server resize confirm' command instead."))
            compute_client.servers.confirm_resize(server)
        elif parsed_args.revert:
            self.log.warning(_(
                "The --revert option has been deprecated. Please use the "
                "'openstack server resize revert' command instead."))
            compute_client.servers.revert_resize(server)


class ResizeConfirm(command.Command):
    _description = _("""Confirm server resize.

Confirm (verify) success of resize operation and release the old server.""")

    def get_parser(self, prog_name):
        parser = super(ResizeConfirm, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        server.confirm_resize()


class ResizeRevert(command.Command):
    _description = _("""Revert server resize.

Revert the resize operation. Release the new server and restart the old
one.""")

    def get_parser(self, prog_name):
        parser = super(ResizeRevert, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        server.revert_resize()


class RestoreServer(command.Command):
    _description = _("Restore server(s)")

    def get_parser(self, prog_name):
        parser = super(RestoreServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to restore (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server
            ).restore()


class ResumeServer(command.Command):
    _description = _("Resume server(s)")

    def get_parser(self, prog_name):
        parser = super(ResumeServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to resume (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).resume()


class SetServer(command.Command):
    _description = _("Set server properties")

    def get_parser(self, prog_name):
        parser = super(SetServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help=_('New server name'),
        )
        parser.add_argument(
            '--root-password',
            action="store_true",
            help=_('Set new root password (interactive only)'),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_('Property to add/change for this server '
                   '(repeat option to set multiple properties)'),
        )
        parser.add_argument(
            '--state',
            metavar='<state>',
            choices=['active', 'error'],
            help=_('New server state (valid value: active, error)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New server description (supported by '
                   '--os-compute-api-version 2.19 or above)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        if parsed_args.name:
            server.update(name=parsed_args.name)

        if parsed_args.property:
            compute_client.servers.set_meta(
                server,
                parsed_args.property,
            )

        if parsed_args.state:
            server.reset_state(state=parsed_args.state)

        if parsed_args.root_password:
            p1 = getpass.getpass(_('New password: '))
            p2 = getpass.getpass(_('Retype new password: '))
            if p1 == p2:
                server.change_password(p1)
            else:
                msg = _("Passwords do not match, password unchanged")
                raise exceptions.CommandError(msg)

        if parsed_args.description:
            if server.api_version < api_versions.APIVersion("2.19"):
                msg = _("Description is not supported for "
                        "--os-compute-api-version less than 2.19")
                raise exceptions.CommandError(msg)
            server.update(description=parsed_args.description)


class ShelveServer(command.Command):
    _description = _("Shelve server(s)")

    def get_parser(self, prog_name):
        parser = super(ShelveServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to shelve (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).shelve()


class ShowServer(command.ShowOne):
    _description = _(
        "Show server details. Specify ``--os-compute-api-version 2.47`` "
        "or higher to see the embedded flavor information for the server.")

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--diagnostics',
            action='store_true',
            default=False,
            help=_('Display server diagnostics information'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(compute_client.servers,
                                     parsed_args.server)

        if parsed_args.diagnostics:
            (resp, data) = server.diagnostics()
            if not resp.status_code == 200:
                self.app.stderr.write(_(
                    "Error retrieving diagnostics data\n"
                ))
                return ({}, {})
        else:
            data = _prep_server_detail(compute_client,
                                       self.app.client_manager.image, server,
                                       refresh=False)

        return zip(*sorted(six.iteritems(data)))


class SshServer(command.Command):
    _description = _("SSH to server")

    def get_parser(self, prog_name):
        parser = super(SshServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--login',
            metavar='<login-name>',
            help=_('Login name (ssh -l option)'),
        )
        parser.add_argument(
            '-l',
            dest='login',
            metavar='<login-name>',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help=_('Destination port (ssh -p option)'),
        )
        parser.add_argument(
            '-p',
            metavar='<port>',
            dest='port',
            type=int,
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--identity',
            metavar='<keyfile>',
            help=_('Private key file (ssh -i option)'),
        )
        parser.add_argument(
            '-i',
            metavar='<filename>',
            dest='identity',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--option',
            metavar='<config-options>',
            help=_('Options in ssh_config(5) format (ssh -o option)'),
        )
        parser.add_argument(
            '-o',
            metavar='<option>',
            dest='option',
            help=argparse.SUPPRESS,
        )
        ip_group = parser.add_mutually_exclusive_group()
        ip_group.add_argument(
            '-4',
            dest='ipv4',
            action='store_true',
            default=False,
            help=_('Use only IPv4 addresses'),
        )
        ip_group.add_argument(
            '-6',
            dest='ipv6',
            action='store_true',
            default=False,
            help=_('Use only IPv6 addresses'),
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--public',
            dest='address_type',
            action='store_const',
            const='public',
            default='public',
            help=_('Use public IP address'),
        )
        type_group.add_argument(
            '--private',
            dest='address_type',
            action='store_const',
            const='private',
            default='public',
            help=_('Use private IP address'),
        )
        type_group.add_argument(
            '--address-type',
            metavar='<address-type>',
            dest='address_type',
            default='public',
            help=_('Use other IP address (public, private, etc)'),
        )
        parser.add_argument(
            '-v',
            dest='verbose',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        # Build the command
        cmd = "ssh"

        ip_address_family = [4, 6]
        if parsed_args.ipv4:
            ip_address_family = [4]
            cmd += " -4"
        if parsed_args.ipv6:
            ip_address_family = [6]
            cmd += " -6"

        if parsed_args.port:
            cmd += " -p %d" % parsed_args.port
        if parsed_args.identity:
            cmd += " -i %s" % parsed_args.identity
        if parsed_args.option:
            cmd += " -o %s" % parsed_args.option
        if parsed_args.login:
            login = parsed_args.login
        else:
            login = self.app.client_manager.auth_ref.username
        if parsed_args.verbose:
            cmd += " -v"

        cmd += " %s@%s"
        ip_address = _get_ip_address(server.addresses,
                                     parsed_args.address_type,
                                     ip_address_family)
        LOG.debug("ssh command: %s", (cmd % (login, ip_address)))
        os.system(cmd % (login, ip_address))


class StartServer(command.Command):
    _description = _("Start server(s).")

    def get_parser(self, prog_name):
        parser = super(StartServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs="+",
            help=_('Server(s) to start (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).start()


class StopServer(command.Command):
    _description = _("Stop server(s).")

    def get_parser(self, prog_name):
        parser = super(StopServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs="+",
            help=_('Server(s) to stop (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).stop()


class SuspendServer(command.Command):
    _description = _("Suspend server(s)")

    def get_parser(self, prog_name):
        parser = super(SuspendServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to suspend (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).suspend()


class UnlockServer(command.Command):
    _description = _("Unlock server(s)")

    def get_parser(self, prog_name):
        parser = super(UnlockServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to unlock (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).unlock()


class UnpauseServer(command.Command):
    _description = _("Unpause server(s)")

    def get_parser(self, prog_name):
        parser = super(UnpauseServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to unpause (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).unpause()


class UnrescueServer(command.Command):
    _description = _("Restore server from rescue mode")

    def get_parser(self, prog_name):
        parser = super(UnrescueServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).unrescue()


class UnsetServer(command.Command):
    _description = _("Unset server properties")

    def get_parser(self, prog_name):
        parser = super(UnsetServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help=_('Property key to remove from server '
                   '(repeat option to remove multiple values)'),
        )
        parser.add_argument(
            '--description',
            dest='description',
            action='store_true',
            help=_('Unset server description (supported by '
                   '--os-compute-api-version 2.19 or above)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        if parsed_args.property:
            compute_client.servers.delete_meta(
                server,
                parsed_args.property,
            )

        if parsed_args.description:
            if compute_client.api_version < api_versions.APIVersion("2.19"):
                msg = _("Description is not supported for "
                        "--os-compute-api-version less than 2.19")
                raise exceptions.CommandError(msg)
            compute_client.servers.update(
                server,
                description="",
            )


class UnshelveServer(command.Command):
    _description = _("Unshelve server(s)")

    def get_parser(self, prog_name):
        parser = super(UnshelveServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to unshelve (name or ID)'),
        )
        parser.add_argument(
            '--availability-zone',
            default=None,
            help=_('Name of the availability zone in which to unshelve a '
                   'SHELVED_OFFLOADED server (supported by '
                   '--os-compute-api-version 2.77 or above)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        support_az = compute_client.api_version >= api_versions.APIVersion(
            '2.77')
        if not support_az and parsed_args.availability_zone:
            msg = _("--os-compute-api-version 2.77 or greater is required "
                    "to support the '--availability-zone' option.")
            raise exceptions.CommandError(msg)

        for server in parsed_args.server:
            if support_az:
                utils.find_resource(
                    compute_client.servers,
                    server
                ).unshelve(availability_zone=parsed_args.availability_zone)
            else:
                utils.find_resource(
                    compute_client.servers,
                    server,
                ).unshelve()
