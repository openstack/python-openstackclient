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

import iso8601
from novaclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class ListServerEvent(command.Lister):
    """List recent events of a server.

    Specify ``--os-compute-api-version 2.21`` or higher to show events for a
    deleted server.
    """

    def get_parser(self, prog_name):
        parser = super(ListServerEvent, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to list events (name or ID)'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
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
        parser.add_argument(
            '--marker',
            help=_(
                'The last server event ID of the previous page '
                '(supported by --os-compute-api-version 2.58 or above)'
            ),
        )
        parser.add_argument(
            '--limit',
            type=int,
            help=_(
                'Maximum number of server events to display '
                '(supported by --os-compute-api-version 2.58 or above)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        kwargs = {}

        if parsed_args.marker:
            if compute_client.api_version < api_versions.APIVersion('2.58'):
                msg = _(
                    '--os-compute-api-version 2.58 or greater is required to '
                    'support the --marker option'
                )
                raise exceptions.CommandError(msg)
            kwargs['marker'] = parsed_args.marker

        if parsed_args.limit:
            if compute_client.api_version < api_versions.APIVersion('2.58'):
                msg = _(
                    '--os-compute-api-version 2.58 or greater is required to '
                    'support the --limit option'
                )
                raise exceptions.CommandError(msg)
            kwargs['limit'] = parsed_args.limit

        if parsed_args.changes_since:
            if compute_client.api_version < api_versions.APIVersion('2.58'):
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
            if compute_client.api_version < api_versions.APIVersion('2.66'):
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

        server_id = utils.find_resource(
            compute_client.servers, parsed_args.server,
        ).id

        data = compute_client.instance_action.list(server_id, **kwargs)

        columns = (
            'request_id',
            'instance_uuid',
            'action',
            'start_time',
        )
        column_headers = (
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
    for a deleted server. Specify ``--os-compute-api-version 2.51`` or higher
    to show event details for non-admin users.
    """

    def get_parser(self, prog_name):
        parser = super(ShowServerEvent, self).get_parser(prog_name)
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

        server_id = utils.find_resource(
            compute_client.servers, parsed_args.server,
        ).id

        action_detail = compute_client.instance_action.get(
            server_id, parsed_args.request_id
        )

        return zip(*sorted(action_detail.to_dict().items()))
