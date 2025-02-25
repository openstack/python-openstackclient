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

from unittest.mock import call

from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import credential as _credential
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import credential
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class TestCredentialCreate(identity_fakes.TestIdentityv3):
    user = sdk_fakes.generate_fake_resource(_user.User)
    project = sdk_fakes.generate_fake_resource(_project.Project)
    columns = (
        'blob',
        'id',
        'project_id',
        'type',
        'user_id',
    )

    def setUp(self):
        super().setUp()

        self.credential = sdk_fakes.generate_fake_resource(
            resource_type=_credential.Credential,
            user_id=self.user.id,
            project_id=self.project.id,
            type='cert',
        )
        self.identity_sdk_client.create_credential.return_value = (
            self.credential
        )
        self.identity_sdk_client.find_user.return_value = self.user
        self.identity_sdk_client.find_project.return_value = self.project
        self.data = (
            self.credential.blob,
            self.credential.id,
            self.credential.project_id,
            self.credential.type,
            self.credential.user_id,
        )

        self.cmd = credential.CreateCredential(self.app, None)

    def test_credential_create_no_options(self):
        arglist = [
            self.credential.user_id,
            self.credential.blob,
        ]
        verifylist = [
            ('user', self.credential.user_id),
            ('data', self.credential.blob),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'user_id': self.credential.user_id,
            'type': self.credential.type,
            'blob': self.credential.blob,
            'project_id': None,
        }
        self.identity_sdk_client.create_credential.assert_called_once_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_credential_create_with_options(self):
        arglist = [
            self.credential.user_id,
            self.credential.blob,
            '--type',
            self.credential.type,
            '--project',
            self.credential.project_id,
        ]
        verifylist = [
            ('user', self.credential.user_id),
            ('data', self.credential.blob),
            ('type', self.credential.type),
            ('project', self.credential.project_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'user_id': self.credential.user_id,
            'type': self.credential.type,
            'blob': self.credential.blob,
            'project_id': self.credential.project_id,
        }
        self.identity_sdk_client.create_credential.assert_called_once_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestCredentialDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.identity_sdk_client.delete_credential.return_value = None

        # Get the command object to test
        self.cmd = credential.DeleteCredential(self.app, None)

    def test_credential_delete(self):
        credential = sdk_fakes.generate_fake_resource(
            _credential.Credential,
        )
        arglist = [
            credential.id,
        ]
        verifylist = [
            ('credential', [credential.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_credential.assert_called_with(
            credential.id,
        )
        self.assertIsNone(result)

    def test_credential_multi_delete(self):
        credentials = sdk_fakes.generate_fake_resources(
            _credential.Credential, count=2
        )
        arglist = []
        for c in credentials:
            arglist.append(c.id)
        verifylist = [
            ('credential', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for c in credentials:
            calls.append(call(c.id))
        self.identity_sdk_client.delete_credential.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_credential_multi_delete_with_exception(self):
        credential = sdk_fakes.generate_fake_resource(
            _credential.Credential,
        )
        arglist = [
            credential.id,
            'unexist_credential',
        ]
        verifylist = [('credential', [credential.id, 'unexist_credential'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.identity_sdk_client.delete_credential.side_effect = [
            None,
            sdk_exceptions.NotFoundException,
        ]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 credential failed to delete.', str(e))

        self.identity_sdk_client.delete_credential.assert_any_call(
            credential.id
        )
        self.identity_sdk_client.delete_credential.assert_any_call(
            'unexist_credential'
        )


class TestCredentialList(identity_fakes.TestIdentityv3):
    credential = sdk_fakes.generate_fake_resource(_credential.Credential)

    columns = ('ID', 'Type', 'User ID', 'Data', 'Project ID')
    data = (
        (
            credential.id,
            credential.type,
            credential.user_id,
            credential.blob,
            credential.project_id,
        ),
    )

    def setUp(self):
        super().setUp()

        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.identity_sdk_client.find_user.return_value = self.user

        self.identity_sdk_client.credentials.return_value = [self.credential]

        # Get the command object to test
        self.cmd = credential.ListCredential(self.app, None)

    def test_credential_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.credentials.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_credential_list_with_options(self):
        arglist = [
            '--user',
            self.credential.user_id,
            '--type',
            self.credential.type,
        ]
        verifylist = [
            ('user', self.credential.user_id),
            ('type', self.credential.type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'user_id': self.user.id,
            'type': self.credential.type,
        }
        self.identity_sdk_client.find_user.assert_called_with(
            self.credential.user_id, domain_id=None, ignore_missing=False
        )
        self.identity_sdk_client.credentials.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))


class TestCredentialSet(identity_fakes.TestIdentityv3):
    credential = sdk_fakes.generate_fake_resource(_credential.Credential)

    def setUp(self):
        super().setUp()
        self.cmd = credential.SetCredential(self.app, None)

    def test_credential_set_no_options(self):
        arglist = [
            self.credential.id,
        ]

        self.assertRaises(
            utils.ParserException, self.check_parser, self.cmd, arglist, []
        )

    def test_credential_set_missing_user(self):
        arglist = [
            '--type',
            'ec2',
            '--data',
            self.credential.blob,
            self.credential.id,
        ]

        self.assertRaises(
            utils.ParserException, self.check_parser, self.cmd, arglist, []
        )

    def test_credential_set_missing_type(self):
        arglist = [
            '--user',
            self.credential.user_id,
            '--data',
            self.credential.blob,
            self.credential.id,
        ]

        self.assertRaises(
            utils.ParserException, self.check_parser, self.cmd, arglist, []
        )

    def test_credential_set_missing_data(self):
        arglist = [
            '--user',
            self.credential.user_id,
            '--type',
            'ec2',
            self.credential.id,
        ]

        self.assertRaises(
            utils.ParserException, self.check_parser, self.cmd, arglist, []
        )

    def test_credential_set_valid(self):
        arglist = [
            '--user',
            self.credential.user_id,
            '--type',
            'ec2',
            '--data',
            self.credential.blob,
            self.credential.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_credential_set_valid_with_project(self):
        arglist = [
            '--user',
            self.credential.user_id,
            '--type',
            'ec2',
            '--data',
            self.credential.blob,
            '--project',
            self.credential.project_id,
            self.credential.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestCredentialShow(identity_fakes.TestIdentityv3):
    columns = (
        'blob',
        'id',
        'project_id',
        'type',
        'user_id',
    )

    def setUp(self):
        super().setUp()

        self.credential = sdk_fakes.generate_fake_resource(
            _credential.Credential
        )
        self.identity_sdk_client.get_credential.return_value = self.credential
        self.data = (
            self.credential.blob,
            self.credential.id,
            self.credential.project_id,
            self.credential.type,
            self.credential.user_id,
        )

        self.cmd = credential.ShowCredential(self.app, None)

    def test_credential_show(self):
        arglist = [
            self.credential.id,
        ]
        verifylist = [
            ('credential', self.credential.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_credential.assert_called_once_with(
            self.credential.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
