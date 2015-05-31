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
