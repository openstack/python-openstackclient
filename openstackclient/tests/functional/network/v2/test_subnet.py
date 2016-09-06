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

import uuid

from openstackclient.tests.functional import base


class SubnetTests(base.TestCase):
    """Functional tests for subnet. """
    NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        # Create a network for the subnet.
        cls.openstack('network create ' + cls.NETWORK_NAME)
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack(
            'subnet create --network ' + cls.NETWORK_NAME +
            ' --subnet-range 10.10.10.0/24 ' +
            cls.NAME + opts
        )
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('subnet delete ' + cls.NAME)
        cls.assertOutput('', raw_output)
        raw_output = cls.openstack('network delete ' + cls.NETWORK_NAME)
        cls.assertOutput('', raw_output)

    def test_subnet_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('subnet list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_subnet_set(self):
        self.openstack('subnet set --no-dhcp ' + self.NAME)
        opts = self.get_opts(['name', 'enable_dhcp'])
        raw_output = self.openstack('subnet show ' + self.NAME + opts)
        self.assertEqual("False\n" + self.NAME + "\n", raw_output)

    def test_subnet_set_service_type(self):
        TYPE = 'network:floatingip_agent_gateway'
        self.openstack('subnet set --service-type ' + TYPE + ' ' + self.NAME)
        opts = self.get_opts(['name', 'service_types'])
        raw_output = self.openstack('subnet show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n" + TYPE + "\n", raw_output)

    def test_subnet_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('subnet show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)
