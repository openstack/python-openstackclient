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

"""Security Groups Default Statefulness action implementations"""

import argparse
import logging
from collections.abc import Iterable, Sequence
from typing import Any

from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)


def _get_columns(item: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    hidden_columns = ['location', 'name', 'revision_number']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateSecurityGroupDefaultStatefulness(command.ShowOne):
    _description = _(
        "Create a default statefulness setting for security groups"
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)

        stateful_group = parser.add_mutually_exclusive_group(required=True)
        stateful_group.add_argument(
            "--stateful",
            action='store_true',
            default=None,
            dest='stateful',
            help=_("Set default statefulness to stateful"),
        )
        stateful_group.add_argument(
            "--stateless",
            action='store_false',
            default=None,
            dest='stateful',
            help=_("Set default statefulness to stateless"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "Apply the setting to this project (name or ID). "
                "If not specified, the setting applies system-wide"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        attrs: dict[str, Any] = {}
        if parsed_args.stateful is not None:
            attrs['stateful'] = parsed_args.stateful
        project_id = None
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.sdk_connection.identity
            project_id = identity_common.find_project_id_sdk(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            )
        # Always set this, even if `None`, otherwise the Neutron API will
        # fulfill this value with the user project ID instead.
        attrs['project_id'] = project_id

        obj = client.create_security_groups_default_statefulness(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)


class DeleteSecurityGroupDefaultStatefulness(command.Command):
    _description = _("Delete security group default statefulness setting(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'setting',
            metavar='<setting>',
            nargs="+",
            help=_("Default statefulness setting(s) to delete (ID only)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        result = 0
        client = self.app.client_manager.network
        for s in parsed_args.setting:
            try:
                obj = client.find_security_groups_default_statefulness(
                    s, ignore_missing=False
                )
                client.delete_security_groups_default_statefulness(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete default statefulness setting "
                        "with ID '%(id)s': %(e)s"
                    ),
                    {'id': s, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.setting)
            msg = _(
                "%(result)s of %(total)s default statefulness settings "
                "failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListSecurityGroupDefaultStatefulness(command.Lister):
    _description = _("List security group default statefulness settings")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List only settings for this project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        client = self.app.client_manager.network
        column_headers = (
            'ID',
            'Project ID',
            'Stateful',
        )
        columns = (
            'id',
            'project_id',
            'stateful',
        )

        query: dict[str, Any] = {}
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.sdk_connection.identity
            project_id = identity_common.find_project_id_sdk(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            )
            query['project_id'] = project_id

        data = client.security_groups_default_statefulness(**query)

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class SetSecurityGroupDefaultStatefulness(command.Command):
    _description = _("Update a security group default statefulness setting")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'setting',
            metavar='<setting>',
            help=_("Default statefulness setting to modify (ID only)"),
        )
        stateful_group = parser.add_mutually_exclusive_group(required=True)
        stateful_group.add_argument(
            "--stateful",
            action='store_true',
            default=None,
            dest='stateful',
            help=_("Set default statefulness to stateful"),
        )
        stateful_group.add_argument(
            "--stateless",
            action='store_false',
            default=None,
            dest='stateful',
            help=_("Set default statefulness to stateless"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        obj = client.find_security_groups_default_statefulness(
            parsed_args.setting, ignore_missing=False
        )
        attrs: dict[str, Any] = {}
        if parsed_args.stateful is not None:
            attrs['stateful'] = parsed_args.stateful
        client.update_security_groups_default_statefulness(obj, **attrs)


class ShowSecurityGroupDefaultStatefulness(command.ShowOne):
    _description = _("Show a security group default statefulness setting")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'setting',
            metavar='<setting>',
            help=_("Default statefulness setting to display (ID only)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        obj = client.find_security_groups_default_statefulness(
            parsed_args.setting, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)
