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

from tempest.lib import exceptions as tempest_exc

from openstackclient.tests.functional.network.v2 import common


class PortTests(common.NetworkTagTests):
    """Functional tests for port"""

    base_command = 'port'

    NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls.haz_network:
            cls.NAME = uuid.uuid4().hex
            cls.NETWORK_NAME = uuid.uuid4().hex

            # Create a network for the port tests
            cls.openstack(f'network create {cls.NETWORK_NAME}')

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_network:
                raw_output = cls.openstack(
                    f'network delete {cls.NETWORK_NAME}'
                )
                cls.assertOutput('', raw_output)
        finally:
            super().tearDownClass()

    def test_port_delete(self):
        """Test create, delete multiple"""
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {self.NAME}',
            parse_output=True,
        )
        id1 = json_output.get('id')
        self.assertIsNotNone(id1)
        self.assertIsNotNone(json_output.get('mac_address'))
        self.assertEqual(self.NAME, json_output.get('name'))

        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {self.NAME}x',
            parse_output=True,
        )
        id2 = json_output.get('id')
        self.assertIsNotNone(id2)
        self.assertIsNotNone(json_output.get('mac_address'))
        self.assertEqual(self.NAME + 'x', json_output.get('name'))

        # Clean up after ourselves
        raw_output = self.openstack(f'port delete {id1} {id2}')
        self.assertOutput('', raw_output)

    def test_port_list(self):
        """Test create defaults, list, delete"""
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {self.NAME}',
            parse_output=True,
        )
        id1 = json_output.get('id')
        self.assertIsNotNone(id1)
        mac1 = json_output.get('mac_address')
        self.assertIsNotNone(mac1)
        self.addCleanup(self.openstack, f'port delete {id1}')
        self.assertEqual(self.NAME, json_output.get('name'))

        # sg for port2
        sg_name1 = uuid.uuid4().hex
        json_output = self.openstack(
            f'security group create {sg_name1}',
            parse_output=True,
        )
        sg_id1 = json_output.get('id')
        self.addCleanup(self.openstack, f'security group delete {sg_id1}')
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} '
            f'--security-group {sg_name1} {self.NAME}x',
            parse_output=True,
        )

        id2 = json_output.get('id')
        self.assertIsNotNone(id2)
        mac2 = json_output.get('mac_address')
        self.assertIsNotNone(mac2)
        self.addCleanup(self.openstack, f'port delete {id2}')
        self.assertEqual(self.NAME + 'x', json_output.get('name'))

        # Test list
        json_output = self.openstack(
            'port list',
            parse_output=True,
        )
        item_map = {
            item.get('ID'): item.get('MAC Address') for item in json_output
        }
        self.assertIn(id1, item_map.keys())
        self.assertIn(id2, item_map.keys())
        self.assertIn(mac1, item_map.values())
        self.assertIn(mac2, item_map.values())

        # Test list --long
        json_output = self.openstack(
            'port list --long',
            parse_output=True,
        )
        id_list = [item.get('ID') for item in json_output]
        self.assertIn(id1, id_list)
        self.assertIn(id2, id_list)
        item_sg_map = {
            item.get('ID'): item.get('Security Groups') for item in json_output
        }
        self.assertIn(id1, item_sg_map.keys())
        self.assertIn(id2, item_sg_map.keys())
        self.assertIn([sg_id1], item_sg_map.values())

        # Test list --mac-address
        json_output = self.openstack(
            f'port list --mac-address {mac2}',
            parse_output=True,
        )
        item_map = {
            item.get('ID'): item.get('MAC Address') for item in json_output
        }
        self.assertNotIn(id1, item_map.keys())
        self.assertIn(id2, item_map.keys())
        self.assertNotIn(mac1, item_map.values())
        self.assertIn(mac2, item_map.values())

        # Test list --security-group
        json_output = self.openstack(
            f'port list --security-group {sg_id1}',
            parse_output=True,
        )
        item_map = {
            item.get('ID'): item.get('Security Groups') for item in json_output
        }
        self.assertNotIn(id1, item_map.keys())
        self.assertIn(id2, item_map.keys())

        # Test list with unknown fields
        json_output = self.openstack(
            'port list -c ID -c Name -c device_id',
            parse_output=True,
        )
        id_list = [p['ID'] for p in json_output]
        self.assertIn(id1, id_list)
        self.assertIn(id2, id_list)
        # Check an unknown field does not exist
        self.assertNotIn('device_id', json_output[0])

        # Test list with only unknown fields
        exc = self.assertRaises(
            tempest_exc.CommandFailed,
            self.openstack,
            'port list -c device_id',
        )
        self.assertIn("No recognized column names in ['device_id']", str(exc))

    def test_port_set(self):
        """Test create, set, show, delete"""
        name = uuid.uuid4().hex
        json_output = self.openstack(
            'port create '
            f'--network {self.NETWORK_NAME} '
            '--description xyzpdq '
            f'--disable {name}',
            parse_output=True,
        )
        id1 = json_output.get('id')
        self.addCleanup(self.openstack, f'port delete {id1}')
        self.assertEqual(name, json_output.get('name'))
        self.assertEqual('xyzpdq', json_output.get('description'))
        self.assertEqual(False, json_output.get('admin_state_up'))

        raw_output = self.openstack(f'port set --enable {name}')
        self.assertOutput('', raw_output)

        json_output = self.openstack(
            f'port show {name}',
            parse_output=True,
        )
        sg_id = json_output.get('security_group_ids')[0]

        self.assertEqual(name, json_output.get('name'))
        self.assertEqual('xyzpdq', json_output.get('description'))
        self.assertEqual(True, json_output.get('admin_state_up'))
        self.assertIsNotNone(json_output.get('mac_address'))

        raw_output = self.openstack(
            f'port unset --security-group {sg_id} {id1}'
        )
        self.assertOutput('', raw_output)

        json_output = self.openstack(
            f'port show {name}',
            parse_output=True,
        )
        self.assertEqual([], json_output.get('security_group_ids'))

    def test_port_admin_set(self):
        """Test create, set (as admin), show, delete"""
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {self.NAME}',
            parse_output=True,
        )
        id_ = json_output.get('id')
        self.addCleanup(self.openstack, f'port delete {id_}')

        raw_output = self.openstack(
            '--os-username admin '
            f'port set --mac-address 11:22:33:44:55:66 {self.NAME}'
        )
        self.assertOutput('', raw_output)
        json_output = self.openstack(
            f'port show {self.NAME}',
            parse_output=True,
        )
        self.assertEqual(json_output.get('mac_address'), '11:22:33:44:55:66')

    def test_port_set_sg(self):
        """Test create, set, show, delete"""
        sg_name1 = uuid.uuid4().hex
        json_output = self.openstack(
            f'security group create {sg_name1}',
            parse_output=True,
        )
        sg_id1 = json_output.get('id')
        self.addCleanup(self.openstack, f'security group delete {sg_id1}')

        sg_name2 = uuid.uuid4().hex
        json_output = self.openstack(
            f'security group create {sg_name2}',
            parse_output=True,
        )
        sg_id2 = json_output.get('id')
        self.addCleanup(self.openstack, f'security group delete {sg_id2}')

        name = uuid.uuid4().hex
        json_output = self.openstack(
            'port create '
            f'--network {self.NETWORK_NAME} '
            f'--security-group {sg_name1} {name}',
            parse_output=True,
        )
        id1 = json_output.get('id')
        self.addCleanup(self.openstack, f'port delete {id1}')
        self.assertEqual(name, json_output.get('name'))
        self.assertEqual([sg_id1], json_output.get('security_group_ids'))

        raw_output = self.openstack(
            f'port set --security-group {sg_name2} {name}'
        )
        self.assertOutput('', raw_output)

        json_output = self.openstack(
            f'port show {name}',
            parse_output=True,
        )
        self.assertEqual(name, json_output.get('name'))
        # NOTE(amotoki): The order of the field is not predictable,
        self.assertIsInstance(json_output.get('security_group_ids'), list)
        self.assertEqual(
            sorted([sg_id1, sg_id2]),
            sorted(json_output.get('security_group_ids')),
        )

        raw_output = self.openstack(
            f'port unset --security-group {sg_id1} {id1}'
        )
        self.assertOutput('', raw_output)

        json_output = self.openstack(
            f'port show {name}',
            parse_output=True,
        )
        self.assertEqual([sg_id2], json_output.get('security_group_ids'))

    def _create_resource_for_tag_test(self, name, args):
        return self.openstack(
            f'{self.base_command} create --network {self.NETWORK_NAME} {args} {name}',
            parse_output=True,
        )

    def _trunk_creation(self):
        pport = uuid.uuid4().hex
        sport1 = uuid.uuid4().hex
        sport2 = uuid.uuid4().hex
        trunk = uuid.uuid4().hex
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {pport}',
            parse_output=True,
        )
        pport_id = json_output.get('id')
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {sport1}',
            parse_output=True,
        )
        sport1_id = json_output.get('id')
        json_output = self.openstack(
            f'port create --network {self.NETWORK_NAME} {sport2}',
            parse_output=True,
        )
        sport2_id = json_output.get('id')

        self.openstack(
            f'network trunk create --parent-port {pport} {trunk}',
        )
        self.openstack(
            f'network trunk set --subport port={sport1},'
            f'segmentation-type=vlan,segmentation-id=100 {trunk}',
        )
        self.openstack(
            f'network trunk set --subport port={sport2},'
            f'segmentation-type=vlan,segmentation-id=101 {trunk}',
        )

        # NOTE(ralonsoh): keep this order to first delete the trunk and then
        # the ports.
        self.addCleanup(self.openstack, f'port delete {pport_id}')
        self.addCleanup(self.openstack, f'port delete {sport1_id}')
        self.addCleanup(self.openstack, f'port delete {sport2_id}')
        self.addCleanup(self.openstack, f'network trunk delete {trunk}')

        return pport_id, sport1_id, sport2_id

    def check_subports(self, subports, pport_id, sport1_id, sport2_id):
        self.assertEqual(2, len(subports))
        for subport in subports:
            if subport['port_id'] == sport1_id:
                self.assertEqual(100, subport['segmentation_id'])
            elif subport['port_id'] == sport2_id:
                self.assertEqual(101, subport['segmentation_id'])
            else:
                self.fail(
                    f'Port {pport_id} does not have subport '
                    f'{subport["port_id"]}'
                )
            self.assertEqual('vlan', subport['segmentation_type'])

    def test_port_list_with_trunk(self):
        pport_id, sport1_id, sport2_id = self._trunk_creation()

        # List all ports with "--long" flag to retrieve the trunk details
        json_output = self.openstack(
            'port list --long',
            parse_output=True,
        )
        port = next(port for port in json_output if port['ID'] == pport_id)
        subports = port['Trunk subports']
        self.check_subports(subports, pport_id, sport1_id, sport2_id)

    def test_port_show_with_trunk(self):
        pport_id, sport1_id, sport2_id = self._trunk_creation()

        # List all ports with "--long" flag to retrieve the trunk details
        port = self.openstack(
            f'port show {pport_id}',
            parse_output=True,
        )
        subports = port['trunk_details']['sub_ports']
        self.check_subports(subports, pport_id, sport1_id, sport2_id)
