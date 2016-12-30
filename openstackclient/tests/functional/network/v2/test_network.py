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


class NetworkTests(base.TestCase):
    """Functional tests for network"""

    @classmethod
    def setUpClass(cls):
        # Set up some regex for matching below
        cls.re_id = re.compile("id\s+\|\s+(\S+)")
        cls.re_description = re.compile("description\s+\|\s+([^|]+?)\s+\|")
        cls.re_enabled = re.compile("admin_state_up\s+\|\s+(\S+)")
        cls.re_shared = re.compile("shared\s+\|\s+(\S+)")
        cls.re_external = re.compile("router:external\s+\|\s+(\S+)")
        cls.re_default = re.compile("is_default\s+\|\s+(\S+)")
        cls.re_port_security = re.compile(
            "port_security_enabled\s+\|\s+(\S+)"
        )

    def test_network_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network create ' +
            '--description aaaa ' +
            name1
        )
        self.assertEqual(
            'aaaa',
            re.search(self.re_description, raw_output).group(1),
        )
        name2 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network create ' +
            '--description bbbb ' +
            name2
        )
        self.assertEqual(
            'bbbb',
            re.search(self.re_description, raw_output).group(1),
        )

        del_output = self.openstack('network delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_network_list(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network create ' +
            '--description aaaa ' +
            name1
        )
        self.addCleanup(self.openstack, 'network delete ' + name1)
        self.assertEqual(
            'aaaa',
            re.search(self.re_description, raw_output).group(1),
        )
        # Check the default values
        self.assertEqual(
            'UP',
            re.search(self.re_enabled, raw_output).group(1),
        )
        self.assertEqual(
            'False',
            re.search(self.re_shared, raw_output).group(1),
        )
        self.assertEqual(
            'Internal',
            re.search(self.re_external, raw_output).group(1),
        )
        # NOTE(dtroyer): is_default is not present in the create output
        #                so make sure it stays that way.
        self.assertIsNone(re.search(self.re_default, raw_output))
        self.assertEqual(
            'True',
            re.search(self.re_port_security, raw_output).group(1),
        )

        name2 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network create ' +
            '--description bbbb ' +
            '--disable ' +
            '--share ' +
            name2
        )
        self.addCleanup(self.openstack, 'network delete ' + name2)
        self.assertEqual(
            'bbbb',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'DOWN',
            re.search(self.re_enabled, raw_output).group(1),
        )
        self.assertEqual(
            'True',
            re.search(self.re_shared, raw_output).group(1),
        )

        # Test list --long
        raw_output = self.openstack('network list --long')
        self.assertIsNotNone(
            re.search("\|\s+" + name1 + "\s+\|\s+ACTIVE", raw_output)
        )
        self.assertIsNotNone(
            re.search("\|\s+" + name2 + "\s+\|\s+ACTIVE", raw_output)
        )

        # Test list --long --enable
        raw_output = self.openstack('network list --long --enable')
        self.assertIsNotNone(
            re.search("\|\s+" + name1 + "\s+\|\s+ACTIVE", raw_output)
        )
        self.assertIsNone(
            re.search("\|\s+" + name2 + "\s+\|\s+ACTIVE", raw_output)
        )

        # Test list --long --disable
        raw_output = self.openstack('network list --long --disable')
        self.assertIsNone(
            re.search("\|\s+" + name1 + "\s+\|\s+ACTIVE", raw_output)
        )
        self.assertIsNotNone(
            re.search("\|\s+" + name2 + "\s+\|\s+ACTIVE", raw_output)
        )

        # Test list --long --share
        raw_output = self.openstack('network list --long --share')
        self.assertIsNone(
            re.search("\|\s+" + name1 + "\s+\|\s+ACTIVE", raw_output)
        )
        self.assertIsNotNone(
            re.search("\|\s+" + name2 + "\s+\|\s+ACTIVE", raw_output)
        )

        # Test list --long --no-share
        raw_output = self.openstack('network list --long --no-share')
        self.assertIsNotNone(
            re.search("\|\s+" + name1 + "\s+\|\s+ACTIVE", raw_output)
        )
        self.assertIsNone(
            re.search("\|\s+" + name2 + "\s+\|\s+ACTIVE", raw_output)
        )

    def test_network_set(self):
        """Tests create options, set, show, delete"""
        name = uuid.uuid4().hex
        raw_output = self.openstack(
            'network create ' +
            '--description aaaa ' +
            '--enable ' +
            '--no-share ' +
            '--internal ' +
            '--no-default ' +
            '--enable-port-security ' +
            name
        )
        self.addCleanup(self.openstack, 'network delete ' + name)
        self.assertEqual(
            'aaaa',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'UP',
            re.search(self.re_enabled, raw_output).group(1),
        )
        self.assertEqual(
            'False',
            re.search(self.re_shared, raw_output).group(1),
        )
        self.assertEqual(
            'Internal',
            re.search(self.re_external, raw_output).group(1),
        )
        # NOTE(dtroyer): is_default is not present in the create output
        #                so make sure it stays that way.
        self.assertIsNone(re.search(self.re_default, raw_output))
        self.assertEqual(
            'True',
            re.search(self.re_port_security, raw_output).group(1),
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

        raw_output = self.openstack('network show ' + name)

        self.assertEqual(
            'cccc',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'DOWN',
            re.search(self.re_enabled, raw_output).group(1),
        )
        self.assertEqual(
            'True',
            re.search(self.re_shared, raw_output).group(1),
        )
        self.assertEqual(
            'External',
            re.search(self.re_external, raw_output).group(1),
        )
        # why not 'None' like above??
        self.assertEqual(
            'False',
            re.search(self.re_default, raw_output).group(1),
        )
        self.assertEqual(
            'False',
            re.search(self.re_port_security, raw_output).group(1),
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

        raw_output = self.openstack('network show ' + name)

        self.assertEqual(
            'cccc',
            re.search(self.re_description, raw_output).group(1),
        )
        # NOTE(dtroyer): This should be 'True'
        self.assertEqual(
            'False',
            re.search(self.re_default, raw_output).group(1),
        )
