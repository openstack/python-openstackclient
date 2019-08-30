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

"""Auto-allocated Topology Implementations"""

import logging

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils

LOG = logging.getLogger(__name__)


_formatters = {
    'location': format_columns.DictColumn,
}


def _get_columns(item):
    column_map = {
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


def _format_check_resource_columns():
    return ('dry_run',)


def _format_check_resource(item):
    item_id = getattr(item, 'id', False)
    if item_id == 'dry-run=pass':
        item.check_resource = 'pass'
    return item


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if parsed_args.project:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id
    if parsed_args.check_resources:
        attrs['check_resources'] = True

    return attrs


# TODO(ankur-gupta-f): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateAutoAllocatedTopology(command.ShowOne):
    _description = _("Create the  auto allocated topology for project")

    def get_parser(self, prog_name):
        parser = super(CreateAutoAllocatedTopology, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Return the auto allocated topology for a given project. "
                   "Default is current project")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--check-resources',
            action='store_true',
            help=_("Validate the requirements for auto allocated topology. "
                   "Does not return a topology.")
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            default=True,
            help=_("If topology exists returns the topology's "
                   "information (Default)")
        )

        return parser

    def check_resource_topology(self, client, parsed_args):
        obj = client.validate_auto_allocated_topology(parsed_args.project)

        columns = _format_check_resource_columns()
        data = utils.get_item_properties(
            _format_check_resource(obj),
            columns,
            formatters=_formatters,
        )
        return (columns, data)

    def get_topology(self, client, parsed_args):
        obj = client.get_auto_allocated_topology(parsed_args.project)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        if parsed_args.check_resources:
            columns, data = self.check_resource_topology(client, parsed_args)
        else:
            columns, data = self.get_topology(client, parsed_args)
        return (columns, data)


# TODO(ankur-gupta-f): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class DeleteAutoAllocatedTopology(command.Command):
    _description = _("Delete auto allocated topology for project")

    def get_parser(self, prog_name):
        parser = super(DeleteAutoAllocatedTopology, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Delete auto allocated topology for a given project. '
                   'Default is the current project')
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        client.delete_auto_allocated_topology(parsed_args.project)
