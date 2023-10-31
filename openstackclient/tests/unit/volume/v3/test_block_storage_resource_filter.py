# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

from cinderclient import api_versions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_resource_filter


class TestBlockStorageResourceFilter(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        patcher = mock.patch.object(
            sdk_utils, 'supports_microversion', return_value=True
        )
        self.addCleanup(patcher.stop)
        self.supports_microversion_mock = patcher.start()
        self._set_mock_microversion(
            self.app.client_manager.volume.api_version.get_string()
        )

    def _set_mock_microversion(self, mock_v):
        """Set a specific microversion for the mock supports_microversion()."""
        self.supports_microversion_mock.reset_mock(return_value=True)
        self.supports_microversion_mock.side_effect = (
            lambda _, v: api_versions.APIVersion(v)
            <= api_versions.APIVersion(mock_v)
        )


class TestBlockStorageResourceFilterList(TestBlockStorageResourceFilter):
    # The resource filters to be listed
    fake_resource_filters = volume_fakes.create_resource_filters()

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.resource_filters.return_value = (
            self.fake_resource_filters
        )

        # Get the command object to test
        self.cmd = (
            block_storage_resource_filter.ListBlockStorageResourceFilter(
                self.app, None
            )
        )

    def test_resource_filter_list(self):
        self._set_mock_microversion('3.33')

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('Resource', 'Filters')
        expected_data = tuple(
            (
                resource_filter.resource,
                format_columns.ListColumn(resource_filter.filters),
            )
            for resource_filter in self.fake_resource_filters
        )
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        # checking if proper call was made to list clusters
        self.volume_sdk_client.resource_filters.assert_called_with()

    def test_resource_filter_list_pre_v333(self):
        self._set_mock_microversion('3.32')

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.33 or greater is required', str(exc)
        )


class TestBlockStorageResourceFilterShow(TestBlockStorageResourceFilter):
    # The resource filters to be listed
    fake_resource_filter = volume_fakes.create_one_resource_filter()

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.resource_filters.return_value = iter(
            [self.fake_resource_filter]
        )

        # Get the command object to test
        self.cmd = (
            block_storage_resource_filter.ShowBlockStorageResourceFilter(
                self.app, None
            )
        )

    def test_resource_filter_show(self):
        self._set_mock_microversion('3.33')

        arglist = [
            self.fake_resource_filter.resource,
        ]
        verifylist = [
            ('resource', self.fake_resource_filter.resource),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('Resource', 'Filters')
        expected_data = (
            self.fake_resource_filter.resource,
            format_columns.ListColumn(self.fake_resource_filter.filters),
        )
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)

        # checking if proper call was made to list clusters
        self.volume_sdk_client.resource_filters.assert_called_with(
            resource='volume'
        )

    def test_resource_filter_show_pre_v333(self):
        self._set_mock_microversion('3.32')

        arglist = [
            self.fake_resource_filter.resource,
        ]
        verifylist = [
            ('resource', self.fake_resource_filter.resource),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.33 or greater is required', str(exc)
        )
