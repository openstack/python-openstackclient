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

"""Router action implementations"""

import json
import logging

from cliff import lister

from openstackclient.common import utils


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


def _format_external_gateway_info(info):
    try:
        return json.dumps(info)
    except (TypeError, KeyError):
        return ''


_formatters = {
    'admin_state_up': _format_admin_state,
    'external_gateway_info': _format_external_gateway_info,
}


class ListRouter(lister.Lister):
    """List routers"""

    log = logging.getLogger(__name__ + '.ListRouter')

    def get_parser(self, prog_name):
        parser = super(ListRouter, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'status',
            'admin_state_up',
            'distributed',
            'ha',
            'tenant_id',
        )
        column_headers = (
            'ID',
            'Name',
            'Status',
            'State',
            'Distributed',
            'HA',
            'Project',
        )
        if parsed_args.long:
            columns = columns + (
                'routes',
                'external_gateway_info',
            )
            column_headers = column_headers + (
                'Routes',
                'External gateway info',
            )

        data = client.routers()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))
