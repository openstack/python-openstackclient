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

import mock
from mock import call

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import consistency_group


class TestConsistencyGroup(volume_fakes.TestVolume):

    def setUp(self):
        super(TestConsistencyGroup, self).setUp()

        # Get a shortcut to the TransferManager Mock
        self.consistencygroups_mock = (
            self.app.client_manager.volume.consistencygroups)
        self.consistencygroups_mock.reset_mock()

        self.cgsnapshots_mock = (
            self.app.client_manager.volume.cgsnapshots)
        self.cgsnapshots_mock.reset_mock()

        self.volumes_mock = (
            self.app.client_manager.volume.volumes)
        self.volumes_mock.reset_mock()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()


class TestConsistencyGroupAddVolume(TestConsistencyGroup):

    _consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())

    def setUp(self):
        super(TestConsistencyGroupAddVolume, self).setUp()

        self.consistencygroups_mock.get.return_value = (
            self._consistency_group)
        # Get the command object to test
        self.cmd = \
            consistency_group.AddVolumeToConsistencyGroup(self.app, None)

    def test_add_one_volume_to_consistency_group(self):
        volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = volume
        arglist = [
            self._consistency_group.id,
            volume.id,
        ]
        verifylist = [
            ('consistency_group', self._consistency_group.id),
            ('volumes', [volume.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'add_volumes': volume.id,
        }
        self.consistencygroups_mock.update.assert_called_once_with(
            self._consistency_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_add_multiple_volumes_to_consistency_group(self):
        volumes = volume_fakes.FakeVolume.create_volumes(count=2)
        self.volumes_mock.get = volume_fakes.FakeVolume.get_volumes(volumes)
        arglist = [
            self._consistency_group.id,
            volumes[0].id,
            volumes[1].id,
        ]
        verifylist = [
            ('consistency_group', self._consistency_group.id),
            ('volumes', [volumes[0].id, volumes[1].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'add_volumes': volumes[0].id + ',' + volumes[1].id,
        }
        self.consistencygroups_mock.update.assert_called_once_with(
            self._consistency_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    @mock.patch.object(consistency_group.LOG, 'error')
    def test_add_multiple_volumes_to_consistency_group_with_exception(
            self, mock_error):
        volume = volume_fakes.FakeVolume.create_one_volume()
        arglist = [
            self._consistency_group.id,
            volume.id,
            'unexist_volume',
        ]
        verifylist = [
            ('consistency_group', self._consistency_group.id),
            ('volumes', [volume.id, 'unexist_volume']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [volume,
                            exceptions.CommandError,
                            self._consistency_group]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            result = self.cmd.take_action(parsed_args)
            mock_error.assert_called_with("1 of 2 volumes failed to add.")
            self.assertIsNone(result)
            find_mock.assert_any_call(self.consistencygroups_mock,
                                      self._consistency_group.id)
            find_mock.assert_any_call(self.volumes_mock,
                                      volume.id)
            find_mock.assert_any_call(self.volumes_mock,
                                      'unexist_volume')
            self.assertEqual(3, find_mock.call_count)
            self.consistencygroups_mock.update.assert_called_once_with(
                self._consistency_group.id, add_volumes=volume.id
            )


class TestConsistencyGroupCreate(TestConsistencyGroup):

    volume_type = volume_fakes.FakeType.create_one_type()
    new_consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())
    consistency_group_snapshot = (
        volume_fakes.
        FakeConsistencyGroupSnapshot.
        create_one_consistency_group_snapshot()
    )

    columns = (
        'availability_zone',
        'created_at',
        'description',
        'id',
        'name',
        'status',
        'volume_types',
    )
    data = (
        new_consistency_group.availability_zone,
        new_consistency_group.created_at,
        new_consistency_group.description,
        new_consistency_group.id,
        new_consistency_group.name,
        new_consistency_group.status,
        new_consistency_group.volume_types,
    )

    def setUp(self):
        super(TestConsistencyGroupCreate, self).setUp()
        self.consistencygroups_mock.create.return_value = (
            self.new_consistency_group)
        self.consistencygroups_mock.create_from_src.return_value = (
            self.new_consistency_group)
        self.consistencygroups_mock.get.return_value = (
            self.new_consistency_group)
        self.types_mock.get.return_value = self.volume_type
        self.cgsnapshots_mock.get.return_value = (
            self.consistency_group_snapshot)

        # Get the command object to test
        self.cmd = consistency_group.CreateConsistencyGroup(self.app, None)

    def test_consistency_group_create(self):
        arglist = [
            '--volume-type', self.volume_type.id,
            '--description', self.new_consistency_group.description,
            '--availability-zone',
            self.new_consistency_group.availability_zone,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('description', self.new_consistency_group.description),
            ('availability_zone',
             self.new_consistency_group.availability_zone),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_called_once_with(
            self.volume_type.id)
        self.consistencygroups_mock.get.assert_not_called()
        self.consistencygroups_mock.create.assert_called_once_with(
            self.volume_type.id,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
            availability_zone=self.new_consistency_group.availability_zone,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_consistency_group_create_without_name(self):
        arglist = [
            '--volume-type', self.volume_type.id,
            '--description', self.new_consistency_group.description,
            '--availability-zone',
            self.new_consistency_group.availability_zone,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
            ('description', self.new_consistency_group.description),
            ('availability_zone',
             self.new_consistency_group.availability_zone),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_called_once_with(
            self.volume_type.id)
        self.consistencygroups_mock.get.assert_not_called()
        self.consistencygroups_mock.create.assert_called_once_with(
            self.volume_type.id,
            name=None,
            description=self.new_consistency_group.description,
            availability_zone=self.new_consistency_group.availability_zone,
        )

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_consistency_group_create_from_source(self):
        arglist = [
            '--consistency-group-source', self.new_consistency_group.id,
            '--description', self.new_consistency_group.description,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('consistency_group_source', self.new_consistency_group.id),
            ('description', self.new_consistency_group.description),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_not_called()
        self.consistencygroups_mock.get.assert_called_once_with(
            self.new_consistency_group.id)
        self.consistencygroups_mock.create_from_src.assert_called_with(
            None,
            self.new_consistency_group.id,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_consistency_group_create_from_snapshot(self):
        arglist = [
            '--consistency-group-snapshot', self.consistency_group_snapshot.id,
            '--description', self.new_consistency_group.description,
            self.new_consistency_group.name,
        ]
        verifylist = [
            ('consistency_group_snapshot', self.consistency_group_snapshot.id),
            ('description', self.new_consistency_group.description),
            ('name', self.new_consistency_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.types_mock.get.assert_not_called()
        self.cgsnapshots_mock.get.assert_called_once_with(
            self.consistency_group_snapshot.id)
        self.consistencygroups_mock.create_from_src.assert_called_with(
            self.consistency_group_snapshot.id,
            None,
            name=self.new_consistency_group.name,
            description=self.new_consistency_group.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)


class TestConsistencyGroupDelete(TestConsistencyGroup):

    consistency_groups =\
        volume_fakes.FakeConsistencyGroup.create_consistency_groups(count=2)

    def setUp(self):
        super(TestConsistencyGroupDelete, self).setUp()

        self.consistencygroups_mock.get = volume_fakes.FakeConsistencyGroup.\
            get_consistency_groups(self.consistency_groups)
        self.consistencygroups_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = consistency_group.DeleteConsistencyGroup(self.app, None)

    def test_consistency_group_delete(self):
        arglist = [
            self.consistency_groups[0].id
        ]
        verifylist = [
            ("consistency_groups", [self.consistency_groups[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.delete.assert_called_with(
            self.consistency_groups[0].id, False)
        self.assertIsNone(result)

    def test_consistency_group_delete_with_force(self):
        arglist = [
            '--force',
            self.consistency_groups[0].id,
        ]
        verifylist = [
            ('force', True),
            ("consistency_groups", [self.consistency_groups[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.delete.assert_called_with(
            self.consistency_groups[0].id, True)
        self.assertIsNone(result)

    def test_delete_multiple_consistency_groups(self):
        arglist = []
        for b in self.consistency_groups:
            arglist.append(b.id)
        verifylist = [
            ('consistency_groups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for b in self.consistency_groups:
            calls.append(call(b.id, False))
        self.consistencygroups_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_consistency_groups_with_exception(self):
        arglist = [
            self.consistency_groups[0].id,
            'unexist_consistency_group',
        ]
        verifylist = [
            ('consistency_groups', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.consistency_groups[0],
                            exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 consistency groups failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.consistencygroups_mock,
                                      self.consistency_groups[0].id)
            find_mock.assert_any_call(self.consistencygroups_mock,
                                      'unexist_consistency_group')

            self.assertEqual(2, find_mock.call_count)
            self.consistencygroups_mock.delete.assert_called_once_with(
                self.consistency_groups[0].id, False
            )


class TestConsistencyGroupList(TestConsistencyGroup):

    consistency_groups = (
        volume_fakes.FakeConsistencyGroup.create_consistency_groups(count=2))

    columns = [
        'ID',
        'Status',
        'Name',
    ]
    columns_long = [
        'ID',
        'Status',
        'Availability Zone',
        'Name',
        'Description',
        'Volume Types',
    ]
    data = []
    for c in consistency_groups:
        data.append((
            c.id,
            c.status,
            c.name,
        ))
    data_long = []
    for c in consistency_groups:
        data_long.append((
            c.id,
            c.status,
            c.availability_zone,
            c.name,
            c.description,
            format_columns.ListColumn(c.volume_types)
        ))

    def setUp(self):
        super(TestConsistencyGroupList, self).setUp()

        self.consistencygroups_mock.list.return_value = self.consistency_groups
        # Get the command to test
        self.cmd = consistency_group.ListConsistencyGroup(self.app, None)

    def test_consistency_group_list_without_options(self):
        arglist = []
        verifylist = [
            ("all_projects", False),
            ("long", False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.list.assert_called_once_with(
            detailed=True, search_opts={'all_tenants': False})
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_consistency_group_list_with_all_project(self):
        arglist = [
            "--all-projects"
        ]
        verifylist = [
            ("all_projects", True),
            ("long", False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.list.assert_called_once_with(
            detailed=True, search_opts={'all_tenants': True})
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

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

        self.consistencygroups_mock.list.assert_called_once_with(
            detailed=True, search_opts={'all_tenants': False})
        self.assertEqual(self.columns_long, columns)
        self.assertListItemEqual(self.data_long, list(data))


class TestConsistencyGroupRemoveVolume(TestConsistencyGroup):

    _consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())

    def setUp(self):
        super(TestConsistencyGroupRemoveVolume, self).setUp()

        self.consistencygroups_mock.get.return_value = (
            self._consistency_group)
        # Get the command object to test
        self.cmd = \
            consistency_group.RemoveVolumeFromConsistencyGroup(self.app, None)

    def test_remove_one_volume_from_consistency_group(self):
        volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = volume
        arglist = [
            self._consistency_group.id,
            volume.id,
        ]
        verifylist = [
            ('consistency_group', self._consistency_group.id),
            ('volumes', [volume.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remove_volumes': volume.id,
        }
        self.consistencygroups_mock.update.assert_called_once_with(
            self._consistency_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_remove_multi_volumes_from_consistency_group(self):
        volumes = volume_fakes.FakeVolume.create_volumes(count=2)
        self.volumes_mock.get = volume_fakes.FakeVolume.get_volumes(volumes)
        arglist = [
            self._consistency_group.id,
            volumes[0].id,
            volumes[1].id,
        ]
        verifylist = [
            ('consistency_group', self._consistency_group.id),
            ('volumes', [volumes[0].id, volumes[1].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'remove_volumes': volumes[0].id + ',' + volumes[1].id,
        }
        self.consistencygroups_mock.update.assert_called_once_with(
            self._consistency_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    @mock.patch.object(consistency_group.LOG, 'error')
    def test_remove_multiple_volumes_from_consistency_group_with_exception(
            self, mock_error):
        volume = volume_fakes.FakeVolume.create_one_volume()
        arglist = [
            self._consistency_group.id,
            volume.id,
            'unexist_volume',
        ]
        verifylist = [
            ('consistency_group', self._consistency_group.id),
            ('volumes', [volume.id, 'unexist_volume']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [volume,
                            exceptions.CommandError,
                            self._consistency_group]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            result = self.cmd.take_action(parsed_args)
            mock_error.assert_called_with("1 of 2 volumes failed to remove.")
            self.assertIsNone(result)
            find_mock.assert_any_call(self.consistencygroups_mock,
                                      self._consistency_group.id)
            find_mock.assert_any_call(self.volumes_mock,
                                      volume.id)
            find_mock.assert_any_call(self.volumes_mock,
                                      'unexist_volume')
            self.assertEqual(3, find_mock.call_count)
            self.consistencygroups_mock.update.assert_called_once_with(
                self._consistency_group.id, remove_volumes=volume.id
            )


class TestConsistencyGroupSet(TestConsistencyGroup):

    consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())

    def setUp(self):
        super(TestConsistencyGroupSet, self).setUp()

        self.consistencygroups_mock.get.return_value = (
            self.consistency_group)
        # Get the command object to test
        self.cmd = consistency_group.SetConsistencyGroup(self.app, None)

    def test_consistency_group_set_name(self):
        new_name = 'new_name'
        arglist = [
            '--name', new_name,
            self.consistency_group.id,
        ]
        verifylist = [
            ('name', new_name),
            ('description', None),
            ('consistency_group', self.consistency_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': new_name,
        }
        self.consistencygroups_mock.update.assert_called_once_with(
            self.consistency_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_consistency_group_set_description(self):
        new_description = 'new_description'
        arglist = [
            '--description', new_description,
            self.consistency_group.id,
        ]
        verifylist = [
            ('name', None),
            ('description', new_description),
            ('consistency_group', self.consistency_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': new_description,
        }
        self.consistencygroups_mock.update.assert_called_once_with(
            self.consistency_group.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestConsistencyGroupShow(TestConsistencyGroup):
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
        super(TestConsistencyGroupShow, self).setUp()

        self.consistency_group = (
            volume_fakes.FakeConsistencyGroup.create_one_consistency_group())
        self.data = (
            self.consistency_group.availability_zone,
            self.consistency_group.created_at,
            self.consistency_group.description,
            self.consistency_group.id,
            self.consistency_group.name,
            self.consistency_group.status,
            self.consistency_group.volume_types,
        )
        self.consistencygroups_mock.get.return_value = self.consistency_group
        self.cmd = consistency_group.ShowConsistencyGroup(self.app, None)

    def test_consistency_group_show(self):
        arglist = [
            self.consistency_group.id
        ]
        verifylist = [
            ("consistency_group", self.consistency_group.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.consistencygroups_mock.get.assert_called_once_with(
            self.consistency_group.id)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)
