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

from unittest import mock

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes_v3
from openstackclient.volume.v3 import volume_snapshot


class TestVolumeSnapshot(volume_fakes_v3.TestVolume):
    def setUp(self):
        super().setUp()

        self.snapshots_mock = self.volume_client.volume_snapshots
        self.snapshots_mock.reset_mock()

        self.volume_sdk_client.unmanage_snapshot.return_value = None


class TestVolumeSnapshotDelete(TestVolumeSnapshot):
    snapshots = volume_fakes.create_snapshots(count=2)

    def setUp(self):
        super().setUp()

        self.snapshots_mock.get = volume_fakes.get_snapshots(self.snapshots)
        self.snapshots_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_snapshot.DeleteVolumeSnapshot(self.app, None)

    def test_snapshot_delete(self):
        arglist = [self.snapshots[0].id]
        verifylist = [("snapshots", [self.snapshots[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.snapshots_mock.delete.assert_called_with(
            self.snapshots[0].id, False
        )
        self.assertIsNone(result)

    def test_snapshot_delete_with_force(self):
        arglist = ['--force', self.snapshots[0].id]
        verifylist = [('force', True), ("snapshots", [self.snapshots[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.snapshots_mock.delete.assert_called_with(
            self.snapshots[0].id, True
        )
        self.assertIsNone(result)

    def test_delete_multiple_snapshots(self):
        arglist = []
        for s in self.snapshots:
            arglist.append(s.id)
        verifylist = [
            ('snapshots', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self.snapshots:
            calls.append(mock.call(s.id, False))
        self.snapshots_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_snapshots_with_exception(self):
        arglist = [
            self.snapshots[0].id,
            'unexist_snapshot',
        ]
        verifylist = [
            ('snapshots', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.snapshots[0], exceptions.CommandError]
        with mock.patch.object(
            utils, 'find_resource', side_effect=find_mock_result
        ) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 snapshots failed to delete.', str(e))

            find_mock.assert_any_call(
                self.snapshots_mock, self.snapshots[0].id
            )
            find_mock.assert_any_call(self.snapshots_mock, 'unexist_snapshot')

            self.assertEqual(2, find_mock.call_count)
            self.snapshots_mock.delete.assert_called_once_with(
                self.snapshots[0].id, False
            )

    def test_snapshot_delete_remote(self):
        arglist = ['--remote', self.snapshots[0].id]
        verifylist = [('remote', True), ("snapshots", [self.snapshots[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.unmanage_snapshot.assert_called_with(
            self.snapshots[0].id
        )
        self.assertIsNone(result)

    def test_snapshot_delete_with_remote_force(self):
        arglist = ['--remote', '--force', self.snapshots[0].id]
        verifylist = [
            ('remote', True),
            ('force', True),
            ("snapshots", [self.snapshots[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            "The --force option is not supported with the --remote parameter.",
            str(exc),
        )

    def test_delete_multiple_snapshots_remote(self):
        arglist = ['--remote']
        for s in self.snapshots:
            arglist.append(s.id)
        verifylist = [('remote', True), ('snapshots', arglist[1:])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self.snapshots:
            calls.append(mock.call(s.id))
        self.volume_sdk_client.unmanage_snapshot.assert_has_calls(calls)
        self.assertIsNone(result)
