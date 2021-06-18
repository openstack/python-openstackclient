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
from openstackclient.volume.v3 import volume_group


class TestVolumeGroup(volume_fakes.TestVolume):

    def setUp(self):
        super().setUp()

        self.volume_groups_mock = self.app.client_manager.volume.groups
        self.volume_groups_mock.reset_mock()

        self.volume_group_types_mock = \
            self.app.client_manager.volume.group_types
        self.volume_group_types_mock.reset_mock()

        self.volume_types_mock = self.app.client_manager.volume.volume_types
        self.volume_types_mock.reset_mock()


class TestVolumeGroupCreate(TestVolumeGroup):

    fake_volume_type = volume_fakes.FakeVolumeType.create_one_volume_type()
    fake_volume_group_type = \
        volume_fakes.FakeVolumeGroupType.create_one_volume_group_type()
    fake_volume_group = volume_fakes.FakeVolumeGroup.create_one_volume_group(
        attrs={
            'group_type': fake_volume_group_type.id,
            'volume_types': [fake_volume_type.id],
        },
    )

    columns = (
        'ID',
        'Status',
        'Name',
        'Description',
        'Group Type',
        'Volume Types',
        'Availability Zone',
        'Created At',
        'Volumes',
        'Group Snapshot ID',
        'Source Group ID',
    )
    data = (
        fake_volume_group.id,
        fake_volume_group.status,
        fake_volume_group.name,
        fake_volume_group.description,
        fake_volume_group.group_type,
        fake_volume_group.volume_types,
        fake_volume_group.availability_zone,
        fake_volume_group.created_at,
        fake_volume_group.volumes,
        fake_volume_group.group_snapshot_id,
        fake_volume_group.source_group_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_types_mock.get.return_value = self.fake_volume_type
        self.volume_group_types_mock.get.return_value = \
            self.fake_volume_group_type
        self.volume_groups_mock.create.return_value = self.fake_volume_group
        self.volume_groups_mock.get.return_value = self.fake_volume_group

        self.cmd = volume_group.CreateVolumeGroup(self.app, None)

    def test_volume_group_create(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.13')

        arglist = [
            self.fake_volume_group_type.id,
            self.fake_volume_type.id,
        ]
        verifylist = [
            ('volume_group_type', self.fake_volume_group_type.id),
            ('volume_types', [self.fake_volume_type.id]),
            ('name', None),
            ('description', None),
            ('availability_zone', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_group_types_mock.get.assert_called_once_with(
            self.fake_volume_group_type.id)
        self.volume_types_mock.get.assert_called_once_with(
            self.fake_volume_type.id)
        self.volume_groups_mock.create.assert_called_once_with(
            self.fake_volume_group_type.id,
            self.fake_volume_type.id,
            None,
            None,
            availability_zone=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_create_with_options(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.13')

        arglist = [
            self.fake_volume_group_type.id,
            self.fake_volume_type.id,
            '--name', 'foo',
            '--description', 'hello, world',
            '--availability-zone', 'bar',
        ]
        verifylist = [
            ('volume_group_type', self.fake_volume_group_type.id),
            ('volume_types', [self.fake_volume_type.id]),
            ('name', 'foo'),
            ('description', 'hello, world'),
            ('availability_zone', 'bar'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_group_types_mock.get.assert_called_once_with(
            self.fake_volume_group_type.id)
        self.volume_types_mock.get.assert_called_once_with(
            self.fake_volume_type.id)
        self.volume_groups_mock.create.assert_called_once_with(
            self.fake_volume_group_type.id,
            self.fake_volume_type.id,
            'foo',
            'hello, world',
            availability_zone='bar',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_create_pre_v313(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.12')

        arglist = [
            self.fake_volume_group_type.id,
            self.fake_volume_type.id,
        ]
        verifylist = [
            ('volume_group_type', self.fake_volume_group_type.id),
            ('volume_types', [self.fake_volume_type.id]),
            ('name', None),
            ('description', None),
            ('availability_zone', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required',
            str(exc))


class TestVolumeGroupDelete(TestVolumeGroup):

    fake_volume_group = \
        volume_fakes.FakeVolumeGroup.create_one_volume_group()

    def setUp(self):
        super().setUp()

        self.volume_groups_mock.get.return_value = self.fake_volume_group
        self.volume_groups_mock.delete.return_value = None

        self.cmd = volume_group.DeleteVolumeGroup(self.app, None)

    def test_volume_group_delete(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.13')

        arglist = [
            self.fake_volume_group.id,
            '--force',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('force', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.delete.assert_called_once_with(
            self.fake_volume_group.id, delete_volumes=True,
        )
        self.assertIsNone(result)

    def test_volume_group_delete_pre_v313(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.12')

        arglist = [
            self.fake_volume_group.id,
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('force', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required',
            str(exc))


class TestVolumeGroupSet(TestVolumeGroup):

    fake_volume_group = \
        volume_fakes.FakeVolumeGroup.create_one_volume_group()

    columns = (
        'ID',
        'Status',
        'Name',
        'Description',
        'Group Type',
        'Volume Types',
        'Availability Zone',
        'Created At',
        'Volumes',
        'Group Snapshot ID',
        'Source Group ID',
    )
    data = (
        fake_volume_group.id,
        fake_volume_group.status,
        fake_volume_group.name,
        fake_volume_group.description,
        fake_volume_group.group_type,
        fake_volume_group.volume_types,
        fake_volume_group.availability_zone,
        fake_volume_group.created_at,
        fake_volume_group.volumes,
        fake_volume_group.group_snapshot_id,
        fake_volume_group.source_group_id,
    )

    def setUp(self):
        super().setUp()

        self.volume_groups_mock.get.return_value = self.fake_volume_group
        self.volume_groups_mock.update.return_value = self.fake_volume_group

        self.cmd = volume_group.SetVolumeGroup(self.app, None)

    def test_volume_group_set(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.13')

        arglist = [
            self.fake_volume_group.id,
            '--name', 'foo',
            '--description', 'hello, world',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.update.assert_called_once_with(
            self.fake_volume_group.id, name='foo', description='hello, world',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_with_enable_replication_option(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.38')

        arglist = [
            self.fake_volume_group.id,
            '--enable-replication',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('enable_replication', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.enable_replication.assert_called_once_with(
            self.fake_volume_group.id)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_set_pre_v313(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.12')

        arglist = [
            self.fake_volume_group.id,
            '--name', 'foo',
            '--description', 'hello, world',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required',
            str(exc))

    def test_volume_group_with_enable_replication_option_pre_v338(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.37')

        arglist = [
            self.fake_volume_group.id,
            '--enable-replication',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('enable_replication', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-volume-api-version 3.38 or greater is required',
            str(exc))


class TestVolumeGroupList(TestVolumeGroup):

    fake_volume_groups = \
        volume_fakes.FakeVolumeGroup.create_volume_groups()

    columns = (
        'ID',
        'Status',
        'Name',
    )
    data = [
        (
            fake_volume_group.id,
            fake_volume_group.status,
            fake_volume_group.name,
        ) for fake_volume_group in fake_volume_groups
    ]

    def setUp(self):
        super().setUp()

        self.volume_groups_mock.list.return_value = self.fake_volume_groups

        self.cmd = volume_group.ListVolumeGroup(self.app, None)

    def test_volume_group_list(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.13')

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.list.assert_called_once_with(
            search_opts={
                'all_tenants': True,
            },
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_group_list_pre_v313(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.12')

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required',
            str(exc))


class TestVolumeGroupFailover(TestVolumeGroup):

    fake_volume_group = \
        volume_fakes.FakeVolumeGroup.create_one_volume_group()

    def setUp(self):
        super().setUp()

        self.volume_groups_mock.get.return_value = self.fake_volume_group
        self.volume_groups_mock.failover_replication.return_value = None

        self.cmd = volume_group.FailoverVolumeGroup(self.app, None)

    def test_volume_group_failover(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.38')

        arglist = [
            self.fake_volume_group.id,
            '--allow-attached-volume',
            '--secondary-backend-id', 'foo',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('allow_attached_volume', True),
            ('secondary_backend_id', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_groups_mock.failover_replication.assert_called_once_with(
            self.fake_volume_group.id,
            allow_attached_volume=True,
            secondary_backend_id='foo',
        )
        self.assertIsNone(result)

    def test_volume_group_failover_pre_v338(self):
        self.app.client_manager.volume.api_version = \
            api_versions.APIVersion('3.37')

        arglist = [
            self.fake_volume_group.id,
            '--allow-attached-volume',
            '--secondary-backend-id', 'foo',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('allow_attached_volume', True),
            ('secondary_backend_id', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-volume-api-version 3.38 or greater is required',
            str(exc))
