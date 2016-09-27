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

import argparse
import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume


class TestVolume(volume_fakes.TestVolume):

    def setUp(self):
        super(TestVolume, self).setUp()

        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()

        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()

        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()

        self.snapshots_mock = self.app.client_manager.volume.volume_snapshots
        self.snapshots_mock.reset_mock()

        self.consistencygroups_mock = (
            self.app.client_manager.volume.consistencygroups)
        self.consistencygroups_mock.reset_mock()

    def setup_volumes_mock(self, count):
        volumes = volume_fakes.FakeVolume.create_volumes(count=count)

        self.volumes_mock.get = volume_fakes.FakeVolume.get_volumes(
            volumes,
            0)
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
        super(TestVolumeCreate, self).setUp()

        self.new_volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.create.return_value = self.new_volume

        self.datalist = (
            self.new_volume.attachments,
            self.new_volume.availability_zone,
            self.new_volume.bootable,
            self.new_volume.description,
            self.new_volume.id,
            self.new_volume.name,
            utils.format_dict(self.new_volume.metadata),
            self.new_volume.size,
            self.new_volume.snapshot_id,
            self.new_volume.status,
            self.new_volume.volume_type,
        )

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_min_options(self):
        arglist = [
            '--size', str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
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
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_options(self):
        consistency_group = (
            volume_fakes.FakeConsistencyGroup.create_one_consistency_group())
        self.consistencygroups_mock.get.return_value = consistency_group
        arglist = [
            '--size', str(self.new_volume.size),
            '--description', self.new_volume.description,
            '--type', self.new_volume.volume_type,
            '--availability-zone', self.new_volume.availability_zone,
            '--consistency-group', consistency_group.id,
            '--hint', 'k=v',
            '--multi-attach',
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('description', self.new_volume.description),
            ('type', self.new_volume.volume_type),
            ('availability_zone', self.new_volume.availability_zone),
            ('consistency_group', consistency_group.id),
            ('hint', {'k': 'v'}),
            ('multi_attach', True),
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
            user_id=None,
            project_id=None,
            availability_zone=self.new_volume.availability_zone,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=consistency_group.id,
            source_replica=None,
            multiattach=True,
            scheduler_hints={'k': 'v'},
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_user_project_id(self):
        # Return a project
        self.projects_mock.get.return_value = self.project
        # Return a user
        self.users_mock.get.return_value = self.user

        arglist = [
            '--size', str(self.new_volume.size),
            '--project', self.project.id,
            '--user', self.user.id,
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('project', self.project.id),
            ('user', self.user.id),
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
            user_id=self.user.id,
            project_id=self.project.id,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_user_project_name(self):
        # Return a project
        self.projects_mock.get.return_value = self.project
        # Return a user
        self.users_mock.get.return_value = self.user

        arglist = [
            '--size', str(self.new_volume.size),
            '--project', self.project.name,
            '--user', self.user.name,
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('project', self.project.name),
            ('user', self.user.name),
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
            user_id=self.user.id,
            project_id=self.project.id,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_properties(self):
        arglist = [
            '--property', 'Alpha=a',
            '--property', 'Beta=b',
            '--size', str(self.new_volume.size),
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
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata={'Alpha': 'a', 'Beta': 'b'},
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_id(self):
        image = image_fakes.FakeImage.create_one_image()
        self.images_mock.get.return_value = image

        arglist = [
            '--image', image.id,
            '--size', str(self.new_volume.size),
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
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata=None,
            imageRef=image.id,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_name(self):
        image = image_fakes.FakeImage.create_one_image()
        self.images_mock.get.return_value = image

        arglist = [
            '--image', image.name,
            '--size', str(self.new_volume.size),
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
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata=None,
            imageRef=image.id,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_snapshot(self):
        snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()
        self.new_volume.snapshot_id = snapshot.id
        arglist = [
            '--snapshot', self.new_volume.snapshot_id,
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
            size=None,
            snapshot_id=snapshot.id,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=None,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_source_replicated(self):
        self.volumes_mock.get.return_value = self.new_volume
        arglist = [
            '--source-replicated', self.new_volume.id,
            self.new_volume.name,
        ]
        verifylist = [
            ('source_replicated', self.new_volume.id),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volumes_mock.create.assert_called_once_with(
            size=None,
            snapshot_id=None,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None,
            consistencygroup_id=None,
            source_replica=self.new_volume.id,
            multiattach=False,
            scheduler_hints=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_without_size(self):
        arglist = [
            self.new_volume.name,
        ]
        verifylist = [
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_volume_create_with_multi_source(self):
        arglist = [
            '--image', 'source_image',
            '--source', 'source_volume',
            '--snapshot', 'source_snapshot',
            '--source-replicated', 'source_replicated_volume',
            '--size', str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('image', 'source_image'),
            ('source', 'source_volume'),
            ('snapshot', 'source_snapshot'),
            ('source-replicated', 'source_replicated_volume'),
            ('size', self.new_volume.size),
            ('name', self.new_volume.name),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)


class TestVolumeDelete(TestVolume):

    def setUp(self):
        super(TestVolumeDelete, self).setUp()

        self.volumes_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume.DeleteVolume(self.app, None)

    def test_volume_delete_one_volume(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [
            volumes[0].id
        ]
        verifylist = [
            ("force", False),
            ("purge", False),
            ("volumes", [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete.assert_called_once_with(
            volumes[0].id, cascade=False)
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

        calls = [call(v.id, cascade=False) for v in volumes]
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
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 volumes failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.volumes_mock, volumes[0].id)
            find_mock.assert_any_call(self.volumes_mock, 'unexist_volume')

            self.assertEqual(2, find_mock.call_count)
            self.volumes_mock.delete.assert_called_once_with(
                volumes[0].id, cascade=False)

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
            volumes[0].id, cascade=True)
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
        'Display Name',
        'Status',
        'Size',
        'Attached to',
    ]

    def setUp(self):
        super(TestVolumeList, self).setUp()

        self.mock_volume = volume_fakes.FakeVolume.create_one_volume()
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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_project(self):
        arglist = [
            '--project', self.project.name,
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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_project_domain(self):
        arglist = [
            '--project', self.project.name,
            '--project-domain', self.project.domain_id,
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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_user(self):
        arglist = [
            '--user', self.user.name,
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

        self.assertEqual(self.columns, columns)
        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_user_domain(self):
        arglist = [
            '--user', self.user.name,
            '--user-domain', self.user.domain_id,
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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_name(self):
        arglist = [
            '--name', self.mock_volume.name,
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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_status(self):
        arglist = [
            '--status', self.mock_volume.status,
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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

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

        self.assertEqual(self.columns, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )
        self.assertEqual(datalist, tuple(data))

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

        collist = [
            'ID',
            'Display Name',
            'Status',
            'Size',
            'Type',
            'Bootable',
            'Attached to',
            'Properties',
        ]
        self.assertEqual(collist, columns)

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            self.mock_volume.volume_type,
            self.mock_volume.bootable,
            msg,
            utils.format_dict(self.mock_volume.metadata),
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_with_marker_and_limit(self):
        arglist = [
            "--marker", self.mock_volume.id,
            "--limit", "2",
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

        server = self.mock_volume.attachments[0]['server_id']
        device = self.mock_volume.attachments[0]['device']
        msg = 'Attached to %s on %s ' % (server, device)
        datalist = ((
            self.mock_volume.id,
            self.mock_volume.name,
            self.mock_volume.status,
            self.mock_volume.size,
            msg,
        ), )

        self.volumes_mock.list.assert_called_once_with(
            marker=self.mock_volume.id,
            limit=2,
            search_opts={
                'status': None,
                'project_id': None,
                'user_id': None,
                'display_name': None,
                'all_tenants': False, }
        )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_negative_limit(self):
        arglist = [
            "--limit", "-2",
        ]
        verifylist = [
            ("limit", -2),
        ]
        self.assertRaises(argparse.ArgumentTypeError, self.check_parser,
                          self.cmd, arglist, verifylist)


class TestVolumeSet(TestVolume):

    def setUp(self):
        super(TestVolumeSet, self).setUp()

        self.new_volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = self.new_volume

        # Get the command object to test
        self.cmd = volume.SetVolume(self.app, None)

    def test_volume_set_image_property(self):
        arglist = [
            '--image-property', 'Alpha=a',
            '--image-property', 'Beta=b',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_property', {'Alpha': 'a', 'Beta': 'b'}),
            ('volume', self.new_volume.id),
            ('bootable', False),
            ('non_bootable', False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args.image_property)

    def test_volume_set_state(self):
        arglist = [
            '--state', 'error',
            self.new_volume.id
        ]
        verifylist = [
            ('state', 'error'),
            ('volume', self.new_volume.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, 'error')
        self.assertIsNone(result)

    def test_volume_set_state_failed(self):
        self.volumes_mock.reset_state.side_effect = exceptions.CommandError()
        arglist = [
            '--state', 'error',
            self.new_volume.id
        ]
        verifylist = [
            ('state', 'error'),
            ('volume', self.new_volume.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('One or more of the set operations failed',
                             str(e))
        self.volumes_mock.reset_state.assert_called_with(
            self.new_volume.id, 'error')

    def test_volume_set_bootable(self):
        arglist = [
            ['--bootable', self.new_volume.id],
            ['--non-bootable', self.new_volume.id]
        ]
        verifylist = [
            [
                ('bootable', True),
                ('non_bootable', False),
                ('volume', self.new_volume.id)
            ],
            [
                ('bootable', False),
                ('non_bootable', True),
                ('volume', self.new_volume.id)
            ]
        ]
        for index in range(len(arglist)):
            parsed_args = self.check_parser(
                self.cmd, arglist[index], verifylist[index])

            self.cmd.take_action(parsed_args)
            self.volumes_mock.set_bootable.assert_called_with(
                self.new_volume.id, verifylist[index][0][1])


class TestVolumeShow(TestVolume):

    def setUp(self):
        super(TestVolumeShow, self).setUp()

        self._volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = self._volume
        # Get the command object to test
        self.cmd = volume.ShowVolume(self.app, None)

    def test_volume_show(self):
        arglist = [
            self._volume.id
        ]
        verifylist = [
            ("volume", self._volume.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volumes_mock.get.assert_called_with(self._volume.id)

        self.assertEqual(
            volume_fakes.FakeVolume.get_volume_columns(self._volume),
            columns)

        self.assertEqual(
            volume_fakes.FakeVolume.get_volume_data(self._volume),
            data)


class TestVolumeUnset(TestVolume):

    def setUp(self):
        super(TestVolumeUnset, self).setUp()

        self.new_volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = self.new_volume

        # Get the command object to set property
        self.cmd_set = volume.SetVolume(self.app, None)

        # Get the command object to unset property
        self.cmd_unset = volume.UnsetVolume(self.app, None)

    def test_volume_unset_image_property(self):

        # Arguments for setting image properties
        arglist = [
            '--image-property', 'Alpha=a',
            '--image-property', 'Beta=b',
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
            '--image-property', 'Alpha',
            self.new_volume.id,
        ]
        verifylist_unset = [
            ('image_property', ['Alpha']),
            ('volume', self.new_volume.id),
        ]
        parsed_args_unset = self.check_parser(self.cmd_unset,
                                              arglist_unset,
                                              verifylist_unset)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd_unset.take_action(parsed_args_unset)

        self.volumes_mock.delete_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args_unset.image_property)

    def test_volume_unset_image_property_fail(self):
        self.volumes_mock.delete_image_metadata.side_effect = (
            exceptions.CommandError())
        arglist = [
            '--image-property', 'Alpha',
            '--property', 'Beta',
            self.new_volume.id,
        ]
        verifylist = [
            ('image_property', ['Alpha']),
            ('property', ['Beta']),
            ('volume', self.new_volume.id),
        ]
        parsed_args = self.check_parser(
            self.cmd_unset, arglist, verifylist)

        try:
            self.cmd_unset.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('One or more of the unset operations failed',
                             str(e))
        self.volumes_mock.delete_image_metadata.assert_called_with(
            self.new_volume.id, parsed_args.image_property)
        self.volumes_mock.delete_metadata.assert_called_with(
            self.new_volume.id, parsed_args.property)
