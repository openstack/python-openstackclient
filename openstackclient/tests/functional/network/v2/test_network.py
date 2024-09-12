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

from openstackclient.tests.functional.network.v2 import common


class NetworkTests(common.NetworkTagTests):
    """Functional tests for network"""

    base_command = 'network'

    def test_network_create_compute(self):
        """Test Nova-net create options, delete"""
        if self.haz_network:
            self.skipTest("Skip Nova-net test")

        # Network create with minimum options
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--subnet 1.2.3.4/28 ' + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network delete ' + name1)
        self.assertIsNotNone(cmd_output["id"])

        self.assertEqual(
            name1,
            cmd_output["label"],
        )
        self.assertEqual(
            '1.2.3.0/28',
            cmd_output["cidr"],
        )

        # Network create with more options
        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--subnet 1.2.4.4/28 ' + '--share ' + name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network delete ' + name2)
        self.assertIsNotNone(cmd_output["id"])

        self.assertEqual(
            name2,
            cmd_output["label"],
        )
        self.assertEqual(
            '1.2.4.0/28',
            cmd_output["cidr"],
        )
        self.assertTrue(
            cmd_output["share_address"],
        )

    def test_network_create_network(self):
        """Test Neutron create options, delete"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        # Get project IDs
        cmd_output = self.openstack('token issue ', parse_output=True)
        auth_project_id = cmd_output['project_id']

        cmd_output = self.openstack('project list ', parse_output=True)
        admin_project_id = None
        demo_project_id = None
        for p in cmd_output:
            if p['Name'] == 'admin':
                admin_project_id = p['ID']
            if p['Name'] == 'demo':
                demo_project_id = p['ID']

        # Verify assumptions:
        # * admin and demo projects are present
        # * demo and admin are distinct projects
        # * tests run as admin
        self.assertIsNotNone(admin_project_id)
        self.assertIsNotNone(demo_project_id)
        self.assertNotEqual(admin_project_id, demo_project_id)
        self.assertEqual(admin_project_id, auth_project_id)

        # Network create with no options
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network delete ' + name1)
        self.assertIsNotNone(cmd_output["id"])

        # Check the default values
        self.assertEqual(
            admin_project_id,
            cmd_output["project_id"],
        )
        self.assertEqual(
            '',
            cmd_output["description"],
        )
        self.assertEqual(
            True,
            cmd_output["admin_state_up"],
        )
        self.assertFalse(
            cmd_output["shared"],
        )
        self.assertEqual(
            False,
            cmd_output["router:external"],
        )

        # Network create with options
        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--project demo ' + name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network delete ' + name2)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            demo_project_id,
            cmd_output["project_id"],
        )
        self.assertEqual(
            '',
            cmd_output["description"],
        )

    def test_network_delete_compute(self):
        """Test create, delete multiple"""
        if self.haz_network:
            self.skipTest("Skip Nova-net test")

        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--subnet 9.8.7.6/28 ' + name1,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            name1,
            cmd_output["label"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--subnet 8.7.6.5/28 ' + name2,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            name2,
            cmd_output["label"],
        )

    def test_network_delete_network(self):
        """Test create, delete multiple"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--description aaaa ' + name1,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create ' + '--description bbbb ' + name2,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )

        del_output = self.openstack(f'network delete {name1} {name2}')
        self.assertOutput('', del_output)

    def test_network_list(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        if self.haz_network:
            network_options = '--description aaaa --no-default '
        else:
            network_options = '--subnet 3.4.5.6/28 '
        cmd_output = self.openstack(
            'network create ' + network_options + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, f'network delete {name1}')
        self.assertIsNotNone(cmd_output["id"])
        if self.haz_network:
            self.assertEqual(
                'aaaa',
                cmd_output["description"],
            )
            # Check the default values
            self.assertEqual(
                True,
                cmd_output["admin_state_up"],
            )
            self.assertFalse(cmd_output["shared"])
            self.assertEqual(
                False,
                cmd_output["router:external"],
            )
            self.assertFalse(cmd_output["is_default"])
            self.assertTrue(cmd_output["port_security_enabled"])
        else:
            self.assertEqual(
                '3.4.5.0/28',
                cmd_output["cidr"],
            )

        name2 = uuid.uuid4().hex
        if self.haz_network:
            network_options = '--description bbbb --disable '
        else:
            network_options = '--subnet 4.5.6.7/28 '
        cmd_output = self.openstack(
            f'network create --share {network_options}{name2}',
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network delete ' + name2)
        self.assertIsNotNone(cmd_output["id"])
        if self.haz_network:
            self.assertEqual(
                'bbbb',
                cmd_output["description"],
            )
            self.assertEqual(
                False,
                cmd_output["admin_state_up"],
            )
            self.assertTrue(cmd_output["shared"])
            self.assertFalse(cmd_output["is_default"])
            self.assertTrue(cmd_output["port_security_enabled"])
        else:
            self.assertEqual(
                '4.5.6.0/28',
                cmd_output["cidr"],
            )
            self.assertTrue(cmd_output["share_address"])

        # Test list
        cmd_output = self.openstack(
            "network list ",
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --long
        if self.haz_network:
            cmd_output = self.openstack(
                "network list --long",
                parse_output=True,
            )
            col_name = [x["Name"] for x in cmd_output]
            self.assertIn(name1, col_name)
            self.assertIn(name2, col_name)

        # Test list --long --enable
        if self.haz_network:
            cmd_output = self.openstack(
                "network list --enable --long",
                parse_output=True,
            )
            col_name = [x["Name"] for x in cmd_output]
            self.assertIn(name1, col_name)
            self.assertNotIn(name2, col_name)

        # Test list --long --disable
        if self.haz_network:
            cmd_output = self.openstack(
                "network list --disable --long",
                parse_output=True,
            )
            col_name = [x["Name"] for x in cmd_output]
            self.assertNotIn(name1, col_name)
            self.assertIn(name2, col_name)

        # Test list --share
        if self.haz_network:
            cmd_output = self.openstack(
                "network list --share ",
                parse_output=True,
            )
            col_name = [x["Name"] for x in cmd_output]
            self.assertNotIn(name1, col_name)
            self.assertIn(name2, col_name)

        # Test list --no-share
        if self.haz_network:
            cmd_output = self.openstack(
                "network list --no-share ",
                parse_output=True,
            )
            col_name = [x["Name"] for x in cmd_output]
            self.assertIn(name1, col_name)
            self.assertNotIn(name2, col_name)

    def test_network_dhcp_agent(self):
        if not self.haz_network:
            self.skipTest("No Network service present")

        if not self.is_extension_enabled("agent"):
            self.skipTest("No dhcp_agent_scheduler extension present")

        if not self.is_extension_enabled("dhcp_agent_scheduler"):
            self.skipTest("No dhcp_agent_scheduler extension present")

        # Get DHCP Agent ID
        cmd_output = self.openstack(
            'network agent list --agent-type dhcp',
            parse_output=True,
        )
        if not cmd_output:
            self.skipTest("No agents with type=dhcp available")

        agent_id = cmd_output[0]['ID']

        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            f'network create --description aaaa {name1}',
            parse_output=True,
        )

        self.addCleanup(self.openstack, f'network delete {name1}')

        # Get network ID
        network_id = cmd_output['id']

        # Add Agent to Network
        self.openstack(
            f'network agent add network --dhcp {agent_id} {network_id}'
        )

        # Test network list --agent
        cmd_output = self.openstack(
            f'network list --agent {agent_id}',
            parse_output=True,
        )

        # Cleanup
        # Remove Agent from Network
        self.openstack(
            f'network agent remove network --dhcp {agent_id} {network_id}'
        )

        # Assert
        col_name = [x["ID"] for x in cmd_output]
        self.assertIn(network_id, col_name)

    def test_network_set(self):
        """Tests create options, set, show, delete"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'network create '
            '--description aaaa '
            '--enable '
            '--no-share '
            '--internal '
            '--no-default '
            f'--enable-port-security {name}',
            parse_output=True,
        )
        self.addCleanup(self.openstack, f'network delete {name}')
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )
        self.assertEqual(
            True,
            cmd_output["admin_state_up"],
        )
        self.assertFalse(cmd_output["shared"])
        self.assertEqual(
            False,
            cmd_output["router:external"],
        )

        self.assertFalse(cmd_output["is_default"])
        self.assertTrue(cmd_output["port_security_enabled"])

        raw_output = self.openstack(
            'network set '
            '--description cccc '
            '--disable '
            '--share '
            '--external '
            f'--disable-port-security {name}'
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'network show ' + name,
            parse_output=True,
        )

        self.assertEqual(
            'cccc',
            cmd_output["description"],
        )
        self.assertEqual(
            False,
            cmd_output["admin_state_up"],
        )
        self.assertTrue(cmd_output["shared"])
        self.assertEqual(
            True,
            cmd_output["router:external"],
        )
        self.assertFalse(cmd_output["is_default"])
        self.assertFalse(cmd_output["port_security_enabled"])
