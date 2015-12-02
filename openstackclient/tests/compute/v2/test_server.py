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

from mock import call
from openstackclient.common import exceptions
from openstackclient.common import utils as common_utils
from openstackclient.compute.v2 import server
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.image.v2 import fakes as image_fakes
from openstackclient.tests import utils
from openstackclient.tests.volume.v2 import fakes as volume_fakes


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

        # Get a shortcut to the VolumeManager Mock
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()

        # Set object attributes to be tested. Could be overwriten in subclass.
        self.attrs = {}

        # Set object methods to be tested. Could be overwriten in subclass.
        self.methods = {}

    def setup_servers_mock(self, count):
        servers = compute_fakes.FakeServer.create_servers(attrs=self.attrs,
                                                          methods=self.methods,
                                                          count=count)

        # This is the return value for utils.find_resource()
        self.servers_mock.get = compute_fakes.FakeServer.get_servers(servers,
                                                                     0)
        return servers

    def run_method_with_servers(self, method_name, server_count):
        servers = self.setup_servers_mock(server_count)

        arglist = []
        verifylist = []

        for s in servers:
            arglist.append(s.id)
        verifylist = [
            ('server', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        for s in servers:
            method = getattr(s, method_name)
            method.assert_called_with()


class TestServerCreate(TestServer):

    def setUp(self):
        super(TestServerCreate, self).setUp()

        attrs = {
            'networks': {},
        }
        self.new_server = compute_fakes.FakeServer.create_one_server(
            attrs=attrs)

        # This is the return value for utils.find_resource().
        # This is for testing --wait option.
        self.servers_mock.get.return_value = self.new_server

        self.servers_mock.create.return_value = self.new_server

        self.image = fakes.FakeResource(
            None,
            copy.deepcopy(image_fakes.IMAGE),
            loaded=True,
        )
        self.cimages_mock.get.return_value = self.image

        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        self.flavors_mock.get.return_value = self.flavor

        self.volume = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.VOLUME),
            loaded=True,
        )
        self.volumes_mock.get.return_value = self.volume

        # Get the command object to test
        self.cmd = server.CreateServer(self.app, None)

    def test_server_create_no_options(self):
        arglist = [
            self.new_server.name,
        ]
        verifylist = [
            ('server_name', self.new_server.name),
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
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
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
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = (
            'addresses',
            'flavor',
            'id',
            'name',
            'networks',
            'properties',
        )
        self.assertEqual(collist, columns)
        datalist = (
            '',
            self.flavor.name + ' ()',
            self.new_server.id,
            self.new_server.name,
            self.new_server.networks,
            '',
        )
        self.assertEqual(datalist, data)

    def test_server_create_with_network(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'net-id=net1',
            '--nic', 'port-id=port1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nic', ['net-id=net1', 'port-id=port1']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
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
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = (
            'addresses',
            'flavor',
            'id',
            'name',
            'networks',
            'properties',
        )
        self.assertEqual(collist, columns)
        datalist = (
            '',
            self.flavor.name + ' ()',
            self.new_server.id,
            self.new_server.name,
            self.new_server.networks,
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
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('user_data', 'userdata.sh'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
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
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = (
            'addresses',
            'flavor',
            'id',
            'name',
            'networks',
            'properties',
        )
        self.assertEqual(collist, columns)
        datalist = (
            '',
            self.flavor.name + ' ()',
            self.new_server.id,
            self.new_server.name,
            self.new_server.networks,
            '',
        )
        self.assertEqual(datalist, data)

    def test_server_create_with_block_device_mapping(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', compute_fakes.block_device_mapping,
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [compute_fakes.block_device_mapping]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        real_volume_mapping = (
            (compute_fakes.block_device_mapping.split('=', 1)[1]).replace(
                volume_fakes.volume_name,
                volume_fakes.volume_id))

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
            block_device_mapping={
                'vda': real_volume_mapping
            },
            nics=[],
            scheduler_hints={},
            config_drive=None,
        )
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        collist = (
            'addresses',
            'flavor',
            'id',
            'name',
            'networks',
            'properties',
        )
        self.assertEqual(collist, columns)
        datalist = (
            '',
            self.flavor.name + ' ()',
            self.new_server.id,
            self.new_server.name,
            self.new_server.networks,
            '',
        )
        self.assertEqual(datalist, data)


class TestServerDelete(TestServer):

    def setUp(self):
        super(TestServerDelete, self).setUp()

        self.servers_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = server.DeleteServer(self.app, None)

    def test_server_delete_no_options(self):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id,
        ]
        verifylist = [
            ('server', [servers[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(
            servers[0].id,
        )

    def test_server_delete_multi_servers(self):
        servers = self.setup_servers_mock(count=3)

        arglist = []
        verifylist = []

        for s in servers:
            arglist.append(s.id)
        verifylist = [
            ('server', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        calls = []
        for s in servers:
            calls.append(call(s.id))
        self.servers_mock.delete.assert_has_calls(calls)

    @mock.patch.object(common_utils, 'wait_for_delete', return_value=True)
    def test_server_delete_wait_ok(self, mock_wait_for_delete):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id, '--wait'
        ]
        verifylist = [
            ('server', [servers[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(
            servers[0].id,
        )

        mock_wait_for_delete.assert_called_once_with(
            self.servers_mock,
            servers[0].id,
            callback=server._show_progress
        )

    @mock.patch.object(common_utils, 'wait_for_delete', return_value=False)
    def test_server_delete_wait_fails(self, mock_wait_for_delete):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id, '--wait'
        ]
        verifylist = [
            ('server', [servers[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        self.servers_mock.delete.assert_called_with(
            servers[0].id,
        )

        mock_wait_for_delete.assert_called_once_with(
            self.servers_mock,
            servers[0].id,
            callback=server._show_progress
        )


class TestServerImageCreate(TestServer):

    def setUp(self):
        super(TestServerImageCreate, self).setUp()

        self.server = compute_fakes.FakeServer.create_one_server()

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

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
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            self.servers_mock.get.return_value,
            self.server.name,
        )

        collist = ('id', 'name', 'owner', 'protected', 'tags', 'visibility')
        self.assertEqual(collist, columns)
        datalist = (
            image_fakes.image_id,
            image_fakes.image_name,
            image_fakes.image_owner,
            image_fakes.image_protected,
            image_fakes.image_tags,
            image_fakes.image_visibility,
        )
        self.assertEqual(datalist, data)

    def test_server_image_create_name(self):
        arglist = [
            '--name', 'img-nam',
            self.server.id,
        ]
        verifylist = [
            ('name', 'img-nam'),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ServerManager.create_image(server, image_name, metadata=)
        self.servers_mock.create_image.assert_called_with(
            self.servers_mock.get.return_value,
            'img-nam',
        )

        collist = ('id', 'name', 'owner', 'protected', 'tags', 'visibility')
        self.assertEqual(collist, columns)
        datalist = (
            image_fakes.image_id,
            image_fakes.image_name,
            image_fakes.image_owner,
            image_fakes.image_protected,
            image_fakes.image_tags,
            image_fakes.image_visibility,
        )
        self.assertEqual(datalist, data)


class TestServerList(TestServer):

    # Columns to be listed up.
    columns = (
        'ID',
        'Name',
        'Status',
        'Networks',
    )

    # Data returned by corresponding Nova API. The elements in this list are
    # tuples filled with server attributes.
    data = []

    # Default search options, in the case of no commandline option specified.
    search_opts = {
        'reservation_id': None,
        'ip': None,
        'ip6': None,
        'name': None,
        'instance_name': None,
        'status': None,
        'flavor': None,
        'image': None,
        'host': None,
        'tenant_id': None,
        'all_tenants': False,
        'user_id': None,
    }

    # Default params of the core function of the command in the case of no
    # commandline option specified.
    kwargs = {
        'search_opts': search_opts,
        'marker': None,
        'limit': None,
    }

    def setUp(self):
        super(TestServerList, self).setUp()

        # The fake servers' attributes.
        self.attrs = {
            'status': 'ACTIVE',
            'networks': {
                u'public': [u'10.20.30.40', u'2001:db8::5']
            },
        }

        # The servers to be listed.
        self.servers = self.setup_servers_mock(3)

        self.servers_mock.list.return_value = self.servers

        # Get the command object to test
        self.cmd = server.ListServer(self.app, None)

        # Prepare data returned by fake Nova API.
        for s in self.servers:
            self.data.append((
                s.id,
                s.name,
                s.status,
                u'public=10.20.30.40, 2001:db8::5',
            ))

    def test_server_list_no_option(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestServerLock(TestServer):

    def setUp(self):
        super(TestServerLock, self).setUp()

        # Get the command object to test
        self.cmd = server.LockServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'lock': None,
        }

    def test_server_lock_one_server(self):
        self.run_method_with_servers('lock', 1)

    def test_server_lock_multi_servers(self):
        self.run_method_with_servers('lock', 3)


class TestServerPause(TestServer):

    def setUp(self):
        super(TestServerPause, self).setUp()

        # Get the command object to test
        self.cmd = server.PauseServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'pause': None,
        }

    def test_server_pause_one_server(self):
        self.run_method_with_servers('pause', 1)

    def test_server_pause_multi_servers(self):
        self.run_method_with_servers('pause', 3)


class TestServerResize(TestServer):

    def setUp(self):
        super(TestServerResize, self).setUp()

        self.server = compute_fakes.FakeServer.create_one_server()

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.resize.return_value = None
        self.servers_mock.confirm_resize.return_value = None
        self.servers_mock.revert_resize.return_value = None

        # This is the return value for utils.find_resource()
        self.flavors_get_return_value = \
            compute_fakes.FakeFlavor.create_one_flavor()
        self.flavors_mock.get.return_value = self.flavors_get_return_value

        # Get the command object to test
        self.cmd = server.ResizeServer(self.app, None)

    def test_server_resize_no_options(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('confirm', False),
            ('revert', False),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            self.server.id,
        )

        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)

    def test_server_resize(self):
        arglist = [
            '--flavor', self.flavors_get_return_value.id,
            self.server.id,
        ]
        verifylist = [
            ('flavor', self.flavors_get_return_value.id),
            ('confirm', False),
            ('revert', False),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            self.server.id,
        )
        self.flavors_mock.get.assert_called_with(
            self.flavors_get_return_value.id,
        )

        self.servers_mock.resize.assert_called_with(
            self.server,
            self.flavors_get_return_value,
        )
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)

    def test_server_resize_confirm(self):
        arglist = [
            '--confirm',
            self.server.id,
        ]
        verifylist = [
            ('confirm', True),
            ('revert', False),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            self.server.id,
        )

        self.assertNotCalled(self.servers_mock.resize)
        self.servers_mock.confirm_resize.assert_called_with(
            self.server,
        )
        self.assertNotCalled(self.servers_mock.revert_resize)

    def test_server_resize_revert(self):
        arglist = [
            '--revert',
            self.server.id,
        ]
        verifylist = [
            ('confirm', False),
            ('revert', True),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            self.server.id,
        )

        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.servers_mock.revert_resize.assert_called_with(
            self.server,
        )


class TestServerResume(TestServer):

    def setUp(self):
        super(TestServerResume, self).setUp()

        # Get the command object to test
        self.cmd = server.ResumeServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'resume': None,
        }

    def test_server_resume_one_server(self):
        self.run_method_with_servers('resume', 1)

    def test_server_resume_multi_servers(self):
        self.run_method_with_servers('resume', 3)


class TestServerShelve(TestServer):

    def setUp(self):
        super(TestServerShelve, self).setUp()

        # Get the command object to test
        self.cmd = server.ShelveServer(self.app, None)

        # Set shelve method to be tested.
        self.methods = {
            'shelve': None,
        }

    def test_shelve_one_server(self):
        self.run_method_with_servers('shelve', 1)

    def test_shelve_multi_servers(self):
        self.run_method_with_servers('shelve', 3)


class TestServerStart(TestServer):

    def setUp(self):
        super(TestServerStart, self).setUp()

        # Get the command object to test
        self.cmd = server.StartServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'start': None,
        }

    def test_server_start_one_server(self):
        self.run_method_with_servers('start', 1)

    def test_server_start_multi_servers(self):
        self.run_method_with_servers('start', 3)


class TestServerStop(TestServer):

    def setUp(self):
        super(TestServerStop, self).setUp()

        # Get the command object to test
        self.cmd = server.StopServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'stop': None,
        }

    def test_server_stop_one_server(self):
        self.run_method_with_servers('stop', 1)

    def test_server_stop_multi_servers(self):
        self.run_method_with_servers('stop', 3)


class TestServerSuspend(TestServer):

    def setUp(self):
        super(TestServerSuspend, self).setUp()

        # Get the command object to test
        self.cmd = server.SuspendServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'suspend': None,
        }

    def test_server_suspend_one_server(self):
        self.run_method_with_servers('suspend', 1)

    def test_server_suspend_multi_servers(self):
        self.run_method_with_servers('suspend', 3)


class TestServerUnlock(TestServer):

    def setUp(self):
        super(TestServerUnlock, self).setUp()

        # Get the command object to test
        self.cmd = server.UnlockServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'unlock': None,
        }

    def test_server_unlock_one_server(self):
        self.run_method_with_servers('unlock', 1)

    def test_server_unlock_multi_servers(self):
        self.run_method_with_servers('unlock', 3)


class TestServerUnpause(TestServer):

    def setUp(self):
        super(TestServerUnpause, self).setUp()

        # Get the command object to test
        self.cmd = server.UnpauseServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'unpause': None,
        }

    def test_server_unpause_one_server(self):
        self.run_method_with_servers('unpause', 1)

    def test_server_unpause_multi_servers(self):
        self.run_method_with_servers('unpause', 3)


class TestServerUnshelve(TestServer):

    def setUp(self):
        super(TestServerUnshelve, self).setUp()

        # Get the command object to test
        self.cmd = server.UnshelveServer(self.app, None)

        # Set unshelve method to be tested.
        self.methods = {
            'unshelve': None,
        }

    def test_unshelve_one_server(self):
        self.run_method_with_servers('unshelve', 1)

    def test_unshelve_multi_servers(self):
        self.run_method_with_servers('unshelve', 3)


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
