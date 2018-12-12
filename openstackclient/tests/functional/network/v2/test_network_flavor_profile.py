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


class NetworkFlavorProfileTests(common.NetworkTests):
    """Functional tests for network flavor profile"""

    DESCRIPTION = 'fakedescription'
    METAINFO = 'Extrainfo'

    def setUp(self):
        super(NetworkFlavorProfileTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_network_flavor_profile_create(self):
        json_output = json.loads(self.openstack(
            'network flavor profile create -f json ' +
            '--description ' + self.DESCRIPTION + ' ' +
            '--enable --metainfo ' + self.METAINFO
        ))
        ID = json_output.get('id')
        self.assertIsNotNone(ID)
        self.assertTrue(json_output.get('enabled'))
        self.assertEqual(
            'fakedescription',
            json_output.get('description'),
        )
        self.assertEqual(
            'Extrainfo',
            json_output.get('meta_info'),
        )

        # Clean up
        raw_output = self.openstack('network flavor profile delete ' + ID)
        self.assertOutput('', raw_output)

    def test_network_flavor_profile_list(self):
        json_output = json.loads(self.openstack(
            'network flavor profile create -f json ' +
            '--description ' + self.DESCRIPTION + ' ' +
            '--enable ' +
            '--metainfo ' + self.METAINFO
        ))
        ID1 = json_output.get('id')
        self.assertIsNotNone(ID1)
        self.assertTrue(json_output.get('enabled'))
        self.assertEqual(
            'fakedescription',
            json_output.get('description'),
        )
        self.assertEqual(
            'Extrainfo',
            json_output.get('meta_info'),
        )

        json_output = json.loads(self.openstack(
            'network flavor profile create -f json ' +
            '--description ' + self.DESCRIPTION + ' ' +
            '--disable ' +
            '--metainfo ' + self.METAINFO
        ))
        ID2 = json_output.get('id')
        self.assertIsNotNone(ID2)
        self.assertFalse(json_output.get('enabled'))
        self.assertEqual(
            'fakedescription',
            json_output.get('description'),
        )
        self.assertEqual(
            'Extrainfo',
            json_output.get('meta_info'),
        )

        # Test list
        json_output = json.loads(self.openstack(
            'network flavor profile list -f json'
        ))
        self.assertIsNotNone(json_output)

        id_list = [item.get('ID') for item in json_output]
        self.assertIn(ID1, id_list)
        self.assertIn(ID2, id_list)

        # Clean up
        raw_output = self.openstack(
            'network flavor profile delete ' + ID1 + ' ' + ID2
        )
        self.assertOutput('', raw_output)

    def test_network_flavor_profile_set(self):
        json_output_1 = json.loads(self.openstack(
            'network flavor profile create -f json ' +
            '--description ' + self.DESCRIPTION + ' ' +
            '--enable ' +
            '--metainfo ' + self.METAINFO
        ))
        ID = json_output_1.get('id')
        self.assertIsNotNone(ID)
        self.assertTrue(json_output_1.get('enabled'))
        self.assertEqual(
            'fakedescription',
            json_output_1.get('description'),
        )
        self.assertEqual(
            'Extrainfo',
            json_output_1.get('meta_info'),
        )

        self.openstack('network flavor profile set --disable ' + ID)

        json_output = json.loads(self.openstack(
            'network flavor profile show -f json ' + ID
        ))
        self.assertFalse(json_output.get('enabled'))
        self.assertEqual(
            'fakedescription',
            json_output.get('description'),
        )
        self.assertEqual(
            'Extrainfo',
            json_output.get('meta_info'),
        )

        # Clean up
        raw_output = self.openstack('network flavor profile delete ' + ID)
        self.assertOutput('', raw_output)

    def test_network_flavor_profile_show(self):
        json_output_1 = json.loads(self.openstack(
            'network flavor profile create -f json ' +
            '--description ' + self.DESCRIPTION + ' ' +
            '--enable ' +
            '--metainfo ' + self.METAINFO
        ))
        ID = json_output_1.get('id')
        self.assertIsNotNone(ID)
        json_output = json.loads(self.openstack(
            'network flavor profile show -f json ' + ID
        ))
        self.assertEqual(
            ID,
            json_output["id"],
        )
        self.assertTrue(json_output["enabled"])
        self.assertEqual(
            'fakedescription',
            json_output["description"],
        )
        self.assertEqual(
            'Extrainfo',
            json_output["meta_info"],
        )

        # Clean up
        raw_output = self.openstack('network flavor profile delete ' + ID)
        self.assertOutput('', raw_output)
