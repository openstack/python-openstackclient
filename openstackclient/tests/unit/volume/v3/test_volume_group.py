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

from openstack.block_storage.v3 import group as _group
from openstack.block_storage.v3 import group_snapshot as _group_snapshot
from openstack.block_storage.v3 import group_type as _group_type
from openstack.block_storage.v3 import type as _type
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_group


class TestVolumeGroupCreate(volume_fakes.TestVolume):
    fake_volume_type = sdk_fakes.generate_fake_resource(_type.Type)
    fake_volume_group_type = sdk_fakes.generate_fake_resource(
        _group_type.GroupType
    )
    fake_volume_group = sdk_fakes.generate_fake_resource(
        _group.Group,
        group_type=fake_volume_group_type.id,
        volume_types=[fake_volume_type.id],
    )
    fake_volume_group_snapshot = sdk_fakes.generate_fake_resource(
        _group_snapshot.GroupSnapshot
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

        self.volume_sdk_client.find_type.return_value = self.fake_volume_type
        self.volume_sdk_client.find_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.create_group.return_value = (
            self.fake_volume_group
        )
        self.volume_sdk_client.get_group.return_value = self.fake_volume_group
        self.volume_sdk_client.create_group_from_source.return_value = (
            self.fake_volume_group
        )
        self.volume_sdk_client.find_group_snapshot.return_value = (
            self.fake_volume_group_snapshot
        )
        self.volume_sdk_client.find_group.return_value = self.fake_volume_group

        self.cmd = volume_group.CreateVolumeGroup(self.app, None)

    def test_volume_group_create(self):
        self.set_volume_api_version('3.13')

        arglist = [
            '--volume-group-type',
            self.fake_volume_group_type.id,
            '--volume-type',
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

        self.volume_sdk_client.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id, ignore_missing=False
        )
        self.volume_sdk_client.find_type.assert_called_once_with(
            self.fake_volume_type.id, ignore_missing=False
        )
        self.volume_sdk_client.create_group.assert_called_once_with(
            group_type=self.fake_volume_group_type.id,
            volume_types=[self.fake_volume_type.id],
            name=None,
            description=None,
            availability_zone=None,
        )
        self.volume_sdk_client.get_group.assert_called_once_with(
            self.fake_volume_group.id
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_create__legacy(self):
        self.set_volume_api_version('3.13')

        arglist = [
            self.fake_volume_group_type.id,
            self.fake_volume_type.id,
        ]
        verifylist = [
            ('volume_group_type_legacy', self.fake_volume_group_type.id),
            ('volume_types_legacy', [self.fake_volume_type.id]),
            ('name', None),
            ('description', None),
            ('availability_zone', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id, ignore_missing=False
        )
        self.volume_sdk_client.find_type.assert_called_once_with(
            self.fake_volume_type.id, ignore_missing=False
        )
        self.volume_sdk_client.create_group.assert_called_once_with(
            group_type=self.fake_volume_group_type.id,
            volume_types=[self.fake_volume_type.id],
            name=None,
            description=None,
            availability_zone=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
        mock_warning.assert_called_once()
        self.assertIn(
            'Passing volume group type and volume types as positional ',
            str(mock_warning.call_args[0][0]),
        )

    def test_volume_group_create_no_volume_type(self):
        self.set_volume_api_version('3.13')

        arglist = [
            '--volume-group-type',
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('volume_group_type', self.fake_volume_group_type.id),
            ('name', None),
            ('description', None),
            ('availability_zone', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--volume-types is a required argument when creating ', str(exc)
        )

    def test_volume_group_create_with_options(self):
        self.set_volume_api_version('3.13')

        arglist = [
            '--volume-group-type',
            self.fake_volume_group_type.id,
            '--volume-type',
            self.fake_volume_type.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
            '--availability-zone',
            'bar',
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

        self.volume_sdk_client.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id, ignore_missing=False
        )
        self.volume_sdk_client.find_type.assert_called_once_with(
            self.fake_volume_type.id, ignore_missing=False
        )
        self.volume_sdk_client.create_group.assert_called_once_with(
            group_type=self.fake_volume_group_type.id,
            volume_types=[self.fake_volume_type.id],
            name='foo',
            description='hello, world',
            availability_zone='bar',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_create_pre_v313(self):
        self.set_volume_api_version('3.12')

        arglist = [
            '--volume-group-type',
            self.fake_volume_group_type.id,
            '--volume-type',
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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required', str(exc)
        )

    def test_volume_group_create_from_source_group(self):
        self.set_volume_api_version('3.14')

        arglist = [
            '--source-group',
            self.fake_volume_group.id,
        ]
        verifylist = [
            ('source_group', self.fake_volume_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group.assert_called_once_with(
            self.fake_volume_group.id, ignore_missing=False
        )
        self.volume_sdk_client.create_group_from_source.assert_called_once_with(
            group_snapshot_id=None,
            source_group_id=self.fake_volume_group.id,
            name=None,
            description=None,
        )
        self.volume_sdk_client.get_group.assert_called_once_with(
            self.fake_volume_group.id
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_create_from_group_snapshot(self):
        self.set_volume_api_version('3.14')

        arglist = [
            '--group-snapshot',
            self.fake_volume_group_snapshot.id,
        ]
        verifylist = [
            ('group_snapshot', self.fake_volume_group_snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group_snapshot.assert_called_once_with(
            self.fake_volume_group_snapshot.id, ignore_missing=False
        )
        self.volume_sdk_client.create_group_from_source.assert_called_once_with(
            group_snapshot_id=self.fake_volume_group_snapshot.id,
            source_group_id=None,
            name=None,
            description=None,
        )
        self.volume_sdk_client.get_group.assert_called_once_with(
            self.fake_volume_group.id
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_create_from_src_pre_v314(self):
        self.set_volume_api_version('3.13')

        arglist = [
            '--source-group',
            self.fake_volume_group.id,
        ]
        verifylist = [
            ('source_group', self.fake_volume_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.14 or greater is required', str(exc)
        )

    def test_volume_group_create_from_src_source_group_group_snapshot(self):
        arglist = [
            '--source-group',
            self.fake_volume_group.id,
            '--group-snapshot',
            self.fake_volume_group_snapshot.id,
        ]
        verifylist = [
            ('source_group', self.fake_volume_group.id),
            ('group_snapshot', self.fake_volume_group_snapshot.id),
        ]

        exc = self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertIn(
            '--group-snapshot: not allowed with argument --source-group',
            str(exc),
        )


class TestVolumeGroupDelete(volume_fakes.TestVolume):
    fake_volume_group = sdk_fakes.generate_fake_resource(_group.Group)

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group.return_value = self.fake_volume_group
        self.volume_sdk_client.delete_group.return_value = None

        self.cmd = volume_group.DeleteVolumeGroup(self.app, None)

    def test_volume_group_delete(self):
        self.set_volume_api_version('3.13')

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

        self.volume_sdk_client.find_group.assert_called_once_with(
            self.fake_volume_group.id, ignore_missing=False
        )
        self.volume_sdk_client.delete_group.assert_called_once_with(
            self.fake_volume_group, delete_volumes=True
        )
        self.assertIsNone(result)

    def test_volume_group_delete_pre_v313(self):
        self.set_volume_api_version('3.12')

        arglist = [
            self.fake_volume_group.id,
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('force', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required', str(exc)
        )


class TestVolumeGroupSet(volume_fakes.TestVolume):
    fake_volume_group = sdk_fakes.generate_fake_resource(_group.Group)

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

        self.volume_sdk_client.find_group.return_value = self.fake_volume_group
        self.volume_sdk_client.update_group.return_value = (
            self.fake_volume_group
        )

        self.cmd = volume_group.SetVolumeGroup(self.app, None)

    def test_volume_group_set(self):
        self.set_volume_api_version('3.13')

        arglist = [
            self.fake_volume_group.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group.assert_called_once_with(
            self.fake_volume_group.id, ignore_missing=False
        )
        self.volume_sdk_client.update_group.assert_called_once_with(
            self.fake_volume_group,
            name='foo',
            description='hello, world',
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_with_enable_replication_option(self):
        self.set_volume_api_version('3.38')

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

        self.volume_sdk_client.enable_group_replication.assert_called_once_with(
            self.fake_volume_group
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_set_pre_v313(self):
        self.set_volume_api_version('3.12')

        arglist = [
            self.fake_volume_group.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.13 or greater is required', str(exc)
        )

    def test_volume_group_with_enable_replication_option_pre_v338(self):
        self.set_volume_api_version('3.37')

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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.38 or greater is required', str(exc)
        )


class TestVolumeGroupList(volume_fakes.TestVolume):
    fake_volume_groups = list(
        sdk_fakes.generate_fake_resources(_group.Group, count=2)
    )

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
        )
        for fake_volume_group in fake_volume_groups
    ]

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.groups.return_value = self.fake_volume_groups

        self.cmd = volume_group.ListVolumeGroup(self.app, None)

    def test_volume_group_list(self):
        self.set_volume_api_version('3.13')

        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.groups.assert_called_once_with(
            all_projects=True,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_group_list_pre_v313(self):
        self.set_volume_api_version('3.12')

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
            '--os-volume-api-version 3.13 or greater is required', str(exc)
        )


class TestVolumeGroupFailover(volume_fakes.TestVolume):
    fake_volume_group = sdk_fakes.generate_fake_resource(_group.Group)

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group.return_value = self.fake_volume_group
        self.volume_sdk_client.failover_group_replication.return_value = None

        self.cmd = volume_group.FailoverVolumeGroup(self.app, None)

    def test_volume_group_failover(self):
        self.set_volume_api_version('3.38')

        arglist = [
            self.fake_volume_group.id,
            '--allow-attached-volume',
            '--secondary-backend-id',
            'foo',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('allow_attached_volume', True),
            ('secondary_backend_id', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group.assert_called_once_with(
            self.fake_volume_group.id, ignore_missing=False
        )
        self.volume_sdk_client.failover_group_replication.assert_called_once_with(
            self.fake_volume_group,
            allowed_attached_volume=True,
            secondary_backend_id='foo',
        )
        self.assertIsNone(result)

    def test_volume_group_failover_pre_v338(self):
        self.set_volume_api_version('3.37')

        arglist = [
            self.fake_volume_group.id,
            '--allow-attached-volume',
            '--secondary-backend-id',
            'foo',
        ]
        verifylist = [
            ('group', self.fake_volume_group.id),
            ('allow_attached_volume', True),
            ('secondary_backend_id', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.38 or greater is required', str(exc)
        )
