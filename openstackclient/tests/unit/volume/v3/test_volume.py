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
from unittest import mock

from cinderclient import api_versions
from openstack.block_storage.v3 import block_storage_summary as _summary
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import volume as _volume
from openstack.test import fakes as sdk_fakes
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes
from openstackclient.volume.v3 import volume


class BaseVolumeTest(fakes.TestVolume):
    def setUp(self):
        super().setUp()

        patcher = mock.patch.object(
            sdk_utils, 'supports_microversion', return_value=True
        )
        self.addCleanup(patcher.stop)
        self.supports_microversion_mock = patcher.start()
        self._set_mock_microversion(
            self.volume_client.api_version.get_string()
        )

    def _set_mock_microversion(self, mock_v):
        """Set a specific microversion for the mock supports_microversion()."""
        self.supports_microversion_mock.reset_mock(return_value=True)
        self.supports_microversion_mock.side_effect = (
            lambda _, v: api_versions.APIVersion(v)
            <= api_versions.APIVersion(mock_v)
        )


class TestVolumeSummary(BaseVolumeTest):
    columns = [
        'Total Count',
        'Total Size',
    ]

    def setUp(self):
        super().setUp()

        self.volume_a = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_b = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.summary = sdk_fakes.generate_fake_resource(
            _summary.BlockStorageSummary,
            total_count=2,
            total_size=self.volume_a.size + self.volume_b.size,
        )
        self.volume_sdk_client.summary.return_value = self.summary

        # Get the command object to test
        self.cmd = volume.VolumeSummary(self.app, None)

    def test_volume_summary(self):
        self._set_mock_microversion('3.12')
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.summary.assert_called_once_with(True)

        self.assertEqual(self.columns, columns)

        datalist = (2, self.volume_a.size + self.volume_b.size)
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_summary_pre_312(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.12 or greater is required', str(exc)
        )

    def test_volume_summary_with_metadata(self):
        self._set_mock_microversion('3.36')

        metadata = {**self.volume_a.metadata, **self.volume_b.metadata}
        self.summary = sdk_fakes.generate_fake_resource(
            _summary.BlockStorageSummary,
            total_count=2,
            total_size=self.volume_a.size + self.volume_b.size,
            metadata=metadata,
        )
        self.volume_sdk_client.summary.return_value = self.summary

        new_cols = copy.deepcopy(self.columns)
        new_cols.extend(['Metadata'])

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.summary.assert_called_once_with(True)

        self.assertEqual(new_cols, columns)

        datalist = (
            2,
            self.volume_a.size + self.volume_b.size,
            format_columns.DictColumn(metadata),
        )
        self.assertCountEqual(datalist, tuple(data))


