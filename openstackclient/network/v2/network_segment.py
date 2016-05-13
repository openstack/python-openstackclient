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

"""Network segment action implementations"""

# TODO(rtheis): Add description and name properties when support is available.

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListNetworkSegment(command.Lister):
    """List network segments

       (Caution: This is a beta command and subject to change.
        Use global option --os-beta-command to enable
        this command)
    """

    def get_parser(self, prog_name):
        parser = super(ListNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_('List network segments that belong to this '
                   'network (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        self.validate_os_beta_command_enabled()

        network_client = self.app.client_manager.network

        filters = {}
        if parsed_args.network:
            _network = network_client.find_network(
                parsed_args.network,
                ignore_missing=False
            )
            filters = {'network_id': _network.id}
        data = network_client.segments(**filters)

        headers = (
            'ID',
            'Network',
            'Network Type',
            'Segment',
        )
        columns = (
            'id',
            'network_id',
            'network_type',
            'segmentation_id',
        )
        if parsed_args.long:
            headers = headers + (
                'Physical Network',
            )
            columns = columns + (
                'physical_network',
            )

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowNetworkSegment(command.ShowOne):
    """Display network segment details

       (Caution: This is a beta command and subject to change.
        Use global option --os-beta-command to enable
        this command)
    """

    def get_parser(self, prog_name):
        parser = super(ShowNetworkSegment, self).get_parser(prog_name)
        parser.add_argument(
            'network_segment',
            metavar='<network-segment>',
            help=_('Network segment to display (ID only)'),
        )
        return parser

    def take_action(self, parsed_args):
        self.validate_os_beta_command_enabled()

        client = self.app.client_manager.network
        obj = client.find_segment(
            parsed_args.network_segment,
            ignore_missing=False
        )
        columns = tuple(sorted(obj.keys()))
        data = utils.get_item_properties(obj, columns)
        return (columns, data)
