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

from unittest import mock
import uuid

from osc_lib import exceptions

from openstackclient.network.v2 import network_qos_rule
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


RULE_TYPE_BANDWIDTH_LIMIT = 'bandwidth-limit'
RULE_TYPE_DSCP_MARKING = 'dscp-marking'
RULE_TYPE_MINIMUM_BANDWIDTH = 'minimum-bandwidth'
RULE_TYPE_MINIMUM_PACKET_RATE = 'minimum-packet-rate'
DSCP_VALID_MARKS = [
    0,
    8,
    10,
    12,
    14,
    16,
    18,
    20,
    22,
    24,
    26,
    28,
    30,
    32,
    34,
    36,
    38,
    40,
    46,
    48,
    56,
]


class TestNetworkQosRule(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()
        self.qos_policy = network_fakes.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )


class TestCreateNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):
    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_BANDWIDTH,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.columns = (
            'direction',
            'id',
            'min_kbps',
            'project_id',
            'type',
        )

        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.min_kbps,
            self.new_rule.project_id,
            self.new_rule.type,
        )
        self.network_client.create_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            '--type',
            RULE_TYPE_MINIMUM_BANDWIDTH,
            '--min-kbps',
            str(self.new_rule.min_kbps),
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
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_minimum_bandwidth_rule.assert_called_once_with(
            self.qos_policy.id,
            **{
                'min_kbps': self.new_rule.min_kbps,
                'direction': self.new_rule.direction,
            },
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type',
            RULE_TYPE_MINIMUM_BANDWIDTH,
            '--max-kbps',
            '10000',
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
            msg = (
                'Failed to create Network QoS rule: "Create" rule command '
                'for type "minimum-bandwidth" requires arguments: '
                'direction, min_kbps'
            )
            self.assertEqual(msg, str(e))


class TestCreateNetworkQosRuleMinimumPacketRate(TestNetworkQosRule):
    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_PACKET_RATE,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.columns = (
            'direction',
            'id',
            'min_kpps',
            'project_id',
            'type',
        )

        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.min_kpps,
            self.new_rule.project_id,
            self.new_rule.type,
        )
        self.network_client.create_qos_minimum_packet_rate_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            '--type',
            RULE_TYPE_MINIMUM_PACKET_RATE,
            '--min-kpps',
            str(self.new_rule.min_kpps),
            '--egress',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_MINIMUM_PACKET_RATE),
            ('min_kpps', self.new_rule.min_kpps),
            ('egress', True),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_minimum_packet_rate_rule.assert_called_once_with(  # noqa: E501
            self.qos_policy.id,
            **{
                'min_kpps': self.new_rule.min_kpps,
                'direction': self.new_rule.direction,
            },
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type',
            RULE_TYPE_MINIMUM_PACKET_RATE,
            '--min-kbps',
            '10000',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_MINIMUM_PACKET_RATE),
            ('min_kbps', 10000),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = (
                'Failed to create Network QoS rule: "Create" rule command '
                'for type "minimum-packet-rate" requires arguments: '
                'direction, min_kpps'
            )
            self.assertEqual(msg, str(e))


