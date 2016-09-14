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

from keystoneauth1 import exceptions as ks_exc
from osc_lib import exceptions

from openstackclient.identity.v3 import group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


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


class TestGroupAddUser(TestGroup):

    group = identity_fakes.FakeGroup.create_one_group()
    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super(TestGroupAddUser, self).setUp()

        self.groups_mock.get.return_value = self.group
        self.users_mock.get.return_value = self.user
        self.users_mock.add_to_group.return_value = None

        self.cmd = group.AddUserToGroup(self.app, None)

    def test_group_add_user(self):
        arglist = [
            self.group.name,
            self.user.name,
        ]
        verifylist = [
            ('group', self.group.name),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.users_mock.add_to_group.assert_called_once_with(
            self.user.id, self.group.id)
        self.assertIsNone(result)


class TestGroupCheckUser(TestGroup):

    group = identity_fakes.FakeGroup.create_one_group()
    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super(TestGroupCheckUser, self).setUp()

        self.groups_mock.get.return_value = self.group
        self.users_mock.get.return_value = self.user
        self.users_mock.check_in_group.return_value = None

        self.cmd = group.CheckUserInGroup(self.app, None)

    def test_group_check_user(self):
        arglist = [
            self.group.name,
            self.user.name,
        ]
        verifylist = [
            ('group', self.group.name),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.users_mock.check_in_group.assert_called_once_with(
            self.user.id, self.group.id)
        self.assertIsNone(result)


class TestGroupCreate(TestGroup):

    domain = identity_fakes.FakeDomain.create_one_domain()

    columns = (
        'description',
        'domain_id',
        'id',
        'name',
    )

    def setUp(self):
        super(TestGroupCreate, self).setUp()
        self.group = identity_fakes.FakeGroup.create_one_group(
            attrs={'domain_id': self.domain.id})
        self.data = (
            self.group.description,
            self.group.domain_id,
            self.group.id,
            self.group.name,
        )

        self.groups_mock.create.return_value = self.group
        self.groups_mock.get.return_value = self.group
        self.domains_mock.get.return_value = self.domain

        self.cmd = group.CreateGroup(self.app, None)

    def test_group_create(self):
        arglist = [
            self.group.name,
        ]
        verifylist = [
            ('name', self.group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.groups_mock.create.assert_called_once_with(
            name=self.group.name,
            domain=None,
            description=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_group_create_with_options(self):
        arglist = [
            '--domain', self.domain.name,
            '--description', self.group.description,
            self.group.name,
        ]
        verifylist = [
            ('domain', self.domain.name),
            ('description', self.group.description),
            ('name', self.group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.groups_mock.create.assert_called_once_with(
            name=self.group.name,
            domain=self.domain.id,
            description=self.group.description,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_group_create_or_show(self):
        self.groups_mock.create.side_effect = ks_exc.Conflict()
        arglist = [
            '--or-show',
            self.group.name,
        ]
        verifylist = [
            ('or_show', True),
            ('name', self.group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_called_once_with(self.group.name)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestGroupDelete(TestGroup):

    domain = identity_fakes.FakeDomain.create_one_domain()
    groups = identity_fakes.FakeGroup.create_groups(
        attrs={'domain_id': domain.id}, count=2)

    def setUp(self):
        super(TestGroupDelete, self).setUp()

        self.groups_mock.get = (
            identity_fakes.FakeGroup.get_groups(self.groups))
        self.groups_mock.delete.return_value = None
        self.domains_mock.get.return_value = self.domain

        self.cmd = group.DeleteGroup(self.app, None)

    def test_group_delete(self):
        arglist = [
            self.groups[0].id,
        ]
        verifylist = [
            ('groups', [self.groups[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_called_once_with(self.groups[0].id)
        self.groups_mock.delete.assert_called_once_with(self.groups[0].id)
        self.assertIsNone(result)

    def test_group_multi_delete(self):
        arglist = []
        verifylist = []

        for g in self.groups:
            arglist.append(g.id)
        verifylist = [
            ('groups', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for g in self.groups:
            calls.append(call(g.id))
        self.groups_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_group_delete_with_domain(self):
        get_mock_result = [exceptions.CommandError, self.groups[0]]
        self.groups_mock.get = (
            mock.Mock(side_effect=get_mock_result))

        arglist = [
            '--domain', self.domain.id,
            self.groups[0].id,
        ]
        verifylist = [
            ('domain', self.groups[0].domain_id),
            ('groups', [self.groups[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_any_call(
            self.groups[0].id, domain_id=self.domain.id)
        self.groups_mock.delete.assert_called_once_with(self.groups[0].id)
        self.assertIsNone(result)


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


class TestGroupRemoveUser(TestGroup):

    group = identity_fakes.FakeGroup.create_one_group()
    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super(TestGroupRemoveUser, self).setUp()

        self.groups_mock.get.return_value = self.group
        self.users_mock.get.return_value = self.user
        self.users_mock.remove_from_group.return_value = None

        self.cmd = group.RemoveUserFromGroup(self.app, None)

    def test_group_remove_user(self):
        arglist = [
            self.group.id,
            self.user.id,
        ]
        verifylist = [
            ('group', self.group.id),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.users_mock.remove_from_group.assert_called_once_with(
            self.user.id, self.group.id)
        self.assertIsNone(result)


class TestGroupSet(TestGroup):

    domain = identity_fakes.FakeDomain.create_one_domain()
    group = identity_fakes.FakeGroup.create_one_group(
        attrs={'domain_id': domain.id})

    def setUp(self):
        super(TestGroupSet, self).setUp()

        self.groups_mock.get.return_value = self.group
        self.domains_mock.get.return_value = self.domain
        self.groups_mock.update.return_value = None

        self.cmd = group.SetGroup(self.app, None)

    def test_group_set_nothing(self):
        arglist = [
            self.group.id,
        ]
        verifylist = [
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.groups_mock.update.assert_called_once_with(self.group.id)
        self.assertIsNone(result)

    def test_group_set_name_and_description(self):
        arglist = [
            '--name', 'new_name',
            '--description', 'new_description',
            self.group.id,
        ]
        verifylist = [
            ('name', 'new_name'),
            ('description', 'new_description'),
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        kwargs = {
            'name': 'new_name',
            'description': 'new_description',
        }
        self.groups_mock.update.assert_called_once_with(
            self.group.id, **kwargs)
        self.assertIsNone(result)

    def test_group_set_with_domain(self):
        get_mock_result = [exceptions.CommandError, self.group]
        self.groups_mock.get = (
            mock.Mock(side_effect=get_mock_result))

        arglist = [
            '--domain', self.domain.id,
            self.group.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_any_call(
            self.group.id, domain_id=self.domain.id)
        self.groups_mock.update.assert_called_once_with(self.group.id)
        self.assertIsNone(result)


class TestGroupShow(TestGroup):

    domain = identity_fakes.FakeDomain.create_one_domain()

    columns = (
        'description',
        'domain_id',
        'id',
        'name',
    )

    def setUp(self):
        super(TestGroupShow, self).setUp()
        self.group = identity_fakes.FakeGroup.create_one_group(
            attrs={'domain_id': self.domain.id})
        self.data = (
            self.group.description,
            self.group.domain_id,
            self.group.id,
            self.group.name,
        )

        self.groups_mock.get.return_value = self.group
        self.domains_mock.get.return_value = self.domain

        self.cmd = group.ShowGroup(self.app, None)

    def test_group_show(self):
        arglist = [
            self.group.id,
        ]
        verifylist = [
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_called_once_with(self.group.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_group_show_with_domain(self):
        get_mock_result = [exceptions.CommandError, self.group]
        self.groups_mock.get = (
            mock.Mock(side_effect=get_mock_result))

        arglist = [
            '--domain', self.domain.id,
            self.group.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_any_call(
            self.group.id, domain_id=self.domain.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
