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

from osc_lib import exceptions

from openstackclient.network.v2 import floating_ip_pool
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestFloatingIPPoolNetwork(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()


class TestListFloatingIPPoolNetwork(TestFloatingIPPoolNetwork):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = floating_ip_pool.ListFloatingIPPool(self.app, None)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
