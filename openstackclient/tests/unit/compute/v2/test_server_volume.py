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

from unittest import mock

from novaclient import api_versions
from openstack import utils as sdk_utils
from osc_lib import exceptions

from openstackclient.compute.v2 import server_volume
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class TestServerVolume(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.app.client_manager.sdk_connection = mock.Mock()
        self.app.client_manager.sdk_connection.compute = mock.Mock()
        self.app.client_manager.sdk_connection.volume = mock.Mock()
        self.compute_client = self.app.client_manager.sdk_connection.compute
        self.volume_client = self.app.client_manager.sdk_connection.volume


class TestServerVolumeList(TestServerVolume):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.volume_attachments = compute_fakes.create_volume_attachments()

        self.compute_client.find_server.return_value = self.server
        self.compute_client.volume_attachments.return_value = (
            self.volume_attachments
        )

        # Get the command object to test
        self.cmd = server_volume.ListServerVolume(self.app, None)

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_list(self, sm_mock):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.1'
        )
        sm_mock.side_effect = [False, False, False, False]

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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_list_with_tags(self, sm_mock):
        sm_mock.side_effect = [False, True, False, False]

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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_list_with_delete_on_attachment(self, sm_mock):
        sm_mock.side_effect = [False, True, True, False]
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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_list_with_attachment_ids(self, sm_mock):
        sm_mock.side_effect = [True, True, True, True]
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


class TestServerVolumeUpdate(TestServerVolume):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.volume = volume_fakes.create_one_sdk_volume()
        self.volume_client.find_volume.return_value = self.volume

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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_update_with_delete_on_termination(self, sm_mock):
        sm_mock.return_value = True

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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_update_with_preserve_on_termination(self, sm_mock):
        sm_mock.return_value = True

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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_update_with_delete_on_termination_pre_v285(
        self,
        sm_mock,
    ):
        sm_mock.return_value = False

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

    @mock.patch.object(sdk_utils, 'supports_microversion')
    def test_server_volume_update_with_preserve_on_termination_pre_v285(
        self,
        sm_mock,
    ):
        sm_mock.return_value = False

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
