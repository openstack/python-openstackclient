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


class ServerGroupTests(base.TestCase):
    """Functional tests for servergroup."""

    def test_server_group_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server group create ' + '--policy affinity ' + name1,
            parse_output=True,
        )
        self.assertEqual(name1, cmd_output['name'])
        self.assertEqual('affinity', cmd_output['policy'])

        cmd_output = self.openstack(
            'server group create ' + '--policy anti-affinity ' + name2,
            parse_output=True,
        )
        self.assertEqual(name2, cmd_output['name'])
        self.assertEqual('anti-affinity', cmd_output['policy'])

        del_output = self.openstack(
            'server group delete ' + name1 + ' ' + name2
        )
        self.assertOutput('', del_output)

    def test_server_group_show_and_list(self):
        """Test server group create, show, and list"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex

        # test server group show
        cmd_output = self.openstack(
            'server group create ' + '--policy affinity ' + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'server group delete ' + name1)
        cmd_output = self.openstack(
            'server group show ' + name1,
            parse_output=True,
        )
        self.assertEqual(name1, cmd_output['name'])
        self.assertEqual('affinity', cmd_output['policy'])

        cmd_output = self.openstack(
            'server group create ' + '--policy anti-affinity ' + name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'server group delete ' + name2)
        cmd_output = self.openstack(
            'server group show ' + name2,
            parse_output=True,
        )
        self.assertEqual(name2, cmd_output['name'])
        self.assertEqual('anti-affinity', cmd_output['policy'])

        # test server group list
        cmd_output = self.openstack(
            'server group list',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)
        policies = [x["Policy"] for x in cmd_output]
        self.assertIn('affinity', policies)
        self.assertIn('anti-affinity', policies)
