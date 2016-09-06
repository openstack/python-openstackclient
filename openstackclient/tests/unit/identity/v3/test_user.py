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

import contextlib
import mock

from openstackclient.identity.v3 import user
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestUser(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestUser, self).setUp()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()

        # Get a shortcut to the GroupManager Mock
        self.groups_mock = self.app.client_manager.identity.groups
        self.groups_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Shortcut for RoleAssignmentManager Mock
        self.role_assignments_mock = self.app.client_manager.identity.\
            role_assignments
        self.role_assignments_mock.reset_mock()


class TestUserCreate(TestUser):

    domain = identity_fakes.FakeDomain.create_one_domain()
    project = identity_fakes.FakeProject.create_one_project()

    columns = (
        'default_project_id',
        'domain_id',
        'email',
        'enabled',
        'id',
        'name',
    )

    def setUp(self):
        super(TestUserCreate, self).setUp()

        self.user = identity_fakes.FakeUser.create_one_user(
            attrs={'domain_id': self.domain.id,
                   'default_project_id': self.project.id}
        )
        self.datalist = (
            self.project.id,
            self.domain.id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
        )

        self.domains_mock.get.return_value = self.domain
        self.projects_mock.get.return_value = self.project
        self.users_mock.create.return_value = self.user

        # Get the command object to test
        self.cmd = user.CreateUser(self.app, None)

    def test_user_create_no_options(self):
        arglist = [
            self.user.name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': True,
            'password': None,
        }

        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_password(self):
        arglist = [
            '--password', 'secret',
            self.user.name,
        ]
        verifylist = [
            ('password', 'secret'),
            ('password_prompt', False),
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': True,
            'password': 'secret',
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_password_prompt(self):
        arglist = [
            '--password-prompt',
            self.user.name,
        ]
        verifylist = [
            ('password', None),
            ('password_prompt', True),
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
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
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': True,
            'password': 'abc123',
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_email(self):
        arglist = [
            '--email', 'barney@example.com',
            self.user.name,
        ]
        verifylist = [
            ('email', 'barney@example.com'),
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': None,
            'email': 'barney@example.com',
            'enabled': True,
            'password': None,
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_project(self):
        arglist = [
            '--project', self.project.name,
            self.user.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': self.project.id,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': True,
            'password': None,
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            self.project.id,
            self.domain.id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
        )
        self.assertEqual(datalist, data)

    def test_user_create_project_domain(self):
        arglist = [
            '--project', self.project.name,
            '--project-domain', self.project.domain_id,
            self.user.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('project_domain', self.project.domain_id),
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': self.project.id,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': True,
            'password': None,
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            self.project.id,
            self.domain.id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
        )
        self.assertEqual(datalist, data)

    def test_user_create_domain(self):
        arglist = [
            '--domain', self.domain.name,
            self.user.name,
        ]
        verifylist = [
            ('domain', self.domain.name),
            ('enable', False),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': self.domain.id,
            'email': None,
            'enabled': True,
            'password': None,
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_enable(self):
        arglist = [
            '--enable',
            self.user.name,
        ]
        verifylist = [
            ('enable', True),
            ('disable', False),
            ('name', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': True,
            'password': None,
        }
        # UserManager.create(name=, domain=, project=, password=, email=,
        #   description=, enabled=, default_project=)
        self.users_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_disable(self):
        arglist = [
            '--disable',
            self.user.name,
        ]
        verifylist = [
            ('name', self.user.name),
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
            'name': self.user.name,
            'default_project': None,
            'description': None,
            'domain': None,
            'email': None,
            'enabled': False,
            'password': None,
        }
        # users.create(name=, password, email, tenant_id=None, enabled=True)
        self.users_mock.create.assert_called_with(
            **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestUserDelete(TestUser):

    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super(TestUserDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.users_mock.get.return_value = self.user
        self.users_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = user.DeleteUser(self.app, None)

    def test_user_delete_no_options(self):
        arglist = [
            self.user.id,
        ]
        verifylist = [
            ('users', [self.user.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.users_mock.delete.assert_called_with(
            self.user.id,
        )
        self.assertIsNone(result)


class TestUserList(TestUser):

    domain = identity_fakes.FakeDomain.create_one_domain()
    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user(
        attrs={'domain_id': domain.id,
               'default_project_id': project.id}
    )
    group = identity_fakes.FakeGroup.create_one_group()
    role_assignment = (
        identity_fakes.FakeRoleAssignment.create_one_role_assignment(
            attrs={'user': {'id': user.id}}))

    columns = [
        'ID',
        'Name'
    ]
    datalist = (
        (
            user.id,
            user.name,
        ),
    )

    def setUp(self):
        super(TestUserList, self).setUp()

        self.users_mock.get.return_value = self.user
        self.users_mock.list.return_value = [self.user]
        self.domains_mock.get.return_value = self.domain
        self.groups_mock.get.return_value = self.group
        self.projects_mock.get.return_value = self.project
        self.role_assignments_mock.list.return_value = [self.role_assignment]

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

        # Set expected values
        kwargs = {
            'domain': None,
            'group': None,
        }

        self.users_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_user_list_domain(self):
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
            'group': None,
        }

        self.users_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_user_list_group(self):
        arglist = [
            '--group', self.group.name,
        ]
        verifylist = [
            ('group', self.group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': None,
            'group': self.group.id,
        }

        self.users_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

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

        # Set expected values
        kwargs = {
            'domain': None,
            'group': None,
        }

        self.users_mock.list.assert_called_with(
            **kwargs
        )

        collist = [
            'ID',
            'Name',
            'Project',
            'Domain',
            'Description',
            'Email',
            'Enabled',
        ]
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.user.id,
                self.user.name,
                self.project.id,
                self.domain.id,
                '',
                self.user.email,
                True,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_user_list_project(self):
        arglist = [
            '--project', self.project.name,
        ]
        verifylist = [
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'project': self.project.id,
        }

        self.role_assignments_mock.list.assert_called_with(**kwargs)
        self.users_mock.get.assert_called_with(self.user.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestUserSet(TestUser):

    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user(
        attrs={'default_project_id': project.id}
    )

    def setUp(self):
        super(TestUserSet, self).setUp()

        self.projects_mock.get.return_value = self.project
        self.users_mock.get.return_value = self.user
        self.users_mock.update.return_value = self.user

        # Get the command object to test
        self.cmd = user.SetUser(self.app, None)

    def test_user_set_no_options(self):
        arglist = [
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_user_set_name(self):
        arglist = [
            '--name', 'qwerty',
            self.user.name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'name': 'qwerty',
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_password(self):
        arglist = [
            '--password', 'secret',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', 'secret'),
            ('password_prompt', False),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'password': 'secret',
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_password_prompt(self):
        arglist = [
            '--password-prompt',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('password_prompt', True),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = 'abc123'
        with mock.patch("osc_lib.utils.get_password", mocker):
            result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'password': 'abc123',
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_email(self):
        arglist = [
            '--email', 'barney@example.com',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', 'barney@example.com'),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'email': 'barney@example.com',
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_project(self):
        arglist = [
            '--project', self.project.id,
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', self.project.id),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'default_project': self.project.id,
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_project_domain(self):
        arglist = [
            '--project', self.project.id,
            '--project-domain', self.project.domain_id,
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', self.project.id),
            ('project_domain', self.project.domain_id),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'default_project': self.project.id,
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_enable(self):
        arglist = [
            '--enable',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', True),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_disable(self):
        arglist = [
            '--disable',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', True),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        # UserManager.update(user, name=, domain=, project=, password=,
        #     email=, description=, enabled=, default_project=)
        self.users_mock.update.assert_called_with(
            self.user.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestUserSetPassword(TestUser):

    def setUp(self):
        super(TestUserSetPassword, self).setUp()
        self.cmd = user.SetPasswordUser(self.app, None)

    @staticmethod
    @contextlib.contextmanager
    def _mock_get_password(*passwords):
        mocker = mock.Mock(side_effect=passwords)
        with mock.patch("osc_lib.utils.get_password", mocker):
            yield

    def test_user_password_change(self):
        current_pass = 'old_pass'
        new_pass = 'new_pass'
        arglist = [
            '--password', new_pass,
        ]
        verifylist = [
            ('password', new_pass),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Mock getting user current password.
        with self._mock_get_password(current_pass):
            result = self.cmd.take_action(parsed_args)

        self.users_mock.update_password.assert_called_with(
            current_pass, new_pass
        )
        self.assertIsNone(result)

    def test_user_create_password_prompt(self):
        current_pass = 'old_pass'
        new_pass = 'new_pass'
        parsed_args = self.check_parser(self.cmd, [], [])

        # Mock getting user current and new password.
        with self._mock_get_password(current_pass, new_pass):
            result = self.cmd.take_action(parsed_args)

        self.users_mock.update_password.assert_called_with(
            current_pass, new_pass
        )
        self.assertIsNone(result)

    def test_user_password_change_no_prompt(self):
        current_pass = 'old_pass'
        new_pass = 'new_pass'
        arglist = [
            '--password', new_pass,
            '--original-password', current_pass,
        ]
        verifylist = [
            ('password', new_pass),
            ('original_password', current_pass),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.users_mock.update_password.assert_called_with(
            current_pass, new_pass
        )
        self.assertIsNone(result)


class TestUserShow(TestUser):

    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super(TestUserShow, self).setUp()

        self.users_mock.get.return_value = self.user

        # Get the command object to test
        self.cmd = user.ShowUser(self.app, None)
        self.app.client_manager.identity.auth.client.get_user_id.\
            return_value = self.user.id
        self.app.client_manager.identity.tokens.get_token_data.return_value = \
            {'token':
             {'user':
              {'domain': {},
               'id': self.user.id,
               'name': self.user.name,
               }
              }
             }

    def test_user_show(self):
        arglist = [
            self.user.id,
        ]
        verifylist = [
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.users_mock.get.assert_called_with(self.user.id)

        collist = ('default_project_id', 'domain_id', 'email',
                   'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            self.user.default_project_id,
            self.user.domain_id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
        )
        self.assertEqual(datalist, data)
