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
    columns = list(item.keys())
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
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if parsed_args.share:
        attrs['shared'] = True
    if parsed_args.no_share:
        attrs['shared'] = False

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
    if parsed_args.share:
        attrs['share_address'] = True
    if parsed_args.no_share:
        attrs['share_address'] = False
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
            action='store_true',
            default=None,
            help='Share the network between projects',
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help='Do not share the network between projects',
        )
        return parser

    def update_parser_network(self, parser):
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help='Enable network (default)',
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
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
                 'repeat option to set multiple availability zones)',
        )
        external_router_grp = parser.add_mutually_exclusive_group()
        external_router_grp.add_argument(
            '--external',
            action='store_true',
            help='Set this network as an external network. '
                 'Requires the "external-net" extension to be enabled.')
        external_router_grp.add_argument(
            '--internal',
            action='store_true',
            help='Set this network as an internal network (default)')
        default_router_grp = parser.add_mutually_exclusive_group()
        default_router_grp.add_argument(
            '--default',
            action='store_true',
            help='Specify if this network should be used as '
                 'the default external network')
        default_router_grp.add_argument(
            '--no-default',
            action='store_true',
            help='Do not use the network as the default external network.'
                 'By default, no network is set as an external network.')
        parser.add_argument(
            '--provider-network-type',
            metavar='<provider-network-type>',
            choices=['flat', 'gre', 'local',
                     'vlan', 'vxlan'],
            help='The physical mechanism by which the virtual network '
                 'is implemented. The supported options are: '
                 'flat, gre, local, vlan, vxlan')
        parser.add_argument(
            '--provider-physical-network',
            metavar='<provider-physical-network>',
            dest='physical_network',
            help='Name of the physical network over which the virtual '
                 'network is implemented')
        parser.add_argument(
            '--provider-segment',
            metavar='<provider-segment>',
            dest='segmentation_id',
            help='VLAN ID for VLAN networks or Tunnel ID for GRE/VXLAN '
                 'networks')
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
        if parsed_args.internal:
            attrs['router:external'] = False
        if parsed_args.external:
            attrs['router:external'] = True
            if parsed_args.no_default:
                attrs['is_default'] = False
            if parsed_args.default:
                attrs['is_default'] = True
        if parsed_args.provider_network_type:
            attrs['provider:network_type'] = parsed_args.provider_network_type
        if parsed_args.physical_network:
            attrs['provider:physical_network'] = parsed_args.physical_network
        if parsed_args.segmentation_id:
            attrs['provider:segmentation_id'] = parsed_args.segmentation_id
        obj = client.create_network(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        attrs = _get_attrs_compute(self.app.client_manager, parsed_args)
        obj = client.networks.create(**attrs)
        columns = _get_columns(obj._info)
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
            action='store_true',
            default=None,
            help='Enable network',
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable network',
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help='Share the network between projects',
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
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
        obj = utils.find_resource(
            client.networks,
            parsed_args.network,
        )
        columns = _get_columns(obj._info)
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)
