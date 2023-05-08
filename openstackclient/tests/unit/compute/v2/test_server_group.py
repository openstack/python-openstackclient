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

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.compute.v2 import server_group
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestServerGroup(compute_fakes.TestComputev2):
    fake_server_group = compute_fakes.create_one_server_group()

    columns = (
        'id',
        'members',
        'name',
        'policy',
        'project_id',
        'rules',
        'user_id',
    )

    data = (
        fake_server_group.id,
        format_columns.ListColumn(fake_server_group.member_ids),
        fake_server_group.name,
        fake_server_group.policy,
        fake_server_group.project_id,
        format_columns.DictColumn(fake_server_group.rules),
        fake_server_group.user_id,
    )

    def setUp(self):
        super().setUp()

        # Create and get a shortcut to the compute client mock
        self.app.client_manager.sdk_connection = mock.Mock()
        self.sdk_client = self.app.client_manager.sdk_connection.compute
        self.sdk_client.reset_mock()


class TestServerGroupCreate(TestServerGroup):
    def setUp(self):
        super().setUp()

        self.sdk_client.create_server_group.return_value = (
            self.fake_server_group
        )
        self.cmd = server_group.CreateServerGroup(self.app, None)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_create(self, sm_mock):
        arglist = [
            '--policy',
            'anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.sdk_client.create_server_group.assert_called_once_with(
            name=parsed_args.name,
            policy=parsed_args.policy,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_create_with_soft_policies(self, sm_mock):
        arglist = [
            '--policy',
            'soft-anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.sdk_client.create_server_group.assert_called_once_with(
            name=parsed_args.name,
            policy=parsed_args.policy,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_server_group_create_with_soft_policies_pre_v215(self, sm_mock):
        arglist = [
            '--policy',
            'soft-anti-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.15 or greater is required', str(ex)
        )

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_create_with_rules(self, sm_mock):
        arglist = [
            '--policy',
            'soft-anti-affinity',
            '--rule',
            'max_server_per_host=2',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('rules', {'max_server_per_host': '2'}),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.sdk_client.create_server_group.assert_called_once_with(
            name=parsed_args.name,
            policy=parsed_args.policy,
            rules=parsed_args.rules,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch.object(
        sdk_utils, 'supports_microversion', side_effect=[True, False]
    )
    def test_server_group_create_with_rules_pre_v264(self, sm_mock):
        arglist = [
            '--policy',
            'soft-anti-affinity',
            '--rule',
            'max_server_per_host=2',
            'affinity_group',
        ]
        verifylist = [
            ('policy', 'soft-anti-affinity'),
            ('rules', {'max_server_per_host': '2'}),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.64 or greater is required', str(ex)
        )


class TestServerGroupDelete(TestServerGroup):
    def setUp(self):
        super().setUp()

        self.sdk_client.find_server_group.return_value = self.fake_server_group
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
        self.sdk_client.find_server_group.assert_called_once_with(
            'affinity_group'
        )
        self.sdk_client.delete_server_group.assert_called_once_with(
            self.fake_server_group.id
        )
        self.assertIsNone(result)

    def test_server_group_multiple_delete(self):
        arglist = ['affinity_group', 'anti_affinity_group']
        verifylist = [
            ('server_group', ['affinity_group', 'anti_affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.sdk_client.find_server_group.assert_any_call('affinity_group')
        self.sdk_client.find_server_group.assert_any_call(
            'anti_affinity_group'
        )
        self.sdk_client.delete_server_group.assert_called_with(
            self.fake_server_group.id
        )
        self.assertEqual(2, self.sdk_client.find_server_group.call_count)
        self.assertEqual(2, self.sdk_client.delete_server_group.call_count)
        self.assertIsNone(result)

    def test_server_group_delete_no_input(self):
        arglist = []
        verifylist = None
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_server_group_multiple_delete_with_exception(self):
        arglist = ['affinity_group', 'anti_affinity_group']
        verifylist = [
            ('server_group', ['affinity_group', 'anti_affinity_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.sdk_client.find_server_group.side_effect = [
            self.fake_server_group,
            exceptions.CommandError,
        ]
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 server groups failed to delete.', str(e))

        self.sdk_client.find_server_group.assert_any_call('affinity_group')
        self.sdk_client.find_server_group.assert_any_call(
            'anti_affinity_group'
        )
        self.assertEqual(2, self.sdk_client.find_server_group.call_count)
        self.sdk_client.delete_server_group.assert_called_once_with(
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

    list_columns_v264 = (
        'ID',
        'Name',
        'Policy',
    )

    list_columns_v264_long = (
        'ID',
        'Name',
        'Policy',
        'Members',
        'Project Id',
        'User Id',
    )

    list_data = (
        (
            TestServerGroup.fake_server_group.id,
            TestServerGroup.fake_server_group.name,
            format_columns.ListColumn(
                TestServerGroup.fake_server_group.policies
            ),
        ),
    )

    list_data_long = (
        (
            TestServerGroup.fake_server_group.id,
            TestServerGroup.fake_server_group.name,
            format_columns.ListColumn(
                TestServerGroup.fake_server_group.policies
            ),
            format_columns.ListColumn(
                TestServerGroup.fake_server_group.member_ids
            ),
            TestServerGroup.fake_server_group.project_id,
            TestServerGroup.fake_server_group.user_id,
        ),
    )

    list_data_v264 = (
        (
            TestServerGroup.fake_server_group.id,
            TestServerGroup.fake_server_group.name,
            TestServerGroup.fake_server_group.policy,
        ),
    )

    list_data_v264_long = (
        (
            TestServerGroup.fake_server_group.id,
            TestServerGroup.fake_server_group.name,
            TestServerGroup.fake_server_group.policy,
            format_columns.ListColumn(
                TestServerGroup.fake_server_group.member_ids
            ),
            TestServerGroup.fake_server_group.project_id,
            TestServerGroup.fake_server_group.user_id,
        ),
    )

    def setUp(self):
        super().setUp()

        self.sdk_client.server_groups.return_value = [self.fake_server_group]
        self.cmd = server_group.ListServerGroup(self.app, None)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_server_group_list(self, sm_mock):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('limit', None),
            ('offset', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.server_groups.assert_called_once_with()

        self.assertCountEqual(self.list_columns, columns)
        self.assertCountEqual(self.list_data, tuple(data))

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_server_group_list_with_all_projects_and_long(self, sm_mock):
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
        self.sdk_client.server_groups.assert_called_once_with(
            all_projects=True
        )

        self.assertCountEqual(self.list_columns_long, columns)
        self.assertCountEqual(self.list_data_long, tuple(data))

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_list_with_limit(self, sm_mock):
        arglist = [
            '--limit',
            '1',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('limit', 1),
            ('offset', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.sdk_client.server_groups.assert_called_once_with(limit=1)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_list_with_offset(self, sm_mock):
        arglist = [
            '--offset',
            '5',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('limit', None),
            ('offset', 5),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.sdk_client.server_groups.assert_called_once_with(offset=5)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_list_v264(self, sm_mock):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.sdk_client.server_groups.assert_called_once_with()

        self.assertCountEqual(self.list_columns_v264, columns)
        self.assertCountEqual(self.list_data_v264, tuple(data))

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_list_with_all_projects_and_long_v264(self, sm_mock):
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
        self.sdk_client.server_groups.assert_called_once_with(
            all_projects=True
        )

        self.assertCountEqual(self.list_columns_v264_long, columns)
        self.assertCountEqual(self.list_data_v264_long, tuple(data))


class TestServerGroupShow(TestServerGroup):
    def setUp(self):
        super().setUp()

        self.sdk_client.find_server_group.return_value = self.fake_server_group
        self.cmd = server_group.ShowServerGroup(self.app, None)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_server_group_show(self, sm_mock):
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
