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

import uuid

from openstackclient.tests.functional.network.v2 import common


class L3ConntrackHelperTests(common.NetworkTests):
    def setUp(self):
        super().setUp()

        if not self.is_extension_enabled('l3-conntrack-helper'):
            self.skipTest("No l3-conntrack-helper extension present")

        if not self.is_extension_enabled('expose-l3-conntrack-helper'):
            self.skipTest("No expose-l3-conntrack-helper extension present")

    def _create_router(self):
        router_name = uuid.uuid4().hex
        json_output = self.openstack(
            'router create ' + router_name,
            parse_output=True,
        )
        self.assertIsNotNone(json_output['id'])
        router_id = json_output['id']
        self.addCleanup(self.openstack, 'router delete ' + router_id)
        return router_id

    def _create_helpers(self, router_id, helpers):
        created_helpers = []
        for helper in helpers:
            output = self.openstack(
                'network l3 conntrack helper create {router} '
                '--helper {helper} --protocol {protocol} '
                '--port {port} '.format(
                    router=router_id,
                    helper=helper['helper'],
                    protocol=helper['protocol'],
                    port=helper['port'],
                ),
                parse_output=True,
            )
            self.assertEqual(helper['helper'], output['helper'])
            self.assertEqual(helper['protocol'], output['protocol'])
            self.assertEqual(helper['port'], output['port'])
            created_helpers.append(output)
        return created_helpers

    def test_l3_conntrack_helper_create_and_delete(self):
        """Test create, delete multiple"""

        helpers = [
            {'helper': 'tftp', 'protocol': 'udp', 'port': 69},
            {'helper': 'ftp', 'protocol': 'tcp', 'port': 21},
        ]
        router_id = self._create_router()
        created_helpers = self._create_helpers(router_id, helpers)
        ct_ids = " ".join([ct['id'] for ct in created_helpers])

        raw_output = self.openstack(
            f'--debug network l3 conntrack helper delete {router_id} {ct_ids}'
        )
        self.assertOutput('', raw_output)

    def test_l3_conntrack_helper_list(self):
        helpers = [
            {'helper': 'tftp', 'protocol': 'udp', 'port': 69},
            {'helper': 'ftp', 'protocol': 'tcp', 'port': 21},
        ]
        expected_helpers = [
            {'Helper': 'tftp', 'Protocol': 'udp', 'Port': 69},
            {'Helper': 'ftp', 'Protocol': 'tcp', 'Port': 21},
        ]
        router_id = self._create_router()
        self._create_helpers(router_id, helpers)
        output = self.openstack(
            f'network l3 conntrack helper list {router_id} ',
            parse_output=True,
        )
        for ct in output:
            self.assertEqual(router_id, ct.pop('Router ID'))
            ct.pop("ID")
            self.assertIn(ct, expected_helpers)

    def test_l3_conntrack_helper_set_and_show(self):
        helper = 'tftp'
        proto = 'udp'
        port = 69
        router_id = self._create_router()
        created_helper = self._create_helpers(
            router_id,
            [{'helper': helper, 'protocol': proto, 'port': port}],
        )[0]
        output = self.openstack(
            'network l3 conntrack helper show {router_id} {ct_id} '
            '-f json'.format(
                router_id=router_id,
                ct_id=created_helper['id'],
            ),
            parse_output=True,
        )
        self.assertEqual(port, output['port'])
        self.assertEqual(helper, output['helper'])
        self.assertEqual(proto, output['protocol'])

        raw_output = self.openstack(
            'network l3 conntrack helper set {router_id} {ct_id} '
            '--port {port} '.format(
                router_id=router_id,
                ct_id=created_helper['id'],
                port=port + 1,
            )
        )
        self.assertOutput('', raw_output)

        output = self.openstack(
            'network l3 conntrack helper show {router_id} {ct_id} '
            '-f json'.format(
                router_id=router_id,
                ct_id=created_helper['id'],
            ),
            parse_output=True,
        )
        self.assertEqual(port + 1, output['port'])
        self.assertEqual(helper, output['helper'])
        self.assertEqual(proto, output['protocol'])
