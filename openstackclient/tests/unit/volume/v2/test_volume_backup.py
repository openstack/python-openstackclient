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

import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_backup


class TestBackup(volume_fakes.TestVolume):

    def setUp(self):
        super(TestBackup, self).setUp()

        self.backups_mock = self.app.client_manager.volume.backups
        self.backups_mock.reset_mock()
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()
        self.snapshots_mock = self.app.client_manager.volume.volume_snapshots
        self.snapshots_mock.reset_mock()
        self.restores_mock = self.app.client_manager.volume.restores
        self.restores_mock.reset_mock()


class TestBackupCreate(TestBackup):

    volume = volume_fakes.FakeVolume.create_one_volume()
    snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()
    new_backup = volume_fakes.FakeBackup.create_one_backup(
        attrs={'volume_id': volume.id, 'snapshot_id': snapshot.id})

    columns = (
        'availability_zone',
        'container',
        'description',
        'id',
        'name',
        'object_count',
        'size',
        'snapshot_id',
        'status',
        'volume_id',
    )
    data = (
        new_backup.availability_zone,
        new_backup.container,
        new_backup.description,
        new_backup.id,
        new_backup.name,
        new_backup.object_count,
        new_backup.size,
        new_backup.snapshot_id,
        new_backup.status,
        new_backup.volume_id,
    )

    def setUp(self):
        super(TestBackupCreate, self).setUp()

        self.volumes_mock.get.return_value = self.volume
        self.snapshots_mock.get.return_value = self.snapshot
        self.backups_mock.create.return_value = self.new_backup

        # Get the command object to test
        self.cmd = volume_backup.CreateVolumeBackup(self.app, None)

    def test_backup_create(self):
        arglist = [
            "--name", self.new_backup.name,
            "--description", self.new_backup.description,
            "--container", self.new_backup.container,
            "--force",
            "--incremental",
            "--snapshot", self.new_backup.snapshot_id,
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

        self.backups_mock.create.assert_called_with(
            self.new_backup.volume_id,
            container=self.new_backup.container,
            name=self.new_backup.name,
            description=self.new_backup.description,
            force=True,
            incremental=True,
            snapshot_id=self.new_backup.snapshot_id,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_backup_create_without_name(self):
        arglist = [
            "--description", self.new_backup.description,
            "--container", self.new_backup.container,
            self.new_backup.volume_id,
        ]
        verifylist = [
            ("description", self.new_backup.description),
            ("container", self.new_backup.container),
            ("volume", self.new_backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.backups_mock.create.assert_called_with(
            self.new_backup.volume_id,
            container=self.new_backup.container,
            name=None,
            description=self.new_backup.description,
            force=False,
            incremental=False,
            snapshot_id=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestBackupDelete(TestBackup):

    backups = volume_fakes.FakeBackup.create_backups(count=2)

    def setUp(self):
        super(TestBackupDelete, self).setUp()

        self.backups_mock.get = (
            volume_fakes.FakeBackup.get_backups(self.backups))
        self.backups_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_backup.DeleteVolumeBackup(self.app, None)

    def test_backup_delete(self):
        arglist = [
            self.backups[0].id
        ]
        verifylist = [
            ("backups", [self.backups[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.backups_mock.delete.assert_called_with(
            self.backups[0].id, False)
        self.assertIsNone(result)

    def test_backup_delete_with_force(self):
        arglist = [
            '--force',
            self.backups[0].id,
        ]
        verifylist = [
            ('force', True),
            ("backups", [self.backups[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.backups_mock.delete.assert_called_with(self.backups[0].id, True)
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
            calls.append(call(b.id, False))
        self.backups_mock.delete.assert_has_calls(calls)
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
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 backups failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.backups_mock, self.backups[0].id)
            find_mock.assert_any_call(self.backups_mock, 'unexist_backup')

            self.assertEqual(2, find_mock.call_count)
            self.backups_mock.delete.assert_called_once_with(
                self.backups[0].id, False
            )


class TestBackupList(TestBackup):

    volume = volume_fakes.FakeVolume.create_one_volume()
    backups = volume_fakes.FakeBackup.create_backups(
        attrs={'volume_id': volume.name}, count=3)

    columns = [
        'ID',
        'Name',
        'Description',
        'Status',
        'Size',
    ]
    columns_long = columns + [
        'Availability Zone',
        'Volume',
        'Container',
    ]

    data = []
    for b in backups:
        data.append((
            b.id,
            b.name,
            b.description,
            b.status,
            b.size,
        ))
    data_long = []
    for b in backups:
        data_long.append((
            b.id,
            b.name,
            b.description,
            b.status,
            b.size,
            b.availability_zone,
            volume_backup.VolumeIdColumn(b.volume_id),
            b.container,
        ))

    def setUp(self):
        super(TestBackupList, self).setUp()

        self.volumes_mock.list.return_value = [self.volume]
        self.backups_mock.list.return_value = self.backups
        self.volumes_mock.get.return_value = self.volume
        self.backups_mock.get.return_value = self.backups[0]
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

        search_opts = {
            "name": None,
            "status": None,
            "volume_id": None,
            'all_tenants': False,
        }
        self.volumes_mock.get.assert_not_called()
        self.backups_mock.get.assert_not_called()
        self.backups_mock.list.assert_called_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_backup_list_with_options(self):
        arglist = [
            "--long",
            "--name", self.backups[0].name,
            "--status", "error",
            "--volume", self.volume.id,
            "--marker", self.backups[0].id,
            "--all-projects",
            "--limit", "3",
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

        search_opts = {
            "name": self.backups[0].name,
            "status": "error",
            "volume_id": self.volume.id,
            'all_tenants': True,
        }
        self.volumes_mock.get.assert_called_once_with(self.volume.id)
        self.backups_mock.get.assert_called_once_with(self.backups[0].id)
        self.backups_mock.list.assert_called_with(
            search_opts=search_opts,
            marker=self.backups[0].id,
            limit=3,
        )
        self.assertEqual(self.columns_long, columns)
        self.assertListItemEqual(self.data_long, list(data))


class TestBackupRestore(TestBackup):

    volume = volume_fakes.FakeVolume.create_one_volume()
    backup = volume_fakes.FakeBackup.create_one_backup(
        attrs={'volume_id': volume.id})

    def setUp(self):
        super(TestBackupRestore, self).setUp()

        self.backups_mock.get.return_value = self.backup
        self.volumes_mock.get.return_value = self.volume
        self.restores_mock.restore.return_value = (
            volume_fakes.FakeVolume.create_one_volume(
                {'id': self.volume['id']}))
        # Get the command object to mock
        self.cmd = volume_backup.RestoreVolumeBackup(self.app, None)

    def test_backup_restore(self):
        arglist = [
            self.backup.id,
            self.backup.volume_id
        ]
        verifylist = [
            ("backup", self.backup.id),
            ("volume", self.backup.volume_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.restores_mock.restore.assert_called_with(self.backup.id,
                                                      self.backup.volume_id)
        self.assertIsNotNone(result)


class TestBackupSet(TestBackup):

    backup = volume_fakes.FakeBackup.create_one_backup()

    def setUp(self):
        super(TestBackupSet, self).setUp()

        self.backups_mock.get.return_value = self.backup

        # Get the command object to test
        self.cmd = volume_backup.SetVolumeBackup(self.app, None)

    def test_backup_set_name(self):
        arglist = [
            '--name', 'new_name',
            self.backup.id,
        ]
        verifylist = [
            ('name', 'new_name'),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        result = self.cmd.take_action(parsed_args)
        self.backups_mock.update.assert_called_once_with(
            self.backup.id, **{'name': 'new_name'})
        self.assertIsNone(result)

    def test_backup_set_description(self):
        arglist = [
            '--description', 'new_description',
            self.backup.id,
        ]
        verifylist = [
            ('name', None),
            ('description', 'new_description'),
            ('backup', self.backup.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new_description'
        }
        self.backups_mock.update.assert_called_once_with(
            self.backup.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_backup_set_state(self):
        arglist = [
            '--state', 'error',
            self.backup.id
        ]
        verifylist = [
            ('state', 'error'),
            ('backup', self.backup.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.backups_mock.reset_state.assert_called_once_with(
            self.backup.id, 'error')
        self.assertIsNone(result)

    def test_backup_set_state_failed(self):
        self.backups_mock.reset_state.side_effect = exceptions.CommandError()
        arglist = [
            '--state', 'error',
            self.backup.id
        ]
        verifylist = [
            ('state', 'error'),
            ('backup', self.backup.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('One or more of the set operations failed',
                             str(e))
        self.backups_mock.reset_state.assert_called_with(
            self.backup.id, 'error')


class TestBackupShow(TestBackup):

    backup = volume_fakes.FakeBackup.create_one_backup()

    columns = (
        'availability_zone',
        'container',
        'description',
        'id',
        'name',
        'object_count',
        'size',
        'snapshot_id',
        'status',
        'volume_id',
    )
    data = (
        backup.availability_zone,
        backup.container,
        backup.description,
        backup.id,
        backup.name,
        backup.object_count,
        backup.size,
        backup.snapshot_id,
        backup.status,
        backup.volume_id,
    )

    def setUp(self):
        super(TestBackupShow, self).setUp()

        self.backups_mock.get.return_value = self.backup
        # Get the command object to test
        self.cmd = volume_backup.ShowVolumeBackup(self.app, None)

    def test_backup_show(self):
        arglist = [
            self.backup.id
        ]
        verifylist = [
            ("backup", self.backup.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.backups_mock.get.assert_called_with(self.backup.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
