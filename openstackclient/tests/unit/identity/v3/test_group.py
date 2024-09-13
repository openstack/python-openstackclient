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
from unittest.mock import call

from keystoneauth1 import exceptions as ks_exc
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.identity.v3 import group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestGroup(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the GroupManager Mock
        self.groups_mock = self.identity_client.groups
        self.groups_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.identity_client.users
        self.users_mock.reset_mock()


class TestGroupAddUser(TestGroup):
    _group = identity_fakes.FakeGroup.create_one_group()
    users = identity_fakes.FakeUser.create_users(count=2)

    def setUp(self):
        super().setUp()

        self.groups_mock.get.return_value = self._group
        self.users_mock.get = identity_fakes.FakeUser.get_users(self.users)
        self.users_mock.add_to_group.return_value = None

        self.cmd = group.AddUserToGroup(self.app, None)

    def test_group_add_user(self):
        arglist = [
            self._group.name,
            self.users[0].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.users_mock.add_to_group.assert_called_once_with(
            self.users[0].id, self._group.id
        )
        self.assertIsNone(result)

    def test_group_add_multi_users(self):
        arglist = [
            self._group.name,
            self.users[0].name,
            self.users[1].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name, self.users[1].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        calls = [
            call(self.users[0].id, self._group.id),
            call(self.users[1].id, self._group.id),
        ]
        self.users_mock.add_to_group.assert_has_calls(calls)
        self.assertIsNone(result)

    @mock.patch.object(group.LOG, 'error')
    def test_group_add_user_with_error(self, mock_error):
        self.users_mock.add_to_group.side_effect = [
            exceptions.CommandError(),
            None,
        ]
        arglist = [
            self._group.name,
            self.users[0].name,
            self.users[1].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name, self.users[1].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            msg = f"1 of 2 users not added to group {self._group.name}."
            self.assertEqual(msg, str(e))
        msg = f"{self.users[0].name} not added to group {self._group.name}: "
        mock_error.assert_called_once_with(msg)


class TestGroupCheckUser(TestGroup):
    group = identity_fakes.FakeGroup.create_one_group()
    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super().setUp()

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
            self.user.id, self.group.id
        )
        self.assertIsNone(result)

    def test_group_check_user_server_error(self):
        def server_error(*args):
            raise ks_exc.http.InternalServerError

        self.users_mock.check_in_group.side_effect = server_error
        arglist = [
            self.group.name,
            self.user.name,
        ]
        verifylist = [
            ('group', self.group.name),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            ks_exc.http.InternalServerError, self.cmd.take_action, parsed_args
        )


class TestGroupCreate(TestGroup):
    domain = identity_fakes.FakeDomain.create_one_domain()

    columns = (
        'description',
        'domain_id',
        'id',
        'name',
    )

    def setUp(self):
        super().setUp()
        self.group = identity_fakes.FakeGroup.create_one_group(
            attrs={'domain_id': self.domain.id}
        )
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
            '--domain',
            self.domain.name,
            '--description',
            self.group.description,
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
        attrs={'domain_id': domain.id}, count=2
    )

    def setUp(self):
        super().setUp()

        self.groups_mock.get = identity_fakes.FakeGroup.get_groups(self.groups)
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
        self.groups_mock.get = mock.Mock(side_effect=get_mock_result)

        arglist = [
            '--domain',
            self.domain.id,
            self.groups[0].id,
        ]
        verifylist = [
            ('domain', self.groups[0].domain_id),
            ('groups', [self.groups[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_any_call(
            self.groups[0].id, domain_id=self.domain.id
        )
        self.groups_mock.delete.assert_called_once_with(self.groups[0].id)
        self.assertIsNone(result)

    @mock.patch.object(utils, 'find_resource')
    def test_delete_multi_groups_with_exception(self, find_mock):
        find_mock.side_effect = [self.groups[0], exceptions.CommandError]
        arglist = [
            self.groups[0].id,
            'unexist_group',
        ]
        verifylist = [
            ('groups', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 groups failed to delete.', str(e))

        find_mock.assert_any_call(self.groups_mock, self.groups[0].id)
        find_mock.assert_any_call(self.groups_mock, 'unexist_group')

        self.assertEqual(2, find_mock.call_count)
        self.groups_mock.delete.assert_called_once_with(self.groups[0].id)


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
        super().setUp()

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

        self.groups_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_group_list_domain(self):
        arglist = [
            '--domain',
            self.domain.id,
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

        self.groups_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_group_list_user(self):
        arglist = [
            '--user',
            self.user.name,
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

        self.groups_mock.list.assert_called_with(**kwargs)

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

        self.groups_mock.list.assert_called_with(**kwargs)

        columns = self.columns + (
            'Domain ID',
            'Description',
        )
        datalist = (
            (
                self.group.id,
                self.group.name,
                self.group.domain_id,
                self.group.description,
            ),
        )
        self.assertEqual(columns, columns)
        self.assertEqual(datalist, tuple(data))


class TestGroupRemoveUser(TestGroup):
    _group = identity_fakes.FakeGroup.create_one_group()
    users = identity_fakes.FakeUser.create_users(count=2)

    def setUp(self):
        super().setUp()

        self.groups_mock.get.return_value = self._group
        self.users_mock.get = identity_fakes.FakeUser.get_users(self.users)
        self.users_mock.remove_from_group.return_value = None

        self.cmd = group.RemoveUserFromGroup(self.app, None)

    def test_group_remove_user(self):
        arglist = [
            self._group.id,
            self.users[0].id,
        ]
        verifylist = [
            ('group', self._group.id),
            ('user', [self.users[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.users_mock.remove_from_group.assert_called_once_with(
            self.users[0].id, self._group.id
        )
        self.assertIsNone(result)

    def test_group_remove_multi_users(self):
        arglist = [
            self._group.name,
            self.users[0].name,
            self.users[1].name,
        ]
        verifylist = [
            ('group', self._group.name),
            ('user', [self.users[0].name, self.users[1].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        calls = [
            call(self.users[0].id, self._group.id),
            call(self.users[1].id, self._group.id),
        ]
        self.users_mock.remove_from_group.assert_has_calls(calls)
        self.assertIsNone(result)

    @mock.patch.object(group.LOG, 'error')
    def test_group_remove_user_with_error(self, mock_error):
        self.users_mock.remove_from_group.side_effect = [
            exceptions.CommandError(),
            None,
        ]
        arglist = [
            self._group.id,
            self.users[0].id,
            self.users[1].id,
        ]
        verifylist = [
            ('group', self._group.id),
            ('user', [self.users[0].id, self.users[1].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            msg = f"1 of 2 users not removed from group {self._group.id}."
            self.assertEqual(msg, str(e))
        msg = f"{self.users[0].id} not removed from group {self._group.id}: "
        mock_error.assert_called_once_with(msg)


class TestGroupSet(TestGroup):
    domain = identity_fakes.FakeDomain.create_one_domain()
    group = identity_fakes.FakeGroup.create_one_group(
        attrs={'domain_id': domain.id}
    )

    def setUp(self):
        super().setUp()

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
            '--name',
            'new_name',
            '--description',
            'new_description',
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
            self.group.id, **kwargs
        )
        self.assertIsNone(result)

    def test_group_set_with_domain(self):
        get_mock_result = [exceptions.CommandError, self.group]
        self.groups_mock.get = mock.Mock(side_effect=get_mock_result)

        arglist = [
            '--domain',
            self.domain.id,
            self.group.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_any_call(
            self.group.id, domain_id=self.domain.id
        )
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
        super().setUp()
        self.group = identity_fakes.FakeGroup.create_one_group(
            attrs={'domain_id': self.domain.id}
        )
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
        self.groups_mock.get = mock.Mock(side_effect=get_mock_result)

        arglist = [
            '--domain',
            self.domain.id,
            self.group.id,
        ]
        verifylist = [
            ('domain', self.domain.id),
            ('group', self.group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.groups_mock.get.assert_any_call(
            self.group.id, domain_id=self.domain.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
