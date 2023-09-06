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
from openstack.block_storage.v3 import block_storage_summary as _summary
from openstack.block_storage.v3 import snapshot as _snapshot
from openstack.block_storage.v3 import volume as _volume
from openstack.test import fakes as sdk_fakes
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes
from openstackclient.volume.v3 import volume


class BaseVolumeTest(fakes.TestVolume):
    def setUp(self):
        super().setUp()

        patcher = mock.patch.object(
            sdk_utils, 'supports_microversion', return_value=True
        )
        self.addCleanup(patcher.stop)
        self.supports_microversion_mock = patcher.start()
        self._set_mock_microversion(
            self.volume_client.api_version.get_string()
        )

    def _set_mock_microversion(self, mock_v):
        """Set a specific microversion for the mock supports_microversion()."""
        self.supports_microversion_mock.reset_mock(return_value=True)
        self.supports_microversion_mock.side_effect = (
            lambda _, v: api_versions.APIVersion(v)
            <= api_versions.APIVersion(mock_v)
        )


class TestVolumeSummary(BaseVolumeTest):
    columns = [
        'Total Count',
        'Total Size',
    ]

    def setUp(self):
        super().setUp()

        self.volume_a = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_b = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.summary = sdk_fakes.generate_fake_resource(
            _summary.BlockStorageSummary,
            total_count=2,
            total_size=self.volume_a.size + self.volume_b.size,
        )
        self.volume_sdk_client.summary.return_value = self.summary

        # Get the command object to test
        self.cmd = volume.VolumeSummary(self.app, None)

    def test_volume_summary(self):
        self._set_mock_microversion('3.12')
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.summary.assert_called_once_with(True)

        self.assertEqual(self.columns, columns)

        datalist = (2, self.volume_a.size + self.volume_b.size)
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
        self._set_mock_microversion('3.36')

        metadata = {**self.volume_a.metadata, **self.volume_b.metadata}
        self.summary = sdk_fakes.generate_fake_resource(
            _summary.BlockStorageSummary,
            total_count=2,
            total_size=self.volume_a.size + self.volume_b.size,
            metadata=metadata,
        )
        self.volume_sdk_client.summary.return_value = self.summary

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

        self.volume_sdk_client.summary.assert_called_once_with(True)

        self.assertEqual(new_cols, columns)

        datalist = (
            2,
            self.volume_a.size + self.volume_b.size,
            format_columns.DictColumn(metadata),
        )
        self.assertCountEqual(datalist, tuple(data))


class TestVolumeRevertToSnapshot(BaseVolumeTest):
    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.snapshot = sdk_fakes.generate_fake_resource(
            _snapshot.Snapshot,
            volume_id=self.volume.id,
        )
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.find_snapshot.return_value = self.snapshot

        # Get the command object to test
        self.cmd = volume.VolumeRevertToSnapshot(self.app, None)

    def test_volume_revert_to_snapshot_pre_340(self):
        arglist = [
            self.snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.snapshot.id),
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
            self.snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.volume_sdk_client.revert_volume_to_snapshot.assert_called_once_with(
            self.volume,
            self.snapshot,
        )
        self.volume_sdk_client.find_volume.assert_called_with(
            self.volume.id,
            ignore_missing=False,
        )
        self.volume_sdk_client.find_snapshot.assert_called_with(
            self.snapshot.id,
            ignore_missing=False,
        )
