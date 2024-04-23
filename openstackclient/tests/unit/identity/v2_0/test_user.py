#   Copyright 2013 Nebula Inc.
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

from keystoneauth1 import exceptions as ks_exc
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.identity.v2_0 import user
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes


class TestUser(identity_fakes.TestIdentityv2):
    fake_project = identity_fakes.FakeProject.create_one_project()
    attr = {
        'tenantId': fake_project.id,
    }
    fake_user = identity_fakes.FakeUser.create_one_user(attr)

    def setUp(self):
        super().setUp()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.identity_client.tenants
        self.projects_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.identity_client.users
        self.users_mock.reset_mock()


class TestUserCreate(TestUser):
    fake_project_c = identity_fakes.FakeProject.create_one_project()
    attr = {
        'tenantId': fake_project_c.id,
    }
    fake_user_c = identity_fakes.FakeUser.create_one_user(attr)

    columns = (
        'email',
        'enabled',
        'id',
        'name',
        'project_id',
    )
    datalist = (
        fake_user_c.email,
        True,
        fake_user_c.id,
        fake_user_c.name,
        fake_project_c.id,
    )

    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_project_c

        self.users_mock.create.return_value = self.fake_user_c

        # Get the command object to test
        self.cmd = user.CreateUser(self.app, None)

    def test_user_create_no_options(self):
        arglist = [
            self.fake_user_c.name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', False),
            ('name', self.fake_user_c.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, None, None, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_password(self):
        arglist = [
            '--password',
            'secret',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('password_prompt', False),
            ('password', 'secret'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, 'secret', None, **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_password_prompt(self):
        arglist = [
            '--password-prompt',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('password_prompt', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        mocker = mock.Mock()
        mocker.return_value = 'abc123'
        with mock.patch("osc_lib.utils.get_password", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, 'abc123', None, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_email(self):
        arglist = [
            '--email',
            'barney@example.com',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('email', 'barney@example.com'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, None, 'barney@example.com', **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_project(self):
        # Return the new project
        self.projects_mock.get.return_value = self.fake_project_c

        # Set up to return an updated user
        attr = {
            'tenantId': self.fake_project_c.id,
        }
        user_2 = identity_fakes.FakeUser.create_one_user(attr)
        self.users_mock.create.return_value = user_2

        arglist = [
            '--project',
            self.fake_project_c.name,
            user_2.name,
        ]
        verifylist = [
            ('name', user_2.name),
            ('project', self.fake_project_c.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': self.fake_project_c.id,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            user_2.name, None, None, **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            user_2.email,
            True,
            user_2.id,
            user_2.name,
            self.fake_project_c.id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_enable(self):
        arglist = [
            '--enable',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('enable', True),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, None, None, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_disable(self):
        arglist = [
            '--disable',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('enable', False),
            ('disable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, None, None, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_or_show_exists(self):
        def _raise_conflict(*args, **kwargs):
            raise ks_exc.Conflict(None)

        # need to make this throw an exception...
        self.users_mock.create.side_effect = _raise_conflict

        self.users_mock.get.return_value = self.fake_user_c

        arglist = [
            '--or-show',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.get.assert_called_with(self.fake_user_c.name)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_or_show_not_exists(self):
        arglist = [
            '--or-show',
            self.fake_user_c.name,
        ]
        verifylist = [
            ('name', self.fake_user_c.name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            self.fake_user_c.name, None, None, **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestUserDelete(TestUser):
    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.users_mock.get.return_value = self.fake_user
        self.users_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = user.DeleteUser(self.app, None)

    def test_user_delete_no_options(self):
        arglist = [
            self.fake_user.id,
        ]
        verifylist = [
            ('users', [self.fake_user.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.users_mock.delete.assert_called_with(
            self.fake_user.id,
        )
        self.assertIsNone(result)

    @mock.patch.object(utils, 'find_resource')
    def test_delete_multi_users_with_exception(self, find_mock):
        find_mock.side_effect = [self.fake_user, exceptions.CommandError]
        arglist = [
            self.fake_user.id,
            'unexist_user',
        ]
        verifylist = [
            ('users', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 users failed to delete.', str(e))

        find_mock.assert_any_call(self.users_mock, self.fake_user.id)
        find_mock.assert_any_call(self.users_mock, 'unexist_user')

        self.assertEqual(2, find_mock.call_count)
        self.users_mock.delete.assert_called_once_with(self.fake_user.id)


class TestUserList(TestUser):
    fake_project_l = identity_fakes.FakeProject.create_one_project()
    attr = {
        'tenantId': fake_project_l.id,
    }
    fake_user_l = identity_fakes.FakeUser.create_one_user(attr)

    columns = (
        'ID',
        'Name',
    )
    datalist = (
        (
            fake_user_l.id,
            fake_user_l.name,
        ),
    )

    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_project_l
        self.projects_mock.list.return_value = [self.fake_project_l]

        self.users_mock.list.return_value = [self.fake_user_l]

        # Get the command object to test
        self.cmd = user.ListUser(self.app, None)

    def test_user_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with(tenant_id=None)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_user_list_project(self):
        arglist = [
            '--project',
            self.fake_project_l.id,
        ]
        verifylist = [
            ('project', self.fake_project_l.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        project_id = self.fake_project_l.id

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with(tenant_id=project_id)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_user_list_long(self):
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

        self.users_mock.list.assert_called_with(tenant_id=None)

        collist = ('ID', 'Name', 'Project', 'Email', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.fake_user_l.id,
                self.fake_user_l.name,
                user.ProjectColumn(
                    self.fake_project_l.id,
                    {self.fake_project_l.id: self.fake_project_l},
                ),
                self.fake_user_l.email,
                True,
            ),
        )
        self.assertCountEqual(datalist, tuple(data))


class TestUserSet(TestUser):
    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_project
        self.users_mock.get.return_value = self.fake_user

        # Get the command object to test
        self.cmd = user.SetUser(self.app, None)

    def test_user_set_no_options(self):
        arglist = [
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_user_set_unexist_user(self):
        arglist = [
            "unexist-user",
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', "unexist-user"),
        ]
        self.users_mock.get.side_effect = exceptions.NotFound(None)
        self.users_mock.find.side_effect = exceptions.NotFound(None)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_user_set_name(self):
        arglist = [
            '--name',
            'qwerty',
            self.fake_user.name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'name': 'qwerty',
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(self.fake_user.id, **kwargs)
        self.assertIsNone(result)

    def test_user_set_password(self):
        arglist = [
            '--password',
            'secret',
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', 'secret'),
            ('password_prompt', False),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # UserManager.update_password(user, password)
        self.users_mock.update_password.assert_called_with(
            self.fake_user.id,
            'secret',
        )
        self.assertIsNone(result)

    def test_user_set_password_prompt(self):
        arglist = [
            '--password-prompt',
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('password_prompt', True),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = 'abc123'
        with mock.patch("osc_lib.utils.get_password", mocker):
            result = self.cmd.take_action(parsed_args)

        # UserManager.update_password(user, password)
        self.users_mock.update_password.assert_called_with(
            self.fake_user.id,
            'abc123',
        )
        self.assertIsNone(result)

    def test_user_set_email(self):
        arglist = [
            '--email',
            'barney@example.com',
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', 'barney@example.com'),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'email': 'barney@example.com',
            'enabled': True,
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(self.fake_user.id, **kwargs)
        self.assertIsNone(result)

    def test_user_set_project(self):
        arglist = [
            '--project',
            self.fake_project.id,
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', self.fake_project.id),
            ('enable', False),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # UserManager.update_tenant(user, tenant)
        self.users_mock.update_tenant.assert_called_with(
            self.fake_user.id,
            self.fake_project.id,
        )
        self.assertIsNone(result)

    def test_user_set_enable(self):
        arglist = [
            '--enable',
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', True),
            ('disable', False),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(self.fake_user.id, **kwargs)
        self.assertIsNone(result)

    def test_user_set_disable(self):
        arglist = [
            '--disable',
            self.fake_user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', True),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(self.fake_user.id, **kwargs)
        self.assertIsNone(result)


class TestUserShow(TestUser):
    def setUp(self):
        super().setUp()

        self.users_mock.get.return_value = self.fake_user

        # Get the command object to test
        self.cmd = user.ShowUser(self.app, None)

    def test_user_show(self):
        arglist = [
            self.fake_user.id,
        ]
        verifylist = [
            ('user', self.fake_user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.get.assert_called_with(self.fake_user.id)

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_user.email,
            True,
            self.fake_user.id,
            self.fake_user.name,
            self.fake_project.id,
        )
        self.assertCountEqual(datalist, data)
