#   Copyright 2018 SUSE Linux GmbH
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

import mock
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.identity.v3 import application_credential
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestApplicationCredential(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestApplicationCredential, self).setUp()

        identity_manager = self.app.client_manager.identity
        self.app_creds_mock = identity_manager.application_credentials
        self.app_creds_mock.reset_mock()
        self.roles_mock = identity_manager.roles
        self.roles_mock.reset_mock()


class TestApplicationCredentialCreate(TestApplicationCredential):

    def setUp(self):
        super(TestApplicationCredentialCreate, self).setUp()

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = application_credential.CreateApplicationCredential(
            self.app, None)

    def test_application_credential_create_basic(self):
        self.app_creds_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.APP_CRED_BASIC),
            loaded=True,
        )

        name = identity_fakes.app_cred_name
        arglist = [
            name
        ]
        verifylist = [
            ('name', identity_fakes.app_cred_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'secret': None,
            'roles': [],
            'expires_at': None,
            'description': None,
            'unrestricted': False,
        }
        self.app_creds_mock.create.assert_called_with(
            name,
            **kwargs
        )

        collist = ('description', 'expires_at', 'id', 'name', 'project_id',
                   'roles', 'secret', 'unrestricted')
        self.assertEqual(collist, columns)
        datalist = (
            None,
            None,
            identity_fakes.app_cred_id,
            identity_fakes.app_cred_name,
            identity_fakes.project_id,
            identity_fakes.role_name,
            identity_fakes.app_cred_secret,
            False,
        )
        self.assertEqual(datalist, data)

    def test_application_credential_create_with_options(self):
        name = identity_fakes.app_cred_name
        self.app_creds_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.APP_CRED_OPTIONS),
            loaded=True,
        )

        arglist = [
            name,
            '--secret', 'moresecuresecret',
            '--role', identity_fakes.role_id,
            '--expiration', identity_fakes.app_cred_expires_str,
            '--description', 'credential for testing'
        ]
        verifylist = [
            ('name', identity_fakes.app_cred_name),
            ('secret', 'moresecuresecret'),
            ('role', [identity_fakes.role_id]),
            ('expiration', identity_fakes.app_cred_expires_str),
            ('description', 'credential for testing')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'secret': 'moresecuresecret',
            'roles': [identity_fakes.role_id],
            'expires_at': identity_fakes.app_cred_expires,
            'description': 'credential for testing',
            'unrestricted': False
        }
        self.app_creds_mock.create.assert_called_with(
            name,
            **kwargs
        )

        collist = ('description', 'expires_at', 'id', 'name', 'project_id',
                   'roles', 'secret', 'unrestricted')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.app_cred_description,
            identity_fakes.app_cred_expires_str,
            identity_fakes.app_cred_id,
            identity_fakes.app_cred_name,
            identity_fakes.project_id,
            identity_fakes.role_name,
            identity_fakes.app_cred_secret,
            False,
        )
        self.assertEqual(datalist, data)


class TestApplicationCredentialDelete(TestApplicationCredential):

    def setUp(self):
        super(TestApplicationCredentialDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.app_creds_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.APP_CRED_BASIC),
            loaded=True,
        )
        self.app_creds_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = application_credential.DeleteApplicationCredential(
            self.app, None)

    def test_application_credential_delete(self):
        arglist = [
            identity_fakes.app_cred_id,
        ]
        verifylist = [
            ('application_credential', [identity_fakes.app_cred_id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.app_creds_mock.delete.assert_called_with(
            identity_fakes.app_cred_id,
        )
        self.assertIsNone(result)

    @mock.patch.object(utils, 'find_resource')
    def test_delete_multi_app_creds_with_exception(self, find_mock):
        find_mock.side_effect = [self.app_creds_mock.get.return_value,
                                 exceptions.CommandError]
        arglist = [
            identity_fakes.app_cred_id,
            'nonexistent_app_cred',
        ]
        verifylist = [
            ('application_credential', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 application credentials failed to'
                             ' delete.', str(e))

        find_mock.assert_any_call(self.app_creds_mock,
                                  identity_fakes.app_cred_id)
        find_mock.assert_any_call(self.app_creds_mock,
                                  'nonexistent_app_cred')

        self.assertEqual(2, find_mock.call_count)
        self.app_creds_mock.delete.assert_called_once_with(
            identity_fakes.app_cred_id)


class TestApplicationCredentialList(TestApplicationCredential):

    def setUp(self):
        super(TestApplicationCredentialList, self).setUp()

        self.app_creds_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.APP_CRED_BASIC),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = application_credential.ListApplicationCredential(self.app,
                                                                    None)

    def test_application_credential_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.app_creds_mock.list.assert_called_with(user=None)

        collist = ('ID', 'Name', 'Project ID', 'Description', 'Expires At')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.app_cred_id,
            identity_fakes.app_cred_name,
            identity_fakes.project_id,
            None,
            None
        ), )
        self.assertEqual(datalist, tuple(data))


class TestApplicationCredentialShow(TestApplicationCredential):

    def setUp(self):
        super(TestApplicationCredentialShow, self).setUp()

        self.app_creds_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.APP_CRED_BASIC),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = application_credential.ShowApplicationCredential(self.app,
                                                                    None)

    def test_application_credential_show(self):
        arglist = [
            identity_fakes.app_cred_id,
        ]
        verifylist = [
            ('application_credential', identity_fakes.app_cred_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.app_creds_mock.get.assert_called_with(identity_fakes.app_cred_id)

        collist = ('description', 'expires_at', 'id', 'name', 'project_id',
                   'roles', 'secret', 'unrestricted')
        self.assertEqual(collist, columns)
        datalist = (
            None,
            None,
            identity_fakes.app_cred_id,
            identity_fakes.app_cred_name,
            identity_fakes.project_id,
            identity_fakes.role_name,
            identity_fakes.app_cred_secret,
            False,
        )
        self.assertEqual(datalist, data)
