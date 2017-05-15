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

from glanceclient.common import utils as glanceclient_utils
from glanceclient.v2 import schemas
import mock
from osc_lib.cli import format_columns
from osc_lib import exceptions
import warlock

from openstackclient.image.v2 import image
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestImage(image_fakes.TestImagev2):

    def setUp(self):
        super(TestImage, self).setUp()

        # Get shortcuts to the Mocks in image client
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()
        self.image_members_mock = self.app.client_manager.image.image_members
        self.image_members_mock.reset_mock()
        self.image_tags_mock = self.app.client_manager.image.image_tags
        self.image_tags_mock.reset_mock()

        # Get shortcut to the Mocks in identity client
        self.project_mock = self.app.client_manager.identity.projects
        self.project_mock.reset_mock()
        self.domain_mock = self.app.client_manager.identity.domains
        self.domain_mock.reset_mock()

    def setup_images_mock(self, count):
        images = image_fakes.FakeImage.create_images(count=count)

        self.images_mock.get = image_fakes.FakeImage.get_images(
            images,
            0)
        return images


class TestImageCreate(TestImage):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestImageCreate, self).setUp()

        self.new_image = image_fakes.FakeImage.create_one_image()
        self.images_mock.create.return_value = self.new_image

        self.project_mock.get.return_value = self.project

        self.domain_mock.get.return_value = self.domain

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = copy.deepcopy(
            self.new_image
        )
        self.images_mock.update.return_value = self.new_image

        # Get the command object to test
        self.cmd = image.CreateImage(self.app, None)

    def test_image_reserve_no_options(self):
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)
        arglist = [
            self.new_image.name
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
        self.images_mock.create.assert_called_with(
            name=self.new_image.name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.images_mock.upload.assert_called_with(
            mock.ANY, mock.ANY,
        )

        self.assertEqual(
            image_fakes.FakeImage.get_image_columns(self.new_image),
            columns)
        self.assertItemEqual(
            image_fakes.FakeImage.get_image_data(self.new_image),
            data)

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
            '--disk-format', 'ami',
            '--min-disk', '10',
            '--min-ram', '4',
            ('--protected'
                if self.new_image.protected else '--unprotected'),
            ('--private'
                if self.new_image.visibility == 'private' else '--public'),
            '--project', self.new_image.owner,
            '--project-domain', self.domain.id,
            self.new_image.name,
        ]
        verifylist = [
            ('container_format', 'ovf'),
            ('disk_format', 'ami'),
            ('min_disk', 10),
            ('min_ram', 4),
            ('protected', self.new_image.protected),
            ('unprotected', not self.new_image.protected),
            ('public', self.new_image.visibility == 'public'),
            ('private', self.new_image.visibility == 'private'),
            ('project', self.new_image.owner),
            ('project_domain', self.domain.id),
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ImageManager.create(name=, **)
        self.images_mock.create.assert_called_with(
            name=self.new_image.name,
            container_format='ovf',
            disk_format='ami',
            min_disk=10,
            min_ram=4,
            owner=self.project.id,
            protected=self.new_image.protected,
            visibility=self.new_image.visibility,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.images_mock.upload.assert_called_with(
            mock.ANY, mock.ANY,
        )

        self.assertEqual(
            image_fakes.FakeImage.get_image_columns(self.new_image),
            columns)
        self.assertItemEqual(
            image_fakes.FakeImage.get_image_data(self.new_image),
            data)

    def test_image_create_with_unexist_project(self):
        self.project_mock.get.side_effect = exceptions.NotFound(None)
        self.project_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--container-format', 'ovf',
            '--disk-format', 'ami',
            '--min-disk', '10',
            '--min-ram', '4',
            '--protected',
            '--private',
            '--project', 'unexist_owner',
            image_fakes.image_name,
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
            ('project', 'unexist_owner'),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    @mock.patch('glanceclient.common.utils.get_data_file', name='Open')
    def test_image_create_file(self, mock_open):
        mock_file = mock.MagicMock(name='File')
        mock_open.return_value = mock_file
        mock_open.read.return_value = (
            image_fakes.FakeImage.get_image_data(self.new_image))
        mock_exception = {
            'find.side_effect': exceptions.CommandError('x'),
        }
        self.images_mock.configure_mock(**mock_exception)

        arglist = [
            '--file', 'filer',
            ('--unprotected'
                if not self.new_image.protected else '--protected'),
            ('--public'
                if self.new_image.visibility == 'public' else '--private'),
            '--property', 'Alpha=1',
            '--property', 'Beta=2',
            '--tag', self.new_image.tags[0],
            '--tag', self.new_image.tags[1],
            self.new_image.name,
        ]
        verifylist = [
            ('file', 'filer'),
            ('protected', self.new_image.protected),
            ('unprotected', not self.new_image.protected),
            ('public', self.new_image.visibility == 'public'),
            ('private', self.new_image.visibility == 'private'),
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
        self.images_mock.create.assert_called_with(
            name=self.new_image.name,
            container_format=image.DEFAULT_CONTAINER_FORMAT,
            disk_format=image.DEFAULT_DISK_FORMAT,
            protected=self.new_image.protected,
            visibility=self.new_image.visibility,
            Alpha='1',
            Beta='2',
            tags=self.new_image.tags,
        )

        # Verify update() was not called, if it was show the args
        self.assertEqual(self.images_mock.update.call_args_list, [])

        self.images_mock.upload.assert_called_with(
            mock.ANY, mock.ANY,
        )

        self.assertEqual(
            image_fakes.FakeImage.get_image_columns(self.new_image),
            columns)
        self.assertItemEqual(
            image_fakes.FakeImage.get_image_data(self.new_image),
            data)

    def test_image_create_dead_options(self):

        arglist = [
            '--store', 'somewhere',
            self.new_image.name,
        ]
        verifylist = [
            ('name', self.new_image.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)


class TestAddProjectToImage(TestImage):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    _image = image_fakes.FakeImage.create_one_image()
    new_member = image_fakes.FakeImage.create_one_image_member(
        attrs={'image_id': _image.id,
               'member_id': project.id}
    )

    columns = (
        'image_id',
        'member_id',
        'status',
    )

    datalist = (
        _image.id,
        new_member.member_id,
        new_member.status,
    )

    def setUp(self):
        super(TestAddProjectToImage, self).setUp()

        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = self._image

        # Update the image_id in the MEMBER dict
        self.image_members_mock.create.return_value = self.new_member
        self.project_mock.get.return_value = self.project
        self.domain_mock.get.return_value = self.domain
        # Get the command object to test
        self.cmd = image.AddProjectToImage(self.app, None)

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
        self.image_members_mock.create.assert_called_with(
            self._image.id,
            self.project.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_add_project_to_image_with_option(self):
        arglist = [
            self._image.id,
            self.project.id,
            '--project-domain', self.domain.id,
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
        self.image_members_mock.create.assert_called_with(
            self._image.id,
            self.project.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestImageDelete(TestImage):

    def setUp(self):
        super(TestImageDelete, self).setUp()

        self.images_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = image.DeleteImage(self.app, None)

    def test_image_delete_no_options(self):
        images = self.setup_images_mock(count=1)

        arglist = [
            images[0].id,
        ]
        verifylist = [
            ('images', [images[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.images_mock.delete.assert_called_with(images[0].id)
        self.assertIsNone(result)

    def test_image_delete_multi_images(self):
        images = self.setup_images_mock(count=3)

        arglist = [i.id for i in images]
        verifylist = [
            ('images', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [mock.call(i.id) for i in images]
        self.images_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_image_delete_multi_images_exception(self):

        images = image_fakes.FakeImage.create_images(count=2)
        arglist = [
            images[0].id,
            images[1].id,
            'x-y-x',
        ]
        verifylist = [
            ('images', arglist)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception in utils.find_resource()
        # In image v2, we use utils.find_resource() to find a network.
        # It calls get() several times, but find() only one time. So we
        # choose to fake get() always raise exception, then pass through.
        # And fake find() to find the real network or not.
        ret_find = [
            images[0],
            images[1],
            exceptions.NotFound('404'),
        ]

        self.images_mock.get = Exception()
        self.images_mock.find.side_effect = ret_find
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)
        calls = [mock.call(i.id) for i in images]
        self.images_mock.delete.assert_has_calls(calls)


class TestImageList(TestImage):

    _image = image_fakes.FakeImage.create_one_image()

    columns = (
        'ID',
        'Name',
        'Status',
    )

    datalist = (
        _image.id,
        _image.name,
        '',
    ),

    def setUp(self):
        super(TestImageList, self).setUp()

        self.api_mock = mock.Mock()
        self.api_mock.image_list.side_effect = [
            [self._image], [],
        ]
        self.app.client_manager.image.api = self.api_mock

        # Get the command object to test
        self.cmd = image.ListImage(self.app, None)

    def test_image_list_no_options(self):
        arglist = []
        verifylist = [
            ('public', False),
            ('private', False),
            ('community', False),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.datalist, tuple(data))

    def test_image_list_public_option(self):
        arglist = [
            '--public',
        ]
        verifylist = [
            ('public', True),
            ('private', False),
            ('community', False),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            public=True,
            marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.datalist, tuple(data))

    def test_image_list_private_option(self):
        arglist = [
            '--private',
        ]
        verifylist = [
            ('public', False),
            ('private', True),
            ('community', False),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            private=True,
            marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.datalist, tuple(data))

    def test_image_list_community_option(self):
        arglist = [
            '--community',
        ]
        verifylist = [
            ('public', False),
            ('private', False),
            ('community', True),
            ('shared', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            community=True,
            marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_shared_option(self):
        arglist = [
            '--shared',
        ]
        verifylist = [
            ('public', False),
            ('private', False),
            ('community', False),
            ('shared', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            shared=True,
            marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.datalist, tuple(data))

    def test_image_list_shared_member_status_option(self):
        arglist = [
            '--shared',
            '--member-status', 'all'
        ]
        verifylist = [
            ('public', False),
            ('private', False),
            ('community', False),
            ('shared', True),
            ('long', False),
            ('member_status', 'all')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            shared=True,
            member_status='all',
            marker=self._image.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_image_list_shared_member_status_lower(self):
        arglist = [
            '--shared',
            '--member-status', 'ALl'
        ]
        verifylist = [
            ('public', False),
            ('private', False),
            ('community', False),
            ('shared', True),
            ('long', False),
            ('member_status', 'all')
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
        self.api_mock.image_list.assert_called_with(
            marker=self._image.id,
        )

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
        datalist = ((
            self._image.id,
            self._image.name,
            '',
            '',
            '',
            '',
            '',
            self._image.visibility,
            self._image.protected,
            self._image.owner,
            format_columns.ListColumn(self._image.tags),
        ), )
        self.assertListItemEqual(datalist, tuple(data))

    @mock.patch('osc_lib.api.utils.simple_filter')
    def test_image_list_property_option(self, sf_mock):
        sf_mock.return_value = [copy.deepcopy(self._image)]

        arglist = [
            '--property', 'a=1',
        ]
        verifylist = [
            ('property', {'a': '1'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=self._image.id,
        )
        sf_mock.assert_called_with(
            [self._image],
            attr='a',
            value='1',
            property_field='properties',
        )

        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.datalist, tuple(data))

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
        self.api_mock.image_list.assert_called_with(
            marker=self._image.id,
        )
        si_mock.assert_called_with(
            [self._image],
            'name:asc',
            str,
        )
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.datalist, tuple(data))

    def test_image_list_limit_option(self):
        ret_limit = 1
        arglist = [
            '--limit', str(ret_limit),
        ]
        verifylist = [
            ('limit', ret_limit),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            limit=ret_limit, marker=None
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(ret_limit, len(tuple(data)))

    @mock.patch('osc_lib.utils.find_resource')
    def test_image_list_marker_option(self, fr_mock):
        # tangchen: Since image_fakes.IMAGE is a dict, it cannot offer a .id
        #           operation. Will fix this by using FakeImage class instead
        #           of IMAGE dict.
        fr_mock.return_value = mock.Mock()
        fr_mock.return_value.id = image_fakes.image_id

        arglist = [
            '--marker', image_fakes.image_name,
        ]
        verifylist = [
            ('marker', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            marker=image_fakes.image_id,
        )

    def test_image_list_name_option(self):
        arglist = [
            '--name', 'abc',
        ]
        verifylist = [
            ('name', 'abc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            name='abc', marker=self._image.id
        )

    def test_image_list_status_option(self):
        arglist = [
            '--status', 'active',
        ]
        verifylist = [
            ('status', 'active'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            status='active', marker=self._image.id
        )

    def test_image_list_tag_option(self):
        arglist = [
            '--tag', 'abc',
        ]
        verifylist = [
            ('tag', 'abc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.api_mock.image_list.assert_called_with(
            tag='abc', marker=self._image.id
        )


class TestListImageProjects(TestImage):

    project = identity_fakes.FakeProject.create_one_project()
    _image = image_fakes.FakeImage.create_one_image()
    member = image_fakes.FakeImage.create_one_image_member(
        attrs={'image_id': _image.id,
               'member_id': project.id}
    )

    columns = (
        "Image ID",
        "Member ID",
        "Status"
    )

    datalist = ((
        _image.id,
        member.member_id,
        member.status,
    ))

    def setUp(self):
        super(TestListImageProjects, self).setUp()

        self.images_mock.get.return_value = self._image
        self.image_members_mock.list.return_value = self.datalist

        self.cmd = image.ListImageProjects(self.app, None)

    def test_image_member_list(self):
        arglist = [
            self._image.id
        ]
        verifylist = [
            ('image', self._image.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.image_members_mock.list.assert_called_with(self._image.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(len(self.datalist), len(tuple(data)))


class TestRemoveProjectImage(TestImage):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestRemoveProjectImage, self).setUp()

        self._image = image_fakes.FakeImage.create_one_image()
        # This is the return value for utils.find_resource()
        self.images_mock.get.return_value = self._image

        self.project_mock.get.return_value = self.project
        self.domain_mock.get.return_value = self.domain
        self.image_members_mock.delete.return_value = None
        # Get the command object to test
        self.cmd = image.RemoveProjectImage(self.app, None)

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

        self.image_members_mock.delete.assert_called_with(
            self._image.id,
            self.project.id,
        )
        self.assertIsNone(result)

    def test_remove_project_image_with_options(self):
        arglist = [
            self._image.id,
            self.project.id,
            '--project-domain', self.domain.id,
        ]
        verifylist = [
            ('image', self._image.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.image_members_mock.delete.assert_called_with(
            self._image.id,
            self.project.id,
        )
        self.assertIsNone(result)


class TestImageSet(TestImage):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestImageSet, self).setUp()
        # Set up the schema
        self.model = warlock.model_factory(
            image_fakes.IMAGE_schema,
            schemas.SchemaBasedModel,
        )

        self.project_mock.get.return_value = self.project

        self.domain_mock.get.return_value = self.domain

        self.images_mock.get.return_value = self.model(**image_fakes.IMAGE)
        self.images_mock.update.return_value = self.model(**image_fakes.IMAGE)

        self.app.client_manager.auth_ref = mock.Mock(
            project_id=self.project.id,
        )

        # Get the command object to test
        self.cmd = image.SetImage(self.app, None)

    def test_image_set_no_options(self):
        arglist = [
            image_fakes.image_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

        self.image_members_mock.update.assert_not_called()

    def test_image_set_membership_option_accept(self):
        membership = image_fakes.FakeImage.create_one_image_member(
            attrs={'image_id': image_fakes.image_id,
                   'member_id': self.project.id}
        )
        self.image_members_mock.update.return_value = membership

        arglist = [
            '--accept',
            image_fakes.image_id,
        ]
        verifylist = [
            ('accept', True),
            ('reject', False),
            ('pending', False),
            ('image', image_fakes.image_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_members_mock.update.assert_called_once_with(
            image_fakes.image_id,
            self.app.client_manager.auth_ref.project_id,
            'accepted',
        )

        # Assert that the 'update image" route is also called, in addition to
        # the 'update membership' route.
        self.images_mock.update.assert_called_with(image_fakes.image_id)

    def test_image_set_membership_option_reject(self):
        membership = image_fakes.FakeImage.create_one_image_member(
            attrs={'image_id': image_fakes.image_id,
                   'member_id': self.project.id}
        )
        self.image_members_mock.update.return_value = membership

        arglist = [
            '--reject',
            image_fakes.image_id,
        ]
        verifylist = [
            ('accept', False),
            ('reject', True),
            ('pending', False),
            ('image', image_fakes.image_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_members_mock.update.assert_called_once_with(
            image_fakes.image_id,
            self.app.client_manager.auth_ref.project_id,
            'rejected',
        )

        # Assert that the 'update image" route is also called, in addition to
        # the 'update membership' route.
        self.images_mock.update.assert_called_with(image_fakes.image_id)

    def test_image_set_membership_option_pending(self):
        membership = image_fakes.FakeImage.create_one_image_member(
            attrs={'image_id': image_fakes.image_id,
                   'member_id': self.project.id}
        )
        self.image_members_mock.update.return_value = membership

        arglist = [
            '--pending',
            image_fakes.image_id,
        ]
        verifylist = [
            ('accept', False),
            ('reject', False),
            ('pending', True),
            ('image', image_fakes.image_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_members_mock.update.assert_called_once_with(
            image_fakes.image_id,
            self.app.client_manager.auth_ref.project_id,
            'pending',
        )

        # Assert that the 'update image" route is also called, in addition to
        # the 'update membership' route.
        self.images_mock.update.assert_called_with(image_fakes.image_id)

    def test_image_set_options(self):
        arglist = [
            '--name', 'new-name',
            '--min-disk', '2',
            '--min-ram', '4',
            '--container-format', 'ovf',
            '--disk-format', 'vmdk',
            '--project', self.project.name,
            '--project-domain', self.domain.id,
            image_fakes.image_id,
        ]
        verifylist = [
            ('name', 'new-name'),
            ('min_disk', 2),
            ('min_ram', 4),
            ('container_format', 'ovf'),
            ('disk_format', 'vmdk'),
            ('project', self.project.name),
            ('project_domain', self.domain.id),
            ('image', image_fakes.image_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': 'new-name',
            'owner': self.project.id,
            'min_disk': 2,
            'min_ram': 4,
            'container_format': 'ovf',
            'disk_format': 'vmdk',
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id, **kwargs)
        self.assertIsNone(result)

    def test_image_set_with_unexist_project(self):
        self.project_mock.get.side_effect = exceptions.NotFound(None)
        self.project_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--project', 'unexist_owner',
            image_fakes.image_id,
        ]
        verifylist = [
            ('project', 'unexist_owner'),
            ('image', image_fakes.image_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)

    def test_image_set_bools1(self):
        arglist = [
            '--protected',
            '--private',
            image_fakes.image_name,
        ]
        verifylist = [
            ('protected', True),
            ('unprotected', False),
            ('public', False),
            ('private', True),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'protected': True,
            'visibility': 'private',
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_bools2(self):
        arglist = [
            '--unprotected',
            '--public',
            image_fakes.image_name,
        ]
        verifylist = [
            ('protected', False),
            ('unprotected', True),
            ('public', True),
            ('private', False),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'protected': False,
            'visibility': 'public',
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_properties(self):
        arglist = [
            '--property', 'Alpha=1',
            '--property', 'Beta=2',
            image_fakes.image_name,
        ]
        verifylist = [
            ('properties', {'Alpha': '1', 'Beta': '2'}),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'Alpha': '1',
            'Beta': '2',
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_fake_properties(self):
        arglist = [
            '--architecture', 'z80',
            '--instance-id', '12345',
            '--kernel-id', '67890',
            '--os-distro', 'cpm',
            '--os-version', '2.2H',
            '--ramdisk-id', 'xyzpdq',
            image_fakes.image_name,
        ]
        verifylist = [
            ('architecture', 'z80'),
            ('instance_id', '12345'),
            ('kernel_id', '67890'),
            ('os_distro', 'cpm'),
            ('os_version', '2.2H'),
            ('ramdisk_id', 'xyzpdq'),
            ('image', image_fakes.image_name),
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
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_tag(self):
        arglist = [
            '--tag', 'test-tag',
            image_fakes.image_name,
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['test-tag'],
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_activate(self):
        arglist = [
            '--tag', 'test-tag',
            '--activate',
            image_fakes.image_name,
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['test-tag'],
        }

        self.images_mock.reactivate.assert_called_with(
            image_fakes.image_id,
        )
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_deactivate(self):
        arglist = [
            '--tag', 'test-tag',
            '--deactivate',
            image_fakes.image_name,
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['test-tag'],
        }

        self.images_mock.deactivate.assert_called_with(
            image_fakes.image_id,
        )
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_image_set_tag_merge(self):
        old_image = copy.copy(image_fakes.IMAGE)
        old_image['tags'] = ['old1', 'new2']
        self.images_mock.get.return_value = self.model(**old_image)
        arglist = [
            '--tag', 'test-tag',
            image_fakes.image_name,
        ]
        verifylist = [
            ('tags', ['test-tag']),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['old1', 'new2', 'test-tag'],
        }
        # ImageManager.update(image, **kwargs)
        a, k = self.images_mock.update.call_args
        self.assertEqual(image_fakes.image_id, a[0])
        self.assertIn('tags', k)
        self.assertEqual(set(kwargs['tags']), set(k['tags']))
        self.assertIsNone(result)

    def test_image_set_tag_merge_dupe(self):
        old_image = copy.copy(image_fakes.IMAGE)
        old_image['tags'] = ['old1', 'new2']
        self.images_mock.get.return_value = self.model(**old_image)
        arglist = [
            '--tag', 'old1',
            image_fakes.image_name,
        ]
        verifylist = [
            ('tags', ['old1']),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'tags': ['new2', 'old1'],
        }
        # ImageManager.update(image, **kwargs)
        a, k = self.images_mock.update.call_args
        self.assertEqual(image_fakes.image_id, a[0])
        self.assertIn('tags', k)
        self.assertEqual(set(kwargs['tags']), set(k['tags']))
        self.assertIsNone(result)

    def test_image_set_dead_options(self):

        arglist = [
            '--visibility', '1-mile',
            image_fakes.image_name,
        ]
        verifylist = [
            ('visibility', '1-mile'),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)

    def test_image_set_numeric_options_to_zero(self):
        arglist = [
            '--min-disk', '0',
            '--min-ram', '0',
            image_fakes.image_name,
        ]
        verifylist = [
            ('min_disk', 0),
            ('min_ram', 0),
            ('image', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'min_disk': 0,
            'min_ram': 0,
        }
        # ImageManager.update(image, **kwargs)
        self.images_mock.update.assert_called_with(
            image_fakes.image_id,
            **kwargs
        )
        self.assertIsNone(result)


class TestImageShow(TestImage):

    new_image = image_fakes.FakeImage.create_one_image(
        attrs={'size': 1000})

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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.images_mock.get.assert_called_with(
            image_fakes.image_id,
        )

        self.assertEqual(image_fakes.IMAGE_columns, columns)
        self.assertItemEqual(image_fakes.IMAGE_SHOW_data, data)

    def test_image_show_human_readable(self):
        self.images_mock.get.return_value = self.new_image
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
        self.images_mock.get.assert_called_with(
            self.new_image.id,
        )

        size_index = columns.index('size')
        self.assertEqual(data[size_index], '1K')


class TestImageUnset(TestImage):

    attrs = {}
    attrs['tags'] = ['test']
    attrs['prop'] = 'test'
    image = image_fakes.FakeImage.create_one_image(attrs)

    def setUp(self):
        super(TestImageUnset, self).setUp()

        # Set up the schema
        self.model = warlock.model_factory(
            image_fakes.IMAGE_schema,
            schemas.SchemaBasedModel,
        )

        self.images_mock.get.return_value = self.image
        self.image_tags_mock.delete.return_value = self.image

        # Get the command object to test
        self.cmd = image.UnsetImage(self.app, None)

    def test_image_unset_no_options(self):
        arglist = [
            image_fakes.image_id,
        ]
        verifylist = [
            ('image', image_fakes.image_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_image_unset_tag_option(self):

        arglist = [
            '--tag', 'test',
            self.image.id,
        ]

        verifylist = [
            ('tags', ['test']),
            ('image', self.image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.image_tags_mock.delete.assert_called_with(
            self.image.id, 'test'
        )
        self.assertIsNone(result)

    def test_image_unset_property_option(self):

        arglist = [
            '--property', 'prop',
            self.image.id,
        ]

        verifylist = [
            ('properties', ['prop']),
            ('image', self.image.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        kwargs = {}
        self.images_mock.update.assert_called_with(
            self.image.id,
            parsed_args.properties,
            **kwargs)

        self.assertIsNone(result)

    def test_image_unset_mixed_option(self):

        arglist = [
            '--tag', 'test',
            '--property', 'prop',
            self.image.id,
        ]

        verifylist = [
            ('tags', ['test']),
            ('properties', ['prop']),
            ('image', self.image.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        kwargs = {}
        self.images_mock.update.assert_called_with(
            self.image.id,
            parsed_args.properties,
            **kwargs)

        self.image_tags_mock.delete.assert_called_with(
            self.image.id, 'test'
        )
        self.assertIsNone(result)


class TestImageSave(TestImage):

    image = image_fakes.FakeImage.create_one_image({})

    def setUp(self):
        super(TestImageSave, self).setUp()

        # Generate a request id
        self.resp = mock.MagicMock()
        self.resp.headers['x-openstack-request-id'] = 'req_id'

        # Get the command object to test
        self.cmd = image.SaveImage(self.app, None)

    def test_save_data(self):
        req_id_proxy = glanceclient_utils.RequestIdProxy(
            ['some_data', self.resp]
        )
        self.images_mock.data.return_value = req_id_proxy

        arglist = ['--file', '/path/to/file', self.image.id]

        verifylist = [
            ('file', '/path/to/file'),
            ('image', self.image.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch('glanceclient.common.utils.save_image') as mocked_save:
            self.cmd.take_action(parsed_args)
            mocked_save.assert_called_once_with(req_id_proxy, '/path/to/file')

    def test_save_no_data(self):
        req_id_proxy = glanceclient_utils.RequestIdProxy(
            [None, self.resp]
        )
        self.images_mock.data.return_value = req_id_proxy

        arglist = ['--file', '/path/to/file', self.image.id]

        verifylist = [
            ('file', '/path/to/file'),
            ('image', self.image.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Raise SystemExit if no data was provided.
        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)
