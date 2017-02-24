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

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import sdk_utils


def _format_admin_state(item):
    return 'UP' if item else 'DOWN'


def _format_router_external(item):
    return 'External' if item else 'Internal'


_formatters = {
    'subnets': utils.format_list,
    'subnet_ids': utils.format_list,
    'admin_state_up': _format_admin_state,
    'is_admin_state_up': _format_admin_state,
    'router:external': _format_router_external,
    'is_router_external': _format_router_external,
    'availability_zones': utils.format_list,
    'availability_zone_hints': utils.format_list,
}


def _get_network_columns(item):
    column_map = {
        'subnet_ids': 'subnets',
        'is_admin_state_up': 'admin_state_up',
        'is_router_external': 'router:external',
        'is_port_security_enabled': 'port_security_enabled',
        'provider_network_type': 'provider:network_type',
        'provider_physical_network': 'provider:physical_network',
        'provider_segmentation_id': 'provider:segmentation_id',
        'is_shared': 'shared',
        'ipv4_address_scope_id': 'ipv4_address_scope',
        'ipv6_address_scope_id': 'ipv6_address_scope',
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
    if 'project_id' not in columns:
        columns.append('project_id')
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
    if parsed_args.enable_port_security:
        attrs['port_security_enabled'] = True
    if parsed_args.disable_port_security:
        attrs['port_security_enabled'] = False

    # "network set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        # TODO(dtroyer): Remove tenant_id when we clean up the SDK refactor
        attrs['tenant_id'] = project_id
        attrs['project_id'] = project_id

    # "network set" command doesn't support setting availability zone hints.
    if 'availability_zone_hints' in parsed_args and \
       parsed_args.availability_zone_hints is not None:
        attrs['availability_zone_hints'] = parsed_args.availability_zone_hints

    # set description
    if parsed_args.description:
        attrs['description'] = parsed_args.description

    # update_external_network_options
    if parsed_args.internal:
        attrs['router:external'] = False
    if parsed_args.external:
        attrs['router:external'] = True
    if parsed_args.no_default:
        attrs['is_default'] = False
    if parsed_args.default:
        attrs['is_default'] = True
    # Update Provider network options
    if parsed_args.provider_network_type:
        attrs['provider:network_type'] = parsed_args.provider_network_type
    if parsed_args.physical_network:
        attrs['provider:physical_network'] = parsed_args.physical_network
    if parsed_args.segmentation_id:
        attrs['provider:segmentation_id'] = parsed_args.segmentation_id
    if parsed_args.qos_policy is not None:
        network_client = client_manager.network
        _qos_policy = network_client.find_qos_policy(parsed_args.qos_policy,
                                                     ignore_missing=False)
        attrs['qos_policy_id'] = _qos_policy.id
    if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
        attrs['qos_policy_id'] = None
    # Update VLAN Transparency for networks
    if parsed_args.transparent_vlan:
        attrs['vlan_transparent'] = True
    if parsed_args.no_transparent_vlan:
        attrs['vlan_transparent'] = False
    return attrs


def _add_additional_network_options(parser):
    # Add additional network options

    parser.add_argument(
        '--provider-network-type',
        metavar='<provider-network-type>',
        help=_("The physical mechanism by which the virtual network "
               "is implemented. For example: "
               "flat, geneve, gre, local, vlan, vxlan."))
    parser.add_argument(
        '--provider-physical-network',
        metavar='<provider-physical-network>',
        dest='physical_network',
        help=_("Name of the physical network over which the virtual "
               "network is implemented"))
    parser.add_argument(
        '--provider-segment',
        metavar='<provider-segment>',
        dest='segmentation_id',
        help=_("VLAN ID for VLAN networks or Tunnel ID for "
               "GENEVE/GRE/VXLAN networks"))

    vlan_transparent_grp = parser.add_mutually_exclusive_group()
    vlan_transparent_grp.add_argument(
        '--transparent-vlan',
        action='store_true',
        help=_("Make the network VLAN transparent"))
    vlan_transparent_grp.add_argument(
        '--no-transparent-vlan',
        action='store_true',
        help=_("Do not make the network VLAN transparent"))


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


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateNetwork(common.NetworkAndComputeShowOne):
    _description = _("Create new network")

    def update_parser_common(self, parser):
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New network name")
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Share the network between projects")
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share the network between projects")
        )
        return parser

    def update_parser_network(self, parser):
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable network (default)")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable network")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set network description")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--availability-zone-hint',
            action='append',
            dest='availability_zone_hints',
            metavar='<availability-zone>',
            help=_("Availability Zone in which to create this network "
                   "(Network Availability Zone extension required, "
                   "repeat option to set multiple availability zones)")
        )
        port_security_group = parser.add_mutually_exclusive_group()
        port_security_group.add_argument(
            '--enable-port-security',
            action='store_true',
            help=_("Enable port security by default for ports created on "
                   "this network (default)")
        )
        port_security_group.add_argument(
            '--disable-port-security',
            action='store_true',
            help=_("Disable port security by default for ports created on "
                   "this network")
        )
        external_router_grp = parser.add_mutually_exclusive_group()
        external_router_grp.add_argument(
            '--external',
            action='store_true',
            help=_("Set this network as an external network "
                   "(external-net extension required)")
        )
        external_router_grp.add_argument(
            '--internal',
            action='store_true',
            help=_("Set this network as an internal network (default)")
        )
        default_router_grp = parser.add_mutually_exclusive_group()
        default_router_grp.add_argument(
            '--default',
            action='store_true',
            help=_("Specify if this network should be used as "
                   "the default external network")
        )
        default_router_grp.add_argument(
            '--no-default',
            action='store_true',
            help=_("Do not use the network as the default external network "
                   "(default)")
        )
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("QoS policy to attach to this network (name or ID)")
        )
        _add_additional_network_options(parser)
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--subnet',
            metavar='<subnet>',
            help=_("IPv4 subnet for fixed IPs (in CIDR notation)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_network(**attrs)
        display_columns, columns = _get_network_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        attrs = _get_attrs_compute(self.app.client_manager, parsed_args)
        obj = client.networks.create(**attrs)
        columns = _get_columns(obj._info)
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)


