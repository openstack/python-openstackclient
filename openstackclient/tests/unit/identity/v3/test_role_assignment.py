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

from openstackclient.identity.v3 import role_assignment
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRoleAssignment(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestRoleAssignment, self).setUp()


class TestRoleAssignmentList(TestRoleAssignment):

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
        super(TestRoleAssignment, self).setUp()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the GroupManager Mock
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

        self.role_assignments_mock = self.app.client_manager.identity.\
            role_assignments
        self.role_assignments_mock.reset_mock()

        # Get the command object to test
        self.cmd = role_assignment.ListRoleAssignment(self.app, None)

    def test_role_assignment_list_no_filters(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_GROUP_ID),
                loaded=True,
            ),
        ]

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            group=None,
            effective=False,
            role=None,
            user=None,
            project=None,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            '',
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            identity_fakes.project_id,
            '',
            '',
            False
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_user(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID),
                loaded=True,
            ),
        ]

        arglist = [
            '--user', identity_fakes.user_name
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            user=self.users_mock.get(),
            group=None,
            project=None,
            role=None,
            effective=False,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            '',
            False
        ), (identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            '',
            False
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_group(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_DOMAIN_ID_AND_GROUP_ID),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_GROUP_ID),
                loaded=True,
            ),
        ]

        arglist = [
            '--group', identity_fakes.group_name
        ]
        verifylist = [
            ('user', None),
            ('group', identity_fakes.group_name),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            group=self.groups_mock.get(),
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            '',
            identity_fakes.domain_id,
            '',
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            identity_fakes.project_id,
            '',
            '',
            False
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_domain(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_DOMAIN_ID_AND_GROUP_ID),
                loaded=True,
            ),
        ]

        arglist = [
            '--domain', identity_fakes.domain_name
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=self.domains_mock.get(),
            system=None,
            group=None,
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            '',
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            '',
            identity_fakes.domain_id,
            '',
            False
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_project(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_GROUP_ID),
                loaded=True,
            ),
        ]

        arglist = [
            '--project', identity_fakes.project_name
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', None),
            ('effective', False),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            group=None,
            effective=False,
            project=self.projects_mock.get(),
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            '',
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            identity_fakes.project_id,
            '',
            '',
            False
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_def_creds(self):

        auth_ref = self.app.client_manager.auth_ref = mock.Mock()
        auth_ref.project_id.return_value = identity_fakes.project_id
        auth_ref.user_id.return_value = identity_fakes.user_id

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID),
                loaded=True,
            ),
        ]

        arglist = [
            '--auth-user',
            '--auth-project',
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
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

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            user=self.users_mock.get(),
            group=None,
            project=self.projects_mock.get(),
            role=None,
            effective=False,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            '',
            False
        ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_effective(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID),
                loaded=True,
            ),
        ]

        arglist = ['--effective']
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', None),
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

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            group=None,
            effective=True,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            '',
            False
        ), (identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            '',
            False
            ),)
        self.assertEqual(tuple(data), datalist)

    def test_role_assignment_list_inherited(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    (identity_fakes.
                        ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID_INHERITED)),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    (identity_fakes.
                        ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID_INHERITED)),
                loaded=True,
            ),
        ]

        arglist = ['--inherited']
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', True),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            group=None,
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to='projects',
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            '',
            True
        ), (identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            '',
            True
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_include_names(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes
                    .ASSIGNMENT_WITH_PROJECT_ID_AND_USER_ID_INCLUDE_NAMES),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes
                    .ASSIGNMENT_WITH_DOMAIN_ID_AND_USER_ID_INCLUDE_NAMES),
                loaded=True,
            ),
        ]

        arglist = ['--names']
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
            ('names', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples

        # This test will not run correctly until the patch in the python
        # client is merged. Once that is done 'data' should return the
        # correct information
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            group=None,
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None,
            include_names=True)

        collist = (
            'Role', 'User', 'Group', 'Project', 'Domain', 'System', 'Inherited'
        )
        self.assertEqual(columns, collist)

        datalist1 = ((
            identity_fakes.role_name,
            '@'.join([identity_fakes.user_name, identity_fakes.domain_name]),
            '',
            '@'.join([identity_fakes.project_name,
                      identity_fakes.domain_name]),
            '',
            '',
            False
        ), (identity_fakes.role_name,
            '@'.join([identity_fakes.user_name, identity_fakes.domain_name]),
            '',
            '',
            identity_fakes.domain_name,
            '',
            False
            ),)
        self.assertEqual(tuple(data), datalist1)

    def test_role_assignment_list_domain_role(self):

        self.role_assignments_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ASSIGNMENT_WITH_DOMAIN_ROLE),
                loaded=True,
            ),
        ]

        arglist = [
            '--role', identity_fakes.ROLE_2['name'],
            '--role-domain', identity_fakes.domain_name
        ]
        verifylist = [
            ('user', None),
            ('group', None),
            ('system', None),
            ('domain', None),
            ('project', None),
            ('role', identity_fakes.ROLE_2['name']),
            ('effective', False),
            ('inherited', False),
            ('names', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            system=None,
            user=None,
            group=None,
            project=None,
            role=self.roles_mock.get(),
            effective=False,
            os_inherit_extension_inherited_to=None,
            include_names=False)

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.ROLE_2['id'],
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            '',
            False
        ),)
        self.assertEqual(datalist, tuple(data))
