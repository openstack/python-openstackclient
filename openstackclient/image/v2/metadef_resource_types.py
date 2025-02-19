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

"""Image V2 Action Implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListMetadefResourceTypes(command.Lister):
    _description = _("List metadef resource types")

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        data = image_client.metadef_resource_types()
        columns = ['Name']
        column_headers = columns
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )
