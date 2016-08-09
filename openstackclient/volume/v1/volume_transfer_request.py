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

"""Volume v1 transfer action implementations"""

from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _


class CreateTransferRequest(command.ShowOne):
    """Create volume transfer request."""

    def get_parser(self, prog_name):
        parser = super(CreateTransferRequest, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar="<name>",
            help=_('New transfer request name (default to None)')
        )
        parser.add_argument(
            'volume',
            metavar="<volume>",
            help=_('Volume to transfer (name or ID)')
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(
            volume_client.volumes, parsed_args.volume).id
        volume_transfer_request = volume_client.transfers.create(
            volume_id, parsed_args.name,
        )
        volume_transfer_request._info.pop("links", None)

        return zip(*sorted(six.iteritems(volume_transfer_request._info)))


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
