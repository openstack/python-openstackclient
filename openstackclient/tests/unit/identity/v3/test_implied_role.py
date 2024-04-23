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

from openstackclient.identity.v3 import implied_role
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestRole(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        identity_client = self.identity_client

        # Get a shortcut to the UserManager Mock
        self.users_mock = identity_client.users
        self.users_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.groups_mock = identity_client.groups
        self.groups_mock.reset_mock()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = identity_client.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = identity_client.projects
        self.projects_mock.reset_mock()

        # Get a shortcut to the RoleManager Mock
        self.roles_mock = identity_client.roles
        self.roles_mock.reset_mock()

        # Get a shortcut to the InferenceRuleManager Mock
        self.inference_rules_mock = identity_client.inference_rules
        self.inference_rules_mock.reset_mock()

    def _is_inheritance_testcase(self):
        return False


class TestImpliedRoleCreate(TestRole):
    def setUp(self):
        super().setUp()

        self.roles_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLES[0]),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLES[1]),
                loaded=True,
            ),
        ]

        fake_resource = fakes.FakeResource(
            None,
            {
                'prior_role': copy.deepcopy(identity_fakes.ROLES[0]),
                'implied': copy.deepcopy(identity_fakes.ROLES[1]),
            },
            loaded=True,
        )
        self.inference_rules_mock.create.return_value = fake_resource

        self.cmd = implied_role.CreateImpliedRole(self.app, None)

    def test_implied_role_create(self):
        arglist = [
            identity_fakes.ROLES[0]['id'],
            '--implied-role',
            identity_fakes.ROLES[1]['id'],
        ]
        verifylist = [
            ('role', identity_fakes.ROLES[0]['id']),
            ('implied_role', identity_fakes.ROLES[1]['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # InferenceRuleManager.create(prior, implied)
        self.inference_rules_mock.create.assert_called_with(
            identity_fakes.ROLES[0]['id'], identity_fakes.ROLES[1]['id']
        )

        collist = ('implied', 'prior_role')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.ROLES[1]['id'],
            identity_fakes.ROLES[0]['id'],
        )
        self.assertEqual(datalist, data)


class TestImpliedRoleDelete(TestRole):
    def setUp(self):
        super().setUp()

        self.roles_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLES[0]),
                loaded=True,
            ),
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ROLES[1]),
                loaded=True,
            ),
        ]

        fake_resource = fakes.FakeResource(
            None,
            {
                'prior-role': copy.deepcopy(identity_fakes.ROLES[0]),
                'implied': copy.deepcopy(identity_fakes.ROLES[1]),
            },
            loaded=True,
        )
        self.inference_rules_mock.delete.return_value = fake_resource

        self.cmd = implied_role.DeleteImpliedRole(self.app, None)

    def test_implied_role_delete(self):
        arglist = [
            identity_fakes.ROLES[0]['id'],
            '--implied-role',
            identity_fakes.ROLES[1]['id'],
        ]
        verifylist = [
            ('role', identity_fakes.ROLES[0]['id']),
            ('implied_role', identity_fakes.ROLES[1]['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.inference_rules_mock.delete.assert_called_with(
            identity_fakes.ROLES[0]['id'], identity_fakes.ROLES[1]['id']
        )


class TestImpliedRoleList(TestRole):
    def setUp(self):
        super().setUp()

        self.inference_rules_mock.list_inference_roles.return_value = (
            identity_fakes.FakeImpliedRoleResponse.create_list()
        )

        self.cmd = implied_role.ListImpliedRole(self.app, None)

    def test_implied_role_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.inference_rules_mock.list_inference_roles.assert_called_with()

        collist = [
            'Prior Role ID',
            'Prior Role Name',
            'Implied Role ID',
            'Implied Role Name',
        ]
        self.assertEqual(collist, columns)
        datalist = [
            (
                identity_fakes.ROLES[0]['id'],
                identity_fakes.ROLES[0]['name'],
                identity_fakes.ROLES[1]['id'],
                identity_fakes.ROLES[1]['name'],
            )
        ]
        x = [d for d in data]
        self.assertEqual(datalist, x)
