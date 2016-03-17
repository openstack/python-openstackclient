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

"""Port action implementations"""

import argparse
import logging

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils
from openstackclient.i18n import _  # noqa
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'

_formatters = {
    'admin_state_up': _format_admin_state,
    'allowed_address_pairs': utils.format_list_of_dicts,
    'binding_profile': utils.format_dict,
    'binding_vif_details': utils.format_dict,
    'dns_assignment': utils.format_list_of_dicts,
    'extra_dhcp_opts': utils.format_list_of_dicts,
    'fixed_ips': utils.format_list_of_dicts,
    'security_groups': utils.format_list,
}


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    binding_columns = [
        'binding:host_id',
        'binding:profile',
        'binding:vif_details',
        'binding:vif_type',
        'binding:vnic_type',
    ]
    for binding_column in binding_columns:
        if binding_column in columns:
            columns.remove(binding_column)
            columns.append(binding_column.replace('binding:', 'binding_', 1))
    return tuple(sorted(columns))


def _get_attrs(client_manager, parsed_args):
    attrs = {}

    # Handle deprecated options
    # NOTE(dtroyer): --device-id and --host-id were deprecated in Mar 2016.
    #                Do not remove before 3.x release or Mar 2017.
    if parsed_args.device_id:
        attrs['device_id'] = parsed_args.device_id
        LOG.warning(_(
            'The --device-id option is deprecated, '
            'please use --device instead.'
        ))
    if parsed_args.host_id:
        attrs['binding:host_id'] = parsed_args.host_id
        LOG.warning(_(
            'The --host-id option is deprecated, '
            'please use --host instead.'
        ))

    if parsed_args.fixed_ip is not None:
        attrs['fixed_ips'] = parsed_args.fixed_ip
    if parsed_args.device:
        attrs['device_id'] = parsed_args.device
    if parsed_args.device_owner is not None:
        attrs['device_owner'] = parsed_args.device_owner
    if parsed_args.admin_state is not None:
        attrs['admin_state_up'] = parsed_args.admin_state
    if parsed_args.binding_profile is not None:
        attrs['binding:profile'] = parsed_args.binding_profile
    if parsed_args.vnic_type is not None:
        attrs['binding:vnic_type'] = parsed_args.vnic_type
    if parsed_args.host:
        attrs['binding:host_id'] = parsed_args.host

    # The remaining options do not support 'port set' command, so they require
    # additional check
    if 'name' in parsed_args and parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if 'mac_address' in parsed_args and parsed_args.mac_address is not None:
        attrs['mac_address'] = parsed_args.mac_address
    if 'network' in parsed_args and parsed_args.network is not None:
        attrs['network_id'] = parsed_args.network
    if 'project' in parsed_args and parsed_args.project is not None:
        # TODO(singhj): since 'project' logic is common among
        # router, network, port etc., maybe move it to a common file.
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    return attrs


def _prepare_fixed_ips(client_manager, parsed_args):
    """Fix and properly format fixed_ip option.

    Appropriately convert any subnet names to their respective ids.
    Convert fixed_ips in parsed args to be in valid dictionary format:
    {'subnet': 'foo'}.
    """
    client = client_manager.network
    ips = []

    if parsed_args.fixed_ip:
        for ip_spec in parsed_args.fixed_ip:
            if 'subnet' in ip_spec:
                subnet_name_id = ip_spec['subnet']
                if subnet_name_id:
                    _subnet = client.find_subnet(subnet_name_id,
                                                 ignore_missing=False)
                    ip_spec['subnet_id'] = _subnet.id
                    del ip_spec['subnet']

            if 'ip-address' in ip_spec:
                ip_spec['ip_address'] = ip_spec['ip-address']
                del ip_spec['ip-address']

            ips.append(ip_spec)

    if ips:
        parsed_args.fixed_ip = ips


