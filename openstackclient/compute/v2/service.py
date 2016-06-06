#   Copyright 2013 OpenStack, LLC.
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

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.i18n import _


class DeleteService(command.Command):
    """Delete service command"""

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            "service",
            metavar="<service>",
            help=_("Compute service to delete (ID only)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        compute_client.services.delete(parsed_args.service)


class ListService(command.Lister):
    """List service command"""

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
        compute_client = self.app.client_manager.compute
        if parsed_args.long:
            columns = (
                "Id",
                "Binary",
                "Host",
                "Zone",
                "Status",
                "State",
                "Updated At",
                "Disabled Reason"
            )
        else:
            columns = (
                "Id",
                "Binary",
                "Host",
                "Zone",
                "Status",
                "State",
                "Updated At"
            )
        data = compute_client.services.list(parsed_args.host,
                                            parsed_args.service)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class SetService(command.Command):
    """Set service command"""

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
            help=_("Name of service")
        )
        enabled_group = parser.add_mutually_exclusive_group()
        enabled_group.add_argument(
            "--enable",
            action="store_true",
            help=_("Enable service")
        )
        enabled_group.add_argument(
            "--disable",
            action="store_true",
            help=_("Disable service")
        )
        parser.add_argument(
            "--disable-reason",
            default=None,
            metavar="<reason>",
            help=_("Reason for disabling the service (in quotas). "
                   "Should be used with --disable option.")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        cs = compute_client.services

        if (parsed_args.enable or not parsed_args.disable) and \
                parsed_args.disable_reason:
            msg = _("Cannot specify option --disable-reason without "
                    "--disable specified.")
            raise exceptions.CommandError(msg)

        enabled = None
        if parsed_args.enable:
            enabled = True
        if parsed_args.disable:
            enabled = False

        if enabled is None:
            return
        elif enabled:
            cs.enable(parsed_args.host, parsed_args.service)
        else:
            if parsed_args.disable_reason:
                cs.disable_log_reason(parsed_args.host,
                                      parsed_args.service,
                                      parsed_args.disable_reason)
            else:
                cs.disable(parsed_args.host, parsed_args.service)
