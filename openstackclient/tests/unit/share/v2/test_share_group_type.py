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

from manilaclient import api_versions
from manilaclient.common.apiclient.exceptions import BadRequest
from manilaclient.common.apiclient.exceptions import NotFound
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient.share import utils
from openstackclient.share.v2 import share_group_types
from openstackclient.tests.unit.share.v2 import fakes as share_fakes
from openstackclient.tests.unit import utils as test_utils

COLUMNS = [
    'ID',
    'Name',
    'Share Types',
    'Visibility',
    'Is Default',
    'Group Specs',
]


class TestShareGroupType(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.sgt_mock = self.share_client.share_group_types
        self.sgt_mock.reset_mock()

        self.set_share_api_version(api_versions.MAX_VERSION)


class TestShareGroupTypeCreate(TestShareGroupType):
    def setUp(self):
        super().setUp()

        self.share_types = share_fakes.FakeShareType.create_share_types(
            count=2
        )

        formatted_share_types = []

        for st in self.share_types:
            formatted_share_types.append(st.name)

        self.share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={'share_types': formatted_share_types}
            )
        )

        self.share_group_type_formatted = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={
                    'id': self.share_group_type['id'],
                    'name': self.share_group_type['name'],
                    'share_types': formatted_share_types,
                }
            )
        )

        formatted_sgt = utils.format_share_group_type(
            self.share_group_type_formatted
        )

        self.sgt_mock.create.return_value = self.share_group_type
        self.sgt_mock.get.return_value = self.share_group_type

        # Get the command object to test
        self.cmd = share_group_types.CreateShareGroupType(self.app, None)

        self.data = tuple(formatted_sgt.values())
        self.columns = tuple(formatted_sgt.keys())

    def test_share_group_type_create_required_args(self):
        """Verifies required arguments."""

        arglist = [
            self.share_group_type.name,
            self.share_types[0].name,
            self.share_types[1].name,
        ]
        verifylist = [
            ('name', self.share_group_type.name),
            (
                'share_types',
                [self.share_types[0].name, self.share_types[1].name],
            ),
        ]

        with mock.patch(
            'manilaclient.common.apiclient.utils.find_resource',
            side_effect=[self.share_types[0], self.share_types[1]],
        ):
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            columns, data = self.cmd.take_action(parsed_args)

            self.sgt_mock.create.assert_called_with(
                group_specs={},
                is_public=True,
                name=self.share_group_type.name,
                share_types=[
                    self.share_types[0].name,
                    self.share_types[1].name,
                ],
            )

            self.assertCountEqual(self.columns, columns)
            self.assertCountEqual(self.data, data)

    def test_share_group_type_create_missing_required_arg(self):
        """Verifies missing required arguments."""

        arglist = [
            self.share_group_type.name,
        ]
        verifylist = [('name', self.share_group_type.name)]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_group_type_create_private(self):
        arglist = [
            self.share_group_type.name,
            self.share_types[0].name,
            self.share_types[1].name,
            '--public',
            'False',
        ]
        verifylist = [
            ('name', self.share_group_type.name),
            (
                'share_types',
                [self.share_types[0].name, self.share_types[1].name],
            ),
            ('public', 'False'),
        ]

        with mock.patch(
            'manilaclient.common.apiclient.utils.find_resource',
            side_effect=[self.share_types[0], self.share_types[1]],
        ):
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            columns, data = self.cmd.take_action(parsed_args)

            self.sgt_mock.create.assert_called_with(
                group_specs={},
                is_public=False,
                name=self.share_group_type.name,
                share_types=[
                    self.share_types[0].name,
                    self.share_types[1].name,
                ],
            )

            self.assertCountEqual(self.columns, columns)
            self.assertCountEqual(self.data, data)

    def test_share_group_type_create_group_specs(self):
        arglist = [
            self.share_group_type.name,
            self.share_types[0].name,
            self.share_types[1].name,
            '--group-specs',
            'consistent_snapshot_support=true',
        ]
        verifylist = [
            ('name', self.share_group_type.name),
            (
                'share_types',
                [self.share_types[0].name, self.share_types[1].name],
            ),
            ('group_specs', ['consistent_snapshot_support=true']),
        ]

        with mock.patch(
            'manilaclient.common.apiclient.utils.find_resource',
            side_effect=[self.share_types[0], self.share_types[1]],
        ):
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            columns, data = self.cmd.take_action(parsed_args)

            self.sgt_mock.create.assert_called_with(
                group_specs={'consistent_snapshot_support': 'True'},
                is_public=True,
                name=self.share_group_type.name,
                share_types=[
                    self.share_types[0].name,
                    self.share_types[1].name,
                ],
            )

            self.assertCountEqual(self.columns, columns)
            self.assertCountEqual(self.data, data)

    def test_create_share_group_type(self):
        arglist = [
            self.share_group_type.name,
            self.share_types[0].name,
            self.share_types[1].name,
        ]
        verifylist = [
            ('name', self.share_group_type.name),
            (
                'share_types',
                [self.share_types[0].name, self.share_types[1].name],
            ),
        ]

        with mock.patch(
            'manilaclient.common.apiclient.utils.find_resource',
            side_effect=[
                self.share_types[0],
                self.share_types[1],
                self.share_group_type,
            ],
        ):
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            columns, data = self.cmd.take_action(parsed_args)

            self.sgt_mock.create.assert_called_with(
                group_specs={},
                is_public=True,
                name=self.share_group_type.name,
                share_types=[
                    self.share_types[0].name,
                    self.share_types[1].name,
                ],
            )

            self.assertCountEqual(self.columns, columns)
            self.assertCountEqual(self.data, data)


