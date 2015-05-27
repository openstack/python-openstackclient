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
