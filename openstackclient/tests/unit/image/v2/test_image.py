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
import io
import tempfile
from unittest import mock

from cinderclient import api_versions
from openstack import exceptions as sdk_exceptions
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.image.v2 import image as _image
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes


class TestImage(image_fakes.TestImagev2, volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        # Get shortcut to the Mocks in identity client
        self.project_mock = self.identity_client.projects
        self.project_mock.reset_mock()
        self.domain_mock = self.identity_client.domains
        self.domain_mock.reset_mock()
        self.volumes_mock = self.volume_client.volumes
        fake_body = {
            'os-volume_upload_image': {'volume_type': {'name': 'fake_type'}}
        }
        self.volumes_mock.upload_to_image.return_value = (200, fake_body)
        self.volumes_mock.reset_mock()


class TestImageCreate(TestImage):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super().setUp()

        self.new_image = image_fakes.create_one_image()
        self.image_client.create_image.return_value = self.new_image
        self.image_client.update_image.return_value = self.new_image
        self.image_client.get_image.return_value = self.new_image

        self.project_mock.get.return_value = self.project

        self.domain_mock.get.return_value = self.domain

        (self.expected_columns, self.expected_data) = zip(
            *sorted(_image._format_image(self.new_image).items())
        )

        # Get the command object to test
        self.cmd = _image.CreateImage(self.app, None)

    @mock.patch("sys.stdin", side_effect=[None])
    def test_image_reserve_no_options(self, raw_input):
        arglist = [self.new_image.name]
        verifylist = [
            ('container_format', _image.DEFAULT_CONTAINER_FORMAT),
            ('disk_format', _image.DEFAULT_DISK_FORMAT),
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
            allow_duplicates=True,
            container_format=_image.DEFAULT_CONTAINER_FORMAT,
            disk_format=_image.DEFAULT_DISK_FORMAT,
        )
        self.image_client.get_image.assert_called_once_with(self.new_image)

        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

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
            '--protected' if self.new_image.is_protected else '--unprotected',
            (
                '--private'
                if self.new_image.visibility == 'private'
                else '--public'
            ),
            '--project',
            self.new_image.owner_id,
            '--project-domain',
            self.domain.id,
            self.new_image.name,
        ]
        verifylist = [
            ('container_format', 'ovf'),
            ('disk_format', 'ami'),
            ('min_disk', 10),
            ('min_ram', 4),
            ('is_protected', self.new_image.is_protected),
            ('visibility', self.new_image.visibility),
            ('project', self.new_image.owner_id),
            ('project_domain', self.domain.id),
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
            allow_duplicates=True,
            container_format='ovf',
            disk_format='ami',
            min_disk=10,
            min_ram=4,
            owner_id=self.project.id,
            is_protected=self.new_image.is_protected,
            visibility=self.new_image.visibility,
        )
        self.image_client.get_image.assert_called_once_with(self.new_image)

        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

    def test_image_create_with_unexist_project(self):
        self.project_mock.get.side_effect = exceptions.NotFound(None)
        self.project_mock.find.side_effect = exceptions.NotFound(None)

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
            'unexist_owner',
            'graven',
        ]
        verifylist = [
            ('container_format', 'ovf'),
            ('disk_format', 'ami'),
            ('min_disk', 10),
            ('min_ram', 4),
            ('is_protected', True),
            ('visibility', 'private'),
            ('project', 'unexist_owner'),
            ('name', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_image_create_file(self):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()

        arglist = [
            '--file',
            imagefile.name,
            (
                '--unprotected'
                if not self.new_image.is_protected
                else '--protected'
            ),
            (
                '--public'
                if self.new_image.visibility == 'public'
                else '--private'
            ),
            '--property',
            'Alpha=1',
            '--property',
            'Beta=2',
            '--tag',
            self.new_image.tags[0],
            '--tag',
            self.new_image.tags[1],
            self.new_image.name,
        ]
        verifylist = [
            ('filename', imagefile.name),
            ('is_protected', self.new_image.is_protected),
            ('visibility', self.new_image.visibility),
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('tags', self.new_image.tags),
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
            allow_duplicates=True,
            container_format=_image.DEFAULT_CONTAINER_FORMAT,
            disk_format=_image.DEFAULT_DISK_FORMAT,
            is_protected=self.new_image.is_protected,
            visibility=self.new_image.visibility,
            Alpha='1',
            Beta='2',
            tags=self.new_image.tags,
            filename=imagefile.name,
        )
        self.image_client.get_image.assert_called_once_with(self.new_image)

        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

    @mock.patch('openstackclient.image.v2.image.get_data_from_stdin')
    def test_image_create__progress_ignore_with_stdin(
        self,
        mock_get_data_from_stdin,
    ):
        fake_stdin = io.BytesIO(b'some fake data')
        mock_get_data_from_stdin.return_value = fake_stdin

        arglist = [
            '--progress',
            self.new_image.name,
        ]
        verifylist = [
            ('progress', True),
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.create_image.assert_called_with(
            name=self.new_image.name,
            allow_duplicates=True,
            container_format=_image.DEFAULT_CONTAINER_FORMAT,
            disk_format=_image.DEFAULT_DISK_FORMAT,
            data=fake_stdin,
            validate_checksum=False,
        )
        self.image_client.get_image.assert_called_once_with(self.new_image)

        self.assertEqual(self.expected_columns, columns)
        self.assertCountEqual(self.expected_data, data)

    def test_image_create_dead_options(self):
        arglist = [
            '--store',
            'somewhere',
            self.new_image.name,
        ]
        verifylist = [
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    @mock.patch('sys.stdin', side_effect=[None])
    def test_image_create_import(self, raw_input):
        arglist = [
            '--import',
            self.new_image.name,
        ]
        verifylist = [
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.image_client.create_image.assert_called_with(
            name=self.new_image.name,
            allow_duplicates=True,
            container_format=_image.DEFAULT_CONTAINER_FORMAT,
            disk_format=_image.DEFAULT_DISK_FORMAT,
            use_import=True,
        )
        self.image_client.get_image.assert_called_once_with(self.new_image)

    @mock.patch('osc_lib.utils.find_resource')
    @mock.patch('openstackclient.image.v2.image.get_data_from_stdin')
    def test_image_create_from_volume(self, mock_get_data_f, mock_get_vol):
        fake_vol_id = 'fake-volume-id'
        mock_get_data_f.return_value = None

        class FakeVolume:
            id = fake_vol_id

        mock_get_vol.return_value = FakeVolume()

        arglist = [
            '--volume',
            fake_vol_id,
            self.new_image.name,
        ]
        verifylist = [
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.upload_to_image.assert_called_with(
            fake_vol_id,
            False,
            self.new_image.name,
            'bare',
            'raw',
            visibility=None,
            protected=None,
        )

    @mock.patch('osc_lib.utils.find_resource')
    @mock.patch('openstackclient.image.v2.image.get_data_from_stdin')
    def test_image_create_from_volume_fail(
        self, mock_get_data_f, mock_get_vol
    ):
        fake_vol_id = 'fake-volume-id'
        mock_get_data_f.return_value = None

        class FakeVolume:
            id = fake_vol_id

        mock_get_vol.return_value = FakeVolume()

        arglist = ['--volume', fake_vol_id, self.new_image.name, '--public']
        verifylist = [
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    @mock.patch('osc_lib.utils.find_resource')
    @mock.patch('openstackclient.image.v2.image.get_data_from_stdin')
    def test_image_create_from_volume_v31(self, mock_get_data_f, mock_get_vol):
        self.volume_client.api_version = api_versions.APIVersion('3.1')

        fake_vol_id = 'fake-volume-id'
        mock_get_data_f.return_value = None

        class FakeVolume:
            id = fake_vol_id

        mock_get_vol.return_value = FakeVolume()

        arglist = ['--volume', fake_vol_id, self.new_image.name, '--public']
        verifylist = [
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volumes_mock.upload_to_image.assert_called_with(
            fake_vol_id,
            False,
            self.new_image.name,
            'bare',
            'raw',
            visibility='public',
            protected=False,
        )


class TestAddProjectToImage(TestImage):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    _image = image_fakes.create_one_image()
    new_member = image_fakes.create_one_image_member(
        attrs={'image_id': _image.id, 'member_id': project.id}
    )

    columns = (
        'created_at',
        'image_id',
        'member_id',
        'schema',
        'status',
        'updated_at',
    )

    datalist = (
        new_member.created_at,
        _image.id,
        new_member.member_id,
        new_member.schema,
        new_member.status,
        new_member.updated_at,
    )

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.image_client.find_image.return_value = self._image

        # Update the image_id in the MEMBER dict
        self.image_client.add_member.return_value = self.new_member
        self.project_mock.get.return_value = self.project
        self.domain_mock.get.return_value = self.domain
        # Get the command object to test
        self.cmd = _image.AddProjectToImage(self.app, None)

    def test_add_project_to_image_no_option(self):
        arglist = [
            self._image.id,
            self.project.id,
        ]
        verifylist = [
            ('image', self._image.id),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.add_member.assert_called_with(
            image=self._image.id, member_id=self.project.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_add_project_to_image_with_option(self):
        arglist = [
            self._image.id,
            self.project.id,
            '--project-domain',
            self.domain.id,
        ]
        verifylist = [
            ('image', self._image.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.add_member.assert_called_with(
            image=self._image.id, member_id=self.project.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestImageDelete(TestImage):
    def setUp(self):
        super().setUp()

        self.image_client.delete_image.return_value = None

        # Get the command object to test
        self.cmd = _image.DeleteImage(self.app, None)

    def test_image_delete_no_options(self):
        images = image_fakes.create_images(count=1)

        arglist = [
            images[0].id,
        ]
        verifylist = [
            ('images', [images[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        result = self.cmd.take_action(parsed_args)

        self.image_client.delete_image.assert_called_with(
            images[0].id, store=parsed_args.store, ignore_missing=False
        )
        self.assertIsNone(result)

    def test_image_delete_from_store(self):
        images = image_fakes.create_images(count=1)

        arglist = [
            images[0].id,
            '--store',
            'store1',
        ]
        verifylist = [('images', [images[0].id]), ('store', 'store1')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        result = self.cmd.take_action(parsed_args)

        self.image_client.delete_image.assert_called_with(
            images[0].id, store=parsed_args.store, ignore_missing=False
        )
        self.assertIsNone(result)

    def test_image_delete_multi_images(self):
        images = image_fakes.create_images(count=3)

        arglist = [i.id for i in images]
        verifylist = [
            ('images', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        result = self.cmd.take_action(parsed_args)

        calls = [
            mock.call(i.id, store=parsed_args.store, ignore_missing=False)
            for i in images
        ]
        self.image_client.delete_image.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_image_delete_from_store_without_multi_backend(self):
        images = image_fakes.create_images(count=1)

        arglist = [images[0].id, '--store', 'store1']
        verifylist = [('images', [images[0].id]), ('store', 'store1')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        self.image_client.delete_image.side_effect = (
            sdk_exceptions.ResourceNotFound
        )
        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            "Multi Backend support not enabled",
            str(exc),
        )

    def test_image_delete_multi_images_exception(self):
        images = image_fakes.create_images(count=2)
        arglist = [
            images[0].id,
            images[1].id,
            'x-y-x',
        ]
        verifylist = [('images', arglist)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception in utils.find_resource()
        # In image v2, we use utils.find_resource() to find a network.
        # It calls get() several times, but find() only one time. So we
        # choose to fake get() always raise exception, then pass through.
        # And fake find() to find the real network or not.
        ret_find = [images[0], images[1], sdk_exceptions.ResourceNotFound()]

        self.image_client.find_image.side_effect = ret_find

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        calls = [
            mock.call(i.id, store=parsed_args.store, ignore_missing=False)
            for i in images
        ]
        self.image_client.delete_image.assert_has_calls(calls)


class TestImageList(TestImage):
    _image = image_fakes.create_one_image()

    columns = (
        'ID',
        'Name',
        'Status',
    )

    datalist = (
        (
            _image.id,
            _image.name,
            None,
        ),
    )

    def setUp(self):
        super().setUp()

        self.image_client.images.side_effect = [[self._image], []]

        # Get the command object to test
        self.cmd = _image.ListImage(self.app, None)

    def test_image_list_no_options(self):
        arglist = []
        verifylist = [
            ('visibility', None),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            # marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_image_list_public_option(self):
        arglist = [
            '--public',
        ]
        verifylist = [
            ('visibility', 'public'),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            visibility='public',
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_image_list_private_option(self):
        arglist = [
            '--private',
        ]
        verifylist = [
            ('visibility', 'private'),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            visibility='private',
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_image_list_community_option(self):
        arglist = [
            '--community',
        ]
        verifylist = [
            ('visibility', 'community'),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            visibility='community',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_shared_option(self):
        arglist = [
            '--shared',
        ]
        verifylist = [
            ('visibility', 'shared'),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            visibility='shared',
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_image_list_all_option(self):
        arglist = [
            '--all',
        ]
        verifylist = [
            ('visibility', 'all'),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            visibility='all',
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_image_list_shared_member_status_option(self):
        arglist = ['--shared', '--member-status', 'all']
        verifylist = [
            ('visibility', 'shared'),
            ('long', False),
            ('member_status', 'all'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            visibility='shared',
            member_status='all',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_shared_member_status_lower(self):
        arglist = ['--shared', '--member-status', 'ALl']
        verifylist = [
            ('visibility', 'shared'),
            ('long', False),
            ('member_status', 'all'),
        ]
        self.check_parser(self.cmd, arglist, verifylist)

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
            'Tags',
        )

        self.assertEqual(collist, columns)
        datalist = (
            (
                self._image.id,
                self._image.name,
                None,
                None,
                None,
                None,
                None,
                self._image.visibility,
                self._image.is_protected,
                self._image.owner_id,
                format_columns.ListColumn(self._image.tags),
            ),
        )
        self.assertCountEqual(datalist, tuple(data))

    @mock.patch('osc_lib.api.utils.simple_filter')
    def test_image_list_property_option(self, sf_mock):
        sf_mock.return_value = [copy.deepcopy(self._image)]

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
        self.assertCountEqual(self.datalist, tuple(data))

    @mock.patch('osc_lib.utils.sort_items')
    def test_image_list_sort_option(self, si_mock):
        si_mock.return_value = [copy.deepcopy(self._image)]

        arglist = ['--sort', 'name:asc']
        verifylist = [('sort', 'name:asc')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with()
        si_mock.assert_called_with(
            [self._image],
            'name:asc',
            str,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    def test_image_list_limit_option(self):
        ret_limit = 1
        arglist = [
            '--limit',
            str(ret_limit),
        ]
        verifylist = [
            ('limit', ret_limit),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            limit=ret_limit,
            paginated=False,
            # marker=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(ret_limit, len(tuple(data)))

    def test_image_list_project_option(self):
        self.image_client.find_image = mock.Mock(return_value=self._image)
        arglist = [
            '--project',
            'nova',
        ]
        verifylist = [
            ('project', 'nova'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, tuple(data))

    @mock.patch('osc_lib.utils.find_resource')
    def test_image_list_marker_option(self, fr_mock):
        self.image_client.find_image = mock.Mock(return_value=self._image)

        arglist = [
            '--marker',
            'graven',
        ]
        verifylist = [
            ('marker', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            marker=self._image.id,
        )

        self.image_client.find_image.assert_called_with(
            'graven',
            ignore_missing=False,
        )

    def test_image_list_name_option(self):
        arglist = [
            '--name',
            'abc',
        ]
        verifylist = [
            ('name', 'abc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(
            name='abc',
            # marker=self._image.id
        )

    def test_image_list_status_option(self):
        arglist = [
            '--status',
            'active',
        ]
        verifylist = [
            ('status', 'active'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(status='active')

    def test_image_list_hidden_option(self):
        arglist = [
            '--hidden',
        ]
        verifylist = [
            ('is_hidden', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(is_hidden=True)

    def test_image_list_tag_option(self):
        arglist = ['--tag', 'abc', '--tag', 'cba']
        verifylist = [
            ('tag', ['abc', 'cba']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.images.assert_called_with(tag=['abc', 'cba'])


class TestListImageProjects(TestImage):
    project = identity_fakes.FakeProject.create_one_project()
    _image = image_fakes.create_one_image()
    member = image_fakes.create_one_image_member(
        attrs={'image_id': _image.id, 'member_id': project.id}
    )

    columns = ("Image ID", "Member ID", "Status")

    datalist = [
        (
            _image.id,
            member.member_id,
            member.status,
        )
    ]

    def setUp(self):
        super().setUp()

        self.image_client.find_image.return_value = self._image
        self.image_client.members.return_value = [self.member]

        self.cmd = _image.ListImageProjects(self.app, None)

    def test_image_member_list(self):
        arglist = [self._image.id]
        verifylist = [('image', self._image.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.members.assert_called_with(image=self._image.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, list(data))


class TestRemoveProjectImage(TestImage):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super().setUp()

        self._image = image_fakes.create_one_image()
        # This is the return value for utils.find_resource()
        self.image_client.find_image.return_value = self._image

        self.project_mock.get.return_value = self.project
        self.domain_mock.get.return_value = self.domain
        self.image_client.remove_member.return_value = None
        # Get the command object to test
        self.cmd = _image.RemoveProjectImage(self.app, None)

    def test_remove_project_image_no_options(self):
        arglist = [
            self._image.id,
            self.project.id,
        ]
        verifylist = [
            ('image', self._image.id),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.image_client.find_image.assert_called_with(
            self._image.id, ignore_missing=False
        )

        self.image_client.remove_member.assert_called_with(
            member=self.project.id,
            image=self._image.id,
        )
        self.assertIsNone(result)

    def test_remove_project_image_with_options(self):
        arglist = [
            self._image.id,
            self.project.id,
            '--project-domain',
            self.domain.id,
        ]
        verifylist = [
            ('image', self._image.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.image_client.remove_member.assert_called_with(
            member=self.project.id,
            image=self._image.id,
        )
        self.assertIsNone(result)


class TestShowProjectImage(TestImage):
    _image = image_fakes.create_one_image()
    new_member = image_fakes.create_one_image_member(
        attrs={'image_id': _image.id, 'member_id': 'member1'}
    )

    columns = (
        'created_at',
        'image_id',
        'member_id',
        'schema',
        'status',
        'updated_at',
    )

    datalist = (
        new_member.created_at,
        _image.id,
        new_member.member_id,
        new_member.schema,
        new_member.status,
        new_member.updated_at,
    )

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.image_client.find_image.return_value = self._image

        self.image_client.get_member.return_value = self.new_member
        # Get the command object to test
        self.cmd = _image.ShowProjectImage(self.app, None)

    def test_show_project_image(self):
        arglist = [
            self._image.id,
            'member1',
        ]
        verifylist = [
            ('image', self._image.id),
            ('member', 'member1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.find_image.assert_called_with(
            self._image.id, ignore_missing=False
        )

        self.image_client.get_member.assert_called_with(
            member='member1',
            image=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestImageSet(TestImage):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    _image = image_fakes.create_one_image({'tags': []})

    def setUp(self):
        super().setUp()

        self.project_mock.get.return_value = self.project

        self.domain_mock.get.return_value = self.domain

        self.image_client.find_image.return_value = self._image

        self.app.client_manager.auth_ref = mock.Mock(
            project_id=self.project.id,
        )

        # Get the command object to test
        self.cmd = _image.SetImage(self.app, None)

    def test_image_set_no_options(self):
        arglist = [
            '0f41529e-7c12-4de8-be2d-181abb825b3c',
        ]
        verifylist = [('image', '0f41529e-7c12-4de8-be2d-181abb825b3c')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        # we'll have called this but not set anything
        self.image_client.update_image.assert_called_once_with(
            self._image.id,
        )

    def test_image_set_membership_option_accept(self):
        membership = image_fakes.create_one_image_member(
            attrs={
                'image_id': '0f41529e-7c12-4de8-be2d-181abb825b3c',
                'member_id': self.project.id,
            }
        )
        self.image_client.update_member.return_value = membership

        arglist = [
            '--accept',
            self._image.id,
        ]
        verifylist = [('membership', 'accepted'), ('image', self._image.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_client.update_member.assert_called_once_with(
            image=self._image.id,
            member=self.app.client_manager.auth_ref.project_id,
            status='accepted',
        )

        # Assert that the 'update image" route is also called, in addition to
        # the 'update membership' route.
        self.image_client.update_image.assert_called_with(self._image.id)

    def test_image_set_membership_option_reject(self):
        membership = image_fakes.create_one_image_member(
            attrs={
                'image_id': '0f41529e-7c12-4de8-be2d-181abb825b3c',
                'member_id': self.project.id,
            }
        )
        self.image_client.update_member.return_value = membership

        arglist = [
            '--reject',
            '0f41529e-7c12-4de8-be2d-181abb825b3c',
        ]
        verifylist = [
            ('membership', 'rejected'),
            ('image', '0f41529e-7c12-4de8-be2d-181abb825b3c'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_client.update_member.assert_called_once_with(
            image=self._image.id,
            member=self.app.client_manager.auth_ref.project_id,
            status='rejected',
        )

        # Assert that the 'update image" route is also called, in addition to
        # the 'update membership' route.
        self.image_client.update_image.assert_called_with(self._image.id)

    def test_image_set_membership_option_pending(self):
        membership = image_fakes.create_one_image_member(
            attrs={
                'image_id': '0f41529e-7c12-4de8-be2d-181abb825b3c',
                'member_id': self.project.id,
            }
        )
        self.image_client.update_member.return_value = membership

        arglist = [
            '--pending',
            '0f41529e-7c12-4de8-be2d-181abb825b3c',
        ]
        verifylist = [
            ('membership', 'pending'),
            ('image', '0f41529e-7c12-4de8-be2d-181abb825b3c'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_client.update_member.assert_called_once_with(
            image=self._image.id,
            member=self.app.client_manager.auth_ref.project_id,
            status='pending',
        )

        # Assert that the 'update image" route is also called, in addition to
        # the 'update membership' route.
        self.image_client.update_image.assert_called_with(self._image.id)

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
            '--project',
            self.project.name,
            '--project-domain',
            self.domain.id,
            self._image.id,
        ]
        verifylist = [
            ('name', 'new-name'),
            ('min_disk', 2),
            ('min_ram', 4),
            ('container_format', 'ovf'),
            ('disk_format', 'vmdk'),
            ('project', self.project.name),
            ('project_domain', self.domain.id),
            ('image', self._image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': 'new-name',
            'owner_id': self.project.id,
            'min_disk': 2,
            'min_ram': 4,
            'container_format': 'ovf',
            'disk_format': 'vmdk',
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_with_unexist_project(self):
        self.project_mock.get.side_effect = exceptions.NotFound(None)
        self.project_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--project',
            'unexist_owner',
            '0f41529e-7c12-4de8-be2d-181abb825b3c',
        ]
        verifylist = [
            ('project', 'unexist_owner'),
            ('image', '0f41529e-7c12-4de8-be2d-181abb825b3c'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_image_set_bools1(self):
        arglist = [
            '--protected',
            '--private',
            'graven',
        ]
        verifylist = [
            ('is_protected', True),
            ('visibility', 'private'),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'is_protected': True,
            'visibility': 'private',
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
            'graven',
        ]
        verifylist = [
            ('is_protected', False),
            ('visibility', 'public'),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'is_protected': False,
            'visibility': 'public',
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
            'graven',
        ]
        verifylist = [
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'Alpha': '1',
            'Beta': '2',
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_fake_properties(self):
        arglist = [
            '--architecture',
            'z80',
            '--instance-id',
            '12345',
            '--kernel-id',
            '67890',
            '--os-distro',
            'cpm',
            '--os-version',
            '2.2H',
            '--ramdisk-id',
            'xyzpdq',
            'graven',
        ]
        verifylist = [
            ('architecture', 'z80'),
            ('instance_id', '12345'),
            ('kernel_id', '67890'),
            ('os_distro', 'cpm'),
            ('os_version', '2.2H'),
            ('ramdisk_id', 'xyzpdq'),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'architecture': 'z80',
            'instance_id': '12345',
            'kernel_id': '67890',
            'os_distro': 'cpm',
            'os_version': '2.2H',
            'ramdisk_id': 'xyzpdq',
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_tag(self):
        arglist = [
            '--tag',
            'test-tag',
            'graven',
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['test-tag'],
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_activate(self):
        arglist = [
            '--tag',
            'test-tag',
            '--activate',
            'graven',
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['test-tag'],
        }

        self.image_client.reactivate_image.assert_called_with(
            self._image.id,
        )
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_deactivate(self):
        arglist = [
            '--tag',
            'test-tag',
            '--deactivate',
            'graven',
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['test-tag'],
        }

        self.image_client.deactivate_image.assert_called_with(
            self._image.id,
        )
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_tag_merge(self):
        old_image = self._image
        old_image['tags'] = ['old1', 'new2']
        self.image_client.find_image.return_value = old_image
        arglist = [
            '--tag',
            'test-tag',
            'graven',
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['old1', 'new2', 'test-tag'],
        }
        # ImageManager.update(image, **kwargs)
        a, k = self.image_client.update_image.call_args
        self.assertEqual(self._image.id, a[0])
        self.assertIn('tags', k)
        self.assertEqual(set(kwargs['tags']), set(k['tags']))
        self.assertIsNone(result)

    def test_image_set_tag_merge_dupe(self):
        old_image = self._image
        old_image['tags'] = ['old1', 'new2']
        self.image_client.find_image.return_value = old_image
        arglist = [
            '--tag',
            'old1',
            'graven',
        ]
        verifylist = [
            ('tags', ['old1']),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['new2', 'old1'],
        }
        # ImageManager.update(image, **kwargs)
        a, k = self.image_client.update_image.call_args
        self.assertEqual(self._image.id, a[0])
        self.assertIn('tags', k)
        self.assertEqual(set(kwargs['tags']), set(k['tags']))
        self.assertIsNone(result)

    def test_image_set_dead_options(self):
        arglist = [
            '--visibility',
            '1-mile',
            'graven',
        ]
        verifylist = [
            ('dead_visibility', '1-mile'),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_image_set_numeric_options_to_zero(self):
        arglist = [
            '--min-disk',
            '0',
            '--min-ram',
            '0',
            'graven',
        ]
        verifylist = [
            ('min_disk', 0),
            ('min_ram', 0),
            ('image', 'graven'),
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

    def test_image_set_hidden(self):
        arglist = [
            '--hidden',
            '--public',
            'graven',
        ]
        verifylist = [
            ('is_hidden', True),
            ('visibility', 'public'),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'is_hidden': True,
            'visibility': 'public',
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_unhidden(self):
        arglist = [
            '--unhidden',
            '--public',
            'graven',
        ]
        verifylist = [
            ('is_hidden', False),
            ('visibility', 'public'),
            ('image', 'graven'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'is_hidden': False,
            'visibility': 'public',
        }
        # ImageManager.update(image, **kwargs)
        self.image_client.update_image.assert_called_with(
            self._image.id, **kwargs
        )
        self.assertIsNone(result)


class TestImageShow(TestImage):
    new_image = image_fakes.create_one_image(attrs={'size': 1000})

    _data = image_fakes.create_one_image()

    columns = ('id', 'name', 'owner', 'protected', 'tags', 'visibility')

    data = (
        _data.id,
        _data.name,
        _data.owner_id,
        _data.is_protected,
        format_columns.ListColumn(_data.tags),
        _data.visibility,
    )

    def setUp(self):
        super().setUp()

        self.image_client.find_image = mock.Mock(return_value=self._data)

        # Get the command object to test
        self.cmd = _image.ShowImage(self.app, None)

    def test_image_show(self):
        arglist = [
            '0f41529e-7c12-4de8-be2d-181abb825b3c',
        ]
        verifylist = [
            ('image', '0f41529e-7c12-4de8-be2d-181abb825b3c'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.find_image.assert_called_with(
            '0f41529e-7c12-4de8-be2d-181abb825b3c', ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_image_show_human_readable(self):
        self.image_client.find_image.return_value = self.new_image
        arglist = [
            '--human-readable',
            self.new_image.id,
        ]
        verifylist = [
            ('human_readable', True),
            ('image', self.new_image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.image_client.find_image.assert_called_with(
            self.new_image.id, ignore_missing=False
        )

        size_index = columns.index('size')
        self.assertEqual(data[size_index], '1K')


class TestImageUnset(TestImage):
    def setUp(self):
        super().setUp()

        attrs = {}
        attrs['tags'] = ['test']
        attrs['hw_rng_model'] = 'virtio'
        attrs['prop'] = 'test'
        attrs['prop2'] = 'fake'
        self.image = image_fakes.create_one_image(attrs)

        self.image_client.find_image.return_value = self.image
        self.image_client.remove_tag.return_value = self.image
        self.image_client.update_image.return_value = self.image

        # Get the command object to test
        self.cmd = _image.UnsetImage(self.app, None)

    def test_image_unset_no_options(self):
        arglist = [
            '0f41529e-7c12-4de8-be2d-181abb825b3c',
        ]
        verifylist = [('image', '0f41529e-7c12-4de8-be2d-181abb825b3c')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_image_unset_tag_option(self):
        arglist = [
            '--tag',
            'test',
            self.image.id,
        ]

        verifylist = [
            ('tags', ['test']),
            ('image', self.image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.image_client.remove_tag.assert_called_with(self.image.id, 'test')
        self.assertIsNone(result)

    def test_image_unset_property_option(self):
        arglist = [
            '--property',
            'hw_rng_model',
            '--property',
            'prop',
            self.image.id,
        ]

        verifylist = [
            ('properties', ['hw_rng_model', 'prop']),
            ('image', self.image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.image_client.update_image.assert_called_with(
            self.image, properties={'prop2': 'fake'}
        )

        self.assertIsNone(result)

    def test_image_unset_mixed_option(self):
        arglist = [
            '--tag',
            'test',
            '--property',
            'hw_rng_model',
            '--property',
            'prop',
            self.image.id,
        ]

        verifylist = [
            ('tags', ['test']),
            ('properties', ['hw_rng_model', 'prop']),
            ('image', self.image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.image_client.update_image.assert_called_with(
            self.image, properties={'prop2': 'fake'}
        )

        self.image_client.remove_tag.assert_called_with(self.image.id, 'test')
        self.assertIsNone(result)


class TestImageStage(TestImage):
    image = image_fakes.create_one_image({})

    def setUp(self):
        super().setUp()

        self.image_client.find_image.return_value = self.image

        self.cmd = _image.StageImage(self.app, None)

    def test_stage_image__from_file(self):
        imagefile = tempfile.NamedTemporaryFile(delete=False)
        imagefile.write(b'\0')
        imagefile.close()

        arglist = [
            '--file',
            imagefile.name,
            self.image.name,
        ]
        verifylist = [
            ('filename', imagefile.name),
            ('image', self.image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.stage_image.assert_called_once_with(
            self.image,
            filename=imagefile.name,
        )

    @mock.patch('openstackclient.image.v2.image.get_data_from_stdin')
    def test_stage_image__from_stdin(self, mock_get_data_from_stdin):
        fake_stdin = io.BytesIO(b"some initial binary data: \x00\x01")
        mock_get_data_from_stdin.return_value = fake_stdin

        arglist = [
            self.image.name,
        ]
        verifylist = [
            ('image', self.image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.stage_image.assert_called_once_with(
            self.image,
            data=fake_stdin,
        )


class TestImageImport(TestImage):
    image = image_fakes.create_one_image(
        {
            'container_format': 'bare',
            'disk_format': 'qcow2',
        }
    )
    import_info = image_fakes.create_one_import_info()

    def setUp(self):
        super().setUp()

        self.image_client.find_image.return_value = self.image
        self.image_client.get_import_info.return_value = self.import_info

        self.cmd = _image.ImportImage(self.app, None)

    def test_import_image__glance_direct(self):
        self.image.status = 'uploading'
        arglist = [
            self.image.name,
        ]
        verifylist = [
            ('image', self.image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.import_image.assert_called_once_with(
            self.image,
            method='glance-direct',
            uri=None,
            remote_region=None,
            remote_image_id=None,
            remote_service_interface=None,
            stores=None,
            all_stores=None,
            all_stores_must_succeed=False,
        )

    def test_import_image__web_download(self):
        self.image.status = 'queued'
        arglist = [
            self.image.name,
            '--method',
            'web-download',
            '--uri',
            'https://example.com/',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'web-download'),
            ('uri', 'https://example.com/'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.import_image.assert_called_once_with(
            self.image,
            method='web-download',
            uri='https://example.com/',
            remote_region=None,
            remote_image_id=None,
            remote_service_interface=None,
            stores=None,
            all_stores=None,
            all_stores_must_succeed=False,
        )

    # NOTE(stephenfin): We don't do this for all combinations since that would
    # be tedious af. You get the idea...
    def test_import_image__web_download_missing_options(self):
        arglist = [
            self.image.name,
            '--method',
            'web-download',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'web-download'),
            ('uri', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn("The '--uri' option is required ", str(exc))

        self.image_client.import_image.assert_not_called()

    # NOTE(stephenfin): Ditto
    def test_import_image__web_download_invalid_options(self):
        arglist = [
            self.image.name,
            '--method',
            'glance-direct',  # != web-download
            '--uri',
            'https://example.com/',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'glance-direct'),
            ('uri', 'https://example.com/'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn("The '--uri' option is only supported ", str(exc))

        self.image_client.import_image.assert_not_called()

    def test_import_image__web_download_invalid_image_state(self):
        self.image.status = 'uploading'  # != 'queued'
        arglist = [
            self.image.name,
            '--method',
            'web-download',
            '--uri',
            'https://example.com/',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'web-download'),
            ('uri', 'https://example.com/'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            "The 'web-download' import method can only be used with "
            "an image in status 'queued'",
            str(exc),
        )

        self.image_client.import_image.assert_not_called()

    def test_import_image__copy_image(self):
        self.image.status = 'active'
        arglist = [
            self.image.name,
            '--method',
            'copy-image',
            '--store',
            'fast',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'copy-image'),
            ('stores', ['fast']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.import_image.assert_called_once_with(
            self.image,
            method='copy-image',
            uri=None,
            remote_region=None,
            remote_image_id=None,
            remote_service_interface=None,
            stores=['fast'],
            all_stores=None,
            all_stores_must_succeed=False,
        )

    def test_import_image__copy_image_disallow_failure(self):
        self.image.status = 'active'
        arglist = [
            self.image.name,
            '--method',
            'copy-image',
            '--store',
            'fast',
            '--disallow-failure',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'copy-image'),
            ('stores', ['fast']),
            ('allow_failure', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.import_image.assert_called_once_with(
            self.image,
            method='copy-image',
            uri=None,
            remote_region=None,
            remote_image_id=None,
            remote_service_interface=None,
            stores=['fast'],
            all_stores=None,
            all_stores_must_succeed=True,
        )

    def test_import_image__glance_download(self):
        arglist = [
            self.image.name,
            '--method',
            'glance-download',
            '--remote-region',
            'eu/dublin',
            '--remote-image',
            'remote-image-id',
            '--remote-service-interface',
            'private',
        ]
        verifylist = [
            ('image', self.image.name),
            ('import_method', 'glance-download'),
            ('remote_region', 'eu/dublin'),
            ('remote_image', 'remote-image-id'),
            ('remote_service_interface', 'private'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.import_image.assert_called_once_with(
            self.image,
            method='glance-download',
            uri=None,
            remote_region='eu/dublin',
            remote_image_id='remote-image-id',
            remote_service_interface='private',
            stores=None,
            all_stores=None,
            all_stores_must_succeed=False,
        )


class TestImageSave(TestImage):
    image = image_fakes.create_one_image({})

    def setUp(self):
        super().setUp()

        self.image_client.find_image.return_value = self.image
        self.image_client.download_image.return_value = self.image

        # Get the command object to test
        self.cmd = _image.SaveImage(self.app, None)

    def test_save_data(self):
        arglist = ['--file', '/path/to/file', self.image.id]

        verifylist = [
            ('filename', '/path/to/file'),
            ('image', self.image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.image_client.download_image.assert_called_once_with(
            self.image.id, stream=True, output='/path/to/file'
        )


class TestImageGetData(TestImage):
    def test_get_data_from_stdin(self):
        fd = io.BytesIO(b"some initial binary data: \x00\x01")

        with mock.patch('sys.stdin') as stdin:
            stdin.return_value = fd
            stdin.isatty.return_value = False
            stdin.buffer = fd

            test_fd = _image.get_data_from_stdin()

            # Ensure data written to temp file is correct
            self.assertEqual(fd, test_fd)

    def test_get_data_from_stdin__interactive(self):
        fd = io.BytesIO(b"some initial binary data: \x00\x01")

        with mock.patch('sys.stdin') as stdin:
            # There is stdin, but interactive
            stdin.return_value = fd

            test_fd = _image.get_data_from_stdin()

            self.assertIsNone(test_fd)


class TestStoresInfo(TestImage):
    stores_info = image_fakes.create_one_stores_info()

    def setUp(self):
        super().setUp()

        self.image_client.stores.return_value = self.stores_info

        self.cmd = _image.StoresInfo(self.app, None)

    def test_stores_info(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)

        self.image_client.stores.assert_called()

    def test_stores_info_with_detail(self):
        arglist = ['--detail']
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)

        self.image_client.stores.assert_called_with(details=True)

    def test_stores_info_neg(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.image_client.stores.side_effect = (
            sdk_exceptions.ResourceNotFound()
        )

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            "Multi Backend support not enabled",
            str(exc),
        )
