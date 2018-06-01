# Copyright (c) 2016, Intel Corporation.
# All Rights Reserved.
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

import mock

from osc_lib import exceptions

from openstackclient.network.v2 import network_qos_rule
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


RULE_TYPE_BANDWIDTH_LIMIT = 'bandwidth-limit'
RULE_TYPE_DSCP_MARKING = 'dscp-marking'
RULE_TYPE_MINIMUM_BANDWIDTH = 'minimum-bandwidth'
DSCP_VALID_MARKS = [0, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32,
                    34, 36, 38, 40, 46, 48, 56]


class TestNetworkQosRule(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkQosRule, self).setUp()
        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        self.qos_policy = (network_fakes.FakeNetworkQosPolicy.
                           create_one_qos_policy())
        self.network.find_qos_policy = mock.Mock(return_value=self.qos_policy)


class TestCreateNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):

    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super(TestCreateNetworkQosRuleMinimumBandwidth, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_MINIMUM_BANDWIDTH}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.columns = (
            'direction',
            'id',
            'min_kbps',
            'project_id',
            'qos_policy_id',
            'type'
        )

        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.min_kbps,
            self.new_rule.project_id,
            self.new_rule.qos_policy_id,
            self.new_rule.type,
        )
        self.network.create_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule)

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app,
                                                         self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            '--type', RULE_TYPE_MINIMUM_BANDWIDTH,
            '--min-kbps', str(self.new_rule.min_kbps),
            '--egress',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_MINIMUM_BANDWIDTH),
            ('min_kbps', self.new_rule.min_kbps),
            ('egress', True),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_qos_minimum_bandwidth_rule.assert_called_once_with(
            self.qos_policy.id,
            **{'min_kbps': self.new_rule.min_kbps,
               'direction': self.new_rule.direction}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type', RULE_TYPE_MINIMUM_BANDWIDTH,
            '--max-kbps', '10000',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_MINIMUM_BANDWIDTH),
            ('max_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('"Create" rule command for type "minimum-bandwidth" '
                   'requires arguments: direction, min_kbps')
            self.assertEqual(msg, str(e))


class TestCreateNetworkQosRuleDSCPMarking(TestNetworkQosRule):

    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super(TestCreateNetworkQosRuleDSCPMarking, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_DSCP_MARKING}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.columns = (
            'dscp_mark',
            'id',
            'project_id',
            'qos_policy_id',
            'type'
        )

        self.data = (
            self.new_rule.dscp_mark,
            self.new_rule.id,
            self.new_rule.project_id,
            self.new_rule.qos_policy_id,
            self.new_rule.type,
        )
        self.network.create_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule)

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app,
                                                         self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            '--type', RULE_TYPE_DSCP_MARKING,
            '--dscp-mark', str(self.new_rule.dscp_mark),
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_DSCP_MARKING),
            ('dscp_mark', self.new_rule.dscp_mark),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_qos_dscp_marking_rule.assert_called_once_with(
            self.qos_policy.id,
            **{'dscp_mark': self.new_rule.dscp_mark}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type', RULE_TYPE_DSCP_MARKING,
            '--max-kbps', '10000',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_DSCP_MARKING),
            ('max_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('"Create" rule command for type "dscp-marking" '
                   'requires arguments: dscp_mark')
            self.assertEqual(msg, str(e))


