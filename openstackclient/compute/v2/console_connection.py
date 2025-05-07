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

"""Compute v2 Console auth token implementations."""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


def _get_console_connection_columns(item):
    column_map: dict[str, str] = {}
    hidden_columns = ['id', 'location', 'name']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class ShowConsoleConnectionInformation(command.ShowOne):
    _description = _("Show server's remote console connection information")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'token',
            metavar='<token>',
            help=_("Nova console token to lookup"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        data = compute_client.validate_console_auth_token(parsed_args.token)
        display_columns, columns = _get_console_connection_columns(data)
        data = utils.get_dict_properties(data, columns)

        return (display_columns, data)
