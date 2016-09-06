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

from openstackclient.identity.v3 import trust
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestTrust(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestTrust, self).setUp()

        self.trusts_mock = self.app.client_manager.identity.trusts
        self.trusts_mock.reset_mock()
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()
        self.roles_mock = self.app.client_manager.identity.roles
        self.roles_mock.reset_mock()


class TestTrustCreate(TestTrust):

    def setUp(self):
        super(TestTrustCreate, self).setUp()

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

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        self.trusts_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.TRUST),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = trust.CreateTrust(self.app, None)

    def test_trust_create_basic(self):
        arglist = [
            '--project', identity_fakes.project_id,
            '--role', identity_fakes.role_id,
            identity_fakes.user_id,
            identity_fakes.user_id
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('impersonate', False),
            ('role', [identity_fakes.role_id]),
            ('trustor', identity_fakes.user_id),
            ('trustee', identity_fakes.user_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'impersonation': False,
            'project': identity_fakes.project_id,
            'role_names': [identity_fakes.role_name],
            'expires_at': None,
        }
        # TrustManager.create(trustee_id, trustor_id, impersonation=,
        #   project=, role_names=, expires_at=)
        self.trusts_mock.create.assert_called_with(
            identity_fakes.user_id,
            identity_fakes.user_id,
            **kwargs
        )

        collist = ('expires_at', 'id', 'impersonation', 'project_id',
                   'roles', 'trustee_user_id', 'trustor_user_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.trust_expires,
            identity_fakes.trust_id,
            identity_fakes.trust_impersonation,
            identity_fakes.project_id,
            identity_fakes.role_name,
            identity_fakes.user_id,
            identity_fakes.user_id
        )
        self.assertEqual(datalist, data)


class TestTrustDelete(TestTrust):

    def setUp(self):
        super(TestTrustDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.trusts_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.TRUST),
            loaded=True,
        )
        self.trusts_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = trust.DeleteTrust(self.app, None)

    def test_trust_delete(self):
        arglist = [
            identity_fakes.trust_id,
        ]
        verifylist = [
            ('trust', [identity_fakes.trust_id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.trusts_mock.delete.assert_called_with(
            identity_fakes.trust_id,
        )
        self.assertIsNone(result)


class TestTrustList(TestTrust):

    def setUp(self):
        super(TestTrustList, self).setUp()

        self.trusts_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.TRUST),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = trust.ListTrust(self.app, None)

    def test_trust_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.trusts_mock.list.assert_called_with()

        collist = ('ID', 'Expires At', 'Impersonation', 'Project ID',
                   'Trustee User ID', 'Trustor User ID')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.trust_id,
            identity_fakes.trust_expires,
            identity_fakes.trust_impersonation,
            identity_fakes.project_id,
            identity_fakes.user_id,
            identity_fakes.user_id
        ), )
        self.assertEqual(datalist, tuple(data))


class TestTrustShow(TestTrust):

    def setUp(self):
        super(TestTrustShow, self).setUp()

        self.trusts_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.TRUST),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = trust.ShowTrust(self.app, None)

    def test_trust_show(self):
        arglist = [
            identity_fakes.trust_id,
        ]
        verifylist = [
            ('trust', identity_fakes.trust_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.trusts_mock.get.assert_called_with(identity_fakes.trust_id)

        collist = ('expires_at', 'id', 'impersonation', 'project_id',
                   'roles', 'trustee_user_id', 'trustor_user_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.trust_expires,
            identity_fakes.trust_id,
            identity_fakes.trust_impersonation,
            identity_fakes.project_id,
            identity_fakes.role_name,
            identity_fakes.user_id,
            identity_fakes.user_id
        )
        self.assertEqual(datalist, data)
