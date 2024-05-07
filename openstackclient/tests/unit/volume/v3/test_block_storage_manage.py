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

from osc_lib import exceptions

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_manage


class TestBlockStorageManage(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()
        self.snapshots_mock = self.volume_client.volume_snapshots
        self.snapshots_mock.reset_mock()


class TestBlockStorageVolumeManage(TestBlockStorageManage):
    volume_manage_list = volume_fakes.create_volume_manage_list_records()

    def setUp(self):
        super().setUp()

        self.volumes_mock.list_manageable.return_value = (
            self.volume_manage_list
        )

        # Get the command object to test
        self.cmd = block_storage_manage.BlockStorageManageVolumes(
            self.app, None
        )

    def test_block_storage_volume_manage_list(self):
        self.set_volume_api_version('3.8')

        arglist = [
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
        ]
        datalist = []
        for volume_record in self.volume_manage_list:
            manage_details = (
                volume_record.reference,
                volume_record.size,
                volume_record.safe_to_manage,
            )
            datalist.append(manage_details)
        datalist = tuple(datalist)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get volume manageable list
        self.volumes_mock.list_manageable.assert_called_with(
            host='fake_host',
            detailed=False,
            marker=None,
            limit=None,
            offset=None,
            sort=None,
            cluster=None,
        )

    def test_block_storage_volume_manage_list__pre_v38(self):
        self.set_volume_api_version('3.7')

        arglist = [
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.8 or greater is required', str(exc)
        )

    def test_block_storage_volume_manage_list__pre_v317(self):
        self.set_volume_api_version('3.16')

        arglist = [
            '--cluster',
            'fake_cluster',
        ]
        verifylist = [
            ('cluster', 'fake_cluster'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.17 or greater is required', str(exc)
        )
        self.assertIn('--cluster', str(exc))

    def test_block_storage_volume_manage_list__host_and_cluster(self):
        self.set_volume_api_version('3.17')

        arglist = [
            'fake_host',
            '--cluster',
            'fake_cluster',
        ]
        verifylist = [
            ('host', 'fake_host'),
            ('cluster', 'fake_cluster'),
        ]
        exc = self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertIn(
            'argument --cluster: not allowed with argument <host>', str(exc)
        )

    def test_block_storage_volume_manage_list__detailed(self):
        """This option is deprecated."""
        self.set_volume_api_version('3.8')

        arglist = [
            '--detailed',
            'True',
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
            ('detailed', 'True'),
            ('marker', None),
            ('limit', None),
            ('offset', None),
            ('sort', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
            'reason_not_safe',
            'cinder_id',
            'extra_info',
        ]
        datalist = []
        for volume_record in self.volume_manage_list:
            manage_details = (
                volume_record.reference,
                volume_record.size,
                volume_record.safe_to_manage,
                volume_record.reason_not_safe,
                volume_record.cinder_id,
                volume_record.extra_info,
            )
            datalist.append(manage_details)
        datalist = tuple(datalist)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get volume manageable list
        self.volumes_mock.list_manageable.assert_called_with(
            host='fake_host',
            detailed=True,
            marker=None,
            limit=None,
            offset=None,
            sort=None,
            cluster=None,
        )
        mock_warning.assert_called_once()
        self.assertIn(
            "The --detailed option has been deprecated.",
            str(mock_warning.call_args[0][0]),
        )

    def test_block_storage_volume_manage_list__all_args(self):
        self.set_volume_api_version('3.8')

        arglist = [
            'fake_host',
            '--long',
            '--marker',
            'fake_marker',
            '--limit',
            '5',
            '--offset',
            '3',
            '--sort',
            'size:asc',
        ]
        verifylist = [
            ('host', 'fake_host'),
            ('detailed', None),
            ('long', True),
            ('marker', 'fake_marker'),
            ('limit', '5'),
            ('offset', '3'),
            ('sort', 'size:asc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
            'reason_not_safe',
            'cinder_id',
            'extra_info',
        ]
        datalist = []
        for volume_record in self.volume_manage_list:
            manage_details = (
                volume_record.reference,
                volume_record.size,
                volume_record.safe_to_manage,
                volume_record.reason_not_safe,
                volume_record.cinder_id,
                volume_record.extra_info,
            )
            datalist.append(manage_details)
        datalist = tuple(datalist)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get volume manageable list
        self.volumes_mock.list_manageable.assert_called_with(
            host='fake_host',
            detailed=True,
            marker='fake_marker',
            limit='5',
            offset='3',
            sort='size:asc',
            cluster=None,
        )


class TestBlockStorageSnapshotManage(TestBlockStorageManage):
    snapshot_manage_list = volume_fakes.create_snapshot_manage_list_records()

    def setUp(self):
        super().setUp()

        self.snapshots_mock.list_manageable.return_value = (
            self.snapshot_manage_list
        )

        # Get the command object to test
        self.cmd = block_storage_manage.BlockStorageManageSnapshots(
            self.app, None
        )

    def test_block_storage_snapshot_manage_list(self):
        self.set_volume_api_version('3.8')

        arglist = [
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
            'source_reference',
        ]
        datalist = []
        for snapshot_record in self.snapshot_manage_list:
            manage_details = (
                snapshot_record.reference,
                snapshot_record.size,
                snapshot_record.safe_to_manage,
                snapshot_record.source_reference,
            )
            datalist.append(manage_details)
        datalist = tuple(datalist)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get snapshot manageable list
        self.snapshots_mock.list_manageable.assert_called_with(
            host='fake_host',
            detailed=False,
            marker=None,
            limit=None,
            offset=None,
            sort=None,
            cluster=None,
        )

    def test_block_storage_snapshot_manage_list__pre_v38(self):
        self.set_volume_api_version('3.7')

        arglist = [
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.8 or greater is required', str(exc)
        )

    def test_block_storage_snapshot_manage_list__pre_v317(self):
        self.set_volume_api_version('3.16')

        arglist = [
            '--cluster',
            'fake_cluster',
        ]
        verifylist = [
            ('cluster', 'fake_cluster'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.17 or greater is required', str(exc)
        )
        self.assertIn('--cluster', str(exc))

    def test_block_storage_snapshot_manage_list__host_and_cluster(self):
        self.set_volume_api_version('3.17')

        arglist = [
            'fake_host',
            '--cluster',
            'fake_cluster',
        ]
        verifylist = [
            ('host', 'fake_host'),
            ('cluster', 'fake_cluster'),
        ]
        exc = self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertIn(
            'argument --cluster: not allowed with argument <host>', str(exc)
        )

    def test_block_storage_snapshot_manage_list__detailed(self):
        self.set_volume_api_version('3.8')

        arglist = [
            '--detailed',
            'True',
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
            ('detailed', 'True'),
            ('marker', None),
            ('limit', None),
            ('offset', None),
            ('sort', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
            'source_reference',
            'reason_not_safe',
            'cinder_id',
            'extra_info',
        ]
        datalist = []
        for snapshot_record in self.snapshot_manage_list:
            manage_details = (
                snapshot_record.reference,
                snapshot_record.size,
                snapshot_record.safe_to_manage,
                snapshot_record.source_reference,
                snapshot_record.reason_not_safe,
                snapshot_record.cinder_id,
                snapshot_record.extra_info,
            )
            datalist.append(manage_details)
        datalist = tuple(datalist)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get snapshot manageable list
        self.snapshots_mock.list_manageable.assert_called_with(
            host='fake_host',
            detailed=True,
            marker=None,
            limit=None,
            offset=None,
            sort=None,
            cluster=None,
        )
        mock_warning.assert_called_once()
        self.assertIn(
            "The --detailed option has been deprecated.",
            str(mock_warning.call_args[0][0]),
        )

    def test_block_storage_snapshot_manage_list__all_args(self):
        self.set_volume_api_version('3.8')

        arglist = [
            '--long',
            '--marker',
            'fake_marker',
            '--limit',
            '5',
            '--offset',
            '3',
            '--sort',
            'size:asc',
            'fake_host',
        ]
        verifylist = [
            ('host', 'fake_host'),
            ('detailed', None),
            ('long', True),
            ('marker', 'fake_marker'),
            ('limit', '5'),
            ('offset', '3'),
            ('sort', 'size:asc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
            'source_reference',
            'reason_not_safe',
            'cinder_id',
            'extra_info',
        ]
        datalist = []
        for snapshot_record in self.snapshot_manage_list:
            manage_details = (
                snapshot_record.reference,
                snapshot_record.size,
                snapshot_record.safe_to_manage,
                snapshot_record.source_reference,
                snapshot_record.reason_not_safe,
                snapshot_record.cinder_id,
                snapshot_record.extra_info,
            )
            datalist.append(manage_details)
        datalist = tuple(datalist)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get snapshot manageable list
        self.snapshots_mock.list_manageable.assert_called_with(
            host='fake_host',
            detailed=True,
            marker='fake_marker',
            limit='5',
            offset='3',
            sort='size:asc',
            cluster=None,
        )
