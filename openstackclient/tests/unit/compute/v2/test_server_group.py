#   Copyright 2016 Huawei, Inc. All rights reserved.
#
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

from novaclient import api_versions
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.compute.v2 import server_group
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestServerGroup(compute_fakes.TestComputev2):

    fake_server_group = compute_fakes.FakeServerGroup.create_one_server_group()

    columns = (
        'id',
        'members',
        'name',
        'policies',
        'project_id',
        'user_id',
    )

    data = (
        fake_server_group.id,
        format_columns.ListColumn(fake_server_group.members),
        fake_server_group.name,
        format_columns.ListColumn(fake_server_group.policies),
        fake_server_group.project_id,
        fake_server_group.user_id,
    )

    def setUp(self):
        super(TestServerGroup, self).setUp()

        # Get a shortcut to the ServerGroupsManager Mock
        self.server_groups_mock = self.app.client_manager.compute.server_groups
        self.server_groups_mock.reset_mock()


class TestServerGroupV264(TestServerGroup):

    fake_server_group = \
        compute_fakes.FakeServerGroupV264.create_one_server_group()

    columns = (
        'id',
        'members',
        'name',
        'policy',
        'project_id',
        'user_id',
    )

    data = (
        fake_server_group.id,
        format_columns.ListColumn(fake_server_group.members),
        fake_server_group.name,
        fake_server_group.policy,
        fake_server_group.project_id,
        fake_server_group.user_id,
    )

    def setUp(self):
        super(TestServerGroupV264, self).setUp()


