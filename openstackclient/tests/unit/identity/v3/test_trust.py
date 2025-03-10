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

from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import role as _role
from openstack.identity.v3 import trust as _trust
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes

from openstackclient.identity.v3 import trust
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestTrustCreate(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.trust = sdk_fakes.generate_fake_resource(_trust.Trust)
        self.identity_sdk_client.create_trust.return_value = self.trust

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.identity_sdk_client.find_user.return_value = self.user

        self.role = sdk_fakes.generate_fake_resource(_role.Role)
        self.identity_sdk_client.find_role.return_value = self.role

        # Get the command object to test
        self.cmd = trust.CreateTrust(self.app, None)

    def test_trust_create_basic(self):
        arglist = [
            '--project',
            self.project.id,
            '--role',
            self.role.id,
            self.user.id,
            self.user.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('roles', [self.role.id]),
            ('trustor', self.user.id),
            ('trustee', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'project_id': self.project.id,
            'roles': [{'id': self.role.id}],
            'impersonation': False,
        }
        # TrustManager.create(trustee_id, trustor_id, impersonation=,
        #   project=, role_names=, expires_at=)
        self.identity_sdk_client.create_trust.assert_called_with(
            trustor_user_id=self.user.id,
            trustee_user_id=self.user.id,
            **kwargs,
        )

        collist = (
            'expires_at',
            'id',
            'is_impersonation',
            'project_id',
            'redelegated_trust_id',
            'redelegation_count',
            'remaining_uses',
            'roles',
            'trustee_user_id',
            'trustor_user_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.trust.expires_at,
            self.trust.id,
            self.trust.is_impersonation,
            self.trust.project_id,
            self.trust.redelegated_trust_id,
            self.trust.redelegation_count,
            self.trust.remaining_uses,
            self.trust.roles,
            self.trust.trustee_user_id,
            self.trust.trustor_user_id,
        )
        self.assertEqual(datalist, data)


class TestTrustDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.trust = sdk_fakes.generate_fake_resource(_trust.Trust)
        self.identity_sdk_client.delete_trust.return_value = None
        self.identity_sdk_client.find_trust.return_value = self.trust

        # Get the command object to test
        self.cmd = trust.DeleteTrust(self.app, None)

    def test_trust_delete(self):
        arglist = [
            self.trust.id,
        ]
        verifylist = [('trust', [self.trust.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_trust.assert_called_with(
            self.trust.id,
        )
        self.assertIsNone(result)

    def test_delete_multi_trusts_with_exception(self):
        arglist = [
            self.trust.id,
            'unexist_trust',
        ]
        verifylist = [
            ('trust', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.identity_sdk_client.find_trust.side_effect = [
            self.trust,
            sdk_exceptions.ResourceNotFound,
        ]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 trusts failed to delete.', str(e))

        self.identity_sdk_client.find_trust.assert_has_calls(
            [
                mock.call(self.trust.id, ignore_missing=False),
                mock.call('unexist_trust', ignore_missing=False),
            ]
        )
        self.identity_sdk_client.delete_trust.assert_called_once_with(
            self.trust.id
        )


class TestTrustList(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.trust = sdk_fakes.generate_fake_resource(_trust.Trust)
        self.identity_sdk_client.trusts.return_value = [self.trust]

        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.identity_sdk_client.find_user.return_value = self.user

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

        self.identity_sdk_client.trusts.assert_called_with(
            trustor_user_id=None,
            trustee_user_id=None,
        )

        collist = (
            'ID',
            'Expires At',
            'Impersonation',
            'Project ID',
            'Trustee User ID',
            'Trustor User ID',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.trust.id,
                self.trust.expires_at,
                self.trust.is_impersonation,
                self.trust.project_id,
                self.trust.trustee_user_id,
                self.trust.trustor_user_id,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_trust_list_auth_user(self):
        self.app.client_manager.auth_ref = mock.Mock()
        auth_ref = self.app.client_manager.auth_ref

        arglist = ['--auth-user']
        verifylist = [
            ('trustor', None),
            ('trustee', None),
            ('authuser', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.trusts.assert_has_calls(
            [
                mock.call(trustor_user_id=auth_ref.user_id),
                mock.call(trustee_user_id=auth_ref.user_id),
            ]
        )

        collist = (
            'ID',
            'Expires At',
            'Impersonation',
            'Project ID',
            'Trustee User ID',
            'Trustor User ID',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.trust.id,
                self.trust.expires_at,
                self.trust.is_impersonation,
                self.trust.project_id,
                self.trust.trustee_user_id,
                self.trust.trustor_user_id,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_trust_list_trustee(self):
        arglist = ['--trustee', self.user.name]
        verifylist = [
            ('trustor', None),
            ('trustee', self.user.name),
            ('authuser', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.trusts.assert_called_with(
            trustee_user_id=self.user.id,
            trustor_user_id=None,
        )

        collist = (
            'ID',
            'Expires At',
            'Impersonation',
            'Project ID',
            'Trustee User ID',
            'Trustor User ID',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.trust.id,
                self.trust.expires_at,
                self.trust.is_impersonation,
                self.trust.project_id,
                self.trust.trustee_user_id,
                self.trust.trustor_user_id,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_trust_list_trustor(self):
        arglist = ['--trustor', self.user.name]
        verifylist = [
            ('trustee', None),
            ('trustor', self.user.name),
            ('authuser', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.trusts.assert_called_once_with(
            trustor_user_id=self.user.id,
            trustee_user_id=None,
        )

        collist = (
            'ID',
            'Expires At',
            'Impersonation',
            'Project ID',
            'Trustee User ID',
            'Trustor User ID',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.trust.id,
                self.trust.expires_at,
                self.trust.is_impersonation,
                self.trust.project_id,
                self.trust.trustee_user_id,
                self.trust.trustor_user_id,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestTrustShow(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.trust = sdk_fakes.generate_fake_resource(_trust.Trust)
        self.identity_sdk_client.find_trust.return_value = self.trust

        # Get the command object to test
        self.cmd = trust.ShowTrust(self.app, None)

    def test_trust_show(self):
        arglist = [
            self.trust.id,
        ]
        verifylist = [
            ('trust', self.trust.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_trust.assert_called_with(
            self.trust.id, ignore_missing=False
        )

        collist = (
            'expires_at',
            'id',
            'is_impersonation',
            'project_id',
            'redelegated_trust_id',
            'redelegation_count',
            'remaining_uses',
            'roles',
            'trustee_user_id',
            'trustor_user_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.trust.expires_at,
            self.trust.id,
            self.trust.is_impersonation,
            self.trust.project_id,
            self.trust.redelegated_trust_id,
            self.trust.redelegation_count,
            self.trust.remaining_uses,
            self.trust.roles,
            self.trust.trustee_user_id,
            self.trust.trustor_user_id,
        )
        self.assertEqual(datalist, data)
