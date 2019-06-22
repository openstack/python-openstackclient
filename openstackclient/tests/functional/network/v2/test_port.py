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


class PortTests(common.NetworkTagTests):
    """Functional tests for port"""

    base_command = 'port'

    NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            cls.NAME = uuid.uuid4().hex
            cls.NETWORK_NAME = uuid.uuid4().hex

            # Create a network for the port tests
            cls.openstack(
                'network create %s' % cls.NETWORK_NAME
            )

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_network:
                raw_output = cls.openstack(
                    'network delete %s' % cls.NETWORK_NAME
                )
                cls.assertOutput('', raw_output)
        finally:
            super(PortTests, cls).tearDownClass()

    def setUp(self):
        super(PortTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_port_delete(self):
        """Test create, delete multiple"""
        json_output = json.loads(self.openstack(
            'port create -f json --network %s %s' %
            (self.NETWORK_NAME, self.NAME)
        ))
        id1 = json_output.get('id')
        self.assertIsNotNone(id1)
        self.assertIsNotNone(json_output.get('mac_address'))
        self.assertEqual(self.NAME, json_output.get('name'))

        json_output = json.loads(self.openstack(
            'port create -f json --network %s %sx' %
            (self.NETWORK_NAME, self.NAME)
        ))
        id2 = json_output.get('id')
        self.assertIsNotNone(id2)
        self.assertIsNotNone(json_output.get('mac_address'))
        self.assertEqual(self.NAME + 'x', json_output.get('name'))

        # Clean up after ourselves
        raw_output = self.openstack('port delete %s %s' % (id1, id2))
        self.assertOutput('', raw_output)

    def test_port_list(self):
        """Test create defaults, list, delete"""
        json_output = json.loads(self.openstack(
            'port create -f json --network %s %s' %
            (self.NETWORK_NAME, self.NAME)
        ))
        id1 = json_output.get('id')
        self.assertIsNotNone(id1)
        mac1 = json_output.get('mac_address')
        self.assertIsNotNone(mac1)
        self.addCleanup(self.openstack, 'port delete %s' % id1)
        self.assertEqual(self.NAME, json_output.get('name'))

        json_output = json.loads(self.openstack(
            'port create -f json --network %s %sx' %
            (self.NETWORK_NAME, self.NAME)
        ))
        id2 = json_output.get('id')
        self.assertIsNotNone(id2)
        mac2 = json_output.get('mac_address')
        self.assertIsNotNone(mac2)
        self.addCleanup(self.openstack, 'port delete %s' % id2)
        self.assertEqual(self.NAME + 'x', json_output.get('name'))

        # Test list
        json_output = json.loads(self.openstack(
            'port list -f json'
        ))
        item_map = {item.get('ID'): item.get('MAC Address') for item in
                    json_output}
        self.assertIn(id1, item_map.keys())
        self.assertIn(id2, item_map.keys())
        self.assertIn(mac1, item_map.values())
        self.assertIn(mac2, item_map.values())

        # Test list --long
        json_output = json.loads(self.openstack(
            'port list --long -f json'
        ))
        id_list = [item.get('ID') for item in json_output]
        self.assertIn(id1, id_list)
        self.assertIn(id2, id_list)

        # Test list --mac-address
        json_output = json.loads(self.openstack(
            'port list -f json --mac-address %s' % mac2
        ))
        item_map = {item.get('ID'): item.get('MAC Address') for item in
                    json_output}
        self.assertNotIn(id1, item_map.keys())
        self.assertIn(id2, item_map.keys())
        self.assertNotIn(mac1, item_map.values())
        self.assertIn(mac2, item_map.values())

        # Test list with unknown fields
        json_output = json.loads(self.openstack(
            'port list -f json -c ID -c Name -c device_id'
        ))
        id_list = [p['ID'] for p in json_output]
        self.assertIn(id1, id_list)
        self.assertIn(id2, id_list)
        # Check an unknown field exists
        self.assertIn('device_id', json_output[0])

    def test_port_set(self):
        """Test create, set, show, delete"""
        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'port create -f json '
            '--network %s '
            '--description xyzpdq '
            '--disable %s' %
            (self.NETWORK_NAME, name)
        ))
        id1 = json_output.get('id')
        self.addCleanup(self.openstack, 'port delete %s' % id1)
        self.assertEqual(name, json_output.get('name'))
        self.assertEqual('xyzpdq', json_output.get('description'))
        self.assertEqual(False, json_output.get('admin_state_up'))

        raw_output = self.openstack(
            'port set --enable %s' %
            name
        )
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json %s' % name
        ))
        sg_id = json_output.get('security_group_ids')[0]

        self.assertEqual(name, json_output.get('name'))
        self.assertEqual('xyzpdq', json_output.get('description'))
        self.assertEqual(True, json_output.get('admin_state_up'))
        self.assertIsNotNone(json_output.get('mac_address'))

        raw_output = self.openstack(
            'port unset --security-group %s %s' % (sg_id, id1))
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json %s' % name
        ))
        self.assertEqual([], json_output.get('security_group_ids'))

    def test_port_admin_set(self):
        """Test create, set (as admin), show, delete"""
        json_output = json.loads(self.openstack(
            'port create -f json '
            '--network %s %s' % (self.NETWORK_NAME, self.NAME)
        ))
        id_ = json_output.get('id')
        self.addCleanup(self.openstack, 'port delete %s' % id_)

        raw_output = self.openstack(
            '--os-username admin '
            'port set --mac-address 11:22:33:44:55:66 %s' %
            self.NAME)
        self.assertOutput('', raw_output)
        json_output = json.loads(self.openstack(
            'port show -f json %s' % self.NAME
        ))
        self.assertEqual(json_output.get('mac_address'), '11:22:33:44:55:66')

    def test_port_set_sg(self):
        """Test create, set, show, delete"""
        sg_name1 = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'security group create -f json %s' %
            sg_name1
        ))
        sg_id1 = json_output.get('id')
        self.addCleanup(self.openstack, 'security group delete %s' % sg_id1)

        sg_name2 = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'security group create -f json %s' %
            sg_name2
        ))
        sg_id2 = json_output.get('id')
        self.addCleanup(self.openstack, 'security group delete %s' % sg_id2)

        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'port create -f json '
            '--network %s '
            '--security-group %s %s' %
            (self.NETWORK_NAME, sg_name1, name)
        ))
        id1 = json_output.get('id')
        self.addCleanup(self.openstack, 'port delete %s' % id1)
        self.assertEqual(name, json_output.get('name'))
        self.assertEqual([sg_id1], json_output.get('security_group_ids'))

        raw_output = self.openstack(
            'port set '
            '--security-group %s %s' %
            (sg_name2, name)
        )
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json %s' % name
        ))
        self.assertEqual(name, json_output.get('name'))
        # NOTE(amotoki): The order of the field is not predictable,
        self.assertIsInstance(json_output.get('security_group_ids'), list)
        self.assertEqual(sorted([sg_id1, sg_id2]),
                         sorted(json_output.get('security_group_ids')))

        raw_output = self.openstack(
            'port unset --security-group %s %s' % (sg_id1, id1))
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json %s' % name
        ))
        self.assertEqual(
            [sg_id2],
            json_output.get('security_group_ids')
        )

    def _create_resource_for_tag_test(self, name, args):
        return json.loads(self.openstack(
            '{} create -f json --network {} {} {}'
            .format(self.base_command, self.NETWORK_NAME, args, name)
        ))
