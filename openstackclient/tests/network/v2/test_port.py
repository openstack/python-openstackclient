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

from openstackclient.network.v2 import port
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestPort(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestPort, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestDeletePort(TestPort):

    # The port to delete.
    _port = network_fakes.FakePort.create_one_port()

    def setUp(self):
        super(TestDeletePort, self).setUp()

        self.network.delete_port = mock.Mock(return_value=None)
        self.network.find_port = mock.Mock(return_value=self._port)
        # Get the command object to test
        self.cmd = port.DeletePort(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', [self._port.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_port.assert_called_with(self._port)
        self.assertIsNone(result)
