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
import base64
import getpass
import json
import logging
import os
import typing as ty

from cliff import columns as cliff_columns
import iso8601
from openstack import exceptions as sdk_exceptions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.api import compute_v2
from openstackclient.common import envvars
from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common as network_common

LOG = logging.getLogger(__name__)

IMAGE_STRING_FOR_BFV = 'N/A (booted from volume)'


class PowerStateColumn(cliff_columns.FormattableColumn):
    """Generate a formatted string of a server's power state."""

    power_states = [
        'NOSTATE',  # 0x00
        'Running',  # 0x01
        '',  # 0x02
        'Paused',  # 0x03
        'Shutdown',  # 0x04
        '',  # 0x05
        'Crashed',  # 0x06
        'Suspended',  # 0x07
    ]

    def human_readable(self):
        try:
            return self.power_states[self._value]
        except Exception:
            return 'N/A'


class AddressesColumn(cliff_columns.FormattableColumn):
    """Generate a formatted string of a server's addresses."""

    def human_readable(self):
        try:
            return utils.format_dict_of_list(
                {
                    k: [i['addr'] for i in v if 'addr' in i]
                    for k, v in self._value.items()
                }
            )
        except Exception:
            return 'N/A'

    def machine_readable(self):
        return {
            k: [i['addr'] for i in v if 'addr' in i]
            for k, v in (self._value.items() if self._value else [])
        }


class HostColumn(cliff_columns.FormattableColumn):
    """Generate a formatted string of a hostname."""

    def human_readable(self):
        if self._value is None:
            return ''

        return self._value


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
            if isinstance(addy, str):
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
        msg % {"type": address_type, "family": ip_address_family}
    )


def _prep_server_detail(compute_client, image_client, server, *, refresh=True):
    """Prepare the detailed server dict for printing

    :param compute_client: a compute client instance
    :param image_client: an image client instance
    :param server: a Server resource
    :param refresh: Flag indicating if ``server`` is already the latest version
        or if it needs to be refreshed, for example when showing the latest
        details of a server after creating it.
    :rtype: a dict of server details
    """
    info = server.to_dict()

    if refresh:
        server = compute_client.get_server(info['id'])
        # we only update if the field is not empty, to avoid overwriting
        # existing values
        info.update(
            **{x: y for x, y in server.to_dict().items() if x not in info or y}
        )

    # Some commands using this routine were originally implemented with the
    # nova python wrappers, and were later migrated to use the SDK. Map the
    # SDK's property names to the original property names to maintain backward
    # compatibility for existing users.
    column_map = {
        'access_ipv4': 'accessIPv4',
        'access_ipv6': 'accessIPv6',
        'admin_password': 'adminPass',
        'attached_volumes': 'volumes_attached',
        'availability_zone': 'OS-EXT-AZ:availability_zone',
        'compute_host': 'OS-EXT-SRV-ATTR:host',
        'created_at': 'created',
        'disk_config': 'OS-DCF:diskConfig',
        'has_config_drive': 'config_drive',
        'host_id': 'hostId',
        'fault': 'fault',
        'hostname': 'OS-EXT-SRV-ATTR:hostname',
        'hypervisor_hostname': 'OS-EXT-SRV-ATTR:hypervisor_hostname',
        'instance_name': 'OS-EXT-SRV-ATTR:instance_name',
        'is_locked': 'locked',
        'kernel_id': 'OS-EXT-SRV-ATTR:kernel_id',
        'launch_index': 'OS-EXT-SRV-ATTR:launch_index',
        'launched_at': 'OS-SRV-USG:launched_at',
        'power_state': 'OS-EXT-STS:power_state',
        'project_id': 'tenant_id',
        'ramdisk_id': 'OS-EXT-SRV-ATTR:ramdisk_id',
        'reservation_id': 'OS-EXT-SRV-ATTR:reservation_id',
        'root_device_name': 'OS-EXT-SRV-ATTR:root_device_name',
        'task_state': 'OS-EXT-STS:task_state',
        'terminated_at': 'OS-SRV-USG:terminated_at',
        'updated_at': 'updated',
        'user_data': 'OS-EXT-SRV-ATTR:user_data',
        'vm_state': 'OS-EXT-STS:vm_state',
        'pinned_availability_zone': 'pinned_availability_zone',
    }
    # Some columns returned by openstacksdk should not be shown because they're
    # either irrelevant or duplicates
    ignored_columns = {
        # computed columns
        'interface_ip',
        'location',
        'private_v4',
        'private_v6',
        'public_v4',
        'public_v6',
        # create-only columns
        'block_device_mapping',
        'flavor_id',
        'host',
        'image_id',
        'max_count',
        'min_count',
        'networks',
        'personality',
        'scheduler_hints',
        # aliases
        'volumes',
        # unnecessary
        'links',
    }
    # Some columns are only present in certain responses and should not be
    # shown otherwise.
    optional_columns = {
        # only in create responses if '[api] enable_instance_password' is set
        'admin_password',
        # only present in errored servers
        'fault',
        # only present in create, detail responses
        'security_groups',
    }

    data = {}
    for key, value in info.items():
        if key in ignored_columns:
            continue

        if key in optional_columns:
            if info[key] is None:
                continue

        alias = column_map.get(key)
        data[alias or key] = value

    info = data

    # Convert the image blob to a name
    image_info = info.get('image', {})
    if image_info and any(image_info.values()):
        image_id = image_info.get('id', '')
        try:
            image = image_client.get_image(image_id)
            info['image'] = f"{image.name} ({image_id})"
        except Exception:
            info['image'] = image_id
    else:
        # NOTE(melwitt): An server booted from a volume will have no image
        # associated with it. We fill in the image with "N/A (booted from
        # volume)" to help users who want to be able to grep for
        # boot-from-volume servers when using the CLI.
        info['image'] = IMAGE_STRING_FOR_BFV

    # Convert the flavor blob to a name
    flavor_info = info.get('flavor', {})
    # Microversion 2.47 puts the embedded flavor into the server response
    # body. The presence of the 'original_name' attribute indicates this.
    if flavor_info.get('original_name') is None:  # microversion < 2.47
        flavor_id = flavor_info.get('id', '')
        try:
            flavor = compute_client.find_flavor(
                flavor_id, ignore_missing=False
            )
            info['flavor'] = f"{flavor.name} ({flavor_id})"
        except Exception:
            info['flavor'] = flavor_id
    else:  # microversion >= 2.47
        info['flavor'] = format_columns.DictColumn(flavor_info)

    # there's a lot of redundant information in BDMs - strip it
    if 'volumes_attached' in info:
        info.update(
            {
                'volumes_attached': format_columns.ListDictColumn(
                    [
                        {
                            k: v
                            for k, v in volume.items()
                            if v is not None and k != 'location'
                        }
                        for volume in info.pop('volumes_attached') or []
                    ]
                )
            }
        )

    if 'security_groups' in info:
        info.update(
            {
                'security_groups': format_columns.ListDictColumn(
                    info.pop('security_groups'),
                )
            }
        )

    if 'tags' in info:
        info.update(
            {'tags': format_columns.ListColumn(info.pop('tags') or [])}
        )

    # Map 'networks' to 'addresses', if present. Note that the 'networks' key
    # is used for create responses, otherwise it's 'addresses'. We know it'll
    # be set because this is one of our optional columns.
    if 'networks' in info:
        info['addresses'] = format_columns.DictListColumn(
            info.pop('networks', {}),
        )
    else:
        info['addresses'] = AddressesColumn(info.get('addresses', {}))

    # Map 'metadata' field to 'properties' and format
    info['properties'] = format_columns.DictColumn(info.pop('metadata'))

    # Migrate tenant_id to project_id naming
    if 'tenant_id' in info:
        info['project_id'] = info.pop('tenant_id')

    # Map power state num to meaningful string
    if 'OS-EXT-STS:power_state' in info:
        info['OS-EXT-STS:power_state'] = PowerStateColumn(
            info['OS-EXT-STS:power_state']
        )

    return info


