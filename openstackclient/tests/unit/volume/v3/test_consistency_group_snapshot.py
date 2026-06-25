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

from unittest.mock import call

from openstack.block_storage.v3 import consistency_group as _consistency_group
from openstack.block_storage.v3 import (
    consistency_group_snapshot as _cg_snapshot,
)
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import consistency_group_snapshot


class TestConsistencyGroupSnapshotCreate(volume_fakes.TestVolume):
    _consistency_group_snapshot = sdk_fakes.generate_fake_resource(
        _cg_snapshot.ConsistencyGroupSnapshot
    )
    consistency_group = sdk_fakes.generate_fake_resource(
        _consistency_group.ConsistencyGroup
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
        super().setUp()
        self.volume_client.create_consistency_group_snapshot.return_value = (
            self._consistency_group_snapshot
        )
        self.volume_client.find_consistency_group.return_value = (
            self.consistency_group
        )

        # Get the command object to test
        self.cmd = consistency_group_snapshot.CreateConsistencyGroupSnapshot(
            self.app, None
        )

    def test_consistency_group_snapshot_create(self):
        arglist = [
            '--consistency-group',
            self.consistency_group.id,
            '--description',
            self._consistency_group_snapshot.description,
            self._consistency_group_snapshot.name,
        ]
        verifylist = [
            ('consistency_group', self.consistency_group.id),
            ('description', self._consistency_group_snapshot.description),
            ('snapshot_name', self._consistency_group_snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_client.create_consistency_group_snapshot.assert_called_once_with(
            consistencygroup_id=self.consistency_group.id,
            name=self._consistency_group_snapshot.name,
            description=self._consistency_group_snapshot.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_consistency_group_snapshot_create_no_consistency_group(self):
        arglist = [
            '--description',
            self._consistency_group_snapshot.description,
            self._consistency_group_snapshot.name,
        ]
        verifylist = [
            ('description', self._consistency_group_snapshot.description),
            ('snapshot_name', self._consistency_group_snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.find_consistency_group.assert_called_once_with(
            self._consistency_group_snapshot.name, ignore_missing=False
        )
        self.volume_client.create_consistency_group_snapshot.assert_called_once_with(
            consistencygroup_id=self.consistency_group.id,
            name=self._consistency_group_snapshot.name,
            description=self._consistency_group_snapshot.description,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestConsistencyGroupSnapshotDelete(volume_fakes.TestVolume):
    consistency_group_snapshots = [
        sdk_fakes.generate_fake_resource(
            _cg_snapshot.ConsistencyGroupSnapshot
        ),
        sdk_fakes.generate_fake_resource(
            _cg_snapshot.ConsistencyGroupSnapshot
        ),
    ]

    def setUp(self):
        super().setUp()

        self.volume_client.find_consistency_group_snapshot.side_effect = (
            self.consistency_group_snapshots
        )
        self.volume_client.delete_consistency_group_snapshot.return_value = (
            None
        )

        # Get the command object to mock
        self.cmd = consistency_group_snapshot.DeleteConsistencyGroupSnapshot(
            self.app, None
        )

    def test_consistency_group_snapshot_delete(self):
        arglist = [self.consistency_group_snapshots[0].id]
        verifylist = [
            (
                "consistency_group_snapshot",
                [self.consistency_group_snapshots[0].id],
            )
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_client.find_consistency_group_snapshot.assert_called_once_with(
            self.consistency_group_snapshots[0].id, ignore_missing=False
        )
        self.volume_client.delete_consistency_group_snapshot.assert_called_once_with(
            self.consistency_group_snapshots[0]
        )
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

        find_calls = []
        delete_calls = []
        for c in self.consistency_group_snapshots:
            find_calls.append(call(c.id, ignore_missing=False))
            delete_calls.append(call(c))
        self.volume_client.find_consistency_group_snapshot.assert_has_calls(
            find_calls
        )
        self.volume_client.delete_consistency_group_snapshot.assert_has_calls(
            delete_calls
        )
        self.assertIsNone(result)

    def test_delete_with_exception(self):
        arglist = ['missing-snapshot']
        verifylist = [('consistency_group_snapshot', ['missing-snapshot'])]

        self.volume_client.find_consistency_group_snapshot.side_effect = (
            exceptions.CommandError
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestConsistencyGroupSnapshotList(volume_fakes.TestVolume):
    consistency_group_snapshots = [
        sdk_fakes.generate_fake_resource(
            _cg_snapshot.ConsistencyGroupSnapshot, status='available'
        ),
        sdk_fakes.generate_fake_resource(
            _cg_snapshot.ConsistencyGroupSnapshot, status='available'
        ),
    ]
    consistency_group = sdk_fakes.generate_fake_resource(
        _consistency_group.ConsistencyGroup
    )

    column_headers = [
        'ID',
        'Status',
        'Name',
    ]
    column_headers_long = [
        'ID',
        'Status',
        'ConsistencyGroup ID',
        'Name',
        'Description',
        'Created At',
    ]
    data = []
    for c in consistency_group_snapshots:
        data.append(
            (
                c.id,
                c.status,
                c.name,
            )
        )
    data_long = []
    for c in consistency_group_snapshots:
        data_long.append(
            (
                c.id,
                c.status,
                c.consistencygroup_id,
                c.name,
                c.description,
                c.created_at,
            )
        )

    def setUp(self):
        super().setUp()

        self.volume_client.consistency_group_snapshots.return_value = (
            self.consistency_group_snapshots
        )
        self.volume_client.find_consistency_group.return_value = (
            self.consistency_group
        )
        # Get the command to test
        self.cmd = consistency_group_snapshot.ListConsistencyGroupSnapshot(
            self.app, None
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

        self.volume_client.consistency_group_snapshots.assert_called_once_with(
            all_tenants=False,
            status=None,
            consistencygroup_id=None,
        )
        self.assertEqual(self.column_headers, columns)
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

        self.volume_client.consistency_group_snapshots.assert_called_once_with(
            all_tenants=False,
            status=None,
            consistencygroup_id=None,
        )
        self.assertEqual(self.column_headers_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_consistency_group_snapshot_list_with_options(self):
        arglist = [
            "--all-project",
            "--status",
            self.consistency_group_snapshots[0].status,
            "--consistency-group",
            self.consistency_group.id,
        ]
        verifylist = [
            ("all_projects", True),
            ("long", False),
            ("status", self.consistency_group_snapshots[0].status),
            ("consistency_group", self.consistency_group.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.find_consistency_group.assert_called_once_with(
            self.consistency_group.id, ignore_missing=False
        )
        self.volume_client.consistency_group_snapshots.assert_called_once_with(
            all_tenants=True,
            status=self.consistency_group_snapshots[0].status,
            consistencygroup_id=self.consistency_group.id,
        )
        self.assertEqual(self.column_headers, columns)
        self.assertEqual(self.data, list(data))


class TestConsistencyGroupSnapshotShow(volume_fakes.TestVolume):
    _consistency_group_snapshot = sdk_fakes.generate_fake_resource(
        _cg_snapshot.ConsistencyGroupSnapshot
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
        super().setUp()

        self.volume_client.find_consistency_group_snapshot.return_value = (
            self._consistency_group_snapshot
        )
        self.cmd = consistency_group_snapshot.ShowConsistencyGroupSnapshot(
            self.app, None
        )

    def test_consistency_group_snapshot_show(self):
        arglist = [self._consistency_group_snapshot.id]
        verifylist = [
            ("consistency_group_snapshot", self._consistency_group_snapshot.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.find_consistency_group_snapshot.assert_called_once_with(
            self._consistency_group_snapshot.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
