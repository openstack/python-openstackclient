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

import copy

from openstackclient.tests import fakes
from openstackclient.tests.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import snapshot


class TestSnapshot(volume_fakes.TestVolume):

    def setUp(self):
        super(TestSnapshot, self).setUp()

        self.snapshots_mock = self.app.client_manager.volume.volume_snapshots
        self.snapshots_mock.reset_mock()
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()


class TestSnapshotCreate(TestSnapshot):
    def setUp(self):
        super(TestSnapshotCreate, self).setUp()

        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True
        )

        self.snapshots_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.SNAPSHOT),
            loaded=True
        )
        # Get the command object to test
        self.cmd = snapshot.CreateSnapshot(self.app, None)

    def test_snapshot_create(self):
        arglist = [
            volume_fakes.volume_id,
            "--name", volume_fakes.snapshot_name,
            "--description", volume_fakes.snapshot_description,
            "--force"
        ]
        verifylist = [
            ("volume", volume_fakes.volume_id),
            ("name", volume_fakes.snapshot_name),
            ("description", volume_fakes.snapshot_description),
            ("force", True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.snapshots_mock.create.assert_called_with(
            volume_fakes.volume_id,
            force=True,
            name=volume_fakes.snapshot_name,
            description=volume_fakes.snapshot_description
        )
        self.assertEqual(columns, volume_fakes.SNAPSHOT_columns)
        self.assertEqual(data, volume_fakes.SNAPSHOT_data)


class TestSnapshotShow(TestSnapshot):
    def setUp(self):
        super(TestSnapshotShow, self).setUp()

        self.snapshots_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.SNAPSHOT),
            loaded=True)
        # Get the command object to test
        self.cmd = snapshot.ShowSnapshot(self.app, None)

    def test_snapshot_show(self):
        arglist = [
            volume_fakes.snapshot_id
        ]
        verifylist = [
            ("snapshot", volume_fakes.snapshot_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.snapshots_mock.get.assert_called_with(volume_fakes.snapshot_id)

        self.assertEqual(volume_fakes.SNAPSHOT_columns, columns)
        self.assertEqual(volume_fakes.SNAPSHOT_data, data)


class TestSnapshotDelete(TestSnapshot):
    def setUp(self):
        super(TestSnapshotDelete, self).setUp()

        self.snapshots_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.SNAPSHOT),
            loaded=True)
        self.snapshots_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = snapshot.DeleteSnapshot(self.app, None)

    def test_snapshot_delete(self):
        arglist = [
            volume_fakes.snapshot_id
        ]
        verifylist = [
            ("snapshots", [volume_fakes.snapshot_id])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.snapshots_mock.delete.assert_called_with(volume_fakes.snapshot_id)


class TestSnapshotSet(TestSnapshot):
    def setUp(self):
        super(TestSnapshotSet, self).setUp()

        self.snapshots_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.SNAPSHOT),
            loaded=True
        )
        self.snapshots_mock.set_metadata.return_value = None
        self.snapshots_mock.update.return_value = None
        # Get the command object to mock
        self.cmd = snapshot.SetSnapshot(self.app, None)

    def test_snapshot_set(self):
        arglist = [
            volume_fakes.snapshot_id,
            "--name", "new_snapshot",
            "--property", "x=y",
            "--property", "foo=foo"
        ]
        new_property = {"x": "y", "foo": "foo"}
        verifylist = [
            ("snapshot", volume_fakes.snapshot_id),
            ("name", "new_snapshot"),
            ("property", new_property)
        ]

        kwargs = {
            "name": "new_snapshot",
        }
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.snapshots_mock.update.assert_called_with(
            volume_fakes.snapshot_id, **kwargs)
        self.snapshots_mock.set_metadata.assert_called_with(
            volume_fakes.snapshot_id, new_property
        )


class TestSnapshotUnset(TestSnapshot):
    def setUp(self):
        super(TestSnapshotUnset, self).setUp()

        self.snapshots_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.SNAPSHOT),
            loaded=True
        )
        self.snapshots_mock.delete_metadata.return_value = None
        # Get the command object to mock
        self.cmd = snapshot.UnsetSnapshot(self.app, None)

    def test_snapshot_unset(self):
        arglist = [
            volume_fakes.snapshot_id,
            "--property", "foo"
        ]
        verifylist = [
            ("snapshot", volume_fakes.snapshot_id),
            ("property", ["foo"])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.snapshots_mock.delete_metadata.assert_called_with(
            volume_fakes.snapshot_id, ["foo"]
        )


class TestSnapshotList(TestSnapshot):
    def setUp(self):
        super(TestSnapshotList, self).setUp()

        self.volumes_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(volume_fakes.VOLUME),
                loaded=True
            )
        ]
        self.snapshots_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(volume_fakes.SNAPSHOT),
                loaded=True
            )
        ]
        # Get the command to test
        self.cmd = snapshot.ListSnapshot(self.app, None)

    def test_snapshot_list_without_options(self):
        arglist = []
        verifylist = [
            ("long", False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        collist = ["ID", "Name", "Description", "Status", "Size"]
        self.assertEqual(collist, columns)
        datalist = ((
            volume_fakes.snapshot_id,
            volume_fakes.snapshot_name,
            volume_fakes.snapshot_description,
            "available",
            volume_fakes.snapshot_size
            ),)
        self.assertEqual(datalist, tuple(data))

    def test_snapshot_list_with_options(self):
        arglist = ["--long"]
        verifylist = [("long", True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        collist = ["ID", "Name", "Description", "Status", "Size", "Created At",
                   "Volume", "Properties"]
        self.assertEqual(collist, columns)

        datalist = ((
            volume_fakes.snapshot_id,
            volume_fakes.snapshot_name,
            volume_fakes.snapshot_description,
            "available",
            volume_fakes.snapshot_size,
            "2015-06-03T18:49:19.000000",
            volume_fakes.volume_name,
            volume_fakes.EXPECTED_SNAPSHOT.get("properties")
        ),)
        self.assertEqual(datalist, tuple(data))