class AddFixedIP(command.ShowOne):
    _description = _("Add fixed IP address to server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            help=_(
                'Tag for the attached interface. '
                '(supported by --os-compute-api-version 2.49 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if parsed_args.tag:
            if not sdk_utils.supports_microversion(compute_client, '2.49'):
                msg = _(
                    '--os-compute-api-version 2.49 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            net_id = network_client.find_network(
                parsed_args.network, ignore_missing=False
            ).id
        else:
            net_id = parsed_args.network

        kwargs = {'net_id': net_id}
        if parsed_args.fixed_ip_address:
            kwargs['fixed_ips'] = [
                {"ip_address": parsed_args.fixed_ip_address}
            ]
        if parsed_args.tag:
            kwargs['tag'] = parsed_args.tag

        interface = compute_client.create_server_interface(server.id, **kwargs)

        columns: tuple[str, ...] = (
            'port_id',
            'server_id',
            'net_id',
            'mac_addr',
            'port_state',
            'fixed_ips',
        )
        column_headers: tuple[str, ...] = (
            'Port ID',
            'Server ID',
            'Network ID',
            'MAC Address',
            'Port State',
            'Fixed IPs',
        )

        if parsed_args.tag:
            if sdk_utils.supports_microversion(compute_client, '2.49'):
                columns += ('tag',)
                column_headers += ('Tag',)

        return (
            column_headers,
            utils.get_item_properties(
                interface,
                columns,
                formatters={
                    'fixed_ips': format_columns.ListDictColumn,
                },
            ),
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
            help=_(
                "Floating IP address to assign to the first available "
                "server port (IP only)"
            ),
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

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        ports = list(client.ports(device_id=server.id))
        if not ports:
            msg = _('No attached ports found to associate floating IP with')
            raise exceptions.CommandError(msg)

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
                    LOG.info(
                        'Skipped port %s because it is not attached to '
                        'an external gateway',
                        port.id,
                    )
                    error = exp
                    continue
                else:
                    error = None
                    break
            if error:
                raise error

    def take_action_compute(self, client, parsed_args):
        server = client.find_server(parsed_args.server, ignore_missing=False)
        client.add_floating_ip_to_server(
            server,
            parsed_args.ip_address,
            fixed_address=parsed_args.fixed_ip_address,
        )


class AddPort(command.Command):
    _description = _("Add port to server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            help=_(
                'Tag for the attached interface '
                '(supported by --os-compute-api-version 2.49 or later)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            port_id = network_client.find_port(
                parsed_args.port, ignore_missing=False
            ).id
        else:
            port_id = parsed_args.port

        kwargs = {'port_id': port_id}

        if parsed_args.tag:
            if not sdk_utils.supports_microversion(compute_client, '2.49'):
                msg = _(
                    '--os-compute-api-version 2.49 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)
            kwargs['tag'] = parsed_args.tag

        compute_client.create_server_interface(server, **kwargs)


class AddNetwork(command.Command):
    _description = _("Add network to server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            help=_(
                'Tag for the attached interface. '
                '(supported by --os-compute-api-version 2.49 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            net_id = network_client.find_network(
                parsed_args.network, ignore_missing=False
            ).id
        else:
            net_id = parsed_args.network

        kwargs = {'net_id': net_id}

        if parsed_args.tag:
            if not sdk_utils.supports_microversion(compute_client, '2.49'):
                msg = _(
                    '--os-compute-api-version 2.49 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

            kwargs['tag'] = parsed_args.tag

        compute_client.create_server_interface(server, **kwargs)


class AddServerSecurityGroup(command.Command):
    _description = _("Add security group(s) to server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'security_groups',
            metavar='<security-group>',
            nargs='+',
            help=_(
                'Security group(s) to add to the server (name or ID) '
                '(repeat option to add multiple groups)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        if self.app.client_manager.is_network_endpoint_enabled():
            # the server handles both names and IDs for neutron SGs, so just
            # pass things through if using neutron
            security_groups = parsed_args.security_groups
        else:
            # however, if using nova-network then it needs names, not IDs
            security_groups = []
            for security_group in parsed_args.security_groups:
                security_groups.append(
                    compute_v2.find_security_group(
                        compute_client, security_group
                    )['name']
                )

        errors = 0
        for security_group in security_groups:
            try:
                compute_client.add_security_group_to_server(
                    server,
                    {'name': security_group},
                )
            except sdk_exceptions.HttpException as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to add security group with name or ID "
                        "'%(security_group)s' to server '%(server)s': %(e)s"
                    ),
                    {
                        'security_group': security_group,
                        'server': server.id,
                        'e': e,
                    },
                )

        if errors > 0:
            msg = _(
                "%(errors)d of %(total)d security groups were not added."
            ) % {'errors': errors, 'total': len(security_groups)}
            raise exceptions.CommandError(msg)


class AddServerVolume(command.ShowOne):
    _description = _(
        """Add volume to server.

Specify ``--os-compute-api-version 2.20`` or higher to add a volume to a server
with status ``SHELVED`` or ``SHELVED_OFFLOADED``."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            help=_(
                'Tag for the attached volume '
                '(supported by --os-compute-api-version 2.49 or above)'
            ),
        )
        # TODO(stephenfin): These should be called 'delete-on-termination' and
        # 'preserve-on-termination'
        termination_group = parser.add_mutually_exclusive_group()
        termination_group.add_argument(
            '--enable-delete-on-termination',
            action='store_true',
            help=_(
                'Delete the volume when the server is destroyed '
                '(supported by --os-compute-api-version 2.79 or above)'
            ),
        )
        termination_group.add_argument(
            '--disable-delete-on-termination',
            action='store_true',
            help=_(
                'Do not delete the volume when the server is destroyed '
                '(supported by --os-compute-api-version 2.79 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.sdk_connection.volume

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        volume = volume_client.find_volume(
            parsed_args.volume,
            ignore_missing=False,
        )

        kwargs = {"volumeId": volume.id, "device": parsed_args.device}

        if parsed_args.tag:
            if not sdk_utils.supports_microversion(compute_client, '2.49'):
                msg = _(
                    '--os-compute-api-version 2.49 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

            kwargs['tag'] = parsed_args.tag

        if parsed_args.enable_delete_on_termination:
            if not sdk_utils.supports_microversion(compute_client, '2.79'):
                msg = _(
                    '--os-compute-api-version 2.79 or greater is required to '
                    'support the --enable-delete-on-termination option.'
                )
                raise exceptions.CommandError(msg)

            kwargs['delete_on_termination'] = True

        if parsed_args.disable_delete_on_termination:
            if not sdk_utils.supports_microversion(compute_client, '2.79'):
                msg = _(
                    '--os-compute-api-version 2.79 or greater is required to '
                    'support the --disable-delete-on-termination option.'
                )
                raise exceptions.CommandError(msg)

            kwargs['delete_on_termination'] = False

        volume_attachment = compute_client.create_volume_attachment(
            server,
            **kwargs,
        )

        columns: tuple[str, ...] = ('id', 'server id', 'volume id', 'device')
        column_headers: tuple[str, ...] = (
            'ID',
            'Server ID',
            'Volume ID',
            'Device',
        )
        if sdk_utils.supports_microversion(compute_client, '2.49'):
            columns += ('tag',)
            column_headers += ('Tag',)
        if sdk_utils.supports_microversion(compute_client, '2.79'):
            columns += ('delete_on_termination',)
            column_headers += ('Delete On Termination',)

        return (
            column_headers,
            utils.get_item_properties(
                volume_attachment,
                columns,
            ),
        )


class NoneNICAction(argparse.Action):
    def __init__(self, option_strings, dest, help=None):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=[],
            required=False,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        # Make sure we have an empty dict rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])

        getattr(namespace, self.dest).append('none')


class AutoNICAction(argparse.Action):
    def __init__(self, option_strings, dest, help=None):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=[],
            required=False,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        # Make sure we have an empty dict rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])

        getattr(namespace, self.dest).append('auto')


class NICAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest,
        help=None,
        metavar=None,
        key=None,
    ):
        self.key = key
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=None,
            const=None,
            default=[],
            type=None,
            choices=None,
            required=False,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        # Make sure we have an empty dict rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])

        if self.key:
            if ',' in values or '=' in values:
                msg = _(
                    "Invalid argument %s; characters ',' and '=' are not "
                    "allowed"
                )
                raise argparse.ArgumentError(self, msg % values)

            values = '='.join([self.key, values])
        else:
            # Handle the special auto/none cases but only when a key isn't set
            # (otherwise those could be valid values for the key)
            if values in ('auto', 'none'):
                getattr(namespace, self.dest).append(values)
                return

        # We don't include 'tag' here by default since that requires a
        # particular microversion
        info = {
            'net-id': '',
            'port-id': '',
            'v4-fixed-ip': '',
            'v6-fixed-ip': '',
        }

        for kv_str in values.split(','):
            k, sep, v = kv_str.partition('=')

            if k not in list(info) + ['tag'] or not v:
                msg = _(
                    "Invalid argument %s; argument must be of form "
                    "'net-id=net-uuid,port-id=port-uuid,v4-fixed-ip=ip-addr,"
                    "v6-fixed-ip=ip-addr,tag=tag'"
                )
                raise argparse.ArgumentError(self, msg % values)

            info[k] = v

        if info['net-id'] and info['port-id']:
            msg = _(
                "Invalid argument %s; either 'network' or 'port' should be "
                "specified but not both"
            )
            raise argparse.ArgumentError(self, msg % values)

        if info['v4-fixed-ip'] and info['v6-fixed-ip']:
            msg = _(
                "Invalid argument %s; either 'v4-fixed-ip' or 'v6-fixed-ip' "
                "should be specified but not both"
            )
            raise argparse.ArgumentError(self, msg % values)

        getattr(namespace, self.dest).append(info)


class BDMLegacyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Make sure we have an empty list rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])

        dev_name, sep, dev_map = values.partition('=')
        dev_map = dev_map.split(':') if dev_map else dev_map
        if not dev_name or not dev_map or len(dev_map) > 4:
            msg = _(
                "Invalid argument %s; argument must be of form "
                "'dev-name=id[:type[:size[:delete-on-terminate]]]'"
            )
            raise argparse.ArgumentError(self, msg % values)

        mapping = {
            'device_name': dev_name,
            # store target; this may be a name and will need verification later
            'uuid': dev_map[0],
            'source_type': 'volume',
            'destination_type': 'volume',
        }

        # decide source and destination type
        if len(dev_map) > 1 and dev_map[1]:
            if dev_map[1] not in ('volume', 'snapshot', 'image'):
                msg = _(
                    "Invalid argument %s; 'type' must be one of: volume, "
                    "snapshot, image"
                )
                raise argparse.ArgumentError(self, msg % values)

            mapping['source_type'] = dev_map[1]

        # 3. append size and delete_on_termination, if present
        if len(dev_map) > 2 and dev_map[2]:
            mapping['volume_size'] = dev_map[2]

        if len(dev_map) > 3 and dev_map[3]:
            mapping['delete_on_termination'] = dev_map[3]

        getattr(namespace, self.dest).append(mapping)


class BDMAction(parseractions.MultiKeyValueAction):
    def __init__(self, option_strings, dest, **kwargs):
        optional_keys = [
            'uuid',
            'source_type',
            'destination_type',
            'disk_bus',
            'device_type',
            'device_name',
            'volume_size',
            'guest_format',
            'boot_index',
            'delete_on_termination',
            'tag',
            'volume_type',
        ]
        super().__init__(
            option_strings,
            dest,
            required_keys=[],
            optional_keys=optional_keys,
            **kwargs,
        )

    # TODO(stephenfin): Remove once I549d0897ef3704b7f47000f867d6731ad15d3f2b
    # or similar lands in a release
    def validate_keys(self, keys):
        """Validate the provided keys.

        :param keys: A list of keys to validate.
        """
        valid_keys = self.required_keys | self.optional_keys
        invalid_keys = [k for k in keys if k not in valid_keys]
        if invalid_keys:
            msg = _(
                "Invalid keys %(invalid_keys)s specified.\n"
                "Valid keys are: %(valid_keys)s"
            )
            raise argparse.ArgumentError(
                self,
                msg
                % {
                    'invalid_keys': ', '.join(invalid_keys),
                    'valid_keys': ', '.join(valid_keys),
                },
            )

        missing_keys = [k for k in self.required_keys if k not in keys]
        if missing_keys:
            msg = _(
                "Missing required keys %(missing_keys)s.\n"
                "Required keys are: %(required_keys)s"
            )
            raise argparse.ArgumentError(
                self,
                msg
                % {
                    'missing_keys': ', '.join(missing_keys),
                    'required_keys': ', '.join(self.required_keys),
                },
            )

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])

        if os.path.exists(values):
            with open(values) as fh:
                data = json.load(fh)

            # Validate the keys - other validation is left to later
            self.validate_keys(list(data))

            getattr(namespace, self.dest, []).append(data)
        else:
            super().__call__(parser, namespace, values, option_string)


class CreateServer(command.ShowOne):
    _description = _("Create a new server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server_name',
            metavar='<server-name>',
            help=_('New server name'),
        )
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            required=True,
            help=_('Create server with this flavor (name or ID)'),
        )
        disk_group = parser.add_mutually_exclusive_group()
        disk_group.add_argument(
            '--image',
            metavar='<image>',
            help=_('Create server boot disk from this image (name or ID)'),
        )
        # TODO(stephenfin): Is this actually useful? Looks like a straight port
        # from 'nova boot --image-with'. Perhaps we should deprecate this.
        disk_group.add_argument(
            '--image-property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='image_properties',
            help=_(
                "Create server using the image that matches the specified "
                "property. Property must match exactly one property."
            ),
        )
        disk_group.add_argument(
            '--volume',
            metavar='<volume>',
            help=_(
                'Create server using this volume as the boot disk (name or ID)'
                '\n'
                'This option automatically creates a block device mapping '
                'with a boot index of 0. On many hypervisors (libvirt/kvm '
                'for example) this will be device vda. Do not create a '
                'duplicate mapping using --block-device-mapping for this '
                'volume.'
            ),
        )
        disk_group.add_argument(
            '--snapshot',
            metavar='<snapshot>',
            help=_(
                'Create server using this snapshot as the boot disk (name or '
                'ID)\n'
                'This option automatically creates a block device mapping '
                'with a boot index of 0. On many hypervisors (libvirt/kvm '
                'for example) this will be device vda. Do not create a '
                'duplicate mapping using --block-device-mapping for this '
                'volume.'
            ),
        )
        parser.add_argument(
            '--boot-from-volume',
            metavar='<volume-size>',
            type=int,
            help=_(
                'When used in conjunction with the ``--image`` or '
                '``--image-property`` option, this option automatically '
                'creates a block device mapping with a boot index of 0 '
                'and tells the compute service to create a volume of the '
                'given size (in GB) from the specified image and use it '
                'as the root disk of the server. The root volume will not '
                'be deleted when the server is deleted. This option is '
                'mutually exclusive with the ``--volume`` and ``--snapshot`` '
                'options.'
            ),
        )
        # TODO(stephenfin): Remove this in the v7.0
        parser.add_argument(
            '--block-device-mapping',
            metavar='<dev-name=mapping>',
            action=BDMLegacyAction,
            default=[],
            # NOTE(RuiChen): Add '\n' to the end of line to improve formatting;
            # see cliff's _SmartHelpFormatter for more details.
            help=_(
                '**Deprecated** Create a block device on the server.\n'
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
                'Replaced by --block-device'
            ),
        )
        parser.add_argument(
            '--block-device',
            metavar='<block-device>',
            action=BDMAction,
            dest='block_devices',
            default=[],
            help=_(
                'Create a block device on the server.\n'
                'Either a path to a JSON file or a CSV-serialized string '
                'describing the block device mapping.\n'
                'The following keys are accepted for both:\n'
                'uuid=<uuid>: UUID of the volume, snapshot or ID '
                '(required if using source image, snapshot or volume),\n'
                'source_type=<source_type>: source type '
                '(one of: image, snapshot, volume, blank),\n'
                'destination_type=<destination_type>: destination type '
                '(one of: volume, local) (optional),\n'
                'disk_bus=<disk_bus>: device bus '
                '(one of: uml, lxc, virtio, ...) (optional),\n'
                'device_type=<device_type>: device type '
                '(one of: disk, cdrom, etc. (optional),\n'
                'device_name=<device_name>: name of the device (optional),\n'
                'volume_size=<volume_size>: size of the block device in MiB '
                '(for swap) or GiB (for everything else) (optional),\n'
                'guest_format=<guest_format>: format of device (optional),\n'
                'boot_index=<boot_index>: index of disk used to order boot '
                'disk '
                '(required for volume-backed instances),\n'
                'delete_on_termination=<true|false>: whether to delete the '
                'volume upon deletion of server (optional),\n'
                'tag=<tag>: device metadata tag (optional),\n'
                'volume_type=<volume_type>: type of volume to create (name or '
                'ID) when source if blank, image or snapshot and dest is '
                'volume (optional)'
            ),
        )
        parser.add_argument(
            '--swap',
            metavar='<swap>',
            type=int,
            help=(
                "Create and attach a local swap block device of <swap_size> "
                "MiB."
            ),
        )
        parser.add_argument(
            '--ephemeral',
            metavar='<size=size[,format=format]>',
            action=parseractions.MultiKeyValueAction,
            dest='ephemerals',
            default=[],
            required_keys=['size'],
            optional_keys=['format'],
            help=(
                "Create and attach a local ephemeral block device of <size> "
                "GiB and format it to <format>."
            ),
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            dest='nics',
            action=NICAction,
            key='net-id',
            help=_(
                "Create a NIC on the server and connect it to network. "
                "Specify option multiple times to create multiple NICs. "
                "This is a wrapper for the '--nic net-id=<network>' "
                "parameter that provides simple syntax for the standard "
                "use case of connecting a new server to a given network. "
                "For more advanced use cases, refer to the '--nic' parameter."
            ),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            dest='nics',
            action=NICAction,
            key='port-id',
            help=_(
                "Create a NIC on the server and connect it to port. "
                "Specify option multiple times to create multiple NICs. "
                "This is a wrapper for the '--nic port-id=<port>' "
                "parameter that provides simple syntax for the standard "
                "use case of connecting a new server to a given port. For "
                "more advanced use cases, refer to the '--nic' parameter."
            ),
        )
        parser.add_argument(
            '--no-network',
            dest='nics',
            action=NoneNICAction,
            help=_(
                "Do not attach a network to the server. "
                "This is a wrapper for the '--nic none' option that provides "
                "a simple syntax for disabling network connectivity for a new "
                "server. "
                "For more advanced use cases, refer to the '--nic' parameter. "
                "(supported by --os-compute-api-version 2.37 or above)"
            ),
        )
        parser.add_argument(
            '--auto-network',
            dest='nics',
            action=AutoNICAction,
            help=_(
                "Automatically allocate a network to the server. "
                "This is the default network allocation policy. "
                "This is a wrapper for the '--nic auto' option that provides "
                "a simple syntax for enabling automatic configuration of "
                "network connectivity for a new server. "
                "For more advanced use cases, refer to the '--nic' parameter. "
                "(supported by --os-compute-api-version 2.37 or above)"
            ),
        )
        parser.add_argument(
            '--nic',
            metavar="<net-id=net-uuid,port-id=port-uuid,v4-fixed-ip=ip-addr,"
            "v6-fixed-ip=ip-addr,tag=tag,auto,none>",
            dest='nics',
            action=NICAction,
            # NOTE(RuiChen): Add '\n' to the end of line to improve formatting;
            # see cliff's _SmartHelpFormatter for more details.
            help=_(
                "Create a NIC on the server.\n"
                "NIC in the format:\n"
                "net-id=<net-uuid>: attach NIC to network with this UUID,\n"
                "port-id=<port-uuid>: attach NIC to port with this UUID,\n"
                "v4-fixed-ip=<ip-addr>: IPv4 fixed address for NIC (optional),"
                "\n"
                "v6-fixed-ip=<ip-addr>: IPv6 fixed address for NIC (optional),"
                "\n"
                "tag: interface metadata tag (optional) "
                "(supported by --os-compute-api-version 2.43 or above),\n"
                "none: (v2.37+) no network is attached,\n"
                "auto: (v2.37+) the compute service will automatically "
                "allocate a network.\n"
                "\n"
                "Specify option multiple times to create multiple NICs.\n"
                "Specifying a --nic of auto or none cannot be used with any "
                "other --nic value.\n"
                "Either net-id or port-id must be provided, but not both."
            ),
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_(
                'Set the password to this server. '
                'This option requires cloud support.'
            ),
        )
        secgroups = parser.add_mutually_exclusive_group()
        secgroups.add_argument(
            '--no-security-group',
            dest='security_groups',
            action='store_const',
            const=[],
            help=_(
                'Do not associate a security group with ports attached to '
                'this server. This does not affect the security groups '
                'associated with pre-existing ports.'
            ),
        )
        secgroups.add_argument(
            '--security-group',
            metavar='<security-group>',
            action='append',
            dest='security_groups',
            help=_(
                'Security group to associate with ports attached to this '
                'server (name or ID) '
                '(repeat option to set multiple groups)'
            ),
        )
        parser.add_argument(
            '--key-name',
            metavar='<key-name>',
            help=_('Keypair to inject into this server'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Set a property on this server '
                '(repeat option to set multiple values)'
            ),
        )
        parser.add_argument(
            '--file',
            metavar='<dest-filename=source-filename>',
            action='append',
            default=[],
            help=_(
                'File(s) to inject into image before boot '
                '(repeat option to set multiple files) '
                '(supported by --os-compute-api-version 2.57 or below)'
            ),
        )
        parser.add_argument(
            '--user-data',
            metavar='<user-data>',
            help=_('User data file to serve from the metadata server'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                'Set description for the server '
                '(supported by --os-compute-api-version 2.19 or above)'
            ),
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<zone-name>',
            help=_(
                'Select an availability zone for the server. '
                'Host and node are optional parameters. '
                'Availability zone in the format '
                '<zone-name>:<host-name>:<node-name>, '
                '<zone-name>::<node-name>, <zone-name>:<host-name> '
                'or <zone-name>'
            ),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_(
                'Requested host to create servers. '
                '(admin only) '
                '(supported by --os-compute-api-version 2.74 or above)'
            ),
        )
        parser.add_argument(
            '--hypervisor-hostname',
            metavar='<hypervisor-hostname>',
            help=_(
                'Requested hypervisor hostname to create servers. '
                '(admin only) '
                '(supported by --os-compute-api-version 2.74 or above)'
            ),
        )
        parser.add_argument(
            '--server-group',
            metavar='<server-group>',
            help=_(
                "Server group to create the server within "
                "(this is an alias for '--hint group=<server-group-id>')"
            ),
        )
        parser.add_argument(
            '--hint',
            metavar='<key=value>',
            action=parseractions.KeyValueAppendAction,
            dest='hints',
            default={},
            help=_('Hints for the scheduler'),
        )
        config_drive_group = parser.add_mutually_exclusive_group()
        config_drive_group.add_argument(
            '--use-config-drive',
            action='store_true',
            dest='config_drive',
            help=_("Enable config drive."),
        )
        config_drive_group.add_argument(
            '--no-config-drive',
            action='store_false',
            dest='config_drive',
            help=_("Disable config drive."),
        )
        # TODO(stephenfin): Drop support in the next major version bump after
        # Victoria
        config_drive_group.add_argument(
            '--config-drive',
            metavar='<config-drive-volume>|True',
            default=False,
            help=_(
                "**Deprecated** Use specified volume as the config drive, "
                "or 'True' to use an ephemeral drive. Replaced by "
                "'--use-config-drive'."
            ),
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
            '--tag',
            metavar='<tag>',
            action='append',
            default=[],
            dest='tags',
            help=_(
                'Tags for the server. '
                'Specify multiple times to add multiple tags. '
                '(supported by --os-compute-api-version 2.52 or above)'
            ),
        )
        parser.add_argument(
            '--hostname',
            metavar='<hostname>',
            help=_(
                'Hostname configured for the server in the metadata service. '
                'If unset, a hostname will be automatically generated from '
                'the server name. '
                'A utility such as cloud-init is required to propagate the '
                'hostname in the metadata service to the guest OS itself. '
                '(supported by --os-compute-api-version 2.90 or above)'
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for build to complete'),
        )
        parser.add_argument(
            '--trusted-image-cert',
            metavar='<trusted-cert-id>',
            action='append',
            dest='trusted_image_certs',
            help=_(
                'Trusted image certificate IDs used to validate certificates '
                'during the image signature verification process. '
                'May be specified multiple times to pass multiple trusted '
                'image certificate IDs. '
                '(supported by --os-compute-api-version 2.63 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume
        image_client = self.app.client_manager.image

        # Lookup parsed_args.image
        image = None
        if parsed_args.image:
            image = image_client.find_image(
                parsed_args.image, ignore_missing=False
            )

        if not image and parsed_args.image_properties:

            def _match_image(image_api, wanted_properties):
                image_list = image_api.images()
                images_matched = []
                for img in image_list:
                    img_dict = {}

                    # exclude any unhashable entries
                    img_dict_items = list(img.items())
                    if img.properties:
                        img_dict_items.extend(list(img.properties.items()))
                    for key, value in img_dict_items:
                        try:
                            {key, value}
                        except TypeError:
                            if key != 'properties':
                                LOG.debug(
                                    'Skipped the \'%s\' attribute. '
                                    'That cannot be compared. '
                                    '(image: %s, value: %s)',
                                    key,
                                    img.id,
                                    value,
                                )
                            pass
                        else:
                            img_dict[key] = value

                    if all(
                        k in img_dict and img_dict[k] == v
                        for k, v in wanted_properties.items()
                    ):
                        images_matched.append(img)

                return images_matched

            images = _match_image(image_client, parsed_args.image_properties)
            if len(images) > 1:
                img_uuid_list = [str(image.id) for image in images]
                LOG.warning(
                    'Multiple matching images: %(img_uuid_list)s\n'
                    'Using image: %(chosen_one)s',
                    {
                        'img_uuid_list': img_uuid_list,
                        'chosen_one': img_uuid_list[0],
                    },
                )
            if images:
                image = images[0]
            else:
                msg = _(
                    'No images match the property expected by --image-property'
                )
                raise exceptions.CommandError(msg)

        volume = None
        if parsed_args.volume:
            # --volume and --boot-from-volume are mutually exclusive.
            if parsed_args.boot_from_volume:
                msg = _('--volume is not allowed with --boot-from-volume')
                raise exceptions.CommandError(msg)

            volume = utils.find_resource(
                volume_client.volumes,
                parsed_args.volume,
            ).id

        snapshot = None
        if parsed_args.snapshot:
            # --snapshot and --boot-from-volume are mutually exclusive.
            if parsed_args.boot_from_volume:
                msg = _('--snapshot is not allowed with --boot-from-volume')
                raise exceptions.CommandError(msg)

            snapshot = utils.find_resource(
                volume_client.volume_snapshots,
                parsed_args.snapshot,
            ).id

        flavor = compute_client.find_flavor(
            parsed_args.flavor, ignore_missing=False
        )

        if parsed_args.file:
            if sdk_utils.supports_microversion(compute_client, '2.57'):
                msg = _(
                    'Personality files are deprecated and are not supported '
                    'for --os-compute-api-version greater than 2.56; use '
                    'user data instead'
                )
                raise exceptions.CommandError(msg)

        files = {}
        for f in parsed_args.file:
            dst, src = f.split('=', 1)
            try:
                files[dst] = open(src, 'rb')
            except OSError as e:
                msg = _("Can't open '%(source)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {'source': src, 'exception': e}
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

        user_data = None
        if parsed_args.user_data:
            try:
                with open(parsed_args.user_data, 'rb') as fh:
                    # TODO(stephenfin): SDK should do this for us
                    user_data = base64.b64encode(fh.read()).decode('utf-8')
            except OSError as e:
                msg = _("Can't open '%(data)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {'data': parsed_args.user_data, 'exception': e}
                )

        if parsed_args.description:
            if not sdk_utils.supports_microversion(compute_client, '2.19'):
                msg = _(
                    '--os-compute-api-version 2.19 or greater is '
                    'required to support the --description option'
                )
                raise exceptions.CommandError(msg)

        block_device_mapping_v2 = []
        if parsed_args.boot_from_volume:
            # Tell nova to create a root volume from the image provided.
            if not image:
                msg = _(
                    "An image (--image or --image-property) is required "
                    "to support --boot-from-volume option"
                )
                raise exceptions.CommandError(msg)
            block_device_mapping_v2 = [
                {
                    'uuid': image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'volume',
                    'volume_size': parsed_args.boot_from_volume,
                }
            ]
            # If booting from volume we do not pass an image to compute.
            image = None
        elif image:
            block_device_mapping_v2 = [
                {
                    'uuid': image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                }
            ]
        elif volume:
            block_device_mapping_v2 = [
                {
                    'uuid': volume,
                    'boot_index': 0,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                }
            ]
        elif snapshot:
            block_device_mapping_v2 = [
                {
                    'uuid': snapshot,
                    'boot_index': 0,
                    'source_type': 'snapshot',
                    'destination_type': 'volume',
                    'delete_on_termination': False,
                }
            ]

        if parsed_args.swap:
            block_device_mapping_v2.append(
                {
                    'boot_index': -1,
                    'source_type': 'blank',
                    'destination_type': 'local',
                    'guest_format': 'swap',
                    'volume_size': parsed_args.swap,
                    'delete_on_termination': True,
                }
            )

        for mapping in parsed_args.ephemerals:
            block_device_mapping_dict = {
                'boot_index': -1,
                'source_type': 'blank',
                'destination_type': 'local',
                'delete_on_termination': True,
                'volume_size': mapping['size'],
            }

            if 'format' in mapping:
                block_device_mapping_dict['guest_format'] = mapping['format']

            block_device_mapping_v2.append(block_device_mapping_dict)

        # Handle block device by device name order, like: vdb -> vdc -> vdd
        for mapping in parsed_args.block_device_mapping:
            # The 'uuid' field isn't necessarily a UUID yet; let's validate it
            # just in case
            if mapping['source_type'] == 'volume':
                volume_id = utils.find_resource(
                    volume_client.volumes,
                    mapping['uuid'],
                ).id
                mapping['uuid'] = volume_id
            elif mapping['source_type'] == 'snapshot':
                snapshot_id = utils.find_resource(
                    volume_client.volume_snapshots,
                    mapping['uuid'],
                ).id
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
                image_id = image_client.find_image(
                    mapping['uuid'],
                    ignore_missing=False,
                ).id
                mapping['uuid'] = image_id

            block_device_mapping_v2.append(mapping)

        for mapping in parsed_args.block_devices:
            if 'boot_index' in mapping:
                try:
                    mapping['boot_index'] = int(mapping['boot_index'])
                except ValueError:
                    msg = _(
                        'The boot_index key of --block-device should be an '
                        'integer'
                    )
                    raise exceptions.CommandError(msg)

            if 'tag' in mapping and (
                not sdk_utils.supports_microversion(compute_client, '2.42')
            ):
                msg = _(
                    '--os-compute-api-version 2.42 or greater is '
                    'required to support the tag key of --block-device'
                )
                raise exceptions.CommandError(msg)

            if 'volume_type' in mapping and (
                not sdk_utils.supports_microversion(compute_client, '2.67')
            ):
                msg = _(
                    '--os-compute-api-version 2.67 or greater is '
                    'required to support the volume_type key of --block-device'
                )
                raise exceptions.CommandError(msg)

            if 'source_type' in mapping:
                if mapping['source_type'] not in (
                    'volume',
                    'image',
                    'snapshot',
                    'blank',
                ):
                    msg = _(
                        'The source_type key of --block-device should be one '
                        'of: volume, image, snapshot, blank'
                    )
                    raise exceptions.CommandError(msg)
            else:
                mapping['source_type'] = 'blank'

            if 'destination_type' in mapping:
                if mapping['destination_type'] not in ('local', 'volume'):
                    msg = _(
                        'The destination_type key of --block-device should be '
                        'one of: local, volume'
                    )
                    raise exceptions.CommandError(msg)
            else:
                if mapping['source_type'] in ('blank',):
                    mapping['destination_type'] = 'local'
                else:  # volume, image, snapshot
                    mapping['destination_type'] = 'volume'

            if 'delete_on_termination' in mapping:
                try:
                    value = envvars.bool_from_str(
                        mapping['delete_on_termination'],
                        strict=True,
                    )
                except ValueError:
                    msg = _(
                        'The delete_on_termination key of --block-device '
                        'should be a boolean-like value'
                    )
                    raise exceptions.CommandError(msg)

                mapping['delete_on_termination'] = value
            else:
                if mapping['destination_type'] == 'local':
                    mapping['delete_on_termination'] = True

            block_device_mapping_v2.append(mapping)

        if not any(
            [bdm.get('boot_index') == 0 for bdm in block_device_mapping_v2]
        ):
            msg = _(
                'An image (--image, --image-property) or bootable volume '
                '(--volume, --snapshot, --block-device) is required'
            )
            raise exceptions.CommandError(msg)

        # Default to empty list if nothing was specified and let nova
        # decide the default behavior.
        networks: ty.Union[str, list[dict[str, str]], None] = []

        if 'auto' in parsed_args.nics or 'none' in parsed_args.nics:
            if len(parsed_args.nics) > 1:
                msg = _(
                    'Specifying a --nic of auto or none cannot '
                    'be used with any other --nic, --network '
                    'or --port value.'
                )
                raise exceptions.CommandError(msg)

            if not sdk_utils.supports_microversion(compute_client, '2.37'):
                msg = _(
                    '--os-compute-api-version 2.37 or greater is '
                    'required to support explicit auto-allocation of a '
                    'network or to disable network allocation'
                )
                raise exceptions.CommandError(msg)

            networks = parsed_args.nics[0]
        else:
            for nic in parsed_args.nics:
                if 'tag' in nic:
                    if not sdk_utils.supports_microversion(
                        compute_client, '2.43'
                    ):
                        msg = _(
                            '--os-compute-api-version 2.43 or greater is '
                            'required to support the --nic tag field'
                        )
                        raise exceptions.CommandError(msg)

                if self.app.client_manager.is_network_endpoint_enabled():
                    network_client = self.app.client_manager.network

                    if nic['net-id']:
                        net = network_client.find_network(
                            nic['net-id'],
                            ignore_missing=False,
                        )
                        nic['net-id'] = net.id

                    if nic['port-id']:
                        port = network_client.find_port(
                            nic['port-id'],
                            ignore_missing=False,
                        )
                        nic['port-id'] = port.id
                else:
                    if nic['net-id']:
                        net = compute_v2.find_network(
                            compute_client,
                            nic['net-id'],
                        )
                        nic['net-id'] = net['id']

                    if nic['port-id']:
                        msg = _(
                            "Can't create server with port specified "
                            "since network endpoint not enabled"
                        )
                        raise exceptions.CommandError(msg)

                # convert from the novaclient-derived "NIC" view to the actual
                # "network" view
                network: dict[str, str] = {}

                if nic['net-id']:
                    network['uuid'] = nic['net-id']

                if nic['port-id']:
                    network['port'] = nic['port-id']

                if nic['v4-fixed-ip']:
                    network['fixed'] = nic['v4-fixed-ip']
                elif nic['v6-fixed-ip']:
                    network['fixed'] = nic['v6-fixed-ip']

                if nic.get('tag'):  # tags are optional
                    network['tag'] = nic['tag']

                networks.append(network)  # type: ignore[union-attr]

        if not parsed_args.nics and sdk_utils.supports_microversion(
            compute_client, '2.37'
        ):
            # Compute API version >= 2.37 requires a value, so default to
            # 'auto' to maintain legacy behavior if a nic wasn't specified.
            networks = 'auto'

        # Check security group(s) exist and convert ID to name
        security_groups = None
        if parsed_args.security_groups is not None:
            security_groups = []
            if self.app.client_manager.is_network_endpoint_enabled():
                network_client = self.app.client_manager.network
                for security_group in parsed_args.security_groups:
                    sg = network_client.find_security_group(
                        security_group, ignore_missing=False
                    )
                    # Use security group ID to avoid multiple security group
                    # have same name in neutron networking backend
                    security_groups.append({'name': sg.id})
            else:  # nova-network
                for security_group in parsed_args.security_groups:
                    sg = compute_v2.find_security_group(
                        compute_client, security_group
                    )
                    security_groups.append({'name': sg['name']})

        hints = {}
        for key, values in parsed_args.hints.items():
            # only items with multiple values will result in a list
            if len(values) == 1:
                hints[key] = values[0]
            else:
                hints[key] = values

        if parsed_args.server_group:
            server_group_obj = compute_client.find_server_group(
                parsed_args.server_group, ignore_missing=False
            )
            hints['group'] = server_group_obj.id

        if isinstance(parsed_args.config_drive, bool):
            # NOTE(stephenfin): The API doesn't accept False as a value :'(
            config_drive = parsed_args.config_drive or None
        else:
            # TODO(stephenfin): Remove when we drop support for
            # '--config-drive'
            if str(parsed_args.config_drive).lower() in ("true", "1"):
                config_drive = True
            elif str(parsed_args.config_drive).lower() in (
                "false",
                "0",
                "",
                "none",
            ):
                config_drive = None
            else:
                config_drive = parsed_args.config_drive

        kwargs = {
            'name': parsed_args.server_name,
            'image_id': image.id if image else '',
            'flavor_id': flavor.id,
            'min_count': parsed_args.min,
            'max_count': parsed_args.max,
        }

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.availability_zone:
            kwargs['availability_zone'] = parsed_args.availability_zone

        if parsed_args.password:
            kwargs['admin_password'] = parsed_args.password

        if parsed_args.properties:
            kwargs['metadata'] = parsed_args.properties

        if parsed_args.key_name:
            kwargs['key_name'] = parsed_args.key_name

        if user_data:
            kwargs['user_data'] = user_data

        if files:
            kwargs['personality'] = files

        if security_groups is not None:
            kwargs['security_groups'] = security_groups

        if block_device_mapping_v2:
            kwargs['block_device_mapping'] = block_device_mapping_v2

        if hints:
            kwargs['scheduler_hints'] = hints

        if networks is not None:
            kwargs['networks'] = networks

        if config_drive is not None:
            kwargs['config_drive'] = config_drive

        if parsed_args.tags:
            if not sdk_utils.supports_microversion(compute_client, '2.52'):
                msg = _(
                    '--os-compute-api-version 2.52 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

            kwargs['tags'] = parsed_args.tags

        if parsed_args.host:
            if not sdk_utils.supports_microversion(compute_client, '2.74'):
                msg = _(
                    '--os-compute-api-version 2.74 or greater is required to '
                    'support the --host option'
                )
                raise exceptions.CommandError(msg)

            kwargs['host'] = parsed_args.host

        if parsed_args.hypervisor_hostname:
            if not sdk_utils.supports_microversion(compute_client, '2.74'):
                msg = _(
                    '--os-compute-api-version 2.74 or greater is required to '
                    'support the --hypervisor-hostname option'
                )
                raise exceptions.CommandError(msg)

            kwargs['hypervisor_hostname'] = parsed_args.hypervisor_hostname

        if parsed_args.hostname:
            if not sdk_utils.supports_microversion(compute_client, '2.90'):
                msg = _(
                    '--os-compute-api-version 2.90 or greater is required to '
                    'support the --hostname option'
                )
                raise exceptions.CommandError(msg)

            kwargs['hostname'] = parsed_args.hostname

        # TODO(stephenfin): Handle OS_TRUSTED_IMAGE_CERTIFICATE_IDS
        if parsed_args.trusted_image_certs:
            if not (image and not parsed_args.boot_from_volume):
                msg = _(
                    '--trusted-image-cert option is only supported for '
                    'servers booted directly from images'
                )
                raise exceptions.CommandError(msg)
            if not sdk_utils.supports_microversion(compute_client, '2.63'):
                msg = _(
                    '--os-compute-api-version 2.63 or greater is required to '
                    'support the --trusted-image-cert option'
                )
                raise exceptions.CommandError(msg)

            certs = parsed_args.trusted_image_certs
            kwargs['trusted_image_certificates'] = certs

        LOG.debug('boot_kwargs: %s', kwargs)

        # Wrap the call to catch exceptions in order to close files
        try:
            server = compute_client.create_server(**kwargs)
        finally:
            # Clean up open files - make sure they are not strings
            for f in files:
                if hasattr(f, 'close'):
                    f.close()

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.get_server,
                server.id,
                callback=_show_progress,
            ):
                self.app.stdout.write('\n')
            else:
                msg = _('Error creating server: %s') % parsed_args.server_name
                raise exceptions.CommandError(msg)

        data = _prep_server_detail(compute_client, image_client, server)
        return zip(*sorted(data.items()))


class CreateServerDump(command.Command):
    """Create a dump file in server(s)

    Trigger crash dump in server(s) with features like kdump in Linux.
    It will create a dump file in the server(s) dumping the server(s)'
    memory, and also crash the server(s). This is contingent on guest operating
    system support, and the location of the dump file inside the guest will
    depend on the exact guest operating system.

    This command requires ``--os-compute-api-version`` 2.17 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to create dump file (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for name_or_id in parsed_args.server:
            server = compute_client.find_server(name_or_id)
            server.trigger_crash_dump(compute_client)


class DeleteServer(command.Command):
    _description = _("Delete server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs="+",
            help=_('Server(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_('Force delete server(s)'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=envvars.boolenv('ALL_PROJECTS'),
            help=_(
                'Delete server(s) in another project by name (admin only)'
                '(can be specified using the ALL_PROJECTS envvar)'
            ),
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
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            server_obj = compute_client.find_server(
                server,
                ignore_missing=False,
                all_projects=parsed_args.all_projects,
            )

            compute_client.delete_server(server_obj, force=parsed_args.force)

            if parsed_args.wait:
                try:
                    compute_client.wait_for_delete(
                        server_obj, callback=_show_progress
                    )
                except sdk_exceptions.ResourceTimeout:
                    msg = _('Error deleting server: %s') % server_obj.id
                    raise exceptions.CommandError(msg)


class PercentAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        if nargs == 0:
            raise ValueError(
                'nargs for store actions must be != 0; if you '
                'have nothing to store, actions such as store '
                'true or store const may be more appropriate'
            )

        if const is not None:
            raise ValueError('const does not make sense for PercentAction')

        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        x = int(values)
        if not 0 < x <= 100:
            raise argparse.ArgumentError(self, "Must be between 0 and 100")
        setattr(namespace, self.dest, x)


class ListServer(command.Lister):
    _description = _("List servers")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            help=_(
                'Regular expression to match IPv6 addresses. Note '
                'that this option only applies for non-admin users '
                'when using ``--os-compute-api-version`` 2.5 or greater.'
            ),
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
        # taken from 'task_and_vm_state_from_status' function in nova
        # the API sadly reports these in upper case and while it would be
        # wonderful to plaster over this ugliness client-side, there are
        # already users in the wild doing this in upper case that we need to
        # support
        parser.add_argument(
            '--status',
            metavar='<status>',
            choices=(
                'ACTIVE',
                'BUILD',
                'DELETED',
                'ERROR',
                'HARD_REBOOT',
                'MIGRATING',
                'PASSWORD',
                'PAUSED',
                'REBOOT',
                'REBUILD',
                'RESCUE',
                'RESIZE',
                'REVERT_RESIZE',
                'SHELVED',
                'SHELVED_OFFLOADED',
                'SHUTOFF',
                'SOFT_DELETED',
                'SUSPENDED',
                'VERIFY_RESIZE',
            ),
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
            default=envvars.boolenv('ALL_PROJECTS'),
            help=_(
                'Include all projects (admin only) '
                '(can be specified using the ALL_PROJECTS envvar)'
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Search by project (admin only) (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                'Search by user (name or ID) '
                '(admin only before microversion 2.83)'
            ),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--deleted',
            action='store_true',
            default=False,
            help=_('Only display deleted servers (admin only)'),
        )
        parser.add_argument(
            '--availability-zone',
            default=None,
            help=_(
                'Search by availability zone '
                '(admin only before microversion 2.83)'
            ),
        )
        parser.add_argument(
            '--key-name',
            help=_(
                'Search by keypair name (admin only before microversion 2.83)'
            ),
        )
        config_drive_group = parser.add_mutually_exclusive_group()
        config_drive_group.add_argument(
            '--config-drive',
            action='store_true',
            dest='has_config_drive',
            default=None,
            help=_(
                'Only display servers with a config drive attached '
                '(admin only before microversion 2.83)'
            ),
        )
        # NOTE(gibi): this won't actually do anything until bug 1871409 is
        # fixed and the REST API is cleaned up regarding the values of
        # config_drive
        config_drive_group.add_argument(
            '--no-config-drive',
            action='store_false',
            dest='has_config_drive',
            help=_(
                'Only display servers without a config drive attached '
                '(admin only before microversion 2.83)'
            ),
        )
        parser.add_argument(
            '--progress',
            action=PercentAction,
            default=None,
            help=_(
                'Search by progress value (%%) '
                '(admin only before microversion 2.83)'
            ),
        )
        parser.add_argument(
            '--vm-state',
            metavar='<state>',
            # taken from 'InstanceState' object field in nova
            choices=(
                'active',
                'building',
                'deleted',
                'error',
                'paused',
                'stopped',
                'suspended',
                'rescued',
                'resized',
                'shelved',
                'shelved_offloaded',
                'soft-delete',
            ),
            help=_(
                'Search by vm_state value '
                '(admin only before microversion 2.83)'
            ),
        )
        parser.add_argument(
            '--task-state',
            metavar='<state>',
            # taken from 'InstanceTaskState' object field in nova
            choices=(
                'block_device_mapping',
                'deleting',
                'image_backup',
                'image_pending_upload',
                'image_snapshot',
                'image_snapshot_pending',
                'image_uploading',
                'migrating',
                'networking',
                'pausing',
                'powering-off',
                'powering-on',
                'rebooting',
                'reboot_pending',
                'reboot_started',
                'reboot_pending_hard',
                'reboot_started_hard',
                'rebooting_hard',
                'rebuilding',
                'rebuild_block_device_mapping',
                'rebuild_spawning',
                'rescuing',
                'resize_confirming',
                'resize_finish',
                'resize_migrated',
                'resize_migrating',
                'resize_prep',
                'resize_reverting',
                'restoring',
                'resuming',
                'scheduling',
                'shelving',
                'shelving_image_pending_upload',
                'shelving_image_uploading',
                'shelving_offloading',
                'soft-deleting',
                'spawning',
                'suspending',
                'updating_password',
                'unpausing',
                'unrescuing',
                'unshelving',
            ),
            help=_(
                'Search by task_state value '
                '(admin only before microversion 2.83)'
            ),
        )
        parser.add_argument(
            '--power-state',
            metavar='<state>',
            # taken from 'InstancePowerState' object field in nova
            choices=(
                'pending',
                'running',
                'paused',
                'shutdown',
                'crashed',
                'suspended',
            ),
            help=_(
                'Search by power_state value '
                '(admin only before microversion 2.83)'
            ),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        name_lookup_group = parser.add_mutually_exclusive_group()
        name_lookup_group.add_argument(
            '-n',
            '--no-name-lookup',
            action='store_true',
            default=False,
            help=_(
                'Skip flavor and image name lookup. '
                'Mutually exclusive with "--name-lookup-one-by-one" option.'
            ),
        )
        name_lookup_group.add_argument(
            '--name-lookup-one-by-one',
            action='store_true',
            default=False,
            help=_(
                'When looking up flavor and image names, look them up '
                'one by one as needed instead of all together (default). '
                'Mutually exclusive with "--no-name-lookup|-n" option.'
            ),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        parser.add_argument(
            '--changes-before',
            metavar='<changes-before>',
            default=None,
            help=_(
                "List only servers changed before a certain point of time. "
                "The provided time should be an ISO 8061 formatted time "
                "(e.g., 2016-03-05T06:27:59Z). "
                '(supported by --os-compute-api-version 2.66 or above)'
            ),
        )
        parser.add_argument(
            '--changes-since',
            metavar='<changes-since>',
            default=None,
            help=_(
                "List only servers changed after a certain point of time. "
                "The provided time should be an ISO 8061 formatted time "
                "(e.g., 2016-03-04T06:27:59Z)."
            ),
        )
        lock_group = parser.add_mutually_exclusive_group()
        lock_group.add_argument(
            '--locked',
            action='store_true',
            default=False,
            help=_(
                'Only display locked servers '
                '(supported by --os-compute-api-version 2.73 or above)'
            ),
        )
        lock_group.add_argument(
            '--unlocked',
            action='store_true',
            default=False,
            help=_(
                'Only display unlocked servers '
                '(supported by --os-compute-api-version 2.73 or above)'
            ),
        )
        parser.add_argument(
            '--tags',
            metavar='<tag>',
            action='append',
            default=[],
            dest='tags',
            help=_(
                'Only list servers with the specified tag. '
                'Specify multiple times to filter on multiple tags. '
                '(supported by --os-compute-api-version 2.26 or above)'
            ),
        )
        parser.add_argument(
            '--not-tags',
            metavar='<tag>',
            action='append',
            default=[],
            dest='not_tags',
            help=_(
                'Only list servers without the specified tag. '
                'Specify multiple times to filter on multiple tags. '
                '(supported by --os-compute-api-version 2.26 or above)'
            ),
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
            flavor = compute_client.find_flavor(
                parsed_args.flavor, ignore_missing=False
            )
            flavor_id = flavor.id

        # Nova only supports list servers searching by image ID. So if a
        # image name is given, map it to ID.
        image_id = None
        if parsed_args.image:
            image_id = image_client.find_image(
                parsed_args.image,
                ignore_missing=False,
            ).id

        search_opts = {
            'reservation_id': parsed_args.reservation_id,
            'ip': parsed_args.ip,
            'ip6': parsed_args.ip6,
            'name': parsed_args.name,
            'status': parsed_args.status,
            'flavor': flavor_id,
            'image': image_id,
            'compute_host': parsed_args.host,
            'project_id': project_id,
            'all_projects': parsed_args.all_projects,
            'user_id': user_id,
            'deleted': parsed_args.deleted,
            'changes-before': parsed_args.changes_before,
            'changes-since': parsed_args.changes_since,
        }

        if parsed_args.instance_name is not None:
            search_opts['instance_name'] = parsed_args.instance_name

        if parsed_args.availability_zone:
            search_opts['availability_zone'] = parsed_args.availability_zone

        if parsed_args.key_name:
            search_opts['key_name'] = parsed_args.key_name

        if parsed_args.has_config_drive is not None:
            search_opts['config_drive'] = parsed_args.has_config_drive

        if parsed_args.progress is not None:
            search_opts['progress'] = str(parsed_args.progress)

        if parsed_args.vm_state:
            search_opts['vm_state'] = parsed_args.vm_state

        if parsed_args.task_state:
            search_opts['task_state'] = parsed_args.task_state

        if parsed_args.power_state:
            # taken from 'InstancePowerState' object field in nova
            power_state = {
                'pending': 0,
                'running': 1,
                'paused': 3,
                'shutdown': 4,
                'crashed': 6,
                'suspended': 7,
            }[parsed_args.power_state]
            search_opts['power_state'] = power_state

        if parsed_args.tags:
            if not sdk_utils.supports_microversion(compute_client, '2.26'):
                msg = _(
                    '--os-compute-api-version 2.26 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

            search_opts['tags'] = ','.join(parsed_args.tags)

        if parsed_args.not_tags:
            if not sdk_utils.supports_microversion(compute_client, '2.26'):
                msg = _(
                    '--os-compute-api-version 2.26 or greater is required to '
                    'support the --not-tag option'
                )
                raise exceptions.CommandError(msg)

            search_opts['not-tags'] = ','.join(parsed_args.not_tags)

        if parsed_args.locked:
            if not sdk_utils.supports_microversion(compute_client, '2.73'):
                msg = _(
                    '--os-compute-api-version 2.73 or greater is required to '
                    'support the --locked option'
                )
                raise exceptions.CommandError(msg)

            search_opts['locked'] = True
        elif parsed_args.unlocked:
            if not sdk_utils.supports_microversion(compute_client, '2.73'):
                msg = _(
                    '--os-compute-api-version 2.73 or greater is required to '
                    'support the --unlocked option'
                )
                raise exceptions.CommandError(msg)

            search_opts['locked'] = False

        if parsed_args.limit is not None:
            search_opts['limit'] = parsed_args.limit
            search_opts['paginated'] = False

        LOG.debug('search options: %s', search_opts)

        if search_opts['changes-before']:
            if not sdk_utils.supports_microversion(compute_client, '2.66'):
                msg = _('--os-compute-api-version 2.66 or later is required')
                raise exceptions.CommandError(msg)

            try:
                iso8601.parse_date(search_opts['changes-before'])
            except (TypeError, iso8601.ParseError):
                raise exceptions.CommandError(
                    _('Invalid changes-before value: %s')
                    % search_opts['changes-before']
                )

        if search_opts['changes-since']:
            try:
                iso8601.parse_date(search_opts['changes-since'])
            except (TypeError, iso8601.ParseError):
                msg = _('Invalid changes-since value: %s')
                raise exceptions.CommandError(
                    msg % search_opts['changes-since']
                )

        columns: tuple[str, ...] = (
            'id',
            'name',
            'status',
        )
        column_headers: tuple[str, ...] = (
            'ID',
            'Name',
            'Status',
        )

        if parsed_args.long:
            columns += (
                'task_state',
                'power_state',
            )
            column_headers += (
                'Task State',
                'Power State',
            )

        columns += ('addresses',)
        column_headers += ('Networks',)

        if parsed_args.long:
            columns += (
                'image_name',
                'image_id',
            )
            column_headers += (
                'Image Name',
                'Image ID',
            )
        else:
            if parsed_args.no_name_lookup:
                columns += ('image_id',)
            else:
                columns += ('image_name',)
            column_headers += ('Image',)

        # microversion 2.47 puts the embedded flavor into the server response
        # body but omits the id, so if not present we just expose the original
        # flavor name in the output
        if sdk_utils.supports_microversion(compute_client, '2.47'):
            columns += ('flavor_name',)
            column_headers += ('Flavor',)
        else:
            if parsed_args.long:
                columns += (
                    'flavor_name',
                    'flavor_id',
                )
                column_headers += (
                    'Flavor Name',
                    'Flavor ID',
                )
            else:
                if parsed_args.no_name_lookup:
                    columns += ('flavor_id',)
                else:
                    columns += ('flavor_name',)
                column_headers += ('Flavor',)

        if parsed_args.long:
            columns += (
                'availability_zone',
                'pinned_availability_zone',
                'hypervisor_hostname',
                'metadata',
            )
            column_headers += (
                'Availability Zone',
                'Pinned Availability Zone',
                'Host',
                'Properties',
            )

        # support for additional columns
        if parsed_args.columns:
            for c in parsed_args.columns:
                if c in ('Project ID', 'project_id'):
                    columns += ('project_id',)
                    column_headers += ('Project ID',)
                if c in ('User ID', 'user_id'):
                    columns += ('user_id',)
                    column_headers += ('User ID',)
                if c in ('Created At', 'created_at'):
                    columns += ('created_at',)
                    column_headers += ('Created At',)
                if c in ('Security Groups', 'security_groups'):
                    columns += ('security_groups_name',)
                    column_headers += ('Security Groups',)
                if c in ("Task State", "task_state"):
                    columns += ('task_state',)
                    column_headers += ('Task State',)
                if c in ("Power State", "power_state"):
                    columns += ('power_state',)
                    column_headers += ('Power State',)
                if c in ("Image ID", "image_id"):
                    columns += ('Image ID',)
                    column_headers += ('Image ID',)
                if c in ("Flavor ID", "flavor_id"):
                    columns += ('flavor_id',)
                    column_headers += ('Flavor ID',)
                if c in ('Availability Zone', "availability_zone"):
                    columns += ('availability_zone',)
                    column_headers += ('Availability Zone',)
                if c in (
                    'pinned_availability_zone',
                    "Pinned Availability Zone",
                ):
                    columns += ('Pinned Availability Zone',)
                    column_headers += ('Pinned Availability Zone',)
                if c in ('Host', "host"):
                    columns += ('hypervisor_hostname',)
                    column_headers += ('Host',)
                if c in ('Properties', "properties"):
                    columns += ('Metadata',)
                    column_headers += ('Properties',)

            # remove duplicates
            column_headers = tuple(dict.fromkeys(column_headers))
            columns = tuple(dict.fromkeys(columns))

        if parsed_args.marker is not None:
            # Check if both "--marker" and "--deleted" are used.
            # In that scenario a lookup is not needed as the marker
            # needs to be an ID, because find_resource does not
            # handle deleted resources
            if parsed_args.deleted:
                marker_id = parsed_args.marker
            else:
                marker_id = compute_client.find_server(
                    parsed_args.marker, ignore_missing=False
                ).id
            search_opts['marker'] = marker_id

        data = list(compute_client.servers(**search_opts))

        images = {}
        flavors = {}
        if data and not parsed_args.no_name_lookup:
            # partial responses from down cells will not have an image
            # attribute so we use getattr
            image_ids = {
                s.image['id']
                for s in data
                if getattr(s, 'image', None) and s.image.get('id')
            }

            # create a dict that maps image_id to image object, which is used
            # to display the "Image Name" column. Note that 'image.id' can be
            # empty for BFV instances and 'image' can be missing entirely if
            # there are infra failures
            if parsed_args.name_lookup_one_by_one or image_id:
                for image_id in image_ids:
                    try:
                        images[image_id] = image_client.get_image(image_id)
                    except Exception:  # noqa: S110
                        # retrieving image names is not crucial, so we swallow
                        # any exceptions
                        pass
            else:
                try:
                    # some deployments can have *loads* of images so we only
                    # want to list the ones we care about. It would be better
                    # to only return the *fields* we care about (name) but
                    # glance doesn't support that
                    # NOTE(stephenfin): This could result in super long URLs
                    # but it seems unlikely to cause issues. Apache supports
                    # URL lengths of up to 8190 characters by default, which
                    # should allow for more than 220 unique image ID (different
                    # servers are likely use the same image ID) in the filter.
                    # Who'd need more than that in a single command?
                    images_list = image_client.images(
                        id=f"in:{','.join(image_ids)}"
                    )
                    for i in images_list:
                        images[i.id] = i
                except Exception:  # noqa: S110
                    # retrieving image names is not crucial, so we swallow any
                    # exceptions
                    pass

            # create a dict that maps flavor_id to flavor object, which is used
            # to display the "Flavor Name" column. Note that 'flavor.id' is not
            # present on microversion 2.47 or later and 'flavor' won't be
            # present if there are infra failures
            if parsed_args.name_lookup_one_by_one or flavor_id:
                for f_id in {
                    s.flavor['id']
                    for s in data
                    if s.flavor and s.flavor.get('id')
                }:
                    try:
                        flavors[f_id] = compute_client.find_flavor(
                            f_id, ignore_missing=False
                        )
                    except Exception:  # noqa: S110
                        # retrieving flavor names is not crucial, so we swallow
                        # any exceptions
                        pass
            else:
                try:
                    flavors_list = compute_client.flavors(is_public=None)
                    for i in flavors_list:
                        flavors[i.id] = i
                except Exception:  # noqa: S110
                    # retrieving flavor names is not crucial, so we swallow any
                    # exceptions
                    pass

        # Populate image_name, image_id, flavor_name and flavor_id attributes
        # of server objects so that we can display those columns.
        for s in data:
            if sdk_utils.supports_microversion(compute_client, '2.69'):
                # NOTE(tssurya): From 2.69, we will have the keys 'flavor'
                # and 'image' missing in the server response during
                # infrastructure failure situations.
                # For those servers with partial constructs we just skip the
                # processing of the image and flavor information.
                if not hasattr(s, 'image') or not hasattr(s, 'flavor'):
                    continue

            if 'id' in s.image and s.image.id is not None:
                image = images.get(s.image['id'])
                if image:
                    s.image_name = image.name
                s.image_id = s.image['id']
            else:
                # NOTE(melwitt): An server booted from a volume will have no
                # image associated with it. We fill in the Image Name and ID
                # with "N/A (booted from volume)" to help users who want to be
                # able to grep for boot-from-volume servers when using the CLI.
                s.image_name = IMAGE_STRING_FOR_BFV
                s.image_id = IMAGE_STRING_FOR_BFV

            if not sdk_utils.supports_microversion(compute_client, '2.47'):
                flavor = flavors.get(s.flavor['id'])
                if flavor:
                    s.flavor_name = flavor.name
                s.flavor_id = s.flavor['id']
            else:
                s.flavor_name = s.flavor['original_name']

        # Add a list with security group name as attribute
        for s in data:
            if hasattr(s, 'security_groups') and s.security_groups is not None:
                s.security_groups_name = [x["name"] for x in s.security_groups]
            else:
                s.security_groups_name = []

        # The host_status field contains the status of the compute host the
        # server is on. It is only returned by the API when the nova-api
        # policy allows. Users can look at the host_status field when, for
        # example, their server has status ACTIVE but is unresponsive. The
        # host_status field can indicate a possible problem on the host
        # it's on, providing useful information to a user in this
        # situation.
        if (
            sdk_utils.supports_microversion(compute_client, '2.16')
            and parsed_args.long
        ):
            if any([s.host_status is not None for s in data]):
                columns += ('Host Status',)
                column_headers += ('Host Status',)

        table = (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    mixed_case_fields=(
                        'task_state',
                        'power_state',
                        'availability_zone',
                        'host',
                    ),
                    formatters={
                        'power_state': PowerStateColumn,
                        'addresses': AddressesColumn,
                        'metadata': format_columns.DictColumn,
                        'security_groups_name': format_columns.ListColumn,
                        'hypervisor_hostname': HostColumn,
                    },
                )
                for s in data
            ),
        )
        return table


class LockServer(command.Command):
    _description = _(
        """Lock server(s)

A non-admin user will not be able to execute actions."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            help=_(
                'Reason for locking the server(s) '
                '(supported by --os-compute-api-version 2.73 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        kwargs = {}
        if parsed_args.reason:
            if not sdk_utils.supports_microversion(compute_client, '2.73'):
                msg = _(
                    '--os-compute-api-version 2.73 or greater is required to '
                    'use the --reason option'
                )
                raise exceptions.CommandError(msg)

            kwargs['locked_reason'] = parsed_args.reason

        for server in parsed_args.server:
            server_id = compute_client.find_server(
                server, ignore_missing=False
            ).id
            compute_client.lock_server(server_id, **kwargs)


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
    _description = _(
        """Migrate server to different host.

A migrate operation is implemented as a resize operation using the same flavor
as the old server. This means that, like resize, migrate works by creating a
new server using the same flavor and copying the contents of the original disk
into a new one. As with resize, the migrate operation is a two-step process for
the user: the first step is to perform the migrate, and the second step is to
either confirm (verify) success and release the old server, or to declare a
revert to release the new server and restart the old one."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--live-migration',
            dest='live_migration',
            action='store_true',
            help=_(
                'Live migrate the server; use the ``--host`` option to '
                'specify a target host for the migration which will be '
                'validated by the scheduler'
            ),
        )
        parser.add_argument(
            '--host',
            metavar='<hostname>',
            help=_(
                'Migrate the server to the specified host. '
                '(supported with --os-compute-api-version 2.30 or above '
                'when used with the --live-migration option) '
                '(supported with --os-compute-api-version 2.56 or above '
                'when used without the --live-migration option)'
            ),
        )
        migration_group = parser.add_mutually_exclusive_group()
        migration_group.add_argument(
            '--shared-migration',
            dest='block_migration',
            action='store_false',
            default=None,
            help=_(
                'Perform a shared live migration '
                '(default before --os-compute-api-version 2.25, auto after)'
            ),
        )
        migration_group.add_argument(
            '--block-migration',
            dest='block_migration',
            action='store_true',
            help=_(
                'Perform a block live migration '
                '(auto-configured from --os-compute-api-version 2.25)'
            ),
        )
        disk_group = parser.add_mutually_exclusive_group()
        disk_group.add_argument(
            '--disk-overcommit',
            action='store_true',
            default=None,
            help=_(
                'Allow disk over-commit on the destination host '
                '(supported with --os-compute-api-version 2.24 or below)'
            ),
        )
        disk_group.add_argument(
            '--no-disk-overcommit',
            dest='disk_overcommit',
            action='store_false',
            help=_(
                'Do not over-commit disk on the destination host (default) '
                '(supported with --os-compute-api-version 2.24 or below)'
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for migrate to complete'),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if parsed_args.live_migration:
            kwargs = {}

            block_migration = parsed_args.block_migration
            if block_migration is None:
                if not sdk_utils.supports_microversion(compute_client, '2.25'):
                    block_migration = False
                else:
                    block_migration = 'auto'

            kwargs['block_migration'] = block_migration

            # Technically we could pass a non-None host with
            # --os-compute-api-version < 2.30 but that is the same thing
            # as the --live option bypassing the scheduler which we don't
            # want to support, so if the user is using --live-migration
            # and --host, we want to enforce that they are using version
            # 2.30 or greater.
            if parsed_args.host and not sdk_utils.supports_microversion(
                compute_client, '2.30'
            ):
                raise exceptions.CommandError(
                    '--os-compute-api-version 2.30 or greater is required '
                    'when using --host'
                )

            # The host parameter is required in the API even if None.
            kwargs['host'] = parsed_args.host

            if not sdk_utils.supports_microversion(compute_client, '2.25'):
                kwargs['disk_overcommit'] = parsed_args.disk_overcommit
                # We can't use an argparse default value because then we can't
                # distinguish between explicit 'False' and unset for the below
                # case (microversion >= 2.25)
                if kwargs['disk_overcommit'] is None:
                    kwargs['disk_overcommit'] = False
            elif parsed_args.disk_overcommit is not None:
                # TODO(stephenfin): Raise an error here in OSC 7.0
                msg = _(
                    'The --disk-overcommit and --no-disk-overcommit '
                    'options are only supported by '
                    '--os-compute-api-version 2.24 or below; this will '
                    'be an error in a future release'
                )
                self.log.warning(msg)

            compute_client.live_migrate_server(server, **kwargs)
        else:  # cold migration
            if parsed_args.block_migration or parsed_args.disk_overcommit:
                raise exceptions.CommandError(
                    "--live-migration must be specified if "
                    "--block-migration or --disk-overcommit is "
                    "specified"
                )
            if parsed_args.host:
                if not sdk_utils.supports_microversion(compute_client, '2.56'):
                    msg = _(
                        '--os-compute-api-version 2.56 or greater is '
                        'required to use --host without --live-migration.'
                    )
                    raise exceptions.CommandError(msg)

            kwargs = {'host': parsed_args.host} if parsed_args.host else {}
            compute_client.migrate_server(server, **kwargs)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.get_server,
                server.id,
                success_status=('active', 'verify_resize'),
                callback=_show_progress,
            ):
                self.app.stdout.write(
                    _(
                        'Complete, check success/failure by '
                        'openstack server migration/event list/show\n'
                    )
                )
            else:
                msg = _('Error migrating server: %s') % server.id
                raise exceptions.CommandError(msg)


class PauseServer(command.Command):
    _description = _("Pause server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
            ).id
            compute_client.pause_server(server_id)


class RebootServer(command.Command):
    _description = _("Perform a hard or soft server reboot")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            const='HARD',
            default='SOFT',
            help=_('Perform a hard reboot'),
        )
        group.add_argument(
            '--soft',
            dest='reboot_type',
            action='store_const',
            const='SOFT',
            default='SOFT',
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
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        server_id = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        ).id
        compute_client.reboot_server(server_id, parsed_args.reboot_type)

        if parsed_args.wait:
            # We use osc-lib's wait_for_status since that allows for a callback
            if utils.wait_for_status(
                compute_client.get_server,
                server_id,
                callback=_show_progress,
            ):
                self.app.stdout.write(_('Complete\n'))
            else:
                msg = _('Error rebooting server: %s') % server_id
                raise exceptions.CommandError(msg)


class RebuildServer(command.ShowOne):
    _description = _("Rebuild server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_(
                'Recreate server from the specified image (name or ID). '
                'Defaults to the currently used one.'
            ),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set the new name of the rebuilt server'),
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_(
                'Set the password on the rebuilt server. '
                'This option requires cloud support.'
            ),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Set a new property on the rebuilt server '
                '(repeat option to set multiple values)'
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                'Set a new description on the rebuilt server '
                '(supported by --os-compute-api-version 2.19 or above)'
            ),
        )
        preserve_ephemeral_group = parser.add_mutually_exclusive_group()
        preserve_ephemeral_group.add_argument(
            '--preserve-ephemeral',
            action='store_true',
            default=None,
            help=_(
                'Preserve the default ephemeral storage partition on rebuild.'
            ),
        )
        preserve_ephemeral_group.add_argument(
            '--no-preserve-ephemeral',
            action='store_false',
            dest='preserve_ephemeral',
            help=_(
                'Do not preserve the default ephemeral storage partition on '
                'rebuild.'
            ),
        )
        key_group = parser.add_mutually_exclusive_group()
        key_group.add_argument(
            '--key-name',
            metavar='<key-name>',
            help=_(
                'Set the key name of key pair on the rebuilt server. '
                'Cannot be specified with the --key-unset option. '
                '(supported by --os-compute-api-version 2.54 or above)'
            ),
        )
        key_group.add_argument(
            '--no-key-name',
            action='store_true',
            dest='no_key_name',
            help=_(
                'Unset the key name of key pair on the rebuilt server. '
                'Cannot be specified with the --key-name option. '
                '(supported by --os-compute-api-version 2.54 or above)'
            ),
        )
        # TODO(stephenfin): Remove this in a future major version bump
        key_group.add_argument(
            '--key-unset',
            action='store_true',
            dest='no_key_name',
            help=argparse.SUPPRESS,
        )
        user_data_group = parser.add_mutually_exclusive_group()
        user_data_group.add_argument(
            '--user-data',
            metavar='<user-data>',
            help=_(
                'Add a new user data file to the rebuilt server. '
                'Cannot be specified with the --no-user-data option. '
                '(supported by --os-compute-api-version 2.57 or above)'
            ),
        )
        user_data_group.add_argument(
            '--no-user-data',
            action='store_true',
            default=False,
            help=_(
                'Remove existing user data when rebuilding server. '
                'Cannot be specified with the --user-data option. '
                '(supported by --os-compute-api-version 2.57 or above)'
            ),
        )
        trusted_certs_group = parser.add_mutually_exclusive_group()
        trusted_certs_group.add_argument(
            '--trusted-image-cert',
            metavar='<trusted-cert-id>',
            action='append',
            dest='trusted_image_certs',
            help=_(
                'Trusted image certificate IDs used to validate certificates '
                'during the image signature verification process. '
                'May be specified multiple times to pass multiple trusted '
                'image certificate IDs. '
                'Cannot be specified with the --no-trusted-certs option. '
                '(supported by --os-compute-api-version 2.63 or above)'
            ),
        )
        trusted_certs_group.add_argument(
            '--no-trusted-image-certs',
            action='store_true',
            default=False,
            help=_(
                'Remove any existing trusted image certificates from the '
                'server. '
                'Cannot be specified with the --trusted-certs option. '
                '(supported by --os-compute-api-version 2.63 or above)'
            ),
        )
        parser.add_argument(
            '--hostname',
            metavar='<hostname>',
            help=_(
                'Hostname configured for the server in the metadata service. '
                'A separate utility running in the guest is required to '
                'propagate changes to this value to the guest OS itself. '
                '(supported by --os-compute-api-version 2.90 or above)'
            ),
        )
        parser.add_argument(
            '--reimage-boot-volume',
            action='store_true',
            dest='reimage_boot_volume',
            default=None,
            help=_(
                'Rebuild a volume-backed server. This will wipe the root '
                'volume data and overwrite it with the provided image. '
                'Defaults to False. '
                '(supported by --os-compute-api-version 2.93 or above)'
            ),
        )
        parser.add_argument(
            '--no-reimage-boot-volume',
            action='store_false',
            dest='reimage_boot_volume',
            default=None,
            help=_(
                'Do not rebuild a volume-backed server. '
                '(supported by --os-compute-api-version 2.93 or above)'
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for rebuild to complete'),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        # If parsed_args.image is not set and if the instance is image backed,
        # default to the currently used one. If the instance is volume backed,
        # it is not trivial to fetch the current image and probably better
        # to error out in this case and ask user to supply the image.
        if parsed_args.image:
            image = image_client.find_image(
                parsed_args.image, ignore_missing=False
            )
        else:
            if not server.image or not server.image.id:
                msg = _(
                    'The --image option is required when rebuilding a '
                    'volume-backed server'
                )
                raise exceptions.CommandError(msg)
            image = image_client.get_image(server.image['id'])

        kwargs = {}

        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name

        if parsed_args.password is not None:
            kwargs['admin_password'] = parsed_args.password

        if parsed_args.preserve_ephemeral is not None:
            kwargs['preserve_ephemeral'] = parsed_args.preserve_ephemeral

        if parsed_args.properties:
            kwargs['metadata'] = parsed_args.properties

        if parsed_args.description:
            if not sdk_utils.supports_microversion(compute_client, '2.19'):
                msg = _(
                    '--os-compute-api-version 2.19 or greater is required to '
                    'support the --description option'
                )
                raise exceptions.CommandError(msg)

            kwargs['description'] = parsed_args.description

        if parsed_args.key_name:
            if not sdk_utils.supports_microversion(compute_client, '2.54'):
                msg = _(
                    '--os-compute-api-version 2.54 or greater is required to '
                    'support the --key-name option'
                )
                raise exceptions.CommandError(msg)

            kwargs['key_name'] = parsed_args.key_name
        elif parsed_args.no_key_name:
            if not sdk_utils.supports_microversion(compute_client, '2.54'):
                msg = _(
                    '--os-compute-api-version 2.54 or greater is required to '
                    'support the --no-key-name option'
                )
                raise exceptions.CommandError(msg)

            kwargs['key_name'] = None

        if parsed_args.user_data:
            if not sdk_utils.supports_microversion(compute_client, '2.54'):
                msg = _(
                    '--os-compute-api-version 2.54 or greater is required to '
                    'support the --user-data option'
                )
                raise exceptions.CommandError(msg)

            try:
                with open(parsed_args.user_data, 'rb') as fh:
                    # TODO(stephenfin): SDK should do this for us
                    user_data = base64.b64encode(fh.read()).decode('utf-8')
            except OSError as e:
                msg = _("Can't open '%(data)s': %(exception)s")
                raise exceptions.CommandError(
                    msg % {'data': parsed_args.user_data, 'exception': e}
                )

            kwargs['user_data'] = user_data
        elif parsed_args.no_user_data:
            if not sdk_utils.supports_microversion(compute_client, '2.54'):
                msg = _(
                    '--os-compute-api-version 2.54 or greater is required to '
                    'support the --no-user-data option'
                )
                raise exceptions.CommandError(msg)

            kwargs['user_data'] = None

        # TODO(stephenfin): Handle OS_TRUSTED_IMAGE_CERTIFICATE_IDS
        if parsed_args.trusted_image_certs:
            if not sdk_utils.supports_microversion(compute_client, '2.63'):
                msg = _(
                    '--os-compute-api-version 2.63 or greater is required to '
                    'support the --trusted-certs option'
                )
                raise exceptions.CommandError(msg)

            certs = parsed_args.trusted_image_certs
            kwargs['trusted_image_certificates'] = certs
        elif parsed_args.no_trusted_image_certs:
            if not sdk_utils.supports_microversion(compute_client, '2.63'):
                msg = _(
                    '--os-compute-api-version 2.63 or greater is required to '
                    'support the --no-trusted-certs option'
                )
                raise exceptions.CommandError(msg)

            kwargs['trusted_image_certificates'] = None

        if parsed_args.hostname:
            if not sdk_utils.supports_microversion(compute_client, '2.90'):
                msg = _(
                    '--os-compute-api-version 2.90 or greater is required to '
                    'support the --hostname option'
                )
                raise exceptions.CommandError(msg)

            kwargs['hostname'] = parsed_args.hostname

        if parsed_args.reimage_boot_volume:
            if not sdk_utils.supports_microversion(compute_client, '2.93'):
                msg = _(
                    '--os-compute-api-version 2.93 or greater is required to '
                    'support the --reimage-boot-volume option'
                )
                raise exceptions.CommandError(msg)
        else:
            # force user to explicitly request reimaging of volume-backed
            # server
            if not server.image or not server.image.id:
                if sdk_utils.supports_microversion(compute_client, '2.93'):
                    msg = (
                        '--reimage-boot-volume is required to rebuild a '
                        'volume-backed server'
                    )
                    raise exceptions.CommandError(msg)
                else:  # microversion < 2.93
                    # attempts to rebuild a volume-backed server before API
                    # microversion 2.93 will fail in all cases except one: if
                    # the user attempts the rebuild with the exact same image
                    # that the server was initially built with. We can't check
                    # for this since we don't have the original image ID to
                    # hand, so we simply warn the user.
                    # TODO(stephenfin): Make this a failure in a future
                    # version
                    self.log.warning(
                        'Attempting to rebuild a volume-backed server using '
                        '--os-compute-api-version 2.92 or earlier, which '
                        'will only succeed if the image is identical to the '
                        'one initially used. This will be an error in a '
                        'future release.'
                    )

        status = getattr(server, 'status', '').lower()
        if status == 'shutoff':
            success_status = ['shutoff']
        elif status in ('error', 'active'):
            success_status = ['active']
        else:
            msg = _("The server status is not ACTIVE, SHUTOFF or ERROR.")
            raise exceptions.CommandError(msg)

        server = compute_client.rebuild_server(server, image, **kwargs)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.get_server,
                server.id,
                callback=_show_progress,
                success_status=success_status,
            ):
                self.app.stdout.write(_('Complete\n'))
            else:
                msg = _('Error rebuilding server: %s') % server.id
                raise exceptions.CommandError(msg)

        data = _prep_server_detail(
            compute_client, image_client, server, refresh=False
        )
        return zip(*sorted(data.items()))


class EvacuateServer(command.ShowOne):
    _description = _(
        """Evacuate a server to a different host.

This command is used to recreate a server after the host it was on has failed.
It can only be used if the compute service that manages the server is down.
This command should only be used by an admin after they have confirmed that the
instance is not running on the failed host.

If the server instance was created with an ephemeral root disk on non-shared
storage the server will be rebuilt using the original glance image preserving
the ports and any attached data volumes.

If the server uses boot for volume or has its root disk on shared storage the
root disk will be preserved and reused for the evacuated instance on the new
host."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for evacuation to complete'),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            default=None,
            help=_(
                'Set the preferred host on which to rebuild the evacuated '
                'server. The host will be validated by the scheduler. '
                '(supported by --os-compute-api-version 2.29 or above)'
            ),
        )
        shared_storage_group = parser.add_mutually_exclusive_group()
        shared_storage_group.add_argument(
            '--password',
            metavar='<password>',
            default=None,
            help=_(
                'Set the password on the evacuated instance. This option is '
                'mutually exclusive with the --shared-storage option. '
                'This option requires cloud support.'
            ),
        )
        shared_storage_group.add_argument(
            '--shared-storage',
            action='store_true',
            dest='shared_storage',
            help=_(
                'Indicate that the instance is on shared storage. '
                'This will be auto-calculated with '
                '--os-compute-api-version 2.14 and greater and should not '
                'be used with later microversions. This option is mutually '
                'exclusive with the --password option'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        if parsed_args.host:
            if not sdk_utils.supports_microversion(compute_client, '2.29'):
                msg = _(
                    '--os-compute-api-version 2.29 or later is required '
                    'to specify a preferred host.'
                )
                raise exceptions.CommandError(msg)

        if parsed_args.shared_storage:
            if sdk_utils.supports_microversion(compute_client, '2.14'):
                msg = _(
                    '--os-compute-api-version 2.13 or earlier is required '
                    'to specify shared-storage.'
                )
                raise exceptions.CommandError(msg)

        kwargs = {
            'host': parsed_args.host,
            'admin_pass': parsed_args.password,
        }

        if not sdk_utils.supports_microversion(compute_client, '2.14'):
            kwargs['on_shared_storage'] = parsed_args.shared_storage

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        compute_client.evacuate_server(server, **kwargs)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.get_server,
                server.id,
                callback=_show_progress,
            ):
                self.app.stdout.write(_('Complete\n'))
            else:
                msg = _('Error evacuating server: %s') % server.id
                raise exceptions.CommandError(msg)

        data = _prep_server_detail(compute_client, image_client, server)
        return zip(*sorted(data.items()))


class RemoveFixedIP(command.Command):
    _description = _("Remove fixed IP address from server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        compute_client.remove_fixed_ip_from_server(
            server, parsed_args.ip_address
        )


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
        obj = client.find_ip(
            parsed_args.ip_address,
            ignore_missing=False,
        )

        client.update_ip(obj, port_id=None)

    def take_action_compute(self, client, parsed_args):
        server = client.find_server(parsed_args.server, ignore_missing=False)
        client.remove_floating_ip_from_server(server, parsed_args.ip_address)


class RemovePort(command.Command):
    _description = _("Remove port from server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            port_id = network_client.find_port(
                parsed_args.port, ignore_missing=False
            ).id
        else:
            port_id = parsed_args.port

        compute_client.delete_server_interface(
            port_id,
            server=server,
            ignore_missing=False,
        )


class RemoveNetwork(command.Command):
    _description = _("Remove all ports of a network from server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network
            net_id = network_client.find_network(
                parsed_args.network, ignore_missing=False
            ).id
        else:
            net_id = parsed_args.network

        for inf in compute_client.server_interfaces(server):
            if inf.net_id == net_id:
                compute_client.delete_server_interface(
                    inf.port_id,
                    server=server,
                )


class RemoveServerSecurityGroup(command.Command):
    _description = _("Remove security group from server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'security_groups',
            metavar='<security-group>',
            nargs='+',
            help=_(
                'Security group(s) to remove from server (name or ID) '
                '(repeat option to remove multiple groups)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        if self.app.client_manager.is_network_endpoint_enabled():
            # the server handles both names and IDs for neutron SGs, so just
            # pass things through
            security_groups = parsed_args.security_groups
        else:
            # however, if using nova-network then it needs names, not IDs
            security_groups = []
            for security_group in parsed_args.security_groups:
                security_groups.append(
                    compute_v2.find_security_group(
                        compute_client, security_group
                    )['name']
                )

        errors = 0
        for security_group in security_groups:
            try:
                compute_client.remove_security_group_from_server(
                    server,
                    {'name': security_group},
                )
            except sdk_exceptions.HttpException as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to remove security group with name or ID "
                        "'%(security_group)s' from server '%(server)s': %(e)s"
                    ),
                    {
                        'security_group': security_group,
                        'server': server.id,
                        'e': e,
                    },
                )

        if errors > 0:
            msg = _(
                "%(errors)d of %(total)d security groups were not removed."
            ) % {'errors': errors, 'total': len(security_groups)}
            raise exceptions.CommandError(msg)


class RemoveServerVolume(command.Command):
    _description = _(
        """Remove volume from server.

Specify ``--os-compute-api-version 2.20`` or higher to remove a
volume from a server with status ``SHELVED`` or ``SHELVED_OFFLOADED``."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        volume_client = self.app.client_manager.sdk_connection.volume

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        volume = volume_client.find_volume(
            parsed_args.volume,
            ignore_missing=False,
        )

        compute_client.delete_volume_attachment(
            volume,
            server,
            ignore_missing=False,
        )


class RescueServer(command.Command):
    _description = _(
        """Put server in rescue mode.

Specify ``--os-compute-api-version 2.87`` or higher to rescue a
server booted from a volume."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            help=_(
                'Image (name or ID) to use for the rescue mode '
                '(defaults to the currently used one)'
            ),
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_(
                'Set the password on the rescued instance '
                '(requires cloud support)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        image_ref = None
        if parsed_args.image:
            image_ref = image_client.find_image(
                parsed_args.image, ignore_missing=False
            ).id

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        compute_client.rescue_server(
            server, admin_pass=parsed_args.password, image_ref=image_ref
        )


class ResizeServer(command.Command):
    _description = _(
        """Scale server to a new flavor.

A resize operation is implemented by creating a new server and copying the
contents of the original disk into a new one. It is a two-step process for the
user: the first step is to perform the resize, and the second step is to either
confirm (verify) success and release the old server or to declare a revert to
release the new server and restart the old one."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        phase_group = parser.add_mutually_exclusive_group()
        phase_group.add_argument(
            '--flavor',
            metavar='<flavor>',
            help=_('Resize server to specified flavor'),
        )
        phase_group.add_argument(
            '--confirm',
            action="store_true",
            help=_(
                "**Deprecated** Confirm server resize is complete. "
                "Replaced by the 'openstack server resize confirm' and "
                "'openstack server migration confirm' commands"
            ),
        )
        phase_group.add_argument(
            '--revert',
            action="store_true",
            help=_(
                '**Deprecated** Restore server state before resize. '
                "Replaced by the 'openstack server resize revert' and "
                "'openstack server migration revert' commands"
            ),
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
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        if parsed_args.flavor:
            if not server.image:
                self.log.warning(
                    _(
                        "The root disk size in flavor will not be applied "
                        "while booting from a persistent volume."
                    )
                )
            flavor = compute_client.find_flavor(
                parsed_args.flavor, ignore_missing=False
            )
            compute_client.resize_server(server, flavor)
            if parsed_args.wait:
                if not utils.wait_for_status(
                    compute_client.get_server,
                    server.id,
                    success_status=('active', 'verify_resize'),
                    callback=_show_progress,
                ):
                    msg = _('Error resizing server: %s') % server.id
                    raise exceptions.CommandError(msg)

                self.app.stdout.write(_('Complete\n'))
        elif parsed_args.confirm:
            self.log.warning(
                _(
                    "The --confirm option has been deprecated. Please use the "
                    "'openstack server resize confirm' command instead."
                )
            )
            compute_client.confirm_server_resize(server)
        elif parsed_args.revert:
            self.log.warning(
                _(
                    "The --revert option has been deprecated. Please use the "
                    "'openstack server resize revert' command instead."
                )
            )
            compute_client.revert_server_resize(server)


class ResizeConfirm(command.Command):
    _description = _(
        """Confirm server resize.

Confirm (verify) success of resize operation and release the old server."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        compute_client.confirm_server_resize(server)


# TODO(stephenfin): Remove in OSC 7.0
class MigrateConfirm(ResizeConfirm):
    _description = _("DEPRECATED: Use 'server migration confirm' instead.")

    def take_action(self, parsed_args):
        msg = _(
            "The 'server migrate confirm' command has been deprecated in "
            "favour of the 'server migration confirm' command."
        )
        self.log.warning(msg)

        super().take_action(parsed_args)


class ConfirmMigration(ResizeConfirm):
    _description = _(
        """Confirm server migration.

Confirm (verify) success of the migration operation and release the old
server."""
    )


class ResizeRevert(command.Command):
    _description = _(
        """Revert server resize.

Revert the resize operation. Release the new server and restart the old
one."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        compute_client.revert_server_resize(server)


# TODO(stephenfin): Remove in OSC 7.0
class MigrateRevert(ResizeRevert):
    _description = _("DEPRECATED: Use 'server migration revert' instead.")

    def take_action(self, parsed_args):
        msg = _(
            "The 'server migrate revert' command has been deprecated in "
            "favour of the 'server migration revert' command."
        )
        self.log.warning(msg)

        super().take_action(parsed_args)


class RevertMigration(ResizeRevert):
    _description = _(
        """Revert server migration.

Revert the migration operation. Release the new server and restart the old
one."""
    )


class RestoreServer(command.Command):
    _description = _("Restore server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
            ).id
            compute_client.restore_server(server_id)


class ResumeServer(command.Command):
    _description = _("Resume server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
            ).id
            compute_client.resume_server(server_id)


class SetServer(command.Command):
    _description = _("Set server properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        password_group = parser.add_mutually_exclusive_group()
        password_group.add_argument(
            '--password',
            help=_(
                'Set the server password. This option requires cloud support.'
            ),
        )
        password_group.add_argument(
            '--no-password',
            action='store_true',
            help=_(
                'Clear the admin password for the server from the metadata '
                'service; note that this action does not actually change the '
                'server password'
            ),
        )
        # TODO(stephenfin): Remove this in a future major version
        password_group.add_argument(
            '--root-password',
            action="store_true",
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Property to add/change for this server '
                '(repeat option to set multiple properties)'
            ),
        )
        parser.add_argument(
            '--state',
            metavar='<state>',
            choices=['active', 'error'],
            help=_(
                'New server state '
                '**WARNING** This can result in instances that are no longer '
                'usable and should be used with caution '
                '(admin only)'
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                'New server description '
                '(supported by --os-compute-api-version 2.19 or above)'
            ),
        )
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            action='append',
            default=[],
            dest='tags',
            help=_(
                'Tag for the server. '
                'Specify multiple times to add multiple tags. '
                '(supported by --os-compute-api-version 2.26 or above)'
            ),
        )
        parser.add_argument(
            '--hostname',
            metavar='<hostname>',
            help=_(
                'Hostname configured for the server in the metadata service. '
                'A separate utility running in the guest is required to '
                'propagate changes to this value to the guest OS itself. '
                '(supported by --os-compute-api-version 2.90 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if parsed_args.description:
            if not sdk_utils.supports_microversion(compute_client, '2.19'):
                msg = _(
                    '--os-compute-api-version 2.19 or greater is required to '
                    'support the --description option'
                )
                raise exceptions.CommandError(msg)

        if parsed_args.tags:
            if not sdk_utils.supports_microversion(compute_client, '2.26'):
                msg = _(
                    '--os-compute-api-version 2.26 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

        if parsed_args.hostname:
            if not sdk_utils.supports_microversion(compute_client, '2.90'):
                msg = _(
                    '--os-compute-api-version 2.90 or greater is required to '
                    'support the --hostname option'
                )
                raise exceptions.CommandError(msg)

        update_kwargs = {}

        if parsed_args.name:
            update_kwargs['name'] = parsed_args.name

        if parsed_args.description:
            update_kwargs['description'] = parsed_args.description

        if parsed_args.hostname:
            update_kwargs['hostname'] = parsed_args.hostname

        if update_kwargs:
            compute_client.update_server(server, **update_kwargs)

        if parsed_args.properties:
            compute_client.set_server_metadata(
                server, **parsed_args.properties
            )

        if parsed_args.state:
            compute_client.reset_server_state(server, state=parsed_args.state)

        if parsed_args.root_password:
            p1 = getpass.getpass(_('New password: '))
            p2 = getpass.getpass(_('Retype new password: '))
            if p1 == p2:
                compute_client.change_server_password(server, p1)
            else:
                msg = _("Passwords do not match, password unchanged")
                raise exceptions.CommandError(msg)
        elif parsed_args.password:
            compute_client.change_server_password(server, parsed_args.password)
        elif parsed_args.no_password:
            compute_client.clear_server_password(server)

        if parsed_args.tags:
            for tag in parsed_args.tags:
                compute_client.add_tag_to_server(server, tag=tag)


class ShelveServer(command.Command):
    """Shelve and optionally offload server(s).

    Shelving a server creates a snapshot of the server and stores this
    snapshot before shutting down the server. This shelved server can then be
    offloaded or deleted from the host, freeing up remaining resources on the
    host, such as network interfaces. Shelved servers can be unshelved,
    restoring the server from the snapshot. Shelving is therefore useful where
    users wish to retain the UUID and IP of a server, without utilizing other
    resources or disks.

    Most clouds are configured to automatically offload shelved servers
    immediately or after a small delay. For clouds where this is not
    configured, or where the delay is larger, offloading can be manually
    specified. This is an admin-only operation by default.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'servers',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to shelve (name or ID)'),
        )
        parser.add_argument(
            '--offload',
            action='store_true',
            default=False,
            help=_(
                'Remove the shelved server(s) from the host (admin only). '
                'Invoking this option on an unshelved server(s) will result '
                'in the server being shelved first'
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help=_('Wait for shelve and/or offload operation to complete'),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        server_ids = []

        for server in parsed_args.servers:
            server_obj = compute_client.find_server(
                server,
                ignore_missing=False,
            )
            if server_obj.status.lower() in ('shelved', 'shelved_offloaded'):
                continue

            server_ids.append(server_obj.id)

            compute_client.shelve_server(server_obj.id)

        # if we don't have to wait, either because it was requested explicitly
        # or is required implicitly, then our job is done
        if not parsed_args.wait and not parsed_args.offload:
            return

        for server_id in server_ids:
            # We use osc-lib's wait_for_status since that allows for a callback
            # TODO(stephenfin): We should wait for these in parallel using e.g.
            # https://review.opendev.org/c/openstack/osc-lib/+/762503/
            if not utils.wait_for_status(
                compute_client.get_server,
                server_id,
                success_status=('shelved', 'shelved_offloaded'),
                callback=_show_progress,
            ):
                msg = _('Error shelving server: %s') % server_id
                raise exceptions.CommandError(msg)

        if not parsed_args.offload:
            return

        for server_id in server_ids:
            server_obj = compute_client.get_server(server_id)
            if server_obj.status.lower() == 'shelved_offloaded':
                continue

            compute_client.shelve_offload_server(server_id)

        if not parsed_args.wait:
            return

        for server_id in server_ids:
            # We use osc-lib's wait_for_status since that allows for a callback
            # TODO(stephenfin): We should wait for these in parallel using e.g.
            # https://review.opendev.org/c/openstack/osc-lib/+/762503/
            if not utils.wait_for_status(
                compute_client.get_server,
                server_id,
                success_status=('shelved_offloaded',),
                callback=_show_progress,
            ):
                msg = _('Error offloading shelved server: %s') % server_id
                raise exceptions.CommandError(msg)


class ShowServer(command.ShowOne):
    _description = _(
        """Show server details.

Specify ``--os-compute-api-version 2.47`` or higher to see the embedded flavor
information for the server."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        # TODO(stephenfin): This should be a separate command, not a flag
        diagnostics_group = parser.add_mutually_exclusive_group()
        diagnostics_group.add_argument(
            '--diagnostics',
            action='store_true',
            default=False,
            help=_('Display server diagnostics information'),
        )
        diagnostics_group.add_argument(
            '--topology',
            action='store_true',
            default=False,
            help=_(
                'Include topology information in the output '
                '(supported by --os-compute-api-version 2.78 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
            details=True,
        )

        if parsed_args.diagnostics:
            data = compute_client.get_server_diagnostics(server)
            return zip(*sorted(data.items()))

        topology = None
        if parsed_args.topology:
            if not sdk_utils.supports_microversion(compute_client, '2.78'):
                msg = _(
                    '--os-compute-api-version 2.78 or greater is required to '
                    'support the --topology option'
                )
                raise exceptions.CommandError(msg)

            topology = server.fetch_topology(compute_client)

        data = _prep_server_detail(
            compute_client, image_client, server, refresh=False
        )
        if topology:
            data['topology'] = format_columns.DictColumn(topology)
        return zip(*sorted(data.items()))


class SshServer(command.Command):
    _description = _("SSH to server")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        # Deprecated during the Yoga cycle
        parser.add_argument(
            '--login',
            '-l',
            metavar='<login-name>',
            help=argparse.SUPPRESS,
        )
        # Deprecated during the Yoga cycle
        parser.add_argument(
            '--port',
            '-p',
            metavar='<port>',
            type=int,
            help=argparse.SUPPRESS,
        )
        # Deprecated during the Yoga cycle
        parser.add_argument(
            '--identity',
            '-i',
            metavar='<keyfile>',
            help=argparse.SUPPRESS,
        )
        # Deprecated during the Yoga cycle
        parser.add_argument(
            '--option',
            '-o',
            metavar='<config-options>',
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
        # Deprecated during the Yoga cycle
        parser.add_argument(
            '-v',
            dest='verbose',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            'ssh_args',
            nargs='*',
            metavar='-- <standard ssh args>',
            help=(
                'Any argument or option that ssh allows. '
                'Use -- once between openstackclient args and SSH args.'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        # first, handle the deprecated options
        if any(
            (
                parsed_args.port,
                parsed_args.identity,
                parsed_args.option,
                parsed_args.login,
                parsed_args.verbose,
            )
        ):
            msg = _(
                'The ssh options have been deprecated. The ssh equivalent '
                'options can be used instead as arguments after "--" on '
                'the command line.'
            )
            self.log.warning(msg)

        ip_address_family = [4, 6]
        if parsed_args.ipv4:
            ip_address_family = [4]
        if parsed_args.ipv6:
            ip_address_family = [6]

        args = parsed_args.ssh_args[:]

        if parsed_args.port:
            args.extend(['-p', str(parsed_args.port)])

        if parsed_args.identity:
            args.extend(['-i', parsed_args.identity])

        if parsed_args.option:
            args.extend(['-o', parsed_args.option])

        if parsed_args.login:
            login = parsed_args.login
            args.extend(['-l', login])
        elif '-l' not in args:
            login = self.app.client_manager.auth_ref.username
            args.extend(['-l', login])

        if parsed_args.verbose:
            args.append('-v')

        ip_address = _get_ip_address(
            server.addresses,
            parsed_args.address_type,
            ip_address_family,
        )

        cmd = ' '.join(['ssh', ip_address] + args)
        LOG.debug(f"ssh command: {cmd}")
        # we intentionally pass through user-provided arguments and run this in
        # the user's shell
        os.system(cmd)  # noqa: S605


class StartServer(command.Command):
    _description = _("Start server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs="+",
            help=_('Server(s) to start (name or ID)'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=envvars.boolenv('ALL_PROJECTS'),
            help=_(
                'Start server(s) in another project by name (admin only) '
                '(can be specified using the ALL_PROJECTS envvar)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
                details=False,
                all_projects=parsed_args.all_projects,
            ).id

            compute_client.start_server(server_id)


class StopServer(command.Command):
    _description = _("Stop server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs="+",
            help=_('Server(s) to stop (name or ID)'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=envvars.boolenv('ALL_PROJECTS'),
            help=_(
                'Stop server(s) in another project by name (admin only) '
                '(can be specified using the ALL_PROJECTS envvar)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        for server in parsed_args.server:
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
                details=False,
                all_projects=parsed_args.all_projects,
            ).id
            compute_client.stop_server(server_id)


class SuspendServer(command.Command):
    _description = _("Suspend server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
            ).id
            compute_client.suspend_server(server_id)


class UnlockServer(command.Command):
    _description = _("Unlock server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
            ).id
            compute_client.unlock_server(server_id)


class UnpauseServer(command.Command):
    _description = _("Unpause server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            server_id = compute_client.find_server(
                server,
                ignore_missing=False,
            ).id
            compute_client.unpause_server(server_id)


class UnrescueServer(command.Command):
    _description = _("Restore server from rescue mode")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )
        compute_client.unrescue_server(server)


class UnsetServer(command.Command):
    _description = _("Unset server properties and tags")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        property_group = parser.add_mutually_exclusive_group()
        property_group.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            dest='properties',
            help=_(
                'Property key to remove from server '
                '(repeat option to remove multiple values)'
            ),
        )
        property_group.add_argument(
            '--all-properties',
            action='store_true',
            help=_('Remove all properties'),
        )
        parser.add_argument(
            '--description',
            dest='description',
            action='store_true',
            help=_(
                'Unset server description '
                '(supported by --os-compute-api-version 2.19 or above)'
            ),
        )
        tag_group = parser.add_mutually_exclusive_group()
        tag_group.add_argument(
            '--tag',
            metavar='<tag>',
            action='append',
            default=[],
            dest='tags',
            help=_(
                'Tag to remove from the server. '
                'Specify multiple times to remove multiple tags. '
                '(supported by --os-compute-api-version 2.26 or above)'
            ),
        )
        tag_group.add_argument(
            '--all-tags',
            action='store_true',
            help=_(
                'Remove all tags '
                '(supported by --os-compute-api-version 2.26 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        if parsed_args.properties or parsed_args.all_properties:
            compute_client.delete_server_metadata(
                server, parsed_args.properties or None
            )

        if parsed_args.description:
            if not sdk_utils.supports_microversion(compute_client, '2.19'):
                msg = _(
                    '--os-compute-api-version 2.19 or greater is required to '
                    'support the --description option'
                )
                raise exceptions.CommandError(msg)

            compute_client.update_server(server, description="")

        if parsed_args.tags or parsed_args.all_tags:
            if not sdk_utils.supports_microversion(compute_client, '2.26'):
                msg = _(
                    '--os-compute-api-version 2.26 or greater is required to '
                    'support the --tag option'
                )
                raise exceptions.CommandError(msg)

            for tag in parsed_args.tags:
                compute_client.remove_tag_from_server(server, tag)

            if parsed_args.all_tags:
                compute_client.remove_tags_from_server(server)


class UnshelveServer(command.Command):
    _description = _("Unshelve server(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            nargs='+',
            help=_('Server(s) to unshelve (name or ID)'),
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--availability-zone',
            default=None,
            help=_(
                'Name of the availability zone in which to unshelve a '
                'SHELVED_OFFLOADED server '
                '(supported by --os-compute-api-version 2.77 or above)'
            ),
        )
        group.add_argument(
            '--no-availability-zone',
            action='store_true',
            default=False,
            help=_(
                'Unpin the availability zone of a SHELVED_OFFLOADED '
                'server. Server will be unshelved on a host without '
                'availability zone constraint '
                '(supported by --os-compute-api-version 2.91 or above)'
            ),
        )
        parser.add_argument(
            '--host',
            default=None,
            help=_(
                'Name of the destination host in which to unshelve a '
                'SHELVED_OFFLOADED server '
                '(supported by --os-compute-api-version 2.91 or above)'
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help=_('Wait for unshelve operation to complete'),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        kwargs = {}

        if parsed_args.availability_zone:
            if not sdk_utils.supports_microversion(compute_client, '2.77'):
                msg = _(
                    '--os-compute-api-version 2.77 or greater is required '
                    'to support the --availability-zone option'
                )
                raise exceptions.CommandError(msg)

            kwargs['availability_zone'] = parsed_args.availability_zone

        if parsed_args.host:
            if not sdk_utils.supports_microversion(compute_client, '2.91'):
                msg = _(
                    '--os-compute-api-version 2.91 or greater is required '
                    'to support the --host option'
                )
                raise exceptions.CommandError(msg)

            kwargs['host'] = parsed_args.host

        if parsed_args.no_availability_zone:
            if not sdk_utils.supports_microversion(compute_client, '2.91'):
                msg = _(
                    '--os-compute-api-version 2.91 or greater is required '
                    'to support the --no-availability-zone option'
                )
                raise exceptions.CommandError(msg)

            kwargs['availability_zone'] = None

        for server in parsed_args.server:
            server_obj = compute_client.find_server(
                server,
                ignore_missing=False,
            )

            if server_obj.status.lower() not in (
                'shelved',
                'shelved_offloaded',
            ):
                continue

            compute_client.unshelve_server(server_obj.id, **kwargs)

            if parsed_args.wait:
                if not utils.wait_for_status(
                    compute_client.get_server,
                    server_obj.id,
                    success_status=('active', 'shutoff'),
                    callback=_show_progress,
                ):
                    msg = _('Error unshelving server: %s') % server_obj.id
                    raise exceptions.CommandError(msg)
