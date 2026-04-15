#   Copyright 2017 Huawei, Inc. All rights reserved.
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

"""Compute v2 Server operation event implementations"""

import logging
import uuid

from cliff import columns
import iso8601
from openstack import exceptions as sdk_exceptions
from openstack import utils as sdk_utils
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


# TODO(stephenfin): Move this to osc_lib since it's useful elsewhere (e.g.
# glance)
def is_uuid_like(value) -> bool:
    """Returns validation of a value as a UUID.

    :param val: Value to verify
    :type val: string
    :returns: bool

    .. versionchanged:: 1.1.1
       Support non-lowercase UUIDs.
    """
    try:
        formatted_value = (
            value.replace('urn:', '')
            .replace('uuid:', '')
            .strip('{}')
            .replace('-', '')
            .lower()
        )
        return str(uuid.UUID(value)).replace('-', '') == formatted_value
    except (TypeError, ValueError, AttributeError):
        return False


class ServerActionEventColumn(columns.FormattableColumn):
    """Custom formatter for server action events.

    Format the :class:`~openstack.compute.v2.server_action.ServerActionEvent`
    objects as we'd like.
    """

    def _format_event(self, event):
        hidden_columns = ['id', 'name', 'location']
        _, columns = utils.get_osc_show_columns_for_sdk_resource(
            event, {}, hidden_columns
        )
        data = utils.get_item_properties(event, columns)
        return dict(zip(columns, data))

    def human_readable(self):
        events = [self._format_event(event) for event in self._value]
        return utils.format_list_of_dicts(events)

    def machine_readable(self):
        events = [self._format_event(event) for event in self._value]
        return events


def _get_server_event_columns(item, client):
    hidden_columns = ['name', 'server_id', 'links', 'location']

    if not sdk_utils.supports_microversion(client, '2.58'):
        # updated_at was introduced in 2.58
        hidden_columns.append('updated_at')

    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class ListServerEvent(command.Lister):
    """List recent events of a server.

    Specify ``--os-compute-api-version 2.21`` or higher to show events for a
    deleted server, specified by ID only.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to list events (name or ID)'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        parser.add_argument(
            '--changes-since',
            dest='changes_since',
            metavar='<changes-since>',
            help=_(
                "List only server events changed later or equal to a certain "
                "point of time. The provided time should be an ISO 8061 "
                "formatted time, e.g. ``2016-03-04T06:27:59Z``. "
                "(supported with --os-compute-api-version 2.58 or above)"
            ),
        )
        parser.add_argument(
            '--changes-before',
            dest='changes_before',
            metavar='<changes-before>',
            help=_(
                "List only server events changed earlier or equal to a "
                "certain point of time. The provided time should be an ISO "
                "8061 formatted time, e.g. ``2016-03-04T06:27:59Z``. "
                "(supported with --os-compute-api-version 2.66 or above)"
            ),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        kwargs = {}

        if parsed_args.marker:
            if not sdk_utils.supports_microversion(compute_client, '2.58'):
                msg = _(
                    '--os-compute-api-version 2.58 or greater is required to '
                    'support the --marker option'
                )
                raise exceptions.CommandError(msg)

            kwargs['marker'] = parsed_args.marker

        if parsed_args.limit:
            if not sdk_utils.supports_microversion(compute_client, '2.58'):
                msg = _(
                    '--os-compute-api-version 2.58 or greater is required to '
                    'support the --limit option'
                )
                raise exceptions.CommandError(msg)

            kwargs['limit'] = parsed_args.limit
            kwargs['paginated'] = False

        if parsed_args.changes_since:
            if not sdk_utils.supports_microversion(compute_client, '2.58'):
                msg = _(
                    '--os-compute-api-version 2.58 or greater is required to '
                    'support the --changes-since option'
                )
                raise exceptions.CommandError(msg)

            try:
                iso8601.parse_date(parsed_args.changes_since)
            except (TypeError, iso8601.ParseError):
                msg = _('Invalid changes-since value: %s')
                raise exceptions.CommandError(msg % parsed_args.changes_since)

            kwargs['changes_since'] = parsed_args.changes_since

        if parsed_args.changes_before:
            if not sdk_utils.supports_microversion(compute_client, '2.66'):
                msg = _(
                    '--os-compute-api-version 2.66 or greater is required to '
                    'support the --changes-before option'
                )
                raise exceptions.CommandError(msg)

            try:
                iso8601.parse_date(parsed_args.changes_before)
            except (TypeError, iso8601.ParseError):
                msg = _('Invalid changes-before value: %s')
                raise exceptions.CommandError(msg % parsed_args.changes_before)

            kwargs['changes_before'] = parsed_args.changes_before

        try:
            server_id = compute_client.find_server(
                parsed_args.server, ignore_missing=False
            ).id
        except sdk_exceptions.ResourceNotFound:
            # If we fail to find the resource, it is possible the server is
            # deleted. Try once more using the <server> arg directly if it is a
            # UUID.
            if is_uuid_like(parsed_args.server):
                server_id = parsed_args.server
            else:
                raise

        data = compute_client.server_actions(server_id, **kwargs)

        columns: tuple[str, ...] = (
            'request_id',
            'server_id',
            'action',
            'start_time',
        )
        column_headers: tuple[str, ...] = (
            'Request ID',
            'Server ID',
            'Action',
            'Start Time',
        )

        if parsed_args.long:
            columns += (
                'message',
                'project_id',
                'user_id',
            )
            column_headers += (
                'Message',
                'Project ID',
                'User ID',
            )

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowServerEvent(command.ShowOne):
    """Show server event details.

    Specify ``--os-compute-api-version 2.21`` or higher to show event details
    for a deleted server, specified by ID only. Specify
    ``--os-compute-api-version 2.51`` or higher to show event details for
    non-admin users.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to show event details (name or ID)'),
        )
        parser.add_argument(
            'request_id',
            metavar='<request-id>',
            help=_('Request ID of the event to show (ID only)'),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        try:
            server_id = compute_client.find_server(
                parsed_args.server,
                ignore_missing=False,
            ).id
        except sdk_exceptions.ResourceNotFound:
            # If we fail to find the resource, it is possible the server is
            # deleted. Try once more using the <server> arg directly if it is a
            # UUID.
            if is_uuid_like(parsed_args.server):
                server_id = parsed_args.server
            else:
                raise

        server_action = compute_client.get_server_action(
            parsed_args.request_id,
            server_id,
        )

        column_headers, columns = _get_server_event_columns(
            server_action,
            compute_client,
        )

        return (
            column_headers,
            utils.get_item_properties(
                server_action,
                columns,
                formatters={'events': ServerActionEventColumn},
            ),
        )
