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

from openstack.block_storage.v3 import backup as _backup
from openstack.test import fakes as sdk_fakes

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import backup_record


class TestBackupRecordExport(volume_fakes.TestVolume):
    fake_backup = sdk_fakes.generate_fake_resource(
        _backup.Backup,
        volume_id='a54708a2-0388-4476-a909-09579f885c25',
    )
    fake_record = {
        'backup-record': {
            'backup_service': 'cinder.backup.drivers.swift.SwiftBackupDriver',
            'backup_url': 'eyJzdGF0dXMiOiAiYXZh',
        },
    }

    def setUp(self):
        super().setUp()

        self.volume_client.find_backup.return_value = self.fake_backup
        self.volume_client.export_backup.return_value = self.fake_record

        self.cmd = backup_record.ExportBackupRecord(self.app, None)

    def test_backup_export_table(self):
        arglist = [self.fake_backup.name]
        verifylist = [("backup", self.fake_backup.name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        parsed_args.formatter = 'table'
        columns, __ = self.cmd.take_action(parsed_args)

        self.volume_client.find_backup.assert_called_once_with(
            self.fake_backup.name, ignore_missing=False
        )
        self.volume_client.export_backup.assert_called_once_with(
            self.fake_backup
        )
        self.assertEqual(('Backup Service', 'Metadata'), columns)

    def test_backup_export_json(self):
        arglist = [self.fake_backup.name]
        verifylist = [("backup", self.fake_backup.name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        parsed_args.formatter = 'json'
        columns, __ = self.cmd.take_action(parsed_args)

        self.volume_client.find_backup.assert_called_once_with(
            self.fake_backup.name, ignore_missing=False
        )
        self.volume_client.export_backup.assert_called_once_with(
            self.fake_backup
        )
        self.assertEqual(('backup_service', 'backup_url'), columns)


class TestBackupRecordImport(volume_fakes.TestVolume):
    fake_import = {
        'backup': {
            'id': 'backup.id',
            'name': 'backup.name',
        },
    }

    def setUp(self):
        super().setUp()

        self.volume_client.import_backup.return_value = self.fake_import

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

        self.volume_client.import_backup.assert_called_once_with(
            "cinder.backup.drivers.swift.SwiftBackupDriver",
            "fake_backup_record_data",
        )
        self.assertEqual(('backup',), columns)
