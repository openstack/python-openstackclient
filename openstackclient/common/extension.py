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

import itertools
import logging

from cliff import lister

from openstackclient.common import utils


class ListExtension(lister.Lister):
    """List API extensions"""

    log = logging.getLogger(__name__ + '.ListExtension')

    def get_parser(self, prog_name):
        parser = super(ListExtension, self).get_parser(prog_name)
        parser.add_argument(
            '--compute',
            action='store_true',
            default=False,
            help='List extensions for the Compute API')
        parser.add_argument(
            '--identity',
            action='store_true',
            default=False,
            help='List extensions for the Identity API')
        parser.add_argument(
            '--network',
            action='store_true',
            default=False,
            help='List extensions for the Network API')
        parser.add_argument(
            '--volume',
            action='store_true',
            default=False,
            help='List extensions for the Volume API')
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
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
        # for now, only identity and compute are supported.
        show_all = (not parsed_args.identity and not parsed_args.compute
                    and not parsed_args.volume and not parsed_args.network)

        if parsed_args.identity or show_all:
            identity_client = self.app.client_manager.identity
            try:
                data += identity_client.extensions.list()
            except Exception:
                message = "Extensions list not supported by Identity API"
                self.log.warning(message)

        if parsed_args.compute or show_all:
            compute_client = self.app.client_manager.compute
            try:
                data += compute_client.list_extensions.show_all()
            except Exception:
                message = "Extensions list not supported by Compute API"
                self.log.warning(message)

        if parsed_args.volume or show_all:
            volume_client = self.app.client_manager.volume
            try:
                data += volume_client.list_extensions.show_all()
            except Exception:
                message = "Extensions list not supported by Volume API"
                self.log.warning(message)

        # Resource classes for the above
        extension_tuples = (
            utils.get_item_properties(
                s,
                columns,
                formatters={},
            ) for s in data
        )

        # Dictionaries for the below
        if parsed_args.network or show_all:
            network_client = self.app.client_manager.network
            try:
                data = network_client.list_extensions()['extensions']
                dict_tuples = (
                    utils.get_dict_properties(
                        s,
                        columns,
                        formatters={},
                    ) for s in data
                )
                extension_tuples = itertools.chain(
                    extension_tuples,
                    dict_tuples
                )
            except Exception:
                message = "Extensions list not supported by Network API"
                self.log.warning(message)

        return (columns, extension_tuples)
