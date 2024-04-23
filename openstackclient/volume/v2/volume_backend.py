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

"""Storage backend action implementations"""

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ShowCapability(command.Lister):
    _description = _("Show capability command")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "host",
            metavar="<host>",
            help=_("List capabilities of specified host (host@backend-name)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        columns = [
            'Title',
            'Key',
            'Type',
            'Description',
        ]

        data = volume_client.get_capabilities(parsed_args.host)

        # The get capabilities API is... interesting. We only want the names of
        # the capabilities that can set for a backend through extra specs, so
        # we need to extract out that part of the mess that is returned.
        print_data = []
        keys = data.properties
        for key in keys:
            # Stuff the key into the details to make it easier to output
            capability_data = data.properties[key]
            capability_data['key'] = key
            print_data.append(capability_data)

        return (
            columns,
            (
                utils.get_dict_properties(
                    s,
                    columns,
                )
                for s in print_data
            ),
        )


class ListPool(command.Lister):
    _description = _("List pool command")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=_("Show detailed information about pools."),
        )
        # TODO(smcginnis): Starting with Cinder microversion 3.33, user is also
        # able to pass in --filters with a <key>=<value> pair to filter on.
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if parsed_args.long:
            columns = [
                'name',
                'capabilities',
            ]

            headers = [
                'Name',
                'Capabilities',
            ]
        else:
            columns = [
                'Name',
            ]
            headers = columns

        data = volume_client.backend_pools(detailed=parsed_args.long)
        formatters = {'capabilities': format_columns.DictColumn}
        return (
            headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=formatters,
                )
                for s in data
            ),
        )
