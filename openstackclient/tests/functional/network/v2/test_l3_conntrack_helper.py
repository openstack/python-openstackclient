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


class L3ConntrackHelperTests(common.NetworkTests):

    def setUp(self):
        super(L3ConntrackHelperTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")
        if not self.is_extension_enabled('l3-conntrack-helper'):
            self.skipTest("No l3-conntrack-helper extension present")
        if not self.is_extension_enabled('expose-l3-conntrack-helper'):
            self.skipTest("No expose-l3-conntrack-helper extension present")

    def _create_router(self):
        router_name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'router create -f json ' + router_name
        ))
        self.assertIsNotNone(json_output['id'])
        router_id = json_output['id']
        self.addCleanup(self.openstack, 'router delete ' + router_id)
        return router_id

    def _create_helpers(self, router_id, helpers):
        created_helpers = []
        for helper in helpers:
            output = json.loads(self.openstack(
                'network l3 conntrack helper create %(router)s '
                '--helper %(helper)s --protocol %(protocol)s --port %(port)s '
                '-f json' % {'router': router_id,
                             'helper': helper['helper'],
                             'protocol': helper['protocol'],
                             'port': helper['port']}))
            self.assertEqual(helper['helper'], output['helper'])
            self.assertEqual(helper['protocol'], output['protocol'])
            self.assertEqual(helper['port'], output['port'])
            created_helpers.append(output)
        return created_helpers

    def test_l3_conntrack_helper_create_and_delete(self):
        """Test create, delete multiple"""

        helpers = [
            {
                'helper': 'tftp',
                'protocol': 'udp',
                'port': 69
            }, {
                'helper': 'ftp',
                'protocol': 'tcp',
                'port': 21
            }
        ]
        router_id = self._create_router()
        created_helpers = self._create_helpers(router_id, helpers)
        ct_ids = " ".join([ct['id'] for ct in created_helpers])

        raw_output = self.openstack(
            '--debug network l3 conntrack helper delete %(router)s '
            '%(ct_ids)s' % {
                'router': router_id, 'ct_ids': ct_ids})
        self.assertOutput('', raw_output)

    def test_l3_conntrack_helper_list(self):
        helpers = [
            {
                'helper': 'tftp',
                'protocol': 'udp',
                'port': 69
            }, {
                'helper': 'ftp',
                'protocol': 'tcp',
                'port': 21
            }
        ]
        expected_helpers = [
            {
                'Helper': 'tftp',
                'Protocol': 'udp',
                'Port': 69
            }, {
                'Helper': 'ftp',
                'Protocol': 'tcp',
                'Port': 21
            }
        ]
        router_id = self._create_router()
        self._create_helpers(router_id, helpers)
        output = json.loads(self.openstack(
            'network l3 conntrack helper list %s -f json ' % router_id
        ))
        for ct in output:
            self.assertEqual(router_id, ct.pop('Router ID'))
            ct.pop("ID")
            self.assertIn(ct, expected_helpers)

    def test_l3_conntrack_helper_set_and_show(self):
        helper = {
            'helper': 'tftp',
            'protocol': 'udp',
            'port': 69}
        router_id = self._create_router()
        created_helper = self._create_helpers(router_id, [helper])[0]
        output = json.loads(self.openstack(
            'network l3 conntrack helper show %(router_id)s %(ct_id)s '
            '-f json' % {
                'router_id': router_id, 'ct_id': created_helper['id']}))
        self.assertEqual(helper['helper'], output['helper'])
        self.assertEqual(helper['protocol'], output['protocol'])
        self.assertEqual(helper['port'], output['port'])

        raw_output = self.openstack(
            'network l3 conntrack helper set %(router_id)s %(ct_id)s '
            '--port %(port)s ' % {
                'router_id': router_id,
                'ct_id': created_helper['id'],
                'port': helper['port'] + 1})
        self.assertOutput('', raw_output)

        output = json.loads(self.openstack(
            'network l3 conntrack helper show %(router_id)s %(ct_id)s '
            '-f json' % {
                'router_id': router_id, 'ct_id': created_helper['id']}))
        self.assertEqual(helper['port'] + 1, output['port'])
        self.assertEqual(helper['helper'], output['helper'])
        self.assertEqual(helper['protocol'], output['protocol'])
