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

"""Volume v2 transfer action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListTransferRequests(command.Lister):
    """Lists all volume transfer requests."""

    def get_parser(self, prog_name):
        parser = super(ListTransferRequests, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            dest='all_projects',
            action="store_true",
            default=False,
            help=_('Shows detail for all projects. Admin only. '
                   '(defaults to False)')
        )
        return parser

    def take_action(self, parsed_args):
        columns = ['ID', 'Volume ID', 'Name']
        column_headers = ['ID', 'Volume', 'Name']

        volume_client = self.app.client_manager.volume

        volume_transfer_result = volume_client.transfers.list(
            detailed=True,
            search_opts={'all_tenants': parsed_args.all_projects}
        )

        return (column_headers, (
            utils.get_item_properties(s, columns)
            for s in volume_transfer_result))