class TestCreateNetworkQosRuleBandwidtLimit(TestNetworkQosRule):

    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super(TestCreateNetworkQosRuleBandwidtLimit, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_BANDWIDTH_LIMIT}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.columns = (
            'direction',
            'id',
            'max_burst_kbits',
            'max_kbps',
            'project_id',
            'qos_policy_id',
            'type'
        )

        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.max_burst_kbits,
            self.new_rule.max_kbps,
            self.new_rule.project_id,
            self.new_rule.qos_policy_id,
            self.new_rule.type,
        )
        self.network.create_qos_bandwidth_limit_rule = mock.Mock(
            return_value=self.new_rule)

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app,
                                                         self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            '--type', RULE_TYPE_BANDWIDTH_LIMIT,
            '--max-kbps', str(self.new_rule.max_kbps),
            '--egress',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_BANDWIDTH_LIMIT),
            ('max_kbps', self.new_rule.max_kbps),
            ('egress', True),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            {'qos_policy_id': self.qos_policy.id,
             'type': RULE_TYPE_BANDWIDTH_LIMIT})
        rule.max_burst_kbits = 0
        expected_data = (
            rule.direction,
            rule.id,
            rule.max_burst_kbits,
            rule.max_kbps,
            rule.project_id,
            rule.qos_policy_id,
            rule.type,
        )

        with mock.patch.object(
                self.network, "create_qos_bandwidth_limit_rule",
                return_value=rule) as create_qos_bandwidth_limit_rule:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            columns, data = (self.cmd.take_action(parsed_args))

        create_qos_bandwidth_limit_rule.assert_called_once_with(
            self.qos_policy.id,
            **{'max_kbps': self.new_rule.max_kbps,
               'direction': self.new_rule.direction}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(expected_data, data)

    def test_create_all_options(self):
        arglist = [
            '--type', RULE_TYPE_BANDWIDTH_LIMIT,
            '--max-kbps', str(self.new_rule.max_kbps),
            '--max-burst-kbits', str(self.new_rule.max_burst_kbits),
            '--egress',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_BANDWIDTH_LIMIT),
            ('max_kbps', self.new_rule.max_kbps),
            ('max_burst_kbits', self.new_rule.max_burst_kbits),
            ('egress', True),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_qos_bandwidth_limit_rule.assert_called_once_with(
            self.qos_policy.id,
            **{'max_kbps': self.new_rule.max_kbps,
               'max_burst_kbps': self.new_rule.max_burst_kbits,
               'direction': self.new_rule.direction}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type', RULE_TYPE_BANDWIDTH_LIMIT,
            '--min-kbps', '10000',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_BANDWIDTH_LIMIT),
            ('min_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('"Create" rule command for type "bandwidth-limit" '
                   'requires arguments: max_kbps')
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):

    def setUp(self):
        super(TestDeleteNetworkQosRuleMinimumBandwidth, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_MINIMUM_BANDWIDTH}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network.delete_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=None)
        self.network.find_qos_minimum_bandwidth_rule = (
            network_fakes.FakeNetworkQosRule.get_qos_rules(
                qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app,
                                                         self.namespace)

    def test_qos_policy_delete(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False)
        self.network.delete_qos_minimum_bandwidth_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id)
        self.assertIsNone(result)

    def test_qos_policy_delete_error(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        self.network.delete_qos_minimum_bandwidth_rule.side_effect = \
            Exception('Error message')
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('Failed to delete Network QoS rule ID "%(rule)s": %(e)s' %
                   {'rule': self.new_rule.id, 'e': 'Error message'})
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleDSCPMarking(TestNetworkQosRule):

    def setUp(self):
        super(TestDeleteNetworkQosRuleDSCPMarking, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_DSCP_MARKING}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network.delete_qos_dscp_marking_rule = mock.Mock(
            return_value=None)
        self.network.find_qos_dscp_marking_rule = (
            network_fakes.FakeNetworkQosRule.get_qos_rules(
                qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app,
                                                         self.namespace)

    def test_qos_policy_delete(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False)
        self.network.delete_qos_dscp_marking_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id)
        self.assertIsNone(result)

    def test_qos_policy_delete_error(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        self.network.delete_qos_dscp_marking_rule.side_effect = \
            Exception('Error message')
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('Failed to delete Network QoS rule ID "%(rule)s": %(e)s' %
                   {'rule': self.new_rule.id, 'e': 'Error message'})
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleBandwidthLimit(TestNetworkQosRule):

    def setUp(self):
        super(TestDeleteNetworkQosRuleBandwidthLimit, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_BANDWIDTH_LIMIT}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network.delete_qos_bandwidth_limit_rule = mock.Mock(
            return_value=None)
        self.network.find_qos_bandwidth_limit_rule = (
            network_fakes.FakeNetworkQosRule.get_qos_rules(
                qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app,
                                                         self.namespace)

    def test_qos_policy_delete(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False)
        self.network.delete_qos_bandwidth_limit_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id)
        self.assertIsNone(result)

    def test_qos_policy_delete_error(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        self.network.delete_qos_bandwidth_limit_rule.side_effect = \
            Exception('Error message')
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('Failed to delete Network QoS rule ID "%(rule)s": %(e)s' %
                   {'rule': self.new_rule.id, 'e': 'Error message'})
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):

    def setUp(self):
        super(TestSetNetworkQosRuleMinimumBandwidth, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_MINIMUM_BANDWIDTH}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs=attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network.update_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=None)
        self.network.find_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule)
        self.network.find_qos_policy = mock.Mock(
            return_value=self.qos_policy)

        # Get the command object to test
        self.cmd = (network_qos_rule.SetNetworkQosRule(self.app,
                                                       self.namespace))

    def test_set_nothing(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.update_qos_minimum_bandwidth_rule.assert_called_with(
            self.new_rule, self.qos_policy.id)
        self.assertIsNone(result)

    def test_set_min_kbps(self):
        self._set_min_kbps()

    def test_set_min_kbps_to_zero(self):
        self._set_min_kbps(min_kbps=0)

    def _set_min_kbps(self, min_kbps=None):
        if min_kbps:
            previous_min_kbps = self.new_rule.min_kbps
            self.new_rule.min_kbps = min_kbps

        arglist = [
            '--min-kbps', str(self.new_rule.min_kbps),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('min_kbps', self.new_rule.min_kbps),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'min_kbps': self.new_rule.min_kbps,
        }
        self.network.update_qos_minimum_bandwidth_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs)
        self.assertIsNone(result)

        if min_kbps:
            self.new_rule.min_kbps = previous_min_kbps

    def test_set_wrong_options(self):
        arglist = [
            '--max-kbps', str(10000),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('max_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('Failed to set Network QoS rule ID "%(rule)s": Rule type '
                   '"minimum-bandwidth" only requires arguments: direction, '
                   'min_kbps' % {'rule': self.new_rule.id})
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleDSCPMarking(TestNetworkQosRule):

    def setUp(self):
        super(TestSetNetworkQosRuleDSCPMarking, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_DSCP_MARKING}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs=attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network.update_qos_dscp_marking_rule = mock.Mock(
            return_value=None)
        self.network.find_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule)
        self.network.find_qos_policy = mock.Mock(
            return_value=self.qos_policy)

        # Get the command object to test
        self.cmd = (network_qos_rule.SetNetworkQosRule(self.app,
                                                       self.namespace))

    def test_set_nothing(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.update_qos_dscp_marking_rule.assert_called_with(
            self.new_rule, self.qos_policy.id)
        self.assertIsNone(result)

    def test_set_dscp_mark(self):
        self._set_dscp_mark()

    def test_set_dscp_mark_to_zero(self):
        self._set_dscp_mark(dscp_mark=0)

    def _set_dscp_mark(self, dscp_mark=None):
        if dscp_mark:
            previous_dscp_mark = self.new_rule.dscp_mark
            self.new_rule.dscp_mark = dscp_mark

        arglist = [
            '--dscp-mark', str(self.new_rule.dscp_mark),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('dscp_mark', self.new_rule.dscp_mark),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'dscp_mark': self.new_rule.dscp_mark,
        }
        self.network.update_qos_dscp_marking_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs)
        self.assertIsNone(result)

        if dscp_mark:
            self.new_rule.dscp_mark = previous_dscp_mark

    def test_set_wrong_options(self):
        arglist = [
            '--max-kbps', str(10000),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('max_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('Failed to set Network QoS rule ID "%(rule)s": Rule type '
                   '"dscp-marking" only requires arguments: dscp_mark' %
                   {'rule': self.new_rule.id})
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleBandwidthLimit(TestNetworkQosRule):

    def setUp(self):
        super(TestSetNetworkQosRuleBandwidthLimit, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_BANDWIDTH_LIMIT}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs=attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network.update_qos_bandwidth_limit_rule = mock.Mock(
            return_value=None)
        self.network.find_qos_bandwidth_limit_rule = mock.Mock(
            return_value=self.new_rule)
        self.network.find_qos_policy = mock.Mock(
            return_value=self.qos_policy)

        # Get the command object to test
        self.cmd = (network_qos_rule.SetNetworkQosRule(self.app,
                                                       self.namespace))

    def test_set_nothing(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id)
        self.assertIsNone(result)

    def test_set_max_kbps(self):
        self._set_max_kbps()

    def test_set_max_kbps_to_zero(self):
        self._set_max_kbps(max_kbps=0)

    def _reset_max_kbps(self, max_kbps):
        self.new_rule.max_kbps = max_kbps

    def _set_max_kbps(self, max_kbps=None):
        if max_kbps:
            self.addCleanup(self._reset_max_kbps,
                            self.new_rule.max_kbps)
            self.new_rule.max_kbps = max_kbps

        arglist = [
            '--max-kbps', str(self.new_rule.max_kbps),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('max_kbps', self.new_rule.max_kbps),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'max_kbps': self.new_rule.max_kbps,
        }
        self.network.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs)
        self.assertIsNone(result)

    def test_set_max_burst_kbits(self):
        self._set_max_burst_kbits()

    def test_set_max_burst_kbits_to_zero(self):
        self._set_max_burst_kbits(max_burst_kbits=0)

    def _reset_max_burst_kbits(self, max_burst_kbits):
        self.new_rule.max_burst_kbits = max_burst_kbits

    def _set_max_burst_kbits(self, max_burst_kbits=None):
        if max_burst_kbits:
            self.addCleanup(self._reset_max_burst_kbits,
                            self.new_rule.max_burst_kbits)
            self.new_rule.max_burst_kbits = max_burst_kbits

        arglist = [
            '--max-burst-kbits', str(self.new_rule.max_burst_kbits),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('max_burst_kbits', self.new_rule.max_burst_kbits),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'max_burst_kbps': self.new_rule.max_burst_kbits,
        }
        self.network.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs)
        self.assertIsNone(result)

    def test_set_direction_egress(self):
        self._set_direction('egress')

    def test_set_direction_ingress(self):
        self._set_direction('ingress')

    def _reset_direction(self, direction):
        self.new_rule.direction = direction

    def _set_direction(self, direction):
        self.addCleanup(self._reset_direction, self.new_rule.direction)

        arglist = [
            '--%s' % direction,
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            (direction, True),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'direction': direction,
        }
        self.network.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs)
        self.assertIsNone(result)

    def test_set_wrong_options(self):
        arglist = [
            '--min-kbps', str(10000),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('min_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = ('Failed to set Network QoS rule ID "%(rule)s": Rule type '
                   '"bandwidth-limit" only requires arguments: direction, '
                   'max_burst_kbps, max_kbps' % {'rule': self.new_rule.id})
            self.assertEqual(msg, str(e))


class TestListNetworkQosRule(TestNetworkQosRule):

    def setUp(self):
        super(TestListNetworkQosRule, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_MINIMUM_BANDWIDTH}
        self.new_rule_min_bw = (network_fakes.FakeNetworkQosRule.
                                create_one_qos_rule(attrs=attrs))
        attrs['type'] = RULE_TYPE_DSCP_MARKING
        self.new_rule_dscp_mark = (network_fakes.FakeNetworkQosRule.
                                   create_one_qos_rule(attrs=attrs))
        attrs['type'] = RULE_TYPE_BANDWIDTH_LIMIT
        self.new_rule_max_bw = (network_fakes.FakeNetworkQosRule.
                                create_one_qos_rule(attrs=attrs))
        self.qos_policy.rules = [self.new_rule_min_bw,
                                 self.new_rule_dscp_mark,
                                 self.new_rule_max_bw]
        self.network.find_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule_min_bw)
        self.network.find_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule_dscp_mark)
        self.network.find_qos_bandwidth_limit_rule = mock.Mock(
            return_value=self.new_rule_max_bw)
        self.columns = (
            'ID',
            'QoS Policy ID',
            'Type',
            'Max Kbps',
            'Max Burst Kbits',
            'Min Kbps',
            'DSCP mark',
            'Direction',
        )
        self.data = []
        for index in range(len(self.qos_policy.rules)):
            self.data.append((
                self.qos_policy.rules[index].id,
                self.qos_policy.rules[index].qos_policy_id,
                self.qos_policy.rules[index].type,
                getattr(self.qos_policy.rules[index], 'max_kbps', ''),
                getattr(self.qos_policy.rules[index], 'max_burst_kbps', ''),
                getattr(self.qos_policy.rules[index], 'min_kbps', ''),
                getattr(self.qos_policy.rules[index], 'dscp_mark', ''),
                getattr(self.qos_policy.rules[index], 'direction', ''),
            ))
        # Get the command object to test
        self.cmd = network_qos_rule.ListNetworkQosRule(self.app,
                                                       self.namespace)

    def test_qos_rule_list(self):
        arglist = [
            self.qos_policy.id
        ]
        verifylist = [
            ('qos_policy', self.qos_policy.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        list_data = list(data)
        self.assertEqual(len(self.data), len(list_data))
        for index in range(len(list_data)):
            self.assertEqual(self.data[index], list_data[index])


class TestShowNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):

    def setUp(self):
        super(TestShowNetworkQosRuleMinimumBandwidth, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_MINIMUM_BANDWIDTH}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'direction',
            'id',
            'min_kbps',
            'project_id',
            'qos_policy_id',
            'type'
        )
        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.min_kbps,
            self.new_rule.project_id,
            self.new_rule.qos_policy_id,
            self.new_rule.type,
        )

        self.network.get_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule)

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app,
                                                       self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.get_qos_minimum_bandwidth_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))


