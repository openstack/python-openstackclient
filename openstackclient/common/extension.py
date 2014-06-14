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

"""Extension action implementations"""

import logging

from cliff import lister

from openstackclient.common import exceptions as exc
from openstackclient.common import utils


class ListExtension(lister.Lister):
    """List extension command"""

    # TODO(mfisch): add support for volume and compute
    # when the underlying APIs support it. Add support
    # for network when it's added to openstackclient.

    log = logging.getLogger(__name__ + '.ListExtension')

    def get_parser(self, prog_name):
        parser = super(ListExtension, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
        parser.add_argument(
            '--identity',
            action='store_true',
            default=False,
            help='List extensions for the Identity API')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        if parsed_args.long:
            columns = ('Name', 'Namespace', 'Description',
                       'Alias', 'Updated', 'Links')
        else:
            columns = ('Name', 'Alias', 'Description')

        data = []

        # by default we want to show everything, unless the
        # user specifies one or more of the APIs to show
        # for now, only identity is supported
        show_all = (not parsed_args.identity)

        if parsed_args.identity or show_all:
            identity_client = self.app.client_manager.identity
            try:
                data += identity_client.extensions.list()
            except Exception:
                raise exc.CommandError(
                    "Extensions list not supported by"
                    " identity API")

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))
