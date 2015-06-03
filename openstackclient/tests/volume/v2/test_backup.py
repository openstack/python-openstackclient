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

from openstackclient.tests import fakes
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
    def setUp(self):
        super(TestBackupCreate, self).setUp()

        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True
        )

        self.backups_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.BACKUP),
            loaded=True
        )
        # Get the command object to test
        self.cmd = backup.CreateBackup(self.app, None)

    def test_backup_create(self):
        arglist = [
            volume_fakes.volume_id,
            "--name", volume_fakes.backup_name,
            "--description", volume_fakes.backup_description,
            "--container", volume_fakes.backup_name
        ]
        verifylist = [
            ("volume", volume_fakes.volume_id),
            ("name", volume_fakes.backup_name),
            ("description", volume_fakes.backup_description),
            ("container", volume_fakes.backup_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.backups_mock.create.assert_called_with(
            volume_fakes.volume_id,
            container=volume_fakes.backup_name,
            name=volume_fakes.backup_name,
            description=volume_fakes.backup_description
        )
        self.assertEqual(columns, volume_fakes.BACKUP_columns)
        self.assertEqual(data, volume_fakes.BACKUP_data)


class TestBackupShow(TestBackup):
    def setUp(self):
        super(TestBackupShow, self).setUp()

        self.backups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.BACKUP),
            loaded=True)
        # Get the command object to test
        self.cmd = backup.ShowBackup(self.app, None)

    def test_backup_show(self):
        arglist = [
            volume_fakes.backup_id
        ]
        verifylist = [
            ("backup", volume_fakes.backup_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.backups_mock.get.assert_called_with(volume_fakes.backup_id)

        self.assertEqual(volume_fakes.BACKUP_columns, columns)
        self.assertEqual(volume_fakes.BACKUP_data, data)


class TestBackupDelete(TestBackup):
    def setUp(self):
        super(TestBackupDelete, self).setUp()

        self.backups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.BACKUP),
            loaded=True)
        self.backups_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = backup.DeleteBackup(self.app, None)

    def test_backup_delete(self):
        arglist = [
            volume_fakes.backup_id
        ]
        verifylist = [
            ("backups", [volume_fakes.backup_id])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.backups_mock.delete.assert_called_with(volume_fakes.backup_id)


class TestBackupRestore(TestBackup):
    def setUp(self):
        super(TestBackupRestore, self).setUp()

        self.backups_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.BACKUP),
            loaded=True
        )
        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True
        )
        self.restores_mock.restore.return_value = None
        # Get the command object to mock
        self.cmd = backup.RestoreBackup(self.app, None)

    def test_backup_restore(self):
        arglist = [
            volume_fakes.backup_id,
            volume_fakes.volume_id
        ]
        verifylist = [
            ("backup", volume_fakes.backup_id),
            ("volume", volume_fakes.volume_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.restores_mock.restore.assert_called_with(volume_fakes.backup_id,
                                                      volume_fakes.volume_id)


class TestBackupList(TestBackup):
    def setUp(self):
        super(TestBackupList, self).setUp()

        self.volumes_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(volume_fakes.VOLUME),
                loaded=True
            )
        ]
        self.backups_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(volume_fakes.BACKUP),
                loaded=True
            )
        ]
        # Get the command to test
        self.cmd = backup.ListBackup(self.app, None)

    def test_backup_list_without_options(self):
        arglist = []
        verifylist = [("long", False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        collist = ['ID', 'Name', 'Description', 'Status', 'Size']
        self.assertEqual(collist, columns)

        datalist = ((
            volume_fakes.backup_id,
            volume_fakes.backup_name,
            volume_fakes.backup_description,
            volume_fakes.backup_status,
            volume_fakes.backup_size
        ),)
        self.assertEqual(datalist, tuple(data))

    def test_backup_list_with_options(self):
        arglist = ["--long"]
        verifylist = [("long", True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        collist = ['ID', 'Name', 'Description', 'Status', 'Size',
                   'Availability Zone', 'Volume', 'Container']
        self.assertEqual(collist, columns)

        datalist = ((
            volume_fakes.backup_id,
            volume_fakes.backup_name,
            volume_fakes.backup_description,
            volume_fakes.backup_status,
            volume_fakes.backup_size,
            volume_fakes.volume_availability_zone,
            volume_fakes.backup_volume_id,
            volume_fakes.backup_container
        ),)
        self.assertEqual(datalist, tuple(data))
