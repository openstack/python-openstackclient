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

import copy

from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.volume.v1 import fakes as volume_fakes
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


# TODO(dtroyer): The volume create tests are incomplete, only the minimal
#                options and the options that require additional processing
#                are implemented at this time.

class TestVolumeCreate(TestVolume):

    def setUp(self):
        super(TestVolumeCreate, self).setUp()

        self.volumes_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = volume.CreateVolume(self.app, None)

    def test_volume_create_min_options(self):
        arglist = [
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)

    def test_volume_create_options(self):
        arglist = [
            '--size', str(volume_fakes.volume_size),
            '--description', volume_fakes.volume_description,
            '--type', volume_fakes.volume_type,
            '--availability-zone', volume_fakes.volume_zone,
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('description', volume_fakes.volume_description),
            ('type', volume_fakes.volume_type),
            ('availability_zone', volume_fakes.volume_zone),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            volume_fakes.volume_description,
            volume_fakes.volume_type,
            None,
            None,
            volume_fakes.volume_zone,
            None,
            None,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)

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
            '--size', str(volume_fakes.volume_size),
            '--project', identity_fakes.project_id,
            '--user', identity_fakes.user_id,
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('project', identity_fakes.project_id),
            ('user', identity_fakes.user_id),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            identity_fakes.user_id,
            identity_fakes.project_id,
            None,
            None,
            None,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)

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
            '--size', str(volume_fakes.volume_size),
            '--project', identity_fakes.project_name,
            '--user', identity_fakes.user_name,
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('size', volume_fakes.volume_size),
            ('project', identity_fakes.project_name),
            ('user', identity_fakes.user_name),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            identity_fakes.user_id,
            identity_fakes.project_id,
            None,
            None,
            None,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)

    def test_volume_create_properties(self):
        arglist = [
            '--property', 'Alpha=a',
            '--property', 'Beta=b',
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('property', {'Alpha': 'a', 'Beta': 'b'}),
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            {'Alpha': 'a', 'Beta': 'b'},
            None,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)

    def test_volume_create_image_id(self):
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.IMAGE),
            loaded=True,
        )

        arglist = [
            '--image', volume_fakes.image_id,
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('image', volume_fakes.image_id),
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            None,
            volume_fakes.image_id,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)

    def test_volume_create_image_name(self):
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.IMAGE),
            loaded=True,
        )

        arglist = [
            '--image', volume_fakes.image_name,
            '--size', str(volume_fakes.volume_size),
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('image', volume_fakes.image_name),
            ('size', volume_fakes.volume_size),
            ('name', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # VolumeManager.create(size, snapshot_id=, source_volid=,
        #                      display_name=, display_description=,
        #                      volume_type=, user_id=,
        #                      project_id=, availability_zone=,
        #                      metadata=, imageRef=)
        self.volumes_mock.create.assert_called_with(
            volume_fakes.volume_size,
            None,
            None,
            volume_fakes.volume_name,
            None,
            None,
            None,
            None,
            None,
            None,
            volume_fakes.image_id,
        )

        collist = (
            'attach_status',
            'availability_zone',
            'display_description',
            'display_name',
            'id',
            'properties',
            'size',
            'status',
            'type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            'detached',
            volume_fakes.volume_zone,
            volume_fakes.volume_description,
            volume_fakes.volume_name,
            volume_fakes.volume_id,
            volume_fakes.volume_metadata_str,
            volume_fakes.volume_size,
            volume_fakes.volume_status,
            volume_fakes.volume_type,
        )
        self.assertEqual(datalist, data)


class TestVolumeSet(TestVolume):

    def setUp(self):
        super(TestVolumeSet, self).setUp()

        self.volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )

        self.volumes_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )
        # Get the command object to test
        self.cmd = volume.SetVolume(self.app, None)

    def test_volume_set_no_options(self):
        arglist = [
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', None),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)
        self.assertEqual("No changes requested\n",
                         self.app.log.messages.get('error'))

    def test_volume_set_name(self):
        arglist = [
            '--name', 'qwerty',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('description', None),
            ('size', None),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'display_name': 'qwerty',
        }
        self.volumes_mock.update.assert_called_with(
            volume_fakes.volume_id,
            **kwargs
        )

    def test_volume_set_description(self):
        arglist = [
            '--description', 'new desc',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', 'new desc'),
            ('size', None),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'display_description': 'new desc',
        }
        self.volumes_mock.update.assert_called_with(
            volume_fakes.volume_id,
            **kwargs
        )

    def test_volume_set_size(self):
        arglist = [
            '--size', '130',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 130),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        size = 130

        self.volumes_mock.extend.assert_called_with(
            volume_fakes.volume_id,
            size
        )

    def test_volume_set_size_smaller(self):
        arglist = [
            '--size', '100',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 100),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)
        self.assertEqual("New size must be greater than %s GB" %
                         volume_fakes.volume_size,
                         self.app.log.messages.get('error'))

    def test_volume_set_size_not_available(self):
        self.volumes_mock.get.return_value.status = 'error'
        arglist = [
            '--size', '130',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', 130),
            ('property', None),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)
        self.assertEqual("Volume is in %s state, it must be available before "
                         "size can be extended" % 'error',
                         self.app.log.messages.get('error'))

    def test_volume_set_property(self):
        arglist = [
            '--property', 'myprop=myvalue',
            volume_fakes.volume_name,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('size', None),
            ('property', {'myprop': 'myvalue'}),
            ('volume', volume_fakes.volume_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        metadata = {
            'myprop': 'myvalue'
        }
        self.volumes_mock.set_metadata.assert_called_with(
            volume_fakes.volume_id,
            metadata
        )
