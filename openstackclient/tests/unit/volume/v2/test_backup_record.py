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

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import backup_record


class TestBackupRecord(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.backups_mock = self.volume_client.backups
        self.backups_mock.reset_mock()


class TestBackupRecordExport(TestBackupRecord):
    new_backup = volume_fakes.create_one_backup(
        attrs={'volume_id': 'a54708a2-0388-4476-a909-09579f885c25'},
    )
    new_record = volume_fakes.create_backup_record()

    def setUp(self):
        super().setUp()

        self.backups_mock.export_record.return_value = self.new_record
        self.backups_mock.get.return_value = self.new_backup

        # Get the command object to mock
        self.cmd = backup_record.ExportBackupRecord(self.app, None)

    def test_backup_export_table(self):
        arglist = [
            self.new_backup.name,
        ]
        verifylist = [
            ("backup", self.new_backup.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        parsed_args.formatter = 'table'
        columns, __ = self.cmd.take_action(parsed_args)

        self.backups_mock.export_record.assert_called_with(
            self.new_backup.id,
        )

        expected_columns = ('Backup Service', 'Metadata')
        self.assertEqual(columns, expected_columns)

    def test_backup_export_json(self):
        arglist = [
            self.new_backup.name,
        ]
        verifylist = [
            ("backup", self.new_backup.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        parsed_args.formatter = 'json'
        columns, __ = self.cmd.take_action(parsed_args)

        self.backups_mock.export_record.assert_called_with(
            self.new_backup.id,
        )

        expected_columns = ('backup_service', 'backup_url')
        self.assertEqual(columns, expected_columns)


class TestBackupRecordImport(TestBackupRecord):
    new_backup = volume_fakes.create_one_backup(
        attrs={'volume_id': 'a54708a2-0388-4476-a909-09579f885c25'},
    )
    new_import = volume_fakes.import_backup_record()

    def setUp(self):
        super().setUp()

        self.backups_mock.import_record.return_value = self.new_import

        # Get the command object to mock
        self.cmd = backup_record.ImportBackupRecord(self.app, None)

    def test_backup_import(self):
        arglist = [
            "cinder.backup.drivers.swift.SwiftBackupDriver",
            "fake_backup_record_data",
        ]
        verifylist = [
            (
                "backup_service",
                "cinder.backup.drivers.swift.SwiftBackupDriver",
            ),
            ("backup_metadata", "fake_backup_record_data"),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, __ = self.cmd.take_action(parsed_args)

        self.backups_mock.import_record.assert_called_with(
            "cinder.backup.drivers.swift.SwiftBackupDriver",
            "fake_backup_record_data",
        )
        self.assertEqual(columns, ('backup',))
