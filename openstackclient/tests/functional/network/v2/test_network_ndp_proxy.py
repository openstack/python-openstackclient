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

from openstackclient.tests.functional.network.v2 import common


class L3NDPProxyTests(common.NetworkTests):

    def setUp(self):
        super().setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")
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

        json_output = json.loads(
            self.openstack(
                'address scope create -f json --ip-version 6 '
                '%(address_s_name)s' % {
                    'address_s_name': self.ADDR_SCOPE_NAME}))
        self.assertIsNotNone(json_output['id'])
        self.ADDRESS_SCOPE_ID = json_output['id']
        json_output = json.loads(
            self.openstack(
                'subnet pool create -f json %(subnet_p_name)s '
                '--address-scope %(address_scope)s '
                '--pool-prefix 2001:db8::/96 --default-prefix-length 112' % {
                    'subnet_p_name': self.SUBNET_P_NAME,
                    'address_scope': self.ADDRESS_SCOPE_ID}))
        self.assertIsNotNone(json_output['id'])
        self.SUBNET_POOL_ID = json_output['id']
        json_output = json.loads(
            self.openstack('network create -f json '
                           '--external ' + self.EXT_NET_NAME))
        self.assertIsNotNone(json_output['id'])
        self.EXT_NET_ID = json_output['id']
        json_output = json.loads(
            self.openstack(
                'subnet create -f json --ip-version 6 --subnet-pool '
                '%(subnet_pool)s --network %(net_id)s %(sub_name)s' % {
                    'subnet_pool': self.SUBNET_POOL_ID,
                    'net_id': self.EXT_NET_ID,
                    'sub_name': self.EXT_SUB_NAME}))
        self.assertIsNotNone(json_output['id'])
        self.EXT_SUB_ID = json_output['id']
        json_output = json.loads(
            self.openstack('router create -f json ' + self.ROT_NAME))
        self.assertIsNotNone(json_output['id'])
        self.ROT_ID = json_output['id']
        output = self.openstack(
            'router set %(router_id)s --external-gateway %(net_id)s' % {
                'router_id': self.ROT_ID,
                'net_id': self.EXT_NET_ID})
        self.assertEqual('', output)
        output = self.openstack('router set --enable-ndp-proxy ' + self.ROT_ID)
        self.assertEqual('', output)
        json_output = json.loads(
            self.openstack(
                'router show -f json -c enable_ndp_proxy ' + self.ROT_ID))
        self.assertTrue(json_output['enable_ndp_proxy'])
        json_output = json.loads(
            self.openstack('network create -f json ' + self.INT_NET_NAME))
        self.assertIsNotNone(json_output['id'])
        self.INT_NET_ID = json_output['id']
        json_output = json.loads(
            self.openstack(
                'subnet create -f json --ip-version 6 --subnet-pool '
                '%(subnet_pool)s --network %(net_id)s %(sub_name)s' % {
                    'subnet_pool': self.SUBNET_POOL_ID,
                    'net_id': self.INT_NET_ID,
                    'sub_name': self.INT_SUB_NAME}))
        self.assertIsNotNone(json_output['id'])
        self.INT_SUB_ID = json_output['id']
        json_output = json.loads(
            self.openstack(
                'port create -f json --network %(net_id)s '
                '%(port_name)s' % {
                    'net_id': self.INT_NET_ID,
                    'port_name': self.INT_PORT_NAME}))
        self.assertIsNotNone(json_output['id'])
        self.INT_PORT_ID = json_output['id']
        self.INT_PORT_ADDRESS = json_output['fixed_ips'][0]['ip_address']
        output = self.openstack(
            'router add subnet ' + self.ROT_ID + ' ' + self.INT_SUB_ID)
        self.assertEqual('', output)

    def tearDown(self):
        for ndp_proxy in self.created_ndp_proxies:
            output = self.openstack(
                'router ndp proxy delete ' + ndp_proxy['id'])
            self.assertEqual('', output)
        output = self.openstack('port delete ' + self.INT_PORT_ID)
        self.assertEqual('', output)
        output = self.openstack(
            'router set --disable-ndp-proxy ' + self.ROT_ID)
        self.assertEqual('', output)
        output = self.openstack(
            'router remove subnet ' + self.ROT_ID + ' ' + self.INT_SUB_ID)
        self.assertEqual('', output)
        output = self.openstack('subnet delete ' + self.INT_SUB_ID)
        self.assertEqual('', output)
        output = self.openstack('network delete ' + self.INT_NET_ID)
        self.assertEqual('', output)
        output = self.openstack(
            'router unset ' + self.ROT_ID + ' ' + '--external-gateway')
        self.assertEqual('', output)
        output = self.openstack('router delete ' + self.ROT_ID)
        self.assertEqual('', output)
        output = self.openstack('subnet delete ' + self.EXT_SUB_ID)
        self.assertEqual('', output)
        output = self.openstack('network delete ' + self.EXT_NET_ID)
        self.assertEqual('', output)
        output = self.openstack('subnet pool delete ' + self.SUBNET_POOL_ID)
        self.assertEqual('', output)
        output = self.openstack('address scope delete ' +
                                self.ADDRESS_SCOPE_ID)
        self.assertEqual('', output)
        super().tearDown()

    def _create_ndp_proxies(self, ndp_proxies):
        for ndp_proxy in ndp_proxies:
            output = json.loads(
                self.openstack(
                    'router ndp proxy create %(router)s --name %(name)s '
                    '--port %(port)s --ip-address %(address)s -f json' % {
                        'router': ndp_proxy['router_id'],
                        'name': ndp_proxy['name'],
                        'port': ndp_proxy['port_id'],
                        'address': ndp_proxy['address']}))
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
                'address': self.INT_PORT_ADDRESS
            }
        ]
        self._create_ndp_proxies(ndp_proxies)

    def test_ndp_proxy_list(self):
        ndp_proxies = {
            'name': self.getUniqueString(),
            'router_id': self.ROT_ID,
            'port_id': self.INT_PORT_ID,
            'address': self.INT_PORT_ADDRESS}
        self._create_ndp_proxies([ndp_proxies])
        ndp_proxy = json.loads(self.openstack(
            'router ndp proxy list -f json'))[0]
        self.assertEqual(ndp_proxies['name'], ndp_proxy['Name'])
        self.assertEqual(ndp_proxies['router_id'], ndp_proxy['Router ID'])
        self.assertEqual(ndp_proxies['address'], ndp_proxy['IP Address'])

    def test_ndp_proxy_set_and_show(self):
        ndp_proxies = {
            'name': self.getUniqueString(),
            'router_id': self.ROT_ID,
            'port_id': self.INT_PORT_ID,
            'address': self.INT_PORT_ADDRESS}
        description = 'balala'
        self._create_ndp_proxies([ndp_proxies])
        ndp_proxy_id = self.created_ndp_proxies[0]['id']
        output = self.openstack(
            'router ndp proxy set --description %s %s' % (
                description, ndp_proxy_id))
        self.assertEqual('', output)
        json_output = json.loads(
            self.openstack('router ndp proxy show -f json ' + ndp_proxy_id))
        self.assertEqual(ndp_proxies['name'], json_output['name'])
        self.assertEqual(ndp_proxies['router_id'], json_output['router_id'])
        self.assertEqual(ndp_proxies['port_id'], json_output['port_id'])
        self.assertEqual(ndp_proxies['address'], json_output['ip_address'])
        self.assertEqual(description, json_output['description'])
