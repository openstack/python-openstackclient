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

import random
import re
import uuid

from openstackclient.tests.functional.network.v2 import common


class FloatingIpTests(common.NetworkTests):
    """Functional tests for floating ip"""
    SUBNET_NAME = uuid.uuid4().hex
    NETWORK_NAME = uuid.uuid4().hex
    PRIVATE_NETWORK_NAME = uuid.uuid4().hex
    PRIVATE_SUBNET_NAME = uuid.uuid4().hex
    ROUTER = uuid.uuid4().hex
    PORT_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            # Set up some regex for matching below
            cls.re_id = re.compile("id\s+\|\s+(\S+)")
            cls.re_floating_ip = re.compile("floating_ip_address\s+\|\s+(\S+)")
            cls.re_fixed_ip = re.compile("fixed_ip_address\s+\|\s+(\S+)")
            cls.re_description = re.compile("description\s+\|\s+([^|]+?)\s+\|")
            cls.re_network_id = re.compile("floating_network_id\s+\|\s+(\S+)")
            cls.re_port_id = re.compile("\s+id\s+\|\s+(\S+)")
            cls.re_fp_port_id = re.compile("\s+port_id\s+\|\s+(\S+)")

            # Create a network for the floating ip
            raw_output = cls.openstack(
                'network create --external ' + cls.NETWORK_NAME
            )
            cls.network_id = re.search(cls.re_id, raw_output).group(1)

            # Create a private network for the port
            raw_output = cls.openstack(
                'network create ' + cls.PRIVATE_NETWORK_NAME
            )
            cls.private_network_id = re.search(cls.re_id, raw_output).group(1)

            # Try random subnet range for subnet creating
            # Because we can not determine ahead of time what subnets are
            # already in use, possibly by another test running in parallel,
            # try 4 times
            for i in range(4):
                # Make a random subnet
                cls.subnet = ".".join(map(
                    str,
                    (random.randint(0, 223) for _ in range(3))
                )) + ".0/26"
                cls.private_subnet = ".".join(map(
                    str,
                    (random.randint(0, 223) for _ in range(3))
                )) + ".0/26"
                try:
                    # Create a subnet for the network
                    raw_output = cls.openstack(
                        'subnet create ' +
                        '--network ' + cls.NETWORK_NAME + ' ' +
                        '--subnet-range ' + cls.subnet + ' ' +
                        cls.SUBNET_NAME
                    )
                    # Create a subnet for the private network
                    priv_raw_output = cls.openstack(
                        'subnet create ' +
                        '--network ' + cls.PRIVATE_NETWORK_NAME + ' ' +
                        '--subnet-range ' + cls.private_subnet + ' ' +
                        cls.PRIVATE_SUBNET_NAME
                    )
                except Exception:
                    if (i == 3):
                        # raise the exception at the last time
                        raise
                    pass
                else:
                    # break and no longer retry if create sucessfully
                    break

            cls.subnet_id = re.search(cls.re_id, raw_output).group(1)
            cls.private_subnet_id = re.search(
                cls.re_id, priv_raw_output
            ).group(1)

    @classmethod
    def tearDownClass(cls):
        if cls.haz_network:
            raw_output = cls.openstack(
                'subnet delete ' + cls.SUBNET_NAME,
            )
            cls.assertOutput('', raw_output)
            raw_output = cls.openstack(
                'subnet delete ' + cls.PRIVATE_SUBNET_NAME,
            )
            cls.assertOutput('', raw_output)
            raw_output = cls.openstack(
                'network delete ' + cls.NETWORK_NAME,
            )
            cls.assertOutput('', raw_output)
            raw_output = cls.openstack(
                'network delete ' + cls.PRIVATE_NETWORK_NAME,
            )
            cls.assertOutput('', raw_output)

    def setUp(self):
        super(FloatingIpTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_floating_ip_delete(self):
        """Test create, delete multiple"""
        raw_output = self.openstack(
            'floating ip create ' +
            '--description aaaa ' +
            self.NETWORK_NAME
        )
        re_ip = re.search(self.re_floating_ip, raw_output)
        self.assertIsNotNone(re_ip)
        ip1 = re_ip.group(1)
        self.assertEqual(
            'aaaa',
            re.search(self.re_description, raw_output).group(1),
        )

        raw_output = self.openstack(
            'floating ip create ' +
            '--description bbbb ' +
            self.NETWORK_NAME
        )
        ip2 = re.search(self.re_floating_ip, raw_output).group(1)
        self.assertEqual(
            'bbbb',
            re.search(self.re_description, raw_output).group(1),
        )

        # Clean up after ourselves
        raw_output = self.openstack('floating ip delete ' + ip1 + ' ' + ip2)
        self.assertOutput('', raw_output)

    def test_floating_ip_list(self):
        """Test create defaults, list filters, delete"""
        raw_output = self.openstack(
            'floating ip create ' +
            '--description aaaa ' +
            self.NETWORK_NAME
        )
        re_ip = re.search(self.re_floating_ip, raw_output)
        self.assertIsNotNone(re_ip)
        ip1 = re_ip.group(1)
        self.addCleanup(self.openstack, 'floating ip delete ' + ip1)
        self.assertEqual(
            'aaaa',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertIsNotNone(re.search(self.re_network_id, raw_output))

        raw_output = self.openstack(
            'floating ip create ' +
            '--description bbbb ' +
            self.NETWORK_NAME
        )
        ip2 = re.search(self.re_floating_ip, raw_output).group(1)
        self.addCleanup(self.openstack, 'floating ip delete ' + ip2)
        self.assertEqual(
            'bbbb',
            re.search(self.re_description, raw_output).group(1),
        )

        # Test list
        raw_output = self.openstack('floating ip list')
        self.assertIsNotNone(re.search("\|\s+" + ip1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + ip2 + "\s+\|", raw_output))

        # Test list --long
        raw_output = self.openstack('floating ip list --long')
        self.assertIsNotNone(re.search("\|\s+" + ip1 + "\s+\|", raw_output))
        self.assertIsNotNone(re.search("\|\s+" + ip2 + "\s+\|", raw_output))

        # TODO(dtroyer): add more filter tests

    def test_floating_ip_show(self):
        """Test show"""
        raw_output = self.openstack(
            'floating ip create ' +
            '--description shosho ' +
            # '--fixed-ip-address 1.2.3.4 ' +
            self.NETWORK_NAME
        )
        re_ip = re.search(self.re_floating_ip, raw_output)
        self.assertIsNotNone(re_ip)
        ip = re_ip.group(1)

        raw_output = self.openstack('floating ip show ' + ip)
        self.addCleanup(self.openstack, 'floating ip delete ' + ip)

        self.assertEqual(
            'shosho',
            re.search(self.re_description, raw_output).group(1),
        )
        # TODO(dtroyer): not working???
        # self.assertEqual(
        #     '1.2.3.4',
        #     re.search(self.re_floating_ip, raw_output).group(1),
        # )
        self.assertIsNotNone(re.search(self.re_network_id, raw_output))

    def test_floating_ip_set_and_unset_port(self):
        """Test Floating IP Set and Unset port"""
        raw_output = self.openstack(
            'floating ip create ' +
            '--description shosho ' +
            self.NETWORK_NAME
        )
        re_ip = re.search(self.re_floating_ip, raw_output)
        fp_ip = re_ip.group(1)
        self.addCleanup(self.openstack, 'floating ip delete ' + fp_ip)
        self.assertIsNotNone(fp_ip)

        raw_output1 = self.openstack(
            'port create --network ' + self.PRIVATE_NETWORK_NAME
            + ' --fixed-ip subnet=' + self.PRIVATE_SUBNET_NAME +
            ' ' + self.PORT_NAME
        )
        re_port_id = re.search(self.re_port_id, raw_output1)
        self.assertIsNotNone(re_port_id)
        port_id = re_port_id.group(1)

        router = self.openstack('router create ' + self.ROUTER)
        self.assertIsNotNone(router)
        self.addCleanup(self.openstack, 'router delete ' + self.ROUTER)

        self.openstack('router add port ' + self.ROUTER +
                       ' ' + port_id)
        self.openstack('router set --external-gateway ' + self.NETWORK_NAME +
                       ' ' + self.ROUTER)

        self.addCleanup(self.openstack, 'router unset --external-gateway '
                        + self.ROUTER)
        self.addCleanup(self.openstack, 'router remove port ' + self.ROUTER
                        + ' ' + port_id)

        raw_output = self.openstack(
            'floating ip set ' +
            fp_ip + ' --port ' + port_id)
        self.addCleanup(self.openstack, 'floating ip unset --port ' + fp_ip)

        show_output = self.openstack(
            'floating ip show ' + fp_ip)

        self.assertEqual(
            port_id,
            re.search(self.re_fp_port_id, show_output).group(1))
