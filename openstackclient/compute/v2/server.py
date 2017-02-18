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
import sys

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import timeutils
import six

try:
    from novaclient.v2 import servers
except ImportError:
    from novaclient.v1_1 import servers

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


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


def _prep_server_detail(compute_client, image_client, server):
    """Prepare the detailed server dict for printing

    :param compute_client: a compute client instance
    :param server: a Server resource
    :rtype: a dict of server details
    """
    info = server._info.copy()

    server = utils.find_resource(compute_client.servers, info['id'])
    info.update(server._info)

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
    flavor_id = flavor_info.get('id', '')
    try:
        flavor = utils.find_resource(compute_client.flavors, flavor_id)
        info['flavor'] = "%s (%s)" % (flavor.name, flavor_id)
    except Exception:
        info['flavor'] = flavor_id

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

    # Map power state num to meanful string
    if 'OS-EXT-STS:power_state' in info:
        info['OS-EXT-STS:power_state'] = _format_servers_list_power_state(
            info['OS-EXT-STS:power_state'])

    # Remove values that are long and not too useful
    info.pop('links', None)

    return info


def _show_progress(progress):
    if progress:
        sys.stdout.write('\rProgress: %s' % progress)
        sys.stdout.flush()


class AddFixedIP(command.Command):
    _description = _("Add fixed IP address to server")

    def get_parser(self, prog_name):
        parser = super(AddFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server (name or ID) to receive the fixed IP address"),
        )
        parser.add_argument(
            "network",
            metavar="<network>",
            help=_("Network (name or ID) to allocate "
                   "the fixed IP address from"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        network = utils.find_resource(
            compute_client.networks, parsed_args.network)

        server.add_fixed_ip(network.id)


class AddFloatingIP(command.Command):
    _description = _("Add floating IP address to server")

    def get_parser(self, prog_name):
        parser = super(AddFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server (name or ID) to receive the floating IP address"),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Floating IP address (IP address only) to assign "
                   "to server"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.add_floating_ip(parsed_args.ip_address)


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
        security_group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        server.add_security_group(security_group.id)


class AddServerVolume(command.Command):
    _description = _("Add volume to server")

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
            '--volume',
            metavar='<volume>',
            help=_(
                'Create server using this volume as the boot disk '
                '(name or ID)'
            ),
        )
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            required=True,
            help=_('Create server with this flavor (name or ID)'),
        )
        parser.add_argument(
            '--security-group',
            metavar='<security-group-name>',
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
            '--availability-zone',
            metavar='<zone-name>',
            help=_('Select an availability zone for the server'),
        )
        parser.add_argument(
            '--block-device-mapping',
            metavar='<dev-name=mapping>',
            action='append',
            default=[],
            help=_('Map block devices; map is '
                   '<id>:<type>:<size(GB)>:<delete_on_terminate> '
                   '(optional extension)'),
        )
        parser.add_argument(
            '--nic',
            metavar="<net-id=net-uuid,v4-fixed-ip=ip-addr,v6-fixed-ip=ip-addr,"
                    "port-id=port-uuid,auto,none>",
            action='append',
            default=[],
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

        # Lookup parsed_args.volume
        volume = None
        if parsed_args.volume:
            volume = utils.find_resource(
                volume_client.volumes,
                parsed_args.volume,
            ).id

        # Lookup parsed_args.flavor
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)

        boot_args = [parsed_args.server_name, image, flavor]

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

        block_device_mapping_v2 = []
        if volume:
            block_device_mapping_v2 = [{'uuid': volume,
                                        'boot_index': '0',
                                        'source_type': 'volume',
                                        'destination_type': 'volume'
                                        }]
        for dev_map in parsed_args.block_device_mapping:
            dev_name, dev_map = dev_map.split('=', 1)
            if dev_map:
                dev_map = dev_map.split(':')
                if len(dev_map) > 0:
                    mapping = {
                        'device_name': dev_name,
                        'uuid': utils.find_resource(
                            volume_client.volumes,
                            dev_map[0],
                        ).id}
                    # Block device mapping v1 compatibility
                    if len(dev_map) > 1 and \
                            dev_map[1] in ('volume', 'snapshot'):
                        mapping['source_type'] = dev_map[1]
                    else:
                        mapping['source_type'] = 'volume'
                    mapping['destination_type'] = 'volume'
                    if len(dev_map) > 2:
                        mapping['volume_size'] = dev_map[2]
                    if len(dev_map) > 3:
                        mapping['delete_on_termination'] = dev_map[3]
                else:
                    msg = _("Volume name or ID must be specified if "
                            "--block-device-mapping is specified")
                    raise exceptions.CommandError(msg)
                block_device_mapping_v2.append(mapping)

        nics = []
        auto_or_none = False
        for nic_str in parsed_args.nic:
            # Handle the special auto/none cases
            if nic_str in ('auto', 'none'):
                auto_or_none = True
                nics.append(nic_str)
            else:
                nic_info = {"net-id": "", "v4-fixed-ip": "",
                            "v6-fixed-ip": "", "port-id": ""}
                try:
                    nic_info.update(dict(kv_str.split("=", 1)
                                    for kv_str in nic_str.split(",")))
                except ValueError:
                    msg = _('Invalid --nic argument %s.') % nic_str
                    raise exceptions.CommandError(msg)
                if bool(nic_info["net-id"]) == bool(nic_info["port-id"]):
                    msg = _("either net-id or port-id should be specified "
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
                        nic_info["net-id"] = utils.find_resource(
                            compute_client.networks,
                            nic_info["net-id"]
                        ).id
                    if nic_info["port-id"]:
                        msg = _("can't create server with port specified "
                                "since network endpoint not enabled")
                        raise exceptions.CommandError(msg)
                nics.append(nic_info)

        if nics:
            if auto_or_none:
                if len(nics) > 1:
                    msg = _('Specifying a --nic of auto or none cannot '
                            'be used with any other --nic value.')
                    raise exceptions.CommandError(msg)
                nics = nics[0]
        else:
            # Default to empty list if nothing was specified, let nova side to
            # decide the default behavior.
            nics = []

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
            security_groups=parsed_args.security_group,
            userdata=userdata,
            key_name=parsed_args.key_name,
            availability_zone=parsed_args.availability_zone,
            block_device_mapping_v2=block_device_mapping_v2,
            nics=nics,
            scheduler_hints=hints,
            config_drive=config_drive)

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
                sys.stdout.write('\n')
            else:
                LOG.error(_('Error creating server: %s'),
                          parsed_args.server_name)
                sys.stdout.write(_('Error creating server\n'))
                raise SystemExit

        details = _prep_server_detail(compute_client, image_client, server)
        return zip(*sorted(six.iteritems(details)))


class CreateServerDump(command.Command):
    """Create a dump file in server(s)

    Trigger crash dump in server(s) with features like kdump in Linux.
    It will create a dump file in the server(s) dumping the server(s)'
    memory, and also crash the server(s). OSC sees the dump file
    (server dump) as a kind of resource.
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
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            server_obj = utils.find_resource(
                compute_client.servers, server)
            compute_client.servers.delete(server_obj.id)
            if parsed_args.wait:
                if utils.wait_for_delete(
                    compute_client.servers,
                    server_obj.id,
                    callback=_show_progress,
                ):
                    sys.stdout.write('\n')
                else:
                    LOG.error(_('Error deleting server: %s'),
                              server_obj.id)
                    sys.stdout.write(_('Error deleting server\n'))
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
            help=_('Regular expression to match IPv6 addresses'),
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
        parser.add_argument(
            '--marker',
            metavar='<marker>',
            default=None,
            help=_('The last server (name or ID) of the previous page. Display'
                   ' list of servers after marker. Display all servers if not'
                   ' specified.')
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            default=None,
            help=_("Maximum number of servers to display. If limit equals -1,"
                   " all servers will be displayed. If limit is greater than"
                   " 'osapi_max_limit' option of Nova API,"
                   " 'osapi_max_limit' will be used instead."),
        )
        parser.add_argument(
            '--deleted',
            action="store_true",
            default=False,
            help=_('Only display deleted servers (Admin only).')
        )
        parser.add_argument(
            '--changes-since',
            metavar='<changes-since>',
            default=None,
            help=_("List only servers changed after a certain point of time."
                   " The provided time should be an ISO 8061 formatted time."
                   " ex 2016-03-04T06:27:59Z .")
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
            'changes_since': parsed_args.changes_since,
        }
        LOG.debug('search options: %s', search_opts)

        if search_opts['changes_since']:
            try:
                timeutils.parse_isotime(search_opts['changes_since'])
            except ValueError:
                raise exceptions.CommandError(_('Invalid changes-since value:'
                                              ' %s') % search_opts['changes'
                                                                   '_since'])

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
            columns = (
                'ID',
                'Name',
                'Status',
                'Networks',
                'Image Name',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Networks',
                'Image Name',
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
        # Create a dict that maps image_id to image object.
        # Needed so that we can display the "Image Name" column.
        # "Image Name" is not crucial, so we swallow any exceptions.
        try:
            images_list = self.app.client_manager.image.images.list()
            for i in images_list:
                images[i.id] = i
        except Exception:
            pass

        # Populate image_name and image_id attributes of server objects
        # so that we can display "Image Name" and "Image ID" columns.
        for s in data:
            if 'id' in s.image:
                image = images.get(s.image['id'])
                if image:
                    s.image_name = image.name
                s.image_id = s.image['id']
            else:
                s.image_name = ''
                s.image_id = ''

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
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).lock()


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
            '--live',
            metavar='<hostname>',
            help=_('Target hostname'),
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

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        if parsed_args.live:
            server.live_migrate(
                host=parsed_args.live,
                block_migration=parsed_args.block_migration,
                disk_over_commit=parsed_args.disk_overcommit,
            )
        else:
            server.migrate()

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                sys.stdout.write(_('Complete\n'))
            else:
                LOG.error(_('Error migrating server: %s'),
                          server.id)
                sys.stdout.write(_('Error migrating server\n'))
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
                sys.stdout.write(_('Complete\n'))
            else:
                LOG.error(_('Error rebooting server: %s'),
                          server.id)
                sys.stdout.write(_('Error rebooting server\n'))
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
            '--wait',
            action='store_true',
            help=_('Wait for rebuild to complete'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        # If parsed_args.image is not set, default to the currently used one.
        image_id = parsed_args.image or server._info.get('image', {}).get('id')
        image = utils.find_resource(image_client.images, image_id)

        server = server.rebuild(image, parsed_args.password)
        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                sys.stdout.write(_('Complete\n'))
            else:
                LOG.error(_('Error rebuilding server: %s'),
                          server.id)
                sys.stdout.write(_('Error rebuilding server\n'))
                raise SystemExit

        details = _prep_server_detail(compute_client, image_client, server)
        return zip(*sorted(six.iteritems(details)))


class RemoveFixedIP(command.Command):
    _description = _("Remove fixed IP address from server")

    def get_parser(self, prog_name):
        parser = super(RemoveFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server (name or ID) to remove the fixed IP address from"),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Fixed IP address (IP address only) to remove from the "
                   "server"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_fixed_ip(parsed_args.ip_address)


class RemoveFloatingIP(command.Command):
    _description = _("Remove floating IP address from server")

    def get_parser(self, prog_name):
        parser = super(RemoveFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server (name or ID) to remove the "
                   "floating IP address from"),
        )
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("Floating IP address (IP address only) "
                   "to remove from server"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_floating_ip(parsed_args.ip_address)


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
        security_group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        server.remove_security_group(security_group.id)


class RemoveServerVolume(command.Command):
    _description = _("Remove volume from server")

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


class RescueServer(command.ShowOne):
    _description = _("Put server in rescue mode")

    def get_parser(self, prog_name):
        parser = super(RescueServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        _, body = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).rescue()
        return zip(*sorted(six.iteritems(body)))


class ResizeServer(command.Command):
    _description = _("Scale server to a new flavor")

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
                    sys.stdout.write(_('Complete\n'))
                else:
                    LOG.error(_('Error resizing server: %s'),
                              server.id)
                    sys.stdout.write(_('Error resizing server\n'))
                    raise SystemExit
        elif parsed_args.confirm:
            compute_client.servers.confirm_resize(server)
        elif parsed_args.revert:
            compute_client.servers.revert_resize(server)


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
    _description = _("Show server details")

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
                sys.stderr.write(_("Error retrieving diagnostics data\n"))
                return ({}, {})
        else:
            data = _prep_server_detail(compute_client,
                                       self.app.client_manager.image, server)

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
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            utils.find_resource(
                compute_client.servers,
                server,
            ).unshelve()
