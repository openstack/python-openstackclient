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


class PortTests(base.TestCase):
    """Functional tests for port. """
    NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        # Set up some regex for matching below
        cls.re_id = re.compile("\s+id\s+\|\s+(\S+)")
        cls.re_name = re.compile("\s+name\s+\|\s+([^|]+?)\s+\|")
        cls.re_description = re.compile("\s+description\s+\|\s+([^|]+?)\s+\|")
        cls.re_mac_address = re.compile("\s+mac_address\s+\|\s+([^|]+?)\s+\|")
        cls.re_state = re.compile("\s+admin_state_up\s+\|\s+([^|]+?)\s+\|")

        # Create a network for the port
        raw_output = cls.openstack('network create ' + cls.NETWORK_NAME)
        cls.network_id = re.search(cls.re_id, raw_output).group(1)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('network delete ' + cls.NETWORK_NAME)
        cls.assertOutput('', raw_output)

    def test_port_delete(self):
        """Test create, delete multiple"""
        raw_output = self.openstack(
            'port create --network ' + self.NETWORK_NAME + ' ' + self.NAME
        )
        re_id1 = re.search(self.re_id, raw_output)
        self.assertIsNotNone(re_id1)
        id1 = re_id1.group(1)
        self.assertIsNotNone(
            re.search(self.re_mac_address, raw_output).group(1),
        )
        self.assertEqual(
            self.NAME,
            re.search(self.re_name, raw_output).group(1),
        )

        raw_output = self.openstack(
            'port create ' +
            '--network ' + self.NETWORK_NAME + ' ' +
            self.NAME + 'x'
        )
        id2 = re.search(self.re_id, raw_output).group(1)
        self.assertIsNotNone(
            re.search(self.re_mac_address, raw_output).group(1),
        )
        self.assertEqual(
            self.NAME + 'x',
            re.search(self.re_name, raw_output).group(1),
        )

        # Clean up after ourselves
        raw_output = self.openstack('port delete ' + id1 + ' ' + id2)
        self.assertOutput('', raw_output)

    def test_port_list(self):
        """Test create defaults, list, delete"""
        raw_output = self.openstack(
            'port create --network ' + self.NETWORK_NAME + ' ' + self.NAME
        )
        re_id1 = re.search(self.re_id, raw_output)
        self.assertIsNotNone(re_id1)
        id1 = re_id1.group(1)
        mac1 = re.search(self.re_mac_address, raw_output).group(1)
        self.addCleanup(self.openstack, 'port delete ' + id1)
        self.assertEqual(
            self.NAME,
            re.search(self.re_name, raw_output).group(1),
        )

        raw_output = self.openstack(
            'port create ' +
            '--network ' + self.NETWORK_NAME + ' ' +
            self.NAME + 'x'
        )
        id2 = re.search(self.re_id, raw_output).group(1)
        mac2 = re.search(self.re_mac_address, raw_output).group(1)
        self.addCleanup(self.openstack, 'port delete ' + id2)
        self.assertEqual(
            self.NAME + 'x',
            re.search(self.re_name, raw_output).group(1),
        )

        # Test list
        raw_output = self.openstack('port list')
        self.assertIsNotNone(re.search("\|\s+" + id1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + id2 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + mac1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + mac2 + "\s+\|", raw_output))

        # Test list --long
        raw_output = self.openstack('port list --long')
        self.assertIsNotNone(re.search("\|\s+" + id1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + id2 + "\s+\|", raw_output))

        # Test list --mac-address
        raw_output = self.openstack('port list --mac-address ' + mac2)
        self.assertIsNone(re.search("\|\s+" + id1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + id2 + "\s+\|", raw_output))
        self.assertIsNone(re.search("\|\s+" + mac1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + mac2 + "\s+\|", raw_output))

    def test_port_set(self):
        """Test create, set, show, delete"""
        raw_output = self.openstack(
            'port create ' +
            '--network ' + self.NETWORK_NAME + ' ' +
            '--description xyzpdq '
            '--disable ' +
            self.NAME
        )
        re_id = re.search(self.re_id, raw_output)
        self.assertIsNotNone(re_id)
        id = re_id.group(1)
        self.addCleanup(self.openstack, 'port delete ' + id)
        self.assertEqual(
            self.NAME,
            re.search(self.re_name, raw_output).group(1),
        )
        self.assertEqual(
            'xyzpdq',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'DOWN',
            re.search(self.re_state, raw_output).group(1),
        )

        raw_output = self.openstack(
            'port set ' +
            '--enable ' +
            self.NAME
        )
        self.assertOutput('', raw_output)

        raw_output = self.openstack(
            'port show ' +
            self.NAME
        )
        self.assertEqual(
            self.NAME,
            re.search(self.re_name, raw_output).group(1),
        )
        self.assertEqual(
            'xyzpdq',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'UP',
            re.search(self.re_state, raw_output).group(1),
        )
        self.assertIsNotNone(
            re.search(self.re_mac_address, raw_output).group(1),
        )
