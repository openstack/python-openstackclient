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

import unittest
import uuid

from openstackclient.tests.functional.network.v2 import common


class TestMeterRule(common.NetworkTests):
    """Functional tests for meter rule"""

    METER_ID: str
    METER_RULE_ID: str

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if not cls.is_extension_enabled("metering"):
            raise unittest.SkipTest("No metering extension present")

        if cls.haz_network:
            cls.METER_NAME = uuid.uuid4().hex

            json_output = cls.openstack(
                'network meter create ' + cls.METER_NAME,
                parse_output=True,
            )
            cls.METER_ID = json_output.get('id')

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_network:
                raw_output = cls.openstack(
                    'network meter delete ' + cls.METER_ID
                )
                cls.assertOutput('', raw_output)
        finally:
            super().tearDownClass()

    def test_meter_rule_delete(self):
        """test create, delete"""
        json_output = self.openstack(
            'network meter rule create '
            + '--remote-ip-prefix 10.0.0.0/8 '
            + self.METER_ID,
            parse_output=True,
        )
        rule_id = json_output.get('id')
        re_ip = json_output.get('remote_ip_prefix')

        self.addCleanup(self.openstack, 'network meter rule delete ' + rule_id)
        self.assertIsNotNone(re_ip)
        self.assertIsNotNone(rule_id)
        self.assertEqual('10.0.0.0/8', re_ip)

    def test_meter_rule_list(self):
        """Test create, list, delete"""
        json_output = self.openstack(
            'network meter rule create '
            + '--remote-ip-prefix 10.0.0.0/8 '
            + self.METER_ID,
            parse_output=True,
        )
        rule_id_1 = json_output.get('id')
        self.addCleanup(
            self.openstack, 'network meter rule delete ' + rule_id_1
        )
        self.assertEqual('10.0.0.0/8', json_output.get('remote_ip_prefix'))

        json_output_1 = self.openstack(
            'network meter rule create '
            + '--remote-ip-prefix 11.0.0.0/8 '
            + self.METER_ID,
            parse_output=True,
        )
        rule_id_2 = json_output_1.get('id')
        self.addCleanup(
            self.openstack, 'network meter rule delete ' + rule_id_2
        )
        self.assertEqual('11.0.0.0/8', json_output_1.get('remote_ip_prefix'))

        json_output = self.openstack(
            'network meter rule list',
            parse_output=True,
        )
        rule_id_list = [item.get('ID') for item in json_output]
        ip_prefix_list = [item.get('Remote IP Prefix') for item in json_output]
        self.assertIn(rule_id_1, rule_id_list)
        self.assertIn(rule_id_2, rule_id_list)
        self.assertIn('10.0.0.0/8', ip_prefix_list)
        self.assertIn('11.0.0.0/8', ip_prefix_list)

    def test_meter_rule_show(self):
        """Test create, show, delete"""
        json_output = self.openstack(
            'network meter rule create '
            + '--remote-ip-prefix 10.0.0.0/8 '
            + '--egress '
            + self.METER_ID,
            parse_output=True,
        )
        rule_id = json_output.get('id')

        self.assertEqual('egress', json_output.get('direction'))

        json_output = self.openstack(
            'network meter rule show ' + rule_id,
            parse_output=True,
        )
        self.assertEqual('10.0.0.0/8', json_output.get('remote_ip_prefix'))
        self.assertIsNotNone(rule_id)

        self.addCleanup(self.openstack, 'network meter rule delete ' + rule_id)
