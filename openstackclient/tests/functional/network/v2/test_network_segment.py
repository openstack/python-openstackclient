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


class NetworkSegmentTests(base.TestCase):
    """Functional tests for network segment. """
    NETWORK_NAME = uuid.uuid4().hex
    PHYSICAL_NETWORK_NAME = uuid.uuid4().hex
    NETWORK_SEGMENT_ID = None
    NETWORK_ID = None
    NETWORK_SEGMENT_EXTENSION = None

    @classmethod
    def setUpClass(cls):
        # Create a network for the segment.
        opts = cls.get_opts(['id'])
        raw_output = cls.openstack('network create ' + cls.NETWORK_NAME + opts)
        cls.NETWORK_ID = raw_output.strip('\n')

        # NOTE(rtheis): The segment extension is not yet enabled by default.
        # Skip the tests if not enabled.
        extensions = cls.get_openstack_extention_names()
        if 'Segment' in extensions:
            cls.NETWORK_SEGMENT_EXTENSION = 'Segment'

        if cls.NETWORK_SEGMENT_EXTENSION:
            # Get the segment for the network.
            opts = cls.get_opts(['ID', 'Network'])
            raw_output = cls.openstack('network segment list '
                                       ' --network ' + cls.NETWORK_NAME +
                                       ' ' + opts)
            raw_output_row = raw_output.split('\n')[0]
            cls.NETWORK_SEGMENT_ID = raw_output_row.split(' ')[0]

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('network delete ' + cls.NETWORK_NAME)
        cls.assertOutput('', raw_output)

    def test_network_segment_create_delete(self):
        if self.NETWORK_SEGMENT_EXTENSION:
            opts = self.get_opts(['id'])
            raw_output = self.openstack(
                ' network segment create --network ' + self.NETWORK_ID +
                ' --network-type geneve ' +
                ' --segment 2055 test_segment ' + opts
            )
            network_segment_id = raw_output.strip('\n')
            raw_output = self.openstack('network segment delete ' +
                                        network_segment_id)
            self.assertOutput('', raw_output)
        else:
            self.skipTest('Segment extension disabled')

    def test_network_segment_list(self):
        if self.NETWORK_SEGMENT_EXTENSION:
            opts = self.get_opts(['ID'])
            raw_output = self.openstack('network segment list' + opts)
            self.assertIn(self.NETWORK_SEGMENT_ID, raw_output)
        else:
            self.skipTest('Segment extension disabled')

    def test_network_segment_set(self):
        if self.NETWORK_SEGMENT_EXTENSION:
            new_description = 'new_description'
            raw_output = self.openstack('network segment set ' +
                                        '--description ' + new_description +
                                        ' ' + self.NETWORK_SEGMENT_ID)
            self.assertOutput('', raw_output)
            opts = self.get_opts(['description'])
            raw_output = self.openstack('network segment show ' +
                                        self.NETWORK_SEGMENT_ID + opts)
            self.assertEqual(new_description + "\n", raw_output)
        else:
            self.skipTest('Segment extension disabled')

    def test_network_segment_show(self):
        if self.NETWORK_SEGMENT_EXTENSION:
            opts = self.get_opts(['network_id'])
            raw_output = self.openstack('network segment show ' +
                                        self.NETWORK_SEGMENT_ID + opts)
            self.assertEqual(self.NETWORK_ID + "\n", raw_output)
        else:
            self.skipTest('Segment extension disabled')
