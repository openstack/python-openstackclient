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

from openstackclient.image.v1 import image
from openstackclient.tests import fakes
from openstackclient.tests.image.v1 import fakes as image_fakes


class TestImage(image_fakes.TestImagev1):

    def setUp(self):
        super(TestImage, self).setUp()

        # Get a shortcut to the ServerManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()


class TestImageCreate(TestImage):

    def setUp(self):
        super(TestImageCreate, self).setUp()
        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.cmd = image.CreateImage(self.app, None)

    def test_create_volume(self):
        arglist = [
            '--volume', 'volly',
            image_fakes.image_name,
        ]
        verifylist = [
            ('volume', 'volly'),
            ('name', image_fakes.image_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.volume = mock.Mock()
        self.app.client_manager.volume.volumes = mock.Mock()
        volumes = self.app.client_manager.volume.volumes
        volumes.upload_to_image = mock.Mock()
        response = {"id": 'volume_id',
                    "updated_at": 'updated_at',
                    "status": 'uploading',
                    "display_description": 'desc',
                    "size": 'size',
                    "volume_type": 'volume_type',
                    "image_id": 'image1',
                    "container_format": parsed_args.container_format,
                    "disk_format": parsed_args.disk_format,
                    "image_name": parsed_args.name}
        full_response = {"os-volume_upload_image": response}
        volumes.upload_to_image.return_value = (201, full_response)
        volume_resource = fakes.FakeResource(
            None,
            copy.deepcopy({'id': 'vol1', 'name': 'volly'}),
            loaded=True,
        )
        volumes.get.return_value = volume_resource
        results = self.cmd.take_action(parsed_args)
        volumes.upload_to_image.assert_called_with(
            volume_resource,
            False,
            image_fakes.image_name,
            'bare',
            'raw',
        )
        expects = [('container_format',
                    'disk_format',
                    'display_description',
                    'id',
                    'image_id',
                    'image_name',
                    'size',
                    'status',
                    'updated_at',
                    'volume_type'),
                   ('bare',
                    'raw',
                    'desc',
                    'volume_id',
                    'image1',
                    'graven',
                    'size',
                    'uploading',
                    'updated_at',
                    'volume_type')]
        for expected, result in zip(expects, results):
            self.assertEqual(expected, result)


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
            ('image', image_fakes.image_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.images_mock.delete.assert_called_with(
            image_fakes.image_id,
        )
