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

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils as test_utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume


class TestVolume(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()

        self.users_mock = self.identity_client.users
        self.users_mock.reset_mock()

        self.snapshots_mock = self.volume_client.volume_snapshots
        self.snapshots_mock.reset_mock()

        self.types_mock = self.volume_client.volume_types
        self.types_mock.reset_mock()

        self.consistencygroups_mock = self.volume_client.consistencygroups
        self.consistencygroups_mock.reset_mock()

    def setup_volumes_mock(self, count):
        volumes = volume_fakes.create_volumes(count=count)

        self.volumes_mock.get = volume_fakes.get_volumes(volumes, 0)
        return volumes


class TestVolumeCreate(TestVolume):
    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    columns = (
        'attachments',
        'availability_zone',
        'bootable',
        'description',
        'id',
        'name',
        'properties',
        'size',
        'snapshot_id',
        'status',
        'type',
    )

    def setUp(self):
        super().setUp()

        self.new_volume = volume_fakes.create_one_volume()
        self.volumes_mock.create.return_value = self.new_volume

        self.datalist = (
            self.new_volume.attachments,
            self.new_volume.availability_zone,
            self.new_volume.bootable,
            self.new_volume.description,
            self.new_volume.id,
            self.new_volume.name,
            format_columns.DictColumn(self.new_volume.metadata),
            self.new_volume.size,
            self.new_volume.snapshot_id,
            self.new_volume.status,
            self.new_volume.volume_type,
        )

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_min_options(self):
        arglist = [
            '--size',
            str(self.new_volume.size),
        ]
        verifylist = [
            ('size', self.new_volume.size),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=None,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_options(self):
        consistency_group = volume_fakes.create_one_consistency_group()
        self.consistencygroups_mock.get.return_value = consistency_group
        arglist = [
            '--size',
            str(self.new_volume.size),
            '--description',
            self.new_volume.description,
            '--type',
            self.new_volume.volume_type,
            '--availability-zone',
            self.new_volume.availability_zone,
            '--consistency-group',
            consistency_group.id,
            '--hint',
            'k=v',
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('description', self.new_volume.description),
            ('type', self.new_volume.volume_type),
            ('availability_zone', self.new_volume.availability_zone),
            ('consistency_group', consistency_group.id),
            ('hint', {'k': 'v'}),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=self.new_volume.description,
            volume_type=self.new_volume.volume_type,
            availability_zone=self.new_volume.availability_zone,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=consistency_group.id,
            scheduler_hints={'k': 'v'},
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_properties(self):
        arglist = [
            '--property',
            'Alpha=a',
            '--property',
            'Beta=b',
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('property', {'Alpha': 'a', 'Beta': 'b'}),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata={'Alpha': 'a', 'Beta': 'b'},
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_image_id(self):
        image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = image

        arglist = [
            '--image',
            image.id,
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('image', image.id),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=image.id,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_image_name(self):
        image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = image

        arglist = [
            '--image',
            image.name,
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('image', image.name),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=image.id,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_with_snapshot(self):
        snapshot = volume_fakes.create_one_snapshot()
        self.new_volume.snapshot_id = snapshot.id
        arglist = [
            '--snapshot',
            self.new_volume.snapshot_id,
            self.new_volume.name,
        ]
        verifylist = [
            ('snapshot', self.new_volume.snapshot_id),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.snapshots_mock.get.return_value = snapshot

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_once_with(
            size=snapshot.size,
            snapshot_id=snapshot.id,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_with_source_volume(self):
        source_vol = "source_vol"
        arglist = [
            '--source',
            self.new_volume.id,
            source_vol,
        ]
        verifylist = [
            ('source', self.new_volume.id),
            ('name', source_vol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.volumes_mock.get.return_value = self.new_volume

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_once_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=source_vol,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=self.new_volume.id,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    @mock.patch.object(utils, 'wait_for_status', return_value=True)
    def test_volume_create_with_bootable_and_readonly(self, mock_wait):
        arglist = [
            '--bootable',
            '--read-only',
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('bootable', True),
            ('non_bootable', False),
            ('read_only', True),
            ('read_write', False),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)
        self.volumes_mock.set_bootable.assert_called_with(
            self.new_volume.id, True
        )
        self.volumes_mock.update_readonly_flag.assert_called_with(
            self.new_volume.id, True
        )

    @mock.patch.object(utils, 'wait_for_status', return_value=True)
    def test_volume_create_with_nonbootable_and_readwrite(self, mock_wait):
        arglist = [
            '--non-bootable',
            '--read-write',
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('bootable', False),
            ('non_bootable', True),
            ('read_only', False),
            ('read_write', True),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)
        self.volumes_mock.set_bootable.assert_called_with(
            self.new_volume.id, False
        )
        self.volumes_mock.update_readonly_flag.assert_called_with(
            self.new_volume.id, False
        )

    @mock.patch.object(volume.LOG, 'error')
    @mock.patch.object(utils, 'wait_for_status', return_value=True)
    def test_volume_create_with_bootable_and_readonly_fail(
        self, mock_wait, mock_error
    ):
        self.volumes_mock.set_bootable.side_effect = exceptions.CommandError()

        self.volumes_mock.update_readonly_flag.side_effect = (
            exceptions.CommandError()
        )

        arglist = [
            '--bootable',
            '--read-only',
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('bootable', True),
            ('non_bootable', False),
            ('read_only', True),
            ('read_write', False),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(2, mock_error.call_count)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)
        self.volumes_mock.set_bootable.assert_called_with(
            self.new_volume.id, True
        )
        self.volumes_mock.update_readonly_flag.assert_called_with(
            self.new_volume.id, True
        )

    @mock.patch.object(volume.LOG, 'error')
    @mock.patch.object(utils, 'wait_for_status', return_value=False)
    def test_volume_create_non_available_with_readonly(
        self,
        mock_wait,
        mock_error,
    ):
        arglist = [
            '--non-bootable',
            '--read-only',
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('bootable', False),
            ('non_bootable', True),
            ('read_only', True),
            ('read_write', False),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints=None,
        )

        self.assertEqual(2, mock_error.call_count)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)

    def test_volume_create_without_size(self):
        arglist = [
            self.new_volume.name,
        ]
        verifylist = [
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_volume_create_with_multi_source(self):
        arglist = [
            '--image',
            'source_image',
            '--source',
            'source_volume',
            '--snapshot',
            'source_snapshot',
            '--size',
            str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('image', 'source_image'),
            ('source', 'source_volume'),
            ('snapshot', 'source_snapshot'),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_volume_create_hints(self):
        """--hint needs to behave differently based on the given hint

        different_host and same_host need to append to a list if given multiple
        times. All other parameter are strings.
        """
        arglist = [
            '--size',
            str(self.new_volume.size),
            '--hint',
            'k=v',
            '--hint',
            'k=v2',
            '--hint',
            'same_host=v3',
            '--hint',
            'same_host=v4',
            '--hint',
            'different_host=v5',
            '--hint',
            'local_to_instance=v6',
            '--hint',
            'different_host=v7',
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            (
                'hint',
                {
                    'k': 'v2',
                    'same_host': ['v3', 'v4'],
                    'local_to_instance': 'v6',
                    'different_host': ['v5', 'v7'],
                },
            ),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            size=self.new_volume.size,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            scheduler_hints={
                'k': 'v2',
                'same_host': ['v3', 'v4'],
                'local_to_instance': 'v6',
                'different_host': ['v5', 'v7'],
            },
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)


class TestVolumeDelete(TestVolume):
    def setUp(self):
        super().setUp()

        self.volumes_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume.DeleteVolume(self.app, None)

    def test_volume_delete_one_volume(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [volumes[0].id]
        verifylist = [
            ("force", False),
            ("purge", False),
            ("volumes", [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete.assert_called_once_with(
            volumes[0].id, cascade=False
        )
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes(self):
        volumes = self.setup_volumes_mock(count=3)

        arglist = [v.id for v in volumes]
        verifylist = [
            ('force', False),
            ('purge', False),
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [mock.call(v.id, cascade=False) for v in volumes]
        self.volumes_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes_with_exception(self):
        volumes = self.setup_volumes_mock(count=2)

        arglist = [
            volumes[0].id,
            'unexist_volume',
        ]
        verifylist = [
            ('force', False),
            ('purge', False),
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [volumes[0], exceptions.CommandError]
        with mock.patch.object(
            utils, 'find_resource', side_effect=find_mock_result
        ) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 volumes failed to delete.', str(e))

            find_mock.assert_any_call(self.volumes_mock, volumes[0].id)
            find_mock.assert_any_call(self.volumes_mock, 'unexist_volume')

            self.assertEqual(2, find_mock.call_count)
            self.volumes_mock.delete.assert_called_once_with(
                volumes[0].id, cascade=False
            )

    def test_volume_delete_with_purge(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [
            '--purge',
            volumes[0].id,
        ]
        verifylist = [
            ('force', False),
            ('purge', True),
            ('volumes', [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete.assert_called_once_with(
            volumes[0].id, cascade=True
        )
        self.assertIsNone(result)

    def test_volume_delete_with_force(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [
            '--force',
            volumes[0].id,
        ]
        verifylist = [
            ('force', True),
            ('purge', False),
            ('volumes', [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.force_delete.assert_called_once_with(volumes[0].id)
        self.assertIsNone(result)


class TestVolumeList(TestVolume):
    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    columns = [
        'ID',
        'Name',
        'Status',
        'Size',
        'Attached to',
    ]

    def setUp(self):
        super().setUp()

        self.mock_volume = volume_fakes.create_one_volume()
        self.volumes_mock.list.return_value = [self.mock_volume]

        self.users_mock.get.return_value = self.user

        self.projects_mock.get.return_value = self.project

        # Get the command object to test
        self.cmd = volume.ListVolume(self.app, None)

    def test_volume_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_project(self):
        arglist = [
            '--project',
            self.project.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'project_id': self.project.id,
            'user_id': None,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_project_domain(self):
        arglist = [
            '--project',
            self.project.name,
            '--project-domain',
            self.project.domain_id,
        ]
        verifylist = [
            ('project', self.project.name),
            ('project_domain', self.project.domain_id),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'project_id': self.project.id,
            'user_id': None,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_user(self):
        arglist = [
            '--user',
            self.user.name,
        ]
        verifylist = [
            ('user', self.user.name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': self.user.id,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )
        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_user_domain(self):
        arglist = [
            '--user',
            self.user.name,
            '--user-domain',
            self.user.domain_id,
        ]
        verifylist = [
            ('user', self.user.name),
            ('user_domain', self.user.domain_id),
            ('long', False),
            ('all_projects', False),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': self.user.id,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_name(self):
        arglist = [
            '--name',
            self.mock_volume.name,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', self.mock_volume.name),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': self.mock_volume.name,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_status(self):
        arglist = [
            '--status',
            self.mock_volume.status,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', self.mock_volume.status),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': self.mock_volume.status,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', True),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': True,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        collist = [
            'ID',
            'Name',
            'Status',
            'Size',
            'Type',
            'Bootable',
            'Attached to',
            'Properties',
        ]
        self.assertEqual(collist, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                self.mock_volume.volume_type,
                self.mock_volume.bootable,
                volume.AttachmentsColumn(self.mock_volume.attachments),
                format_columns.DictColumn(self.mock_volume.metadata),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_with_marker_and_limit(self):
        arglist = [
            "--marker",
            self.mock_volume.id,
            "--limit",
            "2",
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', self.mock_volume.id),
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)

        datalist = (
            (
                self.mock_volume.id,
                self.mock_volume.name,
                self.mock_volume.status,
                self.mock_volume.size,
                volume.AttachmentsColumn(self.mock_volume.attachments),
            ),
        )

        self.volumes_mock.list.assert_called_once_with(
            marker=self.mock_volume.id,
            limit=2,
            search_opts={
                'status': None,
                'project_id': None,
                'user_id': None,
                'name': None,
                'all_tenants': False,
            },
        )
        self.assertCountEqual(datalist, tuple(data))

    def test_volume_list_negative_limit(self):
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

    def test_volume_list_backward_compatibility(self):
        arglist = [
            '-c',
            'Display Name',
        ]
        verifylist = [
            ('columns', ['Display Name']),
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('marker', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'all_tenants': False,
            'project_id': None,
            'user_id': None,
            'name': None,
            'status': None,
        }
        self.volumes_mock.list.assert_called_once_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )

        self.assertIn('Display Name', columns)
        self.assertNotIn('Name', columns)

        for each_volume in data:
            self.assertIn(self.mock_volume.name, each_volume)


class TestVolumeMigrate(TestVolume):
    _volume = volume_fakes.create_one_volume()

    def setUp(self):
        super().setUp()

        self.volumes_mock.get.return_value = self._volume
        self.volumes_mock.migrate_volume.return_value = None
        # Get the command object to test
        self.cmd = volume.MigrateVolume(self.app, None)

    def test_volume_migrate(self):
        arglist = [
            "--host",
            "host@backend-name#pool",
            self._volume.id,
        ]
        verifylist = [
            ("force_host_copy", False),
            ("lock_volume", False),
            ("host", "host@backend-name#pool"),
            ("volume", self._volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.get.assert_called_once_with(self._volume.id)
        self.volumes_mock.migrate_volume.assert_called_once_with(
            self._volume.id, "host@backend-name#pool", False, False
        )
        self.assertIsNone(result)

    def test_volume_migrate_with_option(self):
        arglist = [
            "--force-host-copy",
            "--lock-volume",
            "--host",
            "host@backend-name#pool",
            self._volume.id,
        ]
        verifylist = [
            ("force_host_copy", True),
            ("lock_volume", True),
            ("host", "host@backend-name#pool"),
            ("volume", self._volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.get.assert_called_once_with(self._volume.id)
        self.volumes_mock.migrate_volume.assert_called_once_with(
            self._volume.id, "host@backend-name#pool", True, True
        )
        self.assertIsNone(result)

    def test_volume_migrate_without_host(self):
        arglist = [
            self._volume.id,
        ]
        verifylist = [
            ("force_host_copy", False),
            ("lock_volume", False),
            ("volume", self._volume.id),
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestVolumeSet(TestVolume):
    volume_type = volume_fakes.create_one_volume_type()

    def setUp(self):
        super().setUp()

        self.new_volume = volume_fakes.create_one_volume()
        self.volumes_mock.get.return_value = self.new_volume
        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume.SetVolume(self.app, None)

    def test_volume_set_property(self):
        arglist = [
            '--property',
            'a=b',
            '--property',
            'c=d',
            self.new_volume.id,
        ]
        verifylist = [
            ('property', {'a': 'b', 'c': 'd'}),
            ('volume', self.new_volume.id),
            ('bootable', False),
            ('non_bootable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_metadata.assert_called_with(
            self.new_volume.id, parsed_args.property
        )

    def test_volume_set_image_property(self):
        arglist = [
            '--image-property',
            'Alpha=a',
            '--image-property',
            'Beta=b',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_property', {'Alpha': 'a', 'Beta': 'b'}),
            ('volume', self.new_volume.id),
            ('bootable', False),
            ('non_bootable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args.image_property
        )

    def test_volume_set_state(self):
        arglist = ['--state', 'error', self.new_volume.id]
        verifylist = [
            ('read_only', False),
            ('read_write', False),
            ('state', 'error'),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, 'error'
        )
        self.volumes_mock.update_readonly_flag.assert_not_called()
        self.assertIsNone(result)

    def test_volume_set_state_failed(self):
        self.volumes_mock.reset_state.side_effect = exceptions.CommandError()
        arglist = ['--state', 'error', self.new_volume.id]
        verifylist = [('state', 'error'), ('volume', self.new_volume.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'One or more of the set operations failed', str(e)
            )
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, 'error'
        )

    def test_volume_set_attached(self):
        arglist = ['--attached', self.new_volume.id]
        verifylist = [
            ('attached', True),
            ('detached', False),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, attach_status='attached', state=None
        )
        self.assertIsNone(result)

    def test_volume_set_detached(self):
        arglist = ['--detached', self.new_volume.id]
        verifylist = [
            ('attached', False),
            ('detached', True),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, attach_status='detached', state=None
        )
        self.assertIsNone(result)

    def test_volume_set_bootable(self):
        arglist = [
            ['--bootable', self.new_volume.id],
            ['--non-bootable', self.new_volume.id],
        ]
        verifylist = [
            [
                ('bootable', True),
                ('non_bootable', False),
                ('volume', self.new_volume.id),
            ],
            [
                ('bootable', False),
                ('non_bootable', True),
                ('volume', self.new_volume.id),
            ],
        ]
        for index in range(len(arglist)):
            parsed_args = self.check_parser(
                self.cmd, arglist[index], verifylist[index]
            )

            self.cmd.take_action(parsed_args)
            self.volumes_mock.set_bootable.assert_called_with(
                self.new_volume.id, verifylist[index][0][1]
            )

    def test_volume_set_readonly(self):
        arglist = ['--read-only', self.new_volume.id]
        verifylist = [
            ('read_only', True),
            ('read_write', False),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.update_readonly_flag.assert_called_once_with(
            self.new_volume.id, True
        )
        self.assertIsNone(result)

    def test_volume_set_read_write(self):
        arglist = ['--read-write', self.new_volume.id]
        verifylist = [
            ('read_only', False),
            ('read_write', True),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.update_readonly_flag.assert_called_once_with(
            self.new_volume.id, False
        )
        self.assertIsNone(result)

    def test_volume_set_type(self):
        arglist = ['--type', self.volume_type.id, self.new_volume.id]
        verifylist = [
            ('retype_policy', None),
            ('type', self.volume_type.id),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.retype.assert_called_once_with(
            self.new_volume.id, self.volume_type.id, 'never'
        )
        self.assertIsNone(result)

    def test_volume_set_type_with_policy(self):
        arglist = [
            '--retype-policy',
            'on-demand',
            '--type',
            self.volume_type.id,
            self.new_volume.id,
        ]
        verifylist = [
            ('retype_policy', 'on-demand'),
            ('type', self.volume_type.id),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.retype.assert_called_once_with(
            self.new_volume.id, self.volume_type.id, 'on-demand'
        )
        self.assertIsNone(result)

    @mock.patch.object(volume.LOG, 'warning')
    def test_volume_set_with_only_retype_policy(self, mock_warning):
        arglist = ['--retype-policy', 'on-demand', self.new_volume.id]
        verifylist = [
            ('retype_policy', 'on-demand'),
            ('volume', self.new_volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.retype.assert_not_called()
        mock_warning.assert_called_with(
            "'--retype-policy' option will not work without '--type' option"
        )
        self.assertIsNone(result)


class TestVolumeShow(TestVolume):
    def setUp(self):
        super().setUp()

        self._volume = volume_fakes.create_one_volume()
        self.volumes_mock.get.return_value = self._volume
        # Get the command object to test
        self.cmd = volume.ShowVolume(self.app, None)

    def test_volume_show(self):
        arglist = [self._volume.id]
        verifylist = [("volume", self._volume.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volumes_mock.get.assert_called_with(self._volume.id)

        self.assertEqual(
            tuple(sorted(self._volume.keys())),
            columns,
        )
        self.assertTupleEqual(
            (
                self._volume.attachments,
                self._volume.availability_zone,
                self._volume.bootable,
                self._volume.description,
                self._volume.id,
                self._volume.name,
                format_columns.DictColumn(self._volume.metadata),
                self._volume.size,
                self._volume.snapshot_id,
                self._volume.status,
                self._volume.volume_type,
            ),
            data,
        )


class TestVolumeUnset(TestVolume):
    def setUp(self):
        super().setUp()

        self.new_volume = volume_fakes.create_one_volume()
        self.volumes_mock.get.return_value = self.new_volume

        # Get the command object to set property
        self.cmd_set = volume.SetVolume(self.app, None)

        # Get the command object to unset property
        self.cmd_unset = volume.UnsetVolume(self.app, None)

    def test_volume_unset_image_property(self):
        # Arguments for setting image properties
        arglist = [
            '--image-property',
            'Alpha=a',
            '--image-property',
            'Beta=b',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_property', {'Alpha': 'a', 'Beta': 'b'}),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd_set, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd_set.take_action(parsed_args)

        # Arguments for unsetting image properties
        arglist_unset = [
            '--image-property',
            'Alpha',
            self.new_volume.id,
        ]
        verifylist_unset = [
            ('image_property', ['Alpha']),
            ('volume', self.new_volume.id),
        ]
        parsed_args_unset = self.check_parser(
            self.cmd_unset, arglist_unset, verifylist_unset
        )

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd_unset.take_action(parsed_args_unset)

        self.volumes_mock.delete_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args_unset.image_property
        )

    def test_volume_unset_image_property_fail(self):
        self.volumes_mock.delete_image_metadata.side_effect = (
            exceptions.CommandError()
        )
        arglist = [
            '--image-property',
            'Alpha',
            '--property',
            'Beta',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_property', ['Alpha']),
            ('property', ['Beta']),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(self.cmd_unset, arglist, verifylist)

        try:
            self.cmd_unset.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'One or more of the unset operations failed', str(e)
            )
        self.volumes_mock.delete_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args.image_property
        )
        self.volumes_mock.delete_metadata.assert_called_with(
            self.new_volume.id, parsed_args.property
        )


class TestColumns(TestVolume):
    def test_attachments_column_without_server_cache(self):
        _volume = volume_fakes.create_one_volume()
        server_id = _volume.attachments[0]['server_id']
        device = _volume.attachments[0]['device']

        col = volume.AttachmentsColumn(_volume.attachments, {})
        self.assertEqual(
            f'Attached to {server_id} on {device} ',
            col.human_readable(),
        )
        self.assertEqual(_volume.attachments, col.machine_readable())

    def test_attachments_column_with_server_cache(self):
        _volume = volume_fakes.create_one_volume()

        server_id = _volume.attachments[0]['server_id']
        device = _volume.attachments[0]['device']
        fake_server = mock.Mock()
        fake_server.name = 'fake-server-name'
        server_cache = {server_id: fake_server}

        col = volume.AttachmentsColumn(_volume.attachments, server_cache)
        self.assertEqual(
            'Attached to {} on {} '.format('fake-server-name', device),
            col.human_readable(),
        )
        self.assertEqual(_volume.attachments, col.machine_readable())
