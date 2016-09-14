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
import collections
import getpass
import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils as common_utils

from openstackclient.compute.v2 import server
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class TestServer(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServer, self).setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()

        # Get a shortcut to the compute client ImageManager Mock
        self.cimages_mock = self.app.client_manager.compute.images
        self.cimages_mock.reset_mock()

        # Get a shortcut to the compute client FlavorManager Mock
        self.flavors_mock = self.app.client_manager.compute.flavors
        self.flavors_mock.reset_mock()

        # Get a shortcut to the compute client SecurityGroupManager Mock
        self.security_groups_mock = \
            self.app.client_manager.compute.security_groups
        self.security_groups_mock.reset_mock()

        # Get a shortcut to the image client ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()

        # Get a shortcut to the volume client VolumeManager Mock
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()

        # Set object attributes to be tested. Could be overwritten in subclass.
        self.attrs = {}

        # Set object methods to be tested. Could be overwritten in subclass.
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

        result = self.cmd.take_action(parsed_args)

        for s in servers:
            method = getattr(s, method_name)
            method.assert_called_with()
        self.assertIsNone(result)


class TestServerAddFixedIP(TestServer):

    def setUp(self):
        super(TestServerAddFixedIP, self).setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.networks_mock = self.app.client_manager.compute.networks

        # Get the command object to test
        self.cmd = server.AddFixedIP(self.app, None)

        # Set add_fixed_ip method to be tested.
        self.methods = {
            'add_fixed_ip': None,
        }

    def test_server_add_fixed_ip(self):
        servers = self.setup_servers_mock(count=1)
        network = compute_fakes.FakeNetwork.create_one_network()
        self.networks_mock.get.return_value = network

        arglist = [
            servers[0].id,
            network.id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', network.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].add_fixed_ip.assert_called_once_with(
            network.id,
        )
        self.assertIsNone(result)


class TestServerAddFloatingIP(TestServer):

    def setUp(self):
        super(TestServerAddFloatingIP, self).setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.networks_mock = self.app.client_manager.compute.networks

        # Get the command object to test
        self.cmd = server.AddFloatingIP(self.app, None)

        # Set add_floating_ip method to be tested.
        self.methods = {
            'add_floating_ip': None,
        }

    def test_server_add_floating_ip(self):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id,
            '1.2.3.4',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('ip_address', '1.2.3.4'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].add_floating_ip.assert_called_once_with('1.2.3.4')
        self.assertIsNone(result)


