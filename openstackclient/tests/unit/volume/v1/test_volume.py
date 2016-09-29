#   Copyright 2013 Nebula Inc.
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
import copy
import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v1 import fakes as volume_fakes
from openstackclient.volume.v1 import volume


class TestVolume(volume_fakes.TestVolumev1):

    def setUp(self):
        super(TestVolume, self).setUp()

        # Get a shortcut to the VolumeManager Mock
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants
        self.projects_mock.reset_mock()

        # Get a shortcut to the UserManager Mock
        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        # Get a shortcut to the ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()

    def setup_volumes_mock(self, count):
        volumes = volume_fakes.FakeVolume.create_volumes(count=count)

        self.volumes_mock.get = volume_fakes.FakeVolume.get_volumes(
            volumes,
            0)
        return volumes


# TODO(dtroyer): The volume create tests are incomplete, only the minimal
#                options and the options that require additional processing
#                are implemented at this time.

class TestVolumeCreate(TestVolume):

    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    columns = (
        'attachments',
        'availability_zone',
        'bootable',
        'created_at',
        'display_description',
        'display_name',
        'id',
        'properties',
        'size',
        'snapshot_id',
        'status',
        'type',
    )

    def setUp(self):
        super(TestVolumeCreate, self).setUp()
        self.new_volume = volume_fakes.FakeVolume.create_one_volume()
        self.datalist = (
            self.new_volume.attachments,
            self.new_volume.availability_zone,
            self.new_volume.bootable,
            self.new_volume.created_at,
            self.new_volume.display_description,
            self.new_volume.display_name,
            self.new_volume.id,
            utils.format_dict(self.new_volume.metadata),
            self.new_volume.size,
            self.new_volume.snapshot_id,
            self.new_volume.status,
            self.new_volume.volume_type,
        )
        self.volumes_mock.create.return_value = self.new_volume

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_min_options(self):
        arglist = [
            '--size', str(self.new_volume.size),
            self.new_volume.display_name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_options(self):
        arglist = [
            '--size', str(self.new_volume.size),
            '--description', self.new_volume.display_description,
            '--type', self.new_volume.volume_type,
            '--availability-zone', self.new_volume.availability_zone,
            self.new_volume.display_name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('description', self.new_volume.display_description),
            ('type', self.new_volume.volume_type),
            ('availability_zone', self.new_volume.availability_zone),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            self.new_volume.display_description,
            self.new_volume.volume_type,
            None,
            None,
            self.new_volume.availability_zone,
            None,
            None,
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
            self.new_volume.display_name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('project', self.project.id),
            ('user', self.user.id),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            None,
            None,
            self.user.id,
            self.project.id,
            None,
            None,
            None,
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
            self.new_volume.display_name,
        ]
        verifylist = [
            ('size', self.new_volume.size),
            ('project', self.project.name),
            ('user', self.user.name),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            None,
            None,
            self.user.id,
            self.project.id,
            None,
            None,
            None,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_properties(self):
        arglist = [
            '--property', 'Alpha=a',
            '--property', 'Beta=b',
            '--size', str(self.new_volume.size),
            self.new_volume.display_name,
        ]
        verifylist = [
            ('property', {'Alpha': 'a', 'Beta': 'b'}),
            ('size', self.new_volume.size),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            None,
            None,
            None,
            None,
            None,
            {'Alpha': 'a', 'Beta': 'b'},
            None,
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
            self.new_volume.display_name,
        ]
        verifylist = [
            ('image', volume_fakes.image_id),
            ('size', self.new_volume.size),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            None,
            None,
            None,
            None,
            None,
            None,
            volume_fakes.image_id,
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
            self.new_volume.display_name,
        ]
        verifylist = [
            ('image', volume_fakes.image_name),
            ('size', self.new_volume.size),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            self.new_volume.size,
            None,
            None,
            self.new_volume.display_name,
            None,
            None,
            None,
            None,
            None,
            None,
            volume_fakes.image_id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_with_source(self):
        self.volumes_mock.get.return_value = self.new_volume
        arglist = [
            '--source', self.new_volume.id,
            self.new_volume.display_name,
        ]
        verifylist = [
            ('source', self.new_volume.id),
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.create.assert_called_with(
            None,
            None,
            self.new_volume.id,
            self.new_volume.display_name,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_volume_create_without_size(self):
        arglist = [
            self.new_volume.display_name,
        ]
        verifylist = [
            ('name', self.new_volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_volume_create_with_multi_source(self):
        arglist = [
            '--image', 'source_image',
            '--source', 'source_volume',
            '--snapshot', 'source_snapshot',
            '--size', str(self.new_volume.size),
            self.new_volume.display_name,
        ]
        verifylist = [
            ('image', 'source_image'),
            ('source', 'source_volume'),
            ('snapshot', 'source_snapshot'),
            ('size', self.new_volume.size),
            ('name', self.new_volume.display_name),
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
            ("volumes", [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete.assert_called_once_with(volumes[0].id)
        self.assertIsNone(result)

    def test_volume_delete_multi_volumes(self):
        volumes = self.setup_volumes_mock(count=3)

        arglist = [v.id for v in volumes]
        verifylist = [
            ('force', False),
            ('volumes', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [call(v.id) for v in volumes]
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
            self.volumes_mock.delete.assert_called_once_with(volumes[0].id)

    def test_volume_delete_with_force(self):
        volumes = self.setup_volumes_mock(count=1)

        arglist = [
            '--force',
            volumes[0].id,
        ]
        verifylist = [
            ('force', True),
            ('volumes', [volumes[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.force_delete.assert_called_once_with(volumes[0].id)
        self.assertIsNone(result)


class TestVolumeList(TestVolume):

    _volume = volume_fakes.FakeVolume.create_one_volume()
    columns = (
        'ID',
        'Display Name',
        'Status',
        'Size',
        'Attached to',
    )
    server = _volume.attachments[0]['server_id']
    device = _volume.attachments[0]['device']
    msg = 'Attached to %s on %s ' % (server, device)
    datalist = (
        (
            _volume.id,
            _volume.display_name,
            _volume.status,
            _volume.size,
            msg,
        ),
    )

    def setUp(self):
        super(TestVolumeList, self).setUp()

        self.volumes_mock.list.return_value = [self._volume]

        # Get the command object to test
        self.cmd = volume.ListVolume(self.app, None)

    def test_volume_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_name(self):
        arglist = [
            '--name', self._volume.display_name,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', self._volume.display_name),
            ('status', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_status(self):
        arglist = [
            '--status', self._volume.status,
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', self._volume.status),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', True),
            ('name', None),
            ('status', None),
            ('limit', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.datalist, tuple(data))

    def test_volume_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('limit', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            'ID',
            'Display Name',
            'Status',
            'Size',
            'Type',
            'Bootable',
            'Attached to',
            'Properties',
        )
        self.assertEqual(collist, columns)

        datalist = ((
            self._volume.id,
            self._volume.display_name,
            self._volume.status,
            self._volume.size,
            self._volume.volume_type,
            self._volume.bootable,
            self.msg,
            utils.format_dict(self._volume.metadata),
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_volume_list_with_limit(self):
        arglist = [
            '--limit', '2',
        ]
        verifylist = [
            ('long', False),
            ('all_projects', False),
            ('name', None),
            ('status', None),
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.list.assert_called_once_with(
            limit=2,
            search_opts={
                'status': None,
                'display_name': None,
                'all_tenants': False, }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

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

    _volume = volume_fakes.FakeVolume.create_one_volume()

    def setUp(self):
        super(TestVolumeSet, self).setUp()

        self.volumes_mock.get.return_value = self._volume

        self.volumes_mock.update.return_value = self._volume
        # Get the command object to test
        self.cmd = volume.SetVolume(self.app, None)

    def test_volume_set_no_options(self):
        arglist = [
            self._volume.display_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', None),
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

    def test_volume_set_name(self):
        arglist = [
            '--name', 'qwerty',
            self._volume.display_name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('description', None),
            ('size', None),
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'display_name': 'qwerty',
        }
        self.volumes_mock.update.assert_called_with(
            self._volume.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_volume_set_description(self):
        arglist = [
            '--description', 'new desc',
            self._volume.display_name,
        ]
        verifylist = [
            ('name', None),
            ('description', 'new desc'),
            ('size', None),
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'display_description': 'new desc',
        }
        self.volumes_mock.update.assert_called_with(
            self._volume.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_volume_set_size(self):
        arglist = [
            '--size', '130',
            self._volume.display_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 130),
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        size = 130
        self.volumes_mock.extend.assert_called_with(
            self._volume.id,
            size
        )
        self.assertIsNone(result)

    @mock.patch.object(volume.LOG, 'error')
    def test_volume_set_size_smaller(self, mock_log_error):
        self._volume.status = 'available'
        arglist = [
            '--size', '1',
            self._volume.display_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 1),
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        mock_log_error.assert_called_with("New size must be greater "
                                          "than %s GB",
                                          self._volume.size)
        self.assertIsNone(result)

    @mock.patch.object(volume.LOG, 'error')
    def test_volume_set_size_not_available(self, mock_log_error):
        self._volume.status = 'error'
        arglist = [
            '--size', '130',
            self._volume.display_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 130),
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        mock_log_error.assert_called_with("Volume is in %s state, it must be "
                                          "available before size can be "
                                          "extended", 'error')
        self.assertIsNone(result)

    def test_volume_set_property(self):
        arglist = [
            '--property', 'myprop=myvalue',
            self._volume.display_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', None),
            ('property', {'myprop': 'myvalue'}),
            ('volume', self._volume.display_name),
            ('bootable', False),
            ('non_bootable', False)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        metadata = {
            'myprop': 'myvalue'
        }
        self.volumes_mock.set_metadata.assert_called_with(
            self._volume.id,
            metadata
        )
        self.assertIsNone(result)

    def test_volume_set_bootable(self):
        arglist = [
            ['--bootable', self._volume.id],
            ['--non-bootable', self._volume.id]
        ]
        verifylist = [
            [
                ('bootable', True),
                ('non_bootable', False),
                ('volume', self._volume.id)
            ],
            [
                ('bootable', False),
                ('non_bootable', True),
                ('volume', self._volume.id)
            ]
        ]
        for index in range(len(arglist)):
            parsed_args = self.check_parser(
                self.cmd, arglist[index], verifylist[index])

            self.cmd.take_action(parsed_args)
            self.volumes_mock.set_bootable.assert_called_with(
                self._volume.id, verifylist[index][0][1])


class TestVolumeShow(TestVolume):

    columns = (
        'attachments',
        'availability_zone',
        'bootable',
        'created_at',
        'display_description',
        'display_name',
        'id',
        'properties',
        'size',
        'snapshot_id',
        'status',
        'type',
    )

    def setUp(self):
        super(TestVolumeShow, self).setUp()
        self._volume = volume_fakes.FakeVolume.create_one_volume()
        self.datalist = (
            self._volume.attachments,
            self._volume.availability_zone,
            self._volume.bootable,
            self._volume.created_at,
            self._volume.display_description,
            self._volume.display_name,
            self._volume.id,
            utils.format_dict(self._volume.metadata),
            self._volume.size,
            self._volume.snapshot_id,
            self._volume.status,
            self._volume.volume_type,
        )
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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestVolumeUnset(TestVolume):

    _volume = volume_fakes.FakeVolume.create_one_volume()

    def setUp(self):
        super(TestVolumeUnset, self).setUp()

        self.volumes_mock.get.return_value = self._volume

        self.volumes_mock.delete_metadata.return_value = None
        # Get the command object to test
        self.cmd = volume.UnsetVolume(self.app, None)

    def test_volume_unset_no_options(self):
        arglist = [
            self._volume.display_name,
        ]
        verifylist = [
            ('property', None),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

    def test_volume_unset_property(self):
        arglist = [
            '--property', 'myprop',
            self._volume.display_name,
        ]
        verifylist = [
            ('property', ['myprop']),
            ('volume', self._volume.display_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volumes_mock.delete_metadata.assert_called_with(
            self._volume.id, ['myprop']
        )
        self.assertIsNone(result)
