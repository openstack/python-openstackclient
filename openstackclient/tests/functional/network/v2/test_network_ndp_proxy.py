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

from openstackclient.tests.functional.network.v2 import common


class L3NDPProxyTests(common.NetworkTests):
    def setUp(self):
        super().setUp()

        if not self.is_extension_enabled('l3-ndp-proxy'):
            self.skipTest("No l3-ndp-proxy extension present")

        self.ROT_NAME = self.getUniqueString()
        self.EXT_NET_NAME = self.getUniqueString()
        self.EXT_SUB_NAME = self.getUniqueString()
        self.INT_NET_NAME = self.getUniqueString()
        self.INT_SUB_NAME = self.getUniqueString()
        self.INT_PORT_NAME = self.getUniqueString()
        self.ADDR_SCOPE_NAME = self.getUniqueString()
        self.SUBNET_P_NAME = self.getUniqueString()
        self.created_ndp_proxies = []

        json_output = self.openstack(
            f'address scope create --ip-version 6 {self.ADDR_SCOPE_NAME}',
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.ADDRESS_SCOPE_ID = json_output['id']
        json_output = self.openstack(
            f'subnet pool create {self.SUBNET_P_NAME} '
            f'--address-scope {self.ADDRESS_SCOPE_ID} '
            '--pool-prefix 2001:db8::/96 --default-prefix-length 112',
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.SUBNET_POOL_ID = json_output['id']
        json_output = self.openstack(
            'network create --external ' + self.EXT_NET_NAME,
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.EXT_NET_ID = json_output['id']
        json_output = self.openstack(
            'subnet create --ip-version 6 --subnet-pool '
            f'{self.SUBNET_POOL_ID} --network {self.EXT_NET_ID} {self.EXT_SUB_NAME}',
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.EXT_SUB_ID = json_output['id']
        json_output = self.openstack(
            'router create ' + self.ROT_NAME,
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.ROT_ID = json_output['id']
        output = self.openstack(
            f'router set {self.ROT_ID} --external-gateway {self.EXT_NET_ID}'
        )
        self.assertEqual('', output)
        output = self.openstack('router set --enable-ndp-proxy ' + self.ROT_ID)
        self.assertEqual('', output)
        json_output = self.openstack(
            'router show -c enable_ndp_proxy ' + self.ROT_ID,
            parse_output=True,
        )
        self.assertTrue(json_output['enable_ndp_proxy'])
        json_output = self.openstack(
            'network create ' + self.INT_NET_NAME,
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.INT_NET_ID = json_output['id']
        json_output = self.openstack(
            'subnet create --ip-version 6 --subnet-pool '
            f'{self.SUBNET_POOL_ID} --network {self.INT_NET_ID} {self.INT_SUB_NAME}',
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.INT_SUB_ID = json_output['id']
        json_output = self.openstack(
            f'port create --network {self.INT_NET_ID} {self.INT_PORT_NAME}',
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        self.INT_PORT_ID = json_output['id']
        self.INT_PORT_ADDRESS = json_output['fixed_ips'][0]['ip_address']
        output = self.openstack(
            'router add subnet ' + self.ROT_ID + ' ' + self.INT_SUB_ID
        )
        self.assertEqual('', output)

    def tearDown(self):
        for ndp_proxy in self.created_ndp_proxies:
            output = self.openstack(
                'router ndp proxy delete ' + ndp_proxy['id']
            )
            self.assertEqual('', output)
        output = self.openstack('port delete ' + self.INT_PORT_ID)
        self.assertEqual('', output)
        output = self.openstack(
            'router set --disable-ndp-proxy ' + self.ROT_ID
        )
        self.assertEqual('', output)
        output = self.openstack(
            'router remove subnet ' + self.ROT_ID + ' ' + self.INT_SUB_ID
        )
        self.assertEqual('', output)
        output = self.openstack('subnet delete ' + self.INT_SUB_ID)
        self.assertEqual('', output)
        output = self.openstack('network delete ' + self.INT_NET_ID)
        self.assertEqual('', output)
        output = self.openstack(
            'router unset ' + self.ROT_ID + ' ' + '--external-gateway'
        )
        self.assertEqual('', output)
        output = self.openstack('router delete ' + self.ROT_ID)
        self.assertEqual('', output)
        output = self.openstack('subnet delete ' + self.EXT_SUB_ID)
        self.assertEqual('', output)
        output = self.openstack('network delete ' + self.EXT_NET_ID)
        self.assertEqual('', output)
        output = self.openstack('subnet pool delete ' + self.SUBNET_POOL_ID)
        self.assertEqual('', output)
        output = self.openstack(
            'address scope delete ' + self.ADDRESS_SCOPE_ID
        )
        self.assertEqual('', output)
        super().tearDown()

    def _create_ndp_proxies(self, ndp_proxies):
        for ndp_proxy in ndp_proxies:
            output = self.openstack(
                'router ndp proxy create {router} --name {name} '
                '--port {port} --ip-address {address}'.format(
                    router=ndp_proxy['router_id'],
                    name=ndp_proxy['name'],
                    port=ndp_proxy['port_id'],
                    address=ndp_proxy['address'],
                ),
                parse_output=True,
            )
            self.assertEqual(ndp_proxy['router_id'], output['router_id'])
            self.assertEqual(ndp_proxy['port_id'], output['port_id'])
            self.assertEqual(ndp_proxy['address'], output['ip_address'])
            self.created_ndp_proxies.append(output)

    def test_create_ndp_proxy(self):
        ndp_proxies = [
            {
                'name': self.getUniqueString(),
                'router_id': self.ROT_ID,
                'port_id': self.INT_PORT_ID,
                'address': self.INT_PORT_ADDRESS,
            }
        ]
        self._create_ndp_proxies(ndp_proxies)

    def test_ndp_proxy_list(self):
        ndp_proxies = {
            'name': self.getUniqueString(),
            'router_id': self.ROT_ID,
            'port_id': self.INT_PORT_ID,
            'address': self.INT_PORT_ADDRESS,
        }
        self._create_ndp_proxies([ndp_proxies])
        ndp_proxy = self.openstack(
            'router ndp proxy list',
            parse_output=True,
        )[0]
        self.assertEqual(ndp_proxies['name'], ndp_proxy['Name'])
        self.assertEqual(ndp_proxies['router_id'], ndp_proxy['Router ID'])
        self.assertEqual(ndp_proxies['address'], ndp_proxy['IP Address'])

    def test_ndp_proxy_set_and_show(self):
        ndp_proxies = {
            'name': self.getUniqueString(),
            'router_id': self.ROT_ID,
            'port_id': self.INT_PORT_ID,
            'address': self.INT_PORT_ADDRESS,
        }
        description = 'balala'
        self._create_ndp_proxies([ndp_proxies])
        ndp_proxy_id = self.created_ndp_proxies[0]['id']
        output = self.openstack(
            f'router ndp proxy set --description {description} {ndp_proxy_id}'
        )
        self.assertEqual('', output)
        json_output = self.openstack(
            'router ndp proxy show ' + ndp_proxy_id,
            parse_output=True,
        )
        self.assertEqual(ndp_proxies['name'], json_output['name'])
        self.assertEqual(ndp_proxies['router_id'], json_output['router_id'])
        self.assertEqual(ndp_proxies['port_id'], json_output['port_id'])
        self.assertEqual(ndp_proxies['address'], json_output['ip_address'])
        self.assertEqual(description, json_output['description'])
