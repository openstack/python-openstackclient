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


class FloatingIpTests(common.NetworkTests):
    """Functional tests for floating ip"""

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            # Create common networks that all tests share
            cls.EXTERNAL_NETWORK_NAME = uuid.uuid4().hex
            cls.PRIVATE_NETWORK_NAME = uuid.uuid4().hex

            # Create a network for the floating ip
            json_output = json.loads(cls.openstack(
                'network create -f json ' +
                '--external ' +
                cls.EXTERNAL_NETWORK_NAME
            ))
            cls.external_network_id = json_output["id"]

            # Create a private network for the port
            json_output = json.loads(cls.openstack(
                'network create -f json ' +
                cls.PRIVATE_NETWORK_NAME
            ))
            cls.private_network_id = json_output["id"]

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.haz_network:
                del_output = cls.openstack(
                    'network delete ' +
                    cls.EXTERNAL_NETWORK_NAME + ' ' +
                    cls.PRIVATE_NETWORK_NAME
                )
                cls.assertOutput('', del_output)
        finally:
            super(FloatingIpTests, cls).tearDownClass()

    def setUp(self):
        super(FloatingIpTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

        # Verify setup
        self.assertIsNotNone(self.external_network_id)
        self.assertIsNotNone(self.private_network_id)

    def _create_subnet(self, network_name, subnet_name):
        subnet_id = None

        # Try random subnet range for subnet creating
        # Because we can not determine ahead of time what subnets are
        # already in use, possibly by another test running in parallel,
        # try 4 times
        for i in range(4):
            # Make a random subnet
            subnet = ".".join(map(
                str,
                (random.randint(0, 223) for _ in range(3))
            )) + ".0/26"
            try:
                # Create a subnet for the network
                json_output = json.loads(self.openstack(
                    'subnet create -f json ' +
                    '--network ' + network_name + ' ' +
                    '--subnet-range ' + subnet + ' ' +
                    subnet_name
                ))
                self.assertIsNotNone(json_output["id"])
                subnet_id = json_output["id"]
            except Exception:
                if (i == 3):
                    # raise the exception at the last time
                    raise
                pass
            else:
                # break and no longer retry if create successfully
                break
        return subnet_id

    def test_floating_ip_delete(self):
        """Test create, delete multiple"""

        # Subnets must exist even if not directly referenced here
        ext_subnet_id = self._create_subnet(
            self.EXTERNAL_NETWORK_NAME,
            "ext-test-delete"
        )
        self.addCleanup(self.openstack, 'subnet delete ' + ext_subnet_id)

        json_output = json.loads(self.openstack(
            'floating ip create -f json ' +
            '--description aaaa ' +
            self.EXTERNAL_NETWORK_NAME
        ))
        self.assertIsNotNone(json_output["id"])
        ip1 = json_output["id"]
        self.assertEqual(
            'aaaa',
            json_output["description"],
        )

        json_output = json.loads(self.openstack(
            'floating ip create -f json ' +
            '--description bbbb ' +
            self.EXTERNAL_NETWORK_NAME
        ))
        self.assertIsNotNone(json_output["id"])
        ip2 = json_output["id"]
        self.assertEqual(
            'bbbb',
            json_output["description"],
        )

        # Clean up after ourselves
        del_output = self.openstack('floating ip delete ' + ip1 + ' ' + ip2)
        self.assertOutput('', del_output)

        self.assertIsNotNone(json_output["floating_network_id"])

    def test_floating_ip_list(self):
        """Test create defaults, list filters, delete"""

        # Subnets must exist even if not directly referenced here
        ext_subnet_id = self._create_subnet(
            self.EXTERNAL_NETWORK_NAME,
            "ext-test-delete"
        )
        self.addCleanup(self.openstack, 'subnet delete ' + ext_subnet_id)

        json_output = json.loads(self.openstack(
            'floating ip create -f json ' +
            '--description aaaa ' +
            self.EXTERNAL_NETWORK_NAME
        ))
        self.assertIsNotNone(json_output["id"])
        ip1 = json_output["id"]
        self.addCleanup(self.openstack, 'floating ip delete ' + ip1)
        self.assertEqual(
            'aaaa',
            json_output["description"],
        )
        self.assertIsNotNone(json_output["floating_network_id"])
        fip1 = json_output["floating_ip_address"]

        json_output = json.loads(self.openstack(
            'floating ip create -f json ' +
            '--description bbbb ' +
            self.EXTERNAL_NETWORK_NAME
        ))
        self.assertIsNotNone(json_output["id"])
        ip2 = json_output["id"]
        self.addCleanup(self.openstack, 'floating ip delete ' + ip2)
        self.assertEqual(
            'bbbb',
            json_output["description"],
        )
        self.assertIsNotNone(json_output["floating_network_id"])
        fip2 = json_output["floating_ip_address"]

        # Test list
        json_output = json.loads(self.openstack(
            'floating ip list -f json'
        ))
        fip_map = {
            item.get('ID'):
                item.get('Floating IP Address') for item in json_output
        }
        # self.assertEqual(item_map, json_output)
        self.assertIn(ip1, fip_map.keys())
        self.assertIn(ip2, fip_map.keys())
        self.assertIn(fip1, fip_map.values())
        self.assertIn(fip2, fip_map.values())

        # Test list --long
        json_output = json.loads(self.openstack(
            'floating ip list -f json ' +
            '--long'
        ))
        fip_map = {
            item.get('ID'):
                item.get('Floating IP Address') for item in json_output
        }
        self.assertIn(ip1, fip_map.keys())
        self.assertIn(ip2, fip_map.keys())
        self.assertIn(fip1, fip_map.values())
        self.assertIn(fip2, fip_map.values())
        desc_map = {
            item.get('ID'): item.get('Description') for item in json_output
        }
        self.assertIn('aaaa', desc_map.values())
        self.assertIn('bbbb', desc_map.values())

        # TODO(dtroyer): add more filter tests

        json_output = json.loads(self.openstack(
            'floating ip show -f json ' +
            ip1
        ))
        self.assertIsNotNone(json_output["id"])
        self.assertEqual(
            ip1,
            json_output["id"],
        )
        self.assertEqual(
            'aaaa',
            json_output["description"],
        )
        self.assertIsNotNone(json_output["floating_network_id"])
        self.assertEqual(
            fip1,
            json_output["floating_ip_address"],
        )

    def test_floating_ip_set_and_unset_port(self):
        """Test Floating IP Set and Unset port"""

        # Subnets must exist even if not directly referenced here
        ext_subnet_id = self._create_subnet(
            self.EXTERNAL_NETWORK_NAME,
            "ext-test-delete"
        )
        self.addCleanup(self.openstack, 'subnet delete ' + ext_subnet_id)
        priv_subnet_id = self._create_subnet(
            self.PRIVATE_NETWORK_NAME,
            "priv-test-delete"
        )
        self.addCleanup(self.openstack, 'subnet delete ' + priv_subnet_id)

        self.ROUTER = uuid.uuid4().hex
        self.PORT_NAME = uuid.uuid4().hex

        json_output = json.loads(self.openstack(
            'floating ip create -f json ' +
            '--description aaaa ' +
            self.EXTERNAL_NETWORK_NAME
        ))
        self.assertIsNotNone(json_output["id"])
        ip1 = json_output["id"]
        self.addCleanup(self.openstack, 'floating ip delete ' + ip1)
        self.assertEqual(
            'aaaa',
            json_output["description"],
        )

        json_output = json.loads(self.openstack(
            'port create -f json ' +
            '--network ' + self.PRIVATE_NETWORK_NAME + ' ' +
            '--fixed-ip subnet=' + priv_subnet_id + ' ' +
            self.PORT_NAME
        ))
        self.assertIsNotNone(json_output["id"])
        port_id = json_output["id"]

        json_output = json.loads(self.openstack(
            'router create -f json ' +
            self.ROUTER
        ))
        self.assertIsNotNone(json_output["id"])
        self.addCleanup(self.openstack, 'router delete ' + self.ROUTER)

        self.openstack(
            'router add port ' +
            self.ROUTER + ' ' +
            port_id
        )

        self.openstack(
            'router set ' +
            '--external-gateway ' + self.EXTERNAL_NETWORK_NAME + ' ' +
            self.ROUTER
        )
        self.addCleanup(
            self.openstack,
            'router unset --external-gateway ' + self.ROUTER,
        )
        self.addCleanup(
            self.openstack,
            'router remove port ' + self.ROUTER + ' ' + port_id,
        )

        self.openstack(
            'floating ip set ' +
            '--port ' + port_id + ' ' +
            ip1
        )
        self.addCleanup(
            self.openstack,
            'floating ip unset --port ' + ip1,
        )

        json_output = json.loads(self.openstack(
            'floating ip show -f json ' +
            ip1
        ))

        self.assertEqual(
            port_id,
            json_output["port_id"],
        )
