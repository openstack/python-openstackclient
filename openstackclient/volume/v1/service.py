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

"""Service action implementations"""

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


class ListService(command.Lister):
    _description = _("List service command")

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            "--host",
            metavar="<host>",
            help=_("List services on specified host (name only)")
        )
        parser.add_argument(
            "--service",
            metavar="<service>",
            help=_("List only specified service (name only)")
        )
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.volume

        if parsed_args.long:
            columns = [
                "Binary",
                "Host",
                "Zone",
                "Status",
                "State",
                "Updated At",
                "Disabled Reason"
            ]
        else:
            columns = [
                "Binary",
                "Host",
                "Zone",
                "Status",
                "State",
                "Updated At"
            ]

        data = service_client.services.list(parsed_args.host,
                                            parsed_args.service)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class SetService(command.Command):
    _description = _("Set volume service properties")

    def get_parser(self, prog_name):
        parser = super(SetService, self).get_parser(prog_name)
        parser.add_argument(
            "host",
            metavar="<host>",
            help=_("Name of host")
        )
        parser.add_argument(
            "service",
            metavar="<service>",
            help=_("Name of service (Binary name)")
        )
        enabled_group = parser.add_mutually_exclusive_group()
        enabled_group.add_argument(
            "--enable",
            action="store_true",
            help=_("Enable volume service")
        )
        enabled_group.add_argument(
            "--disable",
            action="store_true",
            help=_("Disable volume service")
        )
        parser.add_argument(
            "--disable-reason",
            metavar="<reason>",
            help=_("Reason for disabling the service "
                   "(should be used with --disable option)")
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.disable_reason and not parsed_args.disable:
            msg = _("Cannot specify option --disable-reason without "
                    "--disable specified.")
            raise exceptions.CommandError(msg)

        service_client = self.app.client_manager.volume
        if parsed_args.enable:
            service_client.services.enable(
                parsed_args.host, parsed_args.service)
        if parsed_args.disable:
            if parsed_args.disable_reason:
                service_client.services.disable_log_reason(
                    parsed_args.host,
                    parsed_args.service,
                    parsed_args.disable_reason)
            else:
                service_client.services.disable(
                    parsed_args.host, parsed_args.service)
