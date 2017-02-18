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

from openstackclient.tests.functional import base


class RouterTests(base.TestCase):
    """Functional tests for router. """

    def test_router_create_and_delete(self):
        """Test create options, delete"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'router create -f json ' +
            name1
        ))
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        cmd_output = json.loads(self.openstack(
            'router create -f json ' +
            name2
        ))
        self.assertEqual(
            name2,
            cmd_output["name"],
        )

        del_output = self.openstack(
            'router delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_router_list(self):
        """Test create, list filter"""
        # Get project IDs
        cmd_output = json.loads(self.openstack('token issue -f json '))
        auth_project_id = cmd_output['project_id']

        cmd_output = json.loads(self.openstack('project list -f json '))
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

        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'router create -f json ' +
            '--disable ' +
            name1
        ))
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            "DOWN",
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            admin_project_id,
            cmd_output["project_id"],
        )
        cmd_output = json.loads(self.openstack(
            'router create -f json ' +
            '--project ' + demo_project_id +
            ' ' + name2
        ))
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            "UP",
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            demo_project_id,
            cmd_output["project_id"],
        )

        # Test list --project
        cmd_output = json.loads(self.openstack(
            'router list -f json ' +
            '--project ' + demo_project_id
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # Test list --disable
        cmd_output = json.loads(self.openstack(
            'router list -f json ' +
            '--disable '
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --name
        cmd_output = json.loads(self.openstack(
            'router list -f json ' +
            '--name ' + name1
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --long
        cmd_output = json.loads(self.openstack(
            'router list -f json ' +
            '--long '
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        del_output = self.openstack(
            'router delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_router_set_show_unset(self):
        """Tests create router, set, unset, show, delete"""

        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd_output = json.loads(self.openstack(
            'router create -f json ' +
            '--description aaaa ' +
            name
        ))
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
            'router set ' +
            '--name ' + new_name +
            ' --description bbbb ' +
            '--disable ' +
            name
        )
        self.assertOutput('', cmd_output)

        cmd_output = json.loads(self.openstack(
            'router show -f json ' +
            new_name
        ))
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            'DOWN',
            cmd_output["admin_state_up"],
        )

        # Test set --ha --distributed
        cmd_output = self.openstack(
            'router set ' +
            '--distributed ' +
            '--external-gateway public ' +
            new_name
        )
        self.assertOutput('', cmd_output)

        cmd_output = json.loads(self.openstack(
            'router show -f json ' +
            new_name
        ))
        self.assertEqual(
            True,
            cmd_output["distributed"],
        )
        self.assertIsNotNone(cmd_output["external_gateway_info"])

        # Test unset
        cmd_output = self.openstack(
            'router unset ' +
            '--external-gateway ' +
            new_name
        )
        cmd_output = json.loads(self.openstack(
            'router show -f json ' +
            new_name
        ))
        self.assertIsNone(cmd_output["external_gateway_info"])

        del_output = self.openstack(
            'router delete ' + new_name)
        self.assertOutput('', del_output)
