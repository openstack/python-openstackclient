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


class AddressScopeTests(common.NetworkTests):
    """Functional tests for address scope"""

    # NOTE(dtroyer): Do not normalize the setup and teardown of the resource
    #                creation and deletion.  Little is gained when each test
    #                has its own needs and there are collisions when running
    #                tests in parallel.

    def test_address_scope_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'address scope create ' + name1,
            parse_output=True,
        )
        self.assertEqual(
            name1,
            cmd_output['name'],
        )
        # Check the default values
        self.assertFalse(cmd_output['shared'])

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'address scope create ' + name2,
            parse_output=True,
        )
        self.assertEqual(
            name2,
            cmd_output['name'],
        )

        raw_output = self.openstack(
            'address scope delete ' + name1 + ' ' + name2,
        )
        self.assertOutput('', raw_output)

    def test_address_scope_list(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'address scope create ' + '--ip-version 4 ' + '--share ' + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'address scope delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output['name'],
        )
        self.assertEqual(
            4,
            cmd_output['ip_version'],
        )
        self.assertTrue(cmd_output['shared'])

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'address scope create '
            + '--ip-version 6 '
            + '--no-share '
            + name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'address scope delete ' + name2)
        self.assertEqual(
            name2,
            cmd_output['name'],
        )
        self.assertEqual(
            6,
            cmd_output['ip_version'],
        )
        self.assertFalse(cmd_output['shared'])

        # Test list
        cmd_output = self.openstack(
            'address scope list ',
            parse_output=True,
        )
        col_data = [x["IP Version"] for x in cmd_output]
        self.assertIn(4, col_data)
        self.assertIn(6, col_data)

        # Test list --share
        cmd_output = self.openstack(
            'address scope list --share',
            parse_output=True,
        )
        col_data = [x["Shared"] for x in cmd_output]
        self.assertIn(True, col_data)
        self.assertNotIn(False, col_data)

        # Test list --no-share
        cmd_output = self.openstack(
            'address scope list --no-share',
            parse_output=True,
        )
        col_data = [x["Shared"] for x in cmd_output]
        self.assertIn(False, col_data)
        self.assertNotIn(True, col_data)

    def test_address_scope_set(self):
        """Tests create options, set, show, delete"""
        name = uuid.uuid4().hex
        newname = name + "_"
        cmd_output = self.openstack(
            'address scope create ' + '--ip-version 4 ' + '--no-share ' + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'address scope delete ' + newname)
        self.assertEqual(
            name,
            cmd_output['name'],
        )
        self.assertEqual(
            4,
            cmd_output['ip_version'],
        )
        self.assertFalse(cmd_output['shared'])

        raw_output = self.openstack(
            'address scope set ' + '--name ' + newname + ' --share ' + name,
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'address scope show ' + newname,
            parse_output=True,
        )
        self.assertEqual(
            newname,
            cmd_output['name'],
        )
        self.assertEqual(
            4,
            cmd_output['ip_version'],
        )
        self.assertTrue(cmd_output['shared'])
