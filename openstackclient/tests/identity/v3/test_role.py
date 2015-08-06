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

from openstackclient.identity.v3 import role
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestRole(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestRole, self).setUp()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.groups_mock = self.app.client_manager.identity.groups
        self.groups_mock.reset_mock()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()

        # Get a shortcut to the RoleManager Mock
        self.roles_mock = self.app.client_manager.identity.roles
        self.roles_mock.reset_mock()

    def _is_inheritance_testcase(self):
        return False


class TestRoleInherited(TestRole):

    def _is_inheritance_testcase(self):
        return True


class TestRoleAdd(TestRole):

    def setUp(self):
        super(TestRoleAdd, self).setUp()

        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        self.groups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.GROUP),
            loaded=True,
        )

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )
        self.roles_mock.grant.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = role.AddRole(self.app, None)

    def test_role_add_user_domain(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--domain', identity_fakes.domain_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', identity_fakes.user_name),
            ('group', None),
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'user': identity_fakes.user_id,
            'domain': identity_fakes.domain_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.grant(role, user=, group=, domain=, project=)
        self.roles_mock.grant.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )

    def test_role_add_user_project(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--project', identity_fakes.project_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', identity_fakes.user_name),
            ('group', None),
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'user': identity_fakes.user_id,
            'project': identity_fakes.project_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.grant(role, user=, group=, domain=, project=)
        self.roles_mock.grant.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )

    def test_role_add_group_domain(self):
        arglist = [
            '--group', identity_fakes.group_name,
            '--domain', identity_fakes.domain_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', identity_fakes.group_name),
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'group': identity_fakes.group_id,
            'domain': identity_fakes.domain_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.grant(role, user=, group=, domain=, project=)
        self.roles_mock.grant.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )

    def test_role_add_group_project(self):
        arglist = [
            '--group', identity_fakes.group_name,
            '--project', identity_fakes.project_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', identity_fakes.group_name),
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'group': identity_fakes.group_id,
            'project': identity_fakes.project_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.grant(role, user=, group=, domain=, project=)
        self.roles_mock.grant.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )


class TestRoleAddInherited(TestRoleAdd, TestRoleInherited):
    pass


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
            ('name', identity_fakes.role_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': identity_fakes.role_name,
        }

        # RoleManager.create(name=)
        self.roles_mock.create.assert_called_with(
            **kwargs
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

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )
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
        self.groups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.GROUP),
            loaded=True,
        )

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

    def test_user_list_user(self):
        arglist = [
            '--user', identity_fakes.user_id,
        ]
        verifylist = [
            ('user', identity_fakes.user_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': 'default',
            'user': self.users_mock.get(),
        }
        # RoleManager.list(user=, group=, domain=, project=, **kwargs)
        self.roles_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_role_list_domain_user(self):
        arglist = [
            '--domain', identity_fakes.domain_name,
            '--user', identity_fakes.user_id,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_name),
            ('user', identity_fakes.user_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': self.domains_mock.get(),
            'user': self.users_mock.get(),
        }
        # RoleManager.list(user=, group=, domain=, project=, **kwargs)
        self.roles_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name', 'Domain', 'User')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
            identity_fakes.domain_name,
            identity_fakes.user_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_role_list_domain_group(self):
        arglist = [
            '--domain', identity_fakes.domain_name,
            '--group', identity_fakes.group_id,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_name),
            ('group', identity_fakes.group_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': self.domains_mock.get(),
            'group': self.groups_mock.get(),
        }
        # RoleManager.list(user=, group=, domain=, project=, **kwargs)
        self.roles_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name', 'Domain', 'Group')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
            identity_fakes.domain_name,
            identity_fakes.group_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_role_list_project_user(self):
        arglist = [
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_id,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
            ('user', identity_fakes.user_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'project': self.projects_mock.get(),
            'user': self.users_mock.get(),
        }
        # RoleManager.list(user=, group=, domain=, project=, **kwargs)
        self.roles_mock.list.assert_called_with(
            **kwargs
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

    def test_role_list_project_group(self):
        arglist = [
            '--project', identity_fakes.project_name,
            '--group', identity_fakes.group_id,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
            ('group', identity_fakes.group_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'project': self.projects_mock.get(),
            'group': self.groups_mock.get(),
        }
        # RoleManager.list(user=, group=, domain=, project=, **kwargs)
        self.roles_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name', 'Project', 'Group')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.role_name,
            identity_fakes.project_name,
            identity_fakes.group_name,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestRoleRemove(TestRole):

    def setUp(self):
        super(TestRoleRemove, self).setUp()

        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        self.groups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.GROUP),
            loaded=True,
        )

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )
        self.roles_mock.revoke.return_value = None

        # Get the command object to test
        self.cmd = role.RemoveRole(self.app, None)

    def test_role_remove_user_domain(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--domain', identity_fakes.domain_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', identity_fakes.user_name),
            ('group', None),
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': identity_fakes.user_id,
            'domain': identity_fakes.domain_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.revoke(role, user=, group=, domain=, project=)
        self.roles_mock.revoke.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )

    def test_role_remove_user_project(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--project', identity_fakes.project_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', identity_fakes.user_name),
            ('group', None),
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': identity_fakes.user_id,
            'project': identity_fakes.project_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.revoke(role, user=, group=, domain=, project=)
        self.roles_mock.revoke.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )

    def test_role_remove_group_domain(self):
        arglist = [
            '--group', identity_fakes.group_name,
            '--domain', identity_fakes.domain_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', identity_fakes.group_name),
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', identity_fakes.role_name),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': identity_fakes.group_id,
            'domain': identity_fakes.domain_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.revoke(role, user=, group=, domain=, project=)
        self.roles_mock.revoke.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )

    def test_role_remove_group_project(self):
        arglist = [
            '--group', identity_fakes.group_name,
            '--project', identity_fakes.project_name,
            identity_fakes.role_name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', identity_fakes.group_name),
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', identity_fakes.role_name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': identity_fakes.group_id,
            'project': identity_fakes.project_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.revoke(role, user=, group=, domain=, project=)
        self.roles_mock.revoke.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )


class TestRoleSet(TestRole):

    def setUp(self):
        super(TestRoleSet, self).setUp()

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )
        self.roles_mock.update.return_value = None

        # Get the command object to test
        self.cmd = role.SetRole(self.app, None)

    def test_role_set_no_options(self):
        arglist = [
            '--name', 'over',
            identity_fakes.role_name,
        ]
        verifylist = [
            ('name', 'over'),
            ('role', identity_fakes.role_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
        }
        # RoleManager.update(role, name=)
        self.roles_mock.update.assert_called_with(
            identity_fakes.role_id,
            **kwargs
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

    def test_role_show(self):
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
