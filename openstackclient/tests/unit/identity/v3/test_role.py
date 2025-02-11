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

from osc_lib import exceptions

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import group as _group
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import role as _role
from openstack.identity.v3 import system as _system
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes

from openstackclient.identity.v3 import role
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as test_utils


class TestRoleInherited(identity_fakes.TestIdentityv3):
    def _is_inheritance_testcase(self):
        return True


class TestFindSDKId(test_utils.TestCase):
    def setUp(self):
        super().setUp()
        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.identity_sdk_client = mock.Mock()
        self.identity_sdk_client.find_user = mock.Mock()

    def test_find_sdk_id_validate(self):
        self.identity_sdk_client.find_user.side_effect = [self.user]

        result = role._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=True,
        )
        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_no_validate(self):
        self.identity_sdk_client.find_user.side_effect = [self.user]

        result = role._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=False,
        )
        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_not_found_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        self.assertRaises(
            exceptions.CommandError,
            role._find_sdk_id,
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=True,
        )

    def test_find_sdk_id_not_found_no_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        result = role._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=False,
        )
        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_forbidden_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ForbiddenException,
        ]

        result = role._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=True,
        )

        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_forbidden_no_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ForbiddenException,
        ]

        result = role._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=False,
        )

        self.assertEqual(self.user.id, result)


