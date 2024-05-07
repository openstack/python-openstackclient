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

from openstack.block_storage.v3 import group as _group
from openstack.block_storage.v3 import group_snapshot as _group_snapshot
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_group_snapshot


class TestVolumeGroupSnapshotCreate(volume_fakes.TestVolume):
    fake_volume_group = sdk_fakes.generate_fake_resource(_group.Group)
    fake_volume_group_snapshot = sdk_fakes.generate_fake_resource(
        _group_snapshot.GroupSnapshot,
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

        self.volume_sdk_client.find_group.return_value = self.fake_volume_group
        self.volume_sdk_client.create_group_snapshot.return_value = (
            self.fake_volume_group_snapshot
        )
        self.volume_sdk_client.find_group_snapshot.return_value = (
            self.fake_volume_group_snapshot
        )

        self.cmd = volume_group_snapshot.CreateVolumeGroupSnapshot(
            self.app, None
        )

    def test_volume_group_snapshot_create(self):
        self.set_volume_api_version('3.14')

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

        self.volume_sdk_client.find_group.assert_called_once_with(
            self.fake_volume_group.id,
            ignore_missing=False,
            details=False,
        )
        self.volume_sdk_client.create_group_snapshot.assert_called_once_with(
            group_id=self.fake_volume_group.id,
            name=None,
            description=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_snapshot_create_with_options(self):
        self.set_volume_api_version('3.14')

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

        self.volume_sdk_client.find_group.assert_called_once_with(
            self.fake_volume_group.id,
            ignore_missing=False,
            details=False,
        )
        self.volume_sdk_client.create_group_snapshot.assert_called_once_with(
            group_id=self.fake_volume_group.id,
            name='foo',
            description='hello, world',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_snapshot_create_pre_v314(self):
        self.set_volume_api_version('3.13')

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
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required',
            str(exc),
        )


class TestVolumeGroupSnapshotDelete(volume_fakes.TestVolume):
    fake_volume_group_snapshot = sdk_fakes.generate_fake_resource(
        _group_snapshot.GroupSnapshot,
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group_snapshot.return_value = (
            self.fake_volume_group_snapshot
        )
        self.volume_sdk_client.delete_group_snapshot.return_value = None

        self.cmd = volume_group_snapshot.DeleteVolumeGroupSnapshot(
            self.app, None
        )

    def test_volume_group_snapshot_delete(self):
        self.set_volume_api_version('3.14')

        arglist = [
            self.fake_volume_group_snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.fake_volume_group_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_group_snapshot.assert_called_once_with(
            self.fake_volume_group_snapshot.id,
        )
        self.assertIsNone(result)

    def test_volume_group_snapshot_delete_pre_v314(self):
        self.set_volume_api_version('3.13')

        arglist = [
            self.fake_volume_group_snapshot.id,
        ]
        verifylist = [
            ('snapshot', self.fake_volume_group_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required',
            str(exc),
        )


class TestVolumeGroupSnapshotList(volume_fakes.TestVolume):
    fake_volume_group_snapshots = list(
        sdk_fakes.generate_fake_resources(
            _group_snapshot.GroupSnapshot,
            count=3,
        )
    )

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

        self.volume_sdk_client.group_snapshots.return_value = (
            self.fake_volume_group_snapshots
        )

        self.cmd = volume_group_snapshot.ListVolumeGroupSnapshot(
            self.app, None
        )

    def test_volume_group_snapshot_list(self):
        self.set_volume_api_version('3.14')

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.group_snapshots.assert_called_once_with(
            all_projects=True,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_group_snapshot_list_pre_v314(self):
        self.set_volume_api_version('3.13')

        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required',
            str(exc),
        )
