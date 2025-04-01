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

"""Router action implementations"""

import argparse
import collections
import copy
import json
import logging
import typing as ty

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import tags as _tag

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common

LOG = logging.getLogger(__name__)


class AdminStateColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return 'UP' if self._value else 'DOWN'


class RouterInfoColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        try:
            return json.dumps(self._value)
        except (TypeError, KeyError):
            return ''


class RoutesColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        # Map the route keys to match --route option.
        for route in self._value or []:
            if 'nexthop' in route:
                route['gateway'] = route.pop('nexthop')
        return utils.format_list_of_dicts(self._value)


_formatters = {
    'admin_state_up': AdminStateColumn,
    'is_admin_state_up': AdminStateColumn,
    'external_gateway_info': RouterInfoColumn,
    'availability_zones': format_columns.ListColumn,
    'availability_zone_hints': format_columns.ListColumn,
    'routes': RoutesColumn,
    'tags': format_columns.ListColumn,
}


def _get_columns(item):
    column_map = {
        'is_ha': 'ha',
        'is_distributed': 'distributed',
        'is_admin_state_up': 'admin_state_up',
    }
    if hasattr(item, 'interfaces_info'):
        column_map['interfaces_info'] = 'interfaces_info'
    invisible_columns = ['location']
    if item.is_ha is None:
        invisible_columns.append('is_ha')
        column_map.pop('is_ha')
    if item.is_distributed is None:
        invisible_columns.append('is_distributed')
        column_map.pop('is_distributed')
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, invisible_columns
    )


def is_multiple_gateways_supported(n_client):
    return n_client.find_extension("external-gateway-multihoming") is not None


def _passed_multiple_gateways(extension_supported, external_gateways):
    passed_multiple_gws = len(external_gateways) > 1
    if passed_multiple_gws and not extension_supported:
        msg = _(
            'Supplying --external-gateway option multiple times is not '
            'supported due to the lack of external-gateway-multihoming '
            'extension at the Neutron side.'
        )
        raise exceptions.CommandError(msg)
    return passed_multiple_gws


