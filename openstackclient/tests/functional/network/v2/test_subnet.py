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
import random
import uuid

from openstackclient.tests.functional.network.v2 import common


class SubnetTests(common.NetworkTagTests):
    """Functional tests for subnet"""

    base_command = 'subnet'

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            cls.NETWORK_NAME = uuid.uuid4().hex

            # Create a network for the all subnet tests
            cmd_output = json.loads(cls.openstack(
                'network create -f json ' +
                cls.NETWORK_NAME
            ))
            # Get network_id for assertEqual
            cls.NETWORK_ID = cmd_output["id"]

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_network:
                raw_output = cls.openstack(
                    'network delete ' +
                    cls.NETWORK_NAME
                )
                cls.assertOutput('', raw_output)
        finally:
            super(SubnetTests, cls).tearDownClass()

    def setUp(self):
        super(SubnetTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_subnet_create_and_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd = ('subnet create -f json --network ' +
               self.NETWORK_NAME +
               ' --subnet-range')
        cmd_output = self._subnet_create(cmd, name1)
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            self.NETWORK_ID,
            cmd_output["network_id"],
        )
        name2 = uuid.uuid4().hex
        cmd = ('subnet create -f json --network ' +
               self.NETWORK_NAME +
               ' --subnet-range')
        cmd_output = self._subnet_create(cmd, name2)
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            self.NETWORK_ID,
            cmd_output["network_id"],
        )

        del_output = self.openstack(
            'subnet delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_subnet_list(self):
        """Test create, list filter"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        cmd = ('subnet create -f json ' +
               '--network ' + self.NETWORK_NAME +
               ' --dhcp --subnet-range')
        cmd_output = self._subnet_create(cmd, name1)

        self.addCleanup(self.openstack, 'subnet delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            True,
            cmd_output["enable_dhcp"],
        )
        self.assertEqual(
            self.NETWORK_ID,
            cmd_output["network_id"],
        )
        self.assertEqual(
            4,
            cmd_output["ip_version"],
        )

        cmd = ('subnet create -f json ' +
               '--network ' + self.NETWORK_NAME +
               ' --ip-version 6 --no-dhcp ' +
               '--subnet-range')
        cmd_output = self._subnet_create(cmd, name2, is_type_ipv4=False)

        self.addCleanup(self.openstack, 'subnet delete ' + name2)
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            False,
            cmd_output["enable_dhcp"],
        )
        self.assertEqual(
            self.NETWORK_ID,
            cmd_output["network_id"],
        )
        self.assertEqual(
            6,
            cmd_output["ip_version"],
        )

        # Test list --long
        cmd_output = json.loads(self.openstack(
            'subnet list -f json ' +
            '--long '
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --name
        cmd_output = json.loads(self.openstack(
            'subnet list -f json ' +
            '--name ' + name1
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --ip-version
        cmd_output = json.loads(self.openstack(
            'subnet list -f json ' +
            '--ip-version 6'
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # Test list --network
        cmd_output = json.loads(self.openstack(
            'subnet list -f json ' +
            '--network ' + self.NETWORK_ID
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --no-dhcp
        cmd_output = json.loads(self.openstack(
            'subnet list -f json ' +
            '--no-dhcp '
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

    def test_subnet_set_show_unset(self):
        """Test create subnet, set, unset, show"""

        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd = ('subnet create -f json ' +
               '--network ' + self.NETWORK_NAME +
               ' --description aaaa --subnet-range')
        cmd_output = self._subnet_create(cmd, name)

        self.addCleanup(self.openstack, 'subnet delete ' + new_name)
        self.assertEqual(
            name,
            cmd_output["name"],
        )
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )

        # Test set --no-dhcp --name --gateway --description
        cmd_output = self.openstack(
            'subnet set ' +
            '--name ' + new_name +
            ' --description bbbb ' +
            '--no-dhcp ' +
            '--gateway 10.10.11.1 ' +
            '--service-type network:floatingip_agent_gateway ' +
            name
        )
        self.assertOutput('', cmd_output)

        cmd_output = json.loads(self.openstack(
            'subnet show -f json ' +
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
            False,
            cmd_output["enable_dhcp"],
        )
        self.assertEqual(
            '10.10.11.1',
            cmd_output["gateway_ip"],
        )
        self.assertEqual(
            ['network:floatingip_agent_gateway'],
            cmd_output["service_types"],
        )

        # Test unset
        cmd_output = self.openstack(
            'subnet unset ' +
            '--service-type network:floatingip_agent_gateway ' +
            new_name
        )
        self.assertOutput('', cmd_output)

        cmd_output = json.loads(self.openstack(
            'subnet show -f json ' +
            new_name
        ))
        self.assertEqual(
            [],
            cmd_output["service_types"],
        )

    def _subnet_create(self, cmd, name, is_type_ipv4=True):
        # Try random subnet range for subnet creating
        # Because we can not determine ahead of time what subnets are already
        # in use, possibly by another test running in parallel, try 4 times
        for i in range(4):
            # Make a random subnet
            if is_type_ipv4:
                subnet = ".".join(map(
                    str,
                    (random.randint(0, 223) for _ in range(3))
                )) + ".0/26"
            else:
                subnet = ":".join(map(
                    str,
                    (hex(random.randint(0, 65535))[2:] for _ in range(7))
                )) + ":0/112"
            try:
                cmd_output = json.loads(self.openstack(
                    cmd + ' ' + subnet + ' ' +
                    name
                ))
            except Exception:
                if (i == 3):
                    # raise the exception at the last time
                    raise
                pass
            else:
                # break and no longer retry if create successfully
                break
        return cmd_output

    def _create_resource_for_tag_test(self, name, args):
        cmd = ('subnet create -f json --network ' +
               self.NETWORK_NAME + ' ' + args +
               ' --subnet-range')
        return self._subnet_create(cmd, name)
