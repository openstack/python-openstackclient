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

from unittest import mock
import uuid

from manilaclient import api_versions
from osc_lib import exceptions
from osc_lib import exceptions as osc_exceptions
from osc_lib import utils as oscutils

from openstackclient.share import utils
from openstackclient.share.v2 import share_groups
from openstackclient.tests.unit.share.v2 import fakes as share_fakes
from openstackclient.tests.unit import utils as test_utils


class TestShareGroup(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.groups_mock = self.share_client.share_groups
        self.groups_mock.reset_mock()

        self.share_types_mock = self.share_client.share_types
        self.share_types_mock.reset_mock()

        self.set_share_api_version(api_versions.MAX_VERSION)


class TestShareGroupCreate(TestShareGroup):
    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.formatted_result = (
            share_fakes.FakeShareGroup.create_one_share_group(
                attrs={
                    "id": self.share_group.id,
                    'created_at': self.share_group.created_at,
                    "project_id": self.share_group.project_id,
                    'share_group_type_id': (
                        self.share_group.share_group_type_id
                    ),
                    'share_types': '\n'.join(self.share_group.share_types),
                }
            )
        )

        self.groups_mock.create.return_value = self.share_group
        self.groups_mock.get.return_value = self.share_group

        self.cmd = share_groups.CreateShareGroup(self.app, None)

        self.data = tuple(self.formatted_result._info.values())
        self.columns = tuple(self.share_group._info.keys())

    def test_share_group_create_no_args(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.create.assert_called_with(
            name=None,
            description=None,
            share_types=[],
            share_group_type=None,
            share_network=None,
            source_share_group_snapshot=None,
            availability_zone=None,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_share_group_create_with_options(self):
        arglist = [
            '--name',
            self.share_group.name,
            '--description',
            self.share_group.description,
        ]
        verifylist = [
            ('name', self.share_group.name),
            ('description', self.share_group.description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.create.assert_called_with(
            name=self.share_group.name,
            description=self.share_group.description,
            share_types=[],
            share_group_type=None,
            share_network=None,
            source_share_group_snapshot=None,
            availability_zone=None,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_share_group_create_az(self):
        arglist = ['--availability-zone', self.share_group.availability_zone]
        verifylist = [
            ('availability_zone', self.share_group.availability_zone)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.create.assert_called_with(
            name=None,
            description=None,
            share_types=[],
            share_group_type=None,
            share_network=None,
            source_share_group_snapshot=None,
            availability_zone=self.share_group.availability_zone,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_share_group_create_share_types(self):
        share_types = share_fakes.FakeShareType.create_share_types(count=2)
        self.share_types_mock.get = share_fakes.FakeShareType.get_share_types(
            share_types
        )
        arglist = ['--share-types', share_types[0].id, share_types[1].id]
        verifylist = [('share_types', [share_types[0].id, share_types[1].id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.create.assert_called_with(
            name=None,
            description=None,
            share_types=share_types,
            share_group_type=None,
            share_network=None,
            source_share_group_snapshot=None,
            availability_zone=None,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_share_group_create_wait(self):
        arglist = ['--wait']
        verifylist = [('wait', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.create.assert_called_with(
            name=None,
            description=None,
            share_types=[],
            share_group_type=None,
            share_network=None,
            source_share_group_snapshot=None,
            availability_zone=None,
        )

        self.groups_mock.get.assert_called_with(self.share_group.id)
        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    # TODO(archanaserver): Add test cases for share-group-type,
    # share-network and source-share-group-snapshot when the
    # options have OSC support.


class TestShareGroupDelete(TestShareGroup):
    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.groups_mock.get.return_value = self.share_group

        self.cmd = share_groups.DeleteShareGroup(self.app, None)

    def test_share_group_delete(self):
        arglist = [self.share_group.id]
        verifylist = [('share_group', [self.share_group.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.groups_mock.delete.assert_called_with(
            self.share_group, force=False
        )
        self.assertIsNone(result)

    def test_share_group_delete_force(self):
        arglist = [self.share_group.id, '--force']
        verifylist = [('share_group', [self.share_group.id]), ('force', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.groups_mock.delete.assert_called_with(
            self.share_group, force=True
        )
        self.assertIsNone(result)

    def test_share_group_delete_multiple(self):
        share_groups = share_fakes.FakeShareGroup.create_share_groups(count=2)
        arglist = [share_groups[0].id, share_groups[1].id]
        verifylist = [
            ('share_group', [share_groups[0].id, share_groups[1].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertEqual(self.groups_mock.delete.call_count, len(share_groups))
        self.assertIsNone(result)

    def test_share_group_delete_exception(self):
        arglist = [self.share_group.id]
        verifylist = [('share_group', [self.share_group.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.groups_mock.delete.side_effect = exceptions.CommandError()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_share_group_delete_wait(self):
        arglist = [self.share_group.id, '--wait']
        verifylist = [('share_group', [self.share_group.id]), ('wait', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch('osc_lib.utils.wait_for_delete', return_value=True):
            result = self.cmd.take_action(parsed_args)

            self.groups_mock.delete.assert_called_with(
                self.share_group, force=False
            )
            self.groups_mock.get.assert_called_with(self.share_group.id)
            self.assertIsNone(result)

    def test_share_group_delete_wait_exception(self):
        arglist = [self.share_group.id, '--wait']
        verifylist = [('share_group', [self.share_group.id]), ('wait', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch('osc_lib.utils.wait_for_delete', return_value=False):
            self.assertRaises(
                exceptions.CommandError, self.cmd.take_action, parsed_args
            )


class TestShareGroupShow(TestShareGroup):
    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.formatted_result = (
            share_fakes.FakeShareGroup.create_one_share_group(
                attrs={
                    "id": self.share_group.id,
                    'created_at': self.share_group.created_at,
                    "project_id": self.share_group.project_id,
                    'share_group_type_id': (
                        self.share_group.share_group_type_id
                    ),
                    'share_types': '\n'.join(self.share_group.share_types),
                }
            )
        )
        self.groups_mock.get.return_value = self.share_group

        self.data = tuple(self.formatted_result._info.values())
        self.columns = tuple(self.share_group._info.keys())

        self.cmd = share_groups.ShowShareGroup(self.app, None)

    def test_share_group_show(self):
        arglist = [self.share_group.id]
        verifylist = [('share_group', self.share_group.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.get.assert_called_with(self.share_group.id)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestShareGroupSet(TestShareGroup):
    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.share_group = share_fakes.FakeShare.create_one_share(
            methods={"reset_state": None}
        )
        self.groups_mock.get.return_value = self.share_group

        self.cmd = share_groups.SetShareGroup(self.app, None)

    def test_set_share_group_name(self):
        new_name = uuid.uuid4().hex
        arglist = [
            '--name',
            new_name,
            self.share_group.id,
        ]
        verifylist = [('name', new_name), ('share_group', self.share_group.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.groups_mock.update.assert_called_with(
            self.share_group.id, name=parsed_args.name
        )

    def test_set_share_group_description(self):
        new_description = uuid.uuid4().hex
        arglist = [
            '--description',
            new_description,
            self.share_group.id,
        ]
        verifylist = [
            ('description', new_description),
            ('share_group', self.share_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.groups_mock.update.assert_called_with(
            self.share_group.id, description=parsed_args.description
        )

    def test_share_group_set_status(self):
        new_status = 'available'
        arglist = [self.share_group.id, '--status', new_status]
        verifylist = [
            ('share_group', self.share_group.id),
            ('status', new_status),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.share_group.reset_state.assert_called_with(new_status)
        self.assertIsNone(result)

    def test_share_group_set_status_exception(self):
        new_status = 'available'
        arglist = [self.share_group.id, '--status', new_status]
        verifylist = [
            ('share_group', self.share_group.id),
            ('status', new_status),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.share_group.reset_state.side_effect = Exception()
        self.assertRaises(
            osc_exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareGroupUnset(TestShareGroup):
    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.groups_mock.get.return_value = self.share_group

        self.cmd = share_groups.UnsetShareGroup(self.app, None)

    def test_unset_share_group_name(self):
        arglist = [self.share_group.id, '--name']
        verifylist = [('share_group', self.share_group.id), ('name', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.groups_mock.update.assert_called_with(self.share_group, name=None)
        self.assertIsNone(result)

    def test_unset_share_group_description(self):
        arglist = [self.share_group.id, '--description']
        verifylist = [
            ('share_group', self.share_group.id),
            ('description', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.groups_mock.update.assert_called_with(
            self.share_group, description=None
        )
        self.assertIsNone(result)

    def test_unset_share_group_name_exception(self):
        arglist = [
            self.share_group.id,
            '--name',
        ]
        verifylist = [
            ('share_group', self.share_group.id),
            ('name', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.groups_mock.update.side_effect = Exception()

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareGroupList(TestShareGroup):
    columns = ['id', 'name', 'status', 'description']

    column_headers = utils.format_column_headers(columns)

    def setUp(self):
        super().setUp()

        self.new_share_group = (
            share_fakes.FakeShareGroup.create_one_share_group()
        )
        self.groups_mock.list.return_value = [self.new_share_group]

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.groups_mock.get.return_value = self.share_group

        self.share_groups_list = (
            share_fakes.FakeShareGroup.create_share_groups(count=2)
        )
        self.groups_mock.list.return_value = self.share_groups_list

        self.values = (
            oscutils.get_dict_properties(s._info, self.columns)
            for s in self.share_groups_list
        )

        self.cmd = share_groups.ListShareGroup(self.app, None)

    def test_share_group_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.list.assert_called_with(
            search_opts={
                'all_tenants': False,
                'name': None,
                'status': None,
                'share_server_id': None,
                'share_group_type': None,
                'snapshot': None,
                'host': None,
                'share_network': None,
                'project_id': None,
                'limit': None,
                'offset': None,
                'name~': None,
                'description~': None,
                'description': None,
            }
        )

        self.assertEqual(self.column_headers, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_list_pre_v236(self):
        self.set_share_api_version('2.35')

        arglist = ['--description', 'Description']
        verifylist = [('description', 'Description')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_share_group_lists_all_projects(self):
        all_tenants_list = self.column_headers.copy()
        all_tenants_list.append('Project ID')
        list_values = (
            oscutils.get_dict_properties(s._info, all_tenants_list)
            for s in self.share_groups_list
        )

        arglist = ['--all-projects']

        verifylist = [('all_projects', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.list.assert_called_with(
            search_opts={
                'all_tenants': True,
                'name': None,
                'status': None,
                'share_server_id': None,
                'share_group_type': None,
                'snapshot': None,
                'host': None,
                'share_network': None,
                'project_id': None,
                'limit': None,
                'offset': None,
                'name~': None,
                'description~': None,
                'description': None,
            }
        )

        self.assertEqual(all_tenants_list, columns)
        self.assertEqual(list(list_values), list(data))

    def test_share_group_list_name(self):
        arglist = ['--name', self.new_share_group.name]
        verifylist = [('name', self.new_share_group.name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'name': None,
            'status': None,
            'share_server_id': None,
            'share_group_type': None,
            'snapshot': None,
            'host': None,
            'share_network': None,
            'project_id': None,
            'limit': None,
            'offset': None,
            'name~': None,
            'description~': None,
            'description': None,
        }

        search_opts['name'] = self.new_share_group.name

        self.groups_mock.list.assert_called_once_with(
            search_opts=search_opts,
        )

        self.assertEqual(self.column_headers, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_list_description(self):
        arglist = ['--description', self.new_share_group.description]
        verifylist = [('description', self.new_share_group.description)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'name': None,
            'status': None,
            'share_server_id': None,
            'share_group_type': None,
            'snapshot': None,
            'host': None,
            'share_network': None,
            'project_id': None,
            'limit': None,
            'offset': None,
            'name~': None,
            'description~': None,
            'description': None,
        }

        search_opts['description'] = self.new_share_group.description

        self.groups_mock.list.assert_called_once_with(
            search_opts=search_opts,
        )

        self.assertEqual(self.column_headers, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_list_status(self):
        arglist = [
            '--status',
            self.new_share_group.status,
        ]
        verifylist = [
            ('status', self.new_share_group.status),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'name': None,
            'status': None,
            'share_server_id': None,
            'share_group_type': None,
            'snapshot': None,
            'host': None,
            'share_network': None,
            'project_id': None,
            'limit': None,
            'offset': None,
            'name~': None,
            'description~': None,
            'description': None,
        }

        search_opts['status'] = self.new_share_group.status

        self.groups_mock.list.assert_called_once_with(
            search_opts=search_opts,
        )

        self.assertEqual(self.column_headers, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_list_marker_and_limit(self):
        arglist = [
            "--marker",
            self.new_share_group.id,
            "--limit",
            "2",
        ]
        verifylist = [
            ('marker', self.new_share_group.id),
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'name': None,
            'status': None,
            'share_server_id': None,
            'share_group_type': None,
            'snapshot': None,
            'host': None,
            'share_network': None,
            'project_id': None,
            'limit': 2,
            'offset': self.new_share_group.id,
            'name~': None,
            'description~': None,
            'description': None,
        }

        self.groups_mock.list.assert_called_once_with(
            search_opts=search_opts,
        )

        self.assertEqual(self.column_headers, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_list_negative_limit(self):
        arglist = [
            "--limit",
            "-2",
        ]
        verifylist = [
            ("limit", -2),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    # TODO(archanaserver): Add test cases for share-server-id,
    # share-group-type, snapshot, share-network and source-
    # share-group-share_group when the options have OSC support.
