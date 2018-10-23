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
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.identity.v3 import role
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

    def test_role_add_domain_role_on_user_project(self):
        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE_2),
            loaded=True,
        )
        arglist = [
            '--user', identity_fakes.user_name,
            '--project', identity_fakes.project_name,
            '--role-domain', identity_fakes.domain_name,
            identity_fakes.ROLE_2['name'],
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', identity_fakes.user_name),
            ('group', None),
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', identity_fakes.ROLE_2['name']),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': identity_fakes.user_id,
            'project': identity_fakes.project_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.grant(role, user=, group=, domain=, project=)
        self.roles_mock.grant.assert_called_with(
            identity_fakes.ROLE_2['id'],
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_add_with_error(self):
        arglist = [
            identity_fakes.role_name,
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('domain', None),
            ('project', None),
            ('role', identity_fakes.role_name),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)


class TestRoleAddInherited(TestRoleAdd, TestRoleInherited):
    pass


class TestRoleCreate(TestRole):

    def setUp(self):
        super(TestRoleCreate, self).setUp()

        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )

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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'name': identity_fakes.role_name,
        }

        # RoleManager.create(name=, domain=)
        self.roles_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('domain', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            None,
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)

    def test_role_create_with_domain(self):

        self.roles_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE_2),
            loaded=True,
        )

        arglist = [
            '--domain', identity_fakes.domain_name,
            identity_fakes.ROLE_2['name'],
        ]
        verifylist = [
            ('domain', identity_fakes.domain_name),
            ('name', identity_fakes.ROLE_2['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': identity_fakes.domain_id,
            'name': identity_fakes.ROLE_2['name'],
        }

        # RoleManager.create(name=, domain=)
        self.roles_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('domain', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_id,
            identity_fakes.ROLE_2['id'],
            identity_fakes.ROLE_2['name'],
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

        result = self.cmd.take_action(parsed_args)

        self.roles_mock.delete.assert_called_with(
            identity_fakes.role_id,
        )
        self.assertIsNone(result)

    def test_role_delete_with_domain(self):
        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE_2),
            loaded=True,
        )
        self.roles_mock.delete.return_value = None

        arglist = [
            '--domain', identity_fakes.domain_name,
            identity_fakes.ROLE_2['name'],
        ]
        verifylist = [
            ('roles', [identity_fakes.ROLE_2['name']]),
            ('domain', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.roles_mock.delete.assert_called_with(
            identity_fakes.ROLE_2['id'],
        )
        self.assertIsNone(result)

    @mock.patch.object(utils, 'find_resource')
    def test_delete_multi_roles_with_exception(self, find_mock):
        find_mock.side_effect = [self.roles_mock.get.return_value,
                                 exceptions.CommandError]
        arglist = [
            identity_fakes.role_name,
            'unexist_role',
        ]
        verifylist = [
            ('roles', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 roles failed to delete.',
                             str(e))

        find_mock.assert_any_call(self.roles_mock,
                                  identity_fakes.role_name,
                                  domain_id=None)
        find_mock.assert_any_call(self.roles_mock,
                                  'unexist_role',
                                  domain_id=None)

        self.assertEqual(2, find_mock.call_count)
        self.roles_mock.delete.assert_called_once_with(identity_fakes.role_id)


class TestRoleList(TestRole):

    columns = (
        'ID',
        'Name',
    )
    datalist = (
        (
            identity_fakes.role_id,
            identity_fakes.role_name,
        ),
    )

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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_role_list_domain_role(self):
        self.roles_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLE_2),
                loaded=True,
            ),
        ]
        arglist = [
            '--domain', identity_fakes.domain_name,
        ]
        verifylist = [
            ('domain', identity_fakes.domain_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain_id': identity_fakes.domain_id
        }
        # RoleManager.list(user=, group=, domain=, project=, **kwargs)
        self.roles_mock.list.assert_called_with(
            **kwargs
        )

        collist = ('ID', 'Name', 'Domain')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.ROLE_2['id'],
            identity_fakes.ROLE_2['name'],
            identity_fakes.domain_name,
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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

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
        self.assertIsNone(result)

    def test_role_remove_domain_role_on_group_domain(self):
        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE_2),
            loaded=True,
        )
        arglist = [
            '--group', identity_fakes.group_name,
            '--domain', identity_fakes.domain_name,
            identity_fakes.ROLE_2['name'],
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', identity_fakes.group_name),
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', identity_fakes.ROLE_2['name']),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': identity_fakes.group_id,
            'domain': identity_fakes.domain_id,
            'os_inherit_extension_inherited': self._is_inheritance_testcase(),
        }
        # RoleManager.revoke(role, user=, group=, domain=, project=)
        self.roles_mock.revoke.assert_called_with(
            identity_fakes.ROLE_2['id'],
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_with_error(self):
        arglist = [
            identity_fakes.role_name,
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('domain', None),
            ('project', None),
            ('role', identity_fakes.role_name),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)


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

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
        }
        # RoleManager.update(role, name=)
        self.roles_mock.update.assert_called_with(
            identity_fakes.role_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_set_domain_role(self):
        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE_2),
            loaded=True,
        )
        arglist = [
            '--name', 'over',
            '--domain', identity_fakes.domain_name,
            identity_fakes.ROLE_2['name'],
        ]
        verifylist = [
            ('name', 'over'),
            ('domain', identity_fakes.domain_name),
            ('role', identity_fakes.ROLE_2['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
        }
        # RoleManager.update(role, name=)
        self.roles_mock.update.assert_called_with(
            identity_fakes.ROLE_2['id'],
            **kwargs
        )
        self.assertIsNone(result)


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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.get(role)
        self.roles_mock.get.assert_called_with(
            identity_fakes.role_name,
        )

        collist = ('domain', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            None,
            identity_fakes.role_id,
            identity_fakes.role_name,
        )
        self.assertEqual(datalist, data)

    def test_role_show_domain_role(self):
        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE_2),
            loaded=True,
        )
        arglist = [
            '--domain', identity_fakes.domain_name,
            identity_fakes.ROLE_2['name'],
        ]
        verifylist = [
            ('domain', identity_fakes.domain_name),
            ('role', identity_fakes.ROLE_2['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # RoleManager.get(role). This is called from utils.find_resource().
        # In fact, the current implementation calls the get(role) first with
        # just the name, then with the name+domain_id. So technically we should
        # mock this out with a call list, with the first call returning None
        # and the second returning the object. However, if we did that we are
        # then just testing the current sequencing within the utils method, and
        # would become brittle to changes within that method. Hence we just
        # check for the first call which is always lookup by name.
        self.roles_mock.get.assert_called_with(
            identity_fakes.ROLE_2['name'],
        )

        collist = ('domain', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.domain_id,
            identity_fakes.ROLE_2['id'],
            identity_fakes.ROLE_2['name'],
        )
        self.assertEqual(datalist, data)
