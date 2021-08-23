#   Copyright 2021 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import json
import uuid

from openstackclient.tests.functional.network.v2 import common


class LocalIPTests(common.NetworkTests):
    """Functional tests for local IP"""

    def setUp(self):
        super(LocalIPTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")
        if not self.is_extension_enabled('local-ip'):
            self.skipTest("No local-ip extension present")

    def test_local_ip_create_and_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'local ip create -f json ' +
            name1
        ))
        self.assertEqual(
            name1,
            cmd_output['name'],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'local ip create -f json ' +
            name2
        ))
        self.assertEqual(
            name2,
            cmd_output['name'],
        )

        raw_output = self.openstack(
            'local ip delete ' + name1 + ' ' + name2,
        )
        self.assertOutput('', raw_output)

    def test_local_ip_list(self):
        """Test create, list filters, delete"""
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
        cmd_output = json.loads(self.openstack(
            'local ip create -f json ' +
            name1
        ))
        self.addCleanup(self.openstack, 'local ip delete ' + name1)
        self.assertEqual(
            admin_project_id,
            cmd_output["project_id"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'local ip create -f json ' +
            '--project ' + demo_project_id +
            ' ' + name2
        ))
        self.addCleanup(self.openstack, 'local ip delete ' + name2)
        self.assertEqual(
            demo_project_id,
            cmd_output["project_id"],
        )

        # Test list
        cmd_output = json.loads(self.openstack(
            'local ip list -f json ',
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --project
        cmd_output = json.loads(self.openstack(
            'local ip list -f json ' +
            '--project ' + demo_project_id
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # Test list --name
        cmd_output = json.loads(self.openstack(
            'local ip list -f json ' +
            '--name ' + name1
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

    def test_local_ip_set_unset_and_show(self):
        """Tests create options, set, and show"""
        name = uuid.uuid4().hex
        newname = name + "_"
        cmd_output = json.loads(self.openstack(
            'local ip create -f json ' +
            '--description aaaa ' +
            name
        ))
        self.addCleanup(self.openstack, 'local ip delete ' + newname)
        self.assertEqual(name, cmd_output['name'])
        self.assertEqual('aaaa', cmd_output['description'])

        # Test set name and description
        raw_output = self.openstack(
            'local ip set ' +
            '--name ' + newname + ' ' +
            '--description bbbb ' +
            name,
        )
        self.assertOutput('', raw_output)

        # Show the updated local ip
        cmd_output = json.loads(self.openstack(
            'local ip show -f json ' +
            newname,
        ))
        self.assertEqual(newname, cmd_output['name'])
        self.assertEqual('bbbb', cmd_output['description'])