def _get_external_gateway_attrs(client_manager, parsed_args):
    attrs: dict[str, ty.Any] = {}

    if parsed_args.external_gateways:
        external_gateways: collections.defaultdict[str, list[dict]] = (
            collections.defaultdict(list)
        )
        n_client = client_manager.network
        first_network_id = ''

        for gw_net_name_or_id in parsed_args.external_gateways:
            gateway_info = {}
            gw_net = n_client.find_network(
                gw_net_name_or_id, ignore_missing=False
            )
            if not first_network_id:
                first_network_id = gw_net.id
            gateway_info['network_id'] = gw_net.id
            if 'disable_snat' in parsed_args and parsed_args.disable_snat:
                gateway_info['enable_snat'] = False
            if 'enable_snat' in parsed_args and parsed_args.enable_snat:
                gateway_info['enable_snat'] = True

            # This option was added before multiple gateways were supported, so
            # it does not have a per-gateway port granularity so just pass it
            # along in gw info in case it is specified.
            if 'qos_policy' in parsed_args and parsed_args.qos_policy:
                qos_id = n_client.find_qos_policy(
                    parsed_args.qos_policy, ignore_missing=False
                ).id
                gateway_info['qos_policy_id'] = qos_id
            if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
                gateway_info['qos_policy_id'] = None

            external_gateways[gw_net.id].append(gateway_info)

        multiple_gws_supported = is_multiple_gateways_supported(n_client)
        # Parse the external fixed IP specs and match them to specific gateway
        # ports if needed.
        if parsed_args.fixed_ips:
            for ip_spec in parsed_args.fixed_ips:
                # If there is only one gateway, this value will represent the
                # network ID for it, otherwise it will be overridden.
                ip_net_id: str = first_network_id

                if ip_spec.get('subnet', False):
                    subnet_name_id = ip_spec.pop('subnet')
                    if subnet_name_id:
                        subnet = n_client.find_subnet(
                            subnet_name_id, ignore_missing=False
                        )
                        ip_spec['subnet_id'] = subnet.id
                        ip_net_id = subnet.network_id
                if ip_spec.get('ip-address', False):
                    ip_spec['ip_address'] = ip_spec.pop('ip-address')
                # Finally, add an ip_spec to the specific gateway identified
                # by a network from the spec.
                if (
                    'subnet_id' in ip_spec
                    and ip_net_id not in external_gateways
                ):
                    msg = (
                        _(
                            'Subnet %s does not belong to any of the networks '
                            'provided for --external-gateway.'
                        )
                        % (ip_spec['subnet_id'])
                    )
                    raise exceptions.CommandError(msg)
                for gw_info in external_gateways[ip_net_id]:
                    if 'external_fixed_ips' not in gw_info:
                        gw_info['external_fixed_ips'] = [ip_spec]
                        break
                else:
                    # The end user has requested more fixed IPs than there are
                    # gateways, add multiple fixed IPs to single gateway to
                    # retain current behavior.
                    for gw_info in external_gateways[ip_net_id]:
                        gw_info['external_fixed_ips'].append(ip_spec)
                        break

        # Use the newer API whenever it is supported regardless of whether one
        # or multiple gateways are passed as arguments.
        if multiple_gws_supported:
            gateway_list = []
            # Now merge the per-network-id lists of external gateway info
            # dicts into one list.
            for gw_info_list in external_gateways.values():
                gateway_list.extend(gw_info_list)
            attrs['external_gateways'] = gateway_list
        else:
            attrs['external_gateway_info'] = external_gateways[
                first_network_id
            ][0]
    return attrs


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    n_client = client_manager.network

    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if parsed_args.centralized:
        attrs['distributed'] = False
    if parsed_args.distributed:
        attrs['distributed'] = True
    if (
        'availability_zone_hints' in parsed_args
        and parsed_args.availability_zone_hints is not None
    ):
        attrs['availability_zone_hints'] = parsed_args.availability_zone_hints
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    # "router set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    attrs.update(_get_external_gateway_attrs(client_manager, parsed_args))

    # "router set" command doesn't support setting flavor_id.
    if 'flavor_id' in parsed_args and parsed_args.flavor_id is not None:
        flavor = n_client.find_flavor(parsed_args.flavor_id)
        attrs['flavor_id'] = flavor.id
    elif 'flavor' in parsed_args and parsed_args.flavor is not None:
        flavor = n_client.find_flavor(parsed_args.flavor, ignore_missing=False)
        attrs['flavor_id'] = flavor.id

    for attr in ('enable_default_route_bfd', 'enable_default_route_ecmp'):
        value = getattr(parsed_args, attr, None)
        if value is not None:
            attrs[attr] = value

    return attrs


def _parser_add_bfd_ecmp_arguments(parser):
    """Helper to add BFD and ECMP args for CreateRouter and SetRouter."""
    parser.add_argument(
        '--enable-default-route-bfd',
        dest='enable_default_route_bfd',
        default=None,
        action='store_true',
        help=_(
            "Enable BFD sessions for default routes inferred from "
            "the external gateway port subnets for this router"
        ),
    )
    parser.add_argument(
        '--disable-default-route-bfd',
        dest='enable_default_route_bfd',
        default=None,
        action='store_false',
        help=_(
            "Disable BFD sessions for default routes inferred from "
            "the external gateway port subnets for this router"
        ),
    )
    parser.add_argument(
        '--enable-default-route-ecmp',
        dest='enable_default_route_ecmp',
        default=None,
        action='store_true',
        help=_(
            "Add ECMP default routes if multiple are available via "
            "different gateway ports"
        ),
    )
    parser.add_argument(
        '--disable-default-route-ecmp',
        dest='enable_default_route_ecmp',
        default=None,
        action='store_false',
        help=_("Add default route only for first gateway port"),
    )


