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

import json

from openstackclient.identity.v3 import credential
from openstackclient.tests.identity.v3 import fakes as identity_fakes
from openstackclient.tests import utils


class TestCredential(identity_fakes.TestIdentityv3):
    data = {
        "access": "abc123",
        "secret": "hidden-message",
        "trust_id": None
    }

    def __init__(self, *args):
        super(TestCredential, self).__init__(*args)

        self.json_data = json.dumps(self.data)

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


class TestCredentialSet(TestCredential):
    def setUp(self):
        super(TestCredentialSet, self).setUp()
        self.cmd = credential.SetCredential(self.app, None)

    def test_credential_set_no_options(self):
        arglist = [
            identity_fakes.credential_id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_missing_user(self):
        arglist = [
            '--type', 'ec2',
            '--data', self.json_data,
            identity_fakes.credential_id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_missing_type(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--data', self.json_data,
            identity_fakes.credential_id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_missing_data(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--type', 'ec2',
            identity_fakes.credential_id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_credential_set_valid(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--type', 'ec2',
            '--data', self.json_data,
            identity_fakes.credential_id,
        ]

        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)

    def test_credential_set_valid_with_project(self):
        arglist = [
            '--user', identity_fakes.user_name,
            '--type', 'ec2',
            '--data', self.json_data,
            '--project', identity_fakes.project_name,
            identity_fakes.credential_id,
        ]

        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)
