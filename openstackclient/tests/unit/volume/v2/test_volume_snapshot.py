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

from openstack.block_storage.v2 import snapshot as _snapshot
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.identity.v3 import fakes as project_fakes
from openstackclient.tests.unit import utils as test_utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_snapshot


class TestVolumeSnapshotCreate(volume_fakes.TestVolume):
    columns = (
        'created_at',
        'description',
        'id',
        'name',
        'properties',
        'size',
        'status',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.snapshot = sdk_fakes.generate_fake_resource(
            _snapshot.Snapshot, volume_id=self.volume.id
        )
        self.volume_sdk_client.create_snapshot.return_value = self.snapshot
        self.volume_sdk_client.manage_snapshot.return_value = self.snapshot

        self.data = (
            self.snapshot.created_at,
            self.snapshot.description,
            self.snapshot.id,
            self.snapshot.name,
            format_columns.DictColumn(self.snapshot.metadata),
            self.snapshot.size,
            self.snapshot.status,
            self.snapshot.volume_id,
        )

        self.cmd = volume_snapshot.CreateVolumeSnapshot(self.app, None)

    def test_snapshot_create(self):
        arglist = [
            "--volume",
            self.snapshot.volume_id,
            "--description",
            self.snapshot.description,
            "--force",
            '--property',
            'Alpha=a',
            '--property',
            'Beta=b',
            self.snapshot.name,
        ]
        verifylist = [
            ("volume", self.snapshot.volume_id),
            ("description", self.snapshot.description),
            ("force", True),
            ('properties', {'Alpha': 'a', 'Beta': 'b'}),
            ("snapshot_name", self.snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.snapshot.volume_id, ignore_missing=False
        )
        self.volume_sdk_client.create_snapshot.assert_called_with(
            volume_id=self.snapshot.volume_id,
            force=True,
            name=self.snapshot.name,
            description=self.snapshot.description,
            metadata={'Alpha': 'a', 'Beta': 'b'},
        )

    def test_snapshot_create_without_name(self):
        arglist = [
            "--volume",
            self.snapshot.volume_id,
        ]
        verifylist = [
            ("volume", self.snapshot.volume_id),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_snapshot_create_without_volume(self):
        arglist = [
            "--description",
            self.snapshot.description,
            "--force",
            self.snapshot.name,
        ]
        verifylist = [
            ("description", self.snapshot.description),
            ("force", True),
            ("snapshot_name", self.snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.snapshot.name, ignore_missing=False
        )
        self.volume_sdk_client.create_snapshot.assert_called_once_with(
            volume_id=self.snapshot.volume_id,
            force=True,
            name=self.snapshot.name,
            description=self.snapshot.description,
            metadata=None,
        )

    def test_snapshot_create_with_remote_source(self):
        arglist = [
            '--remote-source',
            'source-name=test_source_name',
            '--remote-source',
            'source-id=test_source_id',
            '--volume',
            self.snapshot.volume_id,
            self.snapshot.name,
        ]
        ref_dict = {
            'source-name': 'test_source_name',
            'source-id': 'test_source_id',
        }
        verifylist = [
            ('remote_source', ref_dict),
            ('volume', self.snapshot.volume_id),
            ("snapshot_name", self.snapshot.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
        self.volume_sdk_client.find_volume.assert_called_once_with(
            self.snapshot.volume_id, ignore_missing=False
        )
        self.volume_sdk_client.manage_snapshot.assert_called_with(
            volume_id=self.snapshot.volume_id,
            ref=ref_dict,
            name=self.snapshot.name,
            description=None,
            metadata=None,
        )
        self.volume_sdk_client.create_snapshot.assert_not_called()


class TestVolumeSnapshotDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.snapshots = list(
            sdk_fakes.generate_fake_resources(_snapshot.Snapshot)
        )
        self.volume_sdk_client.find_snapshot.side_effect = self.snapshots
        self.volume_sdk_client.delete_snapshot.return_value = None

        self.cmd = volume_snapshot.DeleteVolumeSnapshot(self.app, None)

    def test_snapshot_delete(self):
        arglist = [self.snapshots[0].id]
        verifylist = [("snapshots", [self.snapshots[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_snapshot.assert_called_once_with(
            self.snapshots[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_snapshot.assert_called_once_with(
            self.snapshots[0].id, force=False
        )

    def test_snapshot_delete_with_force(self):
        arglist = ['--force', self.snapshots[0].id]
        verifylist = [('force', True), ("snapshots", [self.snapshots[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_snapshot.assert_called_once_with(
            self.snapshots[0].id, ignore_missing=False
        )
        self.volume_sdk_client.delete_snapshot.assert_called_once_with(
            self.snapshots[0].id, force=True
        )

    def test_delete_multiple_snapshots(self):
        arglist = []
        for s in self.snapshots:
            arglist.append(s.id)
        verifylist = [
            ('snapshots', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_sdk_client.find_snapshot.assert_has_calls(
            [mock.call(x.id, ignore_missing=False) for x in self.snapshots]
        )
        self.volume_sdk_client.delete_snapshot.assert_has_calls(
            [mock.call(x.id, force=False) for x in self.snapshots]
        )

    def test_delete_multiple_snapshots_with_exception(self):
        self.volume_sdk_client.find_snapshot.side_effect = [
            self.snapshots[0],
            sdk_exceptions.NotFoundException(),
        ]

        arglist = [
            self.snapshots[0].id,
            'unexist_snapshot',
        ]
        verifylist = [
            ('snapshots', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertEqual('1 of 2 snapshots failed to delete.', str(exc))

        self.volume_sdk_client.find_snapshot.assert_has_calls(
            [
                mock.call(self.snapshots[0].id, ignore_missing=False),
                mock.call('unexist_snapshot', ignore_missing=False),
            ]
        )
        self.volume_sdk_client.delete_snapshot.assert_has_calls(
            [
                mock.call(self.snapshots[0].id, force=False),
            ]
        )


class TestVolumeSnapshotList(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.snapshots = list(
            sdk_fakes.generate_fake_resources(
                _snapshot.Snapshot, attrs={'volume_id': self.volume.name}
            )
        )
        self.project = project_fakes.FakeProject.create_one_project()
        self.volume_sdk_client.volumes.return_value = [self.volume]
        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.snapshots.return_value = self.snapshots
        self.project_mock = self.identity_client.projects
        self.project_mock.get.return_value = self.project

        self.columns = ("ID", "Name", "Description", "Status", "Size")
        self.columns_long = self.columns + (
            "Created At",
            "Volume",
            "Properties",
        )

        self.data = []
        self.data_long = []
        for s in self.snapshots:
            self.data.append(
                (
                    s.id,
                    s.name,
                    s.description,
                    s.status,
                    s.size,
                )
            )
            self.data_long.append(
                (
                    s.id,
                    s.name,
                    s.description,
                    s.status,
                    s.size,
                    s.created_at,
                    volume_snapshot.VolumeIdColumn(
                        s.volume_id, volume_cache={self.volume.id: self.volume}
                    ),
                    format_columns.DictColumn(s.metadata),
                )
            )

        self.cmd = volume_snapshot.ListVolumeSnapshot(self.app, None)

    def test_snapshot_list_without_options(self):
        arglist = []
        verifylist = [('all_projects', False), ('long', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.snapshots.assert_called_once_with(
            limit=None,
            marker=None,
            all_projects=False,
            name=None,
            status=None,
            project_id=None,
            volume_id=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_snapshot_list_with_options(self):
        arglist = [
            "--long",
            "--limit",
            "2",
            "--project",
            self.project.id,
            "--marker",
            self.snapshots[0].id,
        ]
        verifylist = [
            ("long", True),
            ("limit", 2),
            ("project", self.project.id),
            ("marker", self.snapshots[0].id),
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.snapshots.assert_called_once_with(
            limit=2,
            marker=self.snapshots[0].id,
            all_projects=True,
            project_id=self.project.id,
            name=None,
            status=None,
            volume_id=None,
        )
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_snapshot_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [('long', False), ('all_projects', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.snapshots.assert_called_once_with(
            limit=None,
            marker=None,
            all_projects=True,
            name=None,
            status=None,
            project_id=None,
            volume_id=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_snapshot_list_name_option(self):
        arglist = [
            '--name',
            self.snapshots[0].name,
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('name', self.snapshots[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.snapshots.assert_called_once_with(
            limit=None,
            marker=None,
            all_projects=False,
            name=self.snapshots[0].name,
            status=None,
            project_id=None,
            volume_id=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_snapshot_list_status_option(self):
        arglist = [
            '--status',
            'available',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('status', 'available'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.snapshots.assert_called_once_with(
            limit=None,
            marker=None,
            all_projects=False,
            name=None,
            status='available',
            project_id=None,
            volume_id=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_snapshot_list_volumeid_option(self):
        arglist = [
            '--volume',
            self.volume.id,
        ]
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.snapshots.assert_called_once_with(
            limit=None,
            marker=None,
            all_projects=False,
            name=None,
            status=None,
            project_id=None,
            volume_id=self.volume.id,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_snapshot_list_negative_limit(self):
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


class TestVolumeSnapshotSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.snapshot = sdk_fakes.generate_fake_resource(
            _snapshot.Snapshot, metadata={'foo': 'bar'}
        )
        self.volume_sdk_client.find_snapshot.return_value = self.snapshot
        self.volume_sdk_client.delete_snapshot_metadata.return_value = None
        self.volume_sdk_client.set_snapshot_metadata.return_value = None
        self.volume_sdk_client.update_snapshot.return_value = None

        self.cmd = volume_snapshot.SetVolumeSnapshot(self.app, None)

    def test_snapshot_set_no_option(self):
        arglist = [
            self.snapshot.id,
        ]
        verifylist = [
            ("snapshot", self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.volume_sdk_client.find_snapshot.assert_called_once_with(
            parsed_args.snapshot, ignore_missing=False
        )
        self.volume_sdk_client.reset_snapshot_status.assert_not_called()
        self.volume_sdk_client.update_snapshot.assert_not_called()
        self.volume_sdk_client.set_snapshot_metadata.assert_not_called()

    def test_snapshot_set_name_and_property(self):
        arglist = [
            "--name",
            "new_snapshot",
            "--property",
            "x=y",
            "--property",
            "foo=foo",
            self.snapshot.id,
        ]
        verifylist = [
            ("name", "new_snapshot"),
            ("properties", {"x": "y", "foo": "foo"}),
            ("snapshot", self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.volume_sdk_client.update_snapshot.assert_called_with(
            self.snapshot.id, name="new_snapshot"
        )
        self.volume_sdk_client.set_snapshot_metadata.assert_called_with(
            self.snapshot.id, x="y", foo="foo"
        )

    def test_snapshot_set_with_no_property(self):
        arglist = [
            "--no-property",
            self.snapshot.id,
        ]
        verifylist = [
            ("no_property", True),
            ("snapshot", self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.volume_sdk_client.find_snapshot.assert_called_once_with(
            parsed_args.snapshot, ignore_missing=False
        )
        self.volume_sdk_client.reset_snapshot_status.assert_not_called()
        self.volume_sdk_client.update_snapshot.assert_not_called()
        self.volume_sdk_client.set_snapshot_metadata.assert_not_called()
        self.volume_sdk_client.delete_snapshot_metadata.assert_called_with(
            self.snapshot.id, keys=["foo"]
        )

    def test_snapshot_set_with_no_property_and_property(self):
        arglist = [
            "--no-property",
            "--property",
            "foo_1=bar_1",
            self.snapshot.id,
        ]
        verifylist = [
            ("no_property", True),
            ("properties", {"foo_1": "bar_1"}),
            ("snapshot", self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.volume_sdk_client.find_snapshot.assert_called_once_with(
            parsed_args.snapshot, ignore_missing=False
        )
        self.volume_sdk_client.reset_snapshot_status.assert_not_called()
        self.volume_sdk_client.update_snapshot.assert_not_called()
        self.volume_sdk_client.delete_snapshot_metadata.assert_called_with(
            self.snapshot.id, keys=["foo"]
        )
        self.volume_sdk_client.set_snapshot_metadata.assert_called_once_with(
            self.snapshot.id,
            foo_1="bar_1",
        )

    def test_snapshot_set_state_to_error(self):
        arglist = ["--state", "error", self.snapshot.id]
        verifylist = [("state", "error"), ("snapshot", self.snapshot.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.volume_sdk_client.reset_snapshot_status.assert_called_with(
            self.snapshot.id, "error"
        )

    def test_volume_set_state_failed(self):
        self.volume_sdk_client.reset_snapshot_status.side_effect = (
            exceptions.CommandError()
        )
        arglist = ['--state', 'error', self.snapshot.id]
        verifylist = [('state', 'error'), ('snapshot', self.snapshot.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertEqual('One or more of the set operations failed', str(exc))
        self.volume_sdk_client.reset_snapshot_status.assert_called_once_with(
            self.snapshot.id, 'error'
        )

    def test_volume_set_name_and_state_failed(self):
        self.volume_sdk_client.reset_snapshot_status.side_effect = (
            exceptions.CommandError()
        )
        arglist = [
            '--state',
            'error',
            "--name",
            "new_snapshot",
            self.snapshot.id,
        ]
        verifylist = [
            ('state', 'error'),
            ("name", "new_snapshot"),
            ('snapshot', self.snapshot.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

        self.assertEqual('One or more of the set operations failed', str(exc))
        self.volume_sdk_client.update_snapshot.assert_called_once_with(
            self.snapshot.id, name="new_snapshot"
        )
        self.volume_sdk_client.reset_snapshot_status.assert_called_once_with(
            self.snapshot.id, 'error'
        )


class TestVolumeSnapshotShow(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.snapshot = sdk_fakes.generate_fake_resource(_snapshot.Snapshot)

        self.columns = (
            'created_at',
            'description',
            'id',
            'name',
            'properties',
            'size',
            'status',
            'volume_id',
        )
        self.data = (
            self.snapshot.created_at,
            self.snapshot.description,
            self.snapshot.id,
            self.snapshot.name,
            format_columns.DictColumn(self.snapshot.metadata),
            self.snapshot.size,
            self.snapshot.status,
            self.snapshot.volume_id,
        )

        self.volume_sdk_client.find_snapshot.return_value = self.snapshot

        self.cmd = volume_snapshot.ShowVolumeSnapshot(self.app, None)

    def test_snapshot_show(self):
        arglist = [self.snapshot.id]
        verifylist = [("snapshot", self.snapshot.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_sdk_client.find_snapshot.assert_called_with(
            self.snapshot.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestVolumeSnapshotUnset(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.snapshot = sdk_fakes.generate_fake_resource(_snapshot.Snapshot)
        self.volume_sdk_client.find_snapshot.return_value = self.snapshot
        self.volume_sdk_client.delete_snapshot_metadata.return_value = None

        self.cmd = volume_snapshot.UnsetVolumeSnapshot(self.app, None)

    def test_snapshot_unset(self):
        arglist = [
            "--property",
            "foo",
            self.snapshot.id,
        ]
        verifylist = [
            ("properties", ["foo"]),
            ("snapshot", self.snapshot.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.volume_sdk_client.delete_snapshot_metadata.assert_called_with(
            self.snapshot.id, keys=["foo"]
        )
