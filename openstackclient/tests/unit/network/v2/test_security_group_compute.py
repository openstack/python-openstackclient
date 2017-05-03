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
from mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import security_group
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestSecurityGroupCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_create'
)
class TestCreateSecurityGroupCompute(TestSecurityGroupCompute):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    # The security group to be shown.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group['description'],
        _security_group['id'],
        _security_group['name'],
        _security_group['tenant_id'],
        security_group.ComputeSecurityGroupRulesColumn([]),
    )

    def setUp(self):
        super(TestCreateSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, None)

    def test_security_group_create_no_options(self, sg_mock):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_security_group_create_min_options(self, sg_mock):
        sg_mock.return_value = self._security_group
        arglist = [
            self._security_group['name'],
        ]
        verifylist = [
            ('name', self._security_group['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(
            self._security_group['name'],
            self._security_group['name'],
        )
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_security_group_create_all_options(self, sg_mock):
        sg_mock.return_value = self._security_group
        arglist = [
            '--description', self._security_group['description'],
            self._security_group['name'],
        ]
        verifylist = [
            ('description', self._security_group['description']),
            ('name', self._security_group['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(
            self._security_group['name'],
            self._security_group['description'],
        )
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_delete'
)
class TestDeleteSecurityGroupCompute(TestSecurityGroupCompute):

    # The security groups to be deleted.
    _security_groups = \
        compute_fakes.FakeSecurityGroup.create_security_groups()

    def setUp(self):
        super(TestDeleteSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.api.security_group_find = (
            compute_fakes.FakeSecurityGroup.get_security_groups(
                self._security_groups)
        )

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, None)

    def test_security_group_delete(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._security_groups[0]['id'],
        ]
        verifylist = [
            ('group', [self._security_groups[0]['id']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(
            self._security_groups[0]['id'],
        )
        self.assertIsNone(result)

    def test_security_group_multi_delete(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        arglist = []
        verifylist = []

        for s in self._security_groups:
            arglist.append(s['id'])
        verifylist = [
            ('group', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self._security_groups:
            calls.append(call(s['id']))
        sg_mock.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_security_group_multi_delete_with_exception(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        sg_mock.side_effect = ([
            mock.Mock(return_value=None),
            exceptions.CommandError,
        ])
        arglist = [
            self._security_groups[0]['id'],
            'unexist_security_group',
        ]
        verifylist = [
            ('group',
             [self._security_groups[0]['id'], 'unexist_security_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 groups failed to delete.', str(e))

        sg_mock.assert_any_call(self._security_groups[0]['id'])
        sg_mock.assert_any_call('unexist_security_group')


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_list'
)
class TestListSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be listed.
    _security_groups = \
        compute_fakes.FakeSecurityGroup.create_security_groups(count=3)

    columns = (
        'ID',
        'Name',
        'Description',
    )
    columns_all_projects = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    data = []
    for grp in _security_groups:
        data.append((
            grp['id'],
            grp['name'],
            grp['description'],
        ))
    data_all_projects = []
    for grp in _security_groups:
        data_all_projects.append((
            grp['id'],
            grp['name'],
            grp['description'],
            grp['tenant_id'],
        ))

    def setUp(self):
        super(TestListSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, None)

    def test_security_group_list_no_options(self, sg_mock):
        sg_mock.return_value = self._security_groups
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': False}}
        sg_mock.assert_called_once_with(**kwargs)
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_security_group_list_all_projects(self, sg_mock):
        sg_mock.return_value = self._security_groups
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': True}}
        sg_mock.assert_called_once_with(**kwargs)
        self.assertEqual(self.columns_all_projects, columns)
        self.assertListItemEqual(self.data_all_projects, list(data))


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_set'
)
class TestSetSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be set.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestSetSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.api.security_group_find = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, None)

    def test_security_group_set_no_options(self, sg_mock):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_security_group_set_no_updates(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._security_group['name'],
        ]
        verifylist = [
            ('group', self._security_group['name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(
            self._security_group,
            self._security_group['name'],
            self._security_group['description'],
        )
        self.assertIsNone(result)

    def test_security_group_set_all_options(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        new_name = 'new-' + self._security_group['name']
        new_description = 'new-' + self._security_group['description']
        arglist = [
            '--name', new_name,
            '--description', new_description,
            self._security_group['name'],
        ]
        verifylist = [
            ('description', new_description),
            ('group', self._security_group['name']),
            ('name', new_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(
            self._security_group,
            new_name,
            new_description
        )
        self.assertIsNone(result)


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_find'
)
class TestShowSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group rule to be shown with the group.
    _security_group_rule = \
        compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    # The security group to be shown.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'rules': [_security_group_rule]}
        )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group['description'],
        _security_group['id'],
        _security_group['name'],
        _security_group['tenant_id'],
        security_group.ComputeSecurityGroupRulesColumn([_security_group_rule]),
    )

    def setUp(self):
        super(TestShowSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, None)

    def test_security_group_show_no_options(self, sg_mock):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_security_group_show_all_options(self, sg_mock):
        sg_mock.return_value = self._security_group
        arglist = [
            self._security_group['id'],
        ]
        verifylist = [
            ('group', self._security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(self._security_group['id'])
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)
