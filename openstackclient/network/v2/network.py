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

"""Network action implementations"""

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import tags as _tag

from openstackclient.api import compute_v2
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common


class AdminStateColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return 'UP' if self._value else 'DOWN'


class RouterExternalColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return 'External' if self._value else 'Internal'


_formatters = {
    'subnets': format_columns.ListColumn,
    'subnet_ids': format_columns.ListColumn,
    'admin_state_up': AdminStateColumn,
    'is_admin_state_up': AdminStateColumn,
    'router:external': RouterExternalColumn,
    'is_router_external': RouterExternalColumn,
    'availability_zones': format_columns.ListColumn,
    'availability_zone_hints': format_columns.ListColumn,
    'tags': format_columns.ListColumn,
}


def _get_columns_network(item):
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
        'tags': 'tags',
    }
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_columns_compute(item):
    return utils.get_osc_show_columns_for_sdk_resource(item, {})


def _get_attrs_network(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
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
        attrs['project_id'] = project_id

    # "network set" command doesn't support setting availability zone hints.
    if (
        'availability_zone_hints' in parsed_args
        and parsed_args.availability_zone_hints is not None
    ):
        attrs['availability_zone_hints'] = parsed_args.availability_zone_hints

    # set description
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description

    # set mtu
    if parsed_args.mtu:
        attrs['mtu'] = parsed_args.mtu

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
        _qos_policy = network_client.find_qos_policy(
            parsed_args.qos_policy, ignore_missing=False
        )
        attrs['qos_policy_id'] = _qos_policy.id
    if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
        attrs['qos_policy_id'] = None
    # Update DNS network options
    if parsed_args.dns_domain is not None:
        attrs['dns_domain'] = parsed_args.dns_domain
    return attrs


def _get_attrs_compute(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.share:
        attrs['share_subnet'] = True
    if parsed_args.no_share:
        attrs['share_subnet'] = False
    if parsed_args.subnet is not None:
        attrs['subnet'] = parsed_args.subnet
    return attrs


def _add_additional_network_options(parser):
    # Add additional network options

    parser.add_argument(
        '--provider-network-type',
        metavar='<provider-network-type>',
        help=_(
            "The physical mechanism by which the virtual network "
            "is implemented. For example: "
            "flat, geneve, gre, local, vlan or vxlan."
        ),
    )
    parser.add_argument(
        '--provider-physical-network',
        metavar='<provider-physical-network>',
        dest='physical_network',
        help=_(
            "Name of the physical network over which the virtual "
            "network is implemented"
        ),
    )
    parser.add_argument(
        '--provider-segment',
        metavar='<provider-segment>',
        dest='segmentation_id',
        help=_(
            "VLAN ID for VLAN networks or Tunnel ID for "
            "GENEVE/GRE/VXLAN networks"
        ),
    )
    parser.add_argument(
        '--dns-domain',
        metavar='<dns-domain>',
        dest='dns_domain',
        help=_(
            "Set DNS domain for this network "
            "(requires DNS integration extension)"
        ),
    )


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateNetwork(
    common.NetworkAndComputeShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create new network")

    def update_parser_common(self, parser):
        parser.add_argument(
            'name', metavar='<name>', help=_("New network name")
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Share the network between projects"),
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share the network between projects"),
        )
        return parser

    def update_parser_network(self, parser):
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=self.enhance_help_neutron(_("Enable network (default)")),
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=self.enhance_help_neutron(_("Disable network")),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=self.enhance_help_neutron(_("Owner's project (name or ID)")),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=self.enhance_help_neutron(_("Set network description")),
        )
        parser.add_argument(
            '--mtu',
            metavar='<mtu>',
            help=self.enhance_help_neutron(_("Set network mtu")),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--availability-zone-hint',
            action='append',
            dest='availability_zone_hints',
            metavar='<availability-zone>',
            help=self.enhance_help_neutron(
                _(
                    "Availability Zone in which to create this network "
                    "(Network Availability Zone extension required, "
                    "repeat option to set multiple availability zones)"
                )
            ),
        )
        port_security_group = parser.add_mutually_exclusive_group()
        port_security_group.add_argument(
            '--enable-port-security',
            action='store_true',
            help=self.enhance_help_neutron(
                _(
                    "Enable port security by default for ports created on "
                    "this network (default)"
                )
            ),
        )
        port_security_group.add_argument(
            '--disable-port-security',
            action='store_true',
            help=self.enhance_help_neutron(
                _(
                    "Disable port security by default for ports created on "
                    "this network"
                )
            ),
        )
        external_router_grp = parser.add_mutually_exclusive_group()
        external_router_grp.add_argument(
            '--external',
            action='store_true',
            help=self.enhance_help_neutron(
                _(
                    "The network has an external routing facility that is not "
                    "managed by Neutron and can be used. For example: "
                    "openstack router set --external-gateway NETWORK "
                    "(external-net extension required)"
                )
            ),
        )
        external_router_grp.add_argument(
            '--internal',
            action='store_true',
            help=self.enhance_help_neutron(
                _("Opposite of '--external' (default)")
            ),
        )
        default_router_grp = parser.add_mutually_exclusive_group()
        default_router_grp.add_argument(
            '--default',
            action='store_true',
            help=self.enhance_help_neutron(
                _(
                    "Specify if this network should be used as the default "
                    "external network"
                )
            ),
        )
        default_router_grp.add_argument(
            '--no-default',
            action='store_true',
            help=self.enhance_help_neutron(
                _(
                    "Do not use the network as the default external network "
                    "(default)"
                )
            ),
        )
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=self.enhance_help_neutron(
                _("QoS policy to attach to this network (name or ID)")
            ),
        )
        vlan_transparent_grp = parser.add_mutually_exclusive_group()
        vlan_transparent_grp.add_argument(
            '--transparent-vlan',
            action='store_true',
            help=self.enhance_help_neutron(
                _("Make the network VLAN transparent")
            ),
        )
        vlan_transparent_grp.add_argument(
            '--no-transparent-vlan',
            action='store_true',
            help=self.enhance_help_neutron(
                _("Do not make the network VLAN transparent")
            ),
        )

        vlan_qinq_grp = parser.add_mutually_exclusive_group()
        vlan_qinq_grp.add_argument(
            '--qinq-vlan',
            action='store_true',
            help=self.enhance_help_neutron(
                _("Enable VLAN QinQ (S-Tag ethtype 0x8a88) for the network")
            ),
        )
        vlan_qinq_grp.add_argument(
            '--no-qinq-vlan',
            action='store_true',
            help=self.enhance_help_neutron(
                _("Disable VLAN QinQ (S-Tag ethtype 0x8a88) for the network")
            ),
        )

        _add_additional_network_options(parser)
        _tag.add_tag_option_to_parser_for_create(
            parser, _('network'), enhance_help=self.enhance_help_neutron
        )
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--subnet',
            metavar='<subnet>',
            required=True,
            help=self.enhance_help_nova_network(
                _("IPv4 subnet for fixed IPs (in CIDR notation)")
            ),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        attrs = _get_attrs_network(self.app.client_manager, parsed_args)
        if parsed_args.transparent_vlan:
            attrs['vlan_transparent'] = True
        if parsed_args.no_transparent_vlan:
            attrs['vlan_transparent'] = False

        if parsed_args.qinq_vlan:
            attrs['vlan_qinq'] = True
        if parsed_args.no_qinq_vlan:
            attrs['vlan_qinq'] = False

        if attrs.get('vlan_transparent') and attrs.get('vlan_qinq'):
            msg = _(
                "--transparent-vlan and --qinq-vlan can not be both enabled "
                "for the network."
            )
            raise exceptions.CommandError(msg)

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        with common.check_missing_extension_if_error(
            self.app.client_manager.network, attrs
        ):
            obj = client.create_network(**attrs)

        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)
        display_columns, columns = _get_columns_network(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        attrs = _get_attrs_compute(self.app.client_manager, parsed_args)
        obj = compute_v2.create_network(client, **attrs)
        display_columns, columns = _get_columns_compute(obj)
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)


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
            help=_("Network(s) to delete (name or ID)"),
        )

        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_network(self.r, ignore_missing=False)
        client.delete_network(obj)

    def take_action_compute(self, client, parsed_args):
        network = compute_v2.find_network(client, self.r)
        compute_v2.delete_network(client, network['id'])


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListNetwork(common.NetworkAndComputeLister):
    _description = _("List networks")

    def update_parser_network(self, parser):
        router_ext_group = parser.add_mutually_exclusive_group()
        router_ext_group.add_argument(
            '--external',
            action='store_true',
            help=self.enhance_help_neutron(_("List external networks")),
        )
        router_ext_group.add_argument(
            '--internal',
            action='store_true',
            help=self.enhance_help_neutron(_("List internal networks")),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            help=self.enhance_help_neutron(
                _("List additional fields in output")
            ),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=self.enhance_help_neutron(
                _("List networks according to their name")
            ),
        )
        admin_state_group = parser.add_mutually_exclusive_group()
        admin_state_group.add_argument(
            '--enable',
            action='store_true',
            help=self.enhance_help_neutron(_("List enabled networks")),
        )
        admin_state_group.add_argument(
            '--disable',
            action='store_true',
            help=self.enhance_help_neutron(_("List disabled networks")),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List networks according to their project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(
            parser, enhance_help=self.enhance_help_neutron
        )
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            help=self.enhance_help_neutron(
                _("List networks shared between projects")
            ),
        )
        shared_group.add_argument(
            '--no-share',
            action='store_true',
            help=self.enhance_help_neutron(
                _("List networks not shared between projects")
            ),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            choices=['ACTIVE', 'BUILD', 'DOWN', 'ERROR'],
            help=self.enhance_help_neutron(
                _(
                    "List networks according to their status "
                    "('ACTIVE', 'BUILD', 'DOWN', 'ERROR')"
                )
            ),
        )
        parser.add_argument(
            '--provider-network-type',
            metavar='<provider-network-type>',
            choices=['flat', 'geneve', 'gre', 'local', 'vlan', 'vxlan'],
            help=self.enhance_help_neutron(
                _(
                    "List networks according to their physical mechanisms. "
                    "The supported options are: flat, geneve, gre, local, "
                    "vlan and vxlan."
                )
            ),
        )
        parser.add_argument(
            '--provider-physical-network',
            metavar='<provider-physical-network>',
            dest='physical_network',
            help=self.enhance_help_neutron(
                _("List networks according to name of the physical network")
            ),
        )
        parser.add_argument(
            '--provider-segment',
            metavar='<provider-segment>',
            dest='segmentation_id',
            help=self.enhance_help_neutron(
                _(
                    "List networks according to VLAN ID for VLAN networks or "
                    "Tunnel ID for GENEVE/GRE/VXLAN networks"
                )
            ),
        )
        parser.add_argument(
            '--agent',
            metavar='<agent-id>',
            dest='agent_id',
            help=self.enhance_help_neutron(
                _('List networks hosted by agent (ID only)')
            ),
        )
        _tag.add_tag_filtering_option_to_parser(
            parser, _('networks'), enhance_help=self.enhance_help_neutron
        )
        return parser

    def take_action_network(self, client, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.long:
            columns: tuple[str, ...] = (
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
                'tags',
            )
            column_headers: tuple[str, ...] = (
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
                'Tags',
            )
        elif parsed_args.agent_id:
            columns = ('id', 'name', 'subnet_ids')
            column_headers = (
                'ID',
                'Name',
                'Subnets',
            )
            client = self.app.client_manager.network
            dhcp_agent = client.get_agent(parsed_args.agent_id)
            data = client.dhcp_agent_hosting_networks(dhcp_agent)

            return (
                column_headers,
                (
                    utils.get_item_properties(
                        s,
                        columns,
                        formatters=_formatters,
                    )
                    for s in data
                ),
            )
        else:
            columns = ('id', 'name', 'subnet_ids')
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

        _tag.get_tag_filtering_args(parsed_args, args)

        data = client.networks(**args)

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )

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

        data = compute_v2.list_networks(client)

        return (
            column_headers,
            (
                utils.get_dict_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )


# TODO(sindhu): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetwork(common.NeutronCommandWithExtraArgs):
    _description = _("Set network properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Network to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_("Set network name")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=None,
            help=_("Enable network"),
        )
        admin_group.add_argument(
            '--disable', action='store_true', help=_("Disable network")
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Share the network between projects"),
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share the network between projects"),
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_("Set network description"),
        )
        parser.add_argument(
            '--mtu', metavar="<mtu>", help=_("Set network mtu")
        )
        port_security_group = parser.add_mutually_exclusive_group()
        port_security_group.add_argument(
            '--enable-port-security',
            action='store_true',
            help=_(
                "Enable port security by default for ports created on "
                "this network"
            ),
        )
        port_security_group.add_argument(
            '--disable-port-security',
            action='store_true',
            help=_(
                "Disable port security by default for ports created on "
                "this network"
            ),
        )
        external_router_grp = parser.add_mutually_exclusive_group()
        external_router_grp.add_argument(
            '--external',
            action='store_true',
            help=_(
                "The network has an external routing facility that is not "
                "managed by Neutron and can be used. For example: "
                "openstack router set --external-gateway NETWORK "
                "(external-net extension required)."
            ),
        )
        external_router_grp.add_argument(
            '--internal',
            action='store_true',
            help=_("Opposite of '--external'"),
        )
        default_router_grp = parser.add_mutually_exclusive_group()
        default_router_grp.add_argument(
            '--default',
            action='store_true',
            help=_("Set the network as the default external network"),
        )
        default_router_grp.add_argument(
            '--no-default',
            action='store_true',
            help=_("Do not use the network as the default external network"),
        )
        qos_group = parser.add_mutually_exclusive_group()
        qos_group.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("QoS policy to attach to this network (name or ID)"),
        )
        qos_group.add_argument(
            '--no-qos-policy',
            action='store_true',
            help=_("Remove the QoS policy attached to this network"),
        )
        _tag.add_tag_option_to_parser_for_set(parser, _('network'))
        _add_additional_network_options(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_network(parsed_args.network, ignore_missing=False)

        attrs = _get_attrs_network(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        if attrs:
            with common.check_missing_extension_if_error(
                self.app.client_manager.network, attrs
            ):
                client.update_network(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)


class ShowNetwork(common.NetworkAndComputeShowOne):
    _description = _("Show network details")

    def update_parser_common(self, parser):
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Network to display (name or ID)"),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_network(parsed_args.network, ignore_missing=False)
        display_columns, columns = _get_columns_network(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = compute_v2.find_network(client, parsed_args.network)
        display_columns, columns = _get_columns_compute(obj)
        data = utils.get_dict_properties(obj, columns)
        return (display_columns, data)


class UnsetNetwork(common.NeutronUnsetCommandWithExtraArgs):
    _description = _("Unset network properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Network to modify (name or ID)"),
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('network'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_network(parsed_args.network, ignore_missing=False)

        attrs = self._parse_extra_properties(parsed_args.extra_properties)
        if attrs:
            client.update_network(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
