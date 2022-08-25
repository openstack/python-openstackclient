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

"""Image V2 Action Implementations"""

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _

_formatters = {
    'tags': format_columns.ListColumn,
}


class ListMetadefNameSpaces(command.Lister):
    _description = _("List metadef namespaces")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--resource-types",
            metavar="<resource_types>",
            help=_("filter resource types"),
        )
        parser.add_argument(
            "--visibility",
            metavar="<visibility>",
            help=_("filter on visibility"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        filter_keys = ['resource_types', 'visibility']
        kwargs = {}
        for key in filter_keys:
            argument = getattr(parsed_args, key, None)
            if argument is not None:
                kwargs[key] = argument
        # List of namespace data received
        data = list(image_client.metadef_namespaces(**kwargs))
        columns = ['namespace']
        column_headers = columns
        return (
            column_headers,
            (utils.get_item_properties(
                s,
                columns,
                formatters=_formatters,
            ) for s in data)
        )