class TestCreateNetworkQosRuleDSCPMarking(TestNetworkQosRule):
    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_DSCP_MARKING,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.columns = (
            'dscp_mark',
            'id',
            'project_id',
            'type',
        )

        self.data = (
            self.new_rule.dscp_mark,
            self.new_rule.id,
            self.new_rule.project_id,
            self.new_rule.type,
        )
        self.network_client.create_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            '--type',
            RULE_TYPE_DSCP_MARKING,
            '--dscp-mark',
            str(self.new_rule.dscp_mark),
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_DSCP_MARKING),
            ('dscp_mark', self.new_rule.dscp_mark),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_dscp_marking_rule.assert_called_once_with(
            self.qos_policy.id, **{'dscp_mark': self.new_rule.dscp_mark}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type',
            RULE_TYPE_DSCP_MARKING,
            '--max-kbps',
            '10000',
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
            msg = (
                'Failed to create Network QoS rule: "Create" rule command '
                'for type "dscp-marking" requires arguments: dscp_mark'
            )
            self.assertEqual(msg, str(e))


class TestCreateNetworkQosRuleBandwidtLimit(TestNetworkQosRule):
    def test_check_type_parameters(self):
        pass

    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_BANDWIDTH_LIMIT,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.columns = (
            'direction',
            'id',
            'max_burst_kbps',
            'max_kbps',
            'project_id',
            'type',
        )

        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.max_burst_kbps,
            self.new_rule.max_kbps,
            self.new_rule.project_id,
            self.new_rule.type,
        )
        self.network_client.create_qos_bandwidth_limit_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.CreateNetworkQosRule(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            '--type',
            RULE_TYPE_BANDWIDTH_LIMIT,
            '--max-kbps',
            str(self.new_rule.max_kbps),
            '--egress',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_BANDWIDTH_LIMIT),
            ('max_kbps', self.new_rule.max_kbps),
            ('egress', True),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        rule = network_fakes.create_one_qos_rule(
            {
                'qos_policy_id': self.qos_policy.id,
                'type': RULE_TYPE_BANDWIDTH_LIMIT,
            }
        )
        rule.max_burst_kbps = 0
        expected_data = (
            rule.direction,
            rule.id,
            rule.max_burst_kbps,
            rule.max_kbps,
            rule.project_id,
            rule.type,
        )

        with mock.patch.object(
            self.network_client,
            "create_qos_bandwidth_limit_rule",
            return_value=rule,
        ) as create_qos_bandwidth_limit_rule:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            columns, data = self.cmd.take_action(parsed_args)

        create_qos_bandwidth_limit_rule.assert_called_once_with(
            self.qos_policy.id,
            **{
                'max_kbps': self.new_rule.max_kbps,
                'direction': self.new_rule.direction,
            },
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(expected_data, data)

    def test_create_all_options(self):
        arglist = [
            '--type',
            RULE_TYPE_BANDWIDTH_LIMIT,
            '--max-kbps',
            str(self.new_rule.max_kbps),
            '--max-burst-kbits',
            str(self.new_rule.max_burst_kbps),
            '--egress',
            self.new_rule.qos_policy_id,
        ]

        verifylist = [
            ('type', RULE_TYPE_BANDWIDTH_LIMIT),
            ('max_kbps', self.new_rule.max_kbps),
            ('max_burst_kbits', self.new_rule.max_burst_kbps),
            ('egress', True),
            ('qos_policy', self.new_rule.qos_policy_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_bandwidth_limit_rule.assert_called_once_with(
            self.qos_policy.id,
            **{
                'max_kbps': self.new_rule.max_kbps,
                'max_burst_kbps': self.new_rule.max_burst_kbps,
                'direction': self.new_rule.direction,
            },
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--type',
            RULE_TYPE_BANDWIDTH_LIMIT,
            '--min-kbps',
            '10000',
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
            msg = (
                'Failed to create Network QoS rule: "Create" rule command '
                'for type "bandwidth-limit" requires arguments: max_kbps'
            )
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_BANDWIDTH,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.delete_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_minimum_bandwidth_rule = (
            network_fakes.get_qos_rules(qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app, None)

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
        self.network_client.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False
        )
        self.network_client.delete_qos_minimum_bandwidth_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
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

        self.network_client.delete_qos_minimum_bandwidth_rule.side_effect = (
            Exception('Error message')
        )
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = 'Failed to delete Network QoS rule ID "{rule}": {e}'.format(
                rule=self.new_rule.id,
                e='Error message',
            )
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleMinimumPacketRate(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_PACKET_RATE,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.delete_qos_minimum_packet_rate_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_minimum_packet_rate_rule = (
            network_fakes.get_qos_rules(qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app, None)

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
        self.network_client.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False
        )
        self.network_client.delete_qos_minimum_packet_rate_rule.assert_called_once_with(  # noqa: E501
            self.new_rule.id, self.qos_policy.id
        )
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

        self.network_client.delete_qos_minimum_packet_rate_rule.side_effect = (
            Exception('Error message')
        )
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = 'Failed to delete Network QoS rule ID "{rule}": {e}'.format(
                rule=self.new_rule.id,
                e='Error message',
            )
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleDSCPMarking(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_DSCP_MARKING,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.delete_qos_dscp_marking_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_dscp_marking_rule = (
            network_fakes.get_qos_rules(qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app, None)

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
        self.network_client.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False
        )
        self.network_client.delete_qos_dscp_marking_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
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

        self.network_client.delete_qos_dscp_marking_rule.side_effect = (
            Exception('Error message')
        )
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = 'Failed to delete Network QoS rule ID "{rule}": {e}'.format(
                rule=self.new_rule.id,
                e='Error message',
            )
            self.assertEqual(msg, str(e))


class TestDeleteNetworkQosRuleBandwidthLimit(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_BANDWIDTH_LIMIT,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.delete_qos_bandwidth_limit_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_bandwidth_limit_rule = (
            network_fakes.get_qos_rules(qos_rules=self.new_rule)
        )

        # Get the command object to test
        self.cmd = network_qos_rule.DeleteNetworkQosRule(self.app, None)

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
        self.network_client.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False
        )
        self.network_client.delete_qos_bandwidth_limit_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
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

        self.network_client.delete_qos_bandwidth_limit_rule.side_effect = (
            Exception('Error message')
        )
        try:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            self.cmd.take_action(parsed_args)
        except exceptions.CommandError as e:
            msg = 'Failed to delete Network QoS rule ID "{rule}": {e}'.format(
                rule=self.new_rule.id,
                e='Error message',
            )
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_BANDWIDTH,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.update_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )

        # Get the command object to test
        self.cmd = network_qos_rule.SetNetworkQosRule(self.app, None)

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

        self.network_client.update_qos_minimum_bandwidth_rule.assert_called_with(
            self.new_rule, self.qos_policy.id
        )
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
            '--min-kbps',
            str(self.new_rule.min_kbps),
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
        self.network_client.update_qos_minimum_bandwidth_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs
        )
        self.assertIsNone(result)

        if min_kbps:
            self.new_rule.min_kbps = previous_min_kbps

    def test_set_wrong_options(self):
        arglist = [
            '--max-kbps',
            str(10000),
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
            msg = (
                f'Failed to set Network QoS rule ID "{self.new_rule.id}": Rule type '
                '"minimum-bandwidth" only requires arguments: direction, '
                'min_kbps'
            )
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleMinimumPacketRate(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_PACKET_RATE,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.update_qos_minimum_packet_rate_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_minimum_packet_rate_rule = mock.Mock(
            return_value=self.new_rule
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )

        # Get the command object to test
        self.cmd = network_qos_rule.SetNetworkQosRule(self.app, None)

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

        self.network_client.update_qos_minimum_packet_rate_rule.assert_called_with(
            self.new_rule, self.qos_policy.id
        )
        self.assertIsNone(result)

    def test_set_min_kpps(self):
        self._set_min_kpps()

    def test_set_min_kpps_to_zero(self):
        self._set_min_kpps(min_kpps=0)

    def _set_min_kpps(self, min_kpps=None):
        if min_kpps:
            previous_min_kpps = self.new_rule.min_kpps
            self.new_rule.min_kpps = min_kpps

        arglist = [
            '--min-kpps',
            str(self.new_rule.min_kpps),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('min_kpps', self.new_rule.min_kpps),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'min_kpps': self.new_rule.min_kpps,
        }
        self.network_client.update_qos_minimum_packet_rate_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs
        )
        self.assertIsNone(result)

        if min_kpps:
            self.new_rule.min_kpps = previous_min_kpps

    def test_set_wrong_options(self):
        arglist = [
            '--min-kbps',
            str(10000),
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
            msg = (
                f'Failed to set Network QoS rule ID "{self.new_rule.id}": Rule type '
                '"minimum-packet-rate" only requires arguments: direction, '
                'min_kpps'
            )
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleDSCPMarking(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_DSCP_MARKING,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.update_qos_dscp_marking_rule = mock.Mock(
            return_value=None
        )
        self.network_client.find_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )

        # Get the command object to test
        self.cmd = network_qos_rule.SetNetworkQosRule(self.app, None)

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

        self.network_client.update_qos_dscp_marking_rule.assert_called_with(
            self.new_rule, self.qos_policy.id
        )
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
            '--dscp-mark',
            str(self.new_rule.dscp_mark),
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
        self.network_client.update_qos_dscp_marking_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs
        )
        self.assertIsNone(result)

        if dscp_mark:
            self.new_rule.dscp_mark = previous_dscp_mark

    def test_set_wrong_options(self):
        arglist = [
            '--max-kbps',
            str(10000),
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
            msg = (
                f'Failed to set Network QoS rule ID "{self.new_rule.id}": Rule type '
                '"dscp-marking" only requires arguments: dscp_mark'
            )
            self.assertEqual(msg, str(e))


class TestSetNetworkQosRuleBandwidthLimit(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_BANDWIDTH_LIMIT,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.network_client.update_qos_bandwidth_limit_rule.return_value = None
        self.network_client.find_qos_bandwidth_limit_rule.return_value = (
            self.new_rule
        )
        self.network_client.find_qos_policy.return_value = self.qos_policy

        self.cmd = network_qos_rule.SetNetworkQosRule(self.app, None)

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

        self.network_client.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id
        )
        self.assertIsNone(result)

    def test_set_max_kbps(self):
        self._set_max_kbps()

    def test_set_max_kbps_to_zero(self):
        self._set_max_kbps(max_kbps=0)

    def _reset_max_kbps(self, max_kbps):
        self.new_rule.max_kbps = max_kbps

    def _set_max_kbps(self, max_kbps=None):
        if max_kbps:
            self.addCleanup(self._reset_max_kbps, self.new_rule.max_kbps)
            self.new_rule.max_kbps = max_kbps

        arglist = [
            '--max-kbps',
            str(self.new_rule.max_kbps),
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
        self.network_client.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs
        )
        self.assertIsNone(result)

    def test_set_max_burst_kbits(self):
        self._set_max_burst_kbits()

    def test_set_max_burst_kbits_to_zero(self):
        self._set_max_burst_kbits(max_burst_kbits=0)

    def _reset_max_burst_kbits(self, max_burst_kbits):
        self.new_rule.max_burst_kbps = max_burst_kbits

    def _set_max_burst_kbits(self, max_burst_kbits=None):
        if max_burst_kbits:
            self.addCleanup(
                self._reset_max_burst_kbits, self.new_rule.max_burst_kbps
            )
            self.new_rule.max_burst_kbps = max_burst_kbits

        arglist = [
            '--max-burst-kbits',
            str(self.new_rule.max_burst_kbps),
            self.new_rule.qos_policy_id,
            self.new_rule.id,
        ]
        verifylist = [
            ('max_burst_kbits', self.new_rule.max_burst_kbps),
            ('qos_policy', self.new_rule.qos_policy_id),
            ('id', self.new_rule.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'max_burst_kbps': self.new_rule.max_burst_kbps,
        }
        self.network_client.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs
        )
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
            f'--{direction}',
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
        self.network_client.update_qos_bandwidth_limit_rule.assert_called_with(
            self.new_rule, self.qos_policy.id, **attrs
        )
        self.assertIsNone(result)

    def test_set_wrong_options(self):
        arglist = [
            '--min-kbps',
            str(10000),
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
            msg = (
                f'Failed to set Network QoS rule ID "{self.new_rule.id}": Rule type '
                '"bandwidth-limit" only requires arguments: direction, '
                'max_burst_kbps, max_kbps'
            )
            self.assertEqual(msg, str(e))


class TestListNetworkQosRule(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        self.qos_policy.rules = [
            {
                'max_kbps': 1024,
                'max_burst_kbps': 1024,
                'direction': 'egress',
                'id': 'qos-rule-id-' + uuid.uuid4().hex,
                'qos_policy_id': self.qos_policy.id,
                'type': 'bandwidth_limit',
            },
            {
                'dscp_mark': 0,
                'id': 'qos-rule-id-' + uuid.uuid4().hex,
                'qos_policy_id': self.qos_policy.id,
                'type': 'dscp_marking',
            },
            {
                'min_kbps': 1024,
                'direction': 'egress',
                'id': 'qos-rule-id-' + uuid.uuid4().hex,
                'qos_policy_id': self.qos_policy.id,
                'type': 'minimum_bandwidth',
            },
            {
                'min_kpps': 2800,
                'direction': 'egress',
                'id': 'qos-rule-id-' + uuid.uuid4().hex,
                'qos_policy_id': self.qos_policy.id,
                'type': 'minimum_packet_rate',
            },
        ]
        self.columns = (
            'ID',
            'QoS Policy ID',
            'Type',
            'Max Kbps',
            'Max Burst Kbits',
            'Min Kbps',
            'Min Kpps',
            'DSCP mark',
            'Direction',
        )
        self.data = []
        for index in range(len(self.qos_policy.rules)):
            self.data.append(
                (
                    self.qos_policy.rules[index]['id'],
                    self.qos_policy.id,
                    self.qos_policy.rules[index]['type'],
                    self.qos_policy.rules[index].get('max_kbps', ''),
                    self.qos_policy.rules[index].get('max_burst_kbps', ''),
                    self.qos_policy.rules[index].get('min_kbps', ''),
                    self.qos_policy.rules[index].get('min_kpps', ''),
                    self.qos_policy.rules[index].get('dscp_mark', ''),
                    self.qos_policy.rules[index].get('direction', ''),
                )
            )
        self.cmd = network_qos_rule.ListNetworkQosRule(self.app, None)

    def test_qos_rule_list(self):
        arglist = [self.qos_policy.id]
        verifylist = [
            ('qos_policy', self.qos_policy.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_qos_policy.assert_called_once_with(
            self.qos_policy.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        list_data = list(data)
        self.assertEqual(len(self.data), len(list_data))
        for index in range(len(list_data)):
            self.assertEqual(self.data[index], list_data[index])


class TestShowNetworkQosRuleMinimumBandwidth(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_BANDWIDTH,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'direction',
            'id',
            'min_kbps',
            'project_id',
            'type',
        )
        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.min_kbps,
            self.new_rule.project_id,
            self.new_rule.type,
        )

        self.network_client.get_qos_minimum_bandwidth_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

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

        self.network_client.get_qos_minimum_bandwidth_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))


class TestShowNetworkQosRuleMinimumPacketRate(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_MINIMUM_PACKET_RATE,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'direction',
            'id',
            'min_kpps',
            'project_id',
            'type',
        )
        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.min_kpps,
            self.new_rule.project_id,
            self.new_rule.type,
        )

        self.network_client.get_qos_minimum_packet_rate_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

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

        self.network_client.get_qos_minimum_packet_rate_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))


class TestShowNetworkQosDSCPMarking(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_DSCP_MARKING,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'dscp_mark',
            'id',
            'project_id',
            'type',
        )
        self.data = (
            self.new_rule.dscp_mark,
            self.new_rule.id,
            self.new_rule.project_id,
            self.new_rule.type,
        )

        self.network_client.get_qos_dscp_marking_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

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

        self.network_client.get_qos_dscp_marking_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))


class TestShowNetworkQosBandwidthLimit(TestNetworkQosRule):
    def setUp(self):
        super().setUp()
        attrs = {
            'qos_policy_id': self.qos_policy.id,
            'type': RULE_TYPE_BANDWIDTH_LIMIT,
        }
        self.new_rule = network_fakes.create_one_qos_rule(attrs)
        self.qos_policy.rules = [self.new_rule]
        self.columns = (
            'direction',
            'id',
            'max_burst_kbps',
            'max_kbps',
            'project_id',
            'type',
        )
        self.data = (
            self.new_rule.direction,
            self.new_rule.id,
            self.new_rule.max_burst_kbps,
            self.new_rule.max_kbps,
            self.new_rule.project_id,
            self.new_rule.type,
        )

        self.network_client.get_qos_bandwidth_limit_rule = mock.Mock(
            return_value=self.new_rule
        )

        # Get the command object to test
        self.cmd = network_qos_rule.ShowNetworkQosRule(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

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

        self.network_client.get_qos_bandwidth_limit_rule.assert_called_once_with(
            self.new_rule.id, self.qos_policy.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))
