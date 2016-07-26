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

from openstackclient.identity.v3 import group
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

    domain = identity_fakes.FakeDomain.create_one_domain()
    group = identity_fakes.FakeGroup.create_one_group()
    user = identity_fakes.FakeUser.create_one_user()

    columns = (
        'ID',
        'Name',
    )
    datalist = (
        (
            group.id,
            group.name,
        ),
    )

    def setUp(self):
        super(TestGroupList, self).setUp()

        self.groups_mock.get.return_value = self.group
        self.groups_mock.list.return_value = [self.group]

        self.domains_mock.get.return_value = self.domain

        self.users_mock.get.return_value = self.user

        # Get the command object to test
        self.cmd = group.ListGroup(self.app, None)

    def test_group_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'user': None,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_group_list_domain(self):
        arglist = [
            '--domain', self.domain.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': self.domain.id,
            'user': None,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_group_list_user(self):
        arglist = [
            '--user', self.user.name,
        ]
        verifylist = [
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'user': self.user.id,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_group_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'user': None,
        }

        self.groups_mock.list.assert_called_with(
            **kwargs
        )

        columns = self.columns + (
            'Domain ID',
            'Description',
        )
        datalist = ((
            self.group.id,
            self.group.name,
            self.group.domain_id,
            self.group.description,
        ), )
        self.assertEqual(columns, columns)
        self.assertEqual(datalist, tuple(data))
