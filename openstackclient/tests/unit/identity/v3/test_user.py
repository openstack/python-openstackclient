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
from unittest import mock

from osc_lib import exceptions

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import group as _group
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import role_assignment as _role_assignment
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes

from openstackclient.identity import common
from openstackclient.identity.v3 import user
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestUserCreate(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)
    project = sdk_fakes.generate_fake_resource(_project.Project)

    columns = (
        'default_project_id',
        'domain_id',
        'email',
        'enabled',
        'id',
        'name',
        'description',
        'password_expires_at',
    )

    def setUp(self):
        super().setUp()

        self.user = sdk_fakes.generate_fake_resource(
            resource_type=_user.User,
            domain_id=self.domain.id,
            default_project_id=self.project.id,
        )
        self.datalist = (
            self.project.id,
            self.domain.id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
            self.user.description,
            self.user.password_expires_at,
        )

        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.create_user.return_value = self.user

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
            'is_enabled': True,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_password(self):
        arglist = [
            '--password',
            'secret',
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
            'is_enabled': True,
            'password': 'secret',
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

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
            'is_enabled': True,
            'password': 'abc123',
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_email(self):
        arglist = [
            '--email',
            'barney@example.com',
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
            'email': 'barney@example.com',
            'is_enabled': True,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_project(self):
        arglist = [
            '--project',
            self.project.name,
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
            'default_project_id': self.project.id,
            'is_enabled': True,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            self.project.id,
            self.domain.id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
            self.user.description,
            self.user.password_expires_at,
        )
        self.assertEqual(datalist, data)

    def test_user_create_project_domain(self):
        arglist = [
            '--project',
            self.project.name,
            '--project-domain',
            self.project.domain_id,
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
            'default_project_id': self.project.id,
            'is_enabled': True,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_once_with(**kwargs)
        self.identity_sdk_client.find_domain.assert_called_once_with(
            self.project.domain_id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            self.project.id,
            self.domain.id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
            self.user.description,
            self.user.password_expires_at,
        )
        self.assertEqual(datalist, data)

    def test_user_create_domain(self):
        arglist = [
            '--domain',
            self.domain.name,
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
            'domain_id': self.domain.id,
            'is_enabled': True,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

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
            'is_enabled': True,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

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
            'is_enabled': False,
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_ignore_lockout_failure_attempts(self):
        arglist = [
            '--ignore-lockout-failure-attempts',
            self.user.name,
        ]
        verifylist = [
            ('ignore_lockout_failure_attempts', True),
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
            'is_enabled': True,
            'options': {'ignore_lockout_failure_attempts': True},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_no_ignore_lockout_failure_attempts(self):
        arglist = [
            '--no-ignore-lockout-failure-attempts',
            self.user.name,
        ]
        verifylist = [
            ('no_ignore_lockout_failure_attempts', True),
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
            'is_enabled': True,
            'options': {'ignore_lockout_failure_attempts': False},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_ignore_password_expiry(self):
        arglist = [
            '--ignore-password-expiry',
            self.user.name,
        ]
        verifylist = [
            ('ignore_password_expiry', True),
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
            'is_enabled': True,
            'options': {'ignore_password_expiry': True},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_no_ignore_password_expiry(self):
        arglist = [
            '--no-ignore-password-expiry',
            self.user.name,
        ]
        verifylist = [
            ('no_ignore_password_expiry', True),
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
            'is_enabled': True,
            'options': {'ignore_password_expiry': False},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_ignore_change_password_upon_first_use(self):
        arglist = [
            '--ignore-change-password-upon-first-use',
            self.user.name,
        ]
        verifylist = [
            ('ignore_change_password_upon_first_use', True),
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
            'is_enabled': True,
            'options': {'ignore_change_password_upon_first_use': True},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_no_ignore_change_password_upon_first_use(self):
        arglist = [
            '--no-ignore-change-password-upon-first-use',
            self.user.name,
        ]
        verifylist = [
            ('no_ignore_change_password_upon_first_use', True),
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
            'is_enabled': True,
            'options': {'ignore_change_password_upon_first_use': False},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_enables_lock_password(self):
        arglist = [
            '--enable-lock-password',
            self.user.name,
        ]
        verifylist = [
            ('enable_lock_password', True),
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
            'is_enabled': True,
            'options': {'lock_password': True},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_disables_lock_password(self):
        arglist = [
            '--disable-lock-password',
            self.user.name,
        ]
        verifylist = [
            ('disable_lock_password', True),
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
            'is_enabled': True,
            'options': {'lock_password': False},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_enable_multi_factor_auth(self):
        arglist = [
            '--enable-multi-factor-auth',
            self.user.name,
        ]
        verifylist = [
            ('enable_multi_factor_auth', True),
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
            'is_enabled': True,
            'options': {'multi_factor_auth_enabled': True},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_disable_multi_factor_auth(self):
        arglist = [
            '--disable-multi-factor-auth',
            self.user.name,
        ]
        verifylist = [
            ('disable_multi_factor_auth', True),
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
            'is_enabled': True,
            'options': {'multi_factor_auth_enabled': False},
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_option_with_multi_factor_auth_rule(self):
        arglist = [
            '--multi-factor-auth-rule',
            identity_fakes.mfa_opt1,
            '--multi-factor-auth-rule',
            identity_fakes.mfa_opt2,
            self.user.name,
        ]
        verifylist = [
            (
                'multi_factor_auth_rule',
                [identity_fakes.mfa_opt1, identity_fakes.mfa_opt2],
            ),
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
            'is_enabled': True,
            'options': {
                'multi_factor_auth_rules': [["password", "totp"], ["password"]]
            },
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_user_create_with_multiple_options(self):
        arglist = [
            '--ignore-password-expiry',
            '--disable-multi-factor-auth',
            '--multi-factor-auth-rule',
            identity_fakes.mfa_opt1,
            self.user.name,
        ]
        verifylist = [
            ('ignore_password_expiry', True),
            ('disable_multi_factor_auth', True),
            ('multi_factor_auth_rule', [identity_fakes.mfa_opt1]),
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
            'is_enabled': True,
            'options': {
                'ignore_password_expiry': True,
                'multi_factor_auth_enabled': False,
                'multi_factor_auth_rules': [["password", "totp"]],
            },
            'password': None,
        }
        self.identity_sdk_client.create_user.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestUserDelete(identity_fakes.TestIdentityv3):
    user = sdk_fakes.generate_fake_resource(_user.User)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.delete_user.return_value = None

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

        self.identity_sdk_client.delete_user.assert_called_with(
            self.user.id,
            ignore_missing=False,
        )
        self.assertIsNone(result)

    @mock.patch.object(_user.User, 'find')
    def test_delete_multi_users_with_exception(self, find_mock):
        self.identity_sdk_client.find_user.side_effect = [
            self.user,
            sdk_exc.ResourceNotFound,
        ]
        arglist = [
            self.user.id,
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

        self.identity_sdk_client.find_user.assert_has_calls(
            [
                mock.call(name_or_id=self.user.id, ignore_missing=False),
                mock.call(name_or_id='unexist_user', ignore_missing=False),
            ]
        )

        self.assertEqual(2, self.identity_sdk_client.find_user.call_count)
        self.identity_sdk_client.delete_user.assert_called_once_with(
            self.user.id, ignore_missing=False
        )


class TestUserList(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)
    project = sdk_fakes.generate_fake_resource(_project.Project)
    user = sdk_fakes.generate_fake_resource(
        resource_type=_user.User,
        domain_id=domain.id,
        default_project_id=project.id,
    )
    group = sdk_fakes.generate_fake_resource(_group.Group)
    role_assignment = sdk_fakes.generate_fake_resource(
        resource_type=_role_assignment.RoleAssignment, user={'id': user.id}
    )

    columns = ['ID', 'Name']
    datalist = (
        (
            user.id,
            user.name,
        ),
    )

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.users.return_value = [self.user]
        self.identity_sdk_client.group_users.return_value = [self.user]
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.role_assignments_filter.return_value = [
            self.role_assignment
        ]

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
            'domain_id': None,
        }

        self.identity_sdk_client.users.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_user_list_domain(self):
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
            'domain_id': self.domain.id,
        }

        self.identity_sdk_client.users.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_user_list_group(self):
        arglist = [
            '--group',
            self.group.name,
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
            'domain_id': None,
            'group': self.group.id,
        }

        self.identity_sdk_client.group_users.assert_called_with(**kwargs)

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
            'domain_id': None,
        }

        self.identity_sdk_client.users.assert_called_with(**kwargs)

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
                self.user.description,
                self.user.email,
                True,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_user_list_project(self):
        arglist = [
            '--project',
            self.project.name,
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

        self.identity_sdk_client.role_assignments_filter.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestUserSet(identity_fakes.TestIdentityv3):
    project = sdk_fakes.generate_fake_resource(_project.Project)
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)
    user = sdk_fakes.generate_fake_resource(
        resource_type=_user.User, default_project_id=project.id
    )
    user2 = sdk_fakes.generate_fake_resource(
        resource_type=_user.User,
        default_project_id=project.id,
        domain_id=domain.id,
    )

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.update_user.return_value = self.user

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
            '--name',
            'qwerty',
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
            'is_enabled': True,
            'name': 'qwerty',
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_specify_domain(self):
        arglist = [
            '--name',
            'qwerty',
            '--domain',
            self.domain.id,
            self.user2.name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('password', None),
            ('domain', self.domain.id),
            ('email', None),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user2.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {'is_enabled': True, 'name': 'qwerty'}

        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_password(self):
        arglist = [
            '--password',
            'secret',
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
            'is_enabled': True,
            'password': 'secret',
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
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
            'is_enabled': True,
            'password': 'abc123',
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_email(self):
        arglist = [
            '--email',
            'barney@example.com',
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
            'is_enabled': True,
            'email': 'barney@example.com',
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_project(self):
        arglist = [
            '--project',
            self.project.id,
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
            'is_enabled': True,
            'default_project_id': self.project.id,
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.identity_sdk_client.find_domain.assert_not_called()

        # Set expected values
        kwargs = {
            'ignore_missing': False,
            'domain_id': None,
        }
        self.identity_sdk_client.find_project.assert_called_once_with(
            name_or_id=self.project.id, **kwargs
        )

        self.assertIsNone(result)

    def test_user_set_project_domain(self):
        arglist = [
            '--project',
            self.project.id,
            '--project-domain',
            self.project.domain_id,
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
            'is_enabled': True,
            'default_project_id': self.project.id,
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )

        self.identity_sdk_client.find_domain.assert_called_once_with(
            name_or_id=self.project.domain_id, ignore_missing=False
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
            'is_enabled': True,
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
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
            'is_enabled': False,
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_ignore_lockout_failure_attempts(self):
        arglist = [
            '--ignore-lockout-failure-attempts',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('ignore_lockout_failure_attempts', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'ignore_lockout_failure_attempts': True},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_no_ignore_lockout_failure_attempts(self):
        arglist = [
            '--no-ignore-lockout-failure-attempts',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('no_ignore_lockout_failure_attempts', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'ignore_lockout_failure_attempts': False},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_ignore_password_expiry(self):
        arglist = [
            '--ignore-password-expiry',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('ignore_password_expiry', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'ignore_password_expiry': True},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_no_ignore_password_expiry(self):
        arglist = [
            '--no-ignore-password-expiry',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('no_ignore_password_expiry', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'ignore_password_expiry': False},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_ignore_change_password_upon_first_use(self):
        arglist = [
            '--ignore-change-password-upon-first-use',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('ignore_change_password_upon_first_use', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'ignore_change_password_upon_first_use': True},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_no_ignore_change_password_upon_first_use(self):
        arglist = [
            '--no-ignore-change-password-upon-first-use',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('no_ignore_change_password_upon_first_use', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'ignore_change_password_upon_first_use': False},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_enable_lock_password(self):
        arglist = [
            '--enable-lock-password',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('enable_lock_password', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'lock_password': True},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_disable_lock_password(self):
        arglist = [
            '--disable-lock-password',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('disable_lock_password', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'lock_password': False},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_enable_multi_factor_auth(self):
        arglist = [
            '--enable-multi-factor-auth',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('enable_multi_factor_auth', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'multi_factor_auth_enabled': True},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_disable_multi_factor_auth(self):
        arglist = [
            '--disable-multi-factor-auth',
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('disable_multi_factor_auth', True),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'multi_factor_auth_enabled': False},
        }
        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_option_multi_factor_auth_rule(self):
        arglist = [
            '--multi-factor-auth-rule',
            identity_fakes.mfa_opt1,
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('multi_factor_auth_rule', [identity_fakes.mfa_opt1]),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {'multi_factor_auth_rules': [["password", "totp"]]},
        }

        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)

    def test_user_set_with_multiple_options(self):
        arglist = [
            '--ignore-password-expiry',
            '--enable-multi-factor-auth',
            '--multi-factor-auth-rule',
            identity_fakes.mfa_opt1,
            self.user.name,
        ]
        verifylist = [
            ('name', None),
            ('password', None),
            ('email', None),
            ('ignore_password_expiry', True),
            ('enable_multi_factor_auth', True),
            ('multi_factor_auth_rule', [identity_fakes.mfa_opt1]),
            ('project', None),
            ('enable', False),
            ('disable', False),
            ('user', self.user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'is_enabled': True,
            'options': {
                'ignore_password_expiry': True,
                'multi_factor_auth_enabled': True,
                'multi_factor_auth_rules': [["password", "totp"]],
            },
        }

        self.identity_sdk_client.update_user.assert_called_with(
            user=self.user, **kwargs
        )
        self.assertIsNone(result)


class TestUserSetPassword(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()
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
            '--password',
            new_pass,
        ]
        verifylist = [
            ('password', new_pass),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Mock getting user current password.
        with self._mock_get_password(current_pass):
            result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_user.assert_called_with(
            current_password=current_pass, password=new_pass
        )
        self.assertIsNone(result)

    def test_user_create_password_prompt(self):
        current_pass = 'old_pass'
        new_pass = 'new_pass'
        parsed_args = self.check_parser(self.cmd, [], [])

        # Mock getting user current and new password.
        with self._mock_get_password(current_pass, new_pass):
            result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_user.assert_called_with(
            current_password=current_pass, password=new_pass
        )
        self.assertIsNone(result)

    def test_user_password_change_no_prompt(self):
        current_pass = 'old_pass'
        new_pass = 'new_pass'
        arglist = [
            '--password',
            new_pass,
            '--original-password',
            current_pass,
        ]
        verifylist = [
            ('password', new_pass),
            ('original_password', current_pass),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_user.assert_called_with(
            current_password=current_pass, password=new_pass
        )
        self.assertIsNone(result)


class TestUserShow(identity_fakes.TestIdentityv3):
    user = sdk_fakes.generate_fake_resource(_user.User)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_user.return_value = self.user

        # Get the command object to test
        self.cmd = user.ShowUser(self.app, None)
        self.identity_client.auth.client.get_user_id.return_value = (  # noqa: E501
            self.user.id
        )
        self.identity_client.tokens.get_token_data.return_value = {
            'token': {
                'user': {
                    'domain_id': {'id': self.user.domain_id},
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

        self.identity_sdk_client.find_user.assert_called_with(
            name_or_id=self.user.id, ignore_missing=False
        )

        collist = (
            'default_project_id',
            'domain_id',
            'email',
            'enabled',
            'id',
            'name',
            'description',
            'password_expires_at',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.user.default_project_id,
            self.user.domain_id,
            self.user.email,
            True,
            self.user.id,
            self.user.name,
            self.user.description,
            self.user.password_expires_at,
        )
        self.assertEqual(datalist, data)

    def test_user_show_with_domain(self):
        user = sdk_fakes.generate_fake_resource(
            resource_type=_user.User, name=self.user.name
        )

        arglist = [
            "--domain",
            self.user.domain_id,
            user.name,
        ]
        verifylist = [
            ('domain', self.user.domain_id),
            ('user', user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        user_str = common._get_token_resource(
            self.identity_sdk_client,
            'user',
            parsed_args.user,
            parsed_args.domain,
        )
        self.assertEqual(self.user.name, user_str)

        arglist = [
            "--domain",
            user.domain_id,
            user.name,
        ]
        verifylist = [
            ('domain', user.domain_id),
            ('user', user.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        user_str = common._get_token_resource(
            self.identity_sdk_client,
            'user',
            parsed_args.user,
            parsed_args.domain,
        )
        self.assertEqual(user.name, user_str)
