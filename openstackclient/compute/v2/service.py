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

from novaclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class DeleteService(command.Command):
    _description = _("Delete compute service(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            "service",
            metavar="<service>",
            nargs='+',
            help=_("Compute service(s) to delete (ID only). If using "
                   "``--os-compute-api-version`` 2.53 or greater, the ID is "
                   "a UUID which can be retrieved by listing compute services "
                   "using the same 2.53+ microversion.")
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
                          "ID '%(service)s': %(e)s"), {'service': s, 'e': e})

        if result > 0:
            total = len(parsed_args.service)
            msg = (_("%(result)s of %(total)s compute services failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListService(command.Lister):
    _description = _("List compute services. Using "
                     "``--os-compute-api-version`` 2.53 or greater will "
                     "return the ID as a UUID value which can be used to "
                     "uniquely identify the service in a multi-cell "
                     "deployment.")

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
            help=_("List only specified service binaries (name only). For "
                   "example, ``nova-compute``, ``nova-conductor``, etc.")
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
    _description = _("Set compute service properties")

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
            help=_("Name of service (Binary name), for example "
                   "``nova-compute``")
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
            help=_("Reason for disabling the service (in quotes). "
                   "Should be used with --disable option.")
        )
        up_down_group = parser.add_mutually_exclusive_group()
        up_down_group.add_argument(
            '--up',
            action='store_true',
            help=_('Force up service. Requires ``--os-compute-api-version`` '
                   '2.11 or greater.'),
        )
        up_down_group.add_argument(
            '--down',
            action='store_true',
            help=_('Force down service. Requires ``--os-compute-api-version`` '
                   '2.11 or greater.'),
        )
        return parser

    @staticmethod
    def _find_service_by_host_and_binary(cs, host, binary):
        """Utility method to find a compute service by host and binary

        :param host: the name of the compute service host
        :param binary: the compute service binary, e.g. nova-compute
        :returns: novaclient.v2.services.Service dict-like object
        :raises: CommandError if no or multiple results were found
        """
        services = cs.list(host=host, binary=binary)
        # Did we find anything?
        if not len(services):
            msg = _('Compute service for host "%(host)s" and binary '
                    '"%(binary)s" not found.') % {
                        'host': host, 'binary': binary}
            raise exceptions.CommandError(msg)
        # Did we find more than one result? This should not happen but let's
        # be safe.
        if len(services) > 1:
            # TODO(mriedem): If we have an --id option for 2.53+ then we can
            # say to use that option to uniquely identify the service.
            msg = _('Multiple compute services found for host "%(host)s" and '
                    'binary "%(binary)s". Unable to proceed.') % {
                        'host': host, 'binary': binary}
            raise exceptions.CommandError(msg)
        return services[0]

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        cs = compute_client.services

        if (parsed_args.enable or not parsed_args.disable) and \
                parsed_args.disable_reason:
            msg = _("Cannot specify option --disable-reason without "
                    "--disable specified.")
            raise exceptions.CommandError(msg)

        # Starting with microversion 2.53, there is a single
        # PUT /os-services/{service_id} API for updating nova-compute
        # services. If 2.53+ is used we need to find the nova-compute
        # service using the --host and --service (binary) values.
        requires_service_id = (
            compute_client.api_version >= api_versions.APIVersion('2.53'))
        service_id = None
        if requires_service_id:
            # TODO(mriedem): Add an --id option so users can pass the service
            # id (as a uuid) directly rather than make us look it up using
            # host/binary.
            service_id = SetService._find_service_by_host_and_binary(
                cs, parsed_args.host, parsed_args.service).id

        result = 0
        enabled = None
        try:
            if parsed_args.enable:
                enabled = True
            if parsed_args.disable:
                enabled = False

            if enabled is not None:
                if enabled:
                    args = (service_id,) if requires_service_id else (
                        parsed_args.host, parsed_args.service)
                    cs.enable(*args)
                else:
                    if parsed_args.disable_reason:
                        args = (service_id, parsed_args.disable_reason) if \
                            requires_service_id else (
                            parsed_args.host,
                            parsed_args.service,
                            parsed_args.disable_reason)
                        cs.disable_log_reason(*args)
                    else:
                        args = (service_id,) if requires_service_id else (
                            parsed_args.host, parsed_args.service)
                        cs.disable(*args)
        except Exception:
            status = "enabled" if enabled else "disabled"
            LOG.error("Failed to set service status to %s", status)
            result += 1

        force_down = None
        if parsed_args.down:
            force_down = True
        if parsed_args.up:
            force_down = False
        if force_down is not None:
            if compute_client.api_version < api_versions.APIVersion(
                    '2.11'):
                msg = _('--os-compute-api-version 2.11 or later is '
                        'required')
                raise exceptions.CommandError(msg)
            try:
                args = (service_id, force_down) if requires_service_id else (
                    parsed_args.host, parsed_args.service, force_down)
                cs.force_down(*args)
            except Exception:
                state = "down" if force_down else "up"
                LOG.error("Failed to set service state to %s", state)
                result += 1

        if result > 0:
            msg = _("Compute service %(service)s of host %(host)s failed to "
                    "set.") % {"service": parsed_args.service,
                               "host": parsed_args.host}
            raise exceptions.CommandError(msg)
