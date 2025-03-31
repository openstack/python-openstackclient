#   Copyright 2019 SUSE LLC
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

from unittest.mock import call

from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import access_rule as _access_rule
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity.v3 import access_rule
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestAccessRuleDelete(identity_fakes.TestIdentityv3):
    access_rule = sdk_fakes.generate_fake_resource(_access_rule.AccessRule)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.get_access_rule.return_value = (
            self.access_rule
        )
        self.identity_sdk_client.delete_access_rule.return_value = None

        # Get the command object to test
        self.cmd = access_rule.DeleteAccessRule(self.app, None)

    def test_access_rule_delete(self):
        arglist = [self.access_rule.id]
        verifylist = [('access_rule', [self.access_rule.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_access_rule.assert_called_with(
            user_id,
            self.access_rule.id,
        )
        self.assertIsNone(result)

    def test_delete_multi_access_rules_with_exception(self):
        self.identity_sdk_client.get_access_rule.side_effect = [
            self.access_rule,
            sdk_exceptions.NotFoundException,
        ]

        arglist = [
            self.access_rule.id,
            'nonexistent_access_rule',
        ]
        verifylist = [
            ('access_rule', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 access rules failed to delete.', str(e))

        calls = []
        for a in arglist:
            calls.append(call(user_id, a))

        self.identity_sdk_client.get_access_rule.assert_has_calls(calls)

        self.assertEqual(
            2, self.identity_sdk_client.get_access_rule.call_count
        )
        self.identity_sdk_client.delete_access_rule.assert_called_once_with(
            user_id, self.access_rule.id
        )


class TestAccessRuleList(identity_fakes.TestIdentityv3):
    access_rule = sdk_fakes.generate_fake_resource(_access_rule.AccessRule)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.access_rules.return_value = [self.access_rule]

        # Get the command object to test
        self.cmd = access_rule.ListAccessRule(self.app, None)

    def test_access_rule_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.access_rules.assert_called_with(user=user_id)

        collist = ('ID', 'Service', 'Method', 'Path')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.access_rule.id,
                self.access_rule.service,
                self.access_rule.method,
                self.access_rule.path,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestAccessRuleShow(identity_fakes.TestIdentityv3):
    access_rule = sdk_fakes.generate_fake_resource(_access_rule.AccessRule)

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.get_access_rule.return_value = (
            self.access_rule
        )

        # Get the command object to test
        self.cmd = access_rule.ShowAccessRule(self.app, None)

    def test_access_rule_show(self):
        arglist = [
            self.access_rule.id,
        ]
        verifylist = [
            ('access_rule', self.access_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.get_access_rule.assert_called_with(
            user_id, self.access_rule.id
        )

        collist = ('ID', 'Method', 'Path', 'Service')
        self.assertEqual(collist, columns)
        datalist = (
            self.access_rule.id,
            self.access_rule.method,
            self.access_rule.path,
            self.access_rule.service,
        )
        self.assertEqual(datalist, data)
