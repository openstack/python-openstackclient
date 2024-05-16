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

"""Floating IP Pool action implementations"""

from osc_lib import exceptions

from openstackclient.api import compute_v2
from openstackclient.i18n import _
from openstackclient.network import common


class ListFloatingIPPool(common.NetworkAndComputeLister):
    _description = _("List pools of floating IP addresses")

    def take_action_network(self, client, parsed_args):
        msg = _(
            "Floating ip pool operations are only available for "
            "Compute v2 network."
        )
        raise exceptions.CommandError(msg)

    def take_action_compute(self, client, parsed_args):
        columns = ('Name',)
        data = [
            (x['name'],) for x in compute_v2.list_floating_ip_pools(client)
        ]

        return (columns, data)
