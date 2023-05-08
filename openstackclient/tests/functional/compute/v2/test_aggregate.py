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

import uuid

from openstackclient.tests.functional import base


class AggregateTests(base.TestCase):
    """Functional tests for aggregate"""

    def test_aggregate_crud(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        self.addCleanup(
            self.openstack,
            'aggregate delete ' + name1,
            fail_ok=True,
        )
        cmd_output = self.openstack(
            'aggregate create ' + '--zone nova ' + '--property a=b ' + name1,
            parse_output=True,
        )
        self.assertEqual(name1, cmd_output['name'])
        self.assertEqual('nova', cmd_output['availability_zone'])
        self.assertIn('a', cmd_output['properties'])
        cmd_output = self.openstack(
            'aggregate show ' + name1,
            parse_output=True,
        )
        self.assertEqual(name1, cmd_output['name'])

        name2 = uuid.uuid4().hex
        self.addCleanup(
            self.openstack,
            'aggregate delete ' + name2,
            fail_ok=True,
        )
        cmd_output = self.openstack(
            'aggregate create ' + '--zone external ' + name2,
            parse_output=True,
        )
        self.assertEqual(name2, cmd_output['name'])
        self.assertEqual('external', cmd_output['availability_zone'])
        cmd_output = self.openstack(
            'aggregate show ' + name2,
            parse_output=True,
        )
        self.assertEqual(name2, cmd_output['name'])

        # Test aggregate set
        name3 = uuid.uuid4().hex
        self.addCleanup(
            self.openstack,
            'aggregate delete ' + name3,
            fail_ok=True,
        )
        raw_output = self.openstack(
            'aggregate set '
            + '--name '
            + name3
            + ' '
            + '--zone internal '
            + '--no-property '
            + '--property c=d '
            + name1
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'aggregate show ' + name3,
            parse_output=True,
        )
        self.assertEqual(name3, cmd_output['name'])
        self.assertEqual('internal', cmd_output['availability_zone'])
        self.assertIn('c', cmd_output['properties'])
        self.assertNotIn('a', cmd_output['properties'])

        # Test aggregate list
        cmd_output = self.openstack(
            'aggregate list',
            parse_output=True,
        )
        names = [x['Name'] for x in cmd_output]
        self.assertIn(name3, names)
        self.assertIn(name2, names)
        zones = [x['Availability Zone'] for x in cmd_output]
        self.assertIn('external', zones)
        self.assertIn('internal', zones)

        # Test aggregate list --long
        cmd_output = self.openstack(
            'aggregate list --long',
            parse_output=True,
        )
        names = [x['Name'] for x in cmd_output]
        self.assertIn(name3, names)
        self.assertIn(name2, names)
        zones = [x['Availability Zone'] for x in cmd_output]
        self.assertIn('external', zones)
        self.assertIn('internal', zones)
        properties = [x['Properties'] for x in cmd_output]
        self.assertNotIn({'a': 'b'}, properties)
        self.assertIn({'c': 'd'}, properties)

        # Test unset
        raw_output = self.openstack(
            'aggregate unset ' + '--property c ' + name3
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'aggregate show ' + name3,
            parse_output=True,
        )
        self.assertNotIn("c='d'", cmd_output['properties'])

        # test aggregate delete
        del_output = self.openstack('aggregate delete ' + name3 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_aggregate_add_and_remove_host(self):
        """Test aggregate add and remove host"""
        # Get a host
        cmd_output = self.openstack(
            'host list',
            parse_output=True,
        )
        host_name = cmd_output[0]['Host Name']

        # NOTE(dtroyer): Cells v1 is not operable with aggregates.  Hostnames
        #                are returned as rrr@host or ccc!rrr@host.
        if '@' in host_name:
            self.skipTest("Skip aggregates in a Nova cells v1 configuration")

        name = uuid.uuid4().hex
        self.addCleanup(self.openstack, 'aggregate delete ' + name)
        self.openstack('aggregate create ' + name)

        # Test add host
        cmd_output = self.openstack(
            'aggregate add host ' + name + ' ' + host_name,
            parse_output=True,
        )
        self.assertIn(host_name, cmd_output['hosts'])

        # Test remove host
        cmd_output = self.openstack(
            'aggregate remove host ' + name + ' ' + host_name,
            parse_output=True,
        )
        self.assertNotIn(host_name, cmd_output['hosts'])
