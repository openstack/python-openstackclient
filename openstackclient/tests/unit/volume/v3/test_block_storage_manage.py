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

from cinderclient import api_versions
from osc_lib import exceptions

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v2 import fakes as v2_volume_fakes
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_manage


class TestBlockStorageManage(v2_volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()
        self.snapshots_mock = self.app.client_manager.volume.volume_snapshots
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
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.8'
        )
        host = 'fake_host'
        arglist = [
            host,
        ]
        verifylist = [
            ('host', host),
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

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

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

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get volume manageable list
        self.volumes_mock.list_manageable.assert_called_with(
            host=parsed_args.host,
            detailed=parsed_args.detailed,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            offset=parsed_args.offset,
            sort=parsed_args.sort,
            cluster=parsed_args.cluster,
        )

    def test_block_storage_volume_manage_pre_38(self):
        host = 'fake_host'
        arglist = [
            host,
        ]
        verifylist = [
            ('host', host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.8 or greater is required', str(exc)
        )

    def test_block_storage_volume_manage_pre_317(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.16'
        )
        cluster = 'fake_cluster'
        arglist = [
            '--cluster',
            cluster,
        ]
        verifylist = [
            ('cluster', cluster),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.17 or greater is required', str(exc)
        )
        self.assertIn('--cluster', str(exc))

    def test_block_storage_volume_manage_host_and_cluster(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.17'
        )
        host = 'fake_host'
        cluster = 'fake_cluster'
        arglist = [
            host,
            '--cluster',
            cluster,
        ]
        verifylist = [
            ('host', host),
            ('cluster', cluster),
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

    def test_block_storage_volume_manage_list_all_args(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.8'
        )
        host = 'fake_host'
        detailed = True
        marker = 'fake_marker'
        limit = '5'
        offset = '3'
        sort = 'size:asc'
        arglist = [
            host,
            '--detailed',
            str(detailed),
            '--marker',
            marker,
            '--limit',
            limit,
            '--offset',
            offset,
            '--sort',
            sort,
        ]
        verifylist = [
            ('host', host),
            ('detailed', str(detailed)),
            ('marker', marker),
            ('limit', limit),
            ('offset', offset),
            ('sort', sort),
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

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

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

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get volume manageable list
        self.volumes_mock.list_manageable.assert_called_with(
            host=host,
            detailed=detailed,
            marker=marker,
            limit=limit,
            offset=offset,
            sort=sort,
            cluster=parsed_args.cluster,
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
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.8'
        )
        host = 'fake_host'
        arglist = [
            host,
        ]
        verifylist = [
            ('host', host),
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

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

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

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get snapshot manageable list
        self.snapshots_mock.list_manageable.assert_called_with(
            host=parsed_args.host,
            detailed=parsed_args.detailed,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            offset=parsed_args.offset,
            sort=parsed_args.sort,
            cluster=parsed_args.cluster,
        )

    def test_block_storage_volume_manage_pre_38(self):
        host = 'fake_host'
        arglist = [
            host,
        ]
        verifylist = [
            ('host', host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.8 or greater is required', str(exc)
        )

    def test_block_storage_volume_manage_pre_317(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.16'
        )
        cluster = 'fake_cluster'
        arglist = [
            '--cluster',
            cluster,
        ]
        verifylist = [
            ('cluster', cluster),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.17 or greater is required', str(exc)
        )
        self.assertIn('--cluster', str(exc))

    def test_block_storage_volume_manage_host_and_cluster(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.17'
        )
        host = 'fake_host'
        cluster = 'fake_cluster'
        arglist = [
            host,
            '--cluster',
            cluster,
        ]
        verifylist = [
            ('host', host),
            ('cluster', cluster),
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

    def test_block_storage_volume_manage_list_all_args(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.8'
        )
        host = 'fake_host'
        detailed = True
        marker = 'fake_marker'
        limit = '5'
        offset = '3'
        sort = 'size:asc'
        arglist = [
            host,
            '--detailed',
            str(detailed),
            '--marker',
            marker,
            '--limit',
            limit,
            '--offset',
            offset,
            '--sort',
            sort,
        ]
        verifylist = [
            ('host', host),
            ('detailed', str(detailed)),
            ('marker', marker),
            ('limit', limit),
            ('offset', offset),
            ('sort', sort),
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

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

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

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get snapshot manageable list
        self.snapshots_mock.list_manageable.assert_called_with(
            host=host,
            detailed=detailed,
            marker=marker,
            limit=limit,
            offset=offset,
            sort=sort,
            cluster=parsed_args.cluster,
        )
