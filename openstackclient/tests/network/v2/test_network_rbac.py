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

from openstackclient.network.v2 import network_rbac
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestNetworkRBAC(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkRBAC, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestListNetworkRABC(TestNetworkRBAC):

    # The network rbac policies going to be listed up.
    rbac_policies = network_fakes.FakeNetworkRBAC.create_network_rbacs(count=3)

    columns = (
        'ID',
        'Object Type',
        'Object ID',
    )

    data = []
    for r in rbac_policies:
        data.append((
            r.id,
            r.object_type,
            r.object_id,
        ))

    def setUp(self):
        super(TestListNetworkRABC, self).setUp()

        # Get the command object to test
        self.cmd = network_rbac.ListNetworkRBAC(self.app, self.namespace)

        self.network.rbac_policies = mock.Mock(return_value=self.rbac_policies)

    def test_network_rbac_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.rbac_policies.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowNetworkRBAC(TestNetworkRBAC):

    rbac_policy = network_fakes.FakeNetworkRBAC.create_one_network_rbac()

    columns = (
        'action',
        'id',
        'object_id',
        'object_type',
        'project_id',
        'target_project',
    )

    data = [
        rbac_policy.action,
        rbac_policy.id,
        rbac_policy.object_id,
        rbac_policy.object_type,
        rbac_policy.tenant_id,
        rbac_policy.target_tenant,
    ]

    def setUp(self):
        super(TestShowNetworkRBAC, self).setUp()

        # Get the command object to test
        self.cmd = network_rbac.ShowNetworkRBAC(self.app, self.namespace)

        self.network.find_rbac_policy = mock.Mock(
            return_value=self.rbac_policy)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_rbac_show_all_options(self):
        arglist = [
            self.rbac_policy.object_id,
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_rbac_policy.assert_called_with(
            self.rbac_policy.object_id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
