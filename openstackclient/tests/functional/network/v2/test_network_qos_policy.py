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


class NetworkQosPolicyTests(common.NetworkTests):
    """Functional tests for QoS policy"""

    def setUp(self):
        super(NetworkQosPolicyTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_qos_rule_create_delete(self):
        # This is to check the output of qos policy delete
        policy_name = uuid.uuid4().hex
        self.openstack('network qos policy create -f json ' + policy_name)
        raw_output = self.openstack(
            'network qos policy delete ' +
            policy_name
        )
        self.assertEqual('', raw_output)

    def test_qos_policy_list(self):
        policy_name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'network qos policy create -f json ' +
            policy_name
        ))
        self.addCleanup(self.openstack,
                        'network qos policy delete ' + policy_name)
        self.assertEqual(policy_name, json_output['name'])

        json_output = json.loads(self.openstack(
            'network qos policy list -f json'
        ))
        self.assertIn(policy_name, [p['Name'] for p in json_output])

    def test_qos_policy_set(self):
        policy_name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'network qos policy create -f json ' +
            policy_name
        ))
        self.addCleanup(self.openstack,
                        'network qos policy delete ' + policy_name)
        self.assertEqual(policy_name, json_output['name'])

        self.openstack(
            'network qos policy set ' +
            '--share ' +
            policy_name
        )

        json_output = json.loads(self.openstack(
            'network qos policy show -f json ' +
            policy_name
        ))
        self.assertTrue(json_output['shared'])

        self.openstack(
            'network qos policy set ' +
            '--no-share ' +
            '--no-default ' +
            policy_name
        )
        json_output = json.loads(self.openstack(
            'network qos policy show -f json ' +
            policy_name
        ))
        self.assertFalse(json_output['shared'])
        self.assertFalse(json_output['is_default'])
