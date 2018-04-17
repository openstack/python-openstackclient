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

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class ListExtension(command.Lister):
    _description = _("List API extensions")

    def get_parser(self, prog_name):
        parser = super(ListExtension, self).get_parser(prog_name)
        parser.add_argument(
            '--compute',
            action='store_true',
            default=False,
            help=_('List extensions for the Compute API'),
        )
        parser.add_argument(
            '--identity',
            action='store_true',
            default=False,
            help=_('List extensions for the Identity API'),
        )
        parser.add_argument(
            '--network',
            action='store_true',
            default=False,
            help=_('List extensions for the Network API'),
        )
        parser.add_argument(
            '--volume',
            action='store_true',
            default=False,
            help=_('List extensions for the Block Storage API'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ('Name', 'Alias', 'Description',
                       'Namespace', 'Updated', 'Links')
        else:
            columns = ('Name', 'Alias', 'Description')

        data = []

        # by default we want to show everything, unless the
        # user specifies one or more of the APIs to show
        # for now, only identity and compute are supported.
        show_all = (not parsed_args.identity and
                    not parsed_args.compute and
                    not parsed_args.volume and
                    not parsed_args.network)

        if parsed_args.identity or show_all:
            identity_client = self.app.client_manager.identity
            try:
                data += identity_client.extensions.list()
            except Exception:
                message = _("Extensions list not supported by Identity API")
                LOG.warning(message)

        if parsed_args.compute or show_all:
            compute_client = self.app.client_manager.compute
            try:
                data += compute_client.list_extensions.show_all()
            except Exception:
                message = _("Extensions list not supported by Compute API")
                LOG.warning(message)

        if parsed_args.volume or show_all:
            volume_client = self.app.client_manager.volume
            try:
                data += volume_client.list_extensions.show_all()
            except Exception:
                message = _("Extensions list not supported by "
                            "Block Storage API")
                LOG.warning(message)

        if parsed_args.network or show_all:
            network_client = self.app.client_manager.network
            try:
                data += network_client.extensions()
            except Exception:
                message = _("Failed to retrieve extensions list "
                            "from Network API")
                LOG.warning(message)

        extension_tuples = (
            utils.get_item_properties(
                s,
                columns,
            ) for s in data
        )

        return (columns, extension_tuples)


class ShowExtension(command.ShowOne):
    _description = _("Show API extension")

    def get_parser(self, prog_name):
        parser = super(ShowExtension, self).get_parser(prog_name)
        parser.add_argument(
            'extension',
            metavar='<extension>',
            help=_('Extension to display. '
                   'Currently, only network extensions are supported. '
                   '(Name or Alias)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        ext = str(parsed_args.extension)
        obj = client.find_extension(ext, ignore_missing=False).to_dict()

        return zip(*sorted(obj.items()))
