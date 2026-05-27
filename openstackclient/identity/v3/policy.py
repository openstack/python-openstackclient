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

"""Identity v3 Policy action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.identity.v3 import policy as _policy
from openstack import utils as sdk_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_policy(
    policy: _policy.Policy,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    columns = ('id', 'blob', 'type')
    column_headers = ('id', 'rules', 'type')
    return (column_headers, utils.get_item_properties(policy, columns))


class CreatePolicy(command.ShowOne):
    _description = _("Create new policy")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            default="application/json",
            help=_(
                'New MIME type of the policy rules file '
                '(defaults to application/json)'
            ),
        )
        parser.add_argument(
            'rules',
            metavar='<filename>',
            help=_('New serialized policy rules file'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        blob = utils.read_blob_file_contents(parsed_args.rules)

        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        policy = identity_client.create_policy(
            blob=blob, type=parsed_args.type
        )

        return _format_policy(policy)


class DeletePolicy(command.Command):
    _description = _("Delete policy(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            nargs='+',
            help=_('Policy(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        result = 0
        for i in parsed_args.policy:
            try:
                identity_client.delete_policy(i, ignore_missing=False)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete policy with name or "
                        "ID '%(policy)s': %(e)s"
                    ),
                    {'policy': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.policy)
            msg = _("%(result)s of %(total)s policies failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListPolicy(command.Lister):
    _description = _("List policies")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        columns: tuple[str, ...] = ('ID', 'Type')
        column_headers: tuple[str, ...] = columns
        if parsed_args.long:
            columns += ('Blob',)
            column_headers += ('Rules',)
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        data = identity_client.policies()
        return (
            column_headers,
            [
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ],
        )


class SetPolicy(command.Command):
    _description = _("Set policy properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help=_('Policy to modify'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            help=_('New MIME type of the policy rules file'),
        )
        parser.add_argument(
            '--rules',
            metavar='<filename>',
            help=_('New serialized policy rules file'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )

        kwargs = {}

        if parsed_args.rules:
            kwargs['blob'] = utils.read_blob_file_contents(parsed_args.rules)

        if parsed_args.type:
            kwargs['type'] = parsed_args.type

        identity_client.update_policy(parsed_args.policy, **kwargs)


class ShowPolicy(command.ShowOne):
    _description = _("Display policy details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help=_('Policy to display'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        policy = identity_client.get_policy(parsed_args.policy)

        return _format_policy(policy)
