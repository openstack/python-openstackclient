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

from osc_lib import exceptions

from openstackclient.api import compute_v2
from openstackclient.network.v2 import security_group
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils


@mock.patch.object(compute_v2, 'create_security_group')
class TestCreateSecurityGroupCompute(compute_fakes.TestComputev2):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    # The security group to be shown.
    _security_group = compute_fakes.create_one_security_group()

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
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, None)

    def test_security_group_create_no_options(self, sg_mock):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

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
            self.compute_client,
            self._security_group['name'],
            self._security_group['name'],
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_security_group_create_all_options(self, sg_mock):
        sg_mock.return_value = self._security_group
        arglist = [
            '--description',
            self._security_group['description'],
            self._security_group['name'],
        ]
        verifylist = [
            ('description', self._security_group['description']),
            ('name', self._security_group['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sg_mock.assert_called_once_with(
            self.compute_client,
            self._security_group['name'],
            self._security_group['description'],
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


@mock.patch.object(compute_v2, 'delete_security_group')
class TestDeleteSecurityGroupCompute(compute_fakes.TestComputev2):
    # The security groups to be deleted.
    _security_groups = compute_fakes.create_security_groups()

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        compute_v2.find_security_group = mock.Mock(
            side_effect=self._security_groups
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
            self.compute_client,
            self._security_groups[0]['id'],
        )
        self.assertIsNone(result)

    def test_security_group_multi_delete(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._security_groups[0]['id'],
            self._security_groups[1]['id'],
        ]
        verifylist = [
            ('group', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        sg_mock.assert_has_calls(
            [
                mock.call(self.compute_client, self._security_groups[0]['id']),
                mock.call(self.compute_client, self._security_groups[1]['id']),
            ]
        )
        self.assertIsNone(result)

    def test_security_group_multi_delete_with_exception(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        compute_v2.find_security_group.side_effect = [
            self._security_groups[0],
            exceptions.NotFound('foo'),
        ]
        arglist = [
            self._security_groups[0]['id'],
            'unexist_security_group',
        ]
        verifylist = [
            ('group', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertEqual('1 of 2 groups failed to delete.', str(exc))

        sg_mock.assert_has_calls(
            [
                mock.call(self.compute_client, self._security_groups[0]['id']),
            ]
        )


@mock.patch.object(compute_v2, 'list_security_groups')
class TestListSecurityGroupCompute(compute_fakes.TestComputev2):
    # The security group to be listed.
    _security_groups = compute_fakes.create_security_groups(count=3)

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
        data.append(
            (
                grp['id'],
                grp['name'],
                grp['description'],
            )
        )
    data_all_projects = []
    for grp in _security_groups:
        data_all_projects.append(
            (
                grp['id'],
                grp['name'],
                grp['description'],
                grp['tenant_id'],
            )
        )

    def setUp(self):
        super().setUp()

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

        sg_mock.assert_called_once_with(
            self.compute_client, all_projects=False
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        sg_mock.assert_called_once_with(self.compute_client, all_projects=True)
        self.assertEqual(self.columns_all_projects, columns)
        self.assertCountEqual(self.data_all_projects, list(data))


@mock.patch.object(compute_v2, 'update_security_group')
class TestSetSecurityGroupCompute(compute_fakes.TestComputev2):
    # The security group to be set.
    _security_group = compute_fakes.create_one_security_group()

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        compute_v2.find_security_group = mock.Mock(
            return_value=self._security_group
        )

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, None)

    def test_security_group_set_no_options(self, sg_mock):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

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
            self.compute_client, self._security_group['id']
        )
        self.assertIsNone(result)

    def test_security_group_set_all_options(self, sg_mock):
        sg_mock.return_value = mock.Mock(return_value=None)
        new_name = 'new-' + self._security_group['name']
        new_description = 'new-' + self._security_group['description']
        arglist = [
            '--name',
            new_name,
            '--description',
            new_description,
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
            self.compute_client,
            self._security_group['id'],
            name=new_name,
            description=new_description,
        )
        self.assertIsNone(result)


@mock.patch.object(compute_v2, 'find_security_group')
class TestShowSecurityGroupCompute(compute_fakes.TestComputev2):
    # The security group rule to be shown with the group.
    _security_group_rule = compute_fakes.create_one_security_group_rule()

    # The security group to be shown.
    _security_group = compute_fakes.create_one_security_group(
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
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, None)

    def test_security_group_show_no_options(self, sg_mock):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

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

        sg_mock.assert_called_once_with(
            self.compute_client, self._security_group['id']
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
