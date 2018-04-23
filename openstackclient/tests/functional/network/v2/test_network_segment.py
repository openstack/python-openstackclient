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

from openstackclient.tests.functional.network.v2 import common


class NetworkSegmentTests(common.NetworkTests):
    """Functional tests for network segment"""

    @classmethod
    def setUpClass(cls):
        common.NetworkTests.setUpClass()
        if cls.haz_network:
            cls.NETWORK_NAME = uuid.uuid4().hex
            cls.PHYSICAL_NETWORK_NAME = uuid.uuid4().hex

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
            super(NetworkSegmentTests, cls).tearDownClass()

    def setUp(self):
        super(NetworkSegmentTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_network_segment_create_delete(self):
        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            ' network segment create -f json ' +
            '--network ' + self.NETWORK_ID + ' ' +
            '--network-type geneve ' +
            '--segment 2055 ' +
            name
        ))
        self.assertEqual(
            name,
            json_output["name"],
        )

        raw_output = self.openstack(
            'network segment delete ' + name,
        )
        self.assertOutput('', raw_output)

    def test_network_segment_list(self):
        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            ' network segment create -f json ' +
            '--network ' + self.NETWORK_ID + ' ' +
            '--network-type geneve ' +
            '--segment 2055 ' +
            name
        ))
        network_segment_id = json_output.get('id')
        network_segment_name = json_output.get('name')
        self.addCleanup(
            self.openstack,
            'network segment delete ' + network_segment_id
        )
        self.assertEqual(
            name,
            json_output["name"],
        )

        json_output = json.loads(self.openstack(
            'network segment list -f json'
        ))
        item_map = {
            item.get('ID'): item.get('Name') for item in json_output
        }
        self.assertIn(network_segment_id, item_map.keys())
        self.assertIn(network_segment_name, item_map.values())

    def test_network_segment_set_show(self):
        name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            ' network segment create -f json ' +
            '--network ' + self.NETWORK_ID + ' ' +
            '--network-type geneve ' +
            '--segment 2055 ' +
            name
        ))
        self.addCleanup(
            self.openstack,
            'network segment delete ' + name
        )

        extension_output = json.loads(self.openstack(
            "extension list -f json "
        ))
        ext_alias = [x["Alias"] for x in extension_output]
        if "standard-attr-segment" in ext_alias:
            self.assertEqual(
                '',
                json_output["description"],
            )
        else:
            self.assertIsNone(
                json_output["description"],
            )

        new_description = 'new_description'
        cmd_output = self.openstack(
            'network segment set ' +
            '--description ' + new_description + ' ' +
            name
        )
        self.assertOutput('', cmd_output)

        json_output = json.loads(self.openstack(
            'network segment show -f json ' +
            name
        ))
        self.assertEqual(
            new_description,
            json_output["description"],
        )
