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


class RouterTests(common.NetworkTagTests):
    """Functional tests for router"""

    base_command = 'router'

    def test_router_create_and_delete(self):
        """Test create options, delete multiple"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'router create ' + name1,
            parse_output=True,
        )
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        cmd_output = self.openstack(
            'router create ' + name2,
            parse_output=True,
        )
        self.assertEqual(
            name2,
            cmd_output["name"],
        )

        del_output = self.openstack('router delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_router_create_with_external_gateway(self):
        network_name = uuid.uuid4().hex
        subnet_name = uuid.uuid4().hex
        qos_policy = uuid.uuid4().hex
        router_name = uuid.uuid4().hex

        cmd_net = self.openstack(
            f'network create --external {network_name}', parse_output=True
        )
        self.addCleanup(self.openstack, f'network delete {network_name}')
        network_id = cmd_net['id']

        self.openstack(
            f'subnet create {subnet_name} '
            f'--network {network_name} --subnet-range 10.0.0.0/24'
        )

        cmd_qos = self.openstack(
            f'network qos policy create {qos_policy}', parse_output=True
        )
        self.addCleanup(
            self.openstack, f'network qos policy delete {qos_policy}'
        )
        qos_id = cmd_qos['id']

        self.openstack(
            f'router create --external-gateway {network_name} '
            f'--qos-policy {qos_policy} {router_name}'
        )
        self.addCleanup(self.openstack, f'router delete {router_name}')

        cmd_output = self.openstack(
            f'router show {router_name}', parse_output=True
        )
        gw_info = cmd_output['external_gateway_info']
        self.assertEqual(network_id, gw_info['network_id'])
        self.assertEqual(qos_id, gw_info['qos_policy_id'])

    def test_router_list(self):
        """Test create, list filter"""
        # Get project IDs
        cmd_output = self.openstack('token issue', parse_output=True)
        auth_project_id = cmd_output['project_id']

        cmd_output = self.openstack('project list', parse_output=True)
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

        # type narrow
        assert admin_project_id is not None
        assert demo_project_id is not None

        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'router create ' + '--disable ' + name1,
            parse_output=True,
        )

        self.addCleanup(self.openstack, 'router delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            False,
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            admin_project_id,
            cmd_output["project_id"],
        )
        cmd_output = self.openstack(
            'router create ' + '--project ' + demo_project_id + ' ' + name2,
            parse_output=True,
        )

        self.addCleanup(self.openstack, 'router delete ' + name2)
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            True,
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            demo_project_id,
            cmd_output["project_id"],
        )

        # Test list --project
        cmd_output = self.openstack(
            'router list ' + '--project ' + demo_project_id,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # Test list --disable
        cmd_output = self.openstack(
            'router list ' + '--disable ',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --name
        cmd_output = self.openstack(
            'router list ' + '--name ' + name1,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --long
        cmd_output = self.openstack(
            'router list ' + '--long ',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

    def test_router_list_l3_agent(self):
        """Tests create router, add l3 agent, list, delete"""

        if not self.is_extension_enabled("l3_agent_scheduler"):
            self.skipTest("No l3_agent_scheduler extension present")

        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'router create ' + name,
            parse_output=True,
        )

        self.addCleanup(self.openstack, 'router delete ' + name)
        # Get router ID
        router_id = cmd_output['id']
        # Get l3 agent id
        cmd_output = self.openstack(
            'network agent list --agent-type l3',
            parse_output=True,
        )

        # Check at least one L3 agent is included in the response.
        self.assertTrue(cmd_output)
        agent_id = cmd_output[0]['ID']

        # Add router to agent
        self.openstack(
            'network agent add router --l3 ' + agent_id + ' ' + router_id
        )

        cmd_output = self.openstack(
            'router list --agent ' + agent_id,
            parse_output=True,
        )
        router_ids = [x['ID'] for x in cmd_output]
        self.assertIn(router_id, router_ids)

        # Remove router from agent
        self.openstack(
            'network agent remove router --l3 ' + agent_id + ' ' + router_id
        )
        cmd_output = self.openstack(
            'router list --agent ' + agent_id,
            parse_output=True,
        )
        router_ids = [x['ID'] for x in cmd_output]
        self.assertNotIn(router_id, router_ids)

    def test_router_set_show_unset(self):
        """Tests create router, set, unset, show"""

        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd_output = self.openstack(
            'router create ' + '--description aaaa ' + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'router delete ' + new_name)
        self.assertEqual(
            name,
            cmd_output["name"],
        )
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )

        # Test set --disable
        cmd_output = self.openstack(
            'router set '
            + '--name '
            + new_name
            + ' --description bbbb '
            + '--disable '
            + name
        )
        self.assertOutput('', cmd_output)

        cmd_output = self.openstack(
            'router show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            False,
            cmd_output["admin_state_up"],
        )

        # Test set --ha --distributed
        self._test_set_router_distributed(new_name)

        # Test unset
        cmd_output = self.openstack(
            'router unset ' + '--external-gateway ' + new_name
        )
        cmd_output = self.openstack(
            'router show ' + new_name,
            parse_output=True,
        )
        self.assertIsNone(cmd_output["external_gateway_info"])

    def _test_set_router_distributed(self, router_name):
        if not self.is_extension_enabled("dvr"):
            return

        cmd_output = self.openstack(
            'router set '
            + '--distributed '
            + '--external-gateway public '
            + router_name
        )
        self.assertOutput('', cmd_output)

        cmd_output = self.openstack(
            'router show ' + router_name,
            parse_output=True,
        )
        self.assertTrue(cmd_output["distributed"])
        self.assertIsNotNone(cmd_output["external_gateway_info"])

    def test_router_add_remove_route(self):
        network_name = uuid.uuid4().hex
        subnet_name = uuid.uuid4().hex
        router_name = uuid.uuid4().hex

        self.openstack(f'network create {network_name}')
        self.addCleanup(self.openstack, f'network delete {network_name}')

        self.openstack(
            f'subnet create {subnet_name} '
            f'--network {network_name} --subnet-range 10.0.0.0/24'
        )

        self.openstack(f'router create {router_name}')
        self.addCleanup(self.openstack, f'router delete {router_name}')

        self.openstack(f'router add subnet {router_name} {subnet_name}')
        self.addCleanup(
            self.openstack,
            f'router remove subnet {router_name} {subnet_name}',
        )

        out1 = (
            self.openstack(
                f'router add route {router_name} '
                '--route destination=10.0.10.0/24,gateway=10.0.0.10',
                parse_output=True,
            ),
        )
        self.assertEqual(1, len(out1[0]['routes']))

        self.addCleanup(self.openstack, f'router set {router_name} --no-route')

        out2 = (
            self.openstack(
                f'router add route {router_name} '
                '--route destination=10.0.10.0/24,gateway=10.0.0.10 '
                '--route destination=10.0.11.0/24,gateway=10.0.0.11',
                parse_output=True,
            ),
        )
        self.assertEqual(2, len(out2[0]['routes']))

        out3 = (
            self.openstack(
                f'router remove route {router_name} '
                '--route destination=10.0.11.0/24,gateway=10.0.0.11 '
                '--route destination=10.0.12.0/24,gateway=10.0.0.12',
                parse_output=True,
            ),
        )
        self.assertEqual(1, len(out3[0]['routes']))
