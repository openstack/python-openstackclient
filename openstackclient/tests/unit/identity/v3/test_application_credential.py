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

import datetime
from unittest import mock
from unittest.mock import call

from osc_lib import exceptions

from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import (
    application_credential as _application_credential,
)
from openstack.identity.v3 import role as _role
from openstack.test import fakes as sdk_fakes
from openstackclient.identity.v3 import application_credential
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestApplicationCredentialCreate(identity_fakes.TestIdentityv3):
    columns = (
        'id',
        'name',
        'description',
        'project_id',
        'roles',
        'unrestricted',
        'access_rules',
        'expires_at',
        'secret',
    )

    def setUp(self):
        super().setUp()

        self.roles = sdk_fakes.generate_fake_resource(_role.Role)
        self.application_credential = sdk_fakes.generate_fake_resource(
            resource_type=_application_credential.ApplicationCredential,
            roles=[],
        )

        self.datalist = (
            self.application_credential.id,
            self.application_credential.name,
            self.application_credential.description,
            self.application_credential.project_id,
            self.application_credential.roles,
            self.application_credential.unrestricted,
            self.application_credential.access_rules,
            self.application_credential.expires_at,
            self.application_credential.secret,
        )

        self.identity_sdk_client.create_application_credential.return_value = (
            self.application_credential
        )

        # Get the command object to test
        self.cmd = application_credential.CreateApplicationCredential(
            self.app, None
        )

    def test_application_credential_create_basic(self):
        name = self.application_credential.name
        arglist = [name]
        verifylist = [('name', self.application_credential.name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'roles': [],
            'expires_at': None,
            'description': None,
            'secret': None,
            'unrestricted': False,
            'access_rules': [],
        }
        self.identity_sdk_client.create_application_credential.assert_called_with(
            user_id, name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_application_credential_create_with_options(self):
        name = self.application_credential.name
        arglist = [
            name,
            '--secret',
            'moresecuresecret',
            '--role',
            self.roles.id,
            '--expiration',
            '2024-01-01T00:00:00',
            '--description',
            'credential for testing',
        ]
        verifylist = [
            ('name', self.application_credential.name),
            ('secret', 'moresecuresecret'),
            ('role', [self.roles.id]),
            ('expiration', '2024-01-01T00:00:00'),
            ('description', 'credential for testing'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'roles': [{'id': self.roles.id}],
            'expires_at': datetime.datetime(2024, 1, 1, 0, 0),
            'description': 'credential for testing',
            'secret': 'moresecuresecret',
            'unrestricted': False,
            'access_rules': [],
        }
        self.identity_sdk_client.create_application_credential.assert_called_with(
            user_id, name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_application_credential_create_with_access_rules_string(self):
        name = self.application_credential.name

        arglist = [
            name,
            '--access-rules',
            '[{"path": "/v2.1/servers", "method": "GET", "service": "compute"}]',
        ]
        verifylist = [
            ('name', self.application_credential.name),
            (
                'access_rules',
                '[{"path": "/v2.1/servers", "method": "GET", "service": "compute"}]',
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'roles': [],
            'expires_at': None,
            'description': None,
            'secret': None,
            'unrestricted': False,
            'access_rules': [
                {
                    "path": "/v2.1/servers",
                    "method": "GET",
                    "service": "compute",
                }
            ],
        }
        self.identity_sdk_client.create_application_credential.assert_called_with(
            user_id, name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch('openstackclient.identity.v3.application_credential.json.load')
    @mock.patch('openstackclient.identity.v3.application_credential.open')
    def test_application_credential_create_with_access_rules_file(
        self, _, mock_json_load
    ):
        mock_json_load.return_value = '/tmp/access_rules.json'
        name = self.application_credential.name

        arglist = [
            name,
            '--access-rules',
            '/tmp/access_rules.json',
        ]
        verifylist = [
            ('name', self.application_credential.name),
            ('access_rules', '/tmp/access_rules.json'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'roles': [],
            'expires_at': None,
            'description': None,
            'secret': None,
            'unrestricted': False,
            'access_rules': '/tmp/access_rules.json',
        }
        self.identity_sdk_client.create_application_credential.assert_called_with(
            user_id, name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestApplicationCredentialDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.application_credential = sdk_fakes.generate_fake_resource(
            resource_type=_application_credential.ApplicationCredential,
            roles=[],
        )
        self.identity_sdk_client.find_application_credential.return_value = (
            self.application_credential
        )
        self.identity_sdk_client.delete_application_credential.return_value = (
            None
        )

        # Get the command object to test
        self.cmd = application_credential.DeleteApplicationCredential(
            self.app, None
        )

    def test_application_credential_delete(self):
        arglist = [
            self.application_credential.id,
        ]
        verifylist = [
            ('application_credential', [self.application_credential.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_application_credential.assert_called_with(
            user_id,
            self.application_credential.id,
        )
        self.assertIsNone(result)

    def test_delete_multi_app_creds_with_exception(self):
        self.identity_sdk_client.find_application_credential.side_effect = [
            self.application_credential,
            sdk_exceptions.NotFoundException,
        ]
        arglist = [
            self.application_credential.id,
            'nonexistent_app_cred',
        ]
        verifylist = [
            ('application_credential', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 application credentials failed to delete.', str(e)
            )

        calls = []
        for a in arglist:
            calls.append(call(user_id, a))

        self.identity_sdk_client.find_application_credential.assert_has_calls(
            calls
        )

        self.assertEqual(
            2, self.identity_sdk_client.find_application_credential.call_count
        )
        self.identity_sdk_client.delete_application_credential.assert_called_once_with(
            user_id, self.application_credential.id
        )


class TestApplicationCredentialList(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.application_credential = sdk_fakes.generate_fake_resource(
            resource_type=_application_credential.ApplicationCredential,
            roles=[],
        )
        self.identity_sdk_client.application_credentials.return_value = [
            self.application_credential
        ]

        # Get the command object to test
        self.cmd = application_credential.ListApplicationCredential(
            self.app, None
        )

    def test_application_credential_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.application_credentials.assert_called_with(
            user=user_id
        )

        collist = (
            'ID',
            'Name',
            'Description',
            'Project ID',
            'Roles',
            'Unrestricted',
            'Access Rules',
            'Expires At',
        )
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.application_credential.id,
                self.application_credential.name,
                self.application_credential.description,
                self.application_credential.project_id,
                self.application_credential.roles,
                self.application_credential.unrestricted,
                self.application_credential.access_rules,
                self.application_credential.expires_at,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestApplicationCredentialShow(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.application_credential = sdk_fakes.generate_fake_resource(
            resource_type=_application_credential.ApplicationCredential,
            roles=[],
        )
        self.identity_sdk_client.find_application_credential.return_value = (
            self.application_credential
        )

        # Get the command object to test
        self.cmd = application_credential.ShowApplicationCredential(
            self.app, None
        )

    def test_application_credential_show(self):
        arglist = [
            self.application_credential.id,
        ]
        verifylist = [
            ('application_credential', self.application_credential.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.find_application_credential.assert_called_with(
            user_id, self.application_credential.id
        )

        collist = (
            'id',
            'name',
            'description',
            'project_id',
            'roles',
            'unrestricted',
            'access_rules',
            'expires_at',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.application_credential.id,
            self.application_credential.name,
            self.application_credential.description,
            self.application_credential.project_id,
            self.application_credential.roles,
            self.application_credential.unrestricted,
            self.application_credential.access_rules,
            self.application_credential.expires_at,
        )
        self.assertEqual(datalist, data)
