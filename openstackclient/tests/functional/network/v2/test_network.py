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


class NetworkTests(base.TestCase):
    """Functional tests for network"""

    def test_network_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network create -f json ' +
            '--description aaaa ' +
            name1
        ))
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network create -f json ' +
            '--description bbbb ' +
            name2
        ))
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )

        del_output = self.openstack('network delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_network_list(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network create -f json ' +
            '--description aaaa ' +
            name1
        ))
        self.addCleanup(self.openstack, 'network delete ' + name1)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )
        # Check the default values
        self.assertEqual(
            'UP',
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            False,
            cmd_output["shared"],
        )
        self.assertEqual(
            'Internal',
            cmd_output["router:external"],
        )
        # NOTE(dtroyer): is_default is not present in the create output
        #                so make sure it stays that way.
        # NOTE(stevemar): is_default *is* present in SDK 0.9.11 and newer,
        #                 but the value seems to always be None, regardless
        #                 of the --default or --no-default value.
        # self.assertEqual('x', cmd_output)
        if ('is_default' in cmd_output):
            self.assertEqual(
                None,
                cmd_output["is_default"],
            )
        self.assertEqual(
            True,
            cmd_output["port_security_enabled"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network create -f json ' +
            '--description bbbb ' +
            '--disable ' +
            '--share ' +
            name2
        ))
        self.addCleanup(self.openstack, 'network delete ' + name2)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            'DOWN',
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            True,
            cmd_output["shared"],
        )
        if ('is_default' in cmd_output):
            self.assertEqual(
                None,
                cmd_output["is_default"],
            )
        self.assertEqual(
            True,
            cmd_output["port_security_enabled"],
        )

        # Test list --long
        cmd_output = json.loads(self.openstack(
            "network list -f json " +
            "--long"
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --long --enable
        cmd_output = json.loads(self.openstack(
            "network list -f json " +
            "--enable " +
            "--long"
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertNotIn(name2, col_name)

        # Test list --long --disable
        cmd_output = json.loads(self.openstack(
            "network list -f json " +
            "--disable " +
            "--long"
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --long --share
        cmd_output = json.loads(self.openstack(
            "network list -f json " +
            "--share " +
            "--long"
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --long --no-share
        cmd_output = json.loads(self.openstack(
            "network list -f json " +
            "--no-share " +
            "--long"
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertNotIn(name2, col_name)

    def test_network_set(self):
        """Tests create options, set, show, delete"""
        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network create -f json ' +
            '--description aaaa ' +
            '--enable ' +
            '--no-share ' +
            '--internal ' +
            '--no-default ' +
            '--enable-port-security ' +
            name
        ))
        self.addCleanup(self.openstack, 'network delete ' + name)
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )
        self.assertEqual(
            'UP',
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            False,
            cmd_output["shared"],
        )
        self.assertEqual(
            'Internal',
            cmd_output["router:external"],
        )
        # NOTE(dtroyer): is_default is not present in the create output
        #                so make sure it stays that way.
        # NOTE(stevemar): is_default *is* present in SDK 0.9.11 and newer,
        #                 but the value seems to always be None, regardless
        #                 of the --default or --no-default value.
        if ('is_default' in cmd_output):
            self.assertEqual(
                None,
                cmd_output["is_default"],
            )
        self.assertEqual(
            True,
            cmd_output["port_security_enabled"],
        )

        raw_output = self.openstack(
            'network set ' +
            '--description cccc ' +
            '--disable ' +
            '--share ' +
            '--external ' +
            '--disable-port-security ' +
            name
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'network show -f json ' + name
        ))

        self.assertEqual(
            'cccc',
            cmd_output["description"],
        )
        self.assertEqual(
            'DOWN',
            cmd_output["admin_state_up"],
        )
        self.assertEqual(
            True,
            cmd_output["shared"],
        )
        self.assertEqual(
            'External',
            cmd_output["router:external"],
        )
        # why not 'None' like above??
        self.assertEqual(
            False,
            cmd_output["is_default"],
        )
        self.assertEqual(
            False,
            cmd_output["port_security_enabled"],
        )

        # NOTE(dtroyer): There is ambiguity around is_default in that
        #                it is not in the API docs and apparently can
        #                not be set when the network is --external,
        #                although the option handling code only looks at
        #                the value of is_default when external is True.
        raw_output = self.openstack(
            'network set ' +
            '--default ' +
            name
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'network show -f json ' + name
        ))

        self.assertEqual(
            'cccc',
            cmd_output["description"],
        )
        # NOTE(dtroyer): This should be 'True'
        self.assertEqual(
            False,
            cmd_output["port_security_enabled"],
        )
