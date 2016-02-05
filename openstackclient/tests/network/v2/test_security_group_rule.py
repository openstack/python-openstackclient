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

from openstackclient.network.v2 import security_group_rule
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestSecurityGroupRuleNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroupRuleNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestSecurityGroupRuleCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupRuleCompute, self).setUp()

        # Get a shortcut to the network client
        self.compute = self.app.client_manager.compute


class TestDeleteSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group rule to be deleted.
    _security_group_rule = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    def setUp(self):
        super(TestDeleteSecurityGroupRuleNetwork, self).setUp()

        self.network.delete_security_group_rule = mock.Mock(return_value=None)

        self.network.find_security_group_rule = mock.Mock(
            return_value=self._security_group_rule)

        # Get the command object to test
        self.cmd = security_group_rule.DeleteSecurityGroupRule(
            self.app, self.namespace)

    def test_security_group_rule_delete(self):
        arglist = [
            self._security_group_rule.id,
        ]
        verifylist = [
            ('rule', self._security_group_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_security_group_rule.assert_called_with(
            self._security_group_rule)
        self.assertEqual(None, result)


class TestDeleteSecurityGroupRuleCompute(TestSecurityGroupRuleCompute):

    # The security group rule to be deleted.
    _security_group_rule = \
        compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    def setUp(self):
        super(TestDeleteSecurityGroupRuleCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group_rule.DeleteSecurityGroupRule(self.app, None)

    def test_security_group_rule_delete(self):
        arglist = [
            self._security_group_rule.id,
        ]
        verifylist = [
            ('rule', self._security_group_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.security_group_rules.delete.assert_called_with(
            self._security_group_rule.id)
        self.assertEqual(None, result)
