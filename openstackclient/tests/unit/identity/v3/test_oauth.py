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

import copy

from openstackclient.identity.v3 import token
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestOAuth1(identity_fakes.TestOAuth1):
    def setUp(self):
        super().setUp()
        identity_client = self.identity_client
        self.access_tokens_mock = identity_client.oauth1.access_tokens
        self.access_tokens_mock.reset_mock()
        self.request_tokens_mock = identity_client.oauth1.request_tokens
        self.request_tokens_mock.reset_mock()
        self.projects_mock = identity_client.projects
        self.projects_mock.reset_mock()
        self.roles_mock = identity_client.roles
        self.roles_mock.reset_mock()


class TestAccessTokenCreate(TestOAuth1):
    def setUp(self):
        super().setUp()

        self.access_tokens_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.OAUTH_ACCESS_TOKEN),
            loaded=True,
        )

        self.cmd = token.CreateAccessToken(self.app, None)

    def test_create_access_tokens(self):
        arglist = [
            '--consumer-key',
            identity_fakes.consumer_id,
            '--consumer-secret',
            identity_fakes.consumer_secret,
            '--request-key',
            identity_fakes.request_token_id,
            '--request-secret',
            identity_fakes.request_token_secret,
            '--verifier',
            identity_fakes.oauth_verifier_pin,
        ]
        verifylist = [
            ('consumer_key', identity_fakes.consumer_id),
            ('consumer_secret', identity_fakes.consumer_secret),
            ('request_key', identity_fakes.request_token_id),
            ('request_secret', identity_fakes.request_token_secret),
            ('verifier', identity_fakes.oauth_verifier_pin),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.access_tokens_mock.create.assert_called_with(
            identity_fakes.consumer_id,
            identity_fakes.consumer_secret,
            identity_fakes.request_token_id,
            identity_fakes.request_token_secret,
            identity_fakes.oauth_verifier_pin,
        )

        collist = ('expires', 'id', 'key', 'secret')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.access_token_expires,
            identity_fakes.access_token_id,
            identity_fakes.access_token_id,
            identity_fakes.access_token_secret,
        )
        self.assertEqual(datalist, data)


class TestRequestTokenAuthorize(TestOAuth1):
    def setUp(self):
        super().setUp()

        self.roles_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ROLE),
            loaded=True,
        )

        copied_verifier = copy.deepcopy(identity_fakes.OAUTH_VERIFIER)
        resource = fakes.FakeResource(None, copied_verifier, loaded=True)
        self.request_tokens_mock.authorize.return_value = resource
        self.cmd = token.AuthorizeRequestToken(self.app, None)

    def test_authorize_request_tokens(self):
        arglist = [
            '--request-key',
            identity_fakes.request_token_id,
            '--role',
            identity_fakes.role_name,
        ]
        verifylist = [
            ('request_key', identity_fakes.request_token_id),
            ('role', [identity_fakes.role_name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.request_tokens_mock.authorize.assert_called_with(
            identity_fakes.request_token_id,
            [identity_fakes.role_id],
        )

        collist = ('oauth_verifier',)
        self.assertEqual(collist, columns)
        datalist = (identity_fakes.oauth_verifier_pin,)
        self.assertEqual(datalist, data)


class TestRequestTokenCreate(TestOAuth1):
    def setUp(self):
        super().setUp()

        self.request_tokens_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.OAUTH_REQUEST_TOKEN),
            loaded=True,
        )

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.cmd = token.CreateRequestToken(self.app, None)

    def test_create_request_tokens(self):
        arglist = [
            '--consumer-key',
            identity_fakes.consumer_id,
            '--consumer-secret',
            identity_fakes.consumer_secret,
            '--project',
            identity_fakes.project_id,
        ]
        verifylist = [
            ('consumer_key', identity_fakes.consumer_id),
            ('consumer_secret', identity_fakes.consumer_secret),
            ('project', identity_fakes.project_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.request_tokens_mock.create.assert_called_with(
            identity_fakes.consumer_id,
            identity_fakes.consumer_secret,
            identity_fakes.project_id,
        )

        collist = ('expires', 'id', 'key', 'secret')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.request_token_expires,
            identity_fakes.request_token_id,
            identity_fakes.request_token_id,
            identity_fakes.request_token_secret,
        )
        self.assertEqual(datalist, data)
