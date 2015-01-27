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

import copy

from openstackclient.identity.v3 import group
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestGroup(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestGroup, self).setUp()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the GroupManager Mock
        self.groups_mock = self.app.client_manager.identity.groups
        self.groups_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()


class TestGroupList(TestGroup):

    def setUp(self):
        super(TestGroupList, self).setUp()

        self.groups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.GROUP),
            loaded=True,
        )
        self.groups_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.GROUP),
                loaded=True,
            ),
        ]

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = group.ListGroup(self.app, None)

    def test_group_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'user': None,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.group_id,
            identity_fakes.group_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_group_list_domain(self):
        arglist = [
            '--domain', identity_fakes.domain_id,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': identity_fakes.domain_id,
            'user': None,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.group_id,
            identity_fakes.group_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_group_list_user(self):
        arglist = [
            '--user', identity_fakes.user_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'user': identity_fakes.user_id,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.group_id,
            identity_fakes.group_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_group_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'user': None,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'Domain ID',
            'Description',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.group_id,
            identity_fakes.group_name,
            '',
            '',
        ), )
        self.assertEqual(datalist, tuple(data))
