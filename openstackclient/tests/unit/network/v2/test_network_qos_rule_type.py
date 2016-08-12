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

from openstackclient.network.v2 import network_qos_rule_type as _qos_rule_type
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestNetworkQosRuleType(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkQosRuleType, self).setUp()
        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestListNetworkQosRuleType(TestNetworkQosRuleType):

    # The QoS policies to list up.
    qos_rule_types = (
        network_fakes.FakeNetworkQosRuleType.create_qos_rule_types(count=3))
    columns = (
        'Type',
    )
    data = []
    for qos_rule_type in qos_rule_types:
        data.append((
            qos_rule_type.type,
        ))

    def setUp(self):
        super(TestListNetworkQosRuleType, self).setUp()
        self.network.qos_rule_types = mock.Mock(
            return_value=self.qos_rule_types)

        # Get the command object to test
        self.cmd = _qos_rule_type.ListNetworkQosRuleType(self.app,
                                                         self.namespace)

    def test_qos_rule_type_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.qos_rule_types.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
