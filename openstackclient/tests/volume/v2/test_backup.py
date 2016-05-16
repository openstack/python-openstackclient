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

from openstackclient.tests.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import backup


class TestBackup(volume_fakes.TestVolume):

    def setUp(self):
        super(TestBackup, self).setUp()

        self.backups_mock = self.app.client_manager.volume.backups
        self.backups_mock.reset_mock()
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()
        self.restores_mock = self.app.client_manager.volume.restores
        self.restores_mock.reset_mock()


class TestBackupCreate(TestBackup):

    volume = volume_fakes.FakeVolume.create_one_volume()
    new_backup = volume_fakes.FakeBackup.create_one_backup(
        attrs={'volume_id': volume.id})

    columns = (
        'availability_zone',
        'container',
        'description',
        'id',
        'name',
        'object_count',
        'size',
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
        new_backup.status,
        new_backup.volume_id,
    )

    def setUp(self):
        super(TestBackupCreate, self).setUp()

        self.volumes_mock.get.return_value = self.volume
        self.backups_mock.create.return_value = self.new_backup

        # Get the command object to test
        self.cmd = backup.CreateBackup(self.app, None)

    def test_backup_create(self):
        arglist = [
            "--name", self.new_backup.name,
            "--description", self.new_backup.description,
            "--container", self.new_backup.container,
            self.new_backup.volume_id,
        ]
        verifylist = [
            ("name", self.new_backup.name),
            ("description", self.new_backup.description),
            ("container", self.new_backup.container),
            ("volume", self.new_backup.volume_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.backups_mock.create.assert_called_with(
            self.new_backup.volume_id,
            container=self.new_backup.container,
            name=self.new_backup.name,
            description=self.new_backup.description
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
            description=self.new_backup.description
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestBackupDelete(TestBackup):

    backup = volume_fakes.FakeBackup.create_one_backup()

    def setUp(self):
        super(TestBackupDelete, self).setUp()

        self.backups_mock.get.return_value = self.backup
        self.backups_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = backup.DeleteBackup(self.app, None)

    def test_backup_delete(self):
        arglist = [
            self.backup.id
        ]
        verifylist = [
            ("backups", [self.backup.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.backups_mock.delete.assert_called_with(self.backup.id)
        self.assertIsNone(result)


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
            b.volume_id,
            b.container,
        ))

    def setUp(self):
        super(TestBackupList, self).setUp()

        self.volumes_mock.list.return_value = [self.volume]
        self.backups_mock.list.return_value = self.backups
        # Get the command to test
        self.cmd = backup.ListBackup(self.app, None)

    def test_backup_list_without_options(self):
        arglist = []
        verifylist = [("long", False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_backup_list_with_options(self):
        arglist = ["--long"]
        verifylist = [("long", True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestBackupRestore(TestBackup):

    volume = volume_fakes.FakeVolume.create_one_volume()
    backup = volume_fakes.FakeBackup.create_one_backup(
        attrs={'volume_id': volume.id})

    def setUp(self):
        super(TestBackupRestore, self).setUp()

        self.backups_mock.get.return_value = self.backup
        self.volumes_mock.get.return_value = self.volume
        self.restores_mock.restore.return_value = None
        # Get the command object to mock
        self.cmd = backup.RestoreBackup(self.app, None)

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
        self.assertIsNone(result)


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
        backup.status,
        backup.volume_id,
    )

    def setUp(self):
        super(TestBackupShow, self).setUp()

        self.backups_mock.get.return_value = self.backup
        # Get the command object to test
        self.cmd = backup.ShowBackup(self.app, None)

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