class TestShowNetworkQosDSCPMarking(TestNetworkQosRule):

    def setUp(self):
        super(TestShowNetworkQosDSCPMarking, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_DSCP_MARKING}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'dscp_mark',
            'id',
            'project_id',
            'qos_policy_id',
            'type'
        )
        self.data = (
            self.new_rule.dscp_mark,
            self.new_rule.id,
            self.new_rule.project_id,
            self.new_rule.qos_policy_id,
            self.new_rule.type,
        )

        self.network.get_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule)

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app,
                                                       self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.get_qos_dscp_marking_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))


class TestShowNetworkQosBandwidthLimit(TestNetworkQosRule):

    def setUp(self):
        super(TestShowNetworkQosBandwidthLimit, self).setUp()
        attrs = {'qos_policy_id': self.qos_policy.id,
                 'type': RULE_TYPE_BANDWIDTH_LIMIT}
        self.new_rule = network_fakes.FakeNetworkQosRule.create_one_qos_rule(
            attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'direction',
            'id',
            'max_burst_kbits',
            'max_kbps',
            'project_id',
            'qos_policy_id',
            'type'
        )
        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.max_burst_kbits,
            self.new_rule.max_kbps,
            self.new_rule.project_id,
            self.new_rule.qos_policy_id,
            self.new_rule.type,
        )

        self.network.get_qos_bandwidth_limit_rule = mock.Mock(
            return_value=self.new_rule)

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app,
                                                       self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.get_qos_bandwidth_limit_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))
