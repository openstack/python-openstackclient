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

import copy

from keystoneclient import exceptions as identity_exc
from osc_lib import exceptions

from openstackclient.identity.v3 import access_rule
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestAccessRule(identity_fakes.TestIdentityv3):
    def setUp(self):
        super(TestAccessRule, self).setUp()

        identity_manager = self.app.client_manager.identity
        self.access_rules_mock = identity_manager.access_rules
        self.access_rules_mock.reset_mock()
        self.roles_mock = identity_manager.roles
        self.roles_mock.reset_mock()


class TestAccessRuleDelete(TestAccessRule):
    def setUp(self):
        super(TestAccessRuleDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.access_rules_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ACCESS_RULE),
            loaded=True,
        )
        self.access_rules_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = access_rule.DeleteAccessRule(self.app, None)

    def test_access_rule_delete(self):
        arglist = [
            identity_fakes.access_rule_id,
        ]
        verifylist = [('access_rule', [identity_fakes.access_rule_id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.access_rules_mock.delete.assert_called_with(
            identity_fakes.access_rule_id,
        )
        self.assertIsNone(result)

    def test_delete_multi_access_rules_with_exception(self):
        # mock returns for common.get_resource_by_id
        mock_get = self.access_rules_mock.get
        mock_get.side_effect = [
            mock_get.return_value,
            identity_exc.NotFound,
        ]
        arglist = [
            identity_fakes.access_rule_id,
            'nonexistent_access_rule',
        ]
        verifylist = [
            ('access_rule', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 access rules failed to' ' delete.', str(e)
            )

        mock_get.assert_any_call(identity_fakes.access_rule_id)
        mock_get.assert_any_call('nonexistent_access_rule')

        self.assertEqual(2, mock_get.call_count)
        self.access_rules_mock.delete.assert_called_once_with(
            identity_fakes.access_rule_id
        )


class TestAccessRuleList(TestAccessRule):
    def setUp(self):
        super(TestAccessRuleList, self).setUp()

        self.access_rules_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ACCESS_RULE),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = access_rule.ListAccessRule(self.app, None)

    def test_access_rule_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.access_rules_mock.list.assert_called_with(user=None)

        collist = ('ID', 'Service', 'Method', 'Path')
        self.assertEqual(collist, columns)
        datalist = (
            (
                identity_fakes.access_rule_id,
                identity_fakes.access_rule_service,
                identity_fakes.access_rule_method,
                identity_fakes.access_rule_path,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestAccessRuleShow(TestAccessRule):
    def setUp(self):
        super(TestAccessRuleShow, self).setUp()

        self.access_rules_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ACCESS_RULE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = access_rule.ShowAccessRule(self.app, None)

    def test_access_rule_show(self):
        arglist = [
            identity_fakes.access_rule_id,
        ]
        verifylist = [
            ('access_rule', identity_fakes.access_rule_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.access_rules_mock.get.assert_called_with(
            identity_fakes.access_rule_id
        )

        collist = ('id', 'method', 'path', 'service')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.access_rule_id,
            identity_fakes.access_rule_method,
            identity_fakes.access_rule_path,
            identity_fakes.access_rule_service,
        )
        self.assertEqual(datalist, data)
