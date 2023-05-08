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

from cinderclient import api_versions
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_group_snapshot


class TestVolumeGroupSnapshot(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_groups_mock = self.app.client_manager.volume.groups
        self.volume_groups_mock.reset_mock()

        self.volume_group_snapshots_mock = (
            self.app.client_manager.volume.group_snapshots
        )
        self.volume_group_snapshots_mock.reset_mock()


class TestVolumeGroupSnapshotCreate(TestVolumeGroupSnapshot):
    fake_volume_group = volume_fakes.create_one_volume_group()
    fake_volume_group_snapshot = (
        volume_fakes.create_one_volume_group_snapshot()
    )

    columns = (
        'ID',
        'Status',
        'Name',
        'Description',
        'Group',
        'Group Type',
    )
    data = (
        fake_volume_group_snapshot.id,
        fake_volume_group_snapshot.status,
        fake_volume_group_snapshot.name,
        fake_volume_group_snapshot.description,
        fake_volume_group_snapshot.group_id,
        fake_volume_group_snapshot.group_type_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_groups_mock.get.return_value = self.fake_volume_group
        self.volume_group_snapshots_mock.create.return_value = (
            self.fake_volume_group_snapshot
        )
        self.volume_group_snapshots_mock.get.return_value = (
            self.fake_volume_group_snapshot
        )

        self.cmd = volume_group_snapshot.CreateVolumeGroupSnapshot(
            self.app, None
        )

    def test_volume_group_snapshot_create(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.14'
        )

        arglist = [
            self.fake_volume_group.id,
        ]
        verifylist = [
            ('volume_group', self.fake_volume_group.id),
            ('name', None),
            ('description', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.get.assert_called_once_with(
            self.fake_volume_group.id
        )
        self.volume_group_snapshots_mock.create.assert_called_once_with(
            self.fake_volume_group.id,
            None,
            None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_snapshot_create_with_options(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.14'
        )

        arglist = [
            self.fake_volume_group.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
        ]
        verifylist = [
            ('volume_group', self.fake_volume_group.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.get.assert_called_once_with(
            self.fake_volume_group.id
        )
        self.volume_group_snapshots_mock.create.assert_called_once_with(
            self.fake_volume_group.id,
            'foo',
            'hello, world',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_snapshot_create_pre_v314(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.13'
        )

        arglist = [
            self.fake_volume_group.id,
        ]
        verifylist = [
            ('volume_group', self.fake_volume_group.id),
            ('name', None),
            ('description', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required', str(exc)
        )


class TestVolumeGroupSnapshotDelete(TestVolumeGroupSnapshot):
    fake_volume_group_snapshot = (
        volume_fakes.create_one_volume_group_snapshot()
    )

    def setUp(self):
        super().setUp()

        self.volume_group_snapshots_mock.get.return_value = (
            self.fake_volume_group_snapshot
        )
        self.volume_group_snapshots_mock.delete.return_value = None

        self.cmd = volume_group_snapshot.DeleteVolumeGroupSnapshot(
            self.app, None
        )

    def test_volume_group_snapshot_delete(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.14'
        )

        arglist = [
            self.fake_volume_group_snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.fake_volume_group_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_group_snapshots_mock.delete.assert_called_once_with(
            self.fake_volume_group_snapshot.id,
        )
        self.assertIsNone(result)

    def test_volume_group_snapshot_delete_pre_v314(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.13'
        )

        arglist = [
            self.fake_volume_group_snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.fake_volume_group_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required', str(exc)
        )


class TestVolumeGroupSnapshotList(TestVolumeGroupSnapshot):
    fake_volume_group_snapshots = volume_fakes.create_volume_group_snapshots()

    columns = (
        'ID',
        'Status',
        'Name',
    )
    data = [
        (
            fake_volume_group_snapshot.id,
            fake_volume_group_snapshot.status,
            fake_volume_group_snapshot.name,
        )
        for fake_volume_group_snapshot in fake_volume_group_snapshots
    ]

    def setUp(self):
        super().setUp()

        self.volume_group_snapshots_mock.list.return_value = (
            self.fake_volume_group_snapshots
        )

        self.cmd = volume_group_snapshot.ListVolumeGroupSnapshot(
            self.app, None
        )

    def test_volume_group_snapshot_list(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.14'
        )

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_group_snapshots_mock.list.assert_called_once_with(
            search_opts={
                'all_tenants': True,
            },
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_group_snapshot_list_pre_v314(self):
        self.app.client_manager.volume.api_version = api_versions.APIVersion(
            '3.13'
        )

        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required', str(exc)
        )
