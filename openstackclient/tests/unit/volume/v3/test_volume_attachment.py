# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_attachment


class TestVolumeAttachment(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.projects_mock = self.app.client_manager.identity.projects


class TestVolumeAttachmentCreate(TestVolumeAttachment):
    volume = volume_fakes.create_one_volume()
    server = compute_fakes.create_one_sdk_server()
    volume_attachment = volume_fakes.create_one_volume_attachment(
        attrs={'instance': server.id, 'volume_id': volume.id},
    )

    columns = (
        'ID',
        'Volume ID',
        'Instance ID',
        'Status',
        'Attach Mode',
        'Attached At',
        'Detached At',
        'Properties',
    )
    data = (
        volume_attachment.id,
        volume_attachment.volume_id,
        volume_attachment.instance,
        volume_attachment.status,
        volume_attachment.attach_mode,
        volume_attachment.attached_at,
        volume_attachment.detached_at,
        format_columns.DictColumn(volume_attachment.connection_info),
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.create_attachment.return_value = (
            self.volume_attachment.to_dict()
        )
        self.compute_client.find_server.return_value = self.server

        self.cmd = volume_attachment.CreateVolumeAttachment(self.app, None)

    def test_volume_attachment_create(self):
        self.set_volume_api_version('3.27')

        arglist = [
            self.volume.id,
            self.server.id,
        ]
        verifylist = [
            ('volume', self.volume.id),
            ('server', self.server.id),
            ('connect', False),
            ('initiator', None),
            ('ip', None),
            ('host', None),
            ('platform', None),
            ('os_type', None),
            ('multipath', False),
            ('mountpoint', None),
            ('mode', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volume.id, ignore_missing=False
        )
        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.volume_sdk_client.create_attachment.assert_called_once_with(
            self.volume.id,
            connector={},
            instance=self.server.id,
            mode=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_attachment_create_with_connect(self):
        self.set_volume_api_version('3.54')

        arglist = [
            self.volume.id,
            self.server.id,
            '--connect',
            '--initiator',
            'iqn.1993-08.org.debian:01:cad181614cec',
            '--ip',
            '192.168.1.20',
            '--host',
            'my-host',
            '--platform',
            'x86_64',
            '--os-type',
            'linux2',
            '--multipath',
            '--mountpoint',
            '/dev/vdb',
            '--mode',
            'null',
        ]
        verifylist = [
            ('volume', self.volume.id),
            ('server', self.server.id),
            ('connect', True),
            ('initiator', 'iqn.1993-08.org.debian:01:cad181614cec'),
            ('ip', '192.168.1.20'),
            ('host', 'my-host'),
            ('platform', 'x86_64'),
            ('os_type', 'linux2'),
            ('multipath', True),
            ('mountpoint', '/dev/vdb'),
            ('mode', 'null'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        connect_info = dict(
            [
                ('initiator', 'iqn.1993-08.org.debian:01:cad181614cec'),
                ('ip', '192.168.1.20'),
                ('host', 'my-host'),
                ('platform', 'x86_64'),
                ('os_type', 'linux2'),
                ('multipath', True),
                ('mountpoint', '/dev/vdb'),
            ]
        )

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volume.id, ignore_missing=False
        )
        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.volume_sdk_client.create_attachment.assert_called_once_with(
            self.volume.id,
            connector=connect_info,
            instance=self.server.id,
            mode='null',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_attachment_create_pre_v327(self):
        self.set_volume_api_version('3.26')

        arglist = [
            self.volume.id,
            self.server.id,
        ]
        verifylist = [
            ('volume', self.volume.id),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.27 or greater is required', str(exc)
        )

    def test_volume_attachment_create_with_mode_pre_v354(self):
        self.set_volume_api_version('3.53')

        arglist = [
            self.volume.id,
            self.server.id,
            '--mode',
            'rw',
        ]
        verifylist = [
            ('volume', self.volume.id),
            ('server', self.server.id),
            ('mode', 'rw'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.54 or greater is required', str(exc)
        )

    def test_volume_attachment_create_with_connect_missing_arg(self):
        self.set_volume_api_version('3.54')

        arglist = [
            self.volume.id,
            self.server.id,
            '--initiator',
            'iqn.1993-08.org.debian:01:cad181614cec',
        ]
        verifylist = [
            ('volume', self.volume.id),
            ('server', self.server.id),
            ('connect', False),
            ('initiator', 'iqn.1993-08.org.debian:01:cad181614cec'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'You must specify the --connect option for any', str(exc)
        )


class TestVolumeAttachmentDelete(TestVolumeAttachment):
    volume_attachment = volume_fakes.create_one_volume_attachment()

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.delete_attachment.return_value = None

        self.cmd = volume_attachment.DeleteVolumeAttachment(self.app, None)

    def test_volume_attachment_delete(self):
        self.set_volume_api_version('3.27')

        arglist = [
            self.volume_attachment.id,
        ]
        verifylist = [
            ('attachment', self.volume_attachment.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_attachment.assert_called_once_with(
            self.volume_attachment.id,
        )
        self.assertIsNone(result)

    def test_volume_attachment_delete_pre_v327(self):
        self.set_volume_api_version('3.26')

        arglist = [
            self.volume_attachment.id,
        ]
        verifylist = [
            ('attachment', self.volume_attachment.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.27 or greater is required', str(exc)
        )


class TestVolumeAttachmentSet(TestVolumeAttachment):
    volume_attachment = volume_fakes.create_one_volume_attachment()

    columns = (
        'ID',
        'Volume ID',
        'Instance ID',
        'Status',
        'Attach Mode',
        'Attached At',
        'Detached At',
        'Properties',
    )
    data = (
        volume_attachment.id,
        volume_attachment.volume_id,
        volume_attachment.instance,
        volume_attachment.status,
        volume_attachment.attach_mode,
        volume_attachment.attached_at,
        volume_attachment.detached_at,
        format_columns.DictColumn(volume_attachment.connection_info),
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.update_attachment.return_value = (
            self.volume_attachment
        )

        self.cmd = volume_attachment.SetVolumeAttachment(self.app, None)

    def test_volume_attachment_set(self):
        self.set_volume_api_version('3.27')

        arglist = [
            self.volume_attachment.id,
            '--initiator',
            'iqn.1993-08.org.debian:01:cad181614cec',
            '--ip',
            '192.168.1.20',
            '--host',
            'my-host',
            '--platform',
            'x86_64',
            '--os-type',
            'linux2',
            '--multipath',
            '--mountpoint',
            '/dev/vdb',
        ]
        verifylist = [
            ('attachment', self.volume_attachment.id),
            ('initiator', 'iqn.1993-08.org.debian:01:cad181614cec'),
            ('ip', '192.168.1.20'),
            ('host', 'my-host'),
            ('platform', 'x86_64'),
            ('os_type', 'linux2'),
            ('multipath', True),
            ('mountpoint', '/dev/vdb'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        connect_info = dict(
            [
                ('initiator', 'iqn.1993-08.org.debian:01:cad181614cec'),
                ('ip', '192.168.1.20'),
                ('host', 'my-host'),
                ('platform', 'x86_64'),
                ('os_type', 'linux2'),
                ('multipath', True),
                ('mountpoint', '/dev/vdb'),
            ]
        )

        self.volume_sdk_client.update_attachment.assert_called_once_with(
            self.volume_attachment.id,
            connector=connect_info,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_attachment_set_pre_v327(self):
        self.set_volume_api_version('3.26')

        arglist = [
            self.volume_attachment.id,
            '--initiator',
            'iqn.1993-08.org.debian:01:cad181614cec',
        ]
        verifylist = [
            ('attachment', self.volume_attachment.id),
            ('initiator', 'iqn.1993-08.org.debian:01:cad181614cec'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.27 or greater is required', str(exc)
        )


class TestVolumeAttachmentComplete(TestVolumeAttachment):
    volume_attachment = volume_fakes.create_one_volume_attachment()

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.complete_attachment.return_value = None

        self.cmd = volume_attachment.CompleteVolumeAttachment(self.app, None)

    def test_volume_attachment_complete(self):
        self.set_volume_api_version('3.44')

        arglist = [
            self.volume_attachment.id,
        ]
        verifylist = [
            ('attachment', self.volume_attachment.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.complete_attachment.assert_called_once_with(
            self.volume_attachment.id,
        )
        self.assertIsNone(result)

    def test_volume_attachment_complete_pre_v344(self):
        self.set_volume_api_version('3.43')

        arglist = [
            self.volume_attachment.id,
        ]
        verifylist = [
            ('attachment', self.volume_attachment.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.44 or greater is required', str(exc)
        )


class TestVolumeAttachmentList(TestVolumeAttachment):
    project = identity_fakes.FakeProject.create_one_project()
    volume_attachments = volume_fakes.create_volume_attachments()

    columns = (
        'ID',
        'Volume ID',
        'Server ID',
        'Status',
    )
    data = [
        (
            volume_attachment.id,
            volume_attachment.volume_id,
            volume_attachment.instance,
            volume_attachment.status,
        )
        for volume_attachment in volume_attachments
    ]

    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.project
        self.volume_sdk_client.attachments.return_value = (
            self.volume_attachments
        )

        self.cmd = volume_attachment.ListVolumeAttachment(self.app, None)

    def test_volume_attachment_list(self):
        self.set_volume_api_version('3.27')

        arglist = []
        verifylist = [
            ('project', None),
            ('all_projects', False),
            ('volume_id', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.attachments.assert_called_once_with(
            search_opts={
                'all_tenants': False,
                'project_id': None,
                'status': None,
                'volume_id': None,
            },
            marker=None,
            limit=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_attachment_list_with_options(self):
        self.set_volume_api_version('3.27')

        arglist = [
            '--project',
            self.project.name,
            '--volume-id',
            'volume-id',
            '--status',
            'attached',
            '--marker',
            'volume-attachment-id',
            '--limit',
            '2',
        ]
        verifylist = [
            ('project', self.project.name),
            ('all_projects', False),
            ('volume_id', 'volume-id'),
            ('status', 'attached'),
            ('marker', 'volume-attachment-id'),
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.attachments.assert_called_once_with(
            search_opts={
                'all_tenants': True,
                'project_id': self.project.id,
                'status': 'attached',
                'volume_id': 'volume-id',
            },
            marker='volume-attachment-id',
            limit=2,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_attachment_list_pre_v327(self):
        self.set_volume_api_version('3.26')

        arglist = []
        verifylist = [
            ('project', None),
            ('all_projects', False),
            ('volume_id', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.27 or greater is required', str(exc)
        )
