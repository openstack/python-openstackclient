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
import copy
import json
import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils


LOG = logging.getLogger(__name__)


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


def _format_external_gateway_info(info):
    try:
        return json.dumps(info)
    except (TypeError, KeyError):
        return ''


def _format_routes(routes):
    # Map the route keys to match --route option.
    for route in routes:
        if 'nexthop' in route:
            route['gateway'] = route.pop('nexthop')
    return utils.format_list_of_dicts(routes)


_formatters = {
    'admin_state_up': _format_admin_state,
    'is_admin_state_up': _format_admin_state,
    'external_gateway_info': _format_external_gateway_info,
    'availability_zones': utils.format_list,
    'availability_zone_hints': utils.format_list,
    'routes': _format_routes,
}


def _get_columns(item):
    column_map = {
        'tenant_id': 'project_id',
        'is_ha': 'ha',
        'is_distributed': 'distributed',
        'is_admin_state_up': 'admin_state_up',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    # centralized is available only for SetRouter and not for CreateRouter
    if 'centralized' in parsed_args and parsed_args.centralized:
        attrs['distributed'] = False
    if parsed_args.distributed:
        attrs['distributed'] = True
    if ('availability_zone_hints' in parsed_args
            and parsed_args.availability_zone_hints is not None):
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
        attrs['tenant_id'] = project_id

    return attrs


class AddPortToRouter(command.Command):
    _description = _("Add a port to a router")

    def get_parser(self, prog_name):
        parser = super(AddPortToRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router to which port will be added (name or ID)")
        )
        parser.add_argument(
            'port',
            metavar='<port>',
            help=_("Port to be added (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        port = client.find_port(parsed_args.port, ignore_missing=False)
        client.add_interface_to_router(client.find_router(
            parsed_args.router, ignore_missing=False), port_id=port.id)


class AddSubnetToRouter(command.Command):
    _description = _("Add a subnet to a router")

    def get_parser(self, prog_name):
        parser = super(AddSubnetToRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router to which subnet will be added (name or ID)")
        )
        parser.add_argument(
            'subnet',
            metavar='<subnet>',
            help=_("Subnet to be added (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        subnet = client.find_subnet(parsed_args.subnet,
                                    ignore_missing=False)
        client.add_interface_to_router(
            client.find_router(parsed_args.router,
                               ignore_missing=False),
            subnet_id=subnet.id)


# TODO(yanxing'an): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateRouter(command.ShowOne):
    _description = _("Create a new router")

    def get_parser(self, prog_name):
        parser = super(CreateRouter, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New router name")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable router (default)")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable router")
        )
        parser.add_argument(
            '--distributed',
            dest='distributed',
            action='store_true',
            default=False,
            help=_("Create a distributed router")
        )
        parser.add_argument(
            '--ha',
            action='store_true',
            help=_("Create a highly available router")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set router description")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--availability-zone-hint',
            metavar='<availability-zone>',
            action='append',
            dest='availability_zone_hints',
            help=_("Availability Zone in which to create this router "
                   "(Router Availability Zone extension required, "
                   "repeat option to set multiple availability zones)")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        if parsed_args.ha:
            attrs['ha'] = parsed_args.ha
        obj = client.create_router(**attrs)

        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (display_columns, data)


class DeleteRouter(command.Command):
    _description = _("Delete router(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            nargs="+",
            help=_("Router(s) to delete (name or ID)")
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
                LOG.error(_("Failed to delete router with "
                          "name or ID '%(router)s': %(e)s"),
                          {'router': router, 'e': e})

        if result > 0:
            total = len(parsed_args.router)
            msg = (_("%(result)s of %(total)s routers failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


# TODO(yanxing'an): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListRouter(command.Lister):
    _description = _("List routers")

    def get_parser(self, prog_name):
        parser = super(ListRouter, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List routers according to their name")
        )
        admin_state_group = parser.add_mutually_exclusive_group()
        admin_state_group.add_argument(
            '--enable',
            action='store_true',
            help=_("List enabled routers")
        )
        admin_state_group.add_argument(
            '--disable',
            action='store_true',
            help=_("List disabled routers")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List routers according to their project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        client = self.app.client_manager.network
        columns = (
            'id',
            'name',
            'status',
            'is_admin_state_up',
            'is_distributed',
            'is_ha',
            'project_id',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
            'State',
            'Distributed',
            'HA',
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
            args['tenant_id'] = project_id
            args['project_id'] = project_id
        if parsed_args.long:
            columns = columns + (
                'routes',
                'external_gateway_info',
            )
            column_headers = column_headers + (
                'Routes',
                'External gateway info',
            )
            # availability zone will be available only when
            # router_availability_zone extension is enabled
            if client.find_extension("router_availability_zone"):
                columns = columns + (
                    'availability_zones',
                )
                column_headers = column_headers + (
                    'Availability zones',
                )

        data = client.routers(**args)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class RemovePortFromRouter(command.Command):
    _description = _("Remove a port from a router")

    def get_parser(self, prog_name):
        parser = super(RemovePortFromRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router from which port will be removed (name or ID)")
        )
        parser.add_argument(
            'port',
            metavar='<port>',
            help=_("Port to be removed and deleted (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        port = client.find_port(parsed_args.port, ignore_missing=False)
        client.remove_interface_from_router(client.find_router(
            parsed_args.router, ignore_missing=False), port_id=port.id)


class RemoveSubnetFromRouter(command.Command):
    _description = _("Remove a subnet from a router")

    def get_parser(self, prog_name):
        parser = super(RemoveSubnetFromRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router from which the subnet will be removed (name or ID)")
        )
        parser.add_argument(
            'subnet',
            metavar='<subnet>',
            help=_("Subnet to be removed (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        subnet = client.find_subnet(parsed_args.subnet,
                                    ignore_missing=False)
        client.remove_interface_from_router(
            client.find_router(parsed_args.router,
                               ignore_missing=False),
            subnet_id=subnet.id)


# TODO(yanxing'an): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetRouter(command.Command):
    _description = _("Set router properties")

    def get_parser(self, prog_name):
        parser = super(SetRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("Set router name")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set router description')
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=None,
            help=_("Enable router")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable router")
        )
        distribute_group = parser.add_mutually_exclusive_group()
        distribute_group.add_argument(
            '--distributed',
            action='store_true',
            help=_("Set router to distributed mode (disabled router only)")
        )
        distribute_group.add_argument(
            '--centralized',
            action='store_true',
            help=_("Set router to centralized mode (disabled router only)")
        )
        routes_group = parser.add_mutually_exclusive_group()
        # ToDo(Reedip):Remove mutual exclusiveness once clear-routes is removed
        parser.add_argument(
            '--route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            dest='routes',
            default=None,
            required_keys=['destination', 'gateway'],
            help=_("Routes associated with the router "
                   "destination: destination subnet (in CIDR notation) "
                   "gateway: nexthop IP address "
                   "(repeat option to set multiple routes)")
        )
        routes_group.add_argument(
            '--no-route',
            action='store_true',
            help=_("Clear routes associated with the router. "
                   "Specify both --route and --no-route to overwrite "
                   "current value of route.")
        )
        routes_group.add_argument(
            '--clear-routes',
            action='store_true',
            help=argparse.SUPPRESS,
        )
        routes_ha = parser.add_mutually_exclusive_group()
        routes_ha.add_argument(
            '--ha',
            action='store_true',
            help=_("Set the router as highly available "
                   "(disabled router only)")
        )
        routes_ha.add_argument(
            '--no-ha',
            action='store_true',
            help=_("Clear high availability attribute of the router "
                   "(disabled router only)")
        )
        parser.add_argument(
            '--external-gateway',
            metavar="<network>",
            help=_("External Network used as router's gateway (name or ID)")
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='subnet=<subnet>,ip-address=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            optional_keys=['subnet', 'ip-address'],
            help=_("Desired IP and/or subnet (name or ID)"
                   "on external gateway: "
                   "subnet=<subnet>,ip-address=<ip-address> "
                   "(repeat option to set multiple fixed IP addresses)")
        )
        snat_group = parser.add_mutually_exclusive_group()
        snat_group.add_argument(
            '--enable-snat',
            action='store_true',
            help=_("Enable Source NAT on external gateway")
        )
        snat_group.add_argument(
            '--disable-snat',
            action='store_true',
            help=_("Disable Source NAT on external gateway")
        )
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
        if parsed_args.clear_routes:
            LOG.warning(_(
                'The --clear-routes option is deprecated, '
                'please use --no-route instead.'
            ))

        if parsed_args.routes is not None:
            for route in parsed_args.routes:
                route['nexthop'] = route.pop('gateway')
            attrs['routes'] = parsed_args.routes
            if not (parsed_args.no_route or parsed_args.clear_routes):
                # Map the route keys and append to the current routes.
                # The REST API will handle route validation and duplicates.
                attrs['routes'] += obj.routes
        elif parsed_args.no_route or parsed_args.clear_routes:
            attrs['routes'] = []
        if (parsed_args.disable_snat or parsed_args.enable_snat or
           parsed_args.fixed_ip) and not parsed_args.external_gateway:
                msg = (_("You must specify '--external-gateway' in order"
                         "to update the SNAT or fixed-ip values"))
                raise exceptions.CommandError(msg)
        if parsed_args.external_gateway:
            gateway_info = {}
            network = client.find_network(
                parsed_args.external_gateway, ignore_missing=False)
            gateway_info['network_id'] = network.id
            if parsed_args.disable_snat:
                gateway_info['enable_snat'] = False
            if parsed_args.enable_snat:
                gateway_info['enable_snat'] = True
            if parsed_args.fixed_ip:
                ips = []
                for ip_spec in parsed_args.fixed_ip:
                    if ip_spec.get('subnet', False):
                        subnet_name_id = ip_spec.pop('subnet')
                        if subnet_name_id:
                            subnet = client.find_subnet(subnet_name_id,
                                                        ignore_missing=False)
                            ip_spec['subnet_id'] = subnet.id
                    if ip_spec.get('ip-address', False):
                        ip_spec['ip_address'] = ip_spec.pop('ip-address')
                    ips.append(ip_spec)
                gateway_info['external_fixed_ips'] = ips
            attrs['external_gateway_info'] = gateway_info
        client.update_router(obj, **attrs)


class ShowRouter(command.ShowOne):
    _description = _("Display router details")

    def get_parser(self, prog_name):
        parser = super(ShowRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (display_columns, data)


class UnsetRouter(command.Command):
    _description = _("Unset router properties")

    def get_parser(self, prog_name):
        parser = super(UnsetRouter, self).get_parser(prog_name)
        parser.add_argument(
            '--route',
            metavar='destination=<subnet>,gateway=<ip-address>',
            action=parseractions.MultiKeyValueAction,
            dest='routes',
            default=None,
            required_keys=['destination', 'gateway'],
            help=_("Routes to be removed from the router "
                   "destination: destination subnet (in CIDR notation) "
                   "gateway: nexthop IP address "
                   "(repeat option to unset multiple routes)"))
        parser.add_argument(
            '--external-gateway',
            action='store_true',
            default=False,
            help=_("Remove external gateway information from the router"))
        parser.add_argument(
            'router',
            metavar="<router>",
            help=_("Router to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)
        tmp_routes = copy.deepcopy(obj.routes)
        attrs = {}
        if parsed_args.routes:
            try:
                for route in parsed_args.routes:
                    route['nexthop'] = route.pop('gateway')
                    tmp_routes.remove(route)
            except ValueError:
                msg = (_("Router does not contain route %s") % route)
                raise exceptions.CommandError(msg)
            attrs['routes'] = tmp_routes
        if parsed_args.external_gateway:
            attrs['external_gateway_info'] = {}
        if attrs:
            client.update_router(obj, **attrs)
