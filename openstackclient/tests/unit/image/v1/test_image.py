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

import copy
from unittest import mock

from osc_lib.cli import format_columns

from openstackclient.image.v1 import image
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.image.v1 import fakes as image_fakes


class TestImageCreate(image_fakes.TestImagev1):
    new_image = image_fakes.create_one_image()
    columns = (
        'container_format',
        'disk_format',
        'id',
        'is_public',
        'min_disk',
        'min_ram',
        'name',
        'owner',
        'properties',
        'protected',
        'size',
    )
    data = (
        new_image.container_format,
        new_image.disk_format,
        new_image.id,
        new_image.is_public,
        new_image.min_disk,
        new_image.min_ram,
        new_image.name,
        new_image.owner_id,
        format_columns.DictColumn(new_image.properties),
        new_image.is_protected,
        new_image.size,
    )

    def setUp(self):
        super().setUp()

        self.image_client.create_image = mock.Mock(return_value=self.new_image)
        self.image_client.find_image = mock.Mock(return_value=self.new_image)
        self.image_client.update_image = mock.Mock(return_image=self.new_image)

        # Get the command object to test
        self.cmd = image.CreateImage(self.app, None)

    @mock.patch('sys.stdin', side_effect=[None])
    def test_image_reserve_no_options(self, raw_input):
        arglist = [
            self.new_image.name,
        ]
        verifylist = [
            ('container_format', image.DEFAULT_CONTAINER_FORMAT),
            ('disk_format', image.DEFAULT_DISK_FORMAT),
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.image_client.create_image.assert_called_with(
            name=self.new_image.name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.image_client.update_image.call_args_list, [])

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch('sys.stdin', side_effect=[None])
    def test_image_reserve_options(self, raw_input):
        arglist = [
            '--container-format',
            'ovf',
            '--disk-format',
            'ami',
            '--min-disk',
            '10',
            '--min-ram',
            '4',
            '--protected',
            '--private',
            '--project',
            'q',
            self.new_image.name,
        ]
        verifylist = [
            ('container_format', 'ovf'),
            ('disk_format', 'ami'),
            ('min_disk', 10),
            ('min_ram', 4),
            ('protected', True),
            ('unprotected', False),
            ('public', False),
            ('private', True),
            ('project', 'q'),
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.image_client.create_image.assert_called_with(
            name=self.new_image.name,
            container_format='ovf',
            disk_format='ami',
            min_disk=10,
            min_ram=4,
            is_protected=True,
            is_public=False,
            owner_id='q',
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.image_client.update_image.call_args_list, [])

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch('openstackclient.image.v1.image.open', name='Open')
    def test_image_create_file(self, mock_open):
        mock_file = mock.Mock(name='File')
        mock_open.return_value = mock_file
        mock_open.read.return_value = self.data

        arglist = [
            '--file',
            'filer',
            '--unprotected',
            '--public',
            '--property',
            'Alpha=1',
            '--property',
            'Beta=2',
            self.new_image.name,
        ]
        verifylist = [
            ('file', 'filer'),
            ('protected', False),
            ('unprotected', True),
            ('public', True),
            ('private', False),
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Ensure input file is opened
        mock_open.assert_called_with('filer', 'rb')

        # Ensure the input file is closed
        mock_file.close.assert_called_with()

        # ImageManager.create(name=, **)
        self.image_client.create_image.assert_called_with(
            name=self.new_image.name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
            is_protected=False,
            is_public=True,
            properties={
                'Alpha': '1',
                'Beta': '2',
            },
            data=mock_file,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.image_client.update_image.call_args_list, [])

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestImageDelete(image_fakes.TestImagev1):
    _image = image_fakes.create_one_image()

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.image_client.find_image = mock.Mock(return_value=self._image)
        self.image_client.delete_image = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = image.DeleteImage(self.app, None)

    def test_image_delete_no_options(self):
        arglist = [
            self._image.id,
        ]
        verifylist = [
            ('images', [self._image.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.image_client.delete_image.assert_called_with(self._image.id)
        self.assertIsNone(result)


class TestImageList(image_fakes.TestImagev1):
    _image = image_fakes.create_one_image()

    columns = (
        'ID',
        'Name',
        'Status',
    )
    datalist = ((_image.id, _image.name, _image.status),)

    # create a image_info as the side_effect of the fake image_list()
    info = {
        'id': _image.id,
        'name': _image.name,
        'owner': _image.owner_id,
        'container_format': _image.container_format,
        'disk_format': _image.disk_format,
        'min_disk': _image.min_disk,
        'min_ram': _image.min_ram,
        'is_public': _image.is_public,
        'protected': _image.is_protected,
        'properties': _image.properties,
    }
    image_info = copy.deepcopy(info)

    def setUp(self):
        super().setUp()

        self.image_client.images = mock.Mock()
        self.image_client.images.side_effect = [
            [self._image],
            [],
        ]

        # Get the command object to test
        self.cmd = image.ListImage(self.app, None)

    def test_image_list_no_options(self):
        arglist = []
        verifylist = [
            ('public', False),
            ('private', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_public_option(self):
        arglist = [
            '--public',
        ]
        verifylist = [
            ('public', True),
            ('private', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            is_public=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_private_option(self):
        arglist = [
            '--private',
        ]
        verifylist = [
            ('public', False),
            ('private', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            is_private=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_long_option(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with()

        collist = (
            'ID',
            'Name',
            'Disk Format',
            'Container Format',
            'Size',
            'Checksum',
            'Status',
            'Visibility',
            'Protected',
            'Project',
            'Properties',
        )

        self.assertEqual(collist, columns)
        datalist = (
            (
                self._image.id,
                self._image.name,
                self._image.disk_format,
                self._image.container_format,
                self._image.size,
                self._image.checksum,
                self._image.status,
                image.VisibilityColumn(self._image.is_public),
                self._image.is_protected,
                self._image.owner_id,
                format_columns.DictColumn(
                    {'Alpha': 'a', 'Beta': 'b', 'Gamma': 'g'}
                ),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    @mock.patch('osc_lib.api.utils.simple_filter')
    def test_image_list_property_option(self, sf_mock):
        sf_mock.side_effect = [
            [self.image_info],
            [],
        ]

        arglist = [
            '--property',
            'a=1',
        ]
        verifylist = [
            ('property', {'a': '1'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with()
        sf_mock.assert_called_with(
            [self._image],
            attr='a',
            value='1',
            property_field='properties',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    @mock.patch('osc_lib.utils.sort_items')
    def test_image_list_sort_option(self, si_mock):
        si_mock.side_effect = [
            [self._image],
            [],
        ]

        arglist = ['--sort', 'name:asc']
        verifylist = [('sort', 'name:asc')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with()
        si_mock.assert_called_with([self._image], 'name:asc')

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestImageSet(image_fakes.TestImagev1):
    _image = image_fakes.create_one_image()

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.image_client.find_image = mock.Mock(return_value=self._image)
        self.image_client.update_image = mock.Mock(return_value=self._image)

        # Get the command object to test
        self.cmd = image.SetImage(self.app, None)

    def test_image_set_no_options(self):
        arglist = [
            self._image.name,
        ]
        verifylist = [
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.image_client.update_image.assert_called_with(self._image.id, **{})
        self.assertIsNone(result)

    def test_image_set_options(self):
        arglist = [
            '--name',
            'new-name',
            '--min-disk',
            '2',
            '--min-ram',
            '4',
            '--container-format',
            'ovf',
            '--disk-format',
            'vmdk',
            '--size',
            '35165824',
            '--project',
            'new-owner',
            self._image.name,
        ]
        verifylist = [
            ('name', 'new-name'),
            ('min_disk', 2),
            ('min_ram', 4),
            ('container_format', 'ovf'),
            ('disk_format', 'vmdk'),
            ('size', 35165824),
            ('project', 'new-owner'),
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': 'new-name',
            'owner': 'new-owner',
            'min_disk': 2,
            'min_ram': 4,
            'container_format': 'ovf',
            'disk_format': 'vmdk',
            'size': 35165824,
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_bools1(self):
        arglist = [
            '--protected',
            '--private',
            self._image.name,
        ]
        verifylist = [
            ('protected', True),
            ('unprotected', False),
            ('public', False),
            ('private', True),
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'is_protected': True,
            'is_public': False,
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_bools2(self):
        arglist = [
            '--unprotected',
            '--public',
            self._image.name,
        ]
        verifylist = [
            ('protected', False),
            ('unprotected', True),
            ('public', True),
            ('private', False),
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'is_protected': False,
            'is_public': True,
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_properties(self):
        arglist = [
            '--property',
            'Alpha=1',
            '--property',
            'Beta=2',
            self._image.name,
        ]
        verifylist = [
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'properties': {
                'Alpha': '1',
                'Beta': '2',
                'Gamma': 'g',
            },
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_update_volume(self):
        # Set up VolumeManager Mock
        volumes_mock = self.volume_client.volumes
        volumes_mock.reset_mock()
        volumes_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy({'id': 'vol1', 'name': 'volly'}),
            loaded=True,
        )
        response = {
            "id": 'volume_id',
            "updated_at": 'updated_at',
            "status": 'uploading',
            "display_description": 'desc',
            "size": 'size',
            "volume_type": 'volume_type',
            "container_format": image.DEFAULT_CONTAINER_FORMAT,
            "disk_format": image.DEFAULT_DISK_FORMAT,
            "image": self._image.name,
        }
        full_response = {"os-volume_upload_image": response}
        volumes_mock.upload_to_image.return_value = (201, full_response)

        arglist = [
            '--volume',
            'volly',
            '--name',
            'updated_image',
            self._image.name,
        ]
        verifylist = [
            ('private', False),
            ('protected', False),
            ('public', False),
            ('unprotected', False),
            ('volume', 'volly'),
            ('force', False),
            ('name', 'updated_image'),
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # VolumeManager.upload_to_image(volume, force, image_name,
        #     container_format, disk_format)
        volumes_mock.upload_to_image.assert_called_with(
            'vol1',
            False,
            self._image.name,
            '',
            '',
        )
        # ImageManager.update(image_id, remove_props=, **)
        self.image_client.update_image.assert_called_with(
            self._image.id,
            name='updated_image',
            volume='volly',
        )
        self.assertIsNone(result)

    def test_image_set_numeric_options_to_zero(self):
        arglist = [
            '--min-disk',
            '0',
            '--min-ram',
            '0',
            self._image.name,
        ]
        verifylist = [
            ('min_disk', 0),
            ('min_ram', 0),
            ('image', self._image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'min_disk': 0,
            'min_ram': 0,
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)


class TestImageShow(image_fakes.TestImagev1):
    _image = image_fakes.create_one_image(attrs={'size': 2000})
    columns = (
        'container_format',
        'disk_format',
        'id',
        'is_public',
        'min_disk',
        'min_ram',
        'name',
        'owner',
        'properties',
        'protected',
        'size',
    )
    data = (
        _image.container_format,
        _image.disk_format,
        _image.id,
        _image.is_public,
        _image.min_disk,
        _image.min_ram,
        _image.name,
        _image.owner_id,
        format_columns.DictColumn(_image.properties),
        _image.is_protected,
        _image.size,
    )

    def setUp(self):
        super().setUp()

        self.image_client.find_image = mock.Mock(return_value=self._image)

        # Get the command object to test
        self.cmd = image.ShowImage(self.app, None)

    def test_image_show(self):
        arglist = [
            self._image.id,
        ]
        verifylist = [
            ('image', self._image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.find_image.assert_called_with(
            self._image.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_image_show_human_readable(self):
        arglist = [
            '--human-readable',
            self._image.id,
        ]
        verifylist = [
            ('human_readable', True),
            ('image', self._image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.find_image.assert_called_with(
            self._image.id, ignore_missing=False
        )

        size_index = columns.index('size')
        self.assertEqual(data[size_index].human_readable(), '2K')
