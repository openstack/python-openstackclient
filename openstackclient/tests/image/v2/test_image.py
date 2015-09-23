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
import mock

import warlock

from glanceclient.v2 import schemas
from openstackclient.common import exceptions
from openstackclient.image.v2 import image
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes
from openstackclient.tests.image.v2 import fakes as image_fakes


class TestImage(image_fakes.TestImagev2):

    def setUp(self):
        super(TestImage, self).setUp()

        # Get a shortcut to the ServerManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()
        self.image_members_mock = self.app.client_manager.image.image_members
        self.image_members_mock.reset_mock()
        self.project_mock = self.app.client_manager.identity.projects
        self.project_mock.reset_mock()
        self.domain_mock = self.app.client_manager.identity.domains
        self.domain_mock.reset_mock()


class TestImageCreate(TestImage):

    def setUp(self):
        super(TestImageCreate, self).setUp()

        self.images_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = copy.deepcopy(image_fakes.IMAGE)
        self.images_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = image.CreateImage(self.app, None)

    def test_image_reserve_no_options(self):
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)
        arglist = [
            image_fakes.image_name,
        ]
        verifylist = [
            ('container_format', image.DEFAULT_CONTAINER_FORMAT),
            ('disk_format', image.DEFAULT_DISK_FORMAT),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=image_fakes.image_name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.images_mock.upload.assert_called_with(
            mock.ANY, mock.ANY,
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    @mock.patch('glanceclient.common.utils.get_data_file', name='Open')
    def test_image_reserve_options(self, mock_open):
        mock_file = mock.MagicMock(name='File')
        mock_open.return_value = mock_file
        mock_open.read.return_value = None
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)
        arglist = [
            '--container-format', 'ovf',
            '--disk-format', 'fs',
            '--min-disk', '10',
            '--min-ram', '4',
            '--protected',
            '--private',
            image_fakes.image_name,
        ]
        verifylist = [
            ('container_format', 'ovf'),
            ('disk_format', 'fs'),
            ('min_disk', 10),
            ('min_ram', 4),
            ('protected', True),
            ('unprotected', False),
            ('public', False),
            ('private', True),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=image_fakes.image_name,
            container_format='ovf',
            disk_format='fs',
            min_disk=10,
            min_ram=4,
            protected=True,
            visibility='private',
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.images_mock.upload.assert_called_with(
            mock.ANY, mock.ANY,
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    @mock.patch('glanceclient.common.utils.get_data_file', name='Open')
    def test_image_create_file(self, mock_open):
        mock_file = mock.MagicMock(name='File')
        mock_open.return_value = mock_file
        mock_open.read.return_value = image_fakes.IMAGE_data
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)

        arglist = [
            '--file', 'filer',
            '--unprotected',
            '--public',
            '--property', 'Alpha=1',
            '--property', 'Beta=2',
            '--tag', 'awesome',
            '--tag', 'better',
            image_fakes.image_name,
        ]
        verifylist = [
            ('file', 'filer'),
            ('protected', False),
            ('unprotected', True),
            ('public', True),
            ('private', False),
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('tags', ['awesome', 'better']),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=image_fakes.image_name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
            protected=False,
            visibility='public',
            Alpha='1',
            Beta='2',
            tags=['awesome', 'better'],
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.images_mock.upload.assert_called_with(
            mock.ANY, mock.ANY,
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)

    def test_image_dead_options(self):

        arglist = [
            '--owner', 'nobody',
            image_fakes.image_name,
        ]
        verifylist = [
            ('owner', 'nobody'),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)


class TestAddProjectToImage(TestImage):

    def setUp(self):
        super(TestAddProjectToImage, self).setUp()

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.image_members_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.MEMBER),
            loaded=True,
        )
        self.project_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.domain_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )
        # Get the command object to test
        self.cmd = image.AddProjectToImage(self.app, None)

    def test_add_project_to_image_no_option(self):
        arglist = [
            image_fakes.image_id,
            identity_fakes.project_id,
            ]
        verifylist = [
            ('image', image_fakes.image_id),
            ('project', identity_fakes.project_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.image_members_mock.create.assert_called_with(
            image_fakes.image_id,
            identity_fakes.project_id
        )
        collist = ('image_id', 'member_id', 'status')
        self.assertEqual(collist, columns)
        datalist = (
            image_fakes.image_id,
            identity_fakes.project_id,
            image_fakes.member_status
        )
        self.assertEqual(datalist, data)

    def test_add_project_to_image_with_option(self):
        arglist = [
            image_fakes.image_id,
            identity_fakes.project_id,
            '--project-domain', identity_fakes.domain_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id),
            ('project', identity_fakes.project_id),
            ('project_domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.image_members_mock.create.assert_called_with(
            image_fakes.image_id,
            identity_fakes.project_id
        )
        collist = ('image_id', 'member_id', 'status')
        self.assertEqual(collist, columns)
        datalist = (
            image_fakes.image_id,
            identity_fakes.project_id,
            image_fakes.member_status
        )
        self.assertEqual(datalist, data)


class TestImageDelete(TestImage):

    def setUp(self):
        super(TestImageDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.images_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = image.DeleteImage(self.app, None)

    def test_image_delete_no_options(self):
        arglist = [
            image_fakes.image_id,
        ]
        verifylist = [
            ('images', [image_fakes.image_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.images_mock.delete.assert_called_with(
            image_fakes.image_id,
        )


class TestImageList(TestImage):

    def setUp(self):
        super(TestImageList, self).setUp()

        self.api_mock = mock.Mock()
        self.api_mock.image_list.side_effect = [
            [copy.deepcopy(image_fakes.IMAGE)], [],
        ]
        self.app.client_manager.image.api = self.api_mock

        # Get the command object to test
        self.cmd = image.ListImage(self.app, None)

    def test_image_list_no_options(self):
        arglist = []
        verifylist = [
            ('public', False),
            ('private', False),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=image_fakes.image_id,
        )

        collist = ('ID', 'Name')

        self.assertEqual(collist, columns)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_image_list_public_option(self):
        arglist = [
            '--public',
        ]
        verifylist = [
            ('public', True),
            ('private', False),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            public=True,
            marker=image_fakes.image_id,
        )

        collist = ('ID', 'Name')

        self.assertEqual(collist, columns)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_image_list_private_option(self):
        arglist = [
            '--private',
        ]
        verifylist = [
            ('public', False),
            ('private', True),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            private=True,
            marker=image_fakes.image_id,
        )

        collist = ('ID', 'Name')

        self.assertEqual(collist, columns)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_image_list_shared_option(self):
        arglist = [
            '--shared',
        ]
        verifylist = [
            ('public', False),
            ('private', False),
            ('shared', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            shared=True,
            marker=image_fakes.image_id,
        )

        collist = ('ID', 'Name')

        self.assertEqual(columns, collist)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_image_list_long_option(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=image_fakes.image_id,
        )

        collist = (
            'ID',
            'Name',
            'Disk Format',
            'Container Format',
            'Size',
            'Status',
            'Visibility',
            'Protected',
            'Owner',
            'Tags',
        )

        self.assertEqual(collist, columns)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
            '',
            '',
            '',
            '',
            'public',
            False,
            image_fakes.image_owner,
            '',
        ), )
        self.assertEqual(datalist, tuple(data))

    @mock.patch('openstackclient.api.utils.simple_filter')
    def test_image_list_property_option(self, sf_mock):
        sf_mock.return_value = [
            copy.deepcopy(image_fakes.IMAGE),
        ]

        arglist = [
            '--property', 'a=1',
        ]
        verifylist = [
            ('property', {'a': '1'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=image_fakes.image_id,
        )
        sf_mock.assert_called_with(
            [image_fakes.IMAGE],
            attr='a',
            value='1',
            property_field='properties',
        )

        collist = ('ID', 'Name')

        self.assertEqual(columns, collist)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    @mock.patch('openstackclient.common.utils.sort_items')
    def test_image_list_sort_option(self, si_mock):
        si_mock.return_value = [
            copy.deepcopy(image_fakes.IMAGE)
        ]

        arglist = ['--sort', 'name:asc']
        verifylist = [('sort', 'name:asc')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=image_fakes.image_id,
        )
        si_mock.assert_called_with(
            [image_fakes.IMAGE],
            'name:asc'
        )

        collist = ('ID', 'Name')

        self.assertEqual(collist, columns)
        datalist = ((
            image_fakes.image_id,
            image_fakes.image_name
        ), )
        self.assertEqual(datalist, tuple(data))


class TestRemoveProjectImage(TestImage):

    def setUp(self):
        super(TestRemoveProjectImage, self).setUp()

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.project_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.domain_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.DOMAIN),
            loaded=True,
        )
        self.image_members_mock.delete.return_value = None
        # Get the command object to test
        self.cmd = image.RemoveProjectImage(self.app, None)

    def test_remove_project_image_no_options(self):
        arglist = [
            image_fakes.image_id,
            identity_fakes.project_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id),
            ('project', identity_fakes.project_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)
        self.image_members_mock.delete.assert_called_with(
            image_fakes.image_id,
            identity_fakes.project_id,
        )

    def test_remove_project_image_with_options(self):
        arglist = [
            image_fakes.image_id,
            identity_fakes.project_id,
            '--project-domain', identity_fakes.domain_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id),
            ('project', identity_fakes.project_id),
            ('project_domain', identity_fakes.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)
        self.image_members_mock.delete.assert_called_with(
            image_fakes.image_id,
            identity_fakes.project_id,
        )


class TestImageShow(TestImage):

    def setUp(self):
        super(TestImageShow, self).setUp()

        # Set up the schema
        self.model = warlock.model_factory(
            image_fakes.IMAGE_schema,
            schemas.SchemaBasedModel,
        )

        self.images_mock.get.return_value = self.model(**image_fakes.IMAGE)

        # Get the command object to test
        self.cmd = image.ShowImage(self.app, None)

    def test_image_show(self):
        arglist = [
            image_fakes.image_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.images_mock.get.assert_called_with(
            image_fakes.image_id,
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)


class TestImageSet(TestImage):

    def setUp(self):
        super(TestImageSet, self).setUp()
        # Set up the schema
        self.model = warlock.model_factory(
            image_fakes.IMAGE_schema,
            schemas.SchemaBasedModel,
        )

        self.images_mock.get.return_value = self.model(**image_fakes.IMAGE)
        self.images_mock.update.return_value = self.model(**image_fakes.IMAGE)
        # Get the command object to test
        self.cmd = image.SetImage(self.app, None)

    def test_image_set_options(self):
        arglist = [
            '--name', 'new-name',
            '--owner', 'new-owner',
            '--min-disk', '2',
            '--min-ram', '4',
            image_fakes.image_id,
        ]
        verifylist = [
            ('name', 'new-name'),
            ('owner', 'new-owner'),
            ('min_disk', 2),
            ('min_ram', 4),
            ('image', image_fakes.image_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': 'new-name',
            'owner': 'new-owner',
            'min_disk': 2,
            'min_ram': 4
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id, **kwargs)

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)
