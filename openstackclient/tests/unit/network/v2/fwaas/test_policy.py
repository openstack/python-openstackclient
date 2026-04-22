# Copyright 2016 FUJITSU LIMITED
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import re
from unittest import mock

from openstack.network.v2 import firewall_policy
from openstack.network.v2 import firewall_rule
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.network.v2.fwaas import policy as fwaas_policy
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as test_utils

CONVERT_MAP = {
    'project': 'project_id',
    'port': 'ports',
    'name': 'name',
    'id': 'id',
    'firewall_rule': 'firewall_rules',
    'description': 'description',
}


def _generate_data(source=None, data=None):
    source = source or {}
    if data:
        source.update(data)
    return tuple(source[key] for key in source)


def _generate_req_and_res(verifylist, response):
    request = dict(verifylist)
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        if re.match('^no_', key) and val is True:
            new_value = None
        elif val is True or val is False:
            new_value = val
        elif key in ('name', 'description'):
            new_value = val
        else:
            new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestFirewallPolicy(network_fakes.TestNetworkV2):
    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))

    def setUp(self):
        super().setUp()

        self.identity_client.projects.get.side_effect = lambda x: mock.Mock(
            id=x
        )
        self.res = 'firewall_policy'
        self.res_plural = 'firewall_policies'
        self.resource = sdk_fakes.generate_fake_resource(
            firewall_policy.FirewallPolicy
        )
        # TODO(slaweq): Remove this "firewall_rules" override once bug
        # https://bugs.launchpad.net/openstacksdk/+bug/2146537 will be fixed in
        # OpenStackSDK
        self.resource['firewall_rules'] = [self.resource['firewall_rules']]

        self.list_headers = (
            'ID',
            'Name',
            'Firewall Rules',
        )
        self.list_data = (
            self.resource['id'],
            self.resource['name'],
            self.resource['firewall_rules'],
        )
        self.headers = tuple(
            (*self.list_headers, 'Description', 'Audited', 'Shared', 'Project')
        )
        self.data = _generate_data(self.resource)
        self.ordered_headers = (
            'Audited',
            'Description',
            'Firewall Rules',
            'ID',
            'Name',
            'Project',
            'Shared',
        )
        self.ordered_data = (
            self.resource['audited'],
            self.resource['description'],
            self.resource['firewall_rules'],
            self.resource['id'],
            self.resource['name'],
            self.resource['project_id'],
            self.resource['shared'],
        )
        self.ordered_columns = (
            'audited',
            'description',
            'firewall_rules',
            'id',
            'name',
            'project_id',
            'shared',
        )


