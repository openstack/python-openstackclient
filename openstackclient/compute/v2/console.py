#   Copyright 2012-2013 OpenStack Foundation
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

"""Compute v2 Console action implementations"""

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


def _get_console_columns(item):
    # To maintain backwards compatibility we need to rename sdk props to
    # whatever OSC was using before
    hidden_columns = ['id', 'links', 'location', 'name']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class ShowConsoleLog(command.Command):
    _description = _("Show server's console output")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Server to show console log (name or ID)"),
        )
        parser.add_argument(
            '--lines',
            metavar='<num-lines>',
            type=int,
            default=None,
            action=parseractions.NonNegativeAction,
            help=_(
                "Number of lines to display from the end of the log "
                "(default=all)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = compute_client.find_server(
            name_or_id=parsed_args.server, ignore_missing=False
        )

        output = compute_client.get_server_console_output(
            server.id, length=parsed_args.lines
        )
        data = None
        if output:
            data = output.get('output', None)

        if data and data[-1] != '\n':
            data += '\n'
        self.app.stdout.write(data)


class ShowConsoleURL(command.ShowOne):
    _description = _("Show server's remote console URL")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_("Server to show URL (name or ID)"),
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--novnc',
            dest='url_type',
            action='store_const',
            const='novnc',
            default='novnc',
            help=_("Show noVNC console URL (default)"),
        )
        type_group.add_argument(
            '--xvpvnc',
            dest='url_type',
            action='store_const',
            const='xvpvnc',
            help=_("Show xvpvnc console URL"),
        )
        type_group.add_argument(
            '--spice',
            dest='url_type',
            action='store_const',
            const='spice-html5',
            help=_("Show SPICE console URL"),
        )
        type_group.add_argument(
            '--rdp',
            dest='url_type',
            action='store_const',
            const='rdp-html5',
            help=_("Show RDP console URL"),
        )
        type_group.add_argument(
            '--serial',
            dest='url_type',
            action='store_const',
            const='serial',
            help=_("Show serial console URL"),
        )
        type_group.add_argument(
            '--mks',
            dest='url_type',
            action='store_const',
            const='webmks',
            help=_("Show WebMKS console URL"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        data = compute_client.create_console(
            server.id, console_type=parsed_args.url_type
        )

        display_columns, columns = _get_console_columns(data)
        data = utils.get_dict_properties(data, columns)

        return (display_columns, data)
