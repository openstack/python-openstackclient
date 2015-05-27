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
from openstackclient.image.v2 import image
from openstackclient.tests import fakes
from openstackclient.tests.image.v2 import fakes as image_fakes


class TestImage(image_fakes.TestImagev2):

    def setUp(self):
        super(TestImage, self).setUp()

        # Get a shortcut to the ServerManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()


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
            'min_ram': 4,
            'protected': False
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id, **kwargs)

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertEqual(image_fakes.IMAGE_data, data)