class TestRoleAdd(identity_fakes.TestIdentityv3):
    def _is_inheritance_testcase(self):
        return False

    user = sdk_fakes.generate_fake_resource(_user.User)
    group = sdk_fakes.generate_fake_resource(_group.Group)
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)
    project = sdk_fakes.generate_fake_resource(_project.Project)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_project.return_value = self.project

        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )

        self.identity_sdk_client.assign_domain_role_to_user.return_value = (
            self.role
        )
        self.identity_sdk_client.assign_domain_role_to_group.return_value = (
            self.role
        )
        self.identity_sdk_client.assign_project_role_to_user.return_value = (
            self.role
        )
        self.identity_sdk_client.assign_project_role_to_group.return_value = (
            self.role
        )
        self.identity_sdk_client.assign_system_role_to_user.return_value = (
            self.role
        )
        self.identity_sdk_client.assign_system_role_to_group.return_value = (
            self.role
        )

        # Get the command object to test
        self.cmd = role.AddRole(self.app, None)

    @mock.patch.object(role.LOG, 'warning')
    def test_role_add_user_system(self, mock_warning):
        arglist = [
            '--user',
            self.user.name,
            '--system',
            'all',
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('system', 'all'),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'system': 'all',
            'user': self.user.id,
            'role': self.role.id,
        }
        self.identity_sdk_client.assign_system_role_to_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

        if self._is_inheritance_testcase():
            mock_warning.assert_called_with(
                "'--inherited' was given, which is not supported when adding a system role; this will be an error in a future release"
            )

    def test_role_add_user_domain(self):
        arglist = [
            '--user',
            self.user.name,
            '--domain',
            self.domain.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': self.domain.id,
            'user': self.user.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.assign_domain_role_to_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_add_user_project(self):
        arglist = [
            '--user',
            self.user.name,
            '--project',
            self.project.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'project': self.project.id,
            'user': self.user.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.assign_project_role_to_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    @mock.patch.object(role.LOG, 'warning')
    def test_role_add_group_system(self, mock_warning):
        arglist = [
            '--group',
            self.group.name,
            '--system',
            'all',
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('system', 'all'),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'system': 'all',
            'group': self.group.id,
            'role': self.role.id,
        }
        self.identity_sdk_client.assign_system_role_to_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

        if self._is_inheritance_testcase():
            mock_warning.assert_called_with(
                "'--inherited' was given, which is not supported when adding a system role; this will be an error in a future release"
            )

    def test_role_add_group_domain(self):
        arglist = [
            '--group',
            self.group.name,
            '--domain',
            self.domain.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain': self.domain.id,
            'group': self.group.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.assign_domain_role_to_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_add_group_project(self):
        arglist = [
            '--group',
            self.group.name,
            '--project',
            self.project.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'project': self.project.id,
            'group': self.group.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.assign_project_role_to_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_add_domain_role_on_user_project(self):
        self.identity_sdk_client.find_role.return_value = self.role_with_domain

        arglist = [
            '--user',
            self.user.name,
            '--project',
            self.project.name,
            '--role-domain',
            self.domain.name,
            self.role_with_domain.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role_with_domain.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'project': self.project.id,
            'user': self.user.id,
            'role': self.role_with_domain.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.assign_project_role_to_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_add_with_error(self):
        arglist = [
            self.role.name,
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestRoleAddInherited(TestRoleAdd, TestRoleInherited):
    pass


class TestRoleCreate(identity_fakes.TestIdentityv3):
    collist = ('id', 'name', 'domain_id', 'description')
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )
        self.role_with_description = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description='role description',
        )
        self.role_with_immutable_option = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
            options={'immutable': True},
        )
        self.identity_sdk_client.find_domain.return_value = self.domain

        # Get the command object to test
        self.cmd = role.CreateRole(self.app, None)

    def test_role_create_no_options(self):
        self.identity_sdk_client.create_role.return_value = self.role

        arglist = [
            self.role.name,
        ]
        verifylist = [
            ('name', self.role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.role.name,
            'options': {},
        }

        self.identity_sdk_client.create_role.assert_called_with(**kwargs)

        self.assertEqual(self.collist, columns)
        datalist = (
            self.role.id,
            self.role.name,
            None,
            None,
        )
        self.assertEqual(datalist, data)

    def test_role_create_with_domain(self):
        self.identity_sdk_client.create_role.return_value = (
            self.role_with_domain
        )

        arglist = [
            '--domain',
            self.domain.name,
            self.role_with_domain.name,
        ]
        verifylist = [
            ('domain', self.domain.name),
            ('name', self.role_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'domain_id': self.domain.id,
            'name': self.role_with_domain.name,
            'options': {},
        }

        self.identity_sdk_client.create_role.assert_called_with(**kwargs)

        self.assertEqual(self.collist, columns)
        datalist = (
            self.role_with_domain.id,
            self.role_with_domain.name,
            self.domain.id,
            None,
        )
        self.assertEqual(datalist, data)

    def test_role_create_with_description(self):
        self.identity_sdk_client.create_role.return_value = (
            self.role_with_description
        )

        arglist = [
            '--description',
            self.role_with_description.description,
            self.role_with_description.name,
        ]
        verifylist = [
            ('description', self.role_with_description.description),
            ('name', self.role_with_description.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.role_with_description.name,
            'description': self.role_with_description.description,
            'options': {},
        }

        self.identity_sdk_client.create_role.assert_called_with(**kwargs)

        self.assertEqual(self.collist, columns)
        datalist = (
            self.role_with_description.id,
            self.role_with_description.name,
            None,
            self.role_with_description.description,
        )
        self.assertEqual(datalist, data)

    def test_role_create_with_immutable_option(self):
        self.identity_sdk_client.create_role.return_value = self.role

        arglist = [
            '--immutable',
            self.role.name,
        ]
        verifylist = [
            ('immutable', True),
            ('name', self.role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'options': {'immutable': True},
            'name': self.role.name,
        }

        self.identity_sdk_client.create_role.assert_called_with(**kwargs)

        self.assertEqual(self.collist, columns)
        datalist = (
            self.role.id,
            self.role.name,
            None,
            None,
        )
        self.assertEqual(datalist, data)

    def test_role_create_with_no_immutable_option(self):
        self.identity_sdk_client.create_role.return_value = self.role

        arglist = [
            '--no-immutable',
            self.role.name,
        ]
        verifylist = [
            ('no_immutable', True),
            ('name', self.role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'options': {'immutable': False},
            'name': self.role.name,
        }

        self.identity_sdk_client.create_role.assert_called_with(**kwargs)

        self.assertEqual(self.collist, columns)
        datalist = (
            self.role.id,
            self.role.name,
            None,
            None,
        )
        self.assertEqual(datalist, data)


class TestRoleDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = role.DeleteRole(self.app, None)

    def test_role_delete_no_options(self):
        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role
        self.identity_sdk_client.delete_role.return_value = None

        arglist = [
            self.role.name,
        ]
        verifylist = [
            ('roles', [self.role.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_role.assert_called_with(
            role=self.role.id,
            ignore_missing=False,
        )
        self.assertIsNone(result)

    def test_role_delete_with_domain(self):
        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role_with_domain
        self.identity_sdk_client.delete_role.return_value = None

        arglist = [
            '--domain',
            self.domain.name,
            self.role_with_domain.name,
        ]
        verifylist = [
            ('roles', [self.role_with_domain.name]),
            ('domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_role.assert_called_with(
            role=self.role_with_domain.id,
            ignore_missing=False,
        )
        self.assertIsNone(result)

    def test_delete_multi_roles_with_exception(self):
        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.identity_sdk_client.find_role.side_effect = [
            self.role,
            sdk_exc.ResourceNotFound,
        ]
        arglist = [
            self.role.id,
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
            self.assertEqual('1 of 2 roles failed to delete.', str(e))

        self.identity_sdk_client.find_role.assert_has_calls(
            [
                mock.call(
                    name_or_id=self.role.id,
                    ignore_missing=False,
                    domain_id=None,
                ),
                mock.call(
                    name_or_id='unexist_role',
                    ignore_missing=False,
                    domain_id=None,
                ),
            ]
        )

        self.assertEqual(2, self.identity_sdk_client.find_role.call_count)
        self.identity_sdk_client.delete_role.assert_called_once_with(
            role=self.role.id, ignore_missing=False
        )


class TestRoleList(identity_fakes.TestIdentityv3):
    columns = (
        'ID',
        'Name',
    )
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )
        self.identity_sdk_client.roles.return_value = [
            self.role,
            self.role_with_domain,
        ]
        self.identity_sdk_client.find_domain.return_value = self.domain

        self.datalist = (
            (
                self.role.id,
                self.role.name,
            ),
            (
                self.role_with_domain.id,
                self.role_with_domain.name,
            ),
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

        self.identity_sdk_client.roles.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_role_list_domain_role(self):
        self.identity_sdk_client.roles.return_value = [self.role_with_domain]
        arglist = [
            '--domain',
            self.domain.name,
        ]
        verifylist = [
            ('domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {'domain_id': self.domain.id}
        self.identity_sdk_client.roles.assert_called_with(**kwargs)

        collist = ('ID', 'Name', 'Domain')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.role_with_domain.id,
                self.role_with_domain.name,
                self.domain.name,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestRoleRemove(identity_fakes.TestIdentityv3):
    def _is_inheritance_testcase(self):
        return False

    user = sdk_fakes.generate_fake_resource(_user.User)
    group = sdk_fakes.generate_fake_resource(_group.Group)
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)
    project = sdk_fakes.generate_fake_resource(_project.Project)
    system = sdk_fakes.generate_fake_resource(_system.System)

    def setUp(self):
        super().setUp()

        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role
        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_project.return_value = self.project

        self.identity_sdk_client.unassign_domain_role_from_user.return_value = None
        self.identity_sdk_client.unassign_domain_role_from_group.return_value = None
        self.identity_sdk_client.unassign_project_role_from_user.return_value = None
        self.identity_sdk_client.unassign_project_role_from_group.return_value = None
        self.identity_sdk_client.unassign_system_role_from_user.return_value = None
        self.identity_sdk_client.unassign_system_role_from_group.return_value = None

        # Get the command object to test
        self.cmd = role.RemoveRole(self.app, None)

    def test_role_remove_user_system(self):
        arglist = [
            '--user',
            self.user.name,
            '--system',
            'all',
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('system', 'all'),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': self.user.id,
            'system': 'all',
            'role': self.role.id,
        }
        self.identity_sdk_client.unassign_system_role_from_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_non_existent_user_system(self):
        # Simulate the user not being in keystone; the client should gracefully
        # handle this exception and send the request to remove the role since
        # keystone supports removing role assignments with non-existent actors
        # (e.g., users or groups).
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]
        arglist = [
            '--user',
            self.user.id,
            '--system',
            'all',
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.id),
            ('group', None),
            ('system', 'all'),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': self.user.id,
            'system': 'all',
            'role': self.role.id,
        }
        self.identity_sdk_client.unassign_system_role_from_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_user_domain(self):
        arglist = [
            '--user',
            self.user.name,
            '--domain',
            self.domain.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': self.user.id,
            'domain': self.domain.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_domain_role_from_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_non_existent_user_domain(self):
        # Simulate the user not being in keystone, the client the gracefully
        # handle this exception and send the request to remove the role since
        # keystone will validate.
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]
        arglist = [
            '--user',
            self.user.id,
            '--domain',
            self.domain.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.id),
            ('group', None),
            ('system', None),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': self.user.id,
            'domain': self.domain.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_domain_role_from_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_user_project(self):
        arglist = [
            '--user',
            self.user.name,
            '--project',
            self.project.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.name),
            ('group', None),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': self.user.id,
            'project': self.project.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_project_role_from_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_non_existent_user_project(self):
        # Simulate the user not being in keystone, the client the gracefully
        # handle this exception and send the request to remove the role since
        # keystone will validate.
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        arglist = [
            '--user',
            self.user.id,
            '--project',
            self.project.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', self.user.id),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'user': self.user.id,
            'project': self.project.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_project_role_from_user.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_group_system(self):
        arglist = [
            '--group',
            self.group.name,
            '--system',
            'all',
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('system', 'all'),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'system': 'all',
            'role': self.role.id,
        }
        self.identity_sdk_client.unassign_system_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_non_existent_group_system(self):
        # Simulate the user not being in keystone, the client the gracefully
        # handle this exception and send the request to remove the role since
        # keystone will validate.
        self.identity_sdk_client.find_group.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        arglist = [
            '--group',
            self.group.id,
            '--system',
            'all',
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.id),
            ('system', 'all'),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'system': 'all',
            'role': self.role.id,
        }
        self.identity_sdk_client.unassign_system_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_group_domain(self):
        arglist = [
            '--group',
            self.group.name,
            '--domain',
            self.domain.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'domain': self.domain.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_domain_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_non_existent_group_domain(self):
        # Simulate the user not being in keystone, the client the gracefully
        # handle this exception and send the request to remove the role since
        # keystone will validate.
        self.identity_sdk_client.find_group.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        arglist = [
            '--group',
            self.group.id,
            '--domain',
            self.domain.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.id),
            ('system', None),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'domain': self.domain.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_domain_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_group_project(self):
        arglist = [
            '--group',
            self.group.name,
            '--project',
            self.project.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'project': self.project.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_project_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_non_existent_group_project(self):
        # Simulate the user not being in keystone, the client the gracefully
        # handle this exception and send the request to remove the role since
        # keystone will validate.
        self.identity_sdk_client.find_group.side_effect = [
            sdk_exc.ResourceNotFound,
        ]
        arglist = [
            '--group',
            self.group.id,
            '--project',
            self.project.name,
            self.role.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.id),
            ('system', None),
            ('domain', None),
            ('project', self.project.name),
            ('role', self.role.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'project': self.project.id,
            'role': self.role.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_project_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_domain_role_on_group_domain(self):
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role_with_domain
        arglist = [
            '--group',
            self.group.name,
            '--domain',
            self.domain.name,
            self.role_with_domain.name,
        ]
        if self._is_inheritance_testcase():
            arglist.append('--inherited')
        verifylist = [
            ('user', None),
            ('group', self.group.name),
            ('domain', self.domain.name),
            ('project', None),
            ('role', self.role_with_domain.name),
            ('inherited', self._is_inheritance_testcase()),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'group': self.group.id,
            'domain': self.domain.id,
            'role': self.role_with_domain.id,
            'inherited': self._is_inheritance_testcase(),
        }
        self.identity_sdk_client.unassign_domain_role_from_group.assert_called_with(
            **kwargs
        )
        self.assertIsNone(result)

    def test_role_remove_with_error(self):
        arglist = [
            self.role.name,
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('domain', None),
            ('project', None),
            ('role', self.role.name),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestRoleSet(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )

        # Get the command object to test
        self.cmd = role.SetRole(self.app, None)

    def test_role_set_no_options(self):
        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role
        self.identity_sdk_client.update_role.return_value = self.role

        arglist = [
            '--name',
            'over',
            self.role.name,
        ]
        verifylist = [
            ('name', 'over'),
            ('role', self.role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
            'role': self.role.id,
            'options': {},
        }
        self.identity_sdk_client.update_role.assert_called_with(**kwargs)
        self.assertIsNone(result)

    def test_role_set_domain_role(self):
        self.domain2 = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.identity_sdk_client.find_domain.return_value = self.domain2

        self.identity_sdk_client.find_role.return_value = self.role_with_domain
        self.identity_sdk_client.update_role.return_value = (
            self.role_with_domain
        )

        arglist = [
            '--name',
            'over',
            '--domain',
            self.domain2.name,
            self.role_with_domain.name,
        ]
        verifylist = [
            ('name', 'over'),
            ('domain', self.domain2.name),
            ('role', self.role_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
            'role': self.role_with_domain.id,
            'domain_id': self.domain2.id,
            'options': {},
        }
        self.identity_sdk_client.update_role.assert_called_with(**kwargs)
        self.assertIsNone(result)

    def test_role_set_description(self):
        self.identity_sdk_client.find_role.return_value = self.role_with_domain

        arglist = [
            '--name',
            'over',
            '--description',
            'role description',
            self.role_with_domain.name,
        ]
        verifylist = [
            ('name', 'over'),
            ('description', 'role description'),
            ('role', self.role_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
            'description': 'role description',
            'role': self.role_with_domain.id,
            'options': {},
        }
        self.identity_sdk_client.update_role.assert_called_with(**kwargs)
        self.assertIsNone(result)

    def test_role_set_with_immutable(self):
        self.identity_sdk_client.find_role.return_value = self.role_with_domain

        arglist = [
            '--name',
            'over',
            '--immutable',
            self.role_with_domain.name,
        ]
        verifylist = [
            ('name', 'over'),
            ('immutable', True),
            ('role', self.role_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
            'role': self.role_with_domain.id,
            'options': {'immutable': True},
        }
        self.identity_sdk_client.update_role.assert_called_with(**kwargs)
        self.assertIsNone(result)

    def test_role_set_with_no_immutable(self):
        self.identity_sdk_client.find_role.return_value = self.role_with_domain

        arglist = [
            '--name',
            'over',
            '--no-immutable',
            self.role_with_domain.name,
        ]
        verifylist = [
            ('name', 'over'),
            ('no_immutable', True),
            ('role', self.role_with_domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'over',
            'role': self.role_with_domain.id,
            'options': {'immutable': False},
        }
        self.identity_sdk_client.update_role.assert_called_with(**kwargs)
        self.assertIsNone(result)


class TestRoleShow(identity_fakes.TestIdentityv3):
    domain = sdk_fakes.generate_fake_resource(_domain.Domain)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_domain.return_value = self.domain

        # Get the command object to test
        self.cmd = role.ShowRole(self.app, None)

    def test_role_show(self):
        self.role = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=None,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role

        arglist = [
            self.role.name,
        ]
        verifylist = [
            ('role', self.role.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_role.assert_called_with(
            name_or_id=self.role.name,
            domain_id=None,
            ignore_missing=False,
        )

        collist = ('id', 'name', 'domain_id', 'description')
        self.assertEqual(collist, columns)
        datalist = (
            self.role.id,
            self.role.name,
            None,
            None,
        )
        self.assertEqual(datalist, data)

    def test_role_show_domain_role(self):
        self.role_with_domain = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=self.domain.id,
            description=None,
        )
        self.identity_sdk_client.find_role.return_value = self.role_with_domain

        arglist = [
            '--domain',
            self.domain.name,
            self.role_with_domain.id,
        ]
        verifylist = [
            ('domain', self.domain.name),
            ('role', self.role_with_domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_role.assert_called_with(
            name_or_id=self.role_with_domain.id,
            domain_id=self.domain.id,
            ignore_missing=False,
        )

        collist = ('id', 'name', 'domain_id', 'description')
        self.assertEqual(collist, columns)
        datalist = (
            self.role_with_domain.id,
            self.role_with_domain.name,
            self.domain.id,
            None,
        )
        self.assertEqual(datalist, data)
