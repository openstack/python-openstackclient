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

import mock
from mock import call

from osc_lib import exceptions

from openstackclient.identity.v3 import credential
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class TestCredential(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestCredential, self).setUp()

        # Get a shortcut to the CredentialManager Mock
        self.credentials_mock = self.app.client_manager.identity.credentials
        self.credentials_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestCredentialCreate(TestCredential):

    user = identity_fakes.FakeUser.create_one_user()
    project = identity_fakes.FakeProject.create_one_project()
    columns = (
        'blob',
        'id',
        'project_id',
        'type',
        'user_id',
    )

    def setUp(self):
        super(TestCredentialCreate, self).setUp()

        self.credential = identity_fakes.FakeCredential.create_one_credential(
            attrs={'user_id': self.user.id, 'project_id': self.project.id})
        self.credentials_mock.create.return_value = self.credential
        self.users_mock.get.return_value = self.user
        self.projects_mock.get.return_value = self.project
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
            'user': self.credential.user_id,
            'type': self.credential.type,
            'blob': self.credential.blob,
            'project': None,
        }
        self.credentials_mock.create.assert_called_once_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_credential_create_with_options(self):
        arglist = [
            self.credential.user_id,
            self.credential.blob,
            '--type', self.credential.type,
            '--project', self.credential.project_id,
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
            'user': self.credential.user_id,
            'type': self.credential.type,
            'blob': self.credential.blob,
            'project': self.credential.project_id,
        }
        self.credentials_mock.create.assert_called_once_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestCredentialDelete(TestCredential):

    credentials = identity_fakes.FakeCredential.create_credentials(count=2)

    def setUp(self):
        super(TestCredentialDelete, self).setUp()

        self.credentials_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = credential.DeleteCredential(self.app, None)

    def test_credential_delete(self):
        arglist = [
            self.credentials[0].id,
        ]
        verifylist = [
            ('credential', [self.credentials[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.credentials_mock.delete.assert_called_with(
            self.credentials[0].id,
        )
        self.assertIsNone(result)

    def test_credential_multi_delete(self):
        arglist = []
        for c in self.credentials:
            arglist.append(c.id)
        verifylist = [
            ('credential', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for c in self.credentials:
            calls.append(call(c.id))
        self.credentials_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_credential_multi_delete_with_exception(self):
        arglist = [
            self.credentials[0].id,
            'unexist_credential',
        ]
        verifylist = [
            ('credential', [self.credentials[0].id, 'unexist_credential'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        delete_mock_result = [None, exceptions.CommandError]
        self.credentials_mock.delete = (
            mock.Mock(side_effect=delete_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 credential failed to delete.', str(e))

        self.credentials_mock.delete.assert_any_call(self.credentials[0].id)
        self.credentials_mock.delete.assert_any_call('unexist_credential')


class TestCredentialList(TestCredential):

    credential = identity_fakes.FakeCredential.create_one_credential()

    columns = ('ID', 'Type', 'User ID', 'Data', 'Project ID')
    data = ((
        credential.id,
        credential.type,
        credential.user_id,
        credential.blob,
        credential.project_id,
    ), )

    def setUp(self):
        super(TestCredentialList, self).setUp()

        self.user = identity_fakes.FakeUser.create_one_user()
        self.users_mock.get.return_value = self.user

        self.credentials_mock.list.return_value = [self.credential]

        # Get the command object to test
        self.cmd = credential.ListCredential(self.app, None)

    def test_credential_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.credentials_mock.list.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_credential_list_with_options(self):
        arglist = [
            '--user', self.credential.user_id,
            '--type', self.credential.type,
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
        self.users_mock.get.assert_called_with(self.credential.user_id)
        self.credentials_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))


class TestCredentialSet(TestCredential):

    credential = identity_fakes.FakeCredential.create_one_credential()

    def setUp(self):
        super(TestCredentialSet, self).setUp()
        self.cmd = credential.SetCredential(self.app, None)

    def test_credential_set_no_options(self):
        arglist = [
            self.credential.id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_missing_user(self):
        arglist = [
            '--type', 'ec2',
            '--data', self.credential.blob,
            self.credential.id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_missing_type(self):
        arglist = [
            '--user', self.credential.user_id,
            '--data', self.credential.blob,
            self.credential.id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_missing_data(self):
        arglist = [
            '--user', self.credential.user_id,
            '--type', 'ec2',
            self.credential.id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_valid(self):
        arglist = [
            '--user', self.credential.user_id,
            '--type', 'ec2',
            '--data', self.credential.blob,
            self.credential.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_credential_set_valid_with_project(self):
        arglist = [
            '--user', self.credential.user_id,
            '--type', 'ec2',
            '--data', self.credential.blob,
            '--project', self.credential.project_id,
            self.credential.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestCredentialShow(TestCredential):

    columns = (
        'blob',
        'id',
        'project_id',
        'type',
        'user_id',
    )

    def setUp(self):
        super(TestCredentialShow, self).setUp()

        self.credential = identity_fakes.FakeCredential.create_one_credential()
        self.credentials_mock.get.return_value = self.credential
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

        self.credentials_mock.get.assert_called_once_with(self.credential.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
