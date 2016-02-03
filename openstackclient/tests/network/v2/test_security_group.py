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

from openstackclient.network.v2 import security_group
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestSecurityGroup(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroup, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network

        # Create compute client mocks.
        self.app.client_manager.compute = mock.Mock()
        self.compute = self.app.client_manager.compute
        self.compute.security_groups = mock.Mock()


class TestDeleteSecurityGroupNetwork(TestSecurityGroup):

    # The security group to be deleted.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestDeleteSecurityGroupNetwork, self).setUp()

        self.network.delete_security_group = mock.Mock(return_value=None)

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, self.namespace)

    def test_security_group_delete(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_security_group.assert_called_with(
            self._security_group)
        self.assertEqual(None, result)


class TestDeleteSecurityGroupCompute(TestSecurityGroup):

    # The security group to be deleted.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestDeleteSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.delete = mock.Mock(return_value=None)

        self.compute.security_groups.get = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, self.namespace)

    def test_security_group_delete(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.delete.assert_called_with(
            self._security_group.id)
        self.assertEqual(None, result)
