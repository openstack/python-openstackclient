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

import json

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.identity import common as identity_common


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


def _format_external_gateway_info(info):
    try:
        return json.dumps(info)
    except (TypeError, KeyError):
        return ''


_formatters = {
    'admin_state_up': _format_admin_state,
    'external_gateway_info': _format_external_gateway_info,
    'availability_zones': utils.format_list,
    'availability_zone_hints': utils.format_list,
}


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.admin_state_up is not None:
        attrs['admin_state_up'] = parsed_args.admin_state_up
    if parsed_args.distributed is not None:
        attrs['distributed'] = parsed_args.distributed
    if ('availability_zone_hints' in parsed_args
            and parsed_args.availability_zone_hints is not None):
        attrs['availability_zone_hints'] = parsed_args.availability_zone_hints
    # "router set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    # TODO(tangchen): Support getting 'ha' property.
    # TODO(tangchen): Support getting 'external_gateway_info' property.
    # TODO(tangchen): Support getting 'routes' property.

    return attrs


class CreateRouter(command.ShowOne):
    """Create a new router"""

    def get_parser(self, prog_name):
        parser = super(CreateRouter, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help="New router name",
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state_up',
            action='store_true',
            default=True,
            help="Enable router (default)",
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state_up',
            action='store_false',
            help="Disable router",
        )
        parser.add_argument(
            '--distributed',
            dest='distributed',
            action='store_true',
            default=False,
            help="Create a distributed router",
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Owner's project (name or ID)",
        )
        parser.add_argument(
            '--availability-zone-hint',
            metavar='<availability-zone>',
            action='append',
            dest='availability_zone_hints',
            help='Availability Zone in which to create this router '
                 '(requires the Router Availability Zone extension, '
                 'this option can be repeated).',
        )

        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_router(**attrs)

        columns = sorted(obj.keys())
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        if 'tenant_id' in columns:
            # Rename "tenant_id" to "project_id".
            index = columns.index('tenant_id')
            columns[index] = 'project_id'
        return (tuple(columns), data)


class DeleteRouter(command.Command):
    """Delete router(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            nargs="+",
            help=("Router(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        for router in parsed_args.router:
            obj = client.find_router(router)
            client.delete_router(obj)


class ListRouter(command.Lister):
    """List routers"""

    def get_parser(self, prog_name):
        parser = super(ListRouter, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
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
                'availability_zones'
            )
            column_headers = column_headers + (
                'Routes',
                'External gateway info',
                'Availability zones'
            )

        data = client.routers()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class SetRouter(command.Command):
    """Set router properties"""

    def get_parser(self, prog_name):
        parser = super(SetRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help=("Router to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set router name',
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state_up',
            action='store_true',
            default=None,
            help='Enable router',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state_up',
            action='store_false',
            help='Disable router',
        )
        distribute_group = parser.add_mutually_exclusive_group()
        distribute_group.add_argument(
            '--distributed',
            dest='distributed',
            action='store_true',
            default=None,
            help="Set router to distributed mode (disabled router only)",
        )
        distribute_group.add_argument(
            '--centralized',
            dest='distributed',
            action='store_false',
            help="Set router to centralized mode (disabled router only)",
        )

        # TODO(tangchen): Support setting 'ha' property in 'router set'
        # command. It appears that changing the ha state is supported by
        # neutron under certain conditions.

        # TODO(tangchen): Support setting 'external_gateway_info' property in
        # 'router set' command.

        # TODO(tangchen): Support setting 'routes' property in 'router set'
        # command.

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)

        attrs = _get_attrs(self.app.client_manager, parsed_args)
        if attrs == {}:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)

        client.update_router(obj, **attrs)


class ShowRouter(command.ShowOne):
    """Display router details"""

    def get_parser(self, prog_name):
        parser = super(ShowRouter, self).get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar="<router>",
            help="Router to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_router(parsed_args.router, ignore_missing=False)
        columns = sorted(obj.keys())
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (tuple(columns), data)
