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
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestSecurityGroupNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroupNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestSecurityGroupCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestDeleteSecurityGroupNetwork(TestSecurityGroupNetwork):

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
        self.assertIsNone(result)


class TestDeleteSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be deleted.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestDeleteSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.delete = mock.Mock(return_value=None)

        self.compute.security_groups.get = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, None)

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
        self.assertIsNone(result)


class TestListSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be listed.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    expected_columns = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    expected_data = ((
        _security_group.id,
        _security_group.name,
        _security_group.description,
        _security_group.tenant_id,
    ),)

    def setUp(self):
        super(TestListSecurityGroupNetwork, self).setUp()

        self.network.security_groups = mock.Mock(
            return_value=[self._security_group])

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, self.namespace)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_groups.assert_called_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, tuple(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_groups.assert_called_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, tuple(data))


class TestListSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be listed.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    expected_columns = (
        'ID',
        'Name',
        'Description',
    )
    expected_columns_all_projects = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    expected_data = ((
        _security_group.id,
        _security_group.name,
        _security_group.description,
    ),)
    expected_data_all_projects = ((
        _security_group.id,
        _security_group.name,
        _security_group.description,
        _security_group.tenant_id,
    ),)

    def setUp(self):
        super(TestListSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False
        self.compute.security_groups.list.return_value = [self._security_group]

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, None)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': False}}
        self.compute.security_groups.list.assert_called_with(**kwargs)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, tuple(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': True}}
        self.compute.security_groups.list.assert_called_with(**kwargs)
        self.assertEqual(self.expected_columns_all_projects, columns)
        self.assertEqual(self.expected_data_all_projects, tuple(data))
