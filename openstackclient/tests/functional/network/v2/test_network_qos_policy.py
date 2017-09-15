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

        self.NAME = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network qos policy create -f json ' +
            self.NAME
        ))
        self.addCleanup(
            self.openstack,
            'network qos policy delete ' + self.NAME,
            fail_ok=True,
        )
        self.assertEqual(self.NAME, cmd_output['name'])

    def test_qos_rule_create_delete(self):
        # This is to check the output of qos policy delete
        policy_name = uuid.uuid4().hex
        self.openstack('network qos policy create -f json ' + policy_name)
        raw_output = self.openstack(
            'network qos policy delete ' + policy_name)
        self.assertEqual('', raw_output)

    def test_qos_policy_list(self):
        cmd_output = json.loads(self.openstack(
            'network qos policy list -f json'))
        self.assertIn(self.NAME, [p['Name'] for p in cmd_output])

    def test_qos_policy_show(self):
        cmd_output = json.loads(self.openstack(
            'network qos policy show -f json ' + self.NAME))
        self.assertEqual(self.NAME, cmd_output['name'])

    def test_qos_policy_set(self):
        self.openstack('network qos policy set --share ' + self.NAME)
        cmd_output = json.loads(self.openstack(
            'network qos policy show -f json ' + self.NAME))
        self.assertTrue(cmd_output['shared'])

    def test_qos_policy_default(self):
        self.openstack('network qos policy set --default ' + self.NAME)
        cmd_output = json.loads(self.openstack(
            'network qos policy show -f json ' + self.NAME))
        self.assertTrue(cmd_output['is_default'])

        self.openstack('network qos policy set --no-default ' + self.NAME)
        cmd_output = json.loads(self.openstack(
            'network qos policy show -f json ' + self.NAME))
        self.assertFalse(cmd_output['is_default'])
