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

from openstack.block_storage.v3 import volume as _volume
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import volume_attachment as _volume_attachment
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.compute.v2 import server_volume
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestServerVolumeList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = sdk_fakes.generate_fake_resource(_server.Server)
        self.volume_attachments = list(
            sdk_fakes.generate_fake_resources(
                _volume_attachment.VolumeAttachment, count=2
            )
        )

        self.compute_client.find_server.return_value = self.server
        self.compute_client.volume_attachments.return_value = (
            self.volume_attachments
        )

        # Get the command object to test
        self.cmd = server_volume.ListServerVolume(self.app, None)

    def test_server_volume_list(self):
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
                    self.volume_attachments[0].server_id,
                    self.volume_attachments[0].volume_id,
                ),
                (
                    self.volume_attachments[1].id,
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].server_id,
                    self.volume_attachments[1].volume_id,
                ),
            ),
            tuple(data),
        )
        self.compute_client.volume_attachments.assert_called_once_with(
            self.server,
        )

    def test_server_volume_list_with_tags(self):
        self.set_compute_api_version('2.70')

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
                'ID',
                'Device',
                'Server ID',
                'Volume ID',
                'Tag',
            ),
            columns,
        )
        self.assertEqual(
            (
                (
                    self.volume_attachments[0].id,
                    self.volume_attachments[0].device,
                    self.volume_attachments[0].server_id,
                    self.volume_attachments[0].volume_id,
                    self.volume_attachments[0].tag,
                ),
                (
                    self.volume_attachments[1].id,
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].server_id,
                    self.volume_attachments[1].volume_id,
                    self.volume_attachments[1].tag,
                ),
            ),
            tuple(data),
        )
        self.compute_client.volume_attachments.assert_called_once_with(
            self.server,
        )

    def test_server_volume_list_with_delete_on_attachment(self):
        self.set_compute_api_version('2.79')

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
                'ID',
                'Device',
                'Server ID',
                'Volume ID',
                'Tag',
                'Delete On Termination?',
            ),
            columns,
        )
        self.assertEqual(
            (
                (
                    self.volume_attachments[0].id,
                    self.volume_attachments[0].device,
                    self.volume_attachments[0].server_id,
                    self.volume_attachments[0].volume_id,
                    self.volume_attachments[0].tag,
                    self.volume_attachments[0].delete_on_termination,
                ),
                (
                    self.volume_attachments[1].id,
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].server_id,
                    self.volume_attachments[1].volume_id,
                    self.volume_attachments[1].tag,
                    self.volume_attachments[1].delete_on_termination,
                ),
            ),
            tuple(data),
        )
        self.compute_client.volume_attachments.assert_called_once_with(
            self.server,
        )

    def test_server_volume_list_with_attachment_ids(self):
        self.set_compute_api_version('2.89')

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
                'Device',
                'Server ID',
                'Volume ID',
                'Tag',
                'Delete On Termination?',
                'Attachment ID',
                'BlockDeviceMapping UUID',
            ),
            columns,
        )
        self.assertEqual(
            (
                (
                    self.volume_attachments[0].device,
                    self.volume_attachments[0].server_id,
                    self.volume_attachments[0].volume_id,
                    self.volume_attachments[0].tag,
                    self.volume_attachments[0].delete_on_termination,
                    self.volume_attachments[0].attachment_id,
                    self.volume_attachments[0].bdm_id,
                ),
                (
                    self.volume_attachments[1].device,
                    self.volume_attachments[1].server_id,
                    self.volume_attachments[1].volume_id,
                    self.volume_attachments[1].tag,
                    self.volume_attachments[1].delete_on_termination,
                    self.volume_attachments[1].attachment_id,
                    self.volume_attachments[1].bdm_id,
                ),
            ),
            tuple(data),
        )
        self.compute_client.volume_attachments.assert_called_once_with(
            self.server,
        )


class TestServerVolumeUpdate(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = sdk_fakes.generate_fake_resource(_server.Server)
        self.compute_client.find_server.return_value = self.server

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume

        # Get the command object to test
        self.cmd = server_volume.UpdateServerVolume(self.app, None)

    def test_server_volume_update(self):
        arglist = [
            self.server.id,
            self.volume.id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('delete_on_termination', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # This is a no-op
        self.compute_client.update_volume_attachment.assert_not_called()
        self.assertIsNone(result)

    def test_server_volume_update_with_delete_on_termination(self):
        self.set_compute_api_version('2.85')

        arglist = [
            self.server.id,
            self.volume.id,
            '--delete-on-termination',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.update_volume_attachment.assert_called_once_with(
            self.server,
            self.volume,
            delete_on_termination=True,
        )
        self.assertIsNone(result)

    def test_server_volume_update_with_preserve_on_termination(self):
        self.set_compute_api_version('2.85')

        arglist = [
            self.server.id,
            self.volume.id,
            '--preserve-on-termination',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('delete_on_termination', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.update_volume_attachment.assert_called_once_with(
            self.server, self.volume, delete_on_termination=False
        )
        self.assertIsNone(result)

    def test_server_volume_update_with_delete_on_termination_pre_v285(self):
        self.set_compute_api_version('2.84')

        arglist = [
            self.server.id,
            self.volume.id,
            '--delete-on-termination',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.compute_client.update_volume_attachment.assert_not_called()

    def test_server_volume_update_with_preserve_on_termination_pre_v285(self):
        self.set_compute_api_version('2.84')

        arglist = [
            self.server.id,
            self.volume.id,
            '--preserve-on-termination',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('delete_on_termination', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.compute_client.update_volume_attachment.assert_not_called()
