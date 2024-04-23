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

import logging as LOG

from cinderclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


class DeleteMessage(command.Command):
    _description = _('Delete a volume failure message')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'message_ids',
            metavar='<message-id>',
            nargs='+',
            help=_('Message(s) to delete (ID)'),
        )

        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.3'):
            msg = _(
                "--os-volume-api-version 3.3 or greater is required to "
                "support the 'volume message delete' command"
            )
            raise exceptions.CommandError(msg)

        errors = 0
        for message_id in parsed_args.message_ids:
            try:
                volume_client.messages.delete(message_id)
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

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter results by project (name or ID) (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        pagination.add_marker_pagination_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        identity_client = self.app.client_manager.identity

        if volume_client.api_version < api_versions.APIVersion('3.3'):
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

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        search_opts = {
            'project_id': project_id,
        }
        data = volume_client.messages.list(
            search_opts=search_opts,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
        )

        return (
            column_headers,
            (utils.get_item_properties(s, column_headers) for s in data),
        )


class ShowMessage(command.ShowOne):
    _description = _('Show a volume failure message')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'message_id',
            metavar='<message-id>',
            help=_('Message to show (ID).'),
        )

        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.3'):
            msg = _(
                "--os-volume-api-version 3.3 or greater is required to "
                "support the 'volume message show' command"
            )
            raise exceptions.CommandError(msg)

        message = volume_client.messages.get(parsed_args.message_id)

        return zip(*sorted(message._info.items()))
