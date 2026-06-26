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

from manilaclient import api_versions
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient.share.v2 import resource_locks
from openstackclient.tests.unit.share.v2 import fakes as share_fakes
from openstackclient.tests.unit import utils as test_utils

DETAIL_COLUMNS = [
    'ID',
    'Resource Id',
    'Resource Type',
    'Resource Action',
    'Created At',
    'Updated At',
    'User Id',
    'Project Id',
    'Lock Reason',
    'Lock Context',
]

SUMMARY_COLUMNS = [
    'ID',
    'Resource Id',
    'Resource Type',
    'Resource Action',
]


class TestResourceLock(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.shares_mock = self.share_client.shares
        self.shares_mock.reset_mock()

        self.locks_mock = self.share_client.resource_locks
        self.locks_mock.reset_mock()

        self.set_share_api_version(api_versions.MAX_VERSION)


class TestResourceLockCreate(TestResourceLock):
    def setUp(self):
        super().setUp()

        self.share = share_fakes.FakeShare.create_one_share()
        self.shares_mock.create.return_value = self.share

        self.shares_mock.get.return_value = self.share

        self.lock = share_fakes.FakeResourceLock.create_one_lock(
            attrs={'resource_id': self.share.id}
        )
        self.locks_mock.get.return_value = self.lock
        self.locks_mock.create.return_value = self.lock

        self.cmd = resource_locks.CreateResourceLock(self.app, None)

        self.data = tuple(self.lock._info.values())
        self.columns = tuple(self.lock._info.keys())

    def test_share_lock_create_missing_required_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_lock_create(self):
        arglist = [
            '--resource-action',
            'revert_to_snapshot',
            '--lock-reason',
            "you cannot go back in time",
            self.share.id,
            'share',
        ]
        verifylist = [
            ('resource', self.share.id),
            ('resource_type', 'share'),
            ('resource_action', 'revert_to_snapshot'),
            ('lock_reason', 'you cannot go back in time'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.locks_mock.create.assert_called_with(
            self.share.id,
            'share',
            'revert_to_snapshot',
            'you cannot go back in time',
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestResourceLockDelete(TestResourceLock):
    def setUp(self):
        super().setUp()

        self.lock = share_fakes.FakeResourceLock.create_one_lock()

        self.locks_mock.get.return_value = self.lock
        self.lock.delete = mock.Mock()

        self.cmd = resource_locks.DeleteResourceLock(self.app, None)

    def test_share_lock_delete_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_lock_delete(self):
        arglist = [self.lock.id]
        verifylist = [('lock', [self.lock.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.lock.delete.assert_called_once_with()
        self.assertIsNone(result)

    def test_share_lock_delete_multiple(self):
        locks = share_fakes.FakeResourceLock.create_locks(count=2)
        arglist = [locks[0].id, locks[1].id]
        verifylist = [('lock', [locks[0].id, locks[1].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertEqual(self.lock.delete.call_count, len(locks))
        self.assertIsNone(result)

    def test_share_lock_delete_exception(self):
        arglist = [self.lock.id]
        verifylist = [('lock', [self.lock.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.lock.delete.side_effect = exceptions.CommandError()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestResourceLockShow(TestResourceLock):
    def setUp(self):
        super().setUp()

        self.lock = share_fakes.FakeResourceLock.create_one_lock()
        self.locks_mock.get.return_value = self.lock

        self.cmd = resource_locks.ShowResourceLock(self.app, None)

        self.data = self.lock._info.values()
        self.columns = list(self.lock._info.keys())

    def test_share_lock_show_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_lock_show(self):
        arglist = [
            self.lock.id,
        ]
        verifylist = [('lock', self.lock.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.locks_mock.get.assert_called_with(self.lock.id)
        self.assertEqual(len(self.columns), len(columns))
        self.assertCountEqual(sorted(self.data), sorted(data))


class TestResourceLockList(TestResourceLock):
    def setUp(self):
        super().setUp()

        self.locks = share_fakes.FakeResourceLock.create_locks(count=2)

        self.locks_mock.list.return_value = self.locks

        self.values = (
            oscutils.get_dict_properties(m._info, DETAIL_COLUMNS)
            for m in self.locks
        )

        self.cmd = resource_locks.ListResourceLock(self.app, None)

    def test_share_lock_list(self):
        arglist = ['--detailed']
        verifylist = [('detailed', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.locks_mock.list.assert_called_with(
            search_opts={
                'all_projects': False,
                'project_id': None,
                'user_id': None,
                'id': None,
                'resource_id': None,
                'resource_type': None,
                'resource_action': None,
                'lock_context': None,
                'created_before': None,
                'created_since': None,
                'limit': None,
                'offset': None,
            },
            sort_key=None,
            sort_dir=None,
        )

        self.assertEqual(sorted(DETAIL_COLUMNS), sorted(columns))
        actual_data = [sorted(d) for d in data]
        expected_data = [sorted(v) for v in self.values]
        self.assertEqual(actual_data, expected_data)


class TestResourceLockSet(TestResourceLock):
    def setUp(self):
        super().setUp()

        self.lock = share_fakes.FakeResourceLock.create_one_lock()
        self.lock.update = mock.Mock()

        self.locks_mock.get.return_value = self.lock

        self.cmd = resource_locks.SetResourceLock(self.app, None)

    def test_share_lock_set_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_lock_set(self):
        arglist = [
            self.lock.id,
            '--resource-action',
            'unmanage',
        ]
        verifylist = [('lock', self.lock.id), ('resource_action', 'unmanage')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.locks_mock.update.assert_called_with(
            self.lock.id, resource_action='unmanage'
        )


class TestResourceLockUnSet(TestResourceLock):
    def setUp(self):
        super().setUp()

        self.lock = share_fakes.FakeResourceLock.create_one_lock()
        self.lock.update = mock.Mock()

        self.locks_mock.get.return_value = self.lock

        self.cmd = resource_locks.UnsetResourceLock(self.app, None)

    def test_share_lock_unset_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_share_lock_unset(self):
        arglist = [self.lock.id, '--lock-reason']
        verifylist = [('lock', self.lock.id), ('lock_reason', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.locks_mock.update.assert_called_with(
            self.lock.id, lock_reason=None
        )
