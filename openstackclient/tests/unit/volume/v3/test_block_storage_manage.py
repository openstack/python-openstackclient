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

from openstack.block_storage.v3 import (
    manageable_snapshot as _manageable_snapshot,
)
from openstack.block_storage.v3 import manageable_volume as _manageable_volume
from osc_lib import exceptions

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_manage

FAKE_VOLUME_MANAGE_LIST = [
    _manageable_volume.ManageableVolume(
        reference={'source-name': 'fake-volume'},
        size='1',
        safe_to_manage=False,
        reason_not_safe='already managed',
        cinder_id='fake-volume',
        extra_info=None,
    ),
    _manageable_volume.ManageableVolume(
        reference={'source-name': 'fake-volume'},
        size='2',
        safe_to_manage=False,
        reason_not_safe='already managed',
        cinder_id='fake-volume',
        extra_info=None,
    ),
]

FAKE_SNAPSHOT_MANAGE_LIST = [
    _manageable_snapshot.ManageableSnapshot(
        reference={'source-name': 'fake-snapshot'},
        source_reference={'source-name': 'fake-source'},
        size='1',
        safe_to_manage=False,
        reason_not_safe='already managed',
        cinder_id='fake-snapshot',
        extra_info=None,
    ),
    _manageable_snapshot.ManageableSnapshot(
        reference={'source-name': 'fake-snapshot'},
        source_reference={'source-name': 'fake-source'},
        size='2',
        safe_to_manage=False,
        reason_not_safe='already managed',
        cinder_id='fake-snapshot',
        extra_info=None,
    ),
]


class TestBlockStorageVolumeManage(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_sdk_client.manageable_volumes.return_value = iter(
            FAKE_VOLUME_MANAGE_LIST
        )

        self.cmd = block_storage_manage.BlockStorageManageVolumes(
            self.app, None
        )

    def test_block_storage_volume_manage_list(self):
        self.set_volume_api_version('3.8')

        arglist = ['fake_host']
        verifylist = [('host', 'fake_host')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = ['reference', 'size', 'safe_to_manage']
        expected_data = tuple(
            (v.reference, v.size, v.safe_to_manage)
            for v in FAKE_VOLUME_MANAGE_LIST
        )

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_sdk_client.manageable_volumes.assert_called_once_with(
            details=False, host='fake_host'
        )

    def test_block_storage_volume_manage_list__pre_v38(self):
        arglist = ['fake_host']
        verifylist = [('host', 'fake_host')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.8 or greater is required', str(exc)
        )

    def test_block_storage_volume_manage_list__pre_v317(self):
        self.set_volume_api_version('3.16')

        arglist = ['--cluster', 'fake_cluster']
        verifylist = [('cluster', 'fake_cluster')]
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

        arglist = ['fake_host', '--cluster', 'fake_cluster']
        verifylist = [('host', 'fake_host'), ('cluster', 'fake_cluster')]
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

        arglist = ['--detailed', 'True', 'fake_host']
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
        expected_data = tuple(
            (
                v.reference,
                v.size,
                v.safe_to_manage,
                v.reason_not_safe,
                v.cinder_id,
                v.extra_info,
            )
            for v in FAKE_VOLUME_MANAGE_LIST
        )

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_sdk_client.manageable_volumes.assert_called_once_with(
            details=True, host='fake_host'
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
        expected_data = tuple(
            (
                v.reference,
                v.size,
                v.safe_to_manage,
                v.reason_not_safe,
                v.cinder_id,
                v.extra_info,
            )
            for v in FAKE_VOLUME_MANAGE_LIST
        )

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_sdk_client.manageable_volumes.assert_called_once_with(
            details=True,
            host='fake_host',
            marker='fake_marker',
            limit='5',
            offset='3',
            sort='size:asc',
        )


class TestBlockStorageSnapshotManage(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_sdk_client.manageable_snapshots.return_value = iter(
            FAKE_SNAPSHOT_MANAGE_LIST
        )

        self.cmd = block_storage_manage.BlockStorageManageSnapshots(
            self.app, None
        )

    def test_block_storage_snapshot_manage_list(self):
        self.set_volume_api_version('3.8')

        arglist = ['fake_host']
        verifylist = [('host', 'fake_host')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'reference',
            'size',
            'safe_to_manage',
            'source_reference',
        ]
        expected_data = tuple(
            (s.reference, s.size, s.safe_to_manage, s.source_reference)
            for s in FAKE_SNAPSHOT_MANAGE_LIST
        )

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_sdk_client.manageable_snapshots.assert_called_once_with(
            details=False, host='fake_host'
        )

    def test_block_storage_snapshot_manage_list__pre_v38(self):
        arglist = ['fake_host']
        verifylist = [('host', 'fake_host')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.8 or greater is required', str(exc)
        )

    def test_block_storage_snapshot_manage_list__pre_v317(self):
        self.set_volume_api_version('3.16')

        arglist = ['--cluster', 'fake_cluster']
        verifylist = [('cluster', 'fake_cluster')]
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

        arglist = ['fake_host', '--cluster', 'fake_cluster']
        verifylist = [('host', 'fake_host'), ('cluster', 'fake_cluster')]
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

        arglist = ['--detailed', 'True', 'fake_host']
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
        expected_data = tuple(
            (
                s.reference,
                s.size,
                s.safe_to_manage,
                s.source_reference,
                s.reason_not_safe,
                s.cinder_id,
                s.extra_info,
            )
            for s in FAKE_SNAPSHOT_MANAGE_LIST
        )

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_sdk_client.manageable_snapshots.assert_called_once_with(
            details=True, host='fake_host'
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
        expected_data = tuple(
            (
                s.reference,
                s.size,
                s.safe_to_manage,
                s.source_reference,
                s.reason_not_safe,
                s.cinder_id,
                s.extra_info,
            )
            for s in FAKE_SNAPSHOT_MANAGE_LIST
        )

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_sdk_client.manageable_snapshots.assert_called_once_with(
            details=True,
            host='fake_host',
            marker='fake_marker',
            limit='5',
            offset='3',
            sort='size:asc',
        )
