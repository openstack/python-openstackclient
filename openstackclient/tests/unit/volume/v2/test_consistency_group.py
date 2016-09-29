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
