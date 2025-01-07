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

from unittest.mock import call

from osc_lib import exceptions

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_backup


class TestBackupLegacy(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.backups_mock = self.volume_client.backups
        self.backups_mock.reset_mock()
        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()
        self.snapshots_mock = self.volume_client.volume_snapshots
        self.snapshots_mock.reset_mock()
        self.restores_mock = self.volume_client.restores
        self.restores_mock.reset_mock()


class TestBackupCreate(volume_fakes.TestVolume):
    volume = volume_fakes.create_one_volume()
    snapshot = volume_fakes.create_one_snapshot()
    new_backup = volume_fakes.create_one_backup(
        attrs={'volume_id': volume.id, 'snapshot_id': snapshot.id}
    )

    columns = (
        'id',
        'name',
        'volume_id',
    )
    data = (
        new_backup.id,
        new_backup.name,
        new_backup.volume_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.find_snapshot.return_value = self.snapshot
        self.volume_sdk_client.create_backup.return_value = self.new_backup

        # Get the command object to test
        self.cmd = volume_backup.CreateVolumeBackup(self.app, None)

    def test_backup_create(self):
        arglist = [
            "--name",
            self.new_backup.name,
            "--description",
            self.new_backup.description,
            "--container",
            self.new_backup.container,
            "--force",
            "--incremental",
            "--snapshot",
            self.new_backup.snapshot_id,
            self.new_backup.volume_id,
        ]
        verifylist = [
            ("name", self.new_backup.name),
            ("description", self.new_backup.description),
            ("container", self.new_backup.container),
            ("force", True),
            ("incremental", True),
            ("snapshot", self.new_backup.snapshot_id),
            ("volume", self.new_backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_backup.assert_called_with(
            volume_id=self.new_backup.volume_id,
            container=self.new_backup.container,
            name=self.new_backup.name,
            description=self.new_backup.description,
            force=True,
            is_incremental=True,
            snapshot_id=self.new_backup.snapshot_id,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_create_without_name(self):
        arglist = [
            "--description",
            self.new_backup.description,
            "--container",
            self.new_backup.container,
            self.new_backup.volume_id,
        ]
        verifylist = [
            ("description", self.new_backup.description),
            ("container", self.new_backup.container),
            ("volume", self.new_backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_backup.assert_called_with(
            volume_id=self.new_backup.volume_id,
            container=self.new_backup.container,
            name=None,
            description=self.new_backup.description,
            force=False,
            is_incremental=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestBackupDelete(volume_fakes.TestVolume):
    backups = volume_fakes.create_backups(count=2)

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_backup = volume_fakes.get_backups(
            self.backups
        )
        self.volume_sdk_client.delete_backup.return_value = None

        # Get the command object to mock
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
            calls.append(call(b.id, ignore_missing=False, force=False))
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
    volume = volume_fakes.create_one_volume()
    backups = volume_fakes.create_backups(
        attrs={'volume_id': volume.name}, count=3
    )

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

    data = []
    for b in backups:
        data.append(
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
    data_long = []
    for b in backups:
        data_long.append(
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

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.volumes.return_value = [self.volume]
        self.volume_sdk_client.backups.return_value = self.backups
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.find_backup.return_value = self.backups[0]

        # Get the command to test
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
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_backup_list_with_options(self):
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
        ]
        verifylist = [
            ("long", True),
            ("name", self.backups[0].name),
            ("status", "error"),
            ("volume", self.volume.id),
            ("marker", self.backups[0].id),
            ('all_projects', True),
            ("limit", 3),
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
        )
        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, list(data))


class TestBackupRestore(volume_fakes.TestVolume):
    volume = volume_fakes.create_one_volume()
    backup = volume_fakes.create_one_backup(
        attrs={'volume_id': volume.id},
    )

    columns = (
        "id",
        "volume_id",
        "volume_name",
    )

    data = (
        backup.id,
        volume.id,
        volume.name,
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_backup.return_value = self.backup
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.restore_backup.return_value = {
            'id': self.backup['id'],
            'volume_id': self.volume['id'],
            'volume_name': self.volume['name'],
        }

        # Get the command object to mock
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


class TestBackupSet(TestBackupLegacy):
    backup = volume_fakes.create_one_backup(
        attrs={'metadata': {'wow': 'cool'}},
    )

    def setUp(self):
        super().setUp()

        self.backups_mock.get.return_value = self.backup

        # Get the command object to test
        self.cmd = volume_backup.SetVolumeBackup(self.app, None)

    def test_backup_set_state(self):
        arglist = ['--state', 'error', self.backup.id]
        verifylist = [('state', 'error'), ('backup', self.backup.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.backups_mock.reset_state.assert_called_once_with(
            self.backup.id, 'error'
        )
        self.assertIsNone(result)

    def test_backup_set_state_failed(self):
        self.backups_mock.reset_state.side_effect = exceptions.CommandError()
        arglist = ['--state', 'error', self.backup.id]
        verifylist = [('state', 'error'), ('backup', self.backup.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'One or more of the set operations failed', str(e)
            )
        self.backups_mock.reset_state.assert_called_with(
            self.backup.id, 'error'
        )


class TestBackupShow(volume_fakes.TestVolume):
    backup = volume_fakes.create_one_backup()

    columns = (
        "availability_zone",
        "container",
        "created_at",
        "data_timestamp",
        "description",
        "fail_reason",
        "has_dependent_backups",
        "id",
        "is_incremental",
        "name",
        "object_count",
        "size",
        "snapshot_id",
        "status",
        "updated_at",
        "volume_id",
    )
    data = (
        backup.availability_zone,
        backup.container,
        backup.created_at,
        backup.data_timestamp,
        backup.description,
        backup.fail_reason,
        backup.has_dependent_backups,
        backup.id,
        backup.is_incremental,
        backup.name,
        backup.object_count,
        backup.size,
        backup.snapshot_id,
        backup.status,
        backup.updated_at,
        backup.volume_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_backup.return_value = self.backup
        # Get the command object to test
        self.cmd = volume_backup.ShowVolumeBackup(self.app, None)

    def test_backup_show(self):
        arglist = [self.backup.id]
        verifylist = [("backup", self.backup.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.find_backup.assert_called_with(self.backup.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
