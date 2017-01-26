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

import re
import uuid

from openstackclient.tests.functional import base


class TestMeterRule(base.TestCase):
    """Functional tests for meter rule"""
    METER_NAME = uuid.uuid4().hex
    METER_ID = None
    METER_RULE_ID = None

    @classmethod
    def setUpClass(cls):
        # Set up some regex for matching below
        cls.re_id = re.compile("id\s+\|\s+(\S+)")
        cls.re_direction = re.compile("direction\s+\|\s+(\S+)")
        cls.re_ip_prefix = re.compile(
            "remote_ip_prefix\s+\|\s+([^|]+?)\s+\|"
        )
        cls.re_meter_id = re.compile("metering_label_id\s+\|\s+(\S+)")

        raw_output = cls.openstack(
            'network meter create ' + cls.METER_NAME
        )

        cls.METER_ID = re.search(cls.re_id, raw_output).group(1)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('network meter delete ' + cls.METER_ID)
        cls.assertOutput('', raw_output)

    def test_meter_rule_delete(self):
        """test create, delete"""

        raw_output = self.openstack(
            'network meter rule create ' +
            '--remote-ip-prefix 10.0.0.0/8 ' +
            self.METER_ID
        )
        rule_id = re.search(self.re_id, raw_output).group(1)
        re_ip = re.search(self.re_ip_prefix, raw_output)

        self.addCleanup(self.openstack,
                        'network meter rule delete ' + rule_id)
        self.assertIsNotNone(re_ip)
        self.assertIsNotNone(rule_id)

    def test_meter_rule_list(self):
        """Test create, list, delete"""
        raw_output = self.openstack(
            'network meter rule create ' +
            '--remote-ip-prefix 10.0.0.0/8 ' +
            self.METER_ID
        )
        rule_id = re.search(self.re_id, raw_output).group(1)
        self.addCleanup(self.openstack,
                        'network meter rule delete ' + rule_id)
        self.assertEqual(
            '10.0.0.0/8',
            re.search(self.re_ip_prefix, raw_output).group(1)
        )

        raw_output = self.openstack('network meter rule list')
        self.assertIsNotNone(re.search(rule_id + "|\s+\|\s+\|\s+10.0.0.0/8",
                                       raw_output))

    def test_meter_rule_show(self):
        """Test create, show, delete"""
        raw_output = self.openstack(
            'network meter rule create ' +
            '--remote-ip-prefix 10.0.0.0/8 ' +
            '--egress ' +
            self.METER_ID
        )
        rule_id = re.search(self.re_id, raw_output).group(1)

        self.assertEqual(
            'egress',
            re.search(self.re_direction, raw_output).group(1)
        )

        raw_output = self.openstack('network meter rule show ' + rule_id)

        self.assertEqual(
            '10.0.0.0/8',
            re.search(self.re_ip_prefix, raw_output).group(1)
        )
        self.assertIsNotNone(rule_id)

        self.addCleanup(self.openstack,
                        'network meter rule delete ' + rule_id)
