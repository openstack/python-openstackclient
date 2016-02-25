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

"""Network action implementations"""

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.identity import common as identity_common
from openstackclient.network import common


def _format_admin_state(item):
    return 'UP' if item else 'DOWN'


def _format_router_external(item):
    return 'External' if item else 'Internal'


_formatters = {
    'subnets': utils.format_list,
    'admin_state_up': _format_admin_state,
    'router_external': _format_router_external,
    'availability_zones': utils.format_list,
    'availability_zone_hints': utils.format_list,
}


def _get_columns(item):
    columns = item.keys()
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    if 'router:external' in columns:
        columns.remove('router:external')
        columns.append('router_external')
    return tuple(sorted(columns))


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.admin_state is not None:
        attrs['admin_state_up'] = parsed_args.admin_state
    if parsed_args.shared is not None:
        attrs['shared'] = parsed_args.shared

    # "network set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    # "network set" command doesn't support setting availability zone hints.
    if 'availability_zone_hints' in parsed_args and \
       parsed_args.availability_zone_hints is not None:
        attrs['availability_zone_hints'] = parsed_args.availability_zone_hints

    return attrs


def _get_attrs_compute(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['label'] = str(parsed_args.name)
    if parsed_args.shared is not None:
        attrs['share_address'] = parsed_args.shared
    if parsed_args.subnet is not None:
        attrs['cidr'] = parsed_args.subnet

    return attrs


class CreateNetwork(common.NetworkAndComputeShowOne):
    """Create new network"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New network name',
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            dest='shared',
            action='store_true',
            default=None,
            help='Share the network between projects',
        )
        share_group.add_argument(
            '--no-share',
            dest='shared',
            action='store_false',
            help='Do not share the network between projects',
        )
        return parser

    def update_parser_network(self, parser):
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            action='store_true',
            default=True,
            help='Enable network (default)',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Disable network',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Owner's project (name or ID)"
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--availability-zone-hint',
            action='append',
            dest='availability_zone_hints',
            metavar='<availability-zone>',
            help='Availability Zone in which to create this network '
                 '(requires the Network Availability Zone extension, '
                 'this option can be repeated).',
        )
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--subnet',
            metavar='<subnet>',
            help="IPv4 subnet for fixed IPs (in CIDR notation)"
        )
        return parser

    def take_action_network(self, client, parsed_args):
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_network(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        attrs = _get_attrs_compute(self.app.client_manager, parsed_args)
        obj = client.networks.create(**attrs)
        columns = tuple(sorted(obj._info.keys()))
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)


class DeleteNetwork(common.NetworkAndComputeCommand):
    """Delete network(s)"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'network',
            metavar="<network>",
            nargs="+",
            help=("Network(s) to delete (name or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        for network in parsed_args.network:
            obj = client.find_network(network)
            client.delete_network(obj)

    def take_action_compute(self, client, parsed_args):
        for network in parsed_args.network:
            network = utils.find_resource(
                client.networks,
                network,
            )
            client.networks.delete(network.id)


class ListNetwork(common.NetworkAndComputeLister):
    """List networks"""

    def update_parser_common(self, parser):
        parser.add_argument(
            '--external',
            action='store_true',
            default=False,
            help='List external networks',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action_network(self, client, parsed_args):
        if parsed_args.long:
            columns = (
                'id',
                'name',
                'status',
                'tenant_id',
                'admin_state_up',
                'shared',
                'subnets',
                'provider_network_type',
                'router_external',
                'availability_zones',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Project',
                'State',
                'Shared',
                'Subnets',
                'Network Type',
                'Router Type',
                'Availability Zones',
            )
        else:
            columns = (
                'id',
                'name',
                'subnets'
            )
            column_headers = (
                'ID',
                'Name',
                'Subnets',
            )

        if parsed_args.external:
            args = {'router:external': True}
        else:
            args = {}

        data = client.networks(**args)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))

    def take_action_compute(self, client, parsed_args):
        columns = (
            'id',
            'label',
            'cidr',
        )
        column_headers = (
            'ID',
            'Name',
            'Subnet',
        )

        data = client.networks.list()

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class SetNetwork(command.Command):
    """Set network properties"""

    def get_parser(self, prog_name):
        parser = super(SetNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'network',
            metavar="<network>",
            help=("Network to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set network name',
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            action='store_true',
            default=None,
            help='Enable network',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Disable network',
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            dest='shared',
            action='store_true',
            default=None,
            help='Share the network between projects',
        )
        share_group.add_argument(
            '--no-share',
            dest='shared',
            action='store_false',
            help='Do not share the network between projects',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_network(parsed_args.network, ignore_missing=False)

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        if attrs == {}:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)

        client.update_network(obj, **attrs)
        return


class ShowNetwork(common.NetworkAndComputeShowOne):
    """Show network details"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'network',
            metavar="<network>",
            help=("Network to display (name or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_network(parsed_args.network, ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        network = utils.find_resource(
            client.networks,
            parsed_args.network,
        )
        columns = sorted(network._info.keys())
        data = utils.get_dict_properties(network._info, columns)
        return (columns, data)
