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

import copy
from unittest import mock
import uuid

from openstack.block_storage.v3 import backup as _backup
from openstack.block_storage.v3 import block_storage_summary as _summary
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.api import volume_v3
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils as test_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume


class TestVolumeCreate(volume_fakes.TestVolume):
    columns = (
        'attachments',
        'availability_zone',
        'bootable',
        'cluster_name',
        'consistencygroup_id',
        'consumes_quota',
        'created_at',
        'description',
        'encrypted',
        'encryption_key_id',
        'group_id',
        'id',
        'multiattach',
        'name',
        'os-vol-host-attr:host',
        'os-vol-mig-status-attr:migstat',
        'os-vol-mig-status-attr:name_id',
        'os-vol-tenant-attr:tenant_id',
        'properties',
        'provider_id',
        'replication_status',
        'service_uuid',
        'shared_targets',
        'size',
        'snapshot_id',
        'source_volid',
        'status',
        'type',
        'updated_at',
        'user_id',
        'volume_image_metadata',
        'volume_type_id',
    )

    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.create_volume.return_value = self.volume

        self.datalist = (
            self.volume.attachments,
            self.volume.availability_zone,
            self.volume.is_bootable,
            self.volume.cluster_name,
            self.volume.consistency_group_id,
            self.volume.consumes_quota,
            self.volume.created_at,
            self.volume.description,
            self.volume.is_encrypted,
            self.volume.encryption_key_id,
            self.volume.group_id,
            self.volume.id,
            self.volume.is_multiattach,
            self.volume.name,
            self.volume.host,
            self.volume.migration_status,
            self.volume.migration_id,
            self.volume.project_id,
            format_columns.DictColumn(self.volume.metadata),
            self.volume.provider_id,
            self.volume.replication_status,
            self.volume.service_uuid,
            self.volume.shared_targets,
            self.volume.size,
            self.volume.snapshot_id,
            self.volume.source_volume_id,
            self.volume.status,
            self.volume.volume_type,
            self.volume.updated_at,
            self.volume.user_id,
            self.volume.volume_image_metadata,
            self.volume.volume_type_id,
        )

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_min_options(self):
        arglist = [
            '--size',
            str(self.volume.size),
        ]
        verifylist = [
            ('size', self.volume.size),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=None,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_options(self):
        consistency_group_id = 'cg123'
        arglist = [
            '--size',
            str(self.volume.size),
            '--description',
            self.volume.description,
            '--type',
            self.volume.volume_type,
            '--availability-zone',
            self.volume.availability_zone,
            '--consistency-group',
            consistency_group_id,
            '--hint',
            'k=v',
            self.volume.name,
        ]
        verifylist = [
            ('size', self.volume.size),
            ('description', self.volume.description),
            ('type', self.volume.volume_type),
            ('availability_zone', self.volume.availability_zone),
            ('consistency_group', consistency_group_id),
            ('hint', {'k': 'v'}),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(
            volume_v3,
            'find_consistency_group',
            return_value={'id': consistency_group_id},
        ) as mock_find_cg:
            columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=self.volume.description,
            volume_type=self.volume.volume_type,
            availability_zone=self.volume.availability_zone,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=consistency_group_id,
            scheduler_hints={'k': 'v'},
            backup_id=None,
        )
        mock_find_cg.assert_called_once_with(
            self.volume_sdk_client, consistency_group_id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_properties(self):
        arglist = [
            '--property',
            'Alpha=a',
            '--property',
            'Beta=b',
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('properties', {'Alpha': 'a', 'Beta': 'b'}),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata={'Alpha': 'a', 'Beta': 'b'},
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_id(self):
        image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = image

        arglist = [
            '--image',
            image.id,
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('image', image.id),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=image.id,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_name(self):
        image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = image

        arglist = [
            '--image',
            image.name,
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('image', image.name),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=image.id,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_snapshot(self):
        snapshot = sdk_fakes.generate_fake_resource(_snapshot.Snapshot)
        self.volume_sdk_client.find_snapshot.return_value = snapshot

        arglist = [
            '--snapshot',
            snapshot.id,
            self.volume.name,
        ]
        verifylist = [
            ('snapshot', snapshot.id),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=snapshot.size,
            snapshot_id=snapshot.id,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )
        self.volume_sdk_client.find_snapshot.assert_called_once_with(
            snapshot.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_backup(self):
        self.set_volume_api_version('3.47')

        backup = sdk_fakes.generate_fake_resource(_backup.Backup)
        self.volume_sdk_client.find_backup.return_value = backup

        arglist = [
            '--backup',
            backup.id,
            self.volume.name,
        ]
        verifylist = [
            ('backup', backup.id),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=backup.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=backup.id,
        )
        self.volume_sdk_client.find_backup.assert_called_once_with(
            backup.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_backup_pre_v347(self):
        backup = sdk_fakes.generate_fake_resource(_backup.Backup)
        self.volume_sdk_client.find_backup.return_value = backup

        arglist = [
            '--backup',
            backup.id,
            self.volume.name,
        ]
        verifylist = [
            ('backup', backup.id),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.47 or greater", str(exc))

        self.volume_sdk_client.create_volume.assert_not_called()

    def test_volume_create_with_source_volume(self):
        source_volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = source_volume

        arglist = [
            '--source',
            source_volume.id,
            self.volume.name,
        ]
        verifylist = [
            ('source', source_volume.id),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=source_volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=source_volume.id,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )
        self.volume_sdk_client.find_volume.assert_called_once_with(
            source_volume.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch.object(utils, 'wait_for_status', return_value=True)
    def test_volume_create_with_bootable_and_readonly(self, mock_wait):
        arglist = [
            '--bootable',
            '--read-only',
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('bootable', True),
            ('read_only', True),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )
        self.volume_sdk_client.set_volume_bootable_status.assert_called_once_with(
            self.volume, True
        )
        self.volume_sdk_client.set_volume_readonly.assert_called_once_with(
            self.volume, True
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch.object(utils, 'wait_for_status', return_value=True)
    def test_volume_create_with_nonbootable_and_readwrite(self, mock_wait):
        arglist = [
            '--non-bootable',
            '--read-write',
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('bootable', False),
            ('read_only', False),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )
        self.volume_sdk_client.set_volume_bootable_status.assert_called_once_with(
            self.volume, False
        )
        self.volume_sdk_client.set_volume_readonly.assert_called_once_with(
            self.volume, False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch.object(volume.LOG, 'error')
    @mock.patch.object(utils, 'wait_for_status', return_value=True)
    def test_volume_create_with_bootable_and_readonly_fail(
        self, mock_wait, mock_error
    ):
        self.volume_sdk_client.set_volume_bootable_status.side_effect = (
            sdk_exceptions.NotFoundException('foo')
        )
        self.volume_sdk_client.set_volume_readonly.side_effect = (
            sdk_exceptions.NotFoundException('foo')
        )

        arglist = [
            '--bootable',
            '--read-only',
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('bootable', True),
            ('read_only', True),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )
        self.volume_sdk_client.set_volume_bootable_status.assert_called_once_with(
            self.volume, True
        )
        self.volume_sdk_client.set_volume_readonly.assert_called_once_with(
            self.volume, True
        )

        self.assertEqual(2, mock_error.call_count)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch.object(volume.LOG, 'error')
    @mock.patch.object(utils, 'wait_for_status', return_value=False)
    def test_volume_create_non_available_with_readonly(
        self, mock_wait, mock_error
    ):
        arglist = [
            '--non-bootable',
            '--read-only',
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('bootable', False),
            ('read_only', True),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints=None,
            backup_id=None,
        )

        self.assertEqual(2, mock_error.call_count)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_without_size(self):
        arglist = [
            self.volume.name,
        ]
        verifylist = [
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_volume_create_with_multi_source(self):
        arglist = [
            '--image',
            'source_image',
            '--source',
            'source_volume',
            '--snapshot',
            'source_snapshot',
            '--size',
            str(self.volume.size),
            self.volume.name,
        ]
        verifylist = [
            ('image', 'source_image'),
            ('source', 'source_volume'),
            ('snapshot', 'source_snapshot'),
            ('size', self.volume.size),
            ('name', self.volume.name),
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_volume_create_hints(self):
        """--hint needs to behave differently based on the given hint

        different_host and same_host need to append to a list if given multiple
        times. All other parameter are strings.
        """
        arglist = [
            '--size',
            str(self.volume.size),
            '--hint',
            'k=v',
            '--hint',
            'k=v2',
            '--hint',
            'same_host=v3',
            '--hint',
            'same_host=v4',
            '--hint',
            'different_host=v5',
            '--hint',
            'local_to_instance=v6',
            '--hint',
            'different_host=v7',
            self.volume.name,
        ]
        verifylist = [
            ('size', self.volume.size),
            (
                'hint',
                {
                    'k': 'v2',
                    'same_host': ['v3', 'v4'],
                    'local_to_instance': 'v6',
                    'different_host': ['v5', 'v7'],
                },
            ),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_volume.assert_called_with(
            size=self.volume.size,
            snapshot_id=None,
            name=self.volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            image_id=None,
            source_volume_id=None,
            consistency_group_id=None,
            scheduler_hints={
                'k': 'v2',
                'same_host': ['v3', 'v4'],
                'local_to_instance': 'v6',
                'different_host': ['v5', 'v7'],
            },
            backup_id=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_remote_source(self):
        self.volume_sdk_client.manage_volume.return_value = self.volume

        arglist = [
            '--remote-source',
            'key=val',
            '--host',
            'fake_host',
            self.volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('host', 'fake_host'),
            ('name', self.volume.name),
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
            metadata=parsed_args.properties,
            bootable=parsed_args.bootable,
            cluster=getattr(parsed_args, 'cluster', None),
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_remote_source_pre_v316(self):
        self.set_volume_api_version('3.15')
        arglist = [
            '--remote-source',
            'key=val',
            '--cluster',
            'fake_cluster',
            self.volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('cluster', 'fake_cluster'),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.16 or greater is required', str(exc)
        )

    def test_volume_create_remote_source_host_and_cluster(self):
        self.set_volume_api_version('3.16')
        arglist = [
            '--remote-source',
            'key=val',
            '--host',
            'fake_host',
            '--cluster',
            'fake_cluster',
            self.volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('host', 'fake_host'),
            ('cluster', 'fake_cluster'),
            ('name', self.volume.name),
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
            self.volume.name,
        ]
        verifylist = [
            ('remote_source', {'key': 'val'}),
            ('name', self.volume.name),
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
            str(self.volume.size),
            '--remote-source',
            'key=val',
            self.volume.name,
        ]
        verifylist = [
            ('size', self.volume.size),
            ('remote_source', {'key': 'val'}),
            ('name', self.volume.name),
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
            str(self.volume.size),
            '--host',
            'fake_host',
            self.volume.name,
        ]
        verifylist = [
            ('size', self.volume.size),
            ('host', 'fake_host'),
            ('name', self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--host and --cluster options are only supported ',
            str(exc),
        )


class TestVolumeDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()

        self.volumes = list(sdk_fakes.generate_fake_resources(_volume.Volume))
        self.volume_sdk_client.find_volume.side_effect = self.volumes
        self.volume_sdk_client.delete_volume.return_value = None
        self.volume_sdk_client.unmanage_volume.return_value = None

        # Get the command object to mock
        self.cmd = volume.DeleteVolume(self.app, None)

    def test_volume_delete_one_volume(self):
        arglist = [self.volumes[0].id]
        verifylist = [
            ("force", False),
            ("purge", False),
            ("volumes", [self.volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volumes[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_volume.assert_called_once_with(
            self.volumes[0].id, cascade=False, force=False
        )

    def test_volume_delete_multi_volumes(self):
        arglist = [v.id for v in self.volumes]
        verifylist = [
            ('force', False),
            ('purge', False),
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_has_calls(
            [mock.call(v.id, ignore_missing=False) for v in self.volumes]
        )
        self.volume_sdk_client.delete_volume.assert_has_calls(
            [mock.call(v.id, cascade=False, force=False) for v in self.volumes]
        )

    def test_volume_delete_multi_volumes_with_exception(self):
        self.volume_sdk_client.find_volume.side_effect = [
            self.volumes[0],
            sdk_exceptions.NotFoundException(),
        ]

        arglist = [
            self.volumes[0].id,
            'unexist_volume',
        ]
        verifylist = [
            ('force', False),
            ('purge', False),
            ('volumes', [self.volumes[0].id, 'unexist_volume']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertEqual('1 of 2 volumes failed to delete.', str(exc))

        self.volume_sdk_client.find_volume.assert_has_calls(
            [
                mock.call(self.volumes[0].id, ignore_missing=False),
                mock.call('unexist_volume', ignore_missing=False),
            ]
        )
        self.volume_sdk_client.delete_volume.assert_has_calls(
            [
                mock.call(self.volumes[0].id, cascade=False, force=False),
            ]
        )

    def test_volume_delete_with_purge(self):
        arglist = [
            '--purge',
            self.volumes[0].id,
        ]
        verifylist = [
            ('force', False),
            ('purge', True),
            ('volumes', [self.volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volumes[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_volume.assert_called_once_with(
            self.volumes[0].id, cascade=True, force=False
        )

    def test_volume_delete_with_force(self):
        arglist = [
            '--force',
            self.volumes[0].id,
        ]
        verifylist = [
            ('force', True),
            ('purge', False),
            ('volumes', [self.volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volumes[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_volume.assert_called_once_with(
            self.volumes[0].id, cascade=False, force=True
        )

    def test_volume_delete_remote(self):
        arglist = ['--remote', self.volumes[0].id]
        verifylist = [
            ("remote", True),
            ("force", False),
            ("purge", False),
            ("volumes", [self.volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volumes[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_volume.assert_not_called()
        self.volume_sdk_client.unmanage_volume.assert_called_once_with(
            self.volumes[0].id
        )

    def test_volume_delete_multi_volumes_remote(self):
        arglist = ['--remote'] + [v.id for v in self.volumes]
        verifylist = [
            ('remote', True),
            ('force', False),
            ('purge', False),
            ('volumes', arglist[1:]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_has_calls(
            [mock.call(v.id, ignore_missing=False) for v in self.volumes]
        )
        self.volume_sdk_client.delete_volume.assert_not_called()
        self.volume_sdk_client.unmanage_volume.assert_has_calls(
            [mock.call(v.id) for v in self.volumes]
        )

    def test_volume_delete_remote_with_purge(self):
        arglist = [
            '--remote',
            '--purge',
            self.volumes[0].id,
        ]
        verifylist = [
            ('remote', True),
            ('force', False),
            ('purge', True),
            ('volumes', [self.volumes[0].id]),
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

        self.volume_sdk_client.find_volume.assert_not_called()
        self.volume_sdk_client.delete_volume.assert_not_called()
        self.volume_sdk_client.unmanage_volume.assert_not_called()

    def test_volume_delete_remote_with_force(self):
        arglist = [
            '--remote',
            '--force',
            self.volumes[0].id,
        ]
        verifylist = [
            ('remote', True),
            ('force', True),
            ('purge', False),
            ('volumes', [self.volumes[0].id]),
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

        self.volume_sdk_client.find_volume.assert_not_called()
        self.volume_sdk_client.delete_volume.assert_not_called()
        self.volume_sdk_client.unmanage_volume.assert_not_called()


class TestVolumeList(volume_fakes.TestVolume):
    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    columns = [
        'ID',
        'Name',
        'Status',
        'Size',
        'Attached to',
    ]

    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()

        self.users_mock = self.identity_client.users
        self.users_mock.reset_mock()

        self.mock_volume = volume_fakes.create_one_volume()
        self.volumes_mock.list.return_value = [self.mock_volume]

        self.users_mock.get.return_value = self.user

        self.projects_mock.get.return_value = self.project

        # Get the command object to test
        self.cmd = volume.ListVolume(self.app, None)

    def test_volume_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_project(self):
        arglist = [
            '--project',
            self.project.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'project_id': self.project.id,
            'user_id': None,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_project_domain(self):
        arglist = [
            '--project',
            self.project.name,
            '--project-domain',
            self.project.domain_id,
        ]
        verifylist = [
            ('project', self.project.name),
            ('project_domain', self.project.domain_id),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'project_id': self.project.id,
            'user_id': None,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_user(self):
        arglist = [
            '--user',
            self.user.name,
        ]
        verifylist = [
            ('user', self.user.name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': self.user.id,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )
        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_user_domain(self):
        arglist = [
            '--user',
            self.user.name,
            '--user-domain',
            self.user.domain_id,
        ]
        verifylist = [
            ('user', self.user.name),
            ('user_domain', self.user.domain_id),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': self.user.id,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_name(self):
        arglist = [
            '--name',
            self.mock_volume.name,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', self.mock_volume.name),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': self.mock_volume.name,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_status(self):
        arglist = [
            '--status',
            self.mock_volume.status,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', self.mock_volume.status),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': self.mock_volume.status,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', True),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        collist = [
            'ID',
            'Name',
            'Status',
            'Size',
            'Type',
            'Bootable',
            'Attached to',
            'Properties',
        ]
        self.assertEqual(collist, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                self.mock_volume.volume_type,
                self.mock_volume.bootable,
                volume.AttachmentsColumn(self.mock_volume.attachments),
                format_columns.DictColumn(self.mock_volume.metadata),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_with_marker_and_limit(self):
        arglist = [
            "--marker",
            self.mock_volume.id,
            "--limit",
            "2",
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', self.mock_volume.id),
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )

        self.volumes_mock.list.assert_called_once_with(
            marker=self.mock_volume.id,
            limit=2,
            search_opts={
                'status': None,
                'project_id': None,
                'user_id': None,
                'name': None,
                'all_tenants': False,
                'metadata': None,
            },
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_negative_limit(self):
        arglist = [
            "--limit",
            "-2",
        ]
        verifylist = [
            ("limit", -2),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_volume_list_backward_compatibility(self):
        arglist = [
            '-c',
            'Display Name',
        ]
        verifylist = [
            ('columns', ['Display Name']),
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
            'metadata': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertIn('Display Name', columns)
        self.assertNotIn('Name', columns)

        for each_volume in data:
            self.assertIn(self.mock_volume.name, each_volume)


class TestVolumeMigrate(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.migrate_volume.return_value = None

        self.cmd = volume.MigrateVolume(self.app, None)

    def test_volume_migrate(self):
        arglist = [
            "--host",
            "host@backend-name#pool",
            self.volume.id,
        ]
        verifylist = [
            ("force_host_copy", False),
            ("lock_volume", False),
            ("host", "host@backend-name#pool"),
            ("volume", self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_called_with(
            self.volume.id, ignore_missing=False
        )
        self.volume_sdk_client.migrate_volume.assert_called_once_with(
            self.volume.id,
            host="host@backend-name#pool",
            force_host_copy=False,
            lock_volume=False,
        )

    def test_volume_migrate_with_option(self):
        arglist = [
            "--force-host-copy",
            "--lock-volume",
            "--host",
            "host@backend-name#pool",
            self.volume.id,
        ]
        verifylist = [
            ("force_host_copy", True),
            ("lock_volume", True),
            ("host", "host@backend-name#pool"),
            ("volume", self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_volume.assert_called_with(
            self.volume.id, ignore_missing=False
        )
        self.volume_sdk_client.migrate_volume.assert_called_once_with(
            self.volume.id,
            host="host@backend-name#pool",
            force_host_copy=True,
            lock_volume=True,
        )

    def test_volume_migrate_without_host(self):
        arglist = [
            self.volume.id,
        ]
        verifylist = [
            ("force_host_copy", False),
            ("lock_volume", False),
            ("volume", self.volume.id),
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

        self.volume_sdk_client.find_volume.assert_not_called()
        self.volume_sdk_client.migrate_volume.assert_not_called()


class TestVolumeSet(volume_fakes.TestVolume):
    volume_type = volume_fakes.create_one_volume_type()

    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()

        self.types_mock = self.volume_client.volume_types
        self.types_mock.reset_mock()

        self.new_volume = volume_fakes.create_one_volume()
        self.volumes_mock.get.return_value = self.new_volume
        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume.SetVolume(self.app, None)

    def test_volume_set_property(self):
        arglist = [
            '--property',
            'a=b',
            '--property',
            'c=d',
            self.new_volume.id,
        ]
        verifylist = [
            ('properties', {'a': 'b', 'c': 'd'}),
            ('read_only', None),
            ('bootable', None),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_metadata.assert_called_with(
            self.new_volume.id, parsed_args.properties
        )

    def test_volume_set_image_property(self):
        arglist = [
            '--image-property',
            'Alpha=a',
            '--image-property',
            'Beta=b',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_properties', {'Alpha': 'a', 'Beta': 'b'}),
            ('read_only', None),
            ('bootable', None),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args.image_properties
        )

    def test_volume_set_state(self):
        arglist = ['--state', 'error', self.new_volume.id]
        verifylist = [
            ('state', 'error'),
            ('read_only', None),
            ('bootable', None),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, 'error'
        )
        self.volumes_mock.update_readonly_flag.assert_not_called()
        self.assertIsNone(result)

    def test_volume_set_state_failed(self):
        self.volumes_mock.reset_state.side_effect = exceptions.CommandError()
        arglist = ['--state', 'error', self.new_volume.id]
        verifylist = [('state', 'error'), ('volume', self.new_volume.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'One or more of the set operations failed', str(e)
            )
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, 'error'
        )

    def test_volume_set_attached(self):
        arglist = ['--attached', self.new_volume.id]
        verifylist = [
            ('attached', True),
            ('detached', False),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, attach_status='attached', state=None
        )
        self.assertIsNone(result)

    def test_volume_set_detached(self):
        arglist = ['--detached', self.new_volume.id]
        verifylist = [
            ('attached', False),
            ('detached', True),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, attach_status='detached', state=None
        )
        self.assertIsNone(result)

    def test_volume_set_bootable(self):
        arglist = [
            '--bootable',
            self.new_volume.id,
        ]
        verifylist = [
            ('bootable', True),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_bootable.assert_called_with(
            self.new_volume.id, verifylist[0][1]
        )

    def test_volume_set_non_bootable(self):
        arglist = [
            '--non-bootable',
            self.new_volume.id,
        ]
        verifylist = [
            ('bootable', False),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_bootable.assert_called_with(
            self.new_volume.id, verifylist[0][1]
        )

    def test_volume_set_readonly(self):
        arglist = ['--read-only', self.new_volume.id]
        verifylist = [
            ('read_only', True),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.update_readonly_flag.assert_called_once_with(
            self.new_volume.id, True
        )
        self.assertIsNone(result)

    def test_volume_set_read_write(self):
        arglist = ['--read-write', self.new_volume.id]
        verifylist = [
            ('read_only', False),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.update_readonly_flag.assert_called_once_with(
            self.new_volume.id, False
        )
        self.assertIsNone(result)

    def test_volume_set_type(self):
        arglist = ['--type', self.volume_type.id, self.new_volume.id]
        verifylist = [
            ('retype_policy', None),
            ('type', self.volume_type.id),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.retype.assert_called_once_with(
            self.new_volume.id, self.volume_type.id, 'never'
        )
        self.assertIsNone(result)

    def test_volume_set_type_with_policy(self):
        arglist = [
            '--retype-policy',
            'on-demand',
            '--type',
            self.volume_type.id,
            self.new_volume.id,
        ]
        verifylist = [
            ('retype_policy', 'on-demand'),
            ('type', self.volume_type.id),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.retype.assert_called_once_with(
            self.new_volume.id, self.volume_type.id, 'on-demand'
        )
        self.assertIsNone(result)

    @mock.patch.object(volume.LOG, 'warning')
    def test_volume_set_with_only_retype_policy(self, mock_warning):
        arglist = ['--retype-policy', 'on-demand', self.new_volume.id]
        verifylist = [
            ('retype_policy', 'on-demand'),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.retype.assert_not_called()
        mock_warning.assert_called_with(
            "'--retype-policy' option will not work without '--type' option"
        )
        self.assertIsNone(result)


class TestVolumeShow(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume

        self.columns = (
            'attachments',
            'availability_zone',
            'bootable',
            'cluster_name',
            'consistencygroup_id',
            'consumes_quota',
            'created_at',
            'description',
            'encrypted',
            'encryption_key_id',
            'group_id',
            'id',
            'multiattach',
            'name',
            'os-vol-host-attr:host',
            'os-vol-mig-status-attr:migstat',
            'os-vol-mig-status-attr:name_id',
            'os-vol-tenant-attr:tenant_id',
            'properties',
            'provider_id',
            'replication_status',
            'service_uuid',
            'shared_targets',
            'size',
            'snapshot_id',
            'source_volid',
            'status',
            'type',
            'updated_at',
            'user_id',
            'volume_image_metadata',
            'volume_type_id',
        )
        self.data = (
            self.volume.attachments,
            self.volume.availability_zone,
            self.volume.is_bootable,
            self.volume.cluster_name,
            self.volume.consistency_group_id,
            self.volume.consumes_quota,
            self.volume.created_at,
            self.volume.description,
            self.volume.is_encrypted,
            self.volume.encryption_key_id,
            self.volume.group_id,
            self.volume.id,
            self.volume.is_multiattach,
            self.volume.name,
            self.volume.host,
            self.volume.migration_status,
            self.volume.migration_id,
            self.volume.project_id,
            format_columns.DictColumn(self.volume.metadata),
            self.volume.provider_id,
            self.volume.replication_status,
            self.volume.service_uuid,
            self.volume.shared_targets,
            self.volume.size,
            self.volume.snapshot_id,
            self.volume.source_volume_id,
            self.volume.status,
            self.volume.volume_type,
            self.volume.updated_at,
            self.volume.user_id,
            self.volume.volume_image_metadata,
            self.volume.volume_type_id,
        )

        self.cmd = volume.ShowVolume(self.app, None)

    def test_volume_show(self):
        arglist = [self.volume.id]
        verifylist = [("volume", self.volume.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
        self.volume_sdk_client.find_volume.assert_called_with(
            self.volume.id, ignore_missing=False
        )


class TestVolumeUnset(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()

        self.new_volume = volume_fakes.create_one_volume()
        self.volumes_mock.get.return_value = self.new_volume

        # Get the command object to set property
        self.cmd_set = volume.SetVolume(self.app, None)

        # Get the command object to unset property
        self.cmd_unset = volume.UnsetVolume(self.app, None)

    def test_volume_unset_image_property(self):
        # Arguments for setting image properties
        arglist = [
            '--image-property',
            'Alpha=a',
            '--image-property',
            'Beta=b',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_properties', {'Alpha': 'a', 'Beta': 'b'}),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd_set, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd_set.take_action(parsed_args)

        # Arguments for unsetting image properties
        arglist_unset = [
            '--image-property',
            'Alpha',
            self.new_volume.id,
        ]
        verifylist_unset = [
            ('image_properties', ['Alpha']),
            ('volume', self.new_volume.id),
        ]
        parsed_args_unset = self.check_parser(
            self.cmd_unset, arglist_unset, verifylist_unset
        )

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd_unset.take_action(parsed_args_unset)

        self.volumes_mock.delete_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args_unset.image_properties
        )

    def test_volume_unset_image_property_fail(self):
        self.volumes_mock.delete_image_metadata.side_effect = (
            exceptions.CommandError()
        )
        arglist = [
            '--image-property',
            'Alpha',
            '--property',
            'Beta',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_properties', ['Alpha']),
            ('properties', ['Beta']),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd_unset, arglist, verifylist)

        try:
            self.cmd_unset.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'One or more of the unset operations failed', str(e)
            )
        self.volumes_mock.delete_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args.image_properties
        )
        self.volumes_mock.delete_metadata.assert_called_with(
            self.new_volume.id, parsed_args.properties
        )


class TestVolumeSummary(volume_fakes.TestVolume):
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
        self.set_volume_api_version('3.12')
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

    def test_volume_summary_pre_v312(self):
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
        self.set_volume_api_version('3.36')

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


class TestVolumeRevertToSnapshot(volume_fakes.TestVolume):
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

    def test_volume_revert_to_snapshot_pre_v340(self):
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
        self.set_volume_api_version('3.40')
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


class TestColumns(volume_fakes.TestVolume):
    def test_attachments_column_without_server_cache(self):
        vol = sdk_fakes.generate_fake_resource(
            _volume.Volume,
            attachments=[
                {
                    'device': '/dev/' + uuid.uuid4().hex,
                    'server_id': uuid.uuid4().hex,
                },
            ],
        )
        server_id = vol.attachments[0]['server_id']
        device = vol.attachments[0]['device']

        col = volume.AttachmentsColumn(vol.attachments, {})
        self.assertEqual(
            f'Attached to {server_id} on {device} ',
            col.human_readable(),
        )
        self.assertEqual(vol.attachments, col.machine_readable())

    def test_attachments_column_with_server_cache(self):
        vol = sdk_fakes.generate_fake_resource(
            _volume.Volume,
            attachments=[
                {
                    'device': '/dev/' + uuid.uuid4().hex,
                    'server_id': uuid.uuid4().hex,
                },
            ],
        )

        server_id = vol.attachments[0]['server_id']
        device = vol.attachments[0]['device']
        fake_server = mock.Mock()
        fake_server.name = 'fake-server-name'
        server_cache = {server_id: fake_server}

        col = volume.AttachmentsColumn(vol.attachments, server_cache)
        self.assertEqual(
            'Attached to {} on {} '.format('fake-server-name', device),
            col.human_readable(),
        )
        self.assertEqual(vol.attachments, col.machine_readable())
