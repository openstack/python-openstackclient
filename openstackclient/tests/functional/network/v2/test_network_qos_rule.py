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

import json
import uuid

from openstackclient.tests.functional.network.v2 import common


class NetworkQosRuleTestsMinimumBandwidth(common.NetworkTests):
    """Functional tests for QoS minimum bandwidth rule"""

    def setUp(self):
        super(NetworkQosRuleTestsMinimumBandwidth, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

        self.QOS_POLICY_NAME = 'qos_policy_%s' % uuid.uuid4().hex

        self.openstack(
            'network qos policy create %s' % self.QOS_POLICY_NAME
        )
        self.addCleanup(self.openstack,
                        'network qos policy delete %s' % self.QOS_POLICY_NAME)
        cmd_output = json.loads(self.openstack(
            'network qos rule create -f json '
            '--type minimum-bandwidth '
            '--min-kbps 2800 '
            '--egress %s' %
            self.QOS_POLICY_NAME
        ))
        self.RULE_ID = cmd_output['id']
        self.addCleanup(self.openstack,
                        'network qos rule delete %s %s' %
                        (self.QOS_POLICY_NAME, self.RULE_ID))
        self.assertTrue(self.RULE_ID)

    def test_qos_rule_create_delete(self):
        # This is to check the output of qos rule delete
        policy_name = uuid.uuid4().hex
        self.openstack('network qos policy create -f json %s' % policy_name)
        self.addCleanup(self.openstack,
                        'network qos policy delete %s' % policy_name)
        rule = json.loads(self.openstack(
            'network qos rule create -f json '
            '--type minimum-bandwidth '
            '--min-kbps 2800 '
            '--egress %s' % policy_name
        ))
        raw_output = self.openstack(
            'network qos rule delete %s %s' %
            (policy_name, rule['id']))
        self.assertEqual('', raw_output)

    def test_qos_rule_list(self):
        cmd_output = json.loads(self.openstack(
            'network qos rule list -f json %s' % self.QOS_POLICY_NAME))
        self.assertIn(self.RULE_ID, [rule['ID'] for rule in cmd_output])

    def test_qos_rule_show(self):
        cmd_output = json.loads(self.openstack(
            'network qos rule show -f json %s %s' %
            (self.QOS_POLICY_NAME, self.RULE_ID)))
        self.assertEqual(self.RULE_ID, cmd_output['id'])

    def test_qos_rule_set(self):
        self.openstack('network qos rule set --min-kbps 7500 %s %s' %
                       (self.QOS_POLICY_NAME, self.RULE_ID))
        cmd_output = json.loads(self.openstack(
            'network qos rule show -f json %s %s' %
            (self.QOS_POLICY_NAME, self.RULE_ID)))
        self.assertEqual(7500, cmd_output['min_kbps'])


class NetworkQosRuleTestsDSCPMarking(common.NetworkTests):
    """Functional tests for QoS DSCP marking rule"""

    def setUp(self):
        super(NetworkQosRuleTestsDSCPMarking, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

        self.QOS_POLICY_NAME = 'qos_policy_%s' % uuid.uuid4().hex
        self.openstack(
            'network qos policy create %s' % self.QOS_POLICY_NAME
        )
        self.addCleanup(self.openstack,
                        'network qos policy delete %s' % self.QOS_POLICY_NAME)
        cmd_output = json.loads(self.openstack(
            'network qos rule create -f json '
            '--type dscp-marking '
            '--dscp-mark 8 %s' %
            self.QOS_POLICY_NAME
        ))
        self.RULE_ID = cmd_output['id']
        self.addCleanup(self.openstack,
                        'network qos rule delete %s %s' %
                        (self.QOS_POLICY_NAME, self.RULE_ID))
        self.assertTrue(self.RULE_ID)

    def test_qos_rule_create_delete(self):
        # This is to check the output of qos rule delete
        policy_name = uuid.uuid4().hex
        self.openstack('network qos policy create -f json %s' % policy_name)
        self.addCleanup(self.openstack,
                        'network qos policy delete %s' % policy_name)
        rule = json.loads(self.openstack(
            'network qos rule create -f json '
            '--type dscp-marking '
            '--dscp-mark 8 %s' % policy_name
        ))
        raw_output = self.openstack(
            'network qos rule delete %s %s' %
            (policy_name, rule['id']))
        self.assertEqual('', raw_output)

    def test_qos_rule_list(self):
        cmd_output = json.loads(self.openstack(
            'network qos rule list -f json %s' % self.QOS_POLICY_NAME))
        self.assertIn(self.RULE_ID, [rule['ID'] for rule in cmd_output])

    def test_qos_rule_show(self):
        cmd_output = json.loads(self.openstack(
            'network qos rule show -f json %s %s' %
            (self.QOS_POLICY_NAME, self.RULE_ID)))
        self.assertEqual(self.RULE_ID, cmd_output['id'])

    def test_qos_rule_set(self):
        self.openstack('network qos rule set --dscp-mark 32 %s %s' %
                       (self.QOS_POLICY_NAME, self.RULE_ID))
        cmd_output = json.loads(self.openstack(
            'network qos rule show -f json %s %s' %
            (self.QOS_POLICY_NAME, self.RULE_ID)))
        self.assertEqual(32, cmd_output['dscp_mark'])


class NetworkQosRuleTestsBandwidthLimit(common.NetworkTests):
    """Functional tests for QoS bandwidth limit rule"""

    def setUp(self):
        super(NetworkQosRuleTestsBandwidthLimit, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

        self.QOS_POLICY_NAME = 'qos_policy_%s' % uuid.uuid4().hex
        self.openstack(
            'network qos policy create %s' % self.QOS_POLICY_NAME
        )
        self.addCleanup(self.openstack,
                        'network qos policy delete %s' % self.QOS_POLICY_NAME)
        cmd_output = json.loads(self.openstack(
            'network qos rule create -f json '
            '--type bandwidth-limit '
            '--max-kbps 10000 '
            '--egress %s' %
            self.QOS_POLICY_NAME
        ))
        self.RULE_ID = cmd_output['id']
        self.addCleanup(self.openstack,
                        'network qos rule delete %s %s' %
                        (self.QOS_POLICY_NAME, self.RULE_ID))
        self.assertTrue(self.RULE_ID)

    def test_qos_rule_create_delete(self):
        # This is to check the output of qos rule delete
        policy_name = uuid.uuid4().hex
        self.openstack('network qos policy create -f json %s' % policy_name)
        self.addCleanup(self.openstack,
                        'network qos policy delete %s' % policy_name)
        rule = json.loads(self.openstack(
            'network qos rule create -f json '
            '--type bandwidth-limit '
            '--max-kbps 10000 '
            '--max-burst-kbits 1400 '
            '--egress %s' % policy_name
        ))
        raw_output = self.openstack(
            'network qos rule delete %s %s' %
            (policy_name, rule['id']))
        self.assertEqual('', raw_output)

    def test_qos_rule_list(self):
        cmd_output = json.loads(self.openstack(
            'network qos rule list -f json %s' %
            self.QOS_POLICY_NAME))
        self.assertIn(self.RULE_ID, [rule['ID'] for rule in cmd_output])

    def test_qos_rule_show(self):
        cmd_output = json.loads(self.openstack(
            'network qos rule show -f json %s %s' %
            (self.QOS_POLICY_NAME, self.RULE_ID)))
        self.assertEqual(self.RULE_ID, cmd_output['id'])

    def test_qos_rule_set(self):
        self.openstack('network qos rule set --max-kbps 15000 '
                       '--max-burst-kbits 1800 '
                       '--ingress %s %s' %
                       (self.QOS_POLICY_NAME, self.RULE_ID))
        cmd_output = json.loads(self.openstack(
            'network qos rule show -f json %s %s' %
            (self.QOS_POLICY_NAME, self.RULE_ID)))
        self.assertEqual(15000, cmd_output['max_kbps'])
        self.assertEqual(1800, cmd_output['max_burst_kbps'])
        self.assertEqual('ingress', cmd_output['direction'])
