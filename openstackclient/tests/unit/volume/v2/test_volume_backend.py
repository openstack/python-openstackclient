#
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

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_backend


class TestShowVolumeCapability(volume_fakes.TestVolume):
    """Test backend capability functionality."""

    # The capability to be listed
    capability = volume_fakes.FakeCapability.create_one_capability()

    def setUp(self):
        super(TestShowVolumeCapability, self).setUp()

        # Get a shortcut to the capability Mock
        self.capability_mock = self.app.client_manager.volume.capabilities
        self.capability_mock.get.return_value = self.capability

        # Get the command object to test
        self.cmd = volume_backend.ShowCapability(self.app, None)

    def test_capability_show(self):
        arglist = [
            'fake',
        ]
        verifylist = [
            ('host', 'fake'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Title',
            'Key',
            'Type',
            'Description',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        capabilities = [
            'Compression',
            'Replication',
            'QoS',
            'Thin Provisioning',
        ]

        # confirming if all expected values are present in the result.
        for cap in data:
            self.assertTrue(cap[0] in capabilities)

        # checking if proper call was made to get capabilities
        self.capability_mock.get.assert_called_with(
            'fake',
        )