class TestServerAddSecurityGroup(TestServer):

    def setUp(self):
        super(TestServerAddSecurityGroup, self).setUp()

        self.security_group = \
            compute_fakes.FakeSecurityGroup.create_one_security_group()
        # This is the return value for utils.find_resource() for security group
        self.security_groups_mock.get.return_value = self.security_group

        attrs = {
            'security_groups': [{'name': self.security_group.id}]
        }
        methods = {
            'add_security_group': None,
        }

        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=attrs,
            methods=methods
        )
        # This is the return value for utils.find_resource() for server
        self.servers_mock.get.return_value = self.server

        # Get the command object to test
        self.cmd = server.AddServerSecurityGroup(self.app, None)

    def test_server_add_security_group(self):
        arglist = [
            self.server.id,
            self.security_group.id
        ]
        verifylist = [
            ('server', self.server.id),
            ('group', self.security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.security_groups_mock.get.assert_called_with(
            self.security_group.id,
        )
        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.add_security_group.assert_called_with(
            self.security_group.id,
        )
        self.assertIsNone(result)


class TestServerCreate(TestServer):

    columns = (
        'OS-EXT-STS:power_state',
        'addresses',
        'flavor',
        'id',
        'image',
        'name',
        'networks',
        'properties',
    )

    def datalist(self):
        datalist = (
            server._format_servers_list_power_state(
                getattr(self.new_server, 'OS-EXT-STS:power_state')),
            '',
            self.flavor.name + ' (' + self.new_server.flavor.get('id') + ')',
            self.new_server.id,
            self.image.name + ' (' + self.new_server.image.get('id') + ')',
            self.new_server.name,
            self.new_server.networks,
            '',
        )
        return datalist

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

        self.image = image_fakes.FakeImage.create_one_image()
        self.cimages_mock.get.return_value = self.image

        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        self.flavors_mock.get.return_value = self.flavor

        self.volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = self.volume
        self.block_device_mapping = 'vda=' + self.volume.name + ':::0'

        # Get the command object to test
        self.cmd = server.CreateServer(self.app, None)

    def test_server_create_no_options(self):
        arglist = [
            self.new_server.name,
        ]
        verifylist = [
            ('server_name', self.new_server.name),
        ]

        self.assertRaises(utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

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

        find_network = mock.Mock()
        find_port = mock.Mock()
        network_client = self.app.client_manager.network
        network_client.find_network = find_network
        network_client.find_port = find_port
        network_resource = mock.Mock()
        network_resource.id = 'net1_uuid'
        port_resource = mock.Mock()
        port_resource.id = 'port1_uuid'
        find_network.return_value = network_resource
        find_port.return_value = port_resource

        # Mock sdk APIs.
        _network = mock.Mock()
        _network.id = 'net1_uuid'
        _port = mock.Mock()
        _port.id = 'port1_uuid'
        find_network = mock.Mock()
        find_port = mock.Mock()
        find_network.return_value = _network
        find_port.return_value = _port
        self.app.client_manager.network.find_network = find_network
        self.app.client_manager.network.find_port = find_port

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    @mock.patch('openstackclient.compute.v2.server.io.open')
    def test_server_create_userdata(self, mock_open):
        mock_file = mock.Mock(name='File')
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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', self.block_device_mapping,
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [self.block_device_mapping]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        real_volume_mapping = (
            (self.block_device_mapping.split('=', 1)[1]).replace(
                self.volume.name,
                self.volume.id))

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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)


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

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(servers[0].id)
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in servers:
            calls.append(call(s.id))
        self.servers_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.delete.assert_called_with(servers[0].id)
        mock_wait_for_delete.assert_called_once_with(
            self.servers_mock,
            servers[0].id,
            callback=server._show_progress
        )
        self.assertIsNone(result)

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

        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        self.servers_mock.delete.assert_called_with(servers[0].id)
        mock_wait_for_delete.assert_called_once_with(
            self.servers_mock,
            servers[0].id,
            callback=server._show_progress
        )


class TestServerDumpCreate(TestServer):

    def setUp(self):
        super(TestServerDumpCreate, self).setUp()

        # Get the command object to test
        self.cmd = server.CreateServerDump(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'trigger_crash_dump': None,
        }

    def test_server_dump_one_server(self):
        self.run_method_with_servers('trigger_crash_dump', 1)

    def test_server_dump_multi_servers(self):
        self.run_method_with_servers('trigger_crash_dump', 3)


class TestServerList(TestServer):

    # Columns to be listed up.
    columns = (
        'ID',
        'Name',
        'Status',
        'Networks',
        'Image Name',
    )
    columns_long = (
        'ID',
        'Name',
        'Status',
        'Task State',
        'Power State',
        'Networks',
        'Image Name',
        'Image ID',
        'Availability Zone',
        'Host',
        'Properties',
    )

    def setUp(self):
        super(TestServerList, self).setUp()

        self.search_opts = {
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
        self.kwargs = {
            'search_opts': self.search_opts,
            'marker': None,
            'limit': None,
        }

        # The fake servers' attributes. Use the original attributes names in
        # nova, not the ones printed by "server list" command.
        self.attrs = {
            'status': 'ACTIVE',
            'OS-EXT-STS:task_state': 'None',
            'OS-EXT-STS:power_state': 0x01,   # Running
            'networks': {
                u'public': [u'10.20.30.40', u'2001:db8::5']
            },
            'OS-EXT-AZ:availability_zone': 'availability-zone-xxx',
            'OS-EXT-SRV-ATTR:host': 'host-name-xxx',
            'Metadata': '',
        }

        # The servers to be listed.
        self.servers = self.setup_servers_mock(3)
        self.servers_mock.list.return_value = self.servers

        self.image = image_fakes.FakeImage.create_one_image()
        self.cimages_mock.get.return_value = self.image

        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        self.flavors_mock.get.return_value = self.flavor

        # Get the command object to test
        self.cmd = server.ListServer(self.app, None)

        # Prepare data returned by fake Nova API.
        self.data = []
        self.data_long = []

        Image = collections.namedtuple('Image', 'id name')
        self.images_mock.list.return_value = [
            Image(id=s.image['id'], name=self.image.name)
            for s in self.servers
        ]

        for s in self.servers:
            self.data.append((
                s.id,
                s.name,
                s.status,
                server._format_servers_list_networks(s.networks),
                self.image.name,
            ))
            self.data_long.append((
                s.id,
                s.name,
                s.status,
                getattr(s, 'OS-EXT-STS:task_state'),
                server._format_servers_list_power_state(
                    getattr(s, 'OS-EXT-STS:power_state')
                ),
                server._format_servers_list_networks(s.networks),
                self.image.name,
                s.image['id'],
                getattr(s, 'OS-EXT-AZ:availability_zone'),
                getattr(s, 'OS-EXT-SRV-ATTR:host'),
                s.Metadata,
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

    def test_server_list_long_option(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(tuple(self.data_long), tuple(data))

    def test_server_list_with_image(self):

        arglist = [
            '--image', self.image.id
        ]
        verifylist = [
            ('image', self.image.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.cimages_mock.get.assert_any_call(self.image.id)

        self.search_opts['image'] = self.image.id
        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_flavor(self):

        arglist = [
            '--flavor', self.flavor.id
        ]
        verifylist = [
            ('flavor', self.flavor.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.flavors_mock.get.assert_called_with(self.flavor.id)

        self.search_opts['flavor'] = self.flavor.id
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


class TestServerRebuild(TestServer):

    def setUp(self):
        super(TestServerRebuild, self).setUp()

        # Return value for utils.find_resource for image
        self.image = image_fakes.FakeImage.create_one_image()
        self.cimages_mock.get.return_value = self.image

        # Fake the rebuilt new server.
        new_server = compute_fakes.FakeServer.create_one_server()

        # Fake the server to be rebuilt. The IDs of them should be the same.
        attrs = {
            'id': new_server.id,
            'image': {
                'id': self.image.id
            },
            'networks': {},
            'adminPass': 'passw0rd',
        }
        methods = {
            'rebuild': new_server,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=attrs,
            methods=methods
        )

        # Return value for utils.find_resource for server.
        self.servers_mock.get.return_value = self.server

        self.cmd = server.RebuildServer(self.app, None)

    def test_rebuild_with_current_image(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test.
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.cimages_mock.get.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None)

    def test_rebuild_with_current_image_and_password(self):
        password = 'password-xxx'
        arglist = [
            self.server.id,
            '--password', password
        ]
        verifylist = [
            ('server', self.server.id),
            ('password', password)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.cimages_mock.get.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, password)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_rebuild_with_wait_ok(self, mock_wait_for_status):
        arglist = [
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('wait', True),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test.
        self.cmd.take_action(parsed_args)

        # kwargs = dict(success_status=['active', 'verify_resize'],)

        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.server.id,
            callback=server._show_progress,
            # **kwargs
        )

        self.servers_mock.get.assert_called_with(self.server.id)
        self.cimages_mock.get.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_rebuild_with_wait_fails(self, mock_wait_for_status):
        arglist = [
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('wait', True),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.server.id,
            callback=server._show_progress
        )

        self.servers_mock.get.assert_called_with(self.server.id)
        self.cimages_mock.get.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None)


class TestServerRemoveFixedIP(TestServer):

    def setUp(self):
        super(TestServerRemoveFixedIP, self).setUp()

        # Get the command object to test
        self.cmd = server.RemoveFixedIP(self.app, None)

        # Set unshelve method to be tested.
        self.methods = {
            'remove_fixed_ip': None,
        }

    def test_server_remove_fixed_ip(self):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id,
            '1.2.3.4',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('ip_address', '1.2.3.4'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].remove_fixed_ip.assert_called_once_with('1.2.3.4')
        self.assertIsNone(result)


class TestServerRemoveFloatingIP(TestServer):

    def setUp(self):
        super(TestServerRemoveFloatingIP, self).setUp()

        # Get the command object to test
        self.cmd = server.RemoveFloatingIP(self.app, None)

        # Set unshelve method to be tested.
        self.methods = {
            'remove_floating_ip': None,
        }

    def test_server_remove_floating_ip(self):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id,
            '1.2.3.4',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('ip_address', '1.2.3.4'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].remove_floating_ip.assert_called_once_with('1.2.3.4')
        self.assertIsNone(result)


class TestServerRemoveSecurityGroup(TestServer):

    def setUp(self):
        super(TestServerRemoveSecurityGroup, self).setUp()

        self.security_group = \
            compute_fakes.FakeSecurityGroup.create_one_security_group()
        # This is the return value for utils.find_resource() for security group
        self.security_groups_mock.get.return_value = self.security_group

        attrs = {
            'security_groups': [{'name': self.security_group.id}]
        }
        methods = {
            'remove_security_group': None,
        }

        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=attrs,
            methods=methods
        )
        # This is the return value for utils.find_resource() for server
        self.servers_mock.get.return_value = self.server

        # Get the command object to test
        self.cmd = server.RemoveServerSecurityGroup(self.app, None)

    def test_server_remove_security_group(self):
        arglist = [
            self.server.id,
            self.security_group.id
        ]
        verifylist = [
            ('server', self.server.id),
            ('group', self.security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.security_groups_mock.get.assert_called_with(
            self.security_group.id,
        )
        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.remove_security_group.assert_called_with(
            self.security_group.id,
        )
        self.assertIsNone(result)


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

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)

        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.flavors_mock.get.assert_called_with(
            self.flavors_get_return_value.id,
        )
        self.servers_mock.resize.assert_called_with(
            self.server,
            self.flavors_get_return_value,
        )
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.resize)
        self.servers_mock.confirm_resize.assert_called_with(self.server)
        self.assertNotCalled(self.servers_mock.revert_resize)
        self.assertIsNone(result)

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

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.servers_mock.revert_resize.assert_called_with(self.server)
        self.assertIsNone(result)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_resize_with_wait_ok(self, mock_wait_for_status):

        arglist = [
            '--flavor', self.flavors_get_return_value.id,
            '--wait',
            self.server.id,
        ]

        verifylist = [
            ('flavor', self.flavors_get_return_value.id),
            ('confirm', False),
            ('revert', False),
            ('wait', True),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(
            self.server.id,
        )

        kwargs = dict(success_status=['active', 'verify_resize'],)

        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.server.id,
            callback=server._show_progress,
            **kwargs
        )

        self.servers_mock.resize.assert_called_with(
            self.server,
            self.flavors_get_return_value
        )
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.assertNotCalled(self.servers_mock.revert_resize)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_resize_with_wait_fails(self, mock_wait_for_status):

        arglist = [
            '--flavor', self.flavors_get_return_value.id,
            '--wait',
            self.server.id,
        ]

        verifylist = [
            ('flavor', self.flavors_get_return_value.id),
            ('confirm', False),
            ('revert', False),
            ('wait', True),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        self.servers_mock.get.assert_called_with(
            self.server.id,
        )

        kwargs = dict(success_status=['active', 'verify_resize'],)

        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.server.id,
            callback=server._show_progress,
            **kwargs
        )

        self.servers_mock.resize.assert_called_with(
            self.server,
            self.flavors_get_return_value
        )


class TestServerRestore(TestServer):

    def setUp(self):
        super(TestServerRestore, self).setUp()

        # Get the command object to test
        self.cmd = server.RestoreServer(self.app, None)

        # Set methods to be tested.
        self.methods = {
            'restore': None,
        }

    def test_server_restore_one_server(self):
        self.run_method_with_servers('restore', 1)

    def test_server_restore_multi_servers(self):
        self.run_method_with_servers('restore', 3)


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


class TestServerSet(TestServer):

    def setUp(self):
        super(TestServerSet, self).setUp()

        self.methods = {
            'update': None,
            'reset_state': None,
            'change_password': None,
        }

        self.fake_servers = self.setup_servers_mock(2)

        # Get the command object to test
        self.cmd = server.SetServer(self.app, None)

    def test_server_set_no_option(self):
        arglist = [
            'foo_vm'
        ]
        verifylist = [
            ('server', 'foo_vm')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertNotCalled(self.fake_servers[0].update)
        self.assertNotCalled(self.fake_servers[0].reset_state)
        self.assertNotCalled(self.fake_servers[0].change_password)
        self.assertNotCalled(self.servers_mock.set_meta)
        self.assertIsNone(result)

    def test_server_set_with_state(self):
        for index, state in enumerate(['active', 'error']):
            arglist = [
                '--state', state,
                'foo_vm',
            ]
            verifylist = [
                ('state', state),
                ('server', 'foo_vm'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            result = self.cmd.take_action(parsed_args)
            self.fake_servers[index].reset_state.assert_called_once_with(
                state=state)
            self.assertIsNone(result)

    def test_server_set_with_invalid_state(self):
        arglist = [
            '--state', 'foo_state',
            'foo_vm',
        ]
        verifylist = [
            ('state', 'foo_state'),
            ('server', 'foo_vm'),
        ]
        self.assertRaises(utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_server_set_with_name(self):
        arglist = [
            '--name', 'foo_name',
            'foo_vm',
        ]
        verifylist = [
            ('name', 'foo_name'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.fake_servers[0].update.assert_called_once_with(name='foo_name')
        self.assertIsNone(result)

    def test_server_set_with_property(self):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'foo_vm',
        ]
        verifylist = [
            ('property', {'key1': 'value1', 'key2': 'value2'}),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.servers_mock.set_meta.assert_called_once_with(
            self.fake_servers[0], parsed_args.property)
        self.assertIsNone(result)

    @mock.patch.object(getpass, 'getpass',
                       return_value=mock.sentinel.fake_pass)
    def test_server_set_with_root_password(self, mock_getpass):
        arglist = [
            '--root-password',
            'foo_vm',
        ]
        verifylist = [
            ('root_password', True),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.fake_servers[0].change_password.assert_called_once_with(
            mock.sentinel.fake_pass)
        self.assertIsNone(result)


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


class TestServerShow(TestServer):

    def setUp(self):
        super(TestServerShow, self).setUp()

        self.image = image_fakes.FakeImage.create_one_image()
        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        server_info = {
            'image': {'id': self.image.id},
            'flavor': {'id': self.flavor.id},
            'tenant_id': 'tenant-id-xxx',
            'networks': {'public': ['10.20.30.40', '2001:db8::f']},
        }
        # Fake the server.diagnostics() method. The return value contains http
        # response and data. The data is a dict. Sincce this method itself is
        # faked, we don't need to fake everything of the return value exactly.
        resp = mock.Mock()
        resp.status_code = 200
        server_method = {
            'diagnostics': (resp, {'test': 'test'}),
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=server_info, methods=server_method)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server
        self.cimages_mock.get.return_value = self.image
        self.flavors_mock.get.return_value = self.flavor

        # Get the command object to test
        self.cmd = server.ShowServer(self.app, None)

        self.columns = (
            'OS-EXT-STS:power_state',
            'addresses',
            'flavor',
            'id',
            'image',
            'name',
            'networks',
            'project_id',
            'properties',
        )

        self.data = (
            'Running',
            'public=10.20.30.40, 2001:db8::f',
            self.flavor.name + " (" + self.flavor.id + ")",
            self.server.id,
            self.image.name + " (" + self.image.id + ")",
            self.server.name,
            {'public': ['10.20.30.40', '2001:db8::f']},
            'tenant-id-xxx',
            '',
        )

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show(self):
        arglist = [
            self.server.name,
        ]
        verifylist = [
            ('diagnostics', False),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_show_diagnostics(self):
        arglist = [
            '--diagnostics',
            self.server.name,
        ]
        verifylist = [
            ('diagnostics', True),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(('test',), columns)
        self.assertEqual(('test',), data)


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


class TestServerUnset(TestServer):

    def setUp(self):
        super(TestServerUnset, self).setUp()

        self.fake_server = self.setup_servers_mock(1)[0]

        # Get the command object to test
        self.cmd = server.UnsetServer(self.app, None)

    def test_server_unset_no_option(self):
        arglist = [
            'foo_vm',
        ]
        verifylist = [
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertNotCalled(self.servers_mock.delete_meta)
        self.assertIsNone(result)

    def test_server_unset_with_property(self):
        arglist = [
            '--property', 'key1',
            '--property', 'key2',
            'foo_vm',
        ]
        verifylist = [
            ('property', ['key1', 'key2']),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.servers_mock.delete_meta.assert_called_once_with(
            self.fake_server, ['key1', 'key2'])
        self.assertIsNone(result)


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


class TestServerGeneral(TestServer):
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

    def test_format_servers_list_power_state(self):
        self.assertEqual("NOSTATE",
                         server._format_servers_list_power_state(0x00))
        self.assertEqual("Running",
                         server._format_servers_list_power_state(0x01))
        self.assertEqual("",
                         server._format_servers_list_power_state(0x02))
        self.assertEqual("Paused",
                         server._format_servers_list_power_state(0x03))
        self.assertEqual("Shutdown",
                         server._format_servers_list_power_state(0x04))
        self.assertEqual("",
                         server._format_servers_list_power_state(0x05))
        self.assertEqual("Crashed",
                         server._format_servers_list_power_state(0x06))
        self.assertEqual("Suspended",
                         server._format_servers_list_power_state(0x07))
        self.assertEqual("N/A",
                         server._format_servers_list_power_state(0x08))

    def test_format_servers_list_networks(self):
        # Setup network info to test.
        networks = {
            u'public': [u'10.20.30.40', u'2001:db8::f'],
            u'private': [u'2001:db8::f', u'10.20.30.40'],
        }

        # Prepare expected data.
        # Since networks is a dict, whose items are in random order, there
        # could be two results after formatted.
        data_1 = (u'private=2001:db8::f, 10.20.30.40; '
                  u'public=10.20.30.40, 2001:db8::f')
        data_2 = (u'public=10.20.30.40, 2001:db8::f; '
                  u'private=2001:db8::f, 10.20.30.40')

        # Call _format_servers_list_networks().
        networks_format = server._format_servers_list_networks(networks)

        msg = ('Network string is not formatted correctly.\n'
               'reference = %s or %s\n'
               'actual    = %s\n' %
               (data_1, data_2, networks_format))
        self.assertIn(networks_format, (data_1, data_2), msg)

    @mock.patch('osc_lib.utils.find_resource')
    def test_prep_server_detail(self, find_resource):
        # Setup mock method return value. utils.find_resource() will be called
        # three times in _prep_server_detail():
        # - The first time, return server info.
        # - The second time, return image info.
        # - The third time, return flavor info.
        _image = image_fakes.FakeImage.create_one_image()
        _flavor = compute_fakes.FakeFlavor.create_one_flavor()
        server_info = {
            'image': {u'id': _image.id},
            'flavor': {u'id': _flavor.id},
            'tenant_id': u'tenant-id-xxx',
            'networks': {u'public': [u'10.20.30.40', u'2001:db8::f']},
            'links': u'http://xxx.yyy.com',
        }
        _server = compute_fakes.FakeServer.create_one_server(attrs=server_info)
        find_resource.side_effect = [_server, _image, _flavor]

        # Prepare result data.
        info = {
            'id': _server.id,
            'name': _server.name,
            'addresses': u'public=10.20.30.40, 2001:db8::f',
            'flavor': u'%s (%s)' % (_flavor.name, _flavor.id),
            'image': u'%s (%s)' % (_image.name, _image.id),
            'project_id': u'tenant-id-xxx',
            'properties': '',
            'OS-EXT-STS:power_state': server._format_servers_list_power_state(
                getattr(_server, 'OS-EXT-STS:power_state')),
        }

        # Call _prep_server_detail().
        server_detail = server._prep_server_detail(
            self.app.client_manager.compute,
            _server
        )
        # 'networks' is used to create _server. Remove it.
        server_detail.pop('networks')

        # Check the results.
        self.assertEqual(info, server_detail)
