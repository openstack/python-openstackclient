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

from unittest import mock

from openstack.block_storage.v2 import consistency_group as _consistency_group
from openstack.block_storage.v2 import (
    consistency_group_snapshot as _consistency_group_snapshot,
)
from openstack.block_storage.v2 import type as _type
from openstack.block_storage.v2 import volume as _volume
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import consistency_group


class TestConsistencyGroupAddVolume(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.consistency_group = sdk_fakes.generate_fake_resource(
            _consistency_group.ConsistencyGroup
        )
        self.volume_sdk_client.find_consistency_group.return_value = (
            self.consistency_group
        )
        self.cmd = consistency_group.AddVolumeToConsistencyGroup(
            self.app, None
        )

    def test_add_one_volume_to_consistency_group(self):
        volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = volume
        arglist = [
            self.consistency_group.id,
            volume.id,
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('volumes', [volume.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_volume.assert_called_once_with(
            volume.id, ignore_missing=False
        )
        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group, add_volumes=volume.id
        )
        self.assertIsNone(result)

    def test_add_multiple_volumes_to_consistency_group(self):
        volumes = [
            sdk_fakes.generate_fake_resource(_volume.Volume),
            sdk_fakes.generate_fake_resource(_volume.Volume),
        ]
        self.volume_sdk_client.find_volume.side_effect = volumes
        arglist = [
            self.consistency_group.id,
            volumes[0].id,
            volumes[1].id,
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('volumes', [volumes[0].id, volumes[1].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group,
            add_volumes=volumes[0].id + ',' + volumes[1].id,
        )
        self.assertIsNone(result)

    @mock.patch.object(consistency_group.LOG, 'error')
    def test_add_multiple_volumes_to_consistency_group_with_exception(
        self, mock_error
    ):
        volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.side_effect = [
            volume,
            exceptions.CommandError,
        ]
        arglist = [
            self.consistency_group.id,
            volume.id,
            'unexist_volume',
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('volumes', [volume.id, 'unexist_volume']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        mock_error.assert_called_with(
            '%(result)s of %(total)s volumes failed to add.',
            {'result': 1, 'total': 2},
        )
        self.assertIsNone(result)
        self.volume_sdk_client.find_volume.assert_any_call(
            volume.id, ignore_missing=False
        )
        self.volume_sdk_client.find_volume.assert_any_call(
            'unexist_volume', ignore_missing=False
        )
        self.assertEqual(2, self.volume_sdk_client.find_volume.call_count)
        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group, add_volumes=volume.id
        )


class TestConsistencyGroupCreate(volume_fakes.TestVolume):
    columns = (
        'availability_zone',
        'created_at',
        'description',
        'id',
        'name',
        'status',
        'volume_types',
    )

    def setUp(self):
        super().setUp()

        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.new_consistency_group = sdk_fakes.generate_fake_resource(
            _consistency_group.ConsistencyGroup
        )
        self.consistency_group_snapshot = sdk_fakes.generate_fake_resource(
            _consistency_group_snapshot.ConsistencyGroupSnapshot
        )
        self.volume_sdk_client.create_consistency_group.return_value = (
            self.new_consistency_group
        )
        self.volume_sdk_client.create_consistency_group_from_source.return_value = self.new_consistency_group
        self.volume_sdk_client.find_type.return_value = self.volume_type
        self.volume_sdk_client.find_consistency_group_snapshot.return_value = (
            self.consistency_group_snapshot
        )
        self.volume_sdk_client.find_consistency_group.return_value = (
            self.new_consistency_group
        )

        self.data = (
            self.new_consistency_group.availability_zone,
            self.new_consistency_group.created_at,
            self.new_consistency_group.description,
            self.new_consistency_group.id,
            self.new_consistency_group.name,
            self.new_consistency_group.status,
            self.new_consistency_group.volume_types,
        )

        self.cmd = consistency_group.CreateConsistencyGroup(self.app, None)

    def test_consistency_group_create(self):
        arglist = [
            '--volume-type',
            self.volume_type.id,
            '--description',
            self.new_consistency_group.description,
            '--availability-zone',
            self.new_consistency_group.availability_zone,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('description', self.new_consistency_group.description),
            (
                'availability_zone',
                self.new_consistency_group.availability_zone,
            ),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_type.assert_called_once_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_sdk_client.find_consistency_group.assert_not_called()
        self.volume_sdk_client.create_consistency_group.assert_called_once_with(
            volume_types=self.volume_type.id,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
            availability_zone=self.new_consistency_group.availability_zone,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_consistency_group_create_without_name(self):
        arglist = [
            '--volume-type',
            self.volume_type.id,
            '--description',
            self.new_consistency_group.description,
            '--availability-zone',
            self.new_consistency_group.availability_zone,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('description', self.new_consistency_group.description),
            (
                'availability_zone',
                self.new_consistency_group.availability_zone,
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_type.assert_called_once_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_sdk_client.find_consistency_group.assert_not_called()
        self.volume_sdk_client.create_consistency_group.assert_called_once_with(
            volume_types=self.volume_type.id,
            name=None,
            description=self.new_consistency_group.description,
            availability_zone=self.new_consistency_group.availability_zone,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_consistency_group_create_from_source(self):
        arglist = [
            '--consistency-group-source',
            self.new_consistency_group.id,
            '--description',
            self.new_consistency_group.description,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('source', self.new_consistency_group.id),
            ('description', self.new_consistency_group.description),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_type.assert_not_called()
        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.new_consistency_group.id, ignore_missing=False
        )
        self.volume_sdk_client.create_consistency_group_from_source.assert_called_once_with(
            consistency_group_snapshot=None,
            consistency_group=self.new_consistency_group.id,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_consistency_group_create_from_snapshot(self):
        arglist = [
            '--consistency-group-snapshot',
            self.consistency_group_snapshot.id,
            '--description',
            self.new_consistency_group.description,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('snapshot', self.consistency_group_snapshot.id),
            ('description', self.new_consistency_group.description),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_type.assert_not_called()
        self.volume_sdk_client.find_consistency_group_snapshot.assert_called_once_with(
            self.consistency_group_snapshot.id, ignore_missing=False
        )
        self.volume_sdk_client.create_consistency_group_from_source.assert_called_once_with(
            consistency_group_snapshot=self.consistency_group_snapshot.id,
            consistency_group=None,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestConsistencyGroupDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.consistency_groups = [
            sdk_fakes.generate_fake_resource(
                _consistency_group.ConsistencyGroup
            ),
            sdk_fakes.generate_fake_resource(
                _consistency_group.ConsistencyGroup
            ),
        ]
        self.volume_sdk_client.find_consistency_group.side_effect = (
            self.consistency_groups
        )
        self.volume_sdk_client.delete_consistency_group.return_value = None

        self.cmd = consistency_group.DeleteConsistencyGroup(self.app, None)

    def test_consistency_group_delete(self):
        arglist = [self.consistency_groups[0].id]
        verifylist = [("consistency_groups", [self.consistency_groups[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_groups[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_consistency_group.assert_called_once_with(
            self.consistency_groups[0], force=False
        )
        self.assertIsNone(result)

    def test_consistency_group_delete_with_force(self):
        arglist = [
            '--force',
            self.consistency_groups[0].id,
        ]
        verifylist = [
            ('force', True),
            ("consistency_groups", [self.consistency_groups[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_consistency_group.assert_called_once_with(
            self.consistency_groups[0], force=True
        )
        self.assertIsNone(result)

    def test_delete_multiple_consistency_groups(self):
        self.volume_sdk_client.find_consistency_group.side_effect = (
            self.consistency_groups
        )
        arglist = [cg.id for cg in self.consistency_groups]
        verifylist = [
            ('consistency_groups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_consistency_group.assert_any_call(
            self.consistency_groups[0], force=False
        )
        self.volume_sdk_client.delete_consistency_group.assert_any_call(
            self.consistency_groups[1], force=False
        )
        self.assertIsNone(result)

    def test_delete_multiple_consistency_groups_with_exception(self):
        self.volume_sdk_client.find_consistency_group.side_effect = [
            self.consistency_groups[0],
            exceptions.CommandError,
        ]
        arglist = [
            self.consistency_groups[0].id,
            'unexist_consistency_group',
        ]
        verifylist = [
            ('consistency_groups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 consistency groups failed to delete.', str(e)
            )

        self.volume_sdk_client.find_consistency_group.assert_any_call(
            self.consistency_groups[0].id, ignore_missing=False
        )
        self.volume_sdk_client.find_consistency_group.assert_any_call(
            'unexist_consistency_group', ignore_missing=False
        )
        self.assertEqual(
            2, self.volume_sdk_client.find_consistency_group.call_count
        )
        self.volume_sdk_client.delete_consistency_group.assert_called_once_with(
            self.consistency_groups[0], force=False
        )


class TestConsistencyGroupList(volume_fakes.TestVolume):
    column_headers = [
        'ID',
        'Status',
        'Name',
    ]
    column_headers_long = [
        'ID',
        'Status',
        'Availability Zone',
        'Name',
        'Description',
        'Volume Types',
    ]

    def setUp(self):
        super().setUp()

        self.consistency_groups = [
            sdk_fakes.generate_fake_resource(
                _consistency_group.ConsistencyGroup
            ),
            sdk_fakes.generate_fake_resource(
                _consistency_group.ConsistencyGroup
            ),
        ]
        self.volume_sdk_client.consistency_groups.return_value = (
            self.consistency_groups
        )

        self.data = []
        for c in self.consistency_groups:
            self.data.append(
                (
                    c.id,
                    c.status,
                    c.name,
                )
            )
        self.data_long = []
        for c in self.consistency_groups:
            self.data_long.append(
                (
                    c.id,
                    c.status,
                    c.availability_zone,
                    c.name,
                    c.description,
                    format_columns.ListColumn(c.volume_types),
                )
            )

        self.cmd = consistency_group.ListConsistencyGroup(self.app, None)

    def test_consistency_group_list_without_options(self):
        arglist = []
        verifylist = [
            ("all_projects", False),
            ("long", False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.consistency_groups.assert_called_once_with(
            all_tenants=False,
        )
        self.assertEqual(self.column_headers, columns)
        self.assertCountEqual(self.data, list(data))

    def test_consistency_group_list_with_all_project(self):
        arglist = ["--all-projects"]
        verifylist = [
            ("all_projects", True),
            ("long", False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.consistency_groups.assert_called_once_with(
            all_tenants=True,
        )
        self.assertEqual(self.column_headers, columns)
        self.assertCountEqual(self.data, list(data))

    def test_consistency_group_list_with_long(self):
        arglist = [
            "--long",
        ]
        verifylist = [
            ("all_projects", False),
            ("long", True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.consistency_groups.assert_called_once_with(
            all_tenants=False,
        )
        self.assertEqual(self.column_headers_long, columns)
        self.assertCountEqual(self.data_long, list(data))


class TestConsistencyGroupRemoveVolume(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.consistency_group = sdk_fakes.generate_fake_resource(
            _consistency_group.ConsistencyGroup
        )
        self.volume_sdk_client.find_consistency_group.return_value = (
            self.consistency_group
        )
        self.cmd = consistency_group.RemoveVolumeFromConsistencyGroup(
            self.app, None
        )

    def test_remove_one_volume_from_consistency_group(self):
        volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = volume
        arglist = [
            self.consistency_group.id,
            volume.id,
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('volumes', [volume.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group, remove_volumes=volume.id
        )
        self.assertIsNone(result)

    def test_remove_multi_volumes_from_consistency_group(self):
        volumes = [
            sdk_fakes.generate_fake_resource(_volume.Volume),
            sdk_fakes.generate_fake_resource(_volume.Volume),
        ]
        self.volume_sdk_client.find_volume.side_effect = volumes
        arglist = [
            self.consistency_group.id,
            volumes[0].id,
            volumes[1].id,
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('volumes', [volumes[0].id, volumes[1].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group,
            remove_volumes=volumes[0].id + ',' + volumes[1].id,
        )
        self.assertIsNone(result)

    @mock.patch.object(consistency_group.LOG, 'error')
    def test_remove_multiple_volumes_from_consistency_group_with_exception(
        self,
        mock_error,
    ):
        volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.side_effect = [
            volume,
            exceptions.CommandError,
        ]
        arglist = [
            self.consistency_group.id,
            volume.id,
            'unexist_volume',
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('volumes', [volume.id, 'unexist_volume']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        mock_error.assert_called_with(
            '%(result)s of %(total)s volumes failed to remove.',
            {'result': 1, 'total': 2},
        )
        self.assertIsNone(result)
        self.volume_sdk_client.find_volume.assert_any_call(
            volume.id, ignore_missing=False
        )
        self.volume_sdk_client.find_volume.assert_any_call(
            'unexist_volume', ignore_missing=False
        )
        self.assertEqual(2, self.volume_sdk_client.find_volume.call_count)
        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group, remove_volumes=volume.id
        )


class TestConsistencyGroupSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.consistency_group = sdk_fakes.generate_fake_resource(
            _consistency_group.ConsistencyGroup
        )
        self.volume_sdk_client.find_consistency_group.return_value = (
            self.consistency_group
        )
        self.cmd = consistency_group.SetConsistencyGroup(self.app, None)

    def test_consistency_group_set_name(self):
        new_name = 'new_name'
        arglist = [
            '--name',
            new_name,
            self.consistency_group.id,
        ]
        verifylist = [
            ('name', new_name),
            ('description', None),
            ('consistency_group', self.consistency_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group, name=new_name
        )
        self.assertIsNone(result)

    def test_consistency_group_set_description(self):
        new_description = 'new_description'
        arglist = [
            '--description',
            new_description,
            self.consistency_group.id,
        ]
        verifylist = [
            ('name', None),
            ('description', new_description),
            ('consistency_group', self.consistency_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_sdk_client.update_consistency_group.assert_called_once_with(
            self.consistency_group, description=new_description
        )
        self.assertIsNone(result)


class TestConsistencyGroupShow(volume_fakes.TestVolume):
    columns = (
        'availability_zone',
        'created_at',
        'description',
        'id',
        'name',
        'status',
        'volume_types',
    )

    def setUp(self):
        super().setUp()

        self.consistency_group = sdk_fakes.generate_fake_resource(
            _consistency_group.ConsistencyGroup
        )
        self.data = (
            self.consistency_group.availability_zone,
            self.consistency_group.created_at,
            self.consistency_group.description,
            self.consistency_group.id,
            self.consistency_group.name,
            self.consistency_group.status,
            self.consistency_group.volume_types,
        )
        self.volume_sdk_client.find_consistency_group.return_value = (
            self.consistency_group
        )
        self.cmd = consistency_group.ShowConsistencyGroup(self.app, None)

    def test_consistency_group_show(self):
        arglist = [self.consistency_group.id]
        verifylist = [("consistency_group", self.consistency_group.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
