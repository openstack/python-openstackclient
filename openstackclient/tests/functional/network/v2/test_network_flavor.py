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


class NetworkFlavorTests(common.NetworkTests):
    """Functional tests for network flavor"""

    def setUp(self):
        super(NetworkFlavorTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_network_flavor_add_remove_profile(self):
        """Test add and remove network flavor to/from profile"""
        # Create Flavor
        name1 = uuid.uuid4().hex
        cmd_output1 = json.loads(self.openstack(
            'network flavor create -f json --description testdescription '
            '--enable  --service-type L3_ROUTER_NAT ' + name1,
        ))
        flavor_id = cmd_output1.get('id')

        # Create Service Flavor
        cmd_output2 = json.loads(self.openstack(
            'network flavor profile create -f json --description '
            'fakedescription --enable --metainfo Extrainfo'
        ))
        service_profile_id = cmd_output2.get('id')

        self.addCleanup(self.openstack, 'network flavor delete %s' %
                        flavor_id)
        self.addCleanup(self.openstack, 'network flavor profile delete %s' %
                        service_profile_id)
        # Add flavor to service profile
        self.openstack(
            'network flavor add profile ' +
            flavor_id + ' ' + service_profile_id
        )

        cmd_output4 = json.loads(self.openstack(
            'network flavor show -f json ' + flavor_id
        ))
        service_profile_ids1 = cmd_output4.get('service_profile_ids')

        # Assert
        self.assertIn(service_profile_id, service_profile_ids1)

        # Cleanup
        # Remove flavor from service profile
        self.openstack(
            'network flavor remove profile ' +
            flavor_id + ' ' + service_profile_id
        )

        cmd_output6 = json.loads(self.openstack(
            'network flavor show -f json ' + flavor_id
        ))
        service_profile_ids2 = cmd_output6.get('service_profile_ids')

        # Assert
        self.assertNotIn(service_profile_id, service_profile_ids2)

    def test_network_flavor_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network flavor create -f json --description testdescription '
            '--enable  --service-type L3_ROUTER_NAT ' + name1,
        ))
        self.assertEqual(
            name1,
            cmd_output['name'],
        )
        self.assertTrue(cmd_output['enabled'])
        self.assertEqual(
            'testdescription',
            cmd_output['description'],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network flavor create -f json --description testdescription1 '
            '--disable --service-type  L3_ROUTER_NAT ' + name2,
        ))
        self.assertEqual(
            name2,
            cmd_output['name'],
        )
        self.assertFalse(cmd_output['enabled'])
        self.assertEqual(
            'testdescription1',
            cmd_output['description'],
        )
        raw_output = self.openstack(
            'network flavor delete ' + name1 + " " + name2)
        self.assertOutput('', raw_output)

    def test_network_flavor_list(self):
        """Test create defaults, list filters, delete"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network flavor create -f json --description testdescription '
            '--enable  --service-type  L3_ROUTER_NAT ' + name1,
        ))
        self.addCleanup(self.openstack, "network flavor delete " + name1)
        self.assertEqual(
            name1,
            cmd_output['name'],
        )
        self.assertEqual(
            True,
            cmd_output['enabled'],
        )
        self.assertEqual(
            'testdescription',
            cmd_output['description'],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network flavor create -f json --description testdescription1 '
            '--disable --service-type  L3_ROUTER_NAT ' + name2,
        ))
        self.assertEqual(
            name2,
            cmd_output['name'],
        )
        self.assertEqual(
            False,
            cmd_output['enabled'],
        )
        self.assertEqual(
            'testdescription1',
            cmd_output['description'],
        )
        self.addCleanup(self.openstack, "network flavor delete " + name2)

        # Test list
        cmd_output = json.loads(self.openstack(
            'network flavor list -f json ',))
        self.assertIsNotNone(cmd_output)

        name_list = [item.get('Name') for item in cmd_output]
        self.assertIn(name1, name_list)
        self.assertIn(name2, name_list)

    def test_network_flavor_set(self):
        """Tests create options, set, show, delete"""
        name = uuid.uuid4().hex
        newname = name + "_"
        cmd_output = json.loads(self.openstack(
            'network flavor create -f json --description testdescription '
            '--disable --service-type  L3_ROUTER_NAT ' + name,
        ))
        self.addCleanup(self.openstack, "network flavor delete " + newname)
        self.assertEqual(
            name,
            cmd_output['name'],
        )
        self.assertEqual(
            False,
            cmd_output['enabled'],
        )
        self.assertEqual(
            'testdescription',
            cmd_output['description'],
        )

        raw_output = self.openstack(
            'network flavor set --name ' + newname + ' --disable ' + name
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'network flavor show -f json ' + newname,))
        self.assertEqual(
            newname,
            cmd_output['name'],
        )
        self.assertEqual(
            False,
            cmd_output['enabled'],
        )
        self.assertEqual(
            'testdescription',
            cmd_output['description'],
        )

    def test_network_flavor_show(self):
        """Test show network flavor"""
        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'network flavor create -f json --description testdescription '
            '--disable --service-type  L3_ROUTER_NAT ' + name,
        ))
        self.addCleanup(self.openstack, "network flavor delete " + name)
        cmd_output = json.loads(self.openstack(
            'network flavor show -f json ' + name,))
        self.assertEqual(
            name,
            cmd_output['name'],
        )
        self.assertEqual(
            False,
            cmd_output['enabled'],
        )
        self.assertEqual(
            'testdescription',
            cmd_output['description'],
        )