class TestServerGroupCreate(TestServerGroup):

    def setUp(self):
        super(TestServerGroupCreate, self).setUp()

        self.server_groups_mock.create.return_value = self.fake_server_group
        self.cmd = server_group.CreateServerGroup(self.app, None)

    def test_server_group_create(self):
        arglist = [
            '--policy', 'anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.create.assert_called_once_with(
            name=parsed_args.name,
            policies=[parsed_args.policy],
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_server_group_create_with_soft_policies(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.15')

        arglist = [
            '--policy', 'soft-anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.create.assert_called_once_with(
            name=parsed_args.name,
            policies=[parsed_args.policy],
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_server_group_create_with_soft_policies_pre_v215(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.14')

        arglist = [
            '--policy', 'soft-anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.15 or greater is required',
            str(ex))

    def test_server_group_create_with_rules(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.64')

        arglist = [
            '--policy', 'soft-anti-affinity',
            '--rule', 'max_server_per_host=2',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('rules', {'max_server_per_host': '2'}),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.create.assert_called_once_with(
            name=parsed_args.name,
            policy=parsed_args.policy,  # should be 'policy', not 'policies'
            rules=parsed_args.rules,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_server_group_create_with_rules_pre_v264(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.63')

        arglist = [
            '--policy', 'soft-anti-affinity',
            '--rule', 'max_server_per_host=2',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('rules', {'max_server_per_host': '2'}),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.64 or greater is required',
            str(ex))


class TestServerGroupDelete(TestServerGroup):

    def setUp(self):
        super(TestServerGroupDelete, self).setUp()

        self.server_groups_mock.get.return_value = self.fake_server_group
        self.cmd = server_group.DeleteServerGroup(self.app, None)

    def test_server_group_delete(self):
        arglist = [
            'affinity_group',
        ]
        verifylist = [
            ('server_group', ['affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.server_groups_mock.get.assert_called_once_with('affinity_group')
        self.server_groups_mock.delete.assert_called_once_with(
            self.fake_server_group.id
        )
        self.assertIsNone(result)

    def test_server_group_multiple_delete(self):
        arglist = [
            'affinity_group',
            'anti_affinity_group'
        ]
        verifylist = [
            ('server_group', ['affinity_group', 'anti_affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.server_groups_mock.get.assert_any_call('affinity_group')
        self.server_groups_mock.get.assert_any_call('anti_affinity_group')
        self.server_groups_mock.delete.assert_called_with(
            self.fake_server_group.id
        )
        self.assertEqual(2, self.server_groups_mock.get.call_count)
        self.assertEqual(2, self.server_groups_mock.delete.call_count)
        self.assertIsNone(result)

    def test_server_group_delete_no_input(self):
        arglist = []
        verifylist = None
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)

    def test_server_group_multiple_delete_with_exception(self):
        arglist = [
            'affinity_group',
            'anti_affinity_group'
        ]
        verifylist = [
            ('server_group', ['affinity_group', 'anti_affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        find_mock_result = [self.fake_server_group, exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 server groups failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.server_groups_mock,
                                      'affinity_group')
            find_mock.assert_any_call(self.server_groups_mock,
                                      'anti_affinity_group')

            self.assertEqual(2, find_mock.call_count)
            self.server_groups_mock.delete.assert_called_once_with(
                self.fake_server_group.id
            )


class TestServerGroupList(TestServerGroup):

    list_columns = (
        'ID',
        'Name',
        'Policies',
    )

    list_columns_long = (
        'ID',
        'Name',
        'Policies',
        'Members',
        'Project Id',
        'User Id',
    )

    list_data = ((
        TestServerGroup.fake_server_group.id,
        TestServerGroup.fake_server_group.name,
        format_columns.ListColumn(TestServerGroup.fake_server_group.policies),
    ),)

    list_data_long = ((
        TestServerGroup.fake_server_group.id,
        TestServerGroup.fake_server_group.name,
        format_columns.ListColumn(TestServerGroup.fake_server_group.policies),
        format_columns.ListColumn(TestServerGroup.fake_server_group.members),
        TestServerGroup.fake_server_group.project_id,
        TestServerGroup.fake_server_group.user_id,
    ),)

    def setUp(self):
        super(TestServerGroupList, self).setUp()

        self.server_groups_mock.list.return_value = [self.fake_server_group]
        self.cmd = server_group.ListServerGroup(self.app, None)

    def test_server_group_list(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('limit', None),
            ('offset', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.server_groups_mock.list.assert_called_once_with()

        self.assertCountEqual(self.list_columns, columns)
        self.assertCountEqual(self.list_data, tuple(data))

    def test_server_group_list_with_all_projects_and_long(self):
        arglist = [
            '--all-projects',
            '--long',
        ]
        verifylist = [
            ('all_projects', True),
            ('long', True),
            ('limit', None),
            ('offset', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.list.assert_called_once_with(
            all_projects=True)

        self.assertCountEqual(self.list_columns_long, columns)
        self.assertCountEqual(self.list_data_long, tuple(data))

    def test_server_group_list_with_limit(self):
        arglist = [
            '--limit', '1',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('limit', 1),
            ('offset', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.server_groups_mock.list.assert_called_once_with(limit=1)

    def test_server_group_list_with_offset(self):
        arglist = [
            '--offset', '5',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('limit', None),
            ('offset', 5),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.server_groups_mock.list.assert_called_once_with(offset=5)


class TestServerGroupListV264(TestServerGroupV264):

    list_columns = (
        'ID',
        'Name',
        'Policy',
    )

    list_columns_long = (
        'ID',
        'Name',
        'Policy',
        'Members',
        'Project Id',
        'User Id',
    )

    list_data = ((
        TestServerGroupV264.fake_server_group.id,
        TestServerGroupV264.fake_server_group.name,
        TestServerGroupV264.fake_server_group.policy,
    ),)

    list_data_long = ((
        TestServerGroupV264.fake_server_group.id,
        TestServerGroupV264.fake_server_group.name,
        TestServerGroupV264.fake_server_group.policy,
        format_columns.ListColumn(
            TestServerGroupV264.fake_server_group.members),
        TestServerGroupV264.fake_server_group.project_id,
        TestServerGroupV264.fake_server_group.user_id,
    ),)

    def setUp(self):
        super(TestServerGroupListV264, self).setUp()

        self.server_groups_mock.list.return_value = [self.fake_server_group]
        self.cmd = server_group.ListServerGroup(self.app, None)
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.64')

    def test_server_group_list(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.list.assert_called_once_with()

        self.assertCountEqual(self.list_columns, columns)
        self.assertCountEqual(self.list_data, tuple(data))

    def test_server_group_list_with_all_projects_and_long(self):
        arglist = [
            '--all-projects',
            '--long',
        ]
        verifylist = [
            ('all_projects', True),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.list.assert_called_once_with(
            all_projects=True)

        self.assertCountEqual(self.list_columns_long, columns)
        self.assertCountEqual(self.list_data_long, tuple(data))


class TestServerGroupShow(TestServerGroup):

    def setUp(self):
        super(TestServerGroupShow, self).setUp()

        self.server_groups_mock.get.return_value = self.fake_server_group
        self.cmd = server_group.ShowServerGroup(self.app, None)

    def test_server_group_show(self):
        arglist = [
            'affinity_group',
        ]
        verifylist = [
            ('server_group', 'affinity_group'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