def _add_updatable_args(parser):
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help='Desired IP and/or subnet (name or ID) for this port: '
                 'subnet=<subnet>,ip-address=<ip-address> '
                 '(this option can be repeated)')
        # NOTE(dtroyer): --device-id is deprecated in Mar 2016.  Do not
        #                remove before 3.x release or Mar 2017.
        device_group = parser.add_mutually_exclusive_group()
        device_group.add_argument(
            '--device',
            metavar='<device-id>',
            help='Port device ID',
        )
        device_group.add_argument(
            '--device-id',
            metavar='<device-id>',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--device-owner',
            metavar='<device-owner>',
            help='Device owner of this port')
        parser.add_argument(
            '--vnic-type',
            metavar='<vnic-type>',
            choices=['direct', 'direct-physical', 'macvtap',
                     'normal', 'baremetal'],
            help="VNIC type for this port (direct | direct-physical |"
                 " macvtap | normal | baremetal). If unspecified during"
                 " port creation, default value will be 'normal'.")
        parser.add_argument(
            '--binding-profile',
            metavar='<binding-profile>',
            action=parseractions.KeyValueAction,
            help='Custom data to be passed as binding:profile: <key>=<value> '
                 '(this option can be repeated)')
        # NOTE(dtroyer): --host-id is deprecated in Mar 2016.  Do not
        #                remove before 3.x release or Mar 2017.
        host_group = parser.add_mutually_exclusive_group()
        host_group.add_argument(
            '--host',
            metavar='<host-id>',
            help='Allocate port on host <host-id> (ID only)',
        )
        host_group.add_argument(
            '--host-id',
            metavar='<host-id>',
            help=argparse.SUPPRESS,
        )


class CreatePort(command.ShowOne):
    """Create a new port"""

    def get_parser(self, prog_name):
        parser = super(CreatePort, self).get_parser(prog_name)

        parser.add_argument(
            '--network',
            metavar='<network>',
            required=True,
            help='Network this port belongs to (name or ID)')
        _add_updatable_args(parser)
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            action='store_true',
            default=True,
            help='Enable port (default)',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Disable port',
        )
        parser.add_argument(
            '--mac-address',
            metavar='<mac-address>',
            help='MAC address of this port')
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Owner's project (name or ID)")
        parser.add_argument(
            'name',
            metavar='<name>',
            help='Name of this port')
        identity_common.add_project_domain_option_to_parser(parser)
        # TODO(singhj): Add support for extended options:
        # qos,security groups,dhcp, address pairs
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        _network = client.find_network(parsed_args.network,
                                       ignore_missing=False)
        parsed_args.network = _network.id
        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_port(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return columns, data


class DeletePort(command.Command):
    """Delete port(s)"""

    def get_parser(self, prog_name):
        parser = super(DeletePort, self).get_parser(prog_name)
        parser.add_argument(
            'port',
            metavar="<port>",
            nargs="+",
            help=("Port(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        for port in parsed_args.port:
            res = client.find_port(port)
            client.delete_port(res)


class ListPort(command.Lister):
    """List ports"""

    def get_parser(self, prog_name):
        parser = super(ListPort, self).get_parser(prog_name)
        parser.add_argument(
            '--router',
            metavar='<router>',
            dest='router',
            help='List only ports attached to this router (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'mac_address',
            'fixed_ips',
        )
        column_headers = (
            'ID',
            'Name',
            'MAC Address',
            'Fixed IP Addresses',
        )

        filters = {}
        if parsed_args.router:
            _router = client.find_router(parsed_args.router,
                                         ignore_missing=False)
            filters = {'device_id': _router.id}

        data = client.ports(**filters)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class SetPort(command.Command):
    """Set port properties"""

    def get_parser(self, prog_name):
        parser = super(SetPort, self).get_parser(prog_name)
        _add_updatable_args(parser)
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            action='store_true',
            default=None,
            help='Enable port',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Disable port',
        )
        parser.add_argument(
            'port',
            metavar="<port>",
            help=("Port to modify (name or ID)")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        _prepare_fixed_ips(self.app.client_manager, parsed_args)
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        if attrs == {}:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)

        obj = client.find_port(parsed_args.port, ignore_missing=False)
        client.update_port(obj, **attrs)


class ShowPort(command.ShowOne):
    """Display port details"""

    def get_parser(self, prog_name):
        parser = super(ShowPort, self).get_parser(prog_name)
        parser.add_argument(
            'port',
            metavar="<port>",
            help="Port to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_port(parsed_args.port, ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return columns, data
