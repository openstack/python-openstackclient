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
from unittest import mock

from cinderclient import api_versions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v3 import volume


class TestVolumeSummary(volume_fakes.TestVolume):
    columns = [
        'Total Count',
        'Total Size',
    ]

    def setUp(self):
        super().setUp()

        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()
        self.mock_vol_1 = volume_fakes.create_one_volume()
        self.mock_vol_2 = volume_fakes.create_one_volume()
        self.return_dict = {
            'volume-summary': {
                'total_count': 2,
                'total_size': self.mock_vol_1.size + self.mock_vol_2.size,
            }
        }
        self.volumes_mock.summary.return_value = self.return_dict

        # Get the command object to test
        self.cmd = volume.VolumeSummary(self.app, None)

    def test_volume_summary(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.12'
        )
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.summary.assert_called_once_with(
            all_tenants=True,
        )

        self.assertEqual(self.columns, columns)

        datalist = (2, self.mock_vol_1.size + self.mock_vol_2.size)
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_summary_pre_312(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.12 or greater is required', str(exc)
        )

    def test_volume_summary_with_metadata(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.36'
        )

        combine_meta = {**self.mock_vol_1.metadata, **self.mock_vol_2.metadata}
        meta_dict = copy.deepcopy(self.return_dict)
        meta_dict['volume-summary']['metadata'] = combine_meta
        self.volumes_mock.summary.return_value = meta_dict

        new_cols = copy.deepcopy(self.columns)
        new_cols.extend(['Metadata'])

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.summary.assert_called_once_with(
            all_tenants=True,
        )

        self.assertEqual(new_cols, columns)

        datalist = (
            2,
            self.mock_vol_1.size + self.mock_vol_2.size,
            format_columns.DictColumn(combine_meta),
        )
        self.assertCountEqual(datalist, tuple(data))


class TestVolumeRevertToSnapshot(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.app.client_manager.sdk_connection = mock.Mock()
        self.app.client_manager.sdk_connection.volume = mock.Mock()
        self.sdk_client = self.app.client_manager.sdk_connection.volume
        self.sdk_client.reset_mock()

        patcher = mock.patch.object(
            sdk_utils, 'supports_microversion', return_value=True
        )
        self.addCleanup(patcher.stop)
        self.supports_microversion_mock = patcher.start()
        self._set_mock_microversion(
            self.app.client_manager.volume.api_version.get_string()
        )

        self.mock_volume = volume_fakes.create_one_volume()
        self.mock_snapshot = volume_fakes.create_one_snapshot(
            attrs={'volume_id': self.mock_volume.id}
        )

        # Get the command object to test
        self.cmd = volume.VolumeRevertToSnapshot(self.app, None)

    def _set_mock_microversion(self, mock_v):
        """Set a specific microversion for the mock supports_microversion()."""
        self.supports_microversion_mock.reset_mock(return_value=True)
        self.supports_microversion_mock.side_effect = (
            lambda _, v: api_versions.APIVersion(v)
            <= api_versions.APIVersion(mock_v)
        )

    def test_volume_revert_to_snapshot_pre_340(self):
        arglist = [
            self.mock_snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.mock_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.40 or greater is required', str(exc)
        )

    def test_volume_revert_to_snapshot(self):
        self._set_mock_microversion('3.40')
        arglist = [
            self.mock_snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.mock_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(
            self.sdk_client, 'find_volume', return_value=self.mock_volume
        ), mock.patch.object(
            self.sdk_client, 'find_snapshot', return_value=self.mock_snapshot
        ):
            self.cmd.take_action(parsed_args)

            self.sdk_client.revert_volume_to_snapshot.assert_called_once_with(
                self.mock_volume,
                self.mock_snapshot,
            )
            self.sdk_client.find_volume.assert_called_with(
                self.mock_volume.id,
                ignore_missing=False,
            )
            self.sdk_client.find_snapshot.assert_called_with(
                self.mock_snapshot.id,
                ignore_missing=False,
            )