class TestVolumeRevertToSnapshot(BaseVolumeTest):
    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.snapshot = sdk_fakes.generate_fake_resource(
            _snapshot.Snapshot,
            volume_id=self.volume.id,
        )
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.find_snapshot.return_value = self.snapshot

        # Get the command object to test
        self.cmd = volume.VolumeRevertToSnapshot(self.app, None)

    def test_volume_revert_to_snapshot_pre_340(self):
        arglist = [
            self.snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.40 or greater is required', str(exc)
        )

    def test_volume_revert_to_snapshot(self):
        self._set_mock_microversion('3.40')
        arglist = [
            self.snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.volume_sdk_client.revert_volume_to_snapshot.assert_called_once_with(
            self.volume,
            self.snapshot,
        )
        self.volume_sdk_client.find_volume.assert_called_with(
            self.volume.id,
            ignore_missing=False,
        )
        self.volume_sdk_client.find_snapshot.assert_called_with(
            self.snapshot.id,
            ignore_missing=False,
        )


class TestVolumeCreate(BaseVolumeTest):
    columns = (
        'attachments',
        'availability_zone',
        'consistency_group_id',
        'created_at',
        'description',
        'extended_replication_status',
        'group_id',
        'host',
        'id',
        'image_id',
        'is_bootable',
        'is_encrypted',
        'is_multiattach',
        'location',
        'metadata',
        'migration_id',
        'migration_status',
        'name',
        'project_id',
        'provider_id',
        'replication_driver_data',
        'replication_status',
        'scheduler_hints',
        'size',
        'snapshot_id',
        'source_volume_id',
        'status',
        'updated_at',
        'user_id',
        'volume_image_metadata',
        'volume_type',
    )

    def setUp(self):
        super().setUp()

        self.new_volume = sdk_fakes.generate_fake_resource(
            _volume.Volume, **{'size': 1}
        )

        self.datalist = (
            self.new_volume.attachments,
            self.new_volume.availability_zone,
            self.new_volume.consistency_group_id,
            self.new_volume.created_at,
            self.new_volume.description,
            self.new_volume.extended_replication_status,
            self.new_volume.group_id,
            self.new_volume.host,
            self.new_volume.id,
            self.new_volume.image_id,
            self.new_volume.is_bootable,
            self.new_volume.is_encrypted,
            self.new_volume.is_multiattach,
            self.new_volume.location,
            self.new_volume.metadata,
            self.new_volume.migration_id,
            self.new_volume.migration_status,
            self.new_volume.name,
            self.new_volume.project_id,
            self.new_volume.provider_id,
            self.new_volume.replication_driver_data,
            self.new_volume.replication_status,
            self.new_volume.scheduler_hints,
            self.new_volume.size,
            self.new_volume.snapshot_id,
            self.new_volume.source_volume_id,
            self.new_volume.status,
            self.new_volume.updated_at,
            self.new_volume.user_id,
            self.new_volume.volume_image_metadata,
            self.new_volume.volume_type,
        )

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_remote_source(self):
        self.volume_sdk_client.manage_volume.return_value = self.new_volume

        arglist = [
            '--remote-source',
            'key=val',
            '--host',
            'fake_host',
            self.new_volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('host', 'fake_host'),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.manage_volume.assert_called_with(
            host='fake_host',
            ref={'key': 'val'},
            name=parsed_args.name,
            description=parsed_args.description,
            volume_type=parsed_args.type,
            availability_zone=parsed_args.availability_zone,
            metadata=parsed_args.property,
            bootable=parsed_args.bootable,
            cluster=getattr(parsed_args, 'cluster', None),
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_remote_source_pre_316(self):
        self._set_mock_microversion('3.15')
        arglist = [
            '--remote-source',
            'key=val',
            '--cluster',
            'fake_cluster',
            self.new_volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('cluster', 'fake_cluster'),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.16 or greater is required', str(exc)
        )

    def test_volume_create_remote_source_host_and_cluster(self):
        self._set_mock_microversion('3.16')
        arglist = [
            '--remote-source',
            'key=val',
            '--host',
            'fake_host',
            '--cluster',
            'fake_cluster',
            self.new_volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('host', 'fake_host'),
            ('cluster', 'fake_cluster'),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'Only one of --host or --cluster needs to be specified', str(exc)
        )

    def test_volume_create_remote_source_no_host_or_cluster(self):
        arglist = [
            '--remote-source',
            'key=val',
            self.new_volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'One of --host or --cluster needs to be specified to ', str(exc)
        )

    def test_volume_create_remote_source_size(self):
        arglist = [
            '--size',
            str(self.new_volume.size),
            '--remote-source',
            'key=val',
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('remote_source', {'key': 'val'}),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--size, --consistency-group, --hint, --read-only and '
            '--read-write options are not supported',
            str(exc),
        )

    def test_volume_create_host_no_remote_source(self):
        arglist = [
            '--size',
            str(self.new_volume.size),
            '--host',
            'fake_host',
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('host', 'fake_host'),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--host and --cluster options are only supported ',
            str(exc),
        )


class TestVolumeDelete(BaseVolumeTest):
    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()
        self.volume_sdk_client.unmanage_volume.return_value = None

        # Get the command object to mock
        self.cmd = volume.DeleteVolume(self.app, None)

    def test_volume_delete_remote(self):
        vol = sdk_fakes.generate_fake_resource(_volume.Volume, **{'size': 1})
        self.volumes_mock.get.return_value = vol

        arglist = ['--remote', vol.id]
        verifylist = [
            ("remote", True),
            ("force", False),
            ("purge", False),
            ("volumes", [vol.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.unmanage_volume.assert_called_once_with(vol.id)
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes_remote(self):
        volumes = sdk_fakes.generate_fake_resources(
            _volume.Volume, count=3, attrs={'size': 1}
        )

        arglist = ['--remote']
        arglist += [v.id for v in volumes]
        verifylist = [
            ('remote', True),
            ('force', False),
            ('purge', False),
            ('volumes', arglist[1:]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [mock.call(v.id) for v in volumes]
        self.volume_sdk_client.unmanage_volume.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_volume_delete_remote_with_purge(self):
        vol = sdk_fakes.generate_fake_resource(_volume.Volume, **{'size': 1})

        arglist = [
            '--remote',
            '--purge',
            vol.id,
        ]
        verifylist = [
            ('remote', True),
            ('force', False),
            ('purge', True),
            ('volumes', [vol.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            "The --force and --purge options are not supported with the "
            "--remote parameter.",
            str(exc),
        )

    def test_volume_delete_remote_with_force(self):
        vol = sdk_fakes.generate_fake_resource(_volume.Volume, **{'size': 1})

        arglist = [
            '--remote',
            '--force',
            vol.id,
        ]
        verifylist = [
            ('remote', True),
            ('force', True),
            ('purge', False),
            ('volumes', [vol.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            "The --force and --purge options are not supported with the "
            "--remote parameter.",
            str(exc),
        )
