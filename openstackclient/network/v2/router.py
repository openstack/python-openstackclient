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
    'external_gateway_info': _format_external_gateway_info,
    'availability_zones': utils.format_list,
    'availability_zone_hints': utils.format_list,
    'routes': _format_routes,
}


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
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

    # TODO(tangchen): Support getting 'external_gateway_info' property.

    return attrs


class AddPortToRouter(command.Command):
    """Add a port to a router"""

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
    """Add a subnet to a router"""

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


class CreateRouter(command.ShowOne):
    """Create a new router"""

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

        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (columns, data)


class DeleteRouter(command.Command):
    """Delete router(s)"""

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
                          "name or ID '%(router)s': %(e)s")
                          % {'router': router, 'e': e})

        if result > 0:
            total = len(parsed_args.router)
            msg = (_("%(result)s of %(total)s routers failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListRouter(command.Lister):
    """List routers"""

    def get_parser(self, prog_name):
        parser = super(ListRouter, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'status',
            'admin_state_up',
            'distributed',
            'ha',
            'tenant_id',
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

        data = client.routers()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class RemovePortFromRouter(command.Command):
    """Remove a port from a router"""

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
    """Remove a subnet from a router"""

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


class SetRouter(command.Command):
    """Set router properties"""

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
        routes_group.add_argument(
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
            help=_("Clear routes associated with the router")
        )
        routes_group.add_argument(
            '--clear-routes',
            action='store_true',
            help=argparse.SUPPRESS,
        )

        # TODO(tangchen): Support setting 'ha' property in 'router set'
        # command. It appears that changing the ha state is supported by
        # neutron under certain conditions.

        # TODO(tangchen): Support setting 'external_gateway_info' property in
        # 'router set' command.

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)

        # Get the common attributes.
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        # Get the route attributes.
        if parsed_args.no_route:
            attrs['routes'] = []
        elif parsed_args.clear_routes:
            attrs['routes'] = []
            LOG.warning(_(
                'The --clear-routes option is deprecated, '
                'please use --no-route instead.'
            ))
        elif parsed_args.routes is not None:
            # Map the route keys and append to the current routes.
            # The REST API will handle route validation and duplicates.
            for route in parsed_args.routes:
                route['nexthop'] = route.pop('gateway')
            attrs['routes'] = obj.routes + parsed_args.routes

        client.update_router(obj, **attrs)


class ShowRouter(command.ShowOne):
    """Display router details"""

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
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)


class UnsetRouter(command.Command):
    """Unset router properties"""

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
                    tmp_routes.remove(route)
            except ValueError:
                msg = (_("Router does not contain route %s") % route)
                raise exceptions.CommandError(msg)
            for route in tmp_routes:
                route['nexthop'] = route.pop('gateway')
            attrs['routes'] = tmp_routes
        if attrs:
            client.update_router(obj, **attrs)
