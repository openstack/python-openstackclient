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
import mock

from osc_lib import exceptions
from osc_lib import utils as common_utils

from openstackclient.compute.v2 import server_image
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestServerImage(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServerImage, self).setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()

        # Get a shortcut to the image client ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()

        # Set object attributes to be tested. Could be overwritten in subclass.
        self.attrs = {}

        # Set object methods to be tested. Could be overwritten in subclass.
        self.methods = {}

    def setup_servers_mock(self, count):
        servers = compute_fakes.FakeServer.create_servers(
            attrs=self.attrs,
            methods=self.methods,
            count=count,
        )

        # This is the return value for utils.find_resource()
        self.servers_mock.get = compute_fakes.FakeServer.get_servers(
            servers,
            0,
        )
        return servers


class TestServerImageCreate(TestServerImage):

    def image_columns(self, image):
        columnlist = tuple(sorted(image.keys()))
        return columnlist

    def image_data(self, image):
        datalist = (
            image['id'],
            image['name'],
            image['owner'],
            image['protected'],
            'active',
            common_utils.format_list(image.get('tags')),
            image['visibility'],
        )
        return datalist

    def setUp(self):
        super(TestServerImageCreate, self).setUp()

        # Get the command object to test
        self.cmd = server_image.CreateServerImage(self.app, None)

        self.methods = {
            'create_image': None,
        }

    def setup_images_mock(self, count, servers=None):
        if servers:
            images = image_fakes.FakeImage.create_images(
                attrs={
                    'name': servers[0].name,
                    'status': 'active',
                },
                count=count,
            )
        else:
            images = image_fakes.FakeImage.create_images(
                attrs={
                    'status': 'active',
                },
                count=count,
            )

        self.images_mock.get = mock.Mock(side_effect=images)
        self.servers_mock.create_image = mock.Mock(
            return_value=images[0].id,
        )
        return images

    def test_server_image_create_defaults(self):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        arglist = [
            servers[0].id,
        ]
        verifylist = [
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            servers[0].id,
            servers[0].name,
        )

        self.assertEqual(self.image_columns(images[0]), columns)
        self.assertEqual(self.image_data(images[0]), data)

    def test_server_image_create_options(self):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        arglist = [
            '--name', 'img-nam',
            servers[0].id,
        ]
        verifylist = [
            ('name', 'img-nam'),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            servers[0].id,
            'img-nam',
        )

        self.assertEqual(self.image_columns(images[0]), columns)
        self.assertEqual(self.image_data(images[0]), data)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_create_image_wait_fail(self, mock_wait_for_status):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        arglist = [
            '--wait',
            servers[0].id,
        ]
        verifylist = [
            ('wait', True),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            servers[0].id,
            servers[0].name,
        )

        mock_wait_for_status.assert_called_once_with(
            self.images_mock.get,
            images[0].id,
            callback=mock.ANY
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_create_image_wait_ok(self, mock_wait_for_status):
        servers = self.setup_servers_mock(count=1)
        images = self.setup_images_mock(count=1, servers=servers)

        arglist = [
            '--wait',
            servers[0].id,
        ]
        verifylist = [
            ('wait', True),
            ('server', servers[0].id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            servers[0].id,
            servers[0].name,
        )

        mock_wait_for_status.assert_called_once_with(
            self.images_mock.get,
            images[0].id,
            callback=mock.ANY
        )

        self.assertEqual(self.image_columns(images[0]), columns)
        self.assertEqual(self.image_data(images[0]), data)
