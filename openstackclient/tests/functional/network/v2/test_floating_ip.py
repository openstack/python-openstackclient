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


class FloatingIpTests(base.TestCase):
    """Functional tests for floating ip. """
    SUBNET_NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex
    ID = None
    HEADERS = ['ID']
    FIELDS = ['id']

    @classmethod
    def setUpClass(cls):
        # Create a network for the floating ip.
        cls.openstack('network create --external ' + cls.NETWORK_NAME)
        # Create a subnet for the network.
        cls.openstack(
            'subnet create --network ' + cls.NETWORK_NAME +
            ' --subnet-range 10.10.10.0/24 ' +
            cls.SUBNET_NAME
        )
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack(
            'floating ip create ' + cls.NETWORK_NAME + opts)
        cls.ID = raw_output.strip('\n')

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('floating ip delete ' + cls.ID)
        cls.assertOutput('', raw_output)
        raw_output = cls.openstack('subnet delete ' + cls.SUBNET_NAME)
        cls.assertOutput('', raw_output)
        raw_output = cls.openstack('network delete ' + cls.NETWORK_NAME)
        cls.assertOutput('', raw_output)

    def test_floating_ip_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('floating ip list' + opts)
        self.assertIn(self.ID, raw_output)

    def test_floating_ip_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('floating ip show ' + self.ID + opts)
        self.assertEqual(self.ID + "\n", raw_output)
