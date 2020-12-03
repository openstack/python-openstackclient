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

from novaclient import api_versions

from openstackclient.compute.v2 import server_volume
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestServerVolume(compute_fakes.TestComputev2):

    def setUp(self):
        super().setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()

        # Get a shortcut to the compute client VolumeManager mock
        self.servers_volumes_mock = self.app.client_manager.compute.volumes
        self.servers_volumes_mock.reset_mock()


class TestServerVolumeList(TestServerVolume):

    def setUp(self):
        super().setUp()

        self.server = compute_fakes.FakeServer.create_one_server()
        self.volume_attachments = (
            compute_fakes.FakeVolumeAttachment.create_volume_attachments())

        self.servers_mock.get.return_value = self.server
        self.servers_volumes_mock.get_server_volumes.return_value = (
            self.volume_attachments)

        # Get the command object to test
        self.cmd = server_volume.ListServerVolume(self.app, None)

    def test_server_volume_list(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.1')

        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(('ID', 'Device', 'Server ID', 'Volume ID'), columns)
        self.assertEqual(
            (
                (
                    self.volume_attachments[0].id,
                    self.volume_attachments[0].device,
                    self.volume_attachments[0].serverId,
                    self.volume_attachments[0].volumeId,
                ),
                (
                    self.volume_attachments[1].id,
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].serverId,
                    self.volume_attachments[1].volumeId,
                ),
            ),
            tuple(data),
        )
        self.servers_volumes_mock.get_server_volumes.assert_called_once_with(
            self.server.id)

    def test_server_volume_list_with_tags(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.70')

        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(
            ('ID', 'Device', 'Server ID', 'Volume ID', 'Tag',), columns,
        )
        self.assertEqual(
            (
                (
                    self.volume_attachments[0].id,
                    self.volume_attachments[0].device,
                    self.volume_attachments[0].serverId,
                    self.volume_attachments[0].volumeId,
                    self.volume_attachments[0].tag,
                ),
                (
                    self.volume_attachments[1].id,
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].serverId,
                    self.volume_attachments[1].volumeId,
                    self.volume_attachments[1].tag,
                ),
            ),
            tuple(data),
        )
        self.servers_volumes_mock.get_server_volumes.assert_called_once_with(
            self.server.id)

    def test_server_volume_list_with_delete_on_attachment(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.79')

        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(
            (
                'ID', 'Device', 'Server ID', 'Volume ID', 'Tag',
                'Delete On Termination?',
            ),
            columns,
        )
        self.assertEqual(
            (
                (
                    self.volume_attachments[0].id,
                    self.volume_attachments[0].device,
                    self.volume_attachments[0].serverId,
                    self.volume_attachments[0].volumeId,
                    self.volume_attachments[0].tag,
                    self.volume_attachments[0].delete_on_termination,
                ),
                (
                    self.volume_attachments[1].id,
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].serverId,
                    self.volume_attachments[1].volumeId,
                    self.volume_attachments[1].tag,
                    self.volume_attachments[1].delete_on_termination,
                ),
            ),
            tuple(data),
        )
        self.servers_volumes_mock.get_server_volumes.assert_called_once_with(
            self.server.id)
