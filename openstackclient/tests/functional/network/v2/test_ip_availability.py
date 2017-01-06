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


class IPAvailabilityTests(base.TestCase):
    """Functional tests for IP availability. """
    NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex
    FIELDS = ['network_name']

    @classmethod
    def setUpClass(cls):
        # Create a network for the subnet.
        cls.openstack('network create ' + cls.NETWORK_NAME)
        opts = cls.get_opts(['name'])
        raw_output = cls.openstack(
            'subnet create --network ' + cls.NETWORK_NAME +
            ' --subnet-range 10.10.10.0/24 ' +
            cls.NAME + opts
        )
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_subnet = cls.openstack('subnet delete ' + cls.NAME)
        raw_network = cls.openstack('network delete ' + cls.NETWORK_NAME)
        cls.assertOutput('', raw_subnet)
        cls.assertOutput('', raw_network)

    def test_ip_availability_list(self):
        opts = ' -f csv -c "Network Name"'
        raw_output = self.openstack('ip availability list' + opts)
        self.assertIn(self.NETWORK_NAME, raw_output)

    def test_ip_availability_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack(
            'ip availability show ' + self.NETWORK_NAME + opts)
        self.assertEqual(self.NETWORK_NAME + "\n", raw_output)
