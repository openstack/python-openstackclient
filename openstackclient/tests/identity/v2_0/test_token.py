#   Copyright 2014 eBay Inc.
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

import mock

from openstackclient.identity.v2_0 import token
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


class TestToken(identity_fakes.TestIdentityv2):

    def setUp(self):
        super(TestToken, self).setUp()

        # Get a shortcut to the Service Catalog Mock
        self.sc_mock = mock.Mock()
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.service_catalog = self.sc_mock


class TestTokenIssue(TestToken):

    def setUp(self):
        super(TestTokenIssue, self).setUp()

        self.sc_mock.get_token.return_value = identity_fakes.TOKEN
        self.cmd = token.IssueToken(self.app, None)

    def test_token_issue(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.sc_mock.get_token.assert_called_with()

        collist = ('expires', 'id', 'project_id', 'user_id')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.token_expires,
            identity_fakes.token_id,
            identity_fakes.project_id,
            identity_fakes.user_id,
        )
        self.assertEqual(datalist, data)


class TestTokenRevoke(TestToken):

    TOKEN = 'fob'

    def setUp(self):
        super(TestTokenRevoke, self).setUp()
        self.tokens_mock = self.app.client_manager.identity.tokens
        self.tokens_mock.reset_mock()
        self.tokens_mock.delete.return_value = True
        self.cmd = token.RevokeToken(self.app, None)

    def test_token_revoke(self):
        arglist = [self.TOKEN]
        verifylist = [('token', self.TOKEN)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.tokens_mock.delete.assert_called_with(self.TOKEN)
