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

"""Service action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.i18n import _LE


LOG = logging.getLogger(__name__)


class DeleteService(command.Command):
    """Delete compute service(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            "service",
            metavar="<service>",
            nargs='+',
            help=_("Compute service(s) to delete (ID only)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for s in parsed_args.service:
            try:
                compute_client.services.delete(s)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete compute service with "
                          "ID '%(service)s': %(e)s")
                          % {'service': s, 'e': e})

        if result > 0:
            total = len(parsed_args.service)
            msg = (_("%(result)s of %(total)s compute services failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListService(command.Lister):
    """List compute services"""

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
                "ID",
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
                "ID",
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
    """Set compute service properties"""

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
        up_down_group = parser.add_mutually_exclusive_group()
        up_down_group.add_argument(
            '--up',
            action='store_true',
            help=_('Force up service'),
        )
        up_down_group.add_argument(
            '--down',
            action='store_true',
            help=_('Force down service'),
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

        result = 0
        enabled = None
        try:
            if parsed_args.enable:
                enabled = True
            if parsed_args.disable:
                enabled = False

            if enabled is not None:
                if enabled:
                    cs.enable(parsed_args.host, parsed_args.service)
                else:
                    if parsed_args.disable_reason:
                        cs.disable_log_reason(parsed_args.host,
                                              parsed_args.service,
                                              parsed_args.disable_reason)
                    else:
                        cs.disable(parsed_args.host, parsed_args.service)
        except Exception:
            status = "enabled" if enabled else "disabled"
            LOG.error(_LE("Failed to set service status to %s"), status)
            result += 1

        force_down = None
        try:
            if parsed_args.down:
                force_down = True
            if parsed_args.up:
                force_down = False
            if force_down is not None:
                cs.force_down(parsed_args.host, parsed_args.service,
                              force_down=force_down)
        except Exception:
            state = "down" if force_down else "up"
            LOG.error(_LE("Failed to set service state to %s"), state)
            result += 1

        if result > 0:
            msg = _("Compute service %(service)s of host %(host)s failed to "
                    "set.") % {"service": parsed_args.service,
                               "host": parsed_args.host}
            raise exceptions.CommandError(msg)
