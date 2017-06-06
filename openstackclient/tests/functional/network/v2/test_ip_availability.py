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


class IPAvailabilityTests(common.NetworkTests):
    """Functional tests for IP availability"""

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            cls.NAME = uuid.uuid4().hex
            cls.NETWORK_NAME = uuid.uuid4().hex

            # Create a network for the subnet
            cls.openstack(
                'network create ' +
                cls.NETWORK_NAME
            )
            cmd_output = json.loads(cls.openstack(
                'subnet create -f json ' +
                '--network ' + cls.NETWORK_NAME + ' ' +
                '--subnet-range 10.10.10.0/24 ' +
                cls.NAME
            ))
            cls.assertOutput(cls.NAME, cmd_output['name'])

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_network:
                raw_subnet = cls.openstack(
                    'subnet delete ' +
                    cls.NAME
                )
                raw_network = cls.openstack(
                    'network delete ' +
                    cls.NETWORK_NAME
                )
                cls.assertOutput('', raw_subnet)
                cls.assertOutput('', raw_network)
        finally:
            super(IPAvailabilityTests, cls).tearDownClass()

    def setUp(self):
        super(IPAvailabilityTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_ip_availability_list(self):
        """Test ip availability list"""
        cmd_output = json.loads(self.openstack(
            'ip availability list -f json'))
        names = [x['Network Name'] for x in cmd_output]
        self.assertIn(self.NETWORK_NAME, names)

    def test_ip_availability_show(self):
        """Test ip availability show"""
        cmd_output = json.loads(self.openstack(
            'ip availability show -f json ' + self.NETWORK_NAME))
        self.assertEqual(
            self.NETWORK_NAME,
            cmd_output['network_name'],
        )
