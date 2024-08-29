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

"""Service action implementations"""

from cinderclient import api_versions
from osc_lib import utils

from openstackclient.volume.v2 import service as service_v2


class ListService(service_v2.ListService):
    def take_action(self, parsed_args):
        service_client = self.app.client_manager.volume

        columns = [
            "Binary",
            "Host",
            "Zone",
            "Status",
            "State",
            "Updated At",
        ]

        if service_client.api_version >= api_versions.APIVersion('3.7'):
            columns.append("Cluster")
        if service_client.api_version >= api_versions.APIVersion('3.49'):
            columns.append("Backend State")
        if parsed_args.long:
            columns.append("Disabled Reason")

        data = service_client.services.list(
            parsed_args.host, parsed_args.service
        )
        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )
