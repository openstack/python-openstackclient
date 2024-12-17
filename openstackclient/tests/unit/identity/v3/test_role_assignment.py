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

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import group as _group
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import role as _role
from openstack.identity.v3 import role_assignment as _role_assignment
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import role_assignment
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRoleAssignmentList(identity_fakes.TestIdentityv3):
    columns = (
        'Role',
        'User',
        'Group',
        'Project',
        'Domain',
        'System',
        'Inherited',
    )

    def setUp(self):
        super().setUp()

        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.group = sdk_fakes.generate_fake_resource(_group.Group)
        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)
        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.role = sdk_fakes.generate_fake_resource(_role.Role)
        self.assignment_with_project_id_and_user_id = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id},
                scope={'project': {'id': self.project.id}},
                user={'id': self.user.id},
            )
        )
        self.assignment_with_project_id_and_group_id = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id},
                scope={'project': {'id': self.project.id}},
                group={'id': self.group.id},
            )
        )
        self.assignment_with_domain_id_and_user_id = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id},
                scope={'domain': {'id': self.domain.id}},
                user={'id': self.user.id},
            )
        )
        self.assignment_with_domain_id_and_group_id = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id},
                scope={'domain': {'id': self.domain.id}},
                group={'id': self.group.id},
            )
        )

        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.find_group.return_value = self.group
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.find_role.return_value = self.role

        # Get the command object to test
        self.cmd = role_assignment.ListRoleAssignment(self.app, None)

    def test_role_assignment_list_no_filters(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_project_id_and_user_id,
            self.assignment_with_project_id_and_group_id,
            self.assignment_with_domain_id_and_user_id,
            self.assignment_with_domain_id_and_group_id,
        ]

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                self.project.id,
                '',
                '',
                False,
            ),
            (
                self.role.id,
                self.user.id,
                '',
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                '',
                self.domain.id,
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_user(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_domain_id_and_user_id,
            self.assignment_with_project_id_and_user_id,
        ]

        arglist = ['--user', self.user.name]
        verifylist = [
            ('user', self.user.name),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_user.assert_called_with(
            name_or_id=self.user.name, ignore_missing=False, domain_id=None
        )
        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=self.user.id,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_user_with_domain(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_domain_id_and_user_id,
            self.assignment_with_project_id_and_user_id,
        ]

        arglist = ['--user', self.user.name, '--user-domain', self.domain.name]
        verifylist = [
            ('user', self.user.name),
            ('user_domain', self.domain.name),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_domain.assert_called_with(
            name_or_id=self.domain.name, ignore_missing=False
        )
        self.identity_sdk_client.find_user.assert_called_with(
            name_or_id=self.user.name,
            ignore_missing=False,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=self.user.id,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    @mock.patch.object(_user.User, 'find')
    def test_role_assignment_list_user_not_found(self, find_mock):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_domain_id_and_user_id,
            self.assignment_with_project_id_and_user_id,
        ]
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ForbiddenException,
            sdk_exc.ForbiddenException,
        ]

        arglist = ['--user', self.user.id]
        verifylist = [
            ('user', self.user.id),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=self.user.id,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_group(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_domain_id_and_group_id,
            self.assignment_with_project_id_and_group_id,
        ]

        arglist = ['--group', self.group.name]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', self.group.name),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_group.assert_called_with(
            name_or_id=self.group.name, ignore_missing=False, domain_id=None
        )
        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=self.group.id,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                '',
                self.group.id,
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_group_with_domain(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_domain_id_and_group_id,
            self.assignment_with_project_id_and_group_id,
        ]

        arglist = [
            '--group',
            self.group.name,
            '--group-domain',
            self.domain.name,
        ]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', self.group.name),
            ('group_domain', self.domain.name),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_domain.assert_called_with(
            name_or_id=self.domain.name, ignore_missing=False
        )
        self.identity_sdk_client.find_group.assert_called_with(
            name_or_id=self.group.name,
            ignore_missing=False,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=self.group.id,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                '',
                self.group.id,
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_domain(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_domain_id_and_user_id,
            self.assignment_with_domain_id_and_group_id,
        ]

        arglist = ['--domain', self.domain.name]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', self.domain.name),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=self.domain.id,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                '',
                self.domain.id,
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                '',
                self.domain.id,
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_project(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_project_id_and_user_id,
            self.assignment_with_project_id_and_group_id,
        ]

        arglist = ['--project', self.project.name]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', self.project.name),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_project.assert_called_with(
            name_or_id=self.project.name, ignore_missing=False, domain_id=None
        )
        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=self.project.id,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_project_with_domain(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_project_id_and_user_id,
            self.assignment_with_project_id_and_group_id,
        ]

        arglist = [
            '--project',
            self.project.name,
            '--project-domain',
            self.domain.name,
        ]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_domain.assert_called_with(
            name_or_id=self.domain.name, ignore_missing=False
        )
        self.identity_sdk_client.find_project.assert_called_with(
            name_or_id=self.project.name,
            ignore_missing=False,
            domain_id=self.domain.id,
        )
        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=self.project.id,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_def_creds(self):
        self.app.client_manager.auth_ref = mock.Mock()
        auth_ref = self.app.client_manager.auth_ref
        auth_ref.project_id.return_value = self.project.id
        auth_ref.user_id.return_value = self.user.id

        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_project_id_and_user_id,
        ]

        arglist = [
            '--auth-user',
            '--auth-project',
        ]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', False),
            ('authuser', True),
            ('authproject', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=self.user.id,
            group_id=None,
            scope_project_id=self.project.id,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_effective(self):
        self.identity_sdk_client.role_assignments.return_value = [
            self.assignment_with_project_id_and_user_id,
            self.assignment_with_domain_id_and_user_id,
        ]

        arglist = ['--effective']
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', True),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=True,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
            (
                self.role.id,
                self.user.id,
                '',
                '',
                self.domain.id,
                '',
                False,
            ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_role_assignment_list_inherited(self):
        assignment_with_project_id_and_user_id_inherited = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id},
                scope={
                    'project': {'id': self.project.id},
                    'OS-INHERIT:inherited_to': 'projects',
                },
                user={'id': self.user.id},
            )
        )
        assignment_with_domain_id_and_group_id_inherited = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id},
                scope={
                    'domain': {'id': self.domain.id},
                    'OS-INHERIT:inherited_to': 'projects',
                },
                group={'id': self.group.id},
            )
        )
        self.identity_sdk_client.role_assignments.return_value = [
            assignment_with_project_id_and_user_id_inherited,
            assignment_with_domain_id_and_group_id_inherited,
        ]

        arglist = ['--inherited']
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', True),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to='projects',
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.role.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                True,
            ),
            (
                self.role.id,
                '',
                self.group.id,
                '',
                self.domain.id,
                '',
                True,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_include_names(self):
        assignment_with_project_id_and_user_id_include_names = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id, 'name': self.role.name},
                scope={
                    'project': {
                        'domain': {
                            'id': self.domain.id,
                            'name': self.domain.name,
                        },
                        'id': self.project.id,
                        'name': self.project.name,
                    }
                },
                user={
                    'domain': {'id': self.domain.id, 'name': self.domain.name},
                    'id': self.user.id,
                    'name': self.user.name,
                },
            )
        )
        assignment_with_domain_id_and_group_id_include_names = (
            sdk_fakes.generate_fake_resource(
                resource_type=_role_assignment.RoleAssignment,
                role={'id': self.role.id, 'name': self.role.name},
                scope={
                    'domain': {'id': self.domain.id, 'name': self.domain.name}
                },
                group={
                    'domain': {'id': self.domain.id, 'name': self.domain.name},
                    'id': self.group.id,
                    'name': self.group.name,
                },
            )
        )

        self.identity_sdk_client.role_assignments.return_value = [
            assignment_with_project_id_and_user_id_include_names,
            assignment_with_domain_id_and_group_id_include_names,
        ]

        arglist = ['--names']
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', None),
            ('effective', None),
            ('inherited', False),
            ('names', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples

        # This test will not run correctly until the patch in the python
        # client is merged. Once that is done 'data' should return the
        # correct information
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=None,
            user_id=None,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=True,
            inherited_to=None,
        )

        collist = (
            'Role',
            'User',
            'Group',
            'Project',
            'Domain',
            'System',
            'Inherited',
        )
        self.assertEqual(columns, collist)

        datalist = (
            (
                self.role.name,
                '@'.join([self.user.name, self.domain.name]),
                '',
                '@'.join([self.project.name, self.domain.name]),
                '',
                '',
                False,
            ),
            (
                self.role.name,
                '',
                '@'.join([self.group.name, self.domain.name]),
                '',
                self.domain.name,
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_domain_role(self):
        domain_2 = sdk_fakes.generate_fake_resource(_domain.Domain)
        # Create new role with same name but different domain
        role_2 = sdk_fakes.generate_fake_resource(
            resource_type=_role.Role,
            domain_id=domain_2.id,
            name=self.role.name,
        )
        assignment_with_role_domain_2 = sdk_fakes.generate_fake_resource(
            resource_type=_role_assignment.RoleAssignment,
            role={'id': role_2.id, 'name': role_2.name},
            scope={'project': {'id': self.project.id}},
            user={'id': self.user.id},
        )

        self.identity_sdk_client.find_domain.return_value = domain_2
        self.identity_sdk_client.find_role.return_value = role_2
        self.identity_sdk_client.role_assignments.return_value = [
            assignment_with_role_domain_2,
        ]

        arglist = [
            '--role',
            role_2.name,
            '--role-domain',
            domain_2.name,
        ]
        verifylist = [
            ('user', None),
            ('user_domain', None),
            ('group', None),
            ('group_domain', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('project_domain', None),
            ('role', role_2.name),
            ('effective', None),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.role_assignments.assert_called_with(
            role_id=role_2.id,
            user_id=None,
            group_id=None,
            scope_project_id=None,
            scope_domain_id=None,
            scope_system=None,
            effective=None,
            include_names=None,
            inherited_to=None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                role_2.id,
                self.user.id,
                '',
                self.project.id,
                '',
                '',
                False,
            ),
        )
        self.assertEqual(datalist, tuple(data))
