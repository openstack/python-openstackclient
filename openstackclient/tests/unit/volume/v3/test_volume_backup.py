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

from unittest import mock

from openstack.block_storage.v3 import backup as _backup
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import project as _project
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_backup


class TestBackupCreate(volume_fakes.TestVolume):
    columns = (
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.snapshot = sdk_fakes.generate_fake_resource(_snapshot.Snapshot)
        self.volume_sdk_client.find_snapshot.return_value = self.snapshot
        self.backup = sdk_fakes.generate_fake_resource(
            _backup.Backup,
            volume_id=self.volume.id,
            snapshot_id=self.snapshot.id,
        )
        self.volume_sdk_client.create_backup.return_value = self.backup

        self.data = (
            self.backup.id,
            self.backup.name,
            self.backup.volume_id,
        )

        self.cmd = volume_backup.CreateVolumeBackup(self.app, None)

    def test_backup_create(self):
        arglist = [
            "--name",
            self.backup.name,
            "--description",
            self.backup.description,
            "--container",
            self.backup.container,
            "--force",
            "--incremental",
            "--snapshot",
            self.backup.snapshot_id,
            self.backup.volume_id,
        ]
        verifylist = [
            ("name", self.backup.name),
            ("description", self.backup.description),
            ("container", self.backup.container),
            ("force", True),
            ("incremental", True),
            ("snapshot", self.backup.snapshot_id),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_backup.assert_called_with(
            volume_id=self.backup.volume_id,
            container=self.backup.container,
            name=self.backup.name,
            description=self.backup.description,
            force=True,
            is_incremental=True,
            snapshot_id=self.backup.snapshot_id,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_create_with_properties(self):
        self.set_volume_api_version('3.43')

        arglist = [
            "--property",
            "foo=bar",
            "--property",
            "wow=much-cool",
            self.backup.volume_id,
        ]
        verifylist = [
            ("properties", {"foo": "bar", "wow": "much-cool"}),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_backup.assert_called_with(
            volume_id=self.backup.volume_id,
            container=None,
            name=None,
            description=None,
            force=False,
            is_incremental=False,
            metadata={"foo": "bar", "wow": "much-cool"},
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_create_with_properties_pre_v343(self):
        self.set_volume_api_version('3.42')

        arglist = [
            "--property",
            "foo=bar",
            "--property",
            "wow=much-cool",
            self.backup.volume_id,
        ]
        verifylist = [
            ("properties", {"foo": "bar", "wow": "much-cool"}),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.43 or greater", str(exc))

    def test_backup_create_with_availability_zone(self):
        self.set_volume_api_version('3.51')

        arglist = [
            "--availability-zone",
            "my-az",
            self.backup.volume_id,
        ]
        verifylist = [
            ("availability_zone", "my-az"),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_backup.assert_called_with(
            volume_id=self.backup.volume_id,
            container=None,
            name=None,
            description=None,
            force=False,
            is_incremental=False,
            availability_zone="my-az",
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_create_with_availability_zone_pre_v351(self):
        self.set_volume_api_version('3.50')

        arglist = [
            "--availability-zone",
            "my-az",
            self.backup.volume_id,
        ]
        verifylist = [
            ("availability_zone", "my-az"),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.51 or greater", str(exc))

    def test_backup_create_without_name(self):
        arglist = [
            "--description",
            self.backup.description,
            "--container",
            self.backup.container,
            self.backup.volume_id,
        ]
        verifylist = [
            ("description", self.backup.description),
            ("container", self.backup.container),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_backup.assert_called_with(
            volume_id=self.backup.volume_id,
            container=self.backup.container,
            name=None,
            description=self.backup.description,
            force=False,
            is_incremental=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestBackupDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.backups = list(sdk_fakes.generate_fake_resources(_backup.Backup))
        self.volume_sdk_client.find_backup.side_effect = self.backups
        self.volume_sdk_client.delete_backup.return_value = None

        self.cmd = volume_backup.DeleteVolumeBackup(self.app, None)

    def test_backup_delete(self):
        arglist = [self.backups[0].id]
        verifylist = [("backups", [self.backups[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_backup.assert_called_with(
            self.backups[0].id, ignore_missing=False, force=False
        )
        self.assertIsNone(result)

    def test_backup_delete_with_force(self):
        arglist = [
            '--force',
            self.backups[0].id,
        ]
        verifylist = [('force', True), ("backups", [self.backups[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_backup.assert_called_with(
            self.backups[0].id, ignore_missing=False, force=True
        )
        self.assertIsNone(result)

    def test_delete_multiple_backups(self):
        arglist = []
        for b in self.backups:
            arglist.append(b.id)
        verifylist = [
            ('backups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for b in self.backups:
            calls.append(mock.call(b.id, ignore_missing=False, force=False))
        self.volume_sdk_client.delete_backup.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_backups_with_exception(self):
        arglist = [
            self.backups[0].id,
            'unexist_backup',
        ]
        verifylist = [
            ('backups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.backups[0], exceptions.CommandError]
        self.volume_sdk_client.find_backup.side_effect = find_mock_result

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 backups failed to delete.', str(e))

        self.volume_sdk_client.find_backup.assert_any_call(
            self.backups[0].id, ignore_missing=False
        )
        self.volume_sdk_client.find_backup.assert_any_call(
            'unexist_backup', ignore_missing=False
        )

        self.assertEqual(2, self.volume_sdk_client.find_backup.call_count)
        self.volume_sdk_client.delete_backup.assert_called_once_with(
            self.backups[0].id,
            ignore_missing=False,
            force=False,
        )


class TestBackupList(volume_fakes.TestVolume):
    columns = (
        'ID',
        'Name',
        'Description',
        'Status',
        'Size',
        'Incremental',
        'Created At',
    )
    columns_long = columns + (
        'Availability Zone',
        'Volume',
        'Container',
    )

    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.volumes.return_value = [self.volume]
        self.backups = list(
            sdk_fakes.generate_fake_resources(
                _backup.Backup,
                attrs={'volume_id': self.volume.id},
            )
        )
        self.volume_sdk_client.backups.return_value = self.backups
        self.volume_sdk_client.find_backup.return_value = self.backups[0]

        self.data = []
        for b in self.backups:
            self.data.append(
                (
                    b.id,
                    b.name,
                    b.description,
                    b.status,
                    b.size,
                    b.is_incremental,
                    b.created_at,
                )
            )
        self.data_long = []
        for b in self.backups:
            self.data_long.append(
                (
                    b.id,
                    b.name,
                    b.description,
                    b.status,
                    b.size,
                    b.is_incremental,
                    b.created_at,
                    b.availability_zone,
                    volume_backup.VolumeIdColumn(b.volume_id),
                    b.container,
                )
            )

        self.cmd = volume_backup.ListVolumeBackup(self.app, None)

    def test_backup_list_without_options(self):
        arglist = []
        verifylist = [
            ("long", False),
            ("name", None),
            ("status", None),
            ("volume", None),
            ("marker", None),
            ("limit", None),
            ('all_projects', False),
            ("project", None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_volume.assert_not_called()
        self.volume_sdk_client.find_backup.assert_not_called()
        self.volume_sdk_client.backups.assert_called_with(
            name=None,
            status=None,
            volume_id=None,
            all_tenants=False,
            marker=None,
            limit=None,
            project_id=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_backup_list_with_options(self):
        project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = project
        arglist = [
            "--long",
            "--name",
            self.backups[0].name,
            "--status",
            "error",
            "--volume",
            self.volume.id,
            "--marker",
            self.backups[0].id,
            "--all-projects",
            "--limit",
            "3",
            "--project",
            project.id,
        ]
        verifylist = [
            ("long", True),
            ("name", self.backups[0].name),
            ("status", "error"),
            ("volume", self.volume.id),
            ("marker", self.backups[0].id),
            ('all_projects', True),
            ("limit", 3),
            ("project", project.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.volume.id, ignore_missing=False
        )
        self.volume_sdk_client.find_backup.assert_called_once_with(
            self.backups[0].id, ignore_missing=False
        )
        self.volume_sdk_client.backups.assert_called_with(
            name=self.backups[0].name,
            status="error",
            volume_id=self.volume.id,
            all_tenants=True,
            marker=self.backups[0].id,
            limit=3,
            project_id=project.id,
        )
        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, list(data))


class TestBackupRestore(volume_fakes.TestVolume):
    columns = (
        "id",
        "volume_id",
        "volume_name",
    )

    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.backup = sdk_fakes.generate_fake_resource(
            _backup.Backup, volume_id=self.volume.id
        )
        self.volume_sdk_client.find_backup.return_value = self.backup
        self.volume_sdk_client.create_backup.return_value = self.backup
        self.volume_sdk_client.restore_backup.return_value = {
            'id': self.backup['id'],
            'volume_id': self.volume['id'],
            'volume_name': self.volume['name'],
        }

        self.data = (
            self.backup.id,
            self.volume.id,
            self.volume.name,
        )

        self.cmd = volume_backup.RestoreVolumeBackup(self.app, None)

    def test_backup_restore(self):
        self.volume_sdk_client.find_volume.side_effect = (
            exceptions.CommandError()
        )
        arglist = [self.backup.id]
        verifylist = [
            ("backup", self.backup.id),
            ("volume", None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.restore_backup.assert_called_with(
            self.backup.id,
            volume_id=None,
            name=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_restore_with_volume(self):
        self.volume_sdk_client.find_volume.side_effect = (
            exceptions.CommandError()
        )
        arglist = [
            self.backup.id,
            self.backup.volume_id,
        ]
        verifylist = [
            ("backup", self.backup.id),
            ("volume", self.backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.restore_backup.assert_called_with(
            self.backup.id,
            volume_id=None,
            name=self.backup.volume_id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_restore_with_volume_force(self):
        arglist = [
            "--force",
            self.backup.id,
            self.volume.name,
        ]
        verifylist = [
            ("force", True),
            ("backup", self.backup.id),
            ("volume", self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.restore_backup.assert_called_with(
            self.backup.id,
            volume_id=self.volume.id,
            name=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_restore_with_volume_existing(self):
        arglist = [
            self.backup.id,
            self.volume.name,
        ]
        verifylist = [
            ("backup", self.backup.id),
            ("volume", self.volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestBackupSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.backup = sdk_fakes.generate_fake_resource(
            _backup.Backup, metadata={'wow': 'cool'}
        )
        self.volume_sdk_client.find_backup.return_value = self.backup

        self.cmd = volume_backup.SetVolumeBackup(self.app, None)

    def test_backup_set_name(self):
        self.set_volume_api_version('3.9')

        arglist = [
            '--name',
            'new_name',
            self.backup.id,
        ]
        verifylist = [
            ('name', 'new_name'),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.update_backup.assert_called_once_with(
            self.backup, name='new_name'
        )

    def test_backup_set_name_pre_v39(self):
        self.set_volume_api_version('3.8')

        arglist = [
            '--name',
            'new_name',
            self.backup.id,
        ]
        verifylist = [
            ('name', 'new_name'),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.9 or greater", str(exc))

    def test_backup_set_description(self):
        self.set_volume_api_version('3.9')

        arglist = [
            '--description',
            'new_description',
            self.backup.id,
        ]
        verifylist = [
            ('name', None),
            ('description', 'new_description'),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.update_backup.assert_called_once_with(
            self.backup, description='new_description'
        )

    def test_backup_set_description_pre_v39(self):
        self.set_volume_api_version('3.8')

        arglist = [
            '--description',
            'new_description',
            self.backup.id,
        ]
        verifylist = [
            ('name', None),
            ('description', 'new_description'),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.9 or greater", str(exc))

    def test_backup_set_state(self):
        arglist = ['--state', 'error', self.backup.id]
        verifylist = [('state', 'error'), ('backup', self.backup.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.reset_backup_status.assert_called_with(
            self.backup, status='error'
        )

    def test_backup_set_state_failed(self):
        self.volume_sdk_client.reset_backup_status.side_effect = (
            sdk_exceptions.NotFoundException('foo')
        )

        arglist = ['--state', 'error', self.backup.id]
        verifylist = [('state', 'error'), ('backup', self.backup.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertEqual('One or more of the set operations failed', str(exc))

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.reset_backup_status.assert_called_with(
            self.backup, status='error'
        )

    def test_backup_set_no_property(self):
        self.set_volume_api_version('3.43')

        arglist = [
            '--no-property',
            self.backup.id,
        ]
        verifylist = [
            ('no_property', True),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.update_backup.assert_called_once_with(
            self.backup, metadata={}
        )

    def test_backup_set_no_property_pre_v343(self):
        self.set_volume_api_version('3.42')

        arglist = [
            '--no-property',
            self.backup.id,
        ]
        verifylist = [
            ('no_property', True),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.43 or greater", str(exc))

    def test_backup_set_property(self):
        self.set_volume_api_version('3.43')

        arglist = [
            '--property',
            'foo=bar',
            self.backup.id,
        ]
        verifylist = [
            ('properties', {'foo': 'bar'}),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.update_backup.assert_called_once_with(
            self.backup, metadata={'wow': 'cool', 'foo': 'bar'}
        )

    def test_backup_set_property_pre_v343(self):
        self.set_volume_api_version('3.42')

        arglist = [
            '--property',
            'foo=bar',
            self.backup.id,
        ]
        verifylist = [
            ('properties', {'foo': 'bar'}),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.43 or greater", str(exc))


class TestBackupUnset(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.backup = sdk_fakes.generate_fake_resource(
            _backup.Backup, metadata={'foo': 'bar', 'wow': 'cool'}
        )
        self.volume_sdk_client.find_backup.return_value = self.backup
        self.volume_sdk_client.delete_backup_metadata.return_value = None

        self.cmd = volume_backup.UnsetVolumeBackup(self.app, None)

    def test_backup_unset_property(self):
        self.set_volume_api_version('3.43')

        arglist = [
            '--property',
            'foo',
            self.backup.id,
        ]
        verifylist = [
            ('properties', ['foo']),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )
        self.volume_sdk_client.delete_backup_metadata.assert_called_once_with(
            self.backup, keys=['wow']
        )

    def test_backup_unset_property_pre_v343(self):
        self.set_volume_api_version('3.42')

        arglist = [
            '--property',
            'foo',
            self.backup.id,
        ]
        verifylist = [
            ('properties', ['foo']),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn("--os-volume-api-version 3.43 or greater", str(exc))


class TestBackupShow(volume_fakes.TestVolume):
    columns = (
        "availability_zone",
        "container",
        "created_at",
        "data_timestamp",
        "description",
        "encryption_key_id",
        "fail_reason",
        "has_dependent_backups",
        "id",
        "is_incremental",
        "metadata",
        "name",
        "object_count",
        "project_id",
        "size",
        "snapshot_id",
        "status",
        "updated_at",
        "user_id",
        "volume_id",
    )

    def setUp(self):
        super().setUp()

        self.backup = sdk_fakes.generate_fake_resource(_backup.Backup)
        self.volume_sdk_client.find_backup.return_value = self.backup

        self.data = (
            self.backup.availability_zone,
            self.backup.container,
            self.backup.created_at,
            self.backup.data_timestamp,
            self.backup.description,
            self.backup.encryption_key_id,
            self.backup.fail_reason,
            self.backup.has_dependent_backups,
            self.backup.id,
            self.backup.is_incremental,
            self.backup.metadata,
            self.backup.name,
            self.backup.object_count,
            self.backup.project_id,
            self.backup.size,
            self.backup.snapshot_id,
            self.backup.status,
            self.backup.updated_at,
            self.backup.user_id,
            self.backup.volume_id,
        )

        self.cmd = volume_backup.ShowVolumeBackup(self.app, None)

    def test_backup_show(self):
        arglist = [self.backup.id]
        verifylist = [("backup", self.backup.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.find_backup.assert_called_with(
            self.backup.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
