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

from openstackclient.tests.functional.network.v2 import common


class NetworkQosRuleTypeTests(common.NetworkTests):
    """Functional tests for Network QoS rule type."""

    AVAILABLE_RULE_TYPES = ['dscp_marking', 'bandwidth_limit']
    # NOTE(ralonsoh): this list was updated in Yoga (February 2022)
    ALL_AVAILABLE_RULE_TYPES = [
        'dscp_marking',
        'bandwidth_limit',
        'minimum_bandwidth',
        'packet_rate_limit',
        'minimum_packet_rate',
    ]

    def setUp(self):
        super().setUp()

        if not self.is_extension_enabled("qos"):
            self.skipTest("No qos extension present")

    def test_qos_rule_type_list(self):
        cmd_output = self.openstack(
            'network qos rule type list -f json',
            parse_output=True,
        )
        for rule_type in self.AVAILABLE_RULE_TYPES:
            self.assertIn(rule_type, [x['Type'] for x in cmd_output])

    def test_qos_rule_type_list_all_supported(self):
        if not self.is_extension_enabled('qos-rule-type-filter'):
            self.skipTest('No "qos-rule-type-filter" extension present')

        cmd_output = self.openstack(
            'network qos rule type list --all-supported -f json',
            parse_output=True,
        )
        for rule_type in self.AVAILABLE_RULE_TYPES:
            self.assertIn(rule_type, [x['Type'] for x in cmd_output])

    def test_qos_rule_type_list_all_rules(self):
        if not self.is_extension_enabled('qos-rule-type-filter'):
            self.skipTest('No "qos-rule-type-filter" extension present')

        cmd_output = self.openstack(
            'network qos rule type list --all-rules -f json', parse_output=True
        )
        for rule_type in self.ALL_AVAILABLE_RULE_TYPES:
            self.assertIn(rule_type, [x['Type'] for x in cmd_output])

    def test_qos_rule_type_details(self):
        for rule_type in self.AVAILABLE_RULE_TYPES:
            cmd_output = self.openstack(
                f'network qos rule type show {rule_type} -f json',
                parse_output=True,
            )
            self.assertEqual(rule_type, cmd_output['rule_type_name'])
            self.assertIn("drivers", cmd_output.keys())