class TestCreateFirewallPolicy(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.create_firewall_policy.return_value = self.resource
        self.mocked = self.network_client.create_firewall_policy
        self.cmd = fwaas_policy.CreateFirewallPolicy(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        pass  # identity_client.projects.get is already mocked in setUp
        # Update response(finally returns 'data')
        self.data = _generate_data(data=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_mandatory_param(self):
        name = 'my-fwg'
        arglist = [
            name,
        ]
        verifylist = [
            ('name', name),
        ]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_rules(self):
        name = 'my-fwg'
        rule1 = 'rule1'
        rule2 = 'rule2'

        def _mock_find_rule(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_rule.side_effect = _mock_find_rule

        arglist = [
            name,
            '--firewall-rule',
            rule1,
            '--firewall-rule',
            rule2,
        ]
        verifylist = [
            ('name', name),
            ('firewall_rule', [rule1, rule2]),
        ]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.assertEqual(2, self.network_client.find_firewall_rule.call_count)

        self.check_results(headers, data, request)

    def test_create_with_all_params(self):
        name = 'my-fwp'
        desc = 'my-desc'
        rule1 = 'rule1'
        rule2 = 'rule2'
        project = 'my-tenant'

        def _mock_find(*args, **kwargs):
            if self.res in args[0]:
                rules = self.resource['firewall_rules']
                return mock.Mock(id=args[0], firewall_rules=rules)
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_policy.side_effect = _mock_find
        self.network_client.find_firewall_rule.side_effect = _mock_find

        arglist = [
            name,
            '--description',
            desc,
            '--firewall-rule',
            rule1,
            '--firewall-rule',
            rule2,
            '--project',
            project,
            '--share',
            '--audited',
        ]
        verifylist = [
            ('name', name),
            ('description', desc),
            ('firewall_rule', [rule1, rule2]),
            ('project', project),
            ('shared', True),
            ('audited', True),
        ]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_firewall_rule_and_no(self):
        name = 'my-fwp'
        rule1 = 'rule1'
        rule2 = 'rule2'
        arglist = [
            name,
            '--firewall-rule',
            rule1,
            '--firewall-rule',
            rule2,
            '--no-firewall-rule',
        ]
        verifylist = [
            ('name', name),
            ('firewall_rule', [rule1, rule2]),
            ('no_firewall_rule', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_shared_and_no_share(self):
        name = 'my-fwp'
        arglist = [
            name,
            '--share',
            '--no-share',
        ]
        verifylist = [
            ('name', name),
            ('shared', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_audited_and_no(self):
        name = 'my-fwp'
        arglist = [
            name,
            '--audited',
            '--no-audited',
        ]
        verifylist = [
            ('name', name),
            ('audited', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestListFirewallPolicy(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.firewall_policies.return_value = [self.resource]
        self.mocked = self.network_client.firewall_policies
        self.cmd = fwaas_policy.ListFirewallPolicy(self.app, None)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.list_headers), headers)
        self.assertEqual([self.list_data], list(data))

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)


class TestShowFirewallPolicy(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.get_firewall_policy.return_value = self.resource
        self.mocked = self.network_client.get_firewall_policy
        self.cmd = fwaas_policy.ShowFirewallPolicy(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_policy.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)


class TestSetFirewallPolicy(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.update_firewall_policy.return_value = self.resource
        self.mocked = self.network_client.update_firewall_policy

        def _mock_find_rule(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        def _mock_find_policy(*args, **kwargs):
            return self.resource

        self.network_client.find_firewall_policy.side_effect = (
            _mock_find_policy
        )
        self.network_client.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = fwaas_policy.SetFirewallPolicy(self.app, None)

    def test_set_name(self):
        target = self.resource['id']
        update = 'change'
        arglist = [target, '--name', update]
        verifylist = [
            (self.res, target),
            ('name', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'name': update})
        self.assertIsNone(result)

    def test_set_options(self):
        target = self.resource['id']
        updated_desc = 'change-desc'
        arglist = [target, '--description', updated_desc, '--share']
        verifylist = [
            (self.res, target),
            ('description', updated_desc),
            ('shared', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, shared=True, description=updated_desc
        )
        self.assertIsNone(result)

    def test_set_rules(self):
        target = self.resource['id']
        rule1 = 'new_rule1'
        rule2 = 'new_rule2'
        arglist = [
            target,
            '--firewall-rule',
            rule1,
            '--firewall-rule',
            rule2,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule1, rule2]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        expect = self.resource['firewall_rules'] + [rule1, rule2]
        body = {'firewall_rules': expect}
        self.mocked.assert_called_once_with(target, **body)
        self.assertEqual(2, self.network_client.find_firewall_rule.call_count)
        self.assertEqual(
            2, self.network_client.find_firewall_policy.call_count
        )
        self.assertIsNone(result)

    def test_set_no_rules(self):
        target = self.resource['id']
        arglist = [target, '--no-firewall-rule']
        verifylist = [
            (self.res, target),
            ('no_firewall_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': []}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_set_rules_and_no_rules(self):
        target = self.resource['id']
        rule1 = 'rule1'
        arglist = [
            target,
            '--firewall-rule',
            rule1,
            '--no-firewall-rule',
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule1]),
            ('no_firewall_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': [rule1]}
        self.mocked.assert_called_once_with(target, **body)
        self.assertEqual(1, self.network_client.find_firewall_rule.call_count)
        self.assertEqual(
            1, self.network_client.find_firewall_policy.call_count
        )
        self.assertIsNone(result)

    def test_set_audited(self):
        target = self.resource['id']
        arglist = [target, '--audited']
        verifylist = [
            (self.res, target),
            ('audited', True),
        ]
        body = {'audited': True}
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_set_no_audited(self):
        target = self.resource['id']
        arglist = [target, '--no-audited']
        verifylist = [
            (self.res, target),
            ('audited', False),
        ]
        body = {'audited': False}
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_set_audited_and_no_audited(self):
        target = self.resource['id']
        arglist = [
            target,
            '--audited',
            '--no-audited',
        ]
        verifylist = [
            (self.res, target),
            ('audited', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_and_raises(self):
        self.network_client.update_firewall_policy.side_effect = Exception
        target = self.resource['id']

        arglist = [target, '--name', 'my-name']
        verifylist = [(self.res, target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestDeleteFirewallPolicy(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.delete_firewall_policy.return_value = {
            self.res: self.resource
        }
        self.mocked = self.network_client.delete_firewall_policy
        self.cmd = fwaas_policy.DeleteFirewallPolicy(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return self.resource

        self.network_client.find_firewall_policy.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_fwaas(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_policy.FirewallPolicy, id=args[0]
            )

        self.network_client.find_firewall_policy.side_effect = _mock_fwaas

        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0][0])
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        def _mock_find(*args, **kwargs):
            if args[0] == target2:
                raise Exception('Not found')
            return self.resource

        self.network_client.find_firewall_policy.side_effect = _mock_find

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestFirewallPolicyInsertRule(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.insert_rule_into_policy.return_value = {
            self.res: self.resource
        }
        self.mocked = self.network_client.insert_rule_into_policy

        def _mock_find_policy(*args, **kwargs):
            return self.resource

        def _mock_find_rule(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_policy.side_effect = (
            _mock_find_policy
        )
        self.network_client.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = fwaas_policy.FirewallPolicyInsertRule(self.app, None)

    def test_insert_firewall_rule(self):
        target = self.resource['id']
        rule = 'new-rule'
        before = 'before'
        after = 'after'
        arglist = [
            target,
            rule,
            '--insert-before',
            before,
            '--insert-after',
            after,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', rule),
            ('insert_before', before),
            ('insert_after', after),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {
            'firewall_rule_id': rule,
            'insert_before': before,
            'insert_after': after,
        }
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
        self.assertEqual(
            1, self.network_client.find_firewall_policy.call_count
        )
        self.assertEqual(3, self.network_client.find_firewall_rule.call_count)

    def test_insert_with_no_firewall_rule(self):
        target = self.resource['id']
        arglist = [
            target,
        ]
        verifylist = [
            (self.res, target),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestFirewallPolicyRemoveRule(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.remove_rule_from_policy.return_value = {
            self.res: self.resource
        }
        self.mocked = self.network_client.remove_rule_from_policy

        def _mock_find_policy(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_policy.side_effect = (
            _mock_find_policy
        )
        self.network_client.find_firewall_rule.side_effect = _mock_find_policy

        self.cmd = fwaas_policy.FirewallPolicyRemoveRule(self.app, None)

    def test_remove_firewall_rule(self):
        target = self.resource['id']
        rule = 'remove-rule'
        arglist = [
            target,
            rule,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', rule),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        body = {'firewall_rule_id': rule}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
        self.assertEqual(
            1, self.network_client.find_firewall_policy.call_count
        )
        self.assertEqual(1, self.network_client.find_firewall_rule.call_count)

    def test_remove_with_no_firewall_rule(self):
        target = self.resource['id']
        arglist = [
            target,
        ]
        verifylist = [
            (self.res, target),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestUnsetFirewallPolicy(TestFirewallPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.update_firewall_policy.return_value = {
            self.res: self.resource
        }
        self.mocked = self.network_client.update_firewall_policy

        def _mock_find_rule(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        def _mock_find_policy(*args, **kwargs):
            return mock.Mock(
                id=args[0],
                firewall_rules=self.resource['firewall_rules'],
            )

        self.network_client.find_firewall_policy.side_effect = (
            _mock_find_policy
        )
        self.network_client.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = fwaas_policy.UnsetFirewallPolicy(self.app, None)

    def test_unset_shared(self):
        target = self.resource['id']
        arglist = [
            target,
            '--share',
        ]
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(fwaas_policy.LOG, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)
            mock_warning.assert_called_once_with(
                'The --share option is deprecated, please use '
                '"firewall policy set --no-share" instead.'
            )
        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_unset_audited(self):
        target = self.resource['id']
        arglist = [
            target,
            '--audited',
        ]
        verifylist = [
            (self.res, target),
            ('audited', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'audited': False}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_unset_firewall_rule_not_matched(self):
        self.resource['firewall_rules'] = ['old_rule']
        target = self.resource['id']
        rule = 'new_rule'
        arglist = [
            target,
            '--firewall-rule',
            rule,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': self.resource['firewall_rules']}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)

    def test_unset_firewall_rule_matched(self):
        self.resource['firewall_rules'] = ['rule1', 'rule2']
        target = self.resource['id']
        rule = 'rule1'
        arglist = [
            target,
            '--firewall-rule',
            rule,
        ]
        verifylist = [
            (self.res, target),
            ('firewall_rule', [rule]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': ['rule2']}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
        self.assertEqual(
            2, self.network_client.find_firewall_policy.call_count
        )
        self.assertEqual(1, self.network_client.find_firewall_rule.call_count)

    def test_unset_all_firewall_rule(self):
        target = self.resource['id']
        arglist = [
            target,
            '--all-firewall-rule',
        ]
        verifylist = [
            (self.res, target),
            ('all_firewall_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        body = {'firewall_rules': []}
        self.mocked.assert_called_once_with(target, **body)
        self.assertIsNone(result)
