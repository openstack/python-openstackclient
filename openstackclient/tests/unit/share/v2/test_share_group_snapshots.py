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

import logging
from unittest import mock
import uuid

from manilaclient import api_versions
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient.share.v2 import share_group_snapshots
from openstackclient.tests.unit.share.v2 import fakes as share_fakes
from openstackclient.tests.unit import utils as test_utils

LOG = logging.getLogger(__name__)


class TestShareGroupSnapshot(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.groups_mock = self.share_client.share_groups
        self.groups_mock.reset_mock()

        self.group_snapshot_mocks = self.share_client.share_group_snapshots
        self.group_snapshot_mocks.reset_mock()

        self.set_share_api_version(api_versions.MAX_VERSION)


class TestCreateShareGroupSnapshot(TestShareGroupSnapshot):
    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.groups_mock.get.return_value = self.share_group

        self.share_group_snapshot = share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot()
        self.group_snapshot_mocks.create.return_value = (
            self.share_group_snapshot
        )
        self.group_snapshot_mocks.get.return_value = self.share_group_snapshot

        self.cmd = share_group_snapshots.CreateShareGroupSnapshot(
            self.app, None
        )

        self.data = tuple(self.share_group_snapshot._info.values())
        self.columns = tuple(self.share_group_snapshot._info.keys())

    def test_share_group_snapshot_create_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_group_snapshot_create(self):
        arglist = [self.share_group.id]
        verifylist = [('share_group', self.share_group.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.create.assert_called_with(
            self.share_group, name=None, description=None
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_share_group_snapshot_create_options(self):
        arglist = [
            self.share_group.id,
            '--name',
            self.share_group_snapshot.name,
            '--description',
            self.share_group_snapshot.description,
        ]
        verifylist = [
            ('share_group', self.share_group.id),
            ('name', self.share_group_snapshot.name),
            ('description', self.share_group_snapshot.description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.create.assert_called_with(
            self.share_group,
            name=self.share_group_snapshot.name,
            description=self.share_group_snapshot.description,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_share_group_snapshot_create_wait(self):
        arglist = [self.share_group.id, '--wait']
        verifylist = [('share_group', self.share_group.id), ('wait', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        with mock.patch('osc_lib.utils.wait_for_status', return_value=True):
            self.group_snapshot_mocks.create.assert_called_with(
                self.share_group,
                name=None,
                description=None,
            )
            self.group_snapshot_mocks.get.assert_called_with(
                self.share_group_snapshot.id
            )
            self.assertCountEqual(self.columns, columns)
            self.assertCountEqual(self.data, data)

    @mock.patch('openstackclient.share.v2.share_group_snapshots.LOG')
    def test_share_group_snapshot_create_wait_exception(self, mock_logger):
        arglist = [self.share_group.id, '--wait']
        verifylist = [('share_group', self.share_group.id), ('wait', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch('osc_lib.utils.wait_for_status', return_value=False):
            columns, data = self.cmd.take_action(parsed_args)

            self.group_snapshot_mocks.create.assert_called_with(
                self.share_group,
                name=None,
                description=None,
            )

            mock_logger.error.assert_called_with(
                "ERROR: Share group snapshot is in error state."
            )

            self.group_snapshot_mocks.get.assert_called_with(
                self.share_group_snapshot.id
            )
            self.assertCountEqual(self.columns, columns)
            self.assertCountEqual(self.data, data)


class TestDeleteShareGroupSnapshot(TestShareGroupSnapshot):
    def setUp(self):
        super().setUp()

        self.share_group_snapshot = share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot()
        self.group_snapshot_mocks.get.return_value = self.share_group_snapshot

        self.cmd = share_group_snapshots.DeleteShareGroupSnapshot(
            self.app, None
        )

    def test_share_group_snapshot_delete_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_group_snapshot_delete(self):
        arglist = [self.share_group_snapshot.id]
        verifylist = [('share_group_snapshot', [self.share_group_snapshot.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.delete.assert_called_with(
            self.share_group_snapshot, force=False
        )
        self.assertIsNone(result)

    def test_share_group_snapshot_delete_force(self):
        arglist = [self.share_group_snapshot.id, '--force']
        verifylist = [
            ('share_group_snapshot', [self.share_group_snapshot.id]),
            ('force', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.delete.assert_called_with(
            self.share_group_snapshot, force=True
        )
        self.assertIsNone(result)

    def test_share_group_snapshot_delete_multiple(self):
        share_group_snapshots = (
            share_fakes.FakeShareGroupSnapshot.create_share_group_snapshots(
                count=2
            )
        )
        arglist = [share_group_snapshots[0].id, share_group_snapshots[1].id]
        verifylist = [
            (
                'share_group_snapshot',
                [share_group_snapshots[0].id, (share_group_snapshots[1].id)],
            )
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertEqual(
            self.group_snapshot_mocks.delete.call_count,
            len(share_group_snapshots),
        )
        self.assertIsNone(result)

    def test_share_group_snapshot_delete_exception(self):
        arglist = [self.share_group_snapshot.id]
        verifylist = [('share_group_snapshot', [self.share_group_snapshot.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.group_snapshot_mocks.delete.side_effect = (
            exceptions.CommandError()
        )
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_share_group_snapshot_delete_wait(self):
        arglist = [self.share_group_snapshot.id, '--wait']
        verifylist = [
            ('share_group_snapshot', [self.share_group_snapshot.id]),
            ('wait', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch('osc_lib.utils.wait_for_delete', return_value=True):
            result = self.cmd.take_action(parsed_args)

            self.group_snapshot_mocks.delete.assert_called_with(
                self.share_group_snapshot, force=False
            )
            self.group_snapshot_mocks.get.assert_called_with(
                self.share_group_snapshot.id
            )
            self.assertIsNone(result)

    def test_share_group_snapshot_delete_wait_exception(self):
        arglist = [self.share_group_snapshot.id, '--wait']
        verifylist = [
            ('share_group_snapshot', [self.share_group_snapshot.id]),
            ('wait', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch('osc_lib.utils.wait_for_delete', return_value=False):
            self.assertRaises(
                exceptions.CommandError, self.cmd.take_action, parsed_args
            )


class TestShowShareGroupSnapshot(TestShareGroupSnapshot):
    def setUp(self):
        super().setUp()

        self.share_group_snapshot = share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot()
        self.group_snapshot_mocks.get.return_value = self.share_group_snapshot

        self.cmd = share_group_snapshots.ShowShareGroupSnapshot(self.app, None)

        self.data = tuple(self.share_group_snapshot._info.values())
        self.columns = tuple(self.share_group_snapshot._info.keys())

    def test_share_group_snapshot_show_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_group_show(self):
        arglist = [self.share_group_snapshot.id]
        verifylist = [('share_group_snapshot', self.share_group_snapshot.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.get.assert_called_with(
            self.share_group_snapshot.id
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestSetShareGroupSnapshot(TestShareGroupSnapshot):
    def setUp(self):
        super().setUp()

        self.share_group_snapshot = share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot()
        self.group_snapshot_mocks.get.return_value = self.share_group_snapshot

        self.cmd = share_group_snapshots.SetShareGroupSnapshot(self.app, None)

        self.data = tuple(self.share_group_snapshot._info.values())
        self.columns = tuple(self.share_group_snapshot._info.keys())

    def test_set_share_group_snapshot_name_description(self):
        group_snapshot_name = 'group-snapshot-name-' + uuid.uuid4().hex
        group_snapshot_description = (
            'group-snapshot-description-' + uuid.uuid4().hex
        )
        arglist = [
            self.share_group_snapshot.id,
            '--name',
            group_snapshot_name,
            '--description',
            group_snapshot_description,
        ]
        verifylist = [
            ('share_group_snapshot', self.share_group_snapshot.id),
            ('name', group_snapshot_name),
            ('description', group_snapshot_description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.update.assert_called_with(
            self.share_group_snapshot,
            name=parsed_args.name,
            description=parsed_args.description,
        )
        self.assertIsNone(result)

    def test_set_share_group_snapshot_status(self):
        arglist = [self.share_group_snapshot.id, '--status', 'available']
        verifylist = [
            ('share_group_snapshot', self.share_group_snapshot.id),
            ('status', 'available'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.reset_state.assert_called_with(
            self.share_group_snapshot, 'available'
        )
        self.assertIsNone(result)

    def test_set_share_group_snapshot_exception(self):
        arglist = [self.share_group_snapshot.id, '--status', 'available']
        verifylist = [
            ('share_group_snapshot', self.share_group_snapshot.id),
            ('status', 'available'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.group_snapshot_mocks.reset_state.side_effect = Exception()

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestUnsetShareGroupSnapshot(TestShareGroupSnapshot):
    def setUp(self):
        super().setUp()

        self.share_group_snapshot = share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot()
        self.group_snapshot_mocks.get.return_value = self.share_group_snapshot

        self.cmd = share_group_snapshots.UnsetShareGroupSnapshot(
            self.app, None
        )

    def test_unset_share_group_snapshot_name_description(self):
        arglist = [self.share_group_snapshot.id, '--name', '--description']
        verifylist = [
            ('share_group_snapshot', self.share_group_snapshot.id),
            ('name', True),
            ('description', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.update.assert_called_with(
            self.share_group_snapshot, name='', description=''
        )
        self.assertIsNone(result)

    def test_unset_share_group_snapshot_name_exception(self):
        arglist = [
            self.share_group_snapshot.id,
            '--name',
        ]
        verifylist = [
            ('share_group_snapshot', self.share_group_snapshot.id),
            ('name', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.group_snapshot_mocks.update.side_effect = Exception()

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestListShareGroupSnapshot(TestShareGroupSnapshot):
    columns = [
        'ID',
        'Name',
        'Status',
        'Description',
    ]

    def setUp(self):
        super().setUp()

        self.share_group = share_fakes.FakeShareGroup.create_one_share_group()
        self.groups_mock.get.return_value = self.share_group

        self.share_group_snapshot = (
            share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot(
                {'share_group_id': self.share_group.id}
            )
        )

        self.share_group_snapshots_list = [self.share_group_snapshot]
        self.group_snapshot_mocks.list.return_value = (
            self.share_group_snapshots_list
        )

        self.values = (
            oscutils.get_dict_properties(s._info, self.columns)
            for s in self.share_group_snapshots_list
        )

        self.cmd = share_group_snapshots.ListShareGroupSnapshot(self.app, None)

    def test_share_group_snapshot_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.list.assert_called_once_with(
            search_opts={
                'all_tenants': False,
                'name': None,
                'status': None,
                'share_group_id': None,
                'limit': None,
                'offset': None,
            }
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.values), list(data))

    def test_share_group_snapshot_list_detail_all_projects(self):
        columns_detail = [
            'ID',
            'Name',
            'Status',
            'Description',
            'Created At',
            'Share Group ID',
            'Project ID',
        ]

        values = (
            oscutils.get_dict_properties(s._info, columns_detail)
            for s in self.share_group_snapshots_list
        )

        arglist = [
            '--detailed',
            '--all-projects',
        ]

        verifylist = [
            ('detailed', True),
            ('all_projects', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.list.assert_called_once_with(
            search_opts={
                'all_tenants': True,
                'name': None,
                'status': None,
                'share_group_id': None,
                'limit': None,
                'offset': None,
            }
        )

        self.assertEqual(columns_detail, columns)
        self.assertEqual(list(values), list(data))

    def test_share_group_snapshot_list_search_options(self):
        arglist = [
            '--name',
            self.share_group_snapshot.name,
            '--status',
            self.share_group_snapshot.status,
            '--share-group',
            self.share_group.id,
        ]
        verifylist = [
            ('name', self.share_group_snapshot.name),
            ('status', self.share_group_snapshot.status),
            ('share_group', self.share_group.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.groups_mock.get.assert_called_with(self.share_group.id)
        self.group_snapshot_mocks.list.assert_called_once_with(
            search_opts={
                'all_tenants': False,
                'name': self.share_group_snapshot.name,
                'status': self.share_group_snapshot.status,
                'share_group_id': self.share_group.id,
                'limit': None,
                'offset': None,
            }
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.values), list(data))


class TestListShareGroupSnapshotMembers(TestShareGroupSnapshot):
    columns = [
        'Share ID',
        'Size',
    ]

    def setUp(self):
        super().setUp()

        self.share = share_fakes.FakeShare.create_one_share()

        self.share_group_snapshot = (
            share_fakes.FakeShareGroupSnapshot.create_one_share_group_snapshot(
                {
                    'members': [
                        {'share_id': self.share.id, 'size': self.share.size}
                    ]
                }
            )
        )

        self.group_snapshot_mocks.get.return_value = self.share_group_snapshot

        self.values = (
            oscutils.get_dict_properties(s, self.columns)
            for s in self.share_group_snapshot.members
        )

        self.cmd = share_group_snapshots.ListShareGroupSnapshotMembers(
            self.app, None
        )

    def test_share_group_snapshot_list_members(self):
        arglist = [self.share_group_snapshot.id]
        verifylist = [('share_group_snapshot', self.share_group_snapshot.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.group_snapshot_mocks.get.assert_called_with(
            self.share_group_snapshot.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.values), list(data))
