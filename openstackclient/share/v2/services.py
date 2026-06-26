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

import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from manilaclient import api_versions
from osc_lib import exceptions
from osc_lib import utils as osc_utils

from openstackclient import command
from openstackclient.i18n import _


class SetShareService(command.Command):
    """Enable/disable share service (Admin only)."""

    _description = _("Enable/Disable share service (Admin only).")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'host',
            metavar='<host>',
            help=_("Host name as 'example_host@example_backend'."),
        )
        parser.add_argument(
            'binary',
            metavar='<binary>',
            help=_(
                "Service binary, could be 'manila-share', "
                "'manila-scheduler' or 'manila-data'"
            ),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable share service'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable share service'),
        )
        parser.add_argument(
            "--disable-reason",
            metavar="<reason>",
            help=_(
                "Reason for disabling the service "
                "(should be used with --disable option)"
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        if parsed_args.disable_reason and not parsed_args.disable:
            msg = _(
                "Cannot specify option --disable-reason without "
                "--disable specified."
            )
            raise exceptions.CommandError(msg)

        share_client = self.app.client_manager.share

        if parsed_args.enable:
            try:
                share_client.services.enable(
                    parsed_args.host, parsed_args.binary
                )
            except Exception as e:
                msg = _("Failed to enable service: %(e)s")
                raise exceptions.CommandError(msg % {'e': e})

        if parsed_args.disable:
            if parsed_args.disable_reason:
                if share_client.api_version < api_versions.APIVersion("2.83"):
                    raise exceptions.CommandError(
                        "Service disable reason can be specified only with "
                        "manila API version >= 2.83"
                    )
            try:
                if parsed_args.disable_reason:
                    share_client.services.disable(
                        parsed_args.host,
                        parsed_args.binary,
                        disable_reason=parsed_args.disable_reason,
                    )
                else:
                    share_client.services.disable(
                        parsed_args.host, parsed_args.binary
                    )
            except Exception as e:
                msg = _("Failed to disable service: %(e)s")
                raise exceptions.CommandError(msg % {'e': e})


class ListShareService(command.Lister):
    """List share services (Admin only)."""

    _description = _("List share services (Admin only).")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--host",
            metavar="<host>",
            default=None,
            help=_("Filter services by name of the host."),
        )
        parser.add_argument(
            "--binary",
            metavar="<binary>",
            default=None,
            help=_("Filter services by the name of the service."),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=_("Filter results by status."),
        )
        parser.add_argument(
            "--state",
            metavar="<state>",
            default=None,
            choices=['up', 'down'],
            help=_("Filter results by state."),
        )
        parser.add_argument(
            "--zone",
            metavar="<zone>",
            default=None,
            help=_("Filter services by their availability zone."),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share

        search_opts = {
            'host': parsed_args.host,
            'binary': parsed_args.binary,
            'status': parsed_args.status,
            'state': parsed_args.state,
            'zone': parsed_args.zone,
        }

        services = share_client.services.list(search_opts=search_opts)

        columns = [
            'ID',
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
        ]
        if share_client.api_version >= api_versions.APIVersion("2.83"):
            columns.append('Disabled Reason')
        if share_client.api_version >= api_versions.APIVersion("2.86"):
            columns.append('Ensuring')

        data = (
            osc_utils.get_dict_properties(service._info, columns)
            for service in services
        )

        return (columns, data)


class EnsureShareService(command.Command):
    """Run ensure shares in a back end (Admin only)."""

    _description = _("Run ensure shares in a back end (Admin only).")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'host',
            metavar='<host>',
            help=_(
                "Host to run ensure shares. 'example_host@example_backend'."
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        if share_client.api_version < api_versions.APIVersion("2.86"):
            raise exceptions.CommandError(
                "Ensure shares API is only available in "
                "manila API version >= 2.86"
            )

        try:
            share_client.services.ensure_shares(parsed_args.host)
        except Exception as e:
            msg = _("Failed to ensure shares: %(e)s")
            raise exceptions.CommandError(msg % {'e': e})
