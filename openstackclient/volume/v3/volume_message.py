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

"""Volume V3 Messages implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.block_storage.v3 import message as _message
from openstack import utils as sdk_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)


def _format_message(
    message: _message.Message,
) -> tuple[tuple[str, ...], tuple[Any, ...]]:
    column_headers = (
        'Created At',
        'Event ID',
        'Guaranteed Until',
        'ID',
        'Message Level',
        'Request ID',
        'Resource Type',
        'Resource UUID',
        'User Message',
    )
    columns = (
        'created_at',
        'event_id',
        'guaranteed_until',
        'id',
        'message_level',
        'request_id',
        'resource_type',
        'resource_uuid',
        'user_message',
    )
    return column_headers, utils.get_item_properties(message, columns)


class DeleteMessage(command.Command):
    _description = _('Delete a volume failure message')

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'message_ids',
            metavar='<message-id>',
            nargs='+',
            help=_('Message(s) to delete (ID)'),
        )

        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.3'):
            msg = _(
                "--os-volume-api-version 3.3 or greater is required to "
                "support the 'volume message delete' command"
            )
            raise exceptions.CommandError(msg)

        errors = 0
        for message_id in parsed_args.message_ids:
            try:
                volume_client.delete_message(message_id, ignore_missing=False)
            except Exception:
                LOG.error(_('Failed to delete message: %s'), message_id)
                errors += 1

        if errors > 0:
            total = len(parsed_args.message_ids)
            msg = _('Failed to delete %(errors)s of %(total)s messages.') % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListMessages(command.Lister):
    _description = _('List volume failure messages')

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter results by project (name or ID) (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        pagination.add_marker_pagination_option_to_parser(
            parser, include_max_items=False
        )

        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.3'):
            msg = _(
                "--os-volume-api-version 3.3 or greater is required to "
                "support the 'volume message list' command"
            )
            raise exceptions.CommandError(msg)

        column_headers = (
            'ID',
            'Event ID',
            'Resource Type',
            'Resource UUID',
            'Message Level',
            'User Message',
            'Request ID',
            'Created At',
            'Guaranteed Until',
        )
        columns = (
            'id',
            'event_id',
            'resource_type',
            'resource_uuid',
            'message_level',
            'user_message',
            'request_id',
            'created_at',
            'guaranteed_until',
        )

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project_id_sdk(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            )

        data = volume_client.messages(
            project_id=project_id,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
        )

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowMessage(command.ShowOne):
    _description = _('Show a volume failure message')

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'message_id',
            metavar='<message-id>',
            help=_('Message to show (ID).'),
        )

        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.3'):
            msg = _(
                "--os-volume-api-version 3.3 or greater is required to "
                "support the 'volume message show' command"
            )
            raise exceptions.CommandError(msg)

        message = volume_client.get_message(parsed_args.message_id)

        return _format_message(message)
