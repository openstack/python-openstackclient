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

from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class ListServerEvent(command.Lister):
    _description = _(
        "List recent events of a server. "
        "Specify ``--os-compute-api-version 2.21`` "
        "or higher to show events for a deleted server.")

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
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        server_id = utils.find_resource(compute_client.servers,
                                        parsed_args.server).id
        data = compute_client.instance_action.list(server_id)

        if parsed_args.long:
            columns = (
                'request_id',
                'instance_uuid',
                'action',
                'start_time',
                'message',
                'project_id',
                'user_id',
            )
            column_headers = (
                'Request ID',
                'Server ID',
                'Action',
                'Start Time',
                'Message',
                'Project ID',
                'User ID',
            )
        else:
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

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowServerEvent(command.ShowOne):
    _description = _(
        "Show server event details. "
        "Specify ``--os-compute-api-version 2.21`` "
        "or higher to show event details for a deleted server. "
        "Specify ``--os-compute-api-version 2.51`` "
        "or higher to show event details for non-admin users.")

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
        server_id = utils.find_resource(compute_client.servers,
                                        parsed_args.server).id
        action_detail = compute_client.instance_action.get(
            server_id, parsed_args.request_id)

        return zip(*sorted(six.iteritems(action_detail.to_dict())))
