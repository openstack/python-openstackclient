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

import mock
from mock import call

from openstackclient.common import utils
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes
from openstackclient.tests.volume.v2 import fakes as volume_fakes
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

    def setup_volumes_mock(self, count):
        volumes = volume_fakes.FakeVolume.create_volumes(count=count)

        self.volumes_mock.get = volume_fakes.FakeVolume.get_volumes(
            volumes,
            0)
        return volumes


class TestVolumeCreate(TestVolume):

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
            source_volid=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_options(self):
        arglist = [
            '--size', str(self.new_volume.size),
            '--description', self.new_volume.description,
            '--type', self.new_volume.volume_type,
            '--availability-zone', self.new_volume.availability_zone,
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('description', self.new_volume.description),
            ('type', self.new_volume.volume_type),
            ('availability_zone', self.new_volume.availability_zone),
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
            source_volid=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_user_project_id(self):
        # Return a project
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        # Return a user
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        arglist = [
            '--size', str(self.new_volume.size),
            '--project', identity_fakes.project_id,
            '--user', identity_fakes.user_id,
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('project', identity_fakes.project_id),
            ('user', identity_fakes.user_id),
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
            user_id=identity_fakes.user_id,
            project_id=identity_fakes.project_id,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_user_project_name(self):
        # Return a project
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        # Return a user
        self.users_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.USER),
            loaded=True,
        )

        arglist = [
            '--size', str(self.new_volume.size),
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_name,
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('project', identity_fakes.project_name),
            ('user', identity_fakes.user_name),
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
            user_id=identity_fakes.user_id,
            project_id=identity_fakes.project_id,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None
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
            source_volid=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_id(self):
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.IMAGE),
            loaded=True,
        )

        arglist = [
            '--image', volume_fakes.image_id,
            '--size', str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('image', volume_fakes.image_id),
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
            imageRef=volume_fakes.image_id,
            source_volid=None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_image_name(self):
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.IMAGE),
            loaded=True,
        )

        arglist = [
            '--image', volume_fakes.image_name,
            '--size', str(self.new_volume.size),
            self.new_volume.name,
        ]
        verifylist = [
            ('image', volume_fakes.image_name),
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
            imageRef=volume_fakes.image_id,
            source_volid=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_snapshot(self):
        arglist = [
            '--size', str(self.new_volume.size),
            '--snapshot', volume_fakes.snapshot_id,
            self.new_volume.name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('snapshot', volume_fakes.snapshot_id),
            ('name', self.new_volume.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        fake_snapshot = mock.Mock()
        fake_snapshot.id = volume_fakes.snapshot_id
        self.snapshots_mock.get.return_value = fake_snapshot

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_once_with(
            size=self.new_volume.size,
            snapshot_id=fake_snapshot.id,
            name=self.new_volume.name,
            description=None,
            volume_type=None,
            user_id=None,
            project_id=None,
            availability_zone=None,
            metadata=None,
            imageRef=None,
            source_volid=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


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
            ("volumes", [volumes[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete.assert_called_with(volumes[0].id)
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes(self):
        volumes = self.setup_volumes_mock(count=3)

        arglist = [v.id for v in volumes]
        verifylist = [
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [call(v.id) for v in volumes]
        self.volumes_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)


class TestVolumeList(TestVolume):

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

        self.users_mock.get.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.USER),
                loaded=True,
            ),
        ]

        self.projects_mock.get.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.PROJECT),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = volume.ListVolume(self.app, None)

    def test_volume_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
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
            '--project', identity_fakes.project_name,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
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
            '--project', identity_fakes.project_name,
            '--project-domain', identity_fakes.domain_name,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
            ('project_domain', identity_fakes.domain_name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
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
            '--user', identity_fakes.user_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
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
            '--user', identity_fakes.user_name,
            '--user-domain', identity_fakes.domain_name,
        ]
        verifylist = [
            ('user', identity_fakes.user_name),
            ('user_domain', identity_fakes.domain_name),
            ('long', False),
            ('all_projects', False),
            ('status', None),
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
            '--name', volume_fakes.volume_name,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', volume_fakes.volume_name),
            ('status', None),
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
            '--status', volume_fakes.volume_status,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', volume_fakes.volume_status),
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


class TestVolumeSet(TestVolume):

    def setUp(self):
        super(TestVolumeSet, self).setUp()

        self.new_volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.create.return_value = self.new_volume

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
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns nothing
        self.cmd.take_action(parsed_args)
        self.volumes_mock.set_image_metadata.assert_called_with(
            self.volumes_mock.get().id, parsed_args.image_property)


class TestVolumeUnset(TestVolume):

    def setUp(self):
        super(TestVolumeUnset, self).setUp()

        self.new_volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.create.return_value = self.new_volume

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
            self.volumes_mock.get().id, parsed_args_unset.image_property)
