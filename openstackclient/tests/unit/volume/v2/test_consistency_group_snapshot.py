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

from mock import call

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import consistency_group_snapshot


class TestConsistencyGroupSnapshot(volume_fakes.TestVolume):

    def setUp(self):
        super(TestConsistencyGroupSnapshot, self).setUp()

        # Get a shortcut to the TransferManager Mock
        self.cgsnapshots_mock = (
            self.app.client_manager.volume.cgsnapshots)
        self.cgsnapshots_mock.reset_mock()
        self.consistencygroups_mock = (
            self.app.client_manager.volume.consistencygroups)
        self.consistencygroups_mock.reset_mock()


class TestConsistencyGroupSnapshotCreate(TestConsistencyGroupSnapshot):

    _consistency_group_snapshot = (
        volume_fakes.
        FakeConsistencyGroupSnapshot.
        create_one_consistency_group_snapshot()
    )
    consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group())

    columns = (
        'consistencygroup_id',
        'created_at',
        'description',
        'id',
        'name',
        'status',
    )
    data = (
        _consistency_group_snapshot.consistencygroup_id,
        _consistency_group_snapshot.created_at,
        _consistency_group_snapshot.description,
        _consistency_group_snapshot.id,
        _consistency_group_snapshot.name,
        _consistency_group_snapshot.status,
    )

    def setUp(self):
        super(TestConsistencyGroupSnapshotCreate, self).setUp()
        self.cgsnapshots_mock.create.return_value = (
            self._consistency_group_snapshot)
        self.consistencygroups_mock.get.return_value = (
            self.consistency_group)

        # Get the command object to test
        self.cmd = (consistency_group_snapshot.
                    CreateConsistencyGroupSnapshot(self.app, None))

    def test_consistency_group_snapshot_create(self):
        arglist = [
            '--consistency-group', self.consistency_group.id,
            '--description', self._consistency_group_snapshot.description,
            self._consistency_group_snapshot.name,
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('description', self._consistency_group_snapshot.description),
            ('snapshot_name', self._consistency_group_snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.get.assert_called_once_with(
            self.consistency_group.id)
        self.cgsnapshots_mock.create.assert_called_once_with(
            self.consistency_group.id,
            name=self._consistency_group_snapshot.name,
            description=self._consistency_group_snapshot.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_consistency_group_snapshot_create_no_consistency_group(self):
        arglist = [
            '--description', self._consistency_group_snapshot.description,
            self._consistency_group_snapshot.name,
        ]
        verifylist = [
            ('description', self._consistency_group_snapshot.description),
            ('snapshot_name', self._consistency_group_snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.consistencygroups_mock.get.assert_called_once_with(
            self._consistency_group_snapshot.name)
        self.cgsnapshots_mock.create.assert_called_once_with(
            self.consistency_group.id,
            name=self._consistency_group_snapshot.name,
            description=self._consistency_group_snapshot.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestConsistencyGroupSnapshotDelete(TestConsistencyGroupSnapshot):

    consistency_group_snapshots = (
        volume_fakes.FakeConsistencyGroupSnapshot.
        create_consistency_group_snapshots(count=2)
    )

    def setUp(self):
        super(TestConsistencyGroupSnapshotDelete, self).setUp()

        self.cgsnapshots_mock.get = (
            volume_fakes.FakeConsistencyGroupSnapshot.
            get_consistency_group_snapshots(self.consistency_group_snapshots)
        )
        self.cgsnapshots_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = (consistency_group_snapshot.
                    DeleteConsistencyGroupSnapshot(self.app, None))

    def test_consistency_group_snapshot_delete(self):
        arglist = [
            self.consistency_group_snapshots[0].id
        ]
        verifylist = [
            ("consistency_group_snapshot",
             [self.consistency_group_snapshots[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.cgsnapshots_mock.delete.assert_called_once_with(
            self.consistency_group_snapshots[0].id)
        self.assertIsNone(result)

    def test_multiple_consistency_group_snapshots_delete(self):
        arglist = []
        for c in self.consistency_group_snapshots:
            arglist.append(c.id)
        verifylist = [
            ('consistency_group_snapshot', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for c in self.consistency_group_snapshots:
            calls.append(call(c.id))
        self.cgsnapshots_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)


class TestConsistencyGroupSnapshotList(TestConsistencyGroupSnapshot):

    consistency_group_snapshots = (
        volume_fakes.FakeConsistencyGroupSnapshot.
        create_consistency_group_snapshots(count=2)
    )
    consistency_group = (
        volume_fakes.FakeConsistencyGroup.create_one_consistency_group()
    )

    columns = [
        'ID',
        'Status',
        'Name',
    ]
    columns_long = [
        'ID',
        'Status',
        'ConsistencyGroup ID',
        'Name',
        'Description',
        'Created At',
    ]
    data = []
    for c in consistency_group_snapshots:
        data.append((
            c.id,
            c.status,
            c.name,
        ))
    data_long = []
    for c in consistency_group_snapshots:
        data_long.append((
            c.id,
            c.status,
            c.consistencygroup_id,
            c.name,
            c.description,
            c.created_at,
        ))

    def setUp(self):
        super(TestConsistencyGroupSnapshotList, self).setUp()

        self.cgsnapshots_mock.list.return_value = (
            self.consistency_group_snapshots)
        self.consistencygroups_mock.get.return_value = self.consistency_group
        # Get the command to test
        self.cmd = (
            consistency_group_snapshot.
            ListConsistencyGroupSnapshot(self.app, None)
        )

    def test_consistency_group_snapshot_list_without_options(self):
        arglist = []
        verifylist = [
            ("all_projects", False),
            ("long", False),
            ("status", None),
            ("consistency_group", None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'status': None,
            'consistencygroup_id': None,
        }
        self.cgsnapshots_mock.list.assert_called_once_with(
            detailed=True, search_opts=search_opts)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_consistency_group_snapshot_list_with_long(self):
        arglist = [
            "--long",
        ]
        verifylist = [
            ("all_projects", False),
            ("long", True),
            ("status", None),
            ("consistency_group", None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'status': None,
            'consistencygroup_id': None,
        }
        self.cgsnapshots_mock.list.assert_called_once_with(
            detailed=True, search_opts=search_opts)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_consistency_group_snapshot_list_with_options(self):
        arglist = [
            "--all-project",
            "--status", self.consistency_group_snapshots[0].status,
            "--consistency-group", self.consistency_group.id,
        ]
        verifylist = [
            ("all_projects", True),
            ("long", False),
            ("status", self.consistency_group_snapshots[0].status),
            ("consistency_group", self.consistency_group.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'status': self.consistency_group_snapshots[0].status,
            'consistencygroup_id': self.consistency_group.id,
        }
        self.consistencygroups_mock.get.assert_called_once_with(
            self.consistency_group.id)
        self.cgsnapshots_mock.list.assert_called_once_with(
            detailed=True, search_opts=search_opts)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestConsistencyGroupSnapshotShow(TestConsistencyGroupSnapshot):

    _consistency_group_snapshot = (
        volume_fakes.
        FakeConsistencyGroupSnapshot.
        create_one_consistency_group_snapshot()
    )

    columns = (
        'consistencygroup_id',
        'created_at',
        'description',
        'id',
        'name',
        'status',
    )
    data = (
        _consistency_group_snapshot.consistencygroup_id,
        _consistency_group_snapshot.created_at,
        _consistency_group_snapshot.description,
        _consistency_group_snapshot.id,
        _consistency_group_snapshot.name,
        _consistency_group_snapshot.status,
    )

    def setUp(self):
        super(TestConsistencyGroupSnapshotShow, self).setUp()

        self.cgsnapshots_mock.get.return_value = (
            self._consistency_group_snapshot)
        self.cmd = (consistency_group_snapshot.
                    ShowConsistencyGroupSnapshot(self.app, None))

    def test_consistency_group_snapshot_show(self):
        arglist = [
            self._consistency_group_snapshot.id
        ]
        verifylist = [
            ("consistency_group_snapshot", self._consistency_group_snapshot.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.cgsnapshots_mock.get.assert_called_once_with(
            self._consistency_group_snapshot.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