class DeleteNetwork(common.NetworkAndComputeDelete):
    _description = _("Delete network(s)")

    # Used by base class to find resources in parsed_args.
    resource = 'network'
    r = None

    def update_parser_common(self, parser):
        parser.add_argument(
            'network',
            metavar="<network>",
            nargs="+",
            help=_("Network(s) to delete (name or ID)")
        )

        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_network(self.r, ignore_missing=False)
        client.delete_network(obj)

    def take_action_compute(self, client, parsed_args):
        network = utils.find_resource(client.networks, self.r)
        client.networks.delete(network.id)


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListNetwork(common.NetworkAndComputeLister):
    _description = _("List networks")

    def update_parser_network(self, parser):
        router_ext_group = parser.add_mutually_exclusive_group()
        router_ext_group.add_argument(
            '--external',
            action='store_true',
            help=_("List external networks")
        )
        router_ext_group.add_argument(
            '--internal',
            action='store_true',
            help=_("List internal networks")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List networks according to their name")
        )
        admin_state_group = parser.add_mutually_exclusive_group()
        admin_state_group.add_argument(
            '--enable',
            action='store_true',
            help=_("List enabled networks")
        )
        admin_state_group.add_argument(
            '--disable',
            action='store_true',
            help=_("List disabled networks")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List networks according to their project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            help=_("List networks shared between projects")
        )
        shared_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("List networks not shared between projects")
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            choices=['ACTIVE', 'BUILD', 'DOWN', 'ERROR'],
            help=_("List networks according to their status "
                   "('ACTIVE', 'BUILD', 'DOWN', 'ERROR')")
        )
        parser.add_argument(
            '--provider-network-type',
            metavar='<provider-network-type>',
            choices=['flat', 'geneve', 'gre', 'local',
                     'vlan', 'vxlan'],
            help=_("List networks according to their physical mechanisms. "
                   "The supported options are: flat, geneve, gre, local, "
                   "vlan, vxlan.")
        )
        parser.add_argument(
            '--provider-physical-network',
            metavar='<provider-physical-network>',
            dest='physical_network',
            help=_("List networks according to name of the physical network")
        )
        parser.add_argument(
            '--provider-segment',
            metavar='<provider-segment>',
            dest='segmentation_id',
            help=_("List networks according to VLAN ID for VLAN networks "
                   "or Tunnel ID for GENEVE/GRE/VXLAN networks")
        )

        return parser

    def take_action_network(self, client, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns = (
                'id',
                'name',
                'status',
                'project_id',
                'is_admin_state_up',
                'is_shared',
                'subnet_ids',
                'provider_network_type',
                'is_router_external',
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
                'subnet_ids'
            )
            column_headers = (
                'ID',
                'Name',
                'Subnets',
            )

        args = {}

        if parsed_args.external:
            args['router:external'] = True
            args['is_router_external'] = True
        elif parsed_args.internal:
            args['router:external'] = False
            args['is_router_external'] = False

        if parsed_args.name is not None:
            args['name'] = parsed_args.name

        if parsed_args.enable:
            args['admin_state_up'] = True
            args['is_admin_state_up'] = True
        elif parsed_args.disable:
            args['admin_state_up'] = False
            args['is_admin_state_up'] = False

        if parsed_args.project:
            project = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            )
            args['tenant_id'] = project.id
            args['project_id'] = project.id

        if parsed_args.share:
            args['shared'] = True
            args['is_shared'] = True
        elif parsed_args.no_share:
            args['shared'] = False
            args['is_shared'] = False

        if parsed_args.status:
            args['status'] = parsed_args.status

        if parsed_args.provider_network_type:
            args['provider:network_type'] = parsed_args.provider_network_type
            args['provider_network_type'] = parsed_args.provider_network_type
        if parsed_args.physical_network:
            args['provider:physical_network'] = parsed_args.physical_network
            args['provider_physical_network'] = parsed_args.physical_network
        if parsed_args.segmentation_id:
            args['provider:segmentation_id'] = parsed_args.segmentation_id
            args['provider_segmentation_id'] = parsed_args.segmentation_id

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


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetwork(command.Command):
    _description = _("Set network properties")

    def get_parser(self, prog_name):
        parser = super(SetNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Network to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("Set network name")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=None,
            help=_("Enable network")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable network")
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Share the network between projects")
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share the network between projects")
        )
        parser.add_argument(
            '--description',
            metavar="<description",
            help=_("Set network description")
        )
        port_security_group = parser.add_mutually_exclusive_group()
        port_security_group.add_argument(
            '--enable-port-security',
            action='store_true',
            help=_("Enable port security by default for ports created on "
                   "this network")
        )
        port_security_group.add_argument(
            '--disable-port-security',
            action='store_true',
            help=_("Disable port security by default for ports created on "
                   "this network")
        )
        external_router_grp = parser.add_mutually_exclusive_group()
        external_router_grp.add_argument(
            '--external',
            action='store_true',
            help=_("Set this network as an external network "
                   "(external-net extension required)")
        )
        external_router_grp.add_argument(
            '--internal',
            action='store_true',
            help=_("Set this network as an internal network")
        )
        default_router_grp = parser.add_mutually_exclusive_group()
        default_router_grp.add_argument(
            '--default',
            action='store_true',
            help=_("Set the network as the default external network")
        )
        default_router_grp.add_argument(
            '--no-default',
            action='store_true',
            help=_("Do not use the network as the default external network")
        )
        qos_group = parser.add_mutually_exclusive_group()
        qos_group.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("QoS policy to attach to this network (name or ID)")
        )
        qos_group.add_argument(
            '--no-qos-policy',
            action='store_true',
            help=_("Remove the QoS policy attached to this network")
        )
        _add_additional_network_options(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_network(parsed_args.network, ignore_missing=False)

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        client.update_network(obj, **attrs)


class ShowNetwork(common.NetworkAndComputeShowOne):
    _description = _("Show network details")

    def update_parser_common(self, parser):
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Network to display (name or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_network(parsed_args.network, ignore_missing=False)
        display_columns, columns = _get_network_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = utils.find_resource(
            client.networks,
            parsed_args.network,
        )
        columns = _get_columns(obj._info)
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)