class TestShareGroupTypeDelete(TestShareGroupType):
    def setUp(self):
        super().setUp()

        self.share_group_types = (
            share_fakes.FakeShareGroupType.create_share_group_types(count=2)
        )

        self.sgt_mock.delete.return_value = None
        self.sgt_mock.get = (
            share_fakes.FakeShareGroupType.get_share_group_types(
                self.share_group_types
            )
        )

        # Get the command object to test
        self.cmd = share_group_types.DeleteShareGroupType(self.app, None)

    def test_share_group_type_delete_one(self):
        arglist = [self.share_group_types[0].name]

        verifylist = [('share_group_types', [self.share_group_types[0].name])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.sgt_mock.delete.assert_called_with(self.share_group_types[0])
        self.assertIsNone(result)

    def test_share_group_type_delete_multiple(self):
        arglist = []
        for t in self.share_group_types:
            arglist.append(t.name)
        verifylist = [
            ('share_group_types', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for t in self.share_group_types:
            calls.append(mock.call(t))
        self.sgt_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_share_group_type_with_exception(self):
        arglist = [
            'non_existing_type',
        ]
        verifylist = [
            ('share_group_types', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.sgt_mock.delete.side_effect = exceptions.CommandError()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_delete_share_group_type(self):
        arglist = [self.share_group_types[0].name]

        verifylist = [('share_group_types', [self.share_group_types[0].name])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.sgt_mock.delete.assert_called_with(self.share_group_types[0])

        self.assertIsNone(result)


class TestShareGroupTypeSet(TestShareGroupType):
    def setUp(self):
        super().setUp()

        self.share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                methods={'set_keys': None, 'update': None}
            )
        )
        self.sgt_mock.get.return_value = self.share_group_type

        # Get the command object to test
        self.cmd = share_group_types.SetShareGroupType(self.app, None)

    def test_share_group_type_set_group_specs(self):
        arglist = [
            self.share_group_type.id,
            '--group-specs',
            'consistent_snapshot_support=true',
        ]
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('group_specs', ['consistent_snapshot_support=true']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.share_group_type.set_keys.assert_called_with(
            {'consistent_snapshot_support': 'True'}
        )
        self.assertIsNone(result)

    def test_share_group_type_set_extra_specs_exception(self):
        arglist = [
            self.share_group_type.id,
            '--group-specs',
            'snapshot_support=true',
        ]
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('group_specs', ['snapshot_support=true']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.share_group_type.set_keys.side_effect = BadRequest()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareGroupTypeUnset(TestShareGroupType):
    def setUp(self):
        super().setUp()

        self.share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                methods={'unset_keys': None}
            )
        )
        self.sgt_mock.get.return_value = self.share_group_type

        # Get the command object to test
        self.cmd = share_group_types.UnsetShareGroupType(self.app, None)

    def test_share_group_type_unset_extra_specs(self):
        arglist = [self.share_group_type.id, 'consistent_snapshot_support']
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('group_specs', ['consistent_snapshot_support']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.share_group_type.unset_keys.assert_called_with(
            ['consistent_snapshot_support']
        )
        self.assertIsNone(result)

    def test_share_group_type_unset_exception(self):
        arglist = [self.share_group_type.id, 'snapshot_support']
        verifylist = [
            ('share_group_type', self.share_group_type.id),
            ('group_specs', ['snapshot_support']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.share_group_type.unset_keys.side_effect = NotFound()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShareGroupTypeList(TestShareGroupType):
    def setUp(self):
        super().setUp()

        self.share_group_types = (
            share_fakes.FakeShareGroupType.create_share_group_types()
        )

        self.sgt_mock.list.return_value = self.share_group_types

        # Get the command object to test
        self.cmd = share_group_types.ListShareGroupType(self.app, None)

        self.values = (
            oscutils.get_dict_properties(s._info, COLUMNS)
            for s in self.share_group_types
        )

    def test_share_group_type_list_no_options(self):
        arglist = []
        verifylist = [('all', False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.sgt_mock.list.assert_called_once_with(
            search_opts={}, show_all=False
        )
        self.assertEqual(COLUMNS, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_type_list_all(self):
        arglist = [
            '--all',
        ]
        verifylist = [('all', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.sgt_mock.list.assert_called_once_with(
            search_opts={}, show_all=True
        )
        self.assertEqual(COLUMNS, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_type_list_group_specs(self):
        arglist = ['--group-specs', 'consistent_snapshot_support=true']
        verifylist = [('group_specs', ['consistent_snapshot_support=true'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.sgt_mock.list.assert_called_once_with(
            search_opts={
                'group_specs': {'consistent_snapshot_support': 'True'}
            },
            show_all=False,
        )
        self.assertEqual(COLUMNS, columns)
        self.assertEqual(list(self.values), list(data))


class TestShareGroupTypeShow(TestShareGroupType):
    def setUp(self):
        super().setUp()

        self.share_types = share_fakes.FakeShareType.create_share_types(
            count=2
        )

        formatted_share_types = []

        for st in self.share_types:
            formatted_share_types.append(st.name)

        self.share_group_type = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={'share_types': formatted_share_types}
            )
        )

        self.share_group_type_formatted = (
            share_fakes.FakeShareGroupType.create_one_share_group_type(
                attrs={
                    'id': self.share_group_type['id'],
                    'name': self.share_group_type['name'],
                    'share_types': formatted_share_types,
                }
            )
        )

        formatted_sgt = utils.format_share_group_type(
            self.share_group_type_formatted
        )

        self.sgt_mock.get.return_value = self.share_group_type

        # Get the command object to test
        self.cmd = share_group_types.ShowShareGroupType(self.app, None)

        self.data = tuple(formatted_sgt.values())
        self.columns = tuple(formatted_sgt.keys())

    def test_share_group_type_show(self):
        arglist = [self.share_group_type.name]
        verifylist = [("share_group_type", self.share_group_type.name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.sgt_mock.get.assert_called_with(self.share_group_type)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
