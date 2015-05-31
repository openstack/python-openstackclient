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

import copy

from openstackclient.tests import fakes
from openstackclient.tests.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume


class TestVolume(volume_fakes.TestVolume):

    def setUp(self):
        super(TestVolume, self).setUp()

        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()


class TestVolumeShow(TestVolume):
    def setUp(self):
        super(TestVolumeShow, self).setUp()

        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True)
        # Get the command object to test
        self.cmd = volume.ShowVolume(self.app, None)

    def test_volume_show(self):
        arglist = [
            volume_fakes.volume_id
        ]
        verifylist = [
            ("volume", volume_fakes.volume_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volumes_mock.get.assert_called_with(volume_fakes.volume_id)

        self.assertEqual(volume_fakes.VOLUME_columns, columns)
        self.assertEqual(volume_fakes.VOLUME_data, data)


class TestVolumeDelete(TestVolume):
    def setUp(self):
        super(TestVolumeDelete, self).setUp()

        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True)
        self.volumes_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume.DeleteVolume(self.app, None)

    def test_volume_delete(self):
        arglist = [
            volume_fakes.volume_id
        ]
        verifylist = [
            ("volumes", [volume_fakes.volume_id])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.volumes_mock.delete.assert_called_with(volume_fakes.volume_id)
