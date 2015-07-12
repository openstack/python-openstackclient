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
import testtools

from openstackclient.common import exceptions
from openstackclient.common import utils as common_utils
from openstackclient.compute.v2 import server
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.image.v2 import fakes as image_fakes
from openstackclient.tests import utils


class TestServer(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServer, self).setUp()

        # Get a shortcut to the ServerManager Mock
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()

        # Get a shortcut to the ImageManager Mock
        self.cimages_mock = self.app.client_manager.compute.images
        self.cimages_mock.reset_mock()

        # Get a shortcut to the FlavorManager Mock
        self.flavors_mock = self.app.client_manager.compute.flavors
        self.flavors_mock.reset_mock()

        # Get a shortcut to the ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()


class TestServerCreate(TestServer):

    def setUp(self):
        super(TestServerCreate, self).setUp()

        self.servers_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVER),
            loaded=True,
        )
        new_server = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVER),
            loaded=True,
        )
        new_server.__dict__['networks'] = {}
        self.servers_mock.get.return_value = new_server

        self.image = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.cimages_mock.get.return_value = self.image

        self.flavor = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.FLAVOR),
            loaded=True,
        )
        self.flavors_mock.get.return_value = self.flavor

        # Get the command object to test
        self.cmd = server.CreateServer(self.app, None)

    def test_server_create_no_options(self):
        arglist = [
            compute_fakes.server_id,
        ]
        verifylist = [
            ('server_name', compute_fakes.server_id),
        ]
        try:
            # Missing required args should bail here
            self.check_parser(self.cmd, arglist, verifylist)
        except utils.ParserException:
            pass

    def test_server_create_minimal(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            compute_fakes.server_id,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('config_drive', False),
            ('server_name', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = dict(
            meta=None,
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[],
            userdata=None,
            key_name=None,
            availability_zone=None,
            block_device_mapping={},
            nics=[],
            scheduler_hints={},
            config_drive=None,
        )
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            compute_fakes.server_id,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = ('addresses', 'flavor', 'id', 'name', 'properties')
        self.assertEqual(collist, columns)
        datalist = (
            '',
            'Large ()',
            compute_fakes.server_id,
            compute_fakes.server_name,
            '',
        )
        self.assertEqual(datalist, data)

    def test_server_create_with_network(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'net-id=net1',
            '--nic', 'port-id=port1',
            compute_fakes.server_id,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nic', ['net-id=net1', 'port-id=port1']),
            ('config_drive', False),
            ('server_name', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        get_endpoints = mock.Mock()
        get_endpoints.return_value = {'network': []}
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.service_catalog = mock.Mock()
        self.app.client_manager.auth_ref.service_catalog.get_endpoints = (
            get_endpoints)

        list_networks = mock.Mock()
        list_ports = mock.Mock()
        self.app.client_manager.network.list_networks = list_networks
        self.app.client_manager.network.list_ports = list_ports
        list_networks.return_value = {'networks': [{'id': 'net1_uuid'}]}
        list_ports.return_value = {'ports': [{'id': 'port1_uuid'}]}

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = dict(
            meta=None,
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[],
            userdata=None,
            key_name=None,
            availability_zone=None,
            block_device_mapping={},
            nics=[{'net-id': 'net1_uuid',
                   'v4-fixed-ip': '',
                   'v6-fixed-ip': '',
                   'port-id': ''},
                  {'net-id': '',
                   'v4-fixed-ip': '',
                   'v6-fixed-ip': '',
                   'port-id': 'port1_uuid'}],
            scheduler_hints={},
            config_drive=None,
        )
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            compute_fakes.server_id,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = ('addresses', 'flavor', 'id', 'name', 'properties')
        self.assertEqual(collist, columns)
        datalist = (
            '',
            'Large ()',
            compute_fakes.server_id,
            compute_fakes.server_name,
            '',
        )
        self.assertEqual(datalist, data)

    @mock.patch('openstackclient.compute.v2.server.io.open')
    def test_server_create_userdata(self, mock_open):
        mock_file = mock.MagicMock(name='File')
        mock_open.return_value = mock_file
        mock_open.read.return_value = '#!/bin/sh'

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--user-data', 'userdata.sh',
            compute_fakes.server_id,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('user_data', 'userdata.sh'),
            ('config_drive', False),
            ('server_name', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Ensure the userdata file is opened
        mock_open.assert_called_with('userdata.sh')

        # Ensure the userdata file is closed
        mock_file.close.assert_called_with()

        # Set expected values
        kwargs = dict(
            meta=None,
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[],
            userdata=mock_file,
            key_name=None,
            availability_zone=None,
            block_device_mapping={},
            nics=[],
            scheduler_hints={},
            config_drive=None,
        )
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            compute_fakes.server_id,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = ('addresses', 'flavor', 'id', 'name', 'properties')
        self.assertEqual(collist, columns)
        datalist = (
            '',
            'Large ()',
            compute_fakes.server_id,
            compute_fakes.server_name,
            '',
        )
        self.assertEqual(datalist, data)


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
            ('servers', [compute_fakes.server_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(
            compute_fakes.server_id,
        )

    @mock.patch.object(common_utils, 'wait_for_delete', return_value=True)
    def test_server_delete_wait_ok(self, mock_wait_for_delete):
        arglist = [
            compute_fakes.server_id, '--wait'
        ]
        verifylist = [
            ('servers', [compute_fakes.server_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(
            compute_fakes.server_id,
        )

        mock_wait_for_delete.assert_called_once_with(
            self.servers_mock,
            compute_fakes.server_id,
            callback=server._show_progress
        )

    @mock.patch.object(common_utils, 'wait_for_delete', return_value=False)
    def test_server_delete_wait_fails(self, mock_wait_for_delete):
        arglist = [
            compute_fakes.server_id, '--wait'
        ]
        verifylist = [
            ('servers', [compute_fakes.server_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        self.servers_mock.delete.assert_called_with(
            compute_fakes.server_id,
        )

        mock_wait_for_delete.assert_called_once_with(
            self.servers_mock,
            compute_fakes.server_id,
            callback=server._show_progress
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

        collist = ('id', 'name', 'owner', 'protected', 'visibility')
        self.assertEqual(collist, columns)
        datalist = (
            image_fakes.image_id,
            image_fakes.image_name,
            image_fakes.image_owner,
            image_fakes.image_protected,
            image_fakes.image_visibility,
        )
        self.assertEqual(datalist, data)

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

        collist = ('id', 'name', 'owner', 'protected', 'visibility')
        self.assertEqual(collist, columns)
        datalist = (
            image_fakes.image_id,
            image_fakes.image_name,
            image_fakes.image_owner,
            image_fakes.image_protected,
            image_fakes.image_visibility,
        )
        self.assertEqual(datalist, data)


class TestServerResize(TestServer):

    def setUp(self):
        super(TestServerResize, self).setUp()

        # This is the return value for utils.find_resource()
        self.servers_get_return_value = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVER),
            loaded=True,
        )
        self.servers_mock.get.return_value = self.servers_get_return_value

        self.servers_mock.resize.return_value = None
        self.servers_mock.confirm_resize.return_value = None
        self.servers_mock.revert_resize.return_value = None

        # This is the return value for utils.find_resource()
        self.flavors_get_return_value = fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.FLAVOR),
            loaded=True,
        )
        self.flavors_mock.get.return_value = self.flavors_get_return_value

        # Get the command object to test
        self.cmd = server.ResizeServer(self.app, None)

    def test_server_resize_no_options(self):
        arglist = [
            compute_fakes.server_id,
        ]
        verifylist = [
            ('confirm', False),
            ('revert', False),
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            compute_fakes.server_id,
        )

        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)

    def test_server_resize(self):
        arglist = [
            '--flavor', compute_fakes.flavor_id,
            compute_fakes.server_id,
        ]
        verifylist = [
            ('flavor', compute_fakes.flavor_id),
            ('confirm', False),
            ('revert', False),
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            compute_fakes.server_id,
        )
        self.flavors_mock.get.assert_called_with(
            compute_fakes.flavor_id,
        )

        self.servers_mock.resize.assert_called_with(
            self.servers_get_return_value,
            self.flavors_get_return_value,
        )
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)

    def test_server_resize_confirm(self):
        arglist = [
            '--confirm',
            compute_fakes.server_id,
        ]
        verifylist = [
            ('confirm', True),
            ('revert', False),
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            compute_fakes.server_id,
        )

        self.assertNotCalled(self.servers_mock.resize)
        self.servers_mock.confirm_resize.assert_called_with(
            self.servers_get_return_value,
        )
        self.assertNotCalled(self.servers_mock.revert_resize)

    def test_server_resize_revert(self):
        arglist = [
            '--revert',
            compute_fakes.server_id,
        ]
        verifylist = [
            ('confirm', False),
            ('revert', True),
            ('server', compute_fakes.server_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            compute_fakes.server_id,
        )

        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.servers_mock.revert_resize.assert_called_with(
            self.servers_get_return_value,
        )


class TestServerGeneral(testtools.TestCase):
    OLD = {
        'private': [
            {
                'addr': '192.168.0.3',
                'version': 4,
            },
        ]
    }
    NEW = {
        'foo': [
            {
                'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:93:b3:01',
                'version': 4,
                'addr': '10.10.1.2',
                'OS-EXT-IPS:type': 'fixed',
            },
            {
                'OS-EXT-IPS-MAC:mac_addr': 'fa:16:3e:93:b3:02',
                'version': 6,
                'addr': '0:0:0:0:0:ffff:a0a:103',
                'OS-EXT-IPS:type': 'floating',
            },
        ]
    }
    ODD = {'jenkins': ['10.3.3.18', '124.12.125.4']}

    def test_get_ip_address(self):
        self.assertEqual("192.168.0.3",
                         server._get_ip_address(self.OLD, 'private', [4, 6]))
        self.assertEqual("10.10.1.2",
                         server._get_ip_address(self.NEW, 'fixed', [4, 6]))
        self.assertEqual("10.10.1.2",
                         server._get_ip_address(self.NEW, 'private', [4, 6]))
        self.assertEqual("0:0:0:0:0:ffff:a0a:103",
                         server._get_ip_address(self.NEW, 'public', [6]))
        self.assertEqual("0:0:0:0:0:ffff:a0a:103",
                         server._get_ip_address(self.NEW, 'floating', [6]))
        self.assertEqual("124.12.125.4",
                         server._get_ip_address(self.ODD, 'public', [4, 6]))
        self.assertEqual("10.3.3.18",
                         server._get_ip_address(self.ODD, 'private', [4, 6]))
        self.assertRaises(exceptions.CommandError,
                          server._get_ip_address, self.NEW, 'public', [4])
        self.assertRaises(exceptions.CommandError,
                          server._get_ip_address, self.NEW, 'admin', [4])
        self.assertRaises(exceptions.CommandError,
                          server._get_ip_address, self.OLD, 'public', [4, 6])
        self.assertRaises(exceptions.CommandError,
                          server._get_ip_address, self.OLD, 'private', [6])
