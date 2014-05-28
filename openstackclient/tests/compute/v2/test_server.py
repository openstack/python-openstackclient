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

from openstackclient.compute.v2 import server
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.image.v2 import fakes as image_fakes


class TestServer(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServer, self).setUp()

        # Get a shortcut to the ServerManager Mock
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()

        # Get a shortcut to the ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()


class TestServerDelete(TestServer):

    def setUp(self):
        super(TestServerDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVER),
            loaded=True,
        )
        self.servers_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = server.DeleteServer(self.app, None)

    def test_server_delete_no_options(self):
        arglist = [
            compute_fakes.server_id,
        ]
        verifylist = [
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(
            compute_fakes.server_id,
        )


class TestServerImageCreate(TestServer):

    def setUp(self):
        super(TestServerImageCreate, self).setUp()

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVER),
            loaded=True,
        )

        self.servers_mock.create_image.return_value = image_fakes.image_id

        self.images_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = server.CreateServerImage(self.app, None)

    def test_server_image_create_no_options(self):
        arglist = [
            compute_fakes.server_id,
        ]
        verifylist = [
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            self.servers_mock.get.return_value,
            compute_fakes.server_name,
        )

        collist = ('id', 'is_public', 'name', 'owner')
        self.assertEqual(columns, collist)
        datalist = (
            image_fakes.image_id,
            False,
            image_fakes.image_name,
            image_fakes.image_owner,
        )
        self.assertEqual(data, datalist)

    def test_server_image_create_name(self):
        arglist = [
            '--name', 'img-nam',
            compute_fakes.server_id,
        ]
        verifylist = [
            ('name', 'img-nam'),
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            self.servers_mock.get.return_value,
            'img-nam',
        )

        collist = ('id', 'is_public', 'name', 'owner')
        self.assertEqual(columns, collist)
        datalist = (
            image_fakes.image_id,
            False,
            image_fakes.image_name,
            image_fakes.image_owner,
        )
        self.assertEqual(data, datalist)
