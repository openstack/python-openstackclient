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

from openstackclient.common import utils
from openstackclient.compute.v2 import server_group
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import utils as tests_utils


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
        utils.format_list(fake_server_group.members),
        fake_server_group.name,
        utils.format_list(fake_server_group.policies),
        fake_server_group.project_id,
        fake_server_group.user_id,
    )

    def setUp(self):
        super(TestServerGroup, self).setUp()

        # Get a shortcut to the ServerGroupsManager Mock
        self.server_groups_mock = self.app.client_manager.compute.server_groups
        self.server_groups_mock.reset_mock()


class TestServerGroupCreate(TestServerGroup):

    def setUp(self):
        super(TestServerGroupCreate, self).setUp()

        self.server_groups_mock.create.return_value = self.fake_server_group
        self.cmd = server_group.CreateServerGroup(self.app, None)

    def test_server_group_create(self):
        arglist = [
            '--policy', 'affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', ['affinity']),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.create.assert_called_once_with(
            name=parsed_args.name,
            policies=parsed_args.policy,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_server_group_create_with_multiple_policies(self):
        arglist = [
            '--policy', 'affinity',
            '--policy', 'soft-affinity',
            'affinity_group',
        ]
        verifylist = [
            ('policy', ['affinity', 'soft-affinity']),
            ('name', 'affinity_group'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.server_groups_mock.create.assert_called_once_with(
            name=parsed_args.name,
            policies=parsed_args.policy,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_server_group_create_no_policy(self):
        arglist = [
            'affinity_group',
        ]
        verifylist = None
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)
