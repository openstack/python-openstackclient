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

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()


class TestConsistencyGroupCreate(TestConsistencyGroup):

    volume_type = volume_fakes.FakeType.create_one_type()
    new_consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())

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
        self.assertEqual(self.data, data)

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
        self.assertEqual(self.data, data)


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
            utils.format_list(c.volume_types)
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
        self.assertEqual(self.data, list(data))

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
        self.assertEqual(self.data, list(data))

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
        self.assertEqual(self.data_long, list(data))
