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

from openstackclient.network.v2 import network_qos_rule_type as _qos_rule_type
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkQosRuleType(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()


class TestShowNetworkQosRuleType(TestNetworkQosRuleType):
    attrs = {'drivers': [{'name': 'driver 1', 'supported_parameters': []}]}
    # The QoS policies to show.
    qos_rule_type = (
        network_fakes.FakeNetworkQosRuleType.create_one_qos_rule_type(attrs)
    )
    columns = ('drivers', 'rule_type_name')
    data = [qos_rule_type.drivers, qos_rule_type.type]

    def setUp(self):
        super().setUp()
        self.network_client.get_qos_rule_type = mock.Mock(
            return_value=self.qos_rule_type
        )

        # Get the command object to test
        self.cmd = _qos_rule_type.ShowNetworkQosRuleType(self.app, None)

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
            self.qos_rule_type.type,
        ]
        verifylist = [
            ('rule_type', self.qos_rule_type.type),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.get_qos_rule_type.assert_called_once_with(
            self.qos_rule_type.type
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))


class TestListNetworkQosRuleType(TestNetworkQosRuleType):
    # The QoS policies to list up.
    qos_rule_types = (
        network_fakes.FakeNetworkQosRuleType.create_qos_rule_types(count=3)
    )
    columns = ('Type',)
    data = []
    for qos_rule_type in qos_rule_types:
        data.append((qos_rule_type.type,))

    def setUp(self):
        super().setUp()
        self.network_client.qos_rule_types = mock.Mock(
            return_value=self.qos_rule_types
        )

        # Get the command object to test
        self.cmd = _qos_rule_type.ListNetworkQosRuleType(self.app, None)

    def test_qos_rule_type_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.qos_rule_types.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_qos_rule_type_list_all_supported(self):
        arglist = ['--all-supported']
        verifylist = [
            ('all_supported', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.qos_rule_types.assert_called_once_with(
            **{'all_supported': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_qos_rule_type_list_all_rules(self):
        arglist = ['--all-rules']
        verifylist = [
            ('all_rules', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.qos_rule_types.assert_called_once_with(
            **{'all_rules': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
