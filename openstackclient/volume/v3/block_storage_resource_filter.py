# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Volume V3 Resource Filters implementations"""

from cinderclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


class ListBlockStorageResourceFilter(command.Lister):
    _description = _('List block storage resource filters')

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.33'):
            msg = _(
                "--os-volume-api-version 3.33 or greater is required to "
                "support the 'block storage resource filter list' command"
            )
            raise exceptions.CommandError(msg)

        column_headers = (
            'Resource',
            'Filters',
        )

        data = volume_client.resource_filters.list()

        return (
            column_headers,
            (utils.get_item_properties(s, column_headers) for s in data),
        )


class ShowBlockStorageResourceFilter(command.ShowOne):
    _description = _('Show filters for a block storage resource type')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource',
            metavar='<resource>',
            help=_('Resource to show filters for (name).'),
        )

        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.33'):
            msg = _(
                "--os-volume-api-version 3.33 or greater is required to "
                "support the 'block storage resource filter show' command"
            )
            raise exceptions.CommandError(msg)

        data = volume_client.resource_filters.list(
            resource=parsed_args.resource
        )
        if not data:
            msg = _(
                "No resource filter with a name of {parsed_args.resource}' "
                "exists."
            )
            raise exceptions.CommandError(msg)
        resource_filter = next(data)

        return zip(*sorted(resource_filter._info.items()))
