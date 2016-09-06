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

import mock

from keystoneauth1 import exceptions as ks_exc
from osc_lib import exceptions

from openstackclient.identity.v2_0 import role
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes


class TestRole(identity_fakes.TestIdentityv2):

    attr = {}
    attr['endpoints'] = [
        {
            'publicURL': identity_fakes.ENDPOINT['publicurl'],
        },
    ]
    fake_service = identity_fakes.FakeService.create_one_service(attr)
    fake_role = identity_fakes.FakeRole.create_one_role()
    fake_project = identity_fakes.FakeProject.create_one_project()
    attr = {}
    attr = {
        'tenantId': fake_project.id,
    }
    fake_user = identity_fakes.FakeUser.create_one_user(attr)

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

        auth_ref = identity_fakes.fake_auth_ref(
            identity_fakes.TOKEN,
            fake_service=self.fake_service,
        )
        self.ar_mock = mock.PropertyMock(return_value=auth_ref)
        type(self.app.client_manager).auth_ref = self.ar_mock


class TestRoleAdd(TestRole):

    def setUp(self):
        super(TestRoleAdd, self).setUp()

        self.projects_mock.get.return_value = self.fake_project

        self.users_mock.get.return_value = self.fake_user

        self.roles_mock.get.return_value = self.fake_role
        self.roles_mock.add_user_role.return_value = self.fake_role

        # Get the command object to test
        self.cmd = role.AddRole(self.app, None)

    def test_role_add(self):
        arglist = [
            '--project', self.fake_project.name,
            '--user', self.fake_user.name,
            self.fake_role.name,
        ]
        verifylist = [
            ('project', self.fake_project.name),
            ('user', self.fake_user.name),
            ('role', self.fake_role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.add_user_role(user, role, tenant=None)
        self.roles_mock.add_user_role.assert_called_with(
            self.fake_user.id,
            self.fake_role.id,
            self.fake_project.id,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_role.id,
            self.fake_role.name,
        )
        self.assertEqual(datalist, data)


class TestRoleCreate(TestRole):

    fake_role_c = identity_fakes.FakeRole.create_one_role()
    columns = (
        'id',
        'name'
    )
    datalist = (
        fake_role_c.id,
        fake_role_c.name,
    )

    def setUp(self):
        super(TestRoleCreate, self).setUp()

        self.roles_mock.create.return_value = self.fake_role_c

        # Get the command object to test
        self.cmd = role.CreateRole(self.app, None)

    def test_role_create_no_options(self):
        arglist = [
            self.fake_role_c.name,
        ]
        verifylist = [
            ('role_name', self.fake_role_c.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.create(name)
        self.roles_mock.create.assert_called_with(
            self.fake_role_c.name,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_role_create_or_show_exists(self):
        def _raise_conflict(*args, **kwargs):
            raise ks_exc.Conflict(None)

        # need to make this throw an exception...
        self.roles_mock.create.side_effect = _raise_conflict

        self.roles_mock.get.return_value = self.fake_role_c

        arglist = [
            '--or-show',
            self.fake_role_c.name,
        ]
        verifylist = [
            ('role_name', self.fake_role_c.name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.get(name, description, enabled)
        self.roles_mock.get.assert_called_with(self.fake_role_c.name)

        # RoleManager.create(name)
        self.roles_mock.create.assert_called_with(
            self.fake_role_c.name,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_role_create_or_show_not_exists(self):
        arglist = [
            '--or-show',
            self.fake_role_c.name,
        ]
        verifylist = [
            ('role_name', self.fake_role_c.name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.create(name)
        self.roles_mock.create.assert_called_with(
            self.fake_role_c.name,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestRoleDelete(TestRole):

    def setUp(self):
        super(TestRoleDelete, self).setUp()

        self.roles_mock.get.return_value = self.fake_role
        self.roles_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = role.DeleteRole(self.app, None)

    def test_role_delete_no_options(self):
        arglist = [
            self.fake_role.name,
        ]
        verifylist = [
            ('roles', [self.fake_role.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.roles_mock.delete.assert_called_with(
            self.fake_role.id,
        )
        self.assertIsNone(result)


class TestRoleList(TestRole):

    def setUp(self):
        super(TestRoleList, self).setUp()

        self.roles_mock.list.return_value = [self.fake_role]

        # Get the command object to test
        self.cmd = role.ListRole(self.app, None)

    def test_role_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            self.fake_role.id,
            self.fake_role.name,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestUserRoleList(TestRole):

    columns = (
        'ID',
        'Name',
        'Project',
        'User'
    )

    def setUp(self):
        super(TestUserRoleList, self).setUp()

        self.projects_mock.get.return_value = self.fake_project

        self.users_mock.get.return_value = self.fake_user

        self.roles_mock.roles_for_user.return_value = [self.fake_role]

        # Get the command object to test
        self.cmd = role.ListUserRole(self.app, None)

    def test_user_role_list_no_options_unscoped_token(self):
        auth_ref = identity_fakes.fake_auth_ref(
            identity_fakes.UNSCOPED_TOKEN,
            fake_service=self.fake_service,
        )
        self.ar_mock = mock.PropertyMock(return_value=auth_ref)
        type(self.app.client_manager).auth_ref = self.ar_mock

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # This argument combination should raise a CommandError
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_user_role_list_no_options_scoped_token(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            self.fake_user.id,
            self.fake_project.id,
        )

        collist = ('ID', 'Name', 'Project', 'User')
        self.assertEqual(collist, columns)
        datalist = ((
            self.fake_role.id,
            self.fake_role.name,
            self.fake_project.name,
            self.fake_user.name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_user_role_list_project_unscoped_token(self):
        auth_ref = identity_fakes.fake_auth_ref(
            identity_fakes.UNSCOPED_TOKEN,
            fake_service=self.fake_service,
        )
        self.ar_mock = mock.PropertyMock(return_value=auth_ref)
        type(self.app.client_manager).auth_ref = self.ar_mock

        self.projects_mock.get.return_value = self.fake_project
        arglist = [
            '--project', self.fake_project.name,
        ]
        verifylist = [
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            self.fake_user.id,
            self.fake_project.id,
        )

        self.assertEqual(columns, columns)
        datalist = ((
            self.fake_role.id,
            self.fake_role.name,
            self.fake_project.name,
            self.fake_user.name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_user_role_list_project_scoped_token(self):
        self.projects_mock.get.return_value = self.fake_project
        arglist = [
            '--project', self.fake_project.name,
        ]
        verifylist = [
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            self.fake_user.id,
            self.fake_project.id,
        )

        self.assertEqual(columns, columns)
        datalist = ((
            self.fake_role.id,
            self.fake_role.name,
            self.fake_project.name,
            self.fake_user.name,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestRoleRemove(TestRole):

    def setUp(self):
        super(TestRoleRemove, self).setUp()

        self.projects_mock.get.return_value = self.fake_project

        self.users_mock.get.return_value = self.fake_user

        self.roles_mock.get.return_value = self.fake_role
        self.roles_mock.remove_user_role.return_value = None

        # Get the command object to test
        self.cmd = role.RemoveRole(self.app, None)

    def test_role_remove(self):
        arglist = [
            '--project', self.fake_project.name,
            '--user', self.fake_user.name,
            self.fake_role.name,
        ]
        verifylist = [
            ('role', self.fake_role.name),
            ('project', self.fake_project.name),
            ('user', self.fake_user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # RoleManager.remove_user_role(user, role, tenant=None)
        self.roles_mock.remove_user_role.assert_called_with(
            self.fake_user.id,
            self.fake_role.id,
            self.fake_project.id,
        )
        self.assertIsNone(result)


class TestRoleShow(TestRole):

    def setUp(self):
        super(TestRoleShow, self).setUp()

        self.roles_mock.get.return_value = self.fake_role

        # Get the command object to test
        self.cmd = role.ShowRole(self.app, None)

    def test_service_show(self):
        arglist = [
            self.fake_role.name,
        ]
        verifylist = [
            ('role', self.fake_role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.get(role)
        self.roles_mock.get.assert_called_with(
            self.fake_role.name,
        )

        collist = ('id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_role.id,
            self.fake_role.name,
        )
        self.assertEqual(datalist, data)
