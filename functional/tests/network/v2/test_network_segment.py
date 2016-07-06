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

import testtools
import uuid

from functional.common import test


# NOTE(rtheis): Routed networks is still a WIP and not enabled by default.
@testtools.skip("bp/routed-networks")
class NetworkSegmentTests(test.TestCase):
    """Functional tests for network segment. """
    NETWORK_NAME = uuid.uuid4().hex
    PHYSICAL_NETWORK_NAME = uuid.uuid4().hex
    NETWORK_SEGMENT_ID = None
    NETWORK_ID = None

    @classmethod
    def setUpClass(cls):
        # Create a network for the segment.
        opts = cls.get_opts(['id'])
        raw_output = cls.openstack('network create ' + cls.NETWORK_NAME + opts)
        cls.NETWORK_ID = raw_output.strip('\n')

        # Get the segment for the network.
        opts = cls.get_opts(['ID', 'Network'])
        raw_output = cls.openstack('--os-beta-command '
                                   'network segment list '
                                   ' --network ' + cls.NETWORK_NAME +
                                   ' ' + opts)
        raw_output_row = raw_output.split('\n')[0]
        cls.NETWORK_SEGMENT_ID = raw_output_row.split(' ')[0]

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('network delete ' + cls.NETWORK_NAME)
        cls.assertOutput('', raw_output)

    def test_network_segment_list(self):
        opts = self.get_opts(['ID'])
        raw_output = self.openstack('--os-beta-command '
                                    'network segment list' + opts)
        self.assertIn(self.NETWORK_SEGMENT_ID, raw_output)

    def test_network_segment_show(self):
        opts = self.get_opts(['network_id'])
        raw_output = self.openstack('--os-beta-command '
                                    'network segment show ' +
                                    self.NETWORK_SEGMENT_ID + opts)
        self.assertEqual(self.NETWORK_ID + "\n", raw_output)
