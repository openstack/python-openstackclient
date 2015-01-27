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

import copy
import mock

from keystoneclient import exceptions as ksc_exc
from openstackclient.identity.v2_0 import user
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


class TestUser(identity_fakes.TestIdentityv2):

    def setUp(self):
        super(TestUser, self).setUp()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants
        self.projects_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()


class TestUserCreate(TestUser):

    def setUp(self):
        super(TestUserCreate, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.users_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = user.CreateUser(self.app, None)

    def test_user_create_no_options(self):
        arglist = [
            identity_fakes.user_name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', False),
            ('name', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_password(self):
        arglist = [
            '--password', 'secret',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('password_prompt', False),
            ('password', 'secret')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            'secret',
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_password_prompt(self):
        arglist = [
            '--password-prompt',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('password_prompt', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        mocker = mock.Mock()
        mocker.return_value = 'abc123'
        with mock.patch("openstackclient.common.utils.get_password", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            'abc123',
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_email(self):
        arglist = [
            '--email', 'barney@example.com',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('email', 'barney@example.com'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            None,
            'barney@example.com',
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_project(self):
        # Return the new project
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT_2),
            loaded=True,
        )
        # Set up to return an updated user
        USER_2 = copy.deepcopy(identity_fakes.USER)
        USER_2['tenantId'] = identity_fakes.PROJECT_2['id']
        self.users_mock.create.return_value = fakes.FakeResource(
            None,
            USER_2,
            loaded=True,
        )

        arglist = [
            '--project', identity_fakes.PROJECT_2['name'],
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('project', identity_fakes.PROJECT_2['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': identity_fakes.PROJECT_2['id'],
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.PROJECT_2['id'],
        )
        self.assertEqual(datalist, data)

    def test_user_create_enable(self):
        arglist = [
            '--enable',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('enable', True),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_disable(self):
        arglist = [
            '--disable',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('enable', False),
            ('disable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_or_show_exists(self):
        def _raise_conflict(*args, **kwargs):
            raise ksc_exc.Conflict(None)

        # need to make this throw an exception...
        self.users_mock.create.side_effect = _raise_conflict

        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        arglist = [
            '--or-show',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.get.assert_called_with(identity_fakes.user_name)

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_user_create_or_show_not_exists(self):
        arglist = [
            '--or-show',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', identity_fakes.user_name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'tenant_id': None,
        }
        # UserManager.create(name, password, email, tenant_id=, enabled=)
        self.users_mock.create.assert_called_with(
            identity_fakes.user_name,
            None,
            None,
            **kwargs
        )

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)


class TestUserDelete(TestUser):

    def setUp(self):
        super(TestUserDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )
        self.users_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = user.DeleteUser(self.app, None)

    def test_user_delete_no_options(self):
        arglist = [
            identity_fakes.user_id,
        ]
        verifylist = [
            ('users', [identity_fakes.user_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.users_mock.delete.assert_called_with(
            identity_fakes.user_id,
        )


class TestUserList(TestUser):

    def setUp(self):
        super(TestUserList, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT_2),
            loaded=True,
        )
        self.projects_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.PROJECT),
                loaded=True,
            ),
        ]

        self.users_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.USER),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = user.ListUser(self.app, None)

    def test_user_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with(tenant_id=None)

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.user_id,
            identity_fakes.user_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_user_list_project(self):
        arglist = [
            '--project', identity_fakes.project_id,
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        project_id = identity_fakes.PROJECT_2['id']

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with(tenant_id=project_id)

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.user_id,
            identity_fakes.user_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_user_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.list.assert_called_with(tenant_id=None)

        collist = ('ID', 'Name', 'Project', 'Email', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_name,
            identity_fakes.user_email,
            True,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestUserSet(TestUser):

    def setUp(self):
        super(TestUserSet, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = user.SetUser(self.app, None)

    def test_user_set_no_options(self):
        arglist = [
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

    def test_user_set_name(self):
        arglist = [
            '--name', 'qwerty',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'name': 'qwerty',
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(
            identity_fakes.user_id,
            **kwargs
        )

    def test_user_set_password(self):
        arglist = [
            '--password', 'secret',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', 'secret'),
            ('password_prompt', False),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # UserManager.update_password(user, password)
        self.users_mock.update_password.assert_called_with(
            identity_fakes.user_id,
            'secret',
        )

    def test_user_set_password_prompt(self):
        arglist = [
            '--password-prompt',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('password_prompt', True),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        mocker = mock.Mock()
        mocker.return_value = 'abc123'
        with mock.patch("openstackclient.common.utils.get_password", mocker):
            self.cmd.take_action(parsed_args)

        # UserManager.update_password(user, password)
        self.users_mock.update_password.assert_called_with(
            identity_fakes.user_id,
            'abc123',
        )

    def test_user_set_email(self):
        arglist = [
            '--email', 'barney@example.com',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', 'barney@example.com'),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'email': 'barney@example.com',
            'enabled': True,
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(
            identity_fakes.user_id,
            **kwargs
        )

    def test_user_set_project(self):
        arglist = [
            '--project', identity_fakes.project_id,
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', identity_fakes.project_id),
            ('enable', False),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # UserManager.update_tenant(user, tenant)
        self.users_mock.update_tenant.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.project_id,
        )

    def test_user_set_enable(self):
        arglist = [
            '--enable',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', True),
            ('disable', False),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(
            identity_fakes.user_id,
            **kwargs
        )

    def test_user_set_disable(self):
        arglist = [
            '--disable',
            identity_fakes.user_name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', True),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        # UserManager.update(user, **kwargs)
        self.users_mock.update.assert_called_with(
            identity_fakes.user_id,
            **kwargs
        )


class TestUserShow(TestUser):

    def setUp(self):
        super(TestUserShow, self).setUp()

        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = user.ShowUser(self.app, None)

    def test_user_show(self):
        arglist = [
            identity_fakes.user_id,
        ]
        verifylist = [
            ('user', identity_fakes.user_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.get.assert_called_with(identity_fakes.user_id)

        collist = ('email', 'enabled', 'id', 'name', 'project_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.user_email,
            True,
            identity_fakes.user_id,
            identity_fakes.user_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)
