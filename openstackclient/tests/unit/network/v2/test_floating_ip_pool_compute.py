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

from unittest import mock

from openstackclient.api import compute_v2
from openstackclient.network.v2 import floating_ip_pool
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


@mock.patch.object(compute_v2, 'list_floating_ip_pools')
class TestListFloatingIPPoolCompute(compute_fakes.TestComputev2):
    # The floating ip pools to list up
    _floating_ip_pools = compute_fakes.create_floating_ip_pools(count=3)

    columns = ('Name',)

    data = []
    for pool in _floating_ip_pools:
        data.append((pool['name'],))

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = floating_ip_pool.ListFloatingIPPool(self.app, None)

    def test_floating_ip_list(self, fipp_mock):
        fipp_mock.return_value = self._floating_ip_pools
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        fipp_mock.assert_called_once_with(self.compute_client)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
