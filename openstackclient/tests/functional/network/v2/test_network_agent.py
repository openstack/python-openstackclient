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


class NetworkAgentTests(base.TestCase):
    """Functional tests for network agent. """
    IDs = None
    HEADERS = ['ID']
    FIELDS = ['id']

    @classmethod
    def test_network_agent_list(cls):
        opts = cls.get_opts(cls.HEADERS)
        raw_output = cls.openstack('network agent list' + opts)
        # get the list of network agent IDs.
        cls.IDs = raw_output.split('\n')

    def test_network_agent_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('network agent show ' + self.IDs[0] + opts)
        self.assertEqual(self.IDs[0] + "\n", raw_output)

    def test_network_agent_set(self):
        opts = self.get_opts(['admin_state_up'])
        self.openstack('network agent set --disable ' + self.IDs[0])
        raw_output = self.openstack('network agent show ' + self.IDs[0] + opts)
        self.assertEqual("DOWN\n", raw_output)
        self.openstack('network agent set --enable ' + self.IDs[0])
        raw_output = self.openstack('network agent show ' + self.IDs[0] + opts)
        self.assertEqual("UP\n", raw_output)


class NetworkAgentListTests(base.TestCase):
    """Functional test for network agent list --network. """

    def test_network_dhcp_agent_list(self):
        """Test network agent list"""

        name1 = uuid.uuid4().hex
        cmd_output1 = json.loads(self.openstack(
            'network create -f json ' +
            '--description aaaa ' +
            name1
        ))

        self.addCleanup(self.openstack, 'network delete ' + name1)

        # Get network ID
        network_id = cmd_output1['id']

        # Get DHCP Agent ID
        cmd_output2 = json.loads(self.openstack(
            'network agent list -f json --agent-type dhcp'
        ))
        agent_id = cmd_output2[0]['ID']

        # Add Agent to Network
        self.openstack(
            'network agent add network --dhcp '
            + agent_id + ' ' + network_id
        )

        # Test network agent list --network
        cmd_output3 = json.loads(self.openstack(
            'network agent list -f json --network ' + network_id
        ))

        # Cleanup
        # Remove Agent from Network
        self.openstack(
            'network agent remove network --dhcp '
            + agent_id + ' ' + network_id
        )

        # Assert
        col_name = [x["ID"] for x in cmd_output3]
        self.assertIn(
            agent_id, col_name
        )
