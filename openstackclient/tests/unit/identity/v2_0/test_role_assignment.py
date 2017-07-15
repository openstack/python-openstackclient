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

from openstackclient.identity.v2_0 import role_assignment
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes


class TestRoleAssignment(identity_fakes.TestIdentityv2):

    def setUp(self):
        super(TestRoleAssignment, self).setUp()


class TestRoleAssignmentList(TestRoleAssignment):

    columns = (
        'Role',
        'User',
        'Project',
    )

    def setUp(self):
        super(TestRoleAssignment, self).setUp()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()

        # Get a shortcut to the RoleManager Mock
        self.roles_mock = self.app.client_manager.identity.roles
        self.roles_mock.reset_mock()

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
        self.cmd = role_assignment.ListRoleAssignment(self.app, None)

    def test_role_assignment_list_no_filters(self):

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # This argument combination should raise a CommandError
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_role_assignment_list_only_project_filter(self):

        arglist = [
            '--project', identity_fakes.project_name,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # This argument combination should raise a CommandError
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_role_assignment_list_only_user_filter(self):

        arglist = [
            '--user', identity_fakes.user_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # This argument combination should raise a CommandError
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_role_assignment_list_project_and_user(self):

        self.roles_mock.roles_for_user.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ROLE),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ROLE_2),
                loaded=True,
            ),
        ]

        arglist = [
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.project_id,
        )

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            identity_fakes.project_id,
        ), (identity_fakes.ROLE_2['id'],
            identity_fakes.user_id,
            identity_fakes.project_id,
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_def_creds(self):

        auth_ref = self.app.client_manager.auth_ref = mock.Mock()
        auth_ref.project_id.return_value = identity_fakes.project_id
        auth_ref.user_id.return_value = identity_fakes.user_id

        self.roles_mock.roles_for_user.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ROLE),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ROLE_2),
                loaded=True,
            ),
        ]

        arglist = [
            '--auth-user',
            '--auth-project',
        ]
        verifylist = [
            ('authuser', True),
            ('authproject', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.project_id,
        )

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_id,
            identity_fakes.user_id,
            identity_fakes.project_id,
        ), (identity_fakes.ROLE_2['id'],
            identity_fakes.user_id,
            identity_fakes.project_id,
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_role_assignment_list_by_name_project_and_user(self):

        self.roles_mock.roles_for_user.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ROLE),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(
                    identity_fakes.ROLE_2),
                loaded=True,
            ),
        ]

        arglist = [
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_name,
            '--names'
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('project', identity_fakes.project_name),
            ('names', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.roles_mock.roles_for_user.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.project_id,
        )

        self.assertEqual(self.columns, columns)
        datalist = ((
            identity_fakes.role_name,
            identity_fakes.user_name,
            identity_fakes.project_name,
        ), (identity_fakes.ROLE_2['name'],
            identity_fakes.user_name,
            identity_fakes.project_name,
            ),)
        self.assertEqual(datalist, tuple(data))
