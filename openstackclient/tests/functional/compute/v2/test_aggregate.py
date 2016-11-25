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

from openstackclient.tests.functional import base


class AggregateTests(base.TestCase):
    """Functional tests for aggregate."""

    def test_aggregate_create_and_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'aggregate create -f json ' +
            '--zone nova ' +
            name1))
        self.assertEqual(
            name1,
            cmd_output['name']
        )
        self.assertEqual(
            'nova',
            cmd_output['availability_zone']
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'aggregate create -f json ' +
            '--zone nova ' +
            name2))
        self.assertEqual(
            name2,
            cmd_output['name']
        )
        self.assertEqual(
            'nova',
            cmd_output['availability_zone']
        )

        del_output = self.openstack(
            'aggregate delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_aggregate_list(self):
        """Test aggregate list"""
        name1 = uuid.uuid4().hex
        self.openstack(
            'aggregate create ' +
            '--zone nova ' +
            '--property a=b ' +
            name1)
        self.addCleanup(self.openstack, 'aggregate delete ' + name1)

        name2 = uuid.uuid4().hex
        self.openstack(
            'aggregate create ' +
            '--zone internal ' +
            '--property c=d ' +
            name2)
        self.addCleanup(self.openstack, 'aggregate delete ' + name2)

        cmd_output = json.loads(self.openstack(
            'aggregate list -f json'))
        names = [x['Name'] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)
        zones = [x['Availability Zone'] for x in cmd_output]
        self.assertIn('nova', zones)
        self.assertIn('internal', zones)

        # Test aggregate list --long
        cmd_output = json.loads(self.openstack(
            'aggregate list --long -f json'))
        names = [x['Name'] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)
        zones = [x['Availability Zone'] for x in cmd_output]
        self.assertIn('nova', zones)
        self.assertIn('internal', zones)
        properties = [x['Properties'] for x in cmd_output]
        self.assertIn({'a': 'b'}, properties)
        self.assertIn({'c': 'd'}, properties)

    def test_aggregate_set_and_unset(self):
        """Test aggregate set, show and unset"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        self.openstack(
            'aggregate create ' +
            '--zone nova ' +
            '--property a=b ' +
            name1)
        self.addCleanup(self.openstack, 'aggregate delete ' + name2)

        raw_output = self.openstack(
            'aggregate set --name ' +
            name2 +
            ' --zone internal ' +
            '--no-property ' +
            '--property c=d ' +
            name1
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'aggregate show -f json ' + name2))
        self.assertEqual(
            name2,
            cmd_output['name']
        )
        self.assertEqual(
            'internal',
            cmd_output['availability_zone']
        )
        self.assertIn(
            "c='d'",
            cmd_output['properties']
        )
        self.assertNotIn(
            "a='b'",
            cmd_output['properties']
        )

        # Test unset
        raw_output = self.openstack(
            'aggregate unset --property c ' +
            name2
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'aggregate show -f json ' + name2))
        self.assertNotIn(
            "c='d'",
            cmd_output['properties']
        )

    def test_aggregate_add_and_remove_host(self):
        """Test aggregate add and remove host"""
        name = uuid.uuid4().hex
        self.openstack(
            'aggregate create ' + name)
        self.addCleanup(self.openstack, 'aggregate delete ' + name)

        # Get a host
        cmd_output = json.loads(self.openstack(
            'host list -f json'))
        host_name = cmd_output[0]['Host Name']

        # Test add host
        cmd_output = json.loads(self.openstack(
            'aggregate add host -f json ' +
            name + ' ' +
            host_name
        ))
        self.assertIn(
            host_name,
            cmd_output['hosts']
        )

        # Test remove host
        cmd_output = json.loads(self.openstack(
            'aggregate remove host -f json ' +
            name + ' ' +
            host_name
        ))
        self.assertNotIn(
            host_name,
            cmd_output['hosts']
        )
