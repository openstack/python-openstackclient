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


class PortTests(common.NetworkTests):
    """Functional tests for port"""
    NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            # Create a network for the port
            cls.openstack(
                'network create ' + cls.NETWORK_NAME
            )

    @classmethod
    def tearDownClass(cls):
        if cls.haz_network:
            raw_output = cls.openstack(
                'network delete ' + cls.NETWORK_NAME
            )
            cls.assertOutput('', raw_output)

    def setUp(self):
        super(PortTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_port_delete(self):
        """Test create, delete multiple"""
        json_output = json.loads(self.openstack(
            'port create -f json --network ' +
            self.NETWORK_NAME + ' ' + self.NAME
        ))
        id1 = json_output.get('id')
        self.assertIsNotNone(id1)
        self.assertIsNotNone(json_output.get('mac_address'))
        self.assertEqual(self.NAME, json_output.get('name'))

        json_output = json.loads(self.openstack(
            'port create -f json --network ' + self.NETWORK_NAME + ' ' +
            self.NAME + 'x'
        ))
        id2 = json_output.get('id')
        self.assertIsNotNone(id2)
        self.assertIsNotNone(json_output.get('mac_address'))
        self.assertEqual(self.NAME + 'x', json_output.get('name'))

        # Clean up after ourselves
        raw_output = self.openstack('port delete ' + id1 + ' ' + id2)
        self.assertOutput('', raw_output)

    def test_port_list(self):
        """Test create defaults, list, delete"""
        json_output = json.loads(self.openstack(
            'port create -f json --network ' + self.NETWORK_NAME + ' ' +
            self.NAME
        ))
        id1 = json_output.get('id')
        self.assertIsNotNone(id1)
        mac1 = json_output.get('mac_address')
        self.assertIsNotNone(mac1)
        self.addCleanup(self.openstack, 'port delete ' + id1)
        self.assertEqual(self.NAME, json_output.get('name'))

        json_output = json.loads(self.openstack(
            'port create -f json --network ' + self.NETWORK_NAME + ' ' +
            self.NAME + 'x'
        ))
        id2 = json_output.get('id')
        self.assertIsNotNone(id2)
        mac2 = json_output.get('mac_address')
        self.assertIsNotNone(mac2)
        self.addCleanup(self.openstack, 'port delete ' + id2)
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
            'port list -f json --mac-address ' + mac2
        ))
        item_map = {item.get('ID'): item.get('MAC Address') for item in
                    json_output}
        self.assertNotIn(id1, item_map.keys())
        self.assertIn(id2, item_map.keys())
        self.assertNotIn(mac1, item_map.values())
        self.assertIn(mac2, item_map.values())

    def test_port_set(self):
        """Test create, set, show, delete"""
        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'port create -f json ' +
            '--network ' + self.NETWORK_NAME + ' ' +
            '--description xyzpdq ' +
            '--disable ' +
            name
        ))
        id1 = json_output.get('id')
        self.addCleanup(self.openstack, 'port delete ' + id1)
        self.assertEqual(name, json_output.get('name'))
        self.assertEqual('xyzpdq', json_output.get('description'))
        self.assertEqual('DOWN', json_output.get('admin_state_up'))

        raw_output = self.openstack(
            'port set ' + '--enable ' +
            name
        )
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json ' + name
        ))
        sg_id = json_output.get('security_group_ids')

        self.assertEqual(name, json_output.get('name'))
        self.assertEqual('xyzpdq', json_output.get('description'))
        self.assertEqual('UP', json_output.get('admin_state_up'))
        self.assertIsNotNone(json_output.get('mac_address'))

        raw_output = self.openstack(
            'port unset --security-group ' + sg_id + ' ' + id1)
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json ' + name
        ))
        self.assertEqual('', json_output.get('security_group_ids'))

    def test_port_admin_set(self):
        """Test create, set (as admin), show, delete"""
        json_output = json.loads(self.openstack(
            'port create -f json ' +
            '--network ' + self.NETWORK_NAME + ' ' + self.NAME
        ))
        id_ = json_output.get('id')
        self.addCleanup(self.openstack, 'port delete ' + id_)

        raw_output = self.openstack(
            '--os-username admin '
            + 'port set --mac-address 11:22:33:44:55:66 '
            + self.NAME)
        self.assertOutput('', raw_output)
        json_output = json.loads(self.openstack(
            'port show -f json ' + self.NAME
        ))
        self.assertEqual(json_output.get('mac_address'), '11:22:33:44:55:66')

    def test_port_set_sg(self):
        """Test create, set, show, delete"""
        sg_name1 = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'security group create -f json ' +
            sg_name1
        ))
        sg_id1 = json_output.get('id')
        self.addCleanup(self.openstack, 'security group delete ' + sg_id1)

        sg_name2 = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'security group create -f json ' +
            sg_name2
        ))
        sg_id2 = json_output.get('id')
        self.addCleanup(self.openstack, 'security group delete ' + sg_id2)

        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'port create -f json ' +
            '--network ' + self.NETWORK_NAME + ' ' +
            '--security-group ' + sg_name1 + ' ' +
            name
        ))
        id1 = json_output.get('id')
        self.addCleanup(self.openstack, 'port delete ' + id1)
        self.assertEqual(name, json_output.get('name'))
        self.assertEqual(sg_id1, json_output.get('security_group_ids'))

        raw_output = self.openstack(
            'port set ' +
            '--security-group ' + sg_name2 + ' ' +
            name
        )
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json ' + name
        ))
        self.assertEqual(name, json_output.get('name'))
        self.assertIn(
            # TODO(dtroyer): output formatters should not mess with JSON!
            sg_id1,
            json_output.get('security_group_ids'),
        )
        self.assertIn(
            # TODO(dtroyer): output formatters should not mess with JSON!
            sg_id2,
            json_output.get('security_group_ids'),
        )

        raw_output = self.openstack(
            'port unset --security-group ' + sg_id1 + ' ' + id1)
        self.assertOutput('', raw_output)

        json_output = json.loads(self.openstack(
            'port show -f json ' + name
        ))
        self.assertEqual(
            # TODO(dtroyer): output formatters should do this on JSON!
            sg_id2,
            json_output.get('security_group_ids'),
        )
