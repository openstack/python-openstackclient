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

from openstackclient.identity.v3 import role_assignment
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestRoleAssignment(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestRoleAssignment, self).setUp()


class TestRoleAssignmentList(TestRoleAssignment):

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

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            group=None,
            effective=False,
            role=None,
            user=None,
            project=None,
            os_inherit_extension_inherited_to=None)

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            identity_fakes.project_id,
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
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            user=self.users_mock.get(),
            group=None,
            project=None,
            role=None,
            effective=False,
            os_inherit_extension_inherited_to=None)

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            False
        ), (identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
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
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            group=self.groups_mock.get(),
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None)

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            '',
            identity_fakes.domain_id,
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            identity_fakes.project_id,
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
            ('domain', identity_fakes.domain_name),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=self.domains_mock.get(),
            group=None,
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None)

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            '',
            identity_fakes.domain_id,
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
            ('domain', None),
            ('project', identity_fakes.project_name),
            ('role', None),
            ('effective', False),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            group=None,
            effective=False,
            project=self.projects_mock.get(),
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None)

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            False
        ), (identity_fakes.role_id,
            '',
            identity_fakes.group_id,
            identity_fakes.project_id,
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
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', True),
            ('inherited', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            group=None,
            effective=True,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to=None)

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            False
        ), (identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
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
            ('domain', None),
            ('project', None),
            ('role', None),
            ('effective', False),
            ('inherited', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.role_assignments_mock.list.assert_called_with(
            domain=None,
            group=None,
            effective=False,
            project=None,
            role=None,
            user=None,
            os_inherit_extension_inherited_to='projects')

        collist = ('Role', 'User', 'Group', 'Project', 'Domain', 'Inherited')
        self.assertEqual(columns, collist)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            identity_fakes.project_id,
            '',
            True
        ), (identity_fakes.role_id,
            identity_fakes.user_id,
            '',
            '',
            identity_fakes.domain_id,
            True
            ),)
        self.assertEqual(datalist, tuple(data))