def _command_check_bfd_ecmp_supported(attrs, client):
    """Helper to check for server side support when bfd/ecmp attrs provided.

    :raises: exceptions.CommandError
    """
    if (
        'enable_default_route_bfd' in attrs
        or 'enable_default_route_ecmp' in attrs
    ) and not is_multiple_gateways_supported(client):
        msg = _(
            'The external-gateway-multihoming extension is not enabled at '
            'the Neutron side, cannot use --enable-default-route-bfd or '
            '--enable-default-route-ecmp arguments.'
        )
        raise exceptions.CommandError(msg)


class AddPortToRouter(command.Command):
    _description = _("Add a port to a router")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router to which port will be added (name or ID)"),
        )
        parser.add_argument(
            'port', metavar='<port>', help=_("Port to be added (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        port = client.find_port(parsed_args.port, ignore_missing=False)
        client.add_interface_to_router(
            client.find_router(parsed_args.router, ignore_missing=False),
            port_id=port.id,
        )


class AddSubnetToRouter(command.Command):
    _description = _("Add a subnet to a router")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router to which subnet will be added (name or ID)"),
        )
        parser.add_argument(
            'subnet',
            metavar='<subnet>',
            help=_("Subnet to be added (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        subnet = client.find_subnet(parsed_args.subnet, ignore_missing=False)
        client.add_interface_to_router(
            client.find_router(parsed_args.router, ignore_missing=False),
            subnet_id=subnet.id,
        )


class AddExtraRoutesToRouter(command.ShowOne):
    _description = _("Add extra static routes to a router's routing table.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_(
                "Router to which extra static routes "
                "will be added (name or ID)"
            ),
        )
        parser.add_argument(
            '--route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            dest='routes',
            default=[],
            required_keys=['destination', 'gateway'],
            help=_(
                "Add extra static route to the router. "
                "destination: destination subnet (in CIDR notation), "
                "gateway: nexthop IP address. "
                "Repeat option to add multiple routes. "
                "Trying to add a route that is already present "
                "(exactly, including destination and nexthop) "
                "in the routing table is allowed and is considered "
                "a successful operation."
            ),
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.routes is not None:
            for route in parsed_args.routes:
                route['nexthop'] = route.pop('gateway')
        client = self.app.client_manager.network
        router_obj = client.add_extra_routes_to_router(
            client.find_router(parsed_args.router, ignore_missing=False),
            body={'router': {'routes': parsed_args.routes}},
        )
        display_columns, columns = _get_columns(router_obj)
        data = utils.get_item_properties(
            router_obj, columns, formatters=_formatters
        )
        return (display_columns, data)


class RemoveExtraRoutesFromRouter(command.ShowOne):
    _description = _(
        "Remove extra static routes from a router's routing table."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_(
                "Router from which extra static routes "
                "will be removed (name or ID)"
            ),
        )
        parser.add_argument(
            '--route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            dest='routes',
            default=[],
            required_keys=['destination', 'gateway'],
            help=_(
                "Remove extra static route from the router. "
                "destination: destination subnet (in CIDR notation), "
                "gateway: nexthop IP address. "
                "Repeat option to remove multiple routes. "
                "Trying to remove a route that is already missing "
                "(fully, including destination and nexthop) "
                "from the routing table is allowed and is considered "
                "a successful operation."
            ),
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.routes is not None:
            for route in parsed_args.routes:
                route['nexthop'] = route.pop('gateway')
        client = self.app.client_manager.network
        router_obj = client.remove_extra_routes_from_router(
            client.find_router(parsed_args.router, ignore_missing=False),
            body={'router': {'routes': parsed_args.routes}},
        )
        display_columns, columns = _get_columns(router_obj)
        data = utils.get_item_properties(
            router_obj, columns, formatters=_formatters
        )
        return (display_columns, data)


# TODO(yanxing'an): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateRouter(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create a new router")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help=_("New router name")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable router (default)"),
        )
        admin_group.add_argument(
            '--disable', action='store_true', help=_("Disable router")
        )
        distribute_group = parser.add_mutually_exclusive_group()
        distribute_group.add_argument(
            '--distributed',
            action='store_true',
            help=_("Create a distributed router"),
        )
        distribute_group.add_argument(
            '--centralized',
            action='store_true',
            help=_("Create a centralized router"),
        )
        ha_group = parser.add_mutually_exclusive_group()
        ha_group.add_argument(
            '--ha',
            action='store_true',
            help=_("Create a highly available router"),
        )
        ha_group.add_argument(
            '--no-ha', action='store_true', help=_("Create a legacy router")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set router description"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--availability-zone-hint',
            metavar='<availability-zone>',
            action='append',
            dest='availability_zone_hints',
            help=_(
                "Availability Zone in which to create this router "
                "(Router Availability Zone extension required, "
                "repeat option to set multiple availability zones)"
            ),
        )
        _tag.add_tag_option_to_parser_for_create(parser, _('router'))
        parser.add_argument(
            '--external-gateway',
            metavar="<network>",
            action='append',
            help=_(
                "External Network used as router's gateway (name or ID) "
                "(repeat option to set multiple gateways per router "
                "if the L3 service plugin in use supports it)"
            ),
            dest='external_gateways',
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            dest='fixed_ips',
            help=_(
                "Desired IP and/or subnet (name or ID) "
                "on external gateway: "
                "subnet=<subnet>,ip-address=<ip-address> "
                "(repeat option to set multiple fixed IP addresses)"
            ),
        )
        snat_group = parser.add_mutually_exclusive_group()
        snat_group.add_argument(
            '--enable-snat',
            action='store_true',
            help=_("Enable Source NAT on external gateway"),
        )
        snat_group.add_argument(
            '--disable-snat',
            action='store_true',
            help=_("Disable Source NAT on external gateway"),
        )
        ndp_proxy_group = parser.add_mutually_exclusive_group()
        ndp_proxy_group.add_argument(
            '--enable-ndp-proxy',
            dest='enable_ndp_proxy',
            default=None,
            action='store_true',
            help=_("Enable IPv6 NDP proxy on external gateway"),
        )
        ndp_proxy_group.add_argument(
            '--disable-ndp-proxy',
            dest='enable_ndp_proxy',
            default=None,
            action='store_false',
            help=_("Disable IPv6 NDP proxy on external gateway"),
        )
        parser.add_argument(
            '--flavor',
            metavar='<flavor-id>',
            help=_("Associate the router to a flavor (by name or ID"),
        )
        parser.add_argument(
            '--flavor-id',
            metavar='<flavor-id>',
            help=argparse.SUPPRESS,
        )
        _parser_add_bfd_ecmp_arguments(parser)
        parser.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_('Attach QoS policy to router gateway IPs'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        if parsed_args.ha:
            attrs['ha'] = True
        if parsed_args.no_ha:
            attrs['ha'] = False
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        if parsed_args.enable_ndp_proxy and not parsed_args.external_gateways:
            msg = _(
                "You must specify '--external-gateway' in order "
                "to enable router's NDP proxy"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.qos_policy and not parsed_args.external_gateways:
            msg = _(
                "You must specify '--external-gateway' in order "
                "to define a QoS policy"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.enable_ndp_proxy is not None:
            attrs['enable_ndp_proxy'] = parsed_args.enable_ndp_proxy

        _command_check_bfd_ecmp_supported(attrs, client)

        external_gateways = attrs.pop('external_gateways', None)
        obj = client.create_router(**attrs)
        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)

        # If the multiple external gateways API is intended to be used,
        # do a separate API call to set the desired external gateways as the
        # router creation API supports adding only one.
        if external_gateways:
            client.update_external_gateways(
                obj, body={'router': {'external_gateways': external_gateways}}
            )

        if (
            parsed_args.disable_snat
            or parsed_args.enable_snat
            or parsed_args.fixed_ips
        ) and not parsed_args.external_gateways:
            msg = _(
                "You must specify '--external-gateway' in order "
                "to specify SNAT or fixed-ip values"
            )
            raise exceptions.CommandError(msg)

        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (display_columns, data)


class DeleteRouter(command.Command):
    _description = _("Delete router(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            nargs="+",
            help=_("Router(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for router in parsed_args.router:
            try:
                obj = client.find_router(router, ignore_missing=False)
                client.delete_router(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete router with "
                        "name or ID '%(router)s': %(e)s"
                    ),
                    {'router': router, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.router)
            msg = _("%(result)s of %(total)s routers failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


# TODO(yanxing'an): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListRouter(command.Lister):
    _description = _("List routers")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List routers according to their name"),
        )
        admin_state_group = parser.add_mutually_exclusive_group()
        admin_state_group.add_argument(
            '--enable', action='store_true', help=_("List enabled routers")
        )
        admin_state_group.add_argument(
            '--disable', action='store_true', help=_("List disabled routers")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List routers according to their project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--agent',
            metavar='<agent-id>',
            help=_("List routers hosted by an agent (ID only)"),
        )
        _tag.add_tag_filtering_option_to_parser(parser, _('routers'))

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        client = self.app.client_manager.network

        columns: tuple[str, ...] = (
            'id',
            'name',
            'status',
            'is_admin_state_up',
            'project_id',
        )
        column_headers: tuple[str, ...] = (
            'ID',
            'Name',
            'Status',
            'State',
            'Project',
        )

        args = {}

        if parsed_args.name is not None:
            args['name'] = parsed_args.name

        if parsed_args.enable:
            args['admin_state_up'] = True
            args['is_admin_state_up'] = True
        elif parsed_args.disable:
            args['admin_state_up'] = False
            args['is_admin_state_up'] = False

        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            args['project_id'] = project_id

        _tag.get_tag_filtering_args(parsed_args, args)

        if parsed_args.agent is not None:
            agent = client.get_agent(parsed_args.agent)
            data = client.agent_hosted_routers(agent)
            # NOTE: Networking API does not support filtering by parameters,
            # so we need filtering in the client side.
            data = [d for d in data if self._filter_match(d, args)]
        else:
            data = client.routers(**args)

        # check if "HA" and "Distributed" columns should be displayed also
        data = list(data)
        for d in data:
            if (
                d.is_distributed is not None
                and 'is_distributed' not in columns
            ):
                columns += ('is_distributed',)
                column_headers += ('Distributed',)
            if d.is_ha is not None and 'is_ha' not in columns:
                columns += ('is_ha',)
                column_headers += ('HA',)
        if parsed_args.long:
            columns += (
                'routes',
                'external_gateway_info',
            )
            column_headers += (
                'Routes',
                'External gateway info',
            )
            # availability zone will be available only when
            # router_availability_zone extension is enabled
            if client.find_extension("router_availability_zone"):
                columns += ('availability_zones',)
                column_headers += ('Availability zones',)
            columns += ('tags',)
            column_headers += ('Tags',)

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

    @staticmethod
    def _filter_match(data, conditions):
        for key, value in conditions.items():
            try:
                if getattr(data, key) != value:
                    return False
            except AttributeError:
                # Some filter attributes like tenant_id or admin_state_up
                # are backward compatibility in older OpenStack SDK support.
                # They does not exist in the latest release.
                # In this case we just skip checking such filter condition.
                continue
        return True


class RemovePortFromRouter(command.Command):
    _description = _("Remove a port from a router")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router from which port will be removed (name or ID)"),
        )
        parser.add_argument(
            'port',
            metavar='<port>',
            help=_("Port to be removed and deleted (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        port = client.find_port(parsed_args.port, ignore_missing=False)
        client.remove_interface_from_router(
            client.find_router(parsed_args.router, ignore_missing=False),
            port_id=port.id,
        )


class RemoveSubnetFromRouter(command.Command):
    _description = _("Remove a subnet from a router")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_(
                "Router from which the subnet will be removed (name or ID)"
            ),
        )
        parser.add_argument(
            'subnet',
            metavar='<subnet>',
            help=_("Subnet to be removed (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        subnet = client.find_subnet(parsed_args.subnet, ignore_missing=False)
        client.remove_interface_from_router(
            client.find_router(parsed_args.router, ignore_missing=False),
            subnet_id=subnet.id,
        )


# TODO(yanxing'an): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetRouter(common.NeutronCommandWithExtraArgs):
    _description = _("Set router properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_("Set router name")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set router description'),
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=None,
            help=_("Enable router"),
        )
        admin_group.add_argument(
            '--disable', action='store_true', help=_("Disable router")
        )
        distribute_group = parser.add_mutually_exclusive_group()
        distribute_group.add_argument(
            '--distributed',
            action='store_true',
            help=_("Set router to distributed mode (disabled router only)"),
        )
        distribute_group.add_argument(
            '--centralized',
            action='store_true',
            help=_("Set router to centralized mode (disabled router only)"),
        )
        parser.add_argument(
            '--route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            dest='routes',
            default=None,
            required_keys=['destination', 'gateway'],
            help=_(
                "Add routes to the router. "
                "destination: destination subnet (in CIDR notation) "
                "gateway: nexthop IP address "
                "(repeat option to add multiple routes). "
                "This is deprecated in favor of 'router add/remove route' "
                "since it is prone to race conditions between concurrent "
                "clients when not used together with --no-route to "
                "overwrite the current value of 'routes'."
            ),
        )
        parser.add_argument(
            '--no-route',
            action='store_true',
            help=_(
                "Clear routes associated with the router. "
                "Specify both --route and --no-route to overwrite "
                "current value of routes."
            ),
        )
        routes_ha = parser.add_mutually_exclusive_group()
        routes_ha.add_argument(
            '--ha',
            action='store_true',
            help=_(
                "Set the router as highly available (disabled router only)"
            ),
        )
        routes_ha.add_argument(
            '--no-ha',
            action='store_true',
            help=_(
                "Clear high availability attribute of the router "
                "(disabled router only)"
            ),
        )
        parser.add_argument(
            '--external-gateway',
            metavar="<network>",
            action='append',
            help=_(
                "External Network used as router's gateway (name or ID) "
                "(repeat option to set multiple gateways per router "
                "if the L3 service plugin in use supports it)."
            ),
            dest='external_gateways',
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            dest='fixed_ips',
            help=_(
                "Desired IP and/or subnet (name or ID) "
                "on external gateway: "
                "subnet=<subnet>,ip-address=<ip-address> "
                "(repeat option to set multiple fixed IP addresses)"
            ),
        )
        snat_group = parser.add_mutually_exclusive_group()
        snat_group.add_argument(
            '--enable-snat',
            action='store_true',
            help=_("Enable Source NAT on external gateway"),
        )
        snat_group.add_argument(
            '--disable-snat',
            action='store_true',
            help=_("Disable Source NAT on external gateway"),
        )
        ndp_proxy_group = parser.add_mutually_exclusive_group()
        ndp_proxy_group.add_argument(
            '--enable-ndp-proxy',
            dest='enable_ndp_proxy',
            default=None,
            action='store_true',
            help=_("Enable IPv6 NDP proxy on external gateway"),
        )
        ndp_proxy_group.add_argument(
            '--disable-ndp-proxy',
            dest='enable_ndp_proxy',
            default=None,
            action='store_false',
            help=_("Disable IPv6 NDP proxy on external gateway"),
        )
        qos_policy_group = parser.add_mutually_exclusive_group()
        qos_policy_group.add_argument(
            '--qos-policy',
            metavar='<qos-policy>',
            help=_("Attach QoS policy to router gateway IPs"),
        )
        qos_policy_group.add_argument(
            '--no-qos-policy',
            action='store_true',
            help=_("Remove QoS policy from router gateway IPs"),
        )
        _tag.add_tag_option_to_parser_for_set(parser, _('router'))
        _parser_add_bfd_ecmp_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)

        # Get the common attributes.
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        # Get the route attributes.
        if parsed_args.ha:
            attrs['ha'] = True
        elif parsed_args.no_ha:
            attrs['ha'] = False

        if parsed_args.routes is not None:
            for route in parsed_args.routes:
                route['nexthop'] = route.pop('gateway')
            attrs['routes'] = parsed_args.routes
            if not parsed_args.no_route:
                # Map the route keys and append to the current routes.
                # The REST API will handle route validation and duplicates.
                attrs['routes'] += obj.routes
        elif parsed_args.no_route:
            attrs['routes'] = []
        if (
            parsed_args.disable_snat
            or parsed_args.enable_snat
            or parsed_args.fixed_ips
        ) and not parsed_args.external_gateways:
            msg = _(
                "You must specify '--external-gateway' in order "
                "to update the SNAT or fixed-ip values"
            )
            raise exceptions.CommandError(msg)

        if (
            parsed_args.qos_policy or parsed_args.no_qos_policy
        ) and not parsed_args.external_gateways:
            try:
                original_net_id = obj.external_gateway_info['network_id']
            except (KeyError, TypeError):
                msg = _(
                    "You must specify '--external-gateway' or the router "
                    "must already have an external network in order to "
                    "set router gateway IP QoS"
                )
                raise exceptions.CommandError(msg)
            else:
                if not attrs.get('external_gateway_info') and not attrs.get(
                    'external_gateways'
                ):
                    attrs['external_gateway_info'] = {}
                attrs['external_gateway_info']['network_id'] = original_net_id
        if parsed_args.qos_policy:
            check_qos_id = client.find_qos_policy(
                parsed_args.qos_policy, ignore_missing=False
            ).id
            if not attrs.get('external_gateways'):
                attrs['external_gateway_info']['qos_policy_id'] = check_qos_id

        if 'no_qos_policy' in parsed_args and parsed_args.no_qos_policy:
            if not attrs.get('external_gateways'):
                attrs['external_gateway_info']['qos_policy_id'] = None

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        if parsed_args.enable_ndp_proxy is not None:
            attrs['enable_ndp_proxy'] = parsed_args.enable_ndp_proxy

        _command_check_bfd_ecmp_supported(attrs, client)

        if attrs:
            external_gateways = attrs.pop('external_gateways', None)
            client.update_router(obj, **attrs)
            # If the multiple external gateways API is intended to be used,
            # do a separate API call to set external gateways.
            if external_gateways:
                client.update_external_gateways(
                    obj,
                    body={'router': {'external_gateways': external_gateways}},
                )

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)


class ShowRouter(command.ShowOne):
    _description = _("Display router details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)
        interfaces_info = []
        filters = {}
        filters['device_id'] = obj.id
        for port in client.ports(**filters):
            if port.device_owner != "network:router_gateway":
                for ip_spec in port.fixed_ips:
                    int_info = {
                        'port_id': port.id,
                        'ip_address': ip_spec.get('ip_address'),
                        'subnet_id': ip_spec.get('subnet_id'),
                    }
                    interfaces_info.append(int_info)

        setattr(obj, 'interfaces_info', interfaces_info)
        display_columns, columns = _get_columns(obj)
        _formatters['interfaces_info'] = RouterInfoColumn
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (display_columns, data)


class UnsetRouter(common.NeutronUnsetCommandWithExtraArgs):
    _description = _("Unset router properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            dest='routes',
            default=None,
            required_keys=['destination', 'gateway'],
            help=_(
                "Routes to be removed from the router. "
                "destination: destination subnet (in CIDR notation) "
                "gateway: nexthop IP address "
                "(repeat option to unset multiple routes)"
            ),
        )
        # NOTE(dmitriis): This was not extended to support selective removal
        # of external gateways due to a cpython bug in argparse:
        # https://github.com/python/cpython/issues/53584
        parser.add_argument(
            '--external-gateway',
            action='store_true',
            default=False,
            help=_("Remove external gateway information from the router"),
            dest='external_gateways',
        )
        parser.add_argument(
            '--qos-policy',
            action='store_true',
            default=False,
            help=_("Remove QoS policy from router gateway IPs"),
        )
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to modify (name or ID)"),
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('router'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)
        tmp_routes = copy.deepcopy(obj.routes)
        tmp_external_gateway_info = copy.deepcopy(obj.external_gateway_info)
        attrs = {}
        if parsed_args.routes:
            try:
                for route in parsed_args.routes:
                    route['nexthop'] = route.pop('gateway')
                    tmp_routes.remove(route)
            except ValueError:
                msg = _("Router does not contain route %s") % route
                raise exceptions.CommandError(msg)
            attrs['routes'] = tmp_routes
        if parsed_args.qos_policy:
            try:
                if (
                    tmp_external_gateway_info['network_id']
                    and tmp_external_gateway_info['qos_policy_id']
                ):
                    pass
            except (KeyError, TypeError):
                msg = _("Router does not have external network or QoS policy")
                raise exceptions.CommandError(msg)
            else:
                attrs['external_gateway_info'] = {
                    'network_id': tmp_external_gateway_info['network_id'],
                    'qos_policy_id': None,
                }

        if parsed_args.external_gateways:
            attrs['external_gateway_info'] = {}

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        if attrs:
            # If removing multiple gateways per router are supported,
            # use the relevant API to remove them all.
            if is_multiple_gateways_supported(client):
                client.remove_external_gateways(
                    obj,
                    body={'router': {'external_gateways': {}}},
                )

            client.update_router(obj, **attrs)
        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)


class AddGatewayToRouter(command.ShowOne):
    _description = _("Add router gateway")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to modify (name or ID)"),
        )
        parser.add_argument(
            metavar="<network>",
            help=_(
                "External Network to a attach a router gateway to (name or ID)"
            ),
            dest='external_gateways',
            # The argument is stored in a list in order to reuse the
            # common attribute parsing code.
            nargs=1,
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            dest='fixed_ips',
            help=_(
                "Desired IP and/or subnet (name or ID) "
                "on external gateway: "
                "subnet=<subnet>,ip-address=<ip-address> "
                "(repeat option to set multiple fixed IP addresses)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        if not is_multiple_gateways_supported(client):
            msg = _(
                'The external-gateway-multihoming extension is not enabled at '
                'the Neutron side.'
            )
            raise exceptions.CommandError(msg)

        router_obj = client.find_router(
            parsed_args.router, ignore_missing=False
        )

        # Get the common attributes.
        attrs = _get_external_gateway_attrs(
            self.app.client_manager, parsed_args
        )

        if attrs:
            external_gateways = attrs.pop('external_gateways')
            router_obj = client.add_external_gateways(
                router_obj,
                body={'router': {'external_gateways': external_gateways}},
            )

        display_columns, columns = _get_columns(router_obj)
        data = utils.get_item_properties(
            router_obj, columns, formatters=_formatters
        )
        return (display_columns, data)


class RemoveGatewayFromRouter(command.ShowOne):
    _description = _("Remove router gateway")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to modify (name or ID)."),
        )
        parser.add_argument(
            metavar="<network>",
            help=_(
                "External Network to remove a router gateway from (name or ID)"
            ),
            dest='external_gateways',
            # The argument is stored in a list in order to reuse the
            # common attribute parsing code.
            nargs=1,
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            dest='fixed_ips',
            help=_(
                "IP and/or subnet (name or ID) on the external gateway "
                "which is used to identify a particular gateway if multiple "
                "are attached to the same network: subnet=<subnet>,"
                "ip-address=<ip-address>"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        if not is_multiple_gateways_supported(client):
            msg = _(
                'The external-gateway-multihoming extension is not enabled at '
                'the Neutron side.'
            )
            raise exceptions.CommandError(msg)

        router_obj = client.find_router(
            parsed_args.router, ignore_missing=False
        )

        # Get the common attributes.
        attrs = _get_external_gateway_attrs(
            self.app.client_manager, parsed_args
        )
        if attrs:
            external_gateways = attrs.pop('external_gateways')
            router_obj = client.remove_external_gateways(
                router_obj,
                body={'router': {'external_gateways': external_gateways}},
            )

        display_columns, columns = _get_columns(router_obj)
        data = utils.get_item_properties(
            router_obj, columns, formatters=_formatters
        )
        return (display_columns, data)
