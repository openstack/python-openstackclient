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

import mock

from openstackclient.network.v2 import floating_ip_pool
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


# Tests for Compute network

class TestFloatingIPPoolCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFloatingIPPoolCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.floating_ip_pool_list'
)
class TestListFloatingIPPoolCompute(TestFloatingIPPoolCompute):

    # The floating ip pools to list up
    _floating_ip_pools = \
        compute_fakes.FakeFloatingIPPool.create_floating_ip_pools(count=3)

    columns = (
        'Name',
    )

    data = []
    for pool in _floating_ip_pools:
        data.append((
            pool['name'],
        ))

    def setUp(self):
        super(TestListFloatingIPPoolCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = floating_ip_pool.ListFloatingIPPool(self.app, None)

    def test_floating_ip_list(self, fipp_mock):
        fipp_mock.return_value = self._floating_ip_pools
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        fipp_mock.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
