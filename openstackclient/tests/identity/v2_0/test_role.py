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

from openstackclient.common import exceptions
from openstackclient.identity.v2_0 import role
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


class TestRole(identity_fakes.TestIdentityv2):

    def setUp(self):
        super(TestRole, self).setUp()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants
        self.projects_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the RoleManager Mock
        self.roles_mock = self.app.client_manager.identity.roles
        self.roles_mock.reset_mock()


class TestRoleAdd(TestRole):

    def setUp(self):
        super(TestRoleAdd, self).setUp()

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

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )
        self.roles_mock.add_user_role.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = role.AddRole(self.app, None)

    def test_role_add(self):
        arglist = [
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_name,
            identity_fakes.role_name,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
            ('user', identity_fakes.user_name),
            ('role', identity_fakes.role_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.add_user_role(user, role, tenant=None)
        self.roles_mock.add_user_role.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.role_id,
            identity_fakes.project_id,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)


class TestRoleCreate(TestRole):

    def setUp(self):
        super(TestRoleCreate, self).setUp()

        self.roles_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = role.CreateRole(self.app, None)

    def test_role_create_no_options(self):
        arglist = [
            identity_fakes.role_name,
        ]
        verifylist = [
            ('role_name', identity_fakes.role_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.create(name)
        self.roles_mock.create.assert_called_with(
            identity_fakes.role_name,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)

    def test_role_create_or_show_exists(self):
        def _raise_conflict(*args, **kwargs):
            raise ksc_exc.Conflict(None)

        # need to make this throw an exception...
        self.roles_mock.create.side_effect = _raise_conflict

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        arglist = [
            '--or-show',
            identity_fakes.role_name,
        ]
        verifylist = [
            ('role_name', identity_fakes.role_name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.get(name, description, enabled)
        self.roles_mock.get.assert_called_with(identity_fakes.role_name)

        # RoleManager.create(name)
        self.roles_mock.create.assert_called_with(
            identity_fakes.role_name,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)

    def test_role_create_or_show_not_exists(self):
        arglist = [
            '--or-show',
            identity_fakes.role_name,
        ]
        verifylist = [
            ('role_name', identity_fakes.role_name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.create(name)
        self.roles_mock.create.assert_called_with(
            identity_fakes.role_name,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)


class TestRoleDelete(TestRole):

    def setUp(self):
        super(TestRoleDelete, self).setUp()

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )
        self.roles_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = role.DeleteRole(self.app, None)

    def test_role_delete_no_options(self):
        arglist = [
            identity_fakes.role_name,
        ]
        verifylist = [
            ('roles', [identity_fakes.role_name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.roles_mock.delete.assert_called_with(
            identity_fakes.role_id,
        )


class TestRoleList(TestRole):

    def setUp(self):
        super(TestRoleList, self).setUp()

        self.roles_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLE),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = role.ListRole(self.app, None)

    def test_role_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestUserRoleList(TestRole):

    def setUp(self):
        super(TestUserRoleList, self).setUp()

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

        self.roles_mock.roles_for_user.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLE),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = role.ListUserRole(self.app, None)

    def test_user_role_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # This argument combination should raise a CommandError
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_user_role_list_no_options_def_creds(self):
        auth_ref = self.app.client_manager.auth_ref = mock.MagicMock()
        auth_ref.project_id.return_value = identity_fakes.project_id
        auth_ref.user_id.return_value = identity_fakes.user_id

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.project_id,
        )

        collist = ('ID', 'Name', 'Project', 'User')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
            identity_fakes.project_name,
            identity_fakes.user_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_user_role_list_project(self):
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT_2),
            loaded=True,
        )
        arglist = [
            '--project', identity_fakes.PROJECT_2['name'],
        ]
        verifylist = [
            ('project', identity_fakes.PROJECT_2['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # This argument combination should raise a CommandError
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_user_role_list_project_def_creds(self):
        auth_ref = self.app.client_manager.auth_ref = mock.MagicMock()
        auth_ref.project_id.return_value = identity_fakes.project_id
        auth_ref.user_id.return_value = identity_fakes.user_id

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT_2),
            loaded=True,
        )
        arglist = [
            '--project', identity_fakes.PROJECT_2['name'],
        ]
        verifylist = [
            ('project', identity_fakes.PROJECT_2['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.PROJECT_2['id'],
        )

        collist = ('ID', 'Name', 'Project', 'User')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
            identity_fakes.PROJECT_2['name'],
            identity_fakes.user_name,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestRoleRemove(TestRole):

    def setUp(self):
        super(TestRoleRemove, self).setUp()

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

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )
        self.roles_mock.remove_user_role.return_value = None

        # Get the command object to test
        self.cmd = role.RemoveRole(self.app, None)

    def test_role_remove(self):
        arglist = [
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_name,
            identity_fakes.role_name,
        ]
        verifylist = [
            ('role', identity_fakes.role_name),
            ('project', identity_fakes.project_name),
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # RoleManager.remove_user_role(user, role, tenant=None)
        self.roles_mock.remove_user_role.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.role_id,
            identity_fakes.project_id,
        )


class TestRoleShow(TestRole):

    def setUp(self):
        super(TestRoleShow, self).setUp()

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = role.ShowRole(self.app, None)

    def test_service_show(self):
        arglist = [
            identity_fakes.role_name,
        ]
        verifylist = [
            ('role', identity_fakes.role_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.get(role)
        self.roles_mock.get.assert_called_with(
            identity_fakes.role_name,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)
