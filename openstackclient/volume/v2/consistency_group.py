#
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

"""Volume v2 consistency group action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListConsistencyGroup(command.Lister):
    """List consistency groups."""

    def get_parser(self, prog_name):
        parser = super(ListConsistencyGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action="store_true",
            help=_('Show detail for all projects. Admin only. '
                   '(defaults to False)')
        )
        parser.add_argument(
            '--long',
            action="store_true",
            help=_('List additional fields in output')
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ['ID', 'Status', 'Availability Zone',
                       'Name', 'Description', 'Volume Types']
        else:
            columns = ['ID', 'Status', 'Name']
        volume_client = self.app.client_manager.volume
        consistency_groups = volume_client.consistencygroups.list(
            detailed=True,
            search_opts={'all_tenants': parsed_args.all_projects}
        )

        return (columns, (
            utils.get_item_properties(
                s, columns,
                formatters={'Volume Types': utils.format_list})
            for s in consistency_groups))
