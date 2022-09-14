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
import argparse
import collections
import copy
import getpass
import json
import tempfile
from unittest import mock
from unittest.mock import call

import iso8601
from novaclient import api_versions
from openstack import exceptions as sdk_exceptions
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils as common_utils

from openstackclient.compute.v2 import server
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class TestPowerStateColumn(utils.TestCase):

    def test_human_readable(self):
        self.assertEqual(
            'NOSTATE', server.PowerStateColumn(0x00).human_readable())
        self.assertEqual(
            'Running', server.PowerStateColumn(0x01).human_readable())
        self.assertEqual(
            '', server.PowerStateColumn(0x02).human_readable())
        self.assertEqual(
            'Paused', server.PowerStateColumn(0x03).human_readable())
        self.assertEqual(
            'Shutdown', server.PowerStateColumn(0x04).human_readable())
        self.assertEqual(
            '', server.PowerStateColumn(0x05).human_readable())
        self.assertEqual(
            'Crashed', server.PowerStateColumn(0x06).human_readable())
        self.assertEqual(
            'Suspended', server.PowerStateColumn(0x07).human_readable())
        self.assertEqual(
            'N/A', server.PowerStateColumn(0x08).human_readable())


class TestServer(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServer, self).setUp()

        # Get a shortcut to the compute client ServerManager Mock
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()

        # Get a shortcut to the compute client ServerMigrationsManager Mock
        self.server_migrations_mock = \
            self.app.client_manager.compute.server_migrations
        self.server_migrations_mock.reset_mock()

        # Get a shortcut to the compute client VolumeManager mock
        self.servers_volumes_mock = self.app.client_manager.compute.volumes
        self.servers_volumes_mock.reset_mock()

        # Get a shortcut to the compute client MigrationManager mock
        self.migrations_mock = self.app.client_manager.compute.migrations
        self.migrations_mock.reset_mock()

        # Get a shortcut to the compute client FlavorManager Mock
        self.flavors_mock = self.app.client_manager.compute.flavors
        self.flavors_mock.reset_mock()

        # Get a shortcut to the image client ImageManager Mock
        self.images_mock = self.app.client_manager.image.images
        self.images_mock.reset_mock()

        self.find_image_mock = self.app.client_manager.image.find_image
        self.find_image_mock.reset_mock()

        self.get_image_mock = self.app.client_manager.image.get_image
        self.get_image_mock.reset_mock()

        # Get a shortcut to the volume client VolumeManager Mock
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()

        # Get a shortcut to the volume client VolumeManager Mock
        self.snapshots_mock = self.app.client_manager.volume.volume_snapshots
        self.snapshots_mock.reset_mock()

        # Set object attributes to be tested. Could be overwritten in subclass.
        self.attrs = {}

        # Set object methods to be tested. Could be overwritten in subclass.
        self.methods = {}

    def setup_servers_mock(self, count):
        # If we are creating more than one server, make one of them
        # boot-from-volume
        include_bfv = count > 1
        servers = compute_fakes.FakeServer.create_servers(
            attrs=self.attrs,
            methods=self.methods,
            count=count - 1 if include_bfv else count
        )
        if include_bfv:
            attrs = copy.deepcopy(self.attrs)
            attrs['image'] = ''
            bfv_server = compute_fakes.FakeServer.create_one_server(
                attrs=attrs,
                methods=self.methods
            )
            servers.append(bfv_server)

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
            if method_name == 'lock':
                version = self.app.client_manager.compute.api_version
                if version >= api_versions.APIVersion('2.73'):
                    method.assert_called_with(reason=None)
            elif method_name == 'unshelve':
                version = self.app.client_manager.compute.api_version
                if version >= api_versions.APIVersion('2.77'):
                    method.assert_called_with(availability_zone=None)
                else:
                    method.assert_called_with()
            else:
                method.assert_called_with()
        self.assertIsNone(result)


class TestServerAddFixedIP(TestServer):

    def setUp(self):
        super(TestServerAddFixedIP, self).setUp()

        # Get the command object to test
        self.cmd = server.AddFixedIP(self.app, None)

        # Set add_fixed_ip method to be tested.
        self.methods = {
            'interface_attach': None,
        }

    def _test_server_add_fixed_ip(self, extralist, fixed_ip_address):
        servers = self.setup_servers_mock(count=1)
        network = compute_fakes.FakeNetwork.create_one_network()
        with mock.patch(
            'openstackclient.api.compute_v2.APIv2.network_find'
        ) as net_mock:
            net_mock.return_value = network

            arglist = [
                servers[0].id,
                network['id'],
            ] + extralist
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', fixed_ip_address),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            result = self.cmd.take_action(parsed_args)

            servers[0].interface_attach.assert_called_once_with(
                port_id=None,
                net_id=network['id'],
                fixed_ip=fixed_ip_address,
            )
            self.assertIsNone(result)

    def test_server_add_fixed_ip(self):
        self._test_server_add_fixed_ip([], None)

    def test_server_add_specific_fixed_ip(self):
        extralist = ['--fixed-ip-address', '5.6.7.8']
        self._test_server_add_fixed_ip(extralist, '5.6.7.8')

    def test_server_add_fixed_ip_with_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.49')

        servers = self.setup_servers_mock(count=1)
        network = compute_fakes.FakeNetwork.create_one_network()
        with mock.patch(
            'openstackclient.api.compute_v2.APIv2.network_find'
        ) as net_mock:
            net_mock.return_value = network

            arglist = [
                servers[0].id,
                network['id'],
                '--fixed-ip-address', '5.6.7.8',
                '--tag', 'tag1',
            ]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', '5.6.7.8'),
                ('tag', 'tag1'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            result = self.cmd.take_action(parsed_args)

            servers[0].interface_attach.assert_called_once_with(
                port_id=None,
                net_id=network['id'],
                fixed_ip='5.6.7.8',
                tag='tag1'
            )
            self.assertIsNone(result)

    def test_server_add_fixed_ip_with_tag_pre_v249(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.48')

        servers = self.setup_servers_mock(count=1)
        network = compute_fakes.FakeNetwork.create_one_network()
        with mock.patch(
            'openstackclient.api.compute_v2.APIv2.network_find'
        ) as net_mock:
            net_mock.return_value = network

            arglist = [
                servers[0].id,
                network['id'],
                '--fixed-ip-address', '5.6.7.8',
                '--tag', 'tag1',
            ]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', '5.6.7.8'),
                ('tag', 'tag1'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
            ex = self.assertRaises(
                exceptions.CommandError,
                self.cmd.take_action,
                parsed_args)
            self.assertIn(
                '--os-compute-api-version 2.49 or greater is required',
                str(ex))


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.floating_ip_add'
)
class TestServerAddFloatingIPCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServerAddFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = server.AddFloatingIP(self.app, None)

    def test_server_add_floating_ip_default(self, fip_mock):
        _floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()
        arglist = [
            'server1',
            _floating_ip['ip'],
        ]
        verifylist = [
            ('server', 'server1'),
            ('ip_address', _floating_ip['ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(
            'server1',
            _floating_ip['ip'],
            fixed_address=None,
        )

    def test_server_add_floating_ip_fixed(self, fip_mock):
        _floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()
        arglist = [
            '--fixed-ip-address', _floating_ip['fixed_ip'],
            'server1',
            _floating_ip['ip'],
        ]
        verifylist = [
            ('fixed_ip_address', _floating_ip['fixed_ip']),
            ('server', 'server1'),
            ('ip_address', _floating_ip['ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(
            'server1',
            _floating_ip['ip'],
            fixed_address=_floating_ip['fixed_ip'],
        )


class TestServerAddFloatingIPNetwork(
    TestServer,
    network_fakes.TestNetworkV2,
):

    def setUp(self):
        super(TestServerAddFloatingIPNetwork, self).setUp()

        self.app.client_manager.network = mock.Mock()
        self.network = self.app.client_manager.network
        self.network.update_ip = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = server.AddFloatingIP(self.app, self.namespace)

    def test_server_add_floating_ip(self):
        _server = compute_fakes.FakeServer.create_one_server()
        self.servers_mock.get.return_value = _server
        _port = network_fakes.FakePort.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network.find_ip = mock.Mock(return_value=_floating_ip)
        self.network.ports = mock.Mock(return_value=[_port])
        arglist = [
            _server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('server', _server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': _port.id,
        }

        self.network.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network.ports.assert_called_once_with(
            device_id=_server.id,
        )
        self.network.update_ip.assert_called_once_with(
            _floating_ip,
            **attrs
        )

    def test_server_add_floating_ip_no_ports(self):
        server = compute_fakes.FakeServer.create_one_server()
        floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()

        self.servers_mock.get.return_value = server
        self.network.find_ip = mock.Mock(return_value=floating_ip)
        self.network.ports = mock.Mock(return_value=[])

        arglist = [
            server.id,
            floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('server', server.id),
            ('ip_address', floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            'No attached ports found to associate floating IP with',
            str(ex))

        self.network.find_ip.assert_called_once_with(
            floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network.ports.assert_called_once_with(
            device_id=server.id,
        )

    def test_server_add_floating_ip_no_external_gateway(self, success=False):
        _server = compute_fakes.FakeServer.create_one_server()
        self.servers_mock.get.return_value = _server
        _port = network_fakes.FakePort.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network.find_ip = mock.Mock(return_value=_floating_ip)
        return_value = [_port]
        # In the success case, we'll have two ports, where the first port is
        # not attached to an external gateway but the second port is.
        if success:
            return_value.append(_port)
        self.network.ports = mock.Mock(return_value=return_value)
        side_effect = [sdk_exceptions.NotFoundException()]
        if success:
            side_effect.append(None)
        self.network.update_ip = mock.Mock(side_effect=side_effect)
        arglist = [
            _server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('server', _server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        if success:
            self.cmd.take_action(parsed_args)
        else:
            self.assertRaises(sdk_exceptions.NotFoundException,
                              self.cmd.take_action, parsed_args)

        attrs = {
            'port_id': _port.id,
        }

        self.network.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network.ports.assert_called_once_with(
            device_id=_server.id,
        )
        if success:
            self.assertEqual(2, self.network.update_ip.call_count)
            calls = [mock.call(_floating_ip, **attrs)] * 2
            self.network.update_ip.assert_has_calls(calls)
        else:
            self.network.update_ip.assert_called_once_with(
                _floating_ip,
                **attrs
            )

    def test_server_add_floating_ip_one_external_gateway(self):
        self.test_server_add_floating_ip_no_external_gateway(success=True)

    def test_server_add_floating_ip_with_fixed_ip(self):
        _server = compute_fakes.FakeServer.create_one_server()
        self.servers_mock.get.return_value = _server
        _port = network_fakes.FakePort.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network.find_ip = mock.Mock(return_value=_floating_ip)
        self.network.ports = mock.Mock(return_value=[_port])
        # The user has specified a fixed ip that matches one of the ports
        # already attached to the instance.
        arglist = [
            '--fixed-ip-address', _port.fixed_ips[0]['ip_address'],
            _server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('fixed_ip_address', _port.fixed_ips[0]['ip_address']),
            ('server', _server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # We expect the update_ip call to specify a new fixed_ip_address which
        # will overwrite the floating ip's existing fixed_ip_address.
        attrs = {
            'port_id': _port.id,
            'fixed_ip_address': _port.fixed_ips[0]['ip_address'],
        }

        self.network.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network.ports.assert_called_once_with(
            device_id=_server.id,
        )
        self.network.update_ip.assert_called_once_with(
            _floating_ip,
            **attrs
        )

    def test_server_add_floating_ip_with_fixed_ip_no_port_found(self):
        _server = compute_fakes.FakeServer.create_one_server()
        self.servers_mock.get.return_value = _server
        _port = network_fakes.FakePort.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network.find_ip = mock.Mock(return_value=_floating_ip)
        self.network.ports = mock.Mock(return_value=[_port])
        # The user has specified a fixed ip that does not match any of the
        # ports already attached to the instance.
        nonexistent_ip = '10.0.0.9'
        arglist = [
            '--fixed-ip-address', nonexistent_ip,
            _server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('fixed_ip_address', nonexistent_ip),
            ('server', _server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        self.network.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network.ports.assert_called_once_with(
            device_id=_server.id,
        )
        self.network.update_ip.assert_not_called()


class TestServerAddPort(TestServer):

    def setUp(self):
        super(TestServerAddPort, self).setUp()

        # Get the command object to test
        self.cmd = server.AddPort(self.app, None)

        # Set add_fixed_ip method to be tested.
        self.methods = {
            'interface_attach': None,
        }

        self.find_port = mock.Mock()
        self.app.client_manager.network.find_port = self.find_port

    def _test_server_add_port(self, port_id):
        servers = self.setup_servers_mock(count=1)
        port = 'fake-port'

        arglist = [
            servers[0].id,
            port,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('port', port)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].interface_attach.assert_called_once_with(
            port_id=port_id, net_id=None, fixed_ip=None)
        self.assertIsNone(result)

    def test_server_add_port(self):
        self._test_server_add_port(self.find_port.return_value.id)
        self.find_port.assert_called_once_with(
            'fake-port', ignore_missing=False)

    def test_server_add_port_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_add_port('fake-port')
        self.find_port.assert_not_called()

    def test_server_add_port_with_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.49')

        servers = self.setup_servers_mock(count=1)
        self.find_port.return_value.id = 'fake-port'
        arglist = [
            servers[0].id,
            'fake-port',
            '--tag', 'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('port', 'fake-port'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        servers[0].interface_attach.assert_called_once_with(
            port_id='fake-port',
            net_id=None,
            fixed_ip=None,
            tag='tag1')

    def test_server_add_port_with_tag_pre_v249(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.48')

        servers = self.setup_servers_mock(count=1)
        self.find_port.return_value.id = 'fake-port'
        arglist = [
            servers[0].id,
            'fake-port',
            '--tag', 'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('port', 'fake-port'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.49 or greater is required',
            str(ex))


class TestServerVolume(TestServer):

    def setUp(self):
        super(TestServerVolume, self).setUp()

        self.volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = self.volume

        self.methods = {
            'create_server_volume': None,
        }

        # Get the command object to test
        self.cmd = server.AddServerVolume(self.app, None)

    def test_server_add_volume(self):
        servers = self.setup_servers_mock(count=1)
        arglist = [
            '--device', '/dev/sdb',
            servers[0].id,
            self.volume.id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_volumes_mock.create_server_volume.assert_called_once_with(
            servers[0].id, self.volume.id, device='/dev/sdb')
        self.assertIsNone(result)

    def test_server_add_volume_with_tag(self):
        # requires API 2.49 or later
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.49')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            '--device', '/dev/sdb',
            '--tag', 'foo',
            servers[0].id,
            self.volume.id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('tag', 'foo'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_volumes_mock.create_server_volume.assert_called_once_with(
            servers[0].id, self.volume.id, device='/dev/sdb', tag='foo')
        self.assertIsNone(result)

    def test_server_add_volume_with_tag_pre_v249(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.48')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            servers[0].id,
            self.volume.id,
            '--tag', 'foo',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('tag', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.49 or greater is required',
            str(ex))

    def test_server_add_volume_with_enable_delete_on_termination(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.79')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            '--enable-delete-on-termination',
            '--device', '/dev/sdb',
            servers[0].id,
            self.volume.id,
        ]

        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('enable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_volumes_mock.create_server_volume.assert_called_once_with(
            servers[0].id, self.volume.id,
            device='/dev/sdb', delete_on_termination=True)
        self.assertIsNone(result)

    def test_server_add_volume_with_disable_delete_on_termination(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.79')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            '--disable-delete-on-termination',
            '--device', '/dev/sdb',
            servers[0].id,
            self.volume.id,
        ]

        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('disable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_volumes_mock.create_server_volume.assert_called_once_with(
            servers[0].id, self.volume.id,
            device='/dev/sdb', delete_on_termination=False)
        self.assertIsNone(result)

    def test_server_add_volume_with_enable_delete_on_termination_pre_v279(
        self,
    ):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.78')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            servers[0].id,
            self.volume.id,
            '--enable-delete-on-termination',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('enable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd.take_action,
                               parsed_args)
        self.assertIn('--os-compute-api-version 2.79 or greater is required',
                      str(ex))

    def test_server_add_volume_with_disable_delete_on_termination_pre_v279(
        self,
    ):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.78')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            servers[0].id,
            self.volume.id,
            '--disable-delete-on-termination',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('disable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd.take_action,
                               parsed_args)
        self.assertIn('--os-compute-api-version 2.79 or greater is required',
                      str(ex))

    def test_server_add_volume_with_disable_and_enable_delete_on_termination(
        self,
    ):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.79')

        servers = self.setup_servers_mock(count=1)
        arglist = [
            '--enable-delete-on-termination',
            '--disable-delete-on-termination',
            '--device', '/dev/sdb',
            servers[0].id,
            self.volume.id,
        ]

        verifylist = [
            ('server', servers[0].id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('enable_delete_on_termination', True),
            ('disable_delete_on_termination', True),
        ]
        ex = self.assertRaises(utils.ParserException,
                               self.check_parser,
                               self.cmd, arglist, verifylist)
        self.assertIn('argument --disable-delete-on-termination: not allowed '
                      'with argument --enable-delete-on-termination', str(ex))


class TestServerAddNetwork(TestServer):

    def setUp(self):
        super(TestServerAddNetwork, self).setUp()

        # Get the command object to test
        self.cmd = server.AddNetwork(self.app, None)

        # Set add_fixed_ip method to be tested.
        self.methods = {
            'interface_attach': None,
        }

        self.find_network = mock.Mock()
        self.app.client_manager.network.find_network = self.find_network

    def _test_server_add_network(self, net_id):
        servers = self.setup_servers_mock(count=1)
        network = 'fake-network'

        arglist = [
            servers[0].id,
            network,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', network)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].interface_attach.assert_called_once_with(
            port_id=None, net_id=net_id, fixed_ip=None)
        self.assertIsNone(result)

    def test_server_add_network(self):
        self._test_server_add_network(self.find_network.return_value.id)
        self.find_network.assert_called_once_with(
            'fake-network', ignore_missing=False)

    def test_server_add_network_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_add_network('fake-network')
        self.find_network.assert_not_called()

    def test_server_add_network_with_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.49')

        servers = self.setup_servers_mock(count=1)
        self.find_network.return_value.id = 'fake-network'

        arglist = [
            servers[0].id,
            'fake-network',
            '--tag', 'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', 'fake-network'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        servers[0].interface_attach.assert_called_once_with(
            port_id=None,
            net_id='fake-network',
            fixed_ip=None,
            tag='tag1'
        )

    def test_server_add_network_with_tag_pre_v249(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.48')

        servers = self.setup_servers_mock(count=1)
        self.find_network.return_value.id = 'fake-network'

        arglist = [
            servers[0].id,
            'fake-network',
            '--tag', 'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', 'fake-network'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.49 or greater is required',
            str(ex))


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_find'
)
class TestServerAddSecurityGroup(TestServer):

    def setUp(self):
        super(TestServerAddSecurityGroup, self).setUp()

        self.security_group = \
            compute_fakes.FakeSecurityGroup.create_one_security_group()

        attrs = {
            'security_groups': [{'name': self.security_group['id']}]
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

    def test_server_add_security_group(self, sg_find_mock):
        sg_find_mock.return_value = self.security_group
        arglist = [
            self.server.id,
            self.security_group['id']
        ]
        verifylist = [
            ('server', self.server.id),
            ('group', self.security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        sg_find_mock.assert_called_with(
            self.security_group['id'],
        )
        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.add_security_group.assert_called_with(
            self.security_group['id'],
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
            server.PowerStateColumn(
                getattr(self.new_server, 'OS-EXT-STS:power_state')),
            format_columns.DictListColumn({}),
            self.flavor.name + ' (' + self.new_server.flavor.get('id') + ')',
            self.new_server.id,
            self.image.name + ' (' + self.new_server.image.get('id') + ')',
            self.new_server.name,
            self.new_server.networks,
            format_columns.DictColumn(self.new_server.metadata),
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
        self.find_image_mock.return_value = self.image
        self.get_image_mock.return_value = self.image

        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        self.flavors_mock.get.return_value = self.flavor

        self.volume = volume_fakes.FakeVolume.create_one_volume()
        self.volumes_mock.get.return_value = self.volume

        self.snapshot = volume_fakes.FakeSnapshot.create_one_snapshot()
        self.snapshots_mock.get.return_value = self.snapshot

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
            admin_pass=None,
            block_device_mapping_v2=[],
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
        self.assertFalse(self.images_mock.called)
        self.assertFalse(self.flavors_mock.called)

    def test_server_create_with_options(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--key-name', 'keyname',
            '--property', 'Beta=b',
            '--security-group', 'securitygroup',
            '--use-config-drive',
            '--password', 'passw0rd',
            '--hint', 'a=b',
            '--hint', 'a=c',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('key_name', 'keyname'),
            ('properties', {'Beta': 'b'}),
            ('security_group', ['securitygroup']),
            ('hint', {'a': ['b', 'c']}),
            ('config_drive', True),
            ('password', 'passw0rd'),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        fake_sg = network_fakes.FakeSecurityGroup.create_security_groups()
        mock_find_sg = (
            network_fakes.FakeSecurityGroup.get_security_groups(fake_sg)
        )
        self.app.client_manager.network.find_security_group = mock_find_sg

        columns, data = self.cmd.take_action(parsed_args)

        mock_find_sg.assert_called_once_with('securitygroup',
                                             ignore_missing=False)
        # Set expected values
        kwargs = dict(
            meta={'Beta': 'b'},
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[fake_sg[0].id],
            userdata=None,
            key_name='keyname',
            availability_zone=None,
            admin_pass='passw0rd',
            block_device_mapping_v2=[],
            nics=[],
            scheduler_hints={'a': ['b', 'c']},
            config_drive=True,
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

    def test_server_create_with_not_exist_security_group(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--key-name', 'keyname',
            '--security-group', 'securitygroup',
            '--security-group', 'not_exist_sg',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('key_name', 'keyname'),
            ('security_group', ['securitygroup', 'not_exist_sg']),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        fake_sg = network_fakes.FakeSecurityGroup.create_security_groups(
            count=1)
        fake_sg.append(exceptions.NotFound(code=404))
        mock_find_sg = (
            network_fakes.FakeSecurityGroup.get_security_groups(fake_sg)
        )
        self.app.client_manager.network.find_security_group = mock_find_sg

        self.assertRaises(exceptions.NotFound,
                          self.cmd.take_action,
                          parsed_args)
        mock_find_sg.assert_called_with('not_exist_sg',
                                        ignore_missing=False)

    def test_server_create_with_security_group_in_nova_network(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--key-name', 'keyname',
            '--security-group', 'securitygroup',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('key_name', 'keyname'),
            ('security_group', ['securitygroup']),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.app.client_manager,
                               'is_network_endpoint_enabled',
                               return_value=False):
            with mock.patch.object(self.app.client_manager.compute.api,
                                   'security_group_find',
                                   return_value={'name': 'fake_sg'}
                                   ) as mock_find:
                columns, data = self.cmd.take_action(parsed_args)
                mock_find.assert_called_once_with('securitygroup')

        # Set expected values
        kwargs = dict(
            meta=None,
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=['fake_sg'],
            userdata=None,
            key_name='keyname',
            availability_zone=None,
            admin_pass=None,
            block_device_mapping_v2=[],
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
            '--network', 'net1',
            '--nic', 'net-id=net1,v4-fixed-ip=10.0.0.2',
            '--port', 'port1',
            '--network', 'net1',
            '--nic', 'port-id=port2',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nics', [
                {
                    'net-id': 'net1', 'port-id': '',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                },
                {
                    'net-id': 'net1', 'port-id': '',
                    'v4-fixed-ip': '10.0.0.2', 'v6-fixed-ip': '',
                },
                {
                    'net-id': '', 'port-id': 'port1',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                },
                {
                    'net-id': 'net1', 'port-id': '',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                },
                {
                    'net-id': '', 'port-id': 'port2',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                },
            ]),
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
        network_resource = mock.Mock(id='net1_uuid')
        port1_resource = mock.Mock(id='port1_uuid')
        port2_resource = mock.Mock(id='port2_uuid')
        find_network.return_value = network_resource
        find_port.side_effect = (lambda port_id, ignore_missing:
                                 {"port1": port1_resource,
                                  "port2": port2_resource}[port_id])

        # Mock sdk APIs.
        _network = mock.Mock(id='net1_uuid')
        _port1 = mock.Mock(id='port1_uuid')
        _port2 = mock.Mock(id='port2_uuid')
        find_network = mock.Mock()
        find_port = mock.Mock()
        find_network.return_value = _network
        find_port.side_effect = (lambda port_id, ignore_missing:
                                 {"port1": _port1,
                                  "port2": _port2}[port_id])
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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics=[{'net-id': 'net1_uuid',
                   'v4-fixed-ip': '',
                   'v6-fixed-ip': '',
                   'port-id': ''},
                  {'net-id': 'net1_uuid',
                   'v4-fixed-ip': '10.0.0.2',
                   'v6-fixed-ip': '',
                   'port-id': ''},
                  {'net-id': '',
                   'v4-fixed-ip': '',
                   'v6-fixed-ip': '',
                   'port-id': 'port1_uuid'},
                  {'net-id': 'net1_uuid',
                   'v4-fixed-ip': '',
                   'v6-fixed-ip': '',
                   'port-id': ''},
                  {'net-id': '',
                   'v4-fixed-ip': '',
                   'v6-fixed-ip': '',
                   'port-id': 'port2_uuid'}],
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

    def test_server_create_with_network_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.43')

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'net-id=net1,tag=foo',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nics', [
                {
                    'net-id': 'net1', 'port-id': '',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                    'tag': 'foo',
                },
            ]),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_network = mock.Mock()
        network_client = self.app.client_manager.network
        network_client.find_network = find_network
        network_resource = mock.Mock(id='net1_uuid')
        find_network.return_value = network_resource

        # Mock sdk APIs.
        _network = mock.Mock(id='net1_uuid')
        find_network = mock.Mock()
        find_network.return_value = _network
        self.app.client_manager.network.find_network = find_network

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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics=[
                {
                    'net-id': 'net1_uuid',
                    'v4-fixed-ip': '',
                    'v6-fixed-ip': '',
                    'port-id': '',
                    'tag': 'foo',
                },
            ],
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

        network_client.find_network.assert_called_once()
        self.app.client_manager.network.find_network.assert_called_once()

    def test_server_create_with_network_tag_pre_v243(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.42')

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'net-id=net1,tag=foo',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nics', [
                {
                    'net-id': 'net1', 'port-id': '',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                    'tag': 'foo',
                },
            ]),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)

    def test_server_create_with_auto_network(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'auto',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nics', ['auto']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='auto',
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

    def test_server_create_with_auto_network_default_v2_37(self):
        """Tests creating a server without specifying --nic using 2.37."""
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

        # Since check_parser doesn't handle compute global options like
        # --os-compute-api-version, we have to mock the construction of
        # the novaclient client object with our own APIVersion.
        with mock.patch.object(self.app.client_manager.compute, 'api_version',
                               api_versions.APIVersion('2.37')):
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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='auto',
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

    def test_server_create_with_none_network(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'none',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nics', ['none']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='none',
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

    def test_server_create_with_conflict_network_options(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'none',
            '--nic', 'auto',
            '--nic', 'port-id=port1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('nics', [
                'none',
                'auto',
                {
                    'net-id': '', 'port-id': 'port1',
                    'v4-fixed-ip': '', 'v6-fixed-ip': '',
                },
            ]),
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

        find_port = mock.Mock()
        network_client = self.app.client_manager.network
        network_client.find_port = find_port
        port_resource = mock.Mock(id='port1_uuid')
        find_port.return_value = port_resource

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)
        self.assertNotCalled(self.servers_mock.create)

    def test_server_create_with_invalid_network_options(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'abcdefgh',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])
        self.assertNotCalled(self.servers_mock.create)

    def test_server_create_with_invalid_network_key(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'abcdefgh=12324',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])
        self.assertNotCalled(self.servers_mock.create)

    def test_server_create_with_empty_network_key_value(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'net-id=',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])
        self.assertNotCalled(self.servers_mock.create)

    def test_server_create_with_only_network_key(self):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--nic', 'net-id',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])

        self.assertNotCalled(self.servers_mock.create)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_create_with_wait_ok(self, mock_wait_for_status):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--wait',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('config_drive', False),
            ('wait', True),
            ('server_name', self.new_server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.new_server.id,
            callback=mock.ANY,
        )

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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics=[],
            scheduler_hints={},
            config_drive=None,
        )
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_create_with_wait_fails(self, mock_wait_for_status):
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--wait',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('config_drive', False),
            ('wait', True),
            ('server_name', self.new_server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.new_server.id,
            callback=mock.ANY,
        )

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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics=[],
            scheduler_hints={},
            config_drive=None,
        )
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

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
            admin_pass=None,
            block_device_mapping_v2=[],
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

    def test_server_create_with_volume(self):
        arglist = [
            '--flavor', self.flavor.id,
            '--volume', self.volume.name,
            self.new_server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('volume', self.volume.name),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'uuid': self.volume.id,
                'boot_index': '0',
                'source_type': 'volume',
                'destination_type': 'volume',
            }],
            'nics': [],
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            None,
            self.flavor,
            **kwargs
        )
        self.volumes_mock.get.assert_called_once_with(
            self.volume.name)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_snapshot(self):
        arglist = [
            '--flavor', self.flavor.id,
            '--snapshot', self.snapshot.name,
            self.new_server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('snapshot', self.snapshot.name),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'uuid': self.snapshot.id,
                'boot_index': '0',
                'source_type': 'snapshot',
                'destination_type': 'volume',
                'delete_on_termination': False,
            }],
            'nics': [],
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            None,
            self.flavor,
            **kwargs
        )
        self.snapshots_mock.get.assert_called_once_with(
            self.snapshot.name)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device(self):
        block_device = f'uuid={self.volume.id},source_type=volume'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_devices', [
                {
                    'uuid': self.volume.id,
                    'source_type': 'volume',
                },
            ]),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'uuid': self.volume.id,
                'source_type': 'volume',
                'destination_type': 'volume',
            }],
            'nics': [],
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_full(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.67')

        block_device = (
            f'uuid={self.volume.id},source_type=volume,'
            f'destination_type=volume,disk_bus=ide,device_type=disk,'
            f'device_name=sdb,guest_format=ext4,volume_size=64,'
            f'volume_type=foo,boot_index=1,delete_on_termination=true,'
            f'tag=foo'
        )

        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_devices', [
                {
                    'uuid': self.volume.id,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                    'disk_bus': 'ide',
                    'device_type': 'disk',
                    'device_name': 'sdb',
                    'guest_format': 'ext4',
                    'volume_size': '64',
                    'volume_type': 'foo',
                    'boot_index': '1',
                    'delete_on_termination': 'true',
                    'tag': 'foo',
                },
            ]),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'uuid': self.volume.id,
                'source_type': 'volume',
                'destination_type': 'volume',
                'disk_bus': 'ide',
                'device_name': 'sdb',
                'volume_size': '64',
                'guest_format': 'ext4',
                'boot_index': 1,
                'device_type': 'disk',
                'delete_on_termination': True,
                'tag': 'foo',
                'volume_type': 'foo',
            }],
            'nics': 'auto',
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_from_file(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.67')

        block_device = {
            'uuid': self.volume.id,
            'source_type': 'volume',
            'destination_type': 'volume',
            'disk_bus': 'ide',
            'device_type': 'disk',
            'device_name': 'sdb',
            'guest_format': 'ext4',
            'volume_size': 64,
            'volume_type': 'foo',
            'boot_index': 1,
            'delete_on_termination': True,
            'tag': 'foo',
        }

        with tempfile.NamedTemporaryFile(mode='w+') as fp:
            json.dump(block_device, fp=fp)
            fp.flush()

            arglist = [
                '--image', 'image1',
                '--flavor', self.flavor.id,
                '--block-device', fp.name,
                self.new_server.name,
            ]
            verifylist = [
                ('image', 'image1'),
                ('flavor', self.flavor.id),
                ('block_devices', [block_device]),
                ('server_name', self.new_server.name),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'uuid': self.volume.id,
                'source_type': 'volume',
                'destination_type': 'volume',
                'disk_bus': 'ide',
                'device_name': 'sdb',
                'volume_size': 64,
                'guest_format': 'ext4',
                'boot_index': 1,
                'device_type': 'disk',
                'delete_on_termination': True,
                'tag': 'foo',
                'volume_type': 'foo',
            }],
            'nics': 'auto',
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_invalid_boot_index(self):
        block_device = \
            f'uuid={self.volume.name},source_type=volume,boot_index=foo'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)
        self.assertIn('The boot_index key of --block-device ', str(ex))

    def test_server_create_with_block_device_invalid_source_type(self):
        block_device = f'uuid={self.volume.name},source_type=foo'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)
        self.assertIn('The source_type key of --block-device ', str(ex))

    def test_server_create_with_block_device_invalid_destination_type(self):
        block_device = \
            f'uuid={self.volume.name},destination_type=foo'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)
        self.assertIn('The destination_type key of --block-device ', str(ex))

    def test_server_create_with_block_device_invalid_shutdown(self):
        block_device = \
            f'uuid={self.volume.name},delete_on_termination=foo'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)
        self.assertIn(
            'The delete_on_termination key of --block-device ', str(ex))

    def test_server_create_with_block_device_tag_pre_v242(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.41')

        block_device = \
            f'uuid={self.volume.name},tag=foo'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.42 or greater is required',
            str(ex))

    def test_server_create_with_block_device_volume_type_pre_v267(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.66')

        block_device = f'uuid={self.volume.name},volume_type=foo'
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device', block_device,
            self.new_server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action, parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.67 or greater is required',
            str(ex))

    def test_server_create_with_block_device_mapping(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', 'vda=' + self.volume.name + ':::false',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [
                {
                    'device_name': 'vda',
                    'uuid': self.volume.name,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                    'delete_on_termination': 'false',
                }
            ]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
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
            admin_pass=None,
            block_device_mapping_v2=[{
                'device_name': 'vda',
                'uuid': self.volume.id,
                'destination_type': 'volume',
                'source_type': 'volume',
                'delete_on_termination': 'false',
            }],
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

    def test_server_create_with_block_device_mapping_min_input(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', 'vdf=' + self.volume.name,
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [
                {
                    'device_name': 'vdf',
                    'uuid': self.volume.name,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                }
            ]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
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
            admin_pass=None,
            block_device_mapping_v2=[{
                'device_name': 'vdf',
                'uuid': self.volume.id,
                'destination_type': 'volume',
                'source_type': 'volume',
            }],
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

    def test_server_create_with_block_device_mapping_default_input(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', 'vdf=' + self.volume.name + ':::',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [
                {
                    'device_name': 'vdf',
                    'uuid': self.volume.name,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                }
            ]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
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
            admin_pass=None,
            block_device_mapping_v2=[{
                'device_name': 'vdf',
                'uuid': self.volume.id,
                'destination_type': 'volume',
                'source_type': 'volume',
            }],
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

    def test_server_create_with_block_device_mapping_full_input(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping',
            'vde=' + self.volume.name + ':volume:3:true',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [
                {
                    'device_name': 'vde',
                    'uuid': self.volume.name,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                    'volume_size': '3',
                    'delete_on_termination': 'true',
                }
            ]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
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
            admin_pass=None,
            block_device_mapping_v2=[{
                'device_name': 'vde',
                'uuid': self.volume.id,
                'destination_type': 'volume',
                'source_type': 'volume',
                'delete_on_termination': 'true',
                'volume_size': '3'
            }],
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

    def test_server_create_with_block_device_mapping_snapshot(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping',
            'vds=' + self.volume.name + ':snapshot:5:true',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [
                {
                    'device_name': 'vds',
                    'uuid': self.volume.name,
                    'source_type': 'snapshot',
                    'volume_size': '5',
                    'destination_type': 'volume',
                    'delete_on_termination': 'true',
                }
            ]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
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
            admin_pass=None,
            block_device_mapping_v2=[{
                'device_name': 'vds',
                'uuid': self.snapshot.id,
                'destination_type': 'volume',
                'source_type': 'snapshot',
                'delete_on_termination': 'true',
                'volume_size': '5'
            }],
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

    def test_server_create_with_block_device_mapping_multiple(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', 'vdb=' + self.volume.name + ':::false',
            '--block-device-mapping', 'vdc=' + self.volume.name + ':::true',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('block_device_mapping', [
                {
                    'device_name': 'vdb',
                    'uuid': self.volume.name,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                    'delete_on_termination': 'false',
                },
                {
                    'device_name': 'vdc',
                    'uuid': self.volume.name,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                    'delete_on_termination': 'true',
                },
            ]),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
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
            admin_pass=None,
            block_device_mapping_v2=[
                {
                    'device_name': 'vdb',
                    'uuid': self.volume.id,
                    'destination_type': 'volume',
                    'source_type': 'volume',
                    'delete_on_termination': 'false',
                },
                {
                    'device_name': 'vdc',
                    'uuid': self.volume.id,
                    'destination_type': 'volume',
                    'source_type': 'volume',
                    'delete_on_termination': 'true',
                }
            ],
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

    def test_server_create_with_block_device_mapping_invalid_format(self):
        # block device mapping don't contain equal sign "="
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', 'not_contain_equal_sign',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])

        # block device mapping don't contain device name "=uuid:::true"
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', '=uuid:::true',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])

    def test_server_create_with_block_device_mapping_no_uuid(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--block-device-mapping', 'vdb=',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])

    def test_server_create_volume_boot_from_volume_conflict(self):
        # Tests that specifying --volume and --boot-from-volume results in
        # an error. Since --boot-from-volume requires --image or
        # --image-property but those are in a mutex group with --volume, we
        # only specify --volume and --boot-from-volume for this test since
        # the validation is not handled with argparse.
        arglist = [
            '--flavor', self.flavor.id,
            '--volume', 'volume1',
            '--boot-from-volume', '1',
            self.new_server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('volume', 'volume1'),
            ('boot_from_volume', 1),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd.take_action, parsed_args)
        # Assert it is the error we expect.
        self.assertIn('--volume is not allowed with --boot-from-volume',
                      str(ex))

    def test_server_create_image_property(self):
        arglist = [
            '--image-property', 'hypervisor_type=qemu',
            '--flavor', 'flavor1',
            '--nic', 'none',
            self.new_server.name,
        ]
        verifylist = [
            ('image_properties', {'hypervisor_type': 'qemu'}),
            ('flavor', 'flavor1'),
            ('nics', ['none']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        # create a image_info as the side_effect of the fake image_list()
        image_info = {
            'hypervisor_type': 'qemu',
        }

        _image = image_fakes.FakeImage.create_one_image(image_info)
        self.images_mock.return_value = [_image]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = dict(
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[],
            userdata=None,
            key_name=None,
            availability_zone=None,
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='none',
            meta=None,
            scheduler_hints={},
            config_drive=None,
        )
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            _image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_image_property_multi(self):
        arglist = [
            '--image-property', 'hypervisor_type=qemu',
            '--image-property', 'hw_disk_bus=ide',
            '--flavor', 'flavor1',
            '--nic', 'none',
            self.new_server.name,
        ]
        verifylist = [
            ('image_properties', {'hypervisor_type': 'qemu',
             'hw_disk_bus': 'ide'}),
            ('flavor', 'flavor1'),
            ('nics', ['none']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        # create a image_info as the side_effect of the fake image_list()
        image_info = {
            'hypervisor_type': 'qemu',
            'hw_disk_bus': 'ide',
        }
        _image = image_fakes.FakeImage.create_one_image(image_info)
        self.images_mock.return_value = [_image]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = dict(
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[],
            userdata=None,
            key_name=None,
            availability_zone=None,
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='none',
            meta=None,
            scheduler_hints={},
            config_drive=None,
        )
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            _image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_image_property_missed(self):
        arglist = [
            '--image-property', 'hypervisor_type=qemu',
            '--image-property', 'hw_disk_bus=virtio',
            '--flavor', 'flavor1',
            '--nic', 'none',
            self.new_server.name,
        ]
        verifylist = [
            ('image_properties', {'hypervisor_type': 'qemu',
             'hw_disk_bus': 'virtio'}),
            ('flavor', 'flavor1'),
            ('nics', ['none']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        # create a image_info as the side_effect of the fake image_list()
        image_info = {
            'hypervisor_type': 'qemu',
            'hw_disk_bus': 'ide',
        }

        _image = image_fakes.FakeImage.create_one_image(image_info)
        self.images_mock.return_value = [_image]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_server_create_image_property_with_image_list(self):
        arglist = [
            '--image-property',
            'owner_specified.openstack.object=image/cirros',
            '--flavor', 'flavor1',
            '--nic', 'none',
            self.new_server.name,
        ]

        verifylist = [
            ('image_properties',
                {'owner_specified.openstack.object': 'image/cirros'}),
            ('flavor', 'flavor1'),
            ('nics', ['none']),
            ('server_name', self.new_server.name),
        ]
        # create a image_info as the side_effect of the fake image_list()
        image_info = {
            'properties': {
                'owner_specified.openstack.object': 'image/cirros'
            }
        }

        target_image = image_fakes.FakeImage.create_one_image(image_info)
        another_image = image_fakes.FakeImage.create_one_image({})
        self.images_mock.return_value = [target_image, another_image]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = dict(
            files={},
            reservation_id=None,
            min_count=1,
            max_count=1,
            security_groups=[],
            userdata=None,
            key_name=None,
            availability_zone=None,
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='none',
            meta=None,
            scheduler_hints={},
            config_drive=None,
        )

        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            target_image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_swap(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--swap', '1024',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('swap', 1024),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'boot_index': -1,
                'source_type': 'blank',
                'destination_type': 'local',
                'guest_format': 'swap',
                'volume_size': 1024,
                'delete_on_termination': True,
            }],
            'nics': [],
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_ephemeral(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--ephemeral', 'size=1024,format=ext4',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', self.flavor.id),
            ('ephemerals', [{'size': '1024', 'format': 'ext4'}]),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # CreateServer.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'admin_pass': None,
            'block_device_mapping_v2': [{
                'boot_index': -1,
                'source_type': 'blank',
                'destination_type': 'local',
                'guest_format': 'ext4',
                'volume_size': '1024',
                'delete_on_termination': True,
            }],
            'nics': [],
            'scheduler_hints': {},
            'config_drive': None,
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_ephemeral_missing_key(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--ephemeral', 'format=ext3',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])

    def test_server_create_with_ephemeral_invalid_key(self):
        arglist = [
            '--image', 'image1',
            '--flavor', self.flavor.id,
            '--ephemeral', 'size=1024,foo=bar',
            self.new_server.name,
        ]
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.check_parser,
            self.cmd, arglist, [])

    def test_server_create_invalid_hint(self):
        # Not a key-value pair
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--hint', 'a0cf03a5-d921-4877-bb5c-86d26cf818e1',
            self.new_server.name,
        ]
        self.assertRaises(argparse.ArgumentTypeError,
                          self.check_parser,
                          self.cmd, arglist, [])

        # Empty key
        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--hint', '=a0cf03a5-d921-4877-bb5c-86d26cf818e1',
            self.new_server.name,
        ]
        self.assertRaises(argparse.ArgumentTypeError,
                          self.check_parser,
                          self.cmd, arglist, [])

    def test_server_create_with_description_api_newer(self):

        # Description is supported for nova api version 2.19 or above
        self.app.client_manager.compute.api_version = 2.19

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--description', 'description1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('description', 'description1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.19):
            # In base command class ShowOne in cliff, abstract method
            # take_action() returns a two-part tuple with a tuple of
            # column names and a tuple of data to be shown.
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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='auto',
            scheduler_hints={},
            config_drive=None,
            description='description1',
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
        self.assertFalse(self.images_mock.called)
        self.assertFalse(self.flavors_mock.called)

    def test_server_create_with_description_api_older(self):

        # Description is not supported for nova api version below 2.19
        self.app.client_manager.compute.api_version = 2.18

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--description', 'description1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('description', 'description1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.19):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)

    def test_server_create_with_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.52')

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--tag', 'tag1',
            '--tag', 'tag2',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('tags', ['tag1', 'tag2']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'meta': None,
            'files': {},
            'reservation_id': None,
            'min_count': 1,
            'max_count': 1,
            'security_groups': [],
            'userdata': None,
            'key_name': None,
            'availability_zone': None,
            'block_device_mapping_v2': [],
            'admin_pass': None,
            'nics': 'auto',
            'scheduler_hints': {},
            'config_drive': None,
            'tags': ['tag1', 'tag2'],
        }
        # ServerManager.create(name, image, flavor, **kwargs)
        self.servers_mock.create.assert_called_with(
            self.new_server.name,
            self.image,
            self.flavor,
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)
        self.assertFalse(self.images_mock.called)
        self.assertFalse(self.flavors_mock.called)

    def test_server_create_with_tag_pre_v252(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.51')

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--tag', 'tag1',
            '--tag', 'tag2',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('tags', ['tag1', 'tag2']),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.52 or greater is required',
            str(ex))

    def test_server_create_with_host_v274(self):

        # Explicit host is supported for nova api version 2.74 or above
        self.app.client_manager.compute.api_version = 2.74

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--host', 'host1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('host', 'host1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.74):
            # In base command class ShowOne in cliff, abstract method
            # take_action() returns a two-part tuple with a tuple of
            # column names and a tuple of data to be shown.
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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='auto',
            scheduler_hints={},
            config_drive=None,
            host='host1',
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
        self.assertFalse(self.images_mock.called)
        self.assertFalse(self.flavors_mock.called)

    def test_server_create_with_host_pre_v274(self):

        # Host is not supported for nova api version below 2.74
        self.app.client_manager.compute.api_version = 2.73

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--host', 'host1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('host', 'host1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.74):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)

    def test_server_create_with_hypervisor_hostname_v274(self):

        # Explicit hypervisor_hostname is supported for nova api version
        # 2.74 or above
        self.app.client_manager.compute.api_version = 2.74

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--hypervisor-hostname', 'node1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('hypervisor_hostname', 'node1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.74):
            # In base command class ShowOne in cliff, abstract method
            # take_action() returns a two-part tuple with a tuple of
            # column names and a tuple of data to be shown.
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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='auto',
            scheduler_hints={},
            config_drive=None,
            hypervisor_hostname='node1',
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
        self.assertFalse(self.images_mock.called)
        self.assertFalse(self.flavors_mock.called)

    def test_server_create_with_hypervisor_hostname_pre_v274(self):

        # Hypervisor_hostname is not supported for nova api version below 2.74
        self.app.client_manager.compute.api_version = 2.73

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--hypervisor-hostname', 'node1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('hypervisor_hostname', 'node1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.74):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)

    def test_server_create_with_host_and_hypervisor_hostname_v274(self):

        # Explicit host and hypervisor_hostname is supported for nova api
        # version 2.74 or above
        self.app.client_manager.compute.api_version = 2.74

        arglist = [
            '--image', 'image1',
            '--flavor', 'flavor1',
            '--host', 'host1',
            '--hypervisor-hostname', 'node1',
            self.new_server.name,
        ]
        verifylist = [
            ('image', 'image1'),
            ('flavor', 'flavor1'),
            ('host', 'host1'),
            ('hypervisor_hostname', 'node1'),
            ('config_drive', False),
            ('server_name', self.new_server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.74):
            # In base command class ShowOne in cliff, abstract method
            # take_action() returns a two-part tuple with a tuple of
            # column names and a tuple of data to be shown.
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
            admin_pass=None,
            block_device_mapping_v2=[],
            nics='auto',
            scheduler_hints={},
            config_drive=None,
            host='host1',
            hypervisor_hostname='node1',
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
        self.assertFalse(self.images_mock.called)
        self.assertFalse(self.flavors_mock.called)


class TestServerDelete(TestServer):

    def setUp(self):
        super(TestServerDelete, self).setUp()

        self.servers_mock.delete.return_value = None
        self.servers_mock.force_delete.return_value = None

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
        self.servers_mock.force_delete.assert_not_called()
        self.assertIsNone(result)

    def test_server_delete_with_force(self):
        servers = self.setup_servers_mock(count=1)

        arglist = [
            servers[0].id,
            '--force',
        ]
        verifylist = [
            ('server', [servers[0].id]),
            ('force', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.force_delete.assert_called_with(servers[0].id)
        self.servers_mock.delete.assert_not_called()
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

    @mock.patch.object(common_utils, 'find_resource')
    def test_server_delete_with_all_projects(self, mock_find_resource):
        servers = self.setup_servers_mock(count=1)
        mock_find_resource.side_effect = compute_fakes.FakeServer.get_servers(
            servers, 0,
        )

        arglist = [
            servers[0].id,
            '--all-projects',
        ]
        verifylist = [
            ('server', [servers[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        mock_find_resource.assert_called_once_with(
            mock.ANY, servers[0].id, all_tenants=True,
        )

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
            callback=mock.ANY,
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
            callback=mock.ANY,
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


class _TestServerList(TestServer):

    # Columns to be listed up.
    columns = (
        'ID',
        'Name',
        'Status',
        'Networks',
        'Image',
        'Flavor',
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
        'Flavor Name',
        'Flavor ID',
        'Availability Zone',
        'Host',
        'Properties',
    )

    def setUp(self):
        super(_TestServerList, self).setUp()

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
            'deleted': False,
            'changes-since': None,
            'changes-before': None,
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
            'Metadata': format_columns.DictColumn({}),
        }

        # The servers to be listed.
        self.servers = self.setup_servers_mock(3)
        self.servers_mock.list.return_value = self.servers

        self.image = image_fakes.FakeImage.create_one_image()

        # self.images_mock.return_value = [self.image]
        self.find_image_mock.return_value = self.image
        self.get_image_mock.return_value = self.image

        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        self.flavors_mock.get.return_value = self.flavor

        # Get the command object to test
        self.cmd = server.ListServer(self.app, None)


class TestServerList(_TestServerList):

    def setUp(self):
        super(TestServerList, self).setUp()

        Image = collections.namedtuple('Image', 'id name')
        self.images_mock.return_value = [
            Image(id=s.image['id'], name=self.image.name)
            # Image will be an empty string if boot-from-volume
            for s in self.servers if s.image
        ]

        Flavor = collections.namedtuple('Flavor', 'id name')
        self.flavors_mock.list.return_value = [
            Flavor(id=s.flavor['id'], name=self.flavor.name)
            for s in self.servers
        ]

        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                format_columns.DictListColumn(s.networks),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
            ) for s in self.servers
        )

    def test_server_list_no_option(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('deleted', False),
            ('name_lookup_one_by_one', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.images_mock.assert_called()
        self.flavors_mock.list.assert_called()
        # we did not pass image or flavor, so gets on those must be absent
        self.assertFalse(self.flavors_mock.get.call_count)
        self.assertFalse(self.get_image_mock.call_count)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_no_servers(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
            ('long', False),
            ('deleted', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.servers_mock.list.return_value = []
        self.data = ()

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(0, self.images_mock.list.call_count)
        self.assertEqual(0, self.flavors_mock.list.call_count)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_long_option(self):
        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                getattr(s, 'OS-EXT-STS:task_state'),
                server.PowerStateColumn(
                    getattr(s, 'OS-EXT-STS:power_state')
                ),
                format_columns.DictListColumn(s.networks),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
                s.flavor['id'],
                getattr(s, 'OS-EXT-AZ:availability_zone'),
                getattr(s, 'OS-EXT-SRV-ATTR:host'),
                s.Metadata,
            ) for s in self.servers)
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
        self.assertEqual(self.data, tuple(data))

    def test_server_list_column_option(self):
        arglist = [
            '-c', 'Project ID',
            '-c', 'User ID',
            '-c', 'Created At',
            '--long'
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertIn('Project ID', columns)
        self.assertIn('User ID', columns)
        self.assertIn('Created At', columns)

    def test_server_list_no_name_lookup_option(self):
        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                format_columns.DictListColumn(s.networks),
                # Image will be an empty string if boot-from-volume
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                s.flavor['id']
            ) for s in self.servers
        )

        arglist = [
            '--no-name-lookup',
        ]
        verifylist = [
            ('all_projects', False),
            ('no_name_lookup', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_n_option(self):
        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                format_columns.DictListColumn(s.networks),
                # Image will be an empty string if boot-from-volume
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                s.flavor['id']
            ) for s in self.servers
        )

        arglist = [
            '-n',
        ]
        verifylist = [
            ('all_projects', False),
            ('no_name_lookup', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_name_lookup_one_by_one(self):
        arglist = [
            '--name-lookup-one-by-one'
        ]
        verifylist = [
            ('all_projects', False),
            ('no_name_lookup', False),
            ('name_lookup_one_by_one', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertFalse(self.images_mock.list.call_count)
        self.assertFalse(self.flavors_mock.list.call_count)
        self.get_image_mock.assert_called()
        self.flavors_mock.get.assert_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_image(self):

        arglist = [
            '--image', self.image.id
        ]
        verifylist = [
            ('image', self.image.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.find_image_mock.assert_called_with(self.image.id,
                                                ignore_missing=False)

        self.search_opts['image'] = self.image.id
        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_flavor(self):

        arglist = [
            '--flavor', self.flavor.id
        ]
        verifylist = [
            ('flavor', self.flavor.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.flavors_mock.get.has_calls(self.flavor.id)

        self.search_opts['flavor'] = self.flavor.id
        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_changes_since(self):

        arglist = [
            '--changes-since', '2016-03-04T06:27:59Z',
            '--deleted'
        ]
        verifylist = [
            ('changes_since', '2016-03-04T06:27:59Z'),
            ('deleted', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['changes-since'] = '2016-03-04T06:27:59Z'
        self.search_opts['deleted'] = True
        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    @mock.patch.object(iso8601, 'parse_date', side_effect=iso8601.ParseError)
    def test_server_list_with_invalid_changes_since(self, mock_parse_isotime):

        arglist = [
            '--changes-since', 'Invalid time value',
        ]
        verifylist = [
            ('changes_since', 'Invalid time value'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('Invalid changes-since value: Invalid time '
                             'value', str(e))
        mock_parse_isotime.assert_called_once_with(
            'Invalid time value'
        )

    def test_server_list_with_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.26')

        arglist = [
            '--tag', 'tag1',
            '--tag', 'tag2',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['tags'] = 'tag1,tag2'

        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_tag_pre_v225(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.25')

        arglist = [
            '--tag', 'tag1',
            '--tag', 'tag2',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required',
            str(ex))

    def test_server_list_with_not_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.26')

        arglist = [
            '--not-tag', 'tag1',
            '--not-tag', 'tag2',
        ]
        verifylist = [
            ('not_tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['not-tags'] = 'tag1,tag2'

        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_not_tag_pre_v226(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.25')

        arglist = [
            '--not-tag', 'tag1',
            '--not-tag', 'tag2',
        ]
        verifylist = [
            ('not_tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required',
            str(ex))

    def test_server_list_with_availability_zone(self):
        arglist = [
            '--availability-zone', 'test-az',
        ]
        verifylist = [
            ('availability_zone', 'test-az'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['availability_zone'] = 'test-az'
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_key_name(self):
        arglist = [
            '--key-name', 'test-key',
        ]
        verifylist = [
            ('key_name', 'test-key'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['key_name'] = 'test-key'
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_config_drive(self):
        arglist = [
            '--config-drive',
        ]
        verifylist = [
            ('has_config_drive', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['config_drive'] = True
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_no_config_drive(self):
        arglist = [
            '--no-config-drive',
        ]
        verifylist = [
            ('has_config_drive', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['config_drive'] = False
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_progress(self):
        arglist = [
            '--progress', '100',
        ]
        verifylist = [
            ('progress', 100),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['progress'] = '100'
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_progress_invalid(self):
        arglist = [
            '--progress', '101',
        ]

        self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verify_args=[])

    def test_server_list_with_vm_state(self):
        arglist = [
            '--vm-state', 'active',
        ]
        verifylist = [
            ('vm_state', 'active'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['vm_state'] = 'active'
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_task_state(self):
        arglist = [
            '--task-state', 'deleting',
        ]
        verifylist = [
            ('task_state', 'deleting'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['task_state'] = 'deleting'
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_power_state(self):
        arglist = [
            '--power-state', 'running',
        ]
        verifylist = [
            ('power_state', 'running'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['power_state'] = 1
        self.servers_mock.list.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestServerListV273(_TestServerList):

    # Columns to be listed up.
    columns = (
        'ID',
        'Name',
        'Status',
        'Networks',
        'Image',
        'Flavor',
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
        'Flavor',
        'Availability Zone',
        'Host',
        'Properties',
    )

    def setUp(self):
        super(TestServerListV273, self).setUp()

        # The fake servers' attributes. Use the original attributes names in
        # nova, not the ones printed by "server list" command.
        self.attrs['flavor'] = {
            'vcpus': self.flavor.vcpus,
            'ram': self.flavor.ram,
            'disk': self.flavor.disk,
            'ephemeral': self.flavor.ephemeral,
            'swap': self.flavor.swap,
            'original_name': self.flavor.name,
            'extra_specs': self.flavor.extra_specs,
        }

        # The servers to be listed.
        self.servers = self.setup_servers_mock(3)
        self.servers_mock.list.return_value = self.servers

        Image = collections.namedtuple('Image', 'id name')
        self.images_mock.return_value = [
            Image(id=s.image['id'], name=self.image.name)
            # Image will be an empty string if boot-from-volume
            for s in self.servers if s.image
        ]

        # The flavor information is embedded, so now reason for this to be
        # called
        self.flavors_mock.list = mock.NonCallableMock()

        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                format_columns.DictListColumn(s.networks),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
            ) for s in self.servers)

    def test_server_list_with_locked_pre_v273(self):

        arglist = [
            '--locked'
        ]
        verifylist = [
            ('locked', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd.take_action,
                               parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.73 or greater is required', str(ex))

    def test_server_list_with_locked(self):

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.73')
        arglist = [
            '--locked'
        ]
        verifylist = [
            ('locked', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['locked'] = True
        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertItemsEqual(self.columns, columns)
        self.assertItemsEqual(self.data, tuple(data))

    def test_server_list_with_unlocked_v273(self):

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.73')
        arglist = [
            '--unlocked'
        ]
        verifylist = [
            ('unlocked', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['locked'] = False
        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertItemsEqual(self.columns, columns)
        self.assertItemsEqual(self.data, tuple(data))

    def test_server_list_with_locked_and_unlocked(self):

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.73')
        arglist = [
            '--locked',
            '--unlocked'
        ]
        verifylist = [
            ('locked', True),
            ('unlocked', True)
        ]

        ex = self.assertRaises(
            utils.ParserException,
            self.check_parser, self.cmd, arglist, verifylist)
        self.assertIn('Argument parse failed', str(ex))

    def test_server_list_with_changes_before(self):
        self.app.client_manager.compute.api_version = (
            api_versions.APIVersion('2.66'))
        arglist = [
            '--changes-before', '2016-03-05T06:27:59Z',
            '--deleted'
        ]
        verifylist = [
            ('changes_before', '2016-03-05T06:27:59Z'),
            ('deleted', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.search_opts['changes-before'] = '2016-03-05T06:27:59Z'
        self.search_opts['deleted'] = True

        self.servers_mock.list.assert_called_with(**self.kwargs)

        self.assertItemsEqual(self.columns, columns)
        self.assertItemsEqual(self.data, tuple(data))

    @mock.patch.object(iso8601, 'parse_date', side_effect=iso8601.ParseError)
    def test_server_list_with_invalid_changes_before(
            self, mock_parse_isotime):
        self.app.client_manager.compute.api_version = (
            api_versions.APIVersion('2.66'))

        arglist = [
            '--changes-before', 'Invalid time value',
        ]
        verifylist = [
            ('changes_before', 'Invalid time value'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('Invalid changes-before value: Invalid time '
                             'value', str(e))
        mock_parse_isotime.assert_called_once_with(
            'Invalid time value'
        )

    def test_server_with_changes_before_pre_v266(self):
        self.app.client_manager.compute.api_version = (
            api_versions.APIVersion('2.65'))

        arglist = [
            '--changes-before', '2016-03-05T06:27:59Z',
            '--deleted'
        ]
        verifylist = [
            ('changes_before', '2016-03-05T06:27:59Z'),
            ('deleted', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_server_list_v269_with_partial_constructs(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.69')
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        # include "partial results" from non-responsive part of
        # infrastructure.
        server_dict = {
            "id": "server-id-95a56bfc4xxxxxx28d7e418bfd97813a",
            "status": "UNKNOWN",
            "tenant_id": "6f70656e737461636b20342065766572",
            "created": "2018-12-03T21:06:18Z",
            "links": [
                {
                    "href": "http://fake/v2.1/",
                    "rel": "self"
                },
                {
                    "href": "http://fake",
                    "rel": "bookmark"
                }
            ],
            # We need to pass networks as {} because its defined as a property
            # of the novaclient Server class which gives {} by default. If not
            # it will fail at formatting the networks info later on.
            "networks": {}
        }
        server = compute_fakes.fakes.FakeResource(
            info=server_dict,
        )
        self.servers.append(server)
        columns, data = self.cmd.take_action(parsed_args)
        # get the first three servers out since our interest is in the partial
        # server.
        next(data)
        next(data)
        next(data)
        partial_server = next(data)
        expected_row = (
            'server-id-95a56bfc4xxxxxx28d7e418bfd97813a', '',
            'UNKNOWN', format_columns.DictListColumn({}), '', '')
        self.assertEqual(expected_row, partial_server)


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

    def test_server_lock_with_reason(self):
        server = compute_fakes.FakeServer.create_one_server()
        arglist = [
            server.id,
            '--reason', "blah",
        ]
        verifylist = [
            ('reason', "blah"),
            ('server', [server.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd.take_action,
                               parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.73 or greater is required', str(ex))


class TestServerLockV273(TestServerLock):

    def setUp(self):
        super(TestServerLockV273, self).setUp()

        self.server = compute_fakes.FakeServer.create_one_server(
            methods=self.methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.73')

        # Get the command object to test
        self.cmd = server.LockServer(self.app, None)

    def test_server_lock_with_reason(self):
        arglist = [
            self.server.id,
            '--reason', "blah",
        ]
        verifylist = [
            ('reason', "blah"),
            ('server', [self.server.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.lock.assert_called_with(reason="blah")

    def test_server_lock_multi_servers_with_reason(self):
        server2 = compute_fakes.FakeServer.create_one_server(
            methods=self.methods)
        arglist = [
            self.server.id, server2.id,
            '--reason', "choo..choo",
        ]
        verifylist = [
            ('reason', "choo..choo"),
            ('server', [self.server.id, server2.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertEqual(2, self.servers_mock.get.call_count)
        self.server.lock.assert_called_with(reason="choo..choo")
        self.assertEqual(2, self.server.lock.call_count)


class TestServerMigrate(TestServer):

    def setUp(self):
        super(TestServerMigrate, self).setUp()

        methods = {
            'migrate': None,
            'live_migrate': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.migrate.return_value = None
        self.servers_mock.live_migrate.return_value = None

        # Get the command object to test
        self.cmd = server.MigrateServer(self.app, None)

    def test_server_migrate_no_options(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.migrate.assert_called_with()
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertIsNone(result)

    def test_server_migrate_with_host_2_56(self):
        # Tests that --host is allowed for a cold migration
        # for microversion 2.56 and greater.
        arglist = [
            '--host', 'fakehost', self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.56')

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.migrate.assert_called_with(host='fakehost')
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertIsNone(result)

    def test_server_migrate_with_block_migration(self):
        arglist = [
            '--block-migration', self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', True),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertNotCalled(self.servers_mock.migrate)

    def test_server_migrate_with_disk_overcommit(self):
        arglist = [
            '--disk-overcommit', self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', True),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertNotCalled(self.servers_mock.migrate)

    def test_server_migrate_with_host_pre_2_56(self):
        # Tests that --host is not allowed for a cold migration
        # before microversion 2.56 (the test defaults to 2.1).
        arglist = [
            '--host', 'fakehost', self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                               parsed_args)

        # Make sure it's the error we expect.
        self.assertIn('--os-compute-api-version 2.56 or greater is required '
                      'to use --host without --live-migration.',
                      str(ex))

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertNotCalled(self.servers_mock.migrate)

    def test_server_live_migrate(self):
        # Tests the --live-migration option without --host or --live.
        arglist = [
            '--live-migration', self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('host', None),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.live_migrate.assert_called_with(
            block_migration=False,
            disk_over_commit=False,
            host=None)
        self.assertNotCalled(self.servers_mock.migrate)
        self.assertIsNone(result)

    def test_server_live_migrate_with_host(self):
        # This requires --os-compute-api-version >= 2.30 so the test uses 2.30.
        arglist = [
            '--live-migration', '--host', 'fakehost', self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.30')

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        # No disk_overcommit and block_migration defaults to auto with
        # microversion >= 2.25
        self.server.live_migrate.assert_called_with(
            block_migration='auto', host='fakehost')
        self.assertNotCalled(self.servers_mock.migrate)
        self.assertIsNone(result)

    def test_server_live_migrate_with_host_pre_v230(self):
        # Tests that the --host option is not supported for --live-migration
        # before microversion 2.30 (the test defaults to 2.1).
        arglist = [
            '--live-migration', '--host', 'fakehost', self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action,
            parsed_args)

        # Make sure it's the error we expect.
        self.assertIn(
            '--os-compute-api-version 2.30 or greater is required '
            'when using --host', str(ex))

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertNotCalled(self.servers_mock.migrate)

    def test_server_block_live_migrate(self):
        arglist = [
            '--live-migration',
            '--block-migration',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('block_migration', True),
            ('disk_overcommit', False),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.24')

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.live_migrate.assert_called_with(
            block_migration=True,
            disk_over_commit=False,
            host=None)
        self.assertNotCalled(self.servers_mock.migrate)
        self.assertIsNone(result)

    def test_server_live_migrate_with_disk_overcommit(self):
        arglist = [
            '--live-migration',
            '--disk-overcommit',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('block_migration', None),
            ('disk_overcommit', True),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.24')

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.live_migrate.assert_called_with(
            block_migration=False,
            disk_over_commit=True,
            host=None)
        self.assertNotCalled(self.servers_mock.migrate)
        self.assertIsNone(result)

    def test_server_live_migrate_with_disk_overcommit_post_v224(self):
        arglist = [
            '--live-migration',
            '--disk-overcommit',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('block_migration', None),
            ('disk_overcommit', True),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.25')

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        # There should be no 'disk_over_commit' value present
        self.server.live_migrate.assert_called_with(
            block_migration='auto',
            host=None)
        self.assertNotCalled(self.servers_mock.migrate)
        self.assertIsNone(result)
        # A warning should have been logged for using --disk-overcommit.
        mock_warning.assert_called_once()
        self.assertIn(
            'The --disk-overcommit and --no-disk-overcommit options ',
            str(mock_warning.call_args[0][0]))

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_migrate_with_wait(self, mock_wait_for_status):
        arglist = [
            '--wait', self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.migrate.assert_called_with()
        self.assertNotCalled(self.servers_mock.live_migrate)
        self.assertIsNone(result)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_migrate_with_wait_fails(self, mock_wait_for_status):
        arglist = [
            '--wait', self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', False),
            ('wait', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(SystemExit, self.cmd.take_action, parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.migrate.assert_called_with()
        self.assertNotCalled(self.servers_mock.live_migrate)


class TestListMigration(TestServer):
    """Test fetch all migrations."""

    MIGRATION_COLUMNS = [
        'Source Node', 'Dest Node', 'Source Compute',
        'Dest Compute', 'Dest Host', 'Status', 'Server UUID',
        'Old Flavor', 'New Flavor', 'Created At', 'Updated At'
    ]

    # These are the fields that come back in the response from the REST API.
    MIGRATION_FIELDS = [
        'source_node', 'dest_node', 'source_compute', 'dest_compute',
        'dest_host', 'status', 'instance_uuid', 'old_instance_type_id',
        'new_instance_type_id', 'created_at', 'updated_at'
    ]

    def setUp(self):
        super(TestListMigration, self).setUp()

        self.server = compute_fakes.FakeServer.create_one_server()
        self.servers_mock.get.return_value = self.server

        self.migrations = compute_fakes.FakeMigration.create_migrations(
            count=3)
        self.migrations_mock.list.return_value = self.migrations

        self.data = (common_utils.get_item_properties(
            s, self.MIGRATION_FIELDS) for s in self.migrations)

        # Get the command object to test
        self.cmd = server.ListMigration(self.app, None)

    def test_server_migration_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': None,
            'host': None,
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_migration_list(self):
        arglist = [
            '--server', 'server1',
            '--host', 'host1',
            '--status', 'migrating',
            '--type', 'cold-migration',
        ]
        verifylist = [
            ('server', 'server1'),
            ('host', 'host1'),
            ('status', 'migrating'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'host': 'host1',
            'instance_uuid': self.server.id,
            'migration_type': 'migration',
        }

        self.servers_mock.get.assert_called_with('server1')
        self.migrations_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestListMigrationV223(TestListMigration):
    """Test fetch all migrations. """

    MIGRATION_COLUMNS = [
        'Id', 'Source Node', 'Dest Node', 'Source Compute', 'Dest Compute',
        'Dest Host', 'Status', 'Server UUID', 'Old Flavor', 'New Flavor',
        'Type', 'Created At', 'Updated At'
    ]

    # These are the fields that come back in the response from the REST API.
    MIGRATION_FIELDS = [
        'id', 'source_node', 'dest_node', 'source_compute', 'dest_compute',
        'dest_host', 'status', 'instance_uuid', 'old_instance_type_id',
        'new_instance_type_id', 'migration_type', 'created_at', 'updated_at'
    ]

    def setUp(self):
        super(TestListMigrationV223, self).setUp()

        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.23')

    def test_server_migration_list(self):
        arglist = [
            '--status', 'migrating'
        ]
        verifylist = [
            ('status', 'migrating')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'host': None,
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestListMigrationV259(TestListMigration):
    """Test fetch all migrations. """

    MIGRATION_COLUMNS = [
        'Id', 'UUID', 'Source Node', 'Dest Node', 'Source Compute',
        'Dest Compute', 'Dest Host', 'Status', 'Server UUID',
        'Old Flavor', 'New Flavor', 'Type', 'Created At', 'Updated At'
    ]

    # These are the fields that come back in the response from the REST API.
    MIGRATION_FIELDS = [
        'id', 'uuid', 'source_node', 'dest_node', 'source_compute',
        'dest_compute', 'dest_host', 'status', 'instance_uuid',
        'old_instance_type_id', 'new_instance_type_id', 'migration_type',
        'created_at', 'updated_at'
    ]

    def setUp(self):
        super(TestListMigrationV259, self).setUp()

        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.59')

    def test_server_migration_list(self):
        arglist = [
            '--status', 'migrating',
            '--limit', '1',
            '--marker', 'test_kp',
            '--changes-since', '2019-08-09T08:03:25Z'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-09T08:03:25Z')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'marker': 'test_kp',
            'host': None,
            'changes_since': '2019-08-09T08:03:25Z',
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_migration_list_with_limit_pre_v259(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.58')
        arglist = [
            '--status', 'migrating',
            '--limit', '1'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required',
            str(ex))

    def test_server_migration_list_with_marker_pre_v259(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.58')
        arglist = [
            '--status', 'migrating',
            '--marker', 'test_kp'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('marker', 'test_kp')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required',
            str(ex))

    def test_server_migration_list_with_changes_since_pre_v259(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.58')
        arglist = [
            '--status', 'migrating',
            '--changes-since', '2019-08-09T08:03:25Z'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_since', '2019-08-09T08:03:25Z')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required',
            str(ex))


class TestListMigrationV266(TestListMigration):
    """Test fetch all migrations by changes-before. """

    MIGRATION_COLUMNS = [
        'Id', 'UUID', 'Source Node', 'Dest Node', 'Source Compute',
        'Dest Compute', 'Dest Host', 'Status', 'Server UUID',
        'Old Flavor', 'New Flavor', 'Type', 'Created At', 'Updated At'
    ]

    # These are the fields that come back in the response from the REST API.
    MIGRATION_FIELDS = [
        'id', 'uuid', 'source_node', 'dest_node', 'source_compute',
        'dest_compute', 'dest_host', 'status', 'instance_uuid',
        'old_instance_type_id', 'new_instance_type_id', 'migration_type',
        'created_at', 'updated_at'
    ]

    def setUp(self):
        super(TestListMigrationV266, self).setUp()

        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.66')

    def test_server_migration_list_with_changes_before(self):
        arglist = [
            '--status', 'migrating',
            '--limit', '1',
            '--marker', 'test_kp',
            '--changes-since', '2019-08-07T08:03:25Z',
            '--changes-before', '2019-08-09T08:03:25Z'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'marker': 'test_kp',
            'host': None,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': '2019-08-09T08:03:25Z',
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_migration_list_with_changes_before_pre_v266(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.65')
        arglist = [
            '--status', 'migrating',
            '--changes-before', '2019-08-09T08:03:25Z'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.66 or greater is required',
            str(ex))


class TestListMigrationV280(TestListMigration):
    """Test fetch all migrations by user-id and/or project-id. """

    MIGRATION_COLUMNS = [
        'Id', 'UUID', 'Source Node', 'Dest Node', 'Source Compute',
        'Dest Compute', 'Dest Host', 'Status', 'Server UUID',
        'Old Flavor', 'New Flavor', 'Type', 'Created At', 'Updated At'
    ]

    # These are the fields that come back in the response from the REST API.
    MIGRATION_FIELDS = [
        'id', 'uuid', 'source_node', 'dest_node', 'source_compute',
        'dest_compute', 'dest_host', 'status', 'instance_uuid',
        'old_instance_type_id', 'new_instance_type_id', 'migration_type',
        'created_at', 'updated_at'
    ]

    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super(TestListMigrationV280, self).setUp()

        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()

        self.users_mock = self.app.client_manager.identity.users
        self.users_mock.reset_mock()

        self.projects_mock.get.return_value = self.project
        self.users_mock.get.return_value = self.user

        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.80')

    def test_server_migration_list_with_project(self):
        arglist = [
            '--status', 'migrating',
            '--limit', '1',
            '--marker', 'test_kp',
            '--changes-since', '2019-08-07T08:03:25Z',
            '--changes-before', '2019-08-09T08:03:25Z',
            '--project', self.project.id
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', self.project.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'marker': 'test_kp',
            'host': None,
            'project_id': self.project.id,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': "2019-08-09T08:03:25Z",
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.MIGRATION_COLUMNS.insert(
            len(self.MIGRATION_COLUMNS) - 2, "Project")
        self.MIGRATION_FIELDS.insert(
            len(self.MIGRATION_FIELDS) - 2, "project_id")
        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))
        # Clean up global variables MIGRATION_COLUMNS
        self.MIGRATION_COLUMNS.remove('Project')
        # Clean up global variables MIGRATION_FIELDS
        self.MIGRATION_FIELDS.remove('project_id')

    def test_get_migrations_with_project_pre_v280(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.79')
        arglist = [
            '--status', 'migrating',
            '--changes-before', '2019-08-09T08:03:25Z',
            '--project', '0c2accde-644a-45fa-8c10-e76debc7fbc3'
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', '0c2accde-644a-45fa-8c10-e76debc7fbc3')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.80 or greater is required',
            str(ex))

    def test_server_migration_list_with_user(self):
        arglist = [
            '--status', 'migrating',
            '--limit', '1',
            '--marker', 'test_kp',
            '--changes-since', '2019-08-07T08:03:25Z',
            '--changes-before', '2019-08-09T08:03:25Z',
            '--user', self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'marker': 'test_kp',
            'host': None,
            'user_id': self.user.id,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': "2019-08-09T08:03:25Z",
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.MIGRATION_COLUMNS.insert(
            len(self.MIGRATION_COLUMNS) - 2, "User")
        self.MIGRATION_FIELDS.insert(
            len(self.MIGRATION_FIELDS) - 2, "user_id")
        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))
        # Clean up global variables MIGRATION_COLUMNS
        self.MIGRATION_COLUMNS.remove('User')
        # Clean up global variables MIGRATION_FIELDS
        self.MIGRATION_FIELDS.remove('user_id')

    def test_get_migrations_with_user_pre_v280(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.79')
        arglist = [
            '--status', 'migrating',
            '--changes-before', '2019-08-09T08:03:25Z',
            '--user', self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.80 or greater is required',
            str(ex))

    def test_server_migration_list_with_project_and_user(self):
        arglist = [
            '--status', 'migrating',
            '--limit', '1',
            '--changes-since', '2019-08-07T08:03:25Z',
            '--changes-before', '2019-08-09T08:03:25Z',
            '--project', self.project.id,
            '--user', self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', self.project.id),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'host': None,
            'project_id': self.project.id,
            'user_id': self.user.id,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': "2019-08-09T08:03:25Z",
        }

        self.migrations_mock.list.assert_called_with(**kwargs)

        self.MIGRATION_COLUMNS.insert(
            len(self.MIGRATION_COLUMNS) - 2, "Project")
        self.MIGRATION_FIELDS.insert(
            len(self.MIGRATION_FIELDS) - 2, "project_id")
        self.MIGRATION_COLUMNS.insert(
            len(self.MIGRATION_COLUMNS) - 2, "User")
        self.MIGRATION_FIELDS.insert(
            len(self.MIGRATION_FIELDS) - 2, "user_id")
        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))
        # Clean up global variables MIGRATION_COLUMNS
        self.MIGRATION_COLUMNS.remove('Project')
        self.MIGRATION_FIELDS.remove('project_id')
        self.MIGRATION_COLUMNS.remove('User')
        self.MIGRATION_FIELDS.remove('user_id')

    def test_get_migrations_with_project_and_user_pre_v280(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.79')
        arglist = [
            '--status', 'migrating',
            '--changes-before', '2019-08-09T08:03:25Z',
            '--project', self.project.id,
            '--user', self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', self.project.id),
            ('user', self.user.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.80 or greater is required',
            str(ex))


class TestServerMigrationShow(TestServer):

    def setUp(self):
        super().setUp()

        self.server = compute_fakes.FakeServer.create_one_server()
        self.servers_mock.get.return_value = self.server

        self.server_migration = compute_fakes.FakeServerMigration\
            .create_one_server_migration()
        self.server_migrations_mock.get.return_value = self.server_migration

        self.columns = (
            'ID',
            'Server UUID',
            'Status',
            'Source Compute',
            'Source Node',
            'Dest Compute',
            'Dest Host',
            'Dest Node',
            'Memory Total Bytes',
            'Memory Processed Bytes',
            'Memory Remaining Bytes',
            'Disk Total Bytes',
            'Disk Processed Bytes',
            'Disk Remaining Bytes',
            'Created At',
            'Updated At',
        )

        self.data = (
            self.server_migration.id,
            self.server_migration.server_uuid,
            self.server_migration.status,
            self.server_migration.source_compute,
            self.server_migration.source_node,
            self.server_migration.dest_compute,
            self.server_migration.dest_host,
            self.server_migration.dest_node,
            self.server_migration.memory_total_bytes,
            self.server_migration.memory_processed_bytes,
            self.server_migration.memory_remaining_bytes,
            self.server_migration.disk_total_bytes,
            self.server_migration.disk_processed_bytes,
            self.server_migration.disk_remaining_bytes,
            self.server_migration.created_at,
            self.server_migration.updated_at,
        )

        # Get the command object to test
        self.cmd = server.ShowMigration(self.app, None)

    def _test_server_migration_show(self):
        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server_migrations_mock.get.assert_called_with(
            self.server.id, '2',)

    def test_server_migration_show(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.24')

        self._test_server_migration_show()

    def test_server_migration_show_v259(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.59')

        self.columns += ('UUID',)
        self.data += (self.server_migration.uuid,)

        self._test_server_migration_show()

    def test_server_migration_show_v280(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.80')

        self.columns += ('UUID', 'User ID', 'Project ID')
        self.data += (
            self.server_migration.uuid,
            self.server_migration.user_id,
            self.server_migration.project_id,
        )

        self._test_server_migration_show()

    def test_server_migration_show_pre_v224(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.23')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.24 or greater is required',
            str(ex))


class TestServerMigrationAbort(TestServer):

    def setUp(self):
        super(TestServerMigrationAbort, self).setUp()

        self.server = compute_fakes.FakeServer.create_one_server()

        # Return value for utils.find_resource for server.
        self.servers_mock.get.return_value = self.server

        # Get the command object to test
        self.cmd = server.AbortMigration(self.app, None)

    def test_migration_abort(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.24')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server_migrations_mock.live_migration_abort.assert_called_with(
            self.server.id, '2',)
        self.assertIsNone(result)

    def test_migration_abort_pre_v224(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.23')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.24 or greater is required',
            str(ex))


class TestServerMigrationForceComplete(TestServer):

    def setUp(self):
        super(TestServerMigrationForceComplete, self).setUp()

        self.server = compute_fakes.FakeServer.create_one_server()

        # Return value for utils.find_resource for server.
        self.servers_mock.get.return_value = self.server

        # Get the command object to test
        self.cmd = server.ForceCompleteMigration(self.app, None)

    def test_migration_force_complete(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.22')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server_migrations_mock.live_migrate_force_complete\
            .assert_called_with(self.server.id, '2',)
        self.assertIsNone(result)

    def test_migration_force_complete_pre_v222(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.21')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.22 or greater is required',
            str(ex))


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
        self.get_image_mock.return_value = self.image

        # Fake the rebuilt new server.
        attrs = {
            'image': {
                'id': self.image.id
            },
            'networks': {},
            'adminPass': 'passw0rd',
        }
        new_server = compute_fakes.FakeServer.create_one_server(attrs=attrs)

        # Fake the server to be rebuilt. The IDs of them should be the same.
        attrs['id'] = new_server.id
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

    def test_rebuild_with_image_name(self):
        image_name = 'my-custom-image'
        user_image = image_fakes.FakeImage.create_one_image(
            attrs={'name': image_name})
        self.find_image_mock.return_value = user_image

        attrs = {
            'image': {
                'id': user_image.id
            },
            'networks': {},
            'adminPass': 'passw0rd',
        }
        new_server = compute_fakes.FakeServer.create_one_server(attrs=attrs)
        self.server.rebuild.return_value = new_server

        arglist = [
            self.server.id,
            '--image', image_name
        ]
        verifylist = [
            ('server', self.server.id),
            ('image', image_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test.
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.find_image_mock.assert_called_with(
            image_name, ignore_missing=False)
        self.get_image_mock.assert_called_with(user_image.id)
        self.server.rebuild.assert_called_with(user_image, None)

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
        self.find_image_mock.assert_not_called()
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None)

    def test_rebuild_with_volume_backed_server_no_image(self):
        # the volume-backed server will have the image attribute set to an
        # empty string, not null/None
        self.server.image = ''

        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn('The --image option is required', str(exc))

    def test_rebuild_with_name(self):
        name = 'test-server-xxx'
        arglist = [
            self.server.id,
            '--name', name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('name', name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None, name=name)

    def test_rebuild_with_preserve_ephemeral(self):
        arglist = [
            self.server.id,
            '--preserve-ephemeral',
        ]
        verifylist = [
            ('server', self.server.id),
            ('preserve_ephemeral', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, preserve_ephemeral=True)

    def test_rebuild_with_no_preserve_ephemeral(self):
        arglist = [
            self.server.id,
            '--no-preserve-ephemeral',
        ]
        verifylist = [
            ('server', self.server.id),
            ('preserve_ephemeral', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, preserve_ephemeral=False)

    def test_rebuild_with_password(self):
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
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, password)

    def test_rebuild_with_description(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.19')

        description = 'description1'
        arglist = [
            self.server.id,
            '--description', description
        ]
        verifylist = [
            ('server', self.server.id),
            ('description', description)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None,
                                               description=description)

    def test_rebuild_with_description_pre_v219(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.18')

        description = 'description1'
        arglist = [
            self.server.id,
            '--description', description
        ]
        verifylist = [
            ('server', self.server.id),
            ('description', description)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

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
            callback=mock.ANY,
            # **kwargs
        )

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
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
            callback=mock.ANY,
        )

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(self.image, None)

    def test_rebuild_with_property(self):
        arglist = [
            self.server.id,
            '--property', 'key1=value1',
            '--property', 'key2=value2'
        ]
        expected_properties = {'key1': 'value1', 'key2': 'value2'}
        verifylist = [
            ('server', self.server.id),
            ('properties', expected_properties)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, meta=expected_properties)

    def test_rebuild_with_keypair_name(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.54')

        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--key-name', self.server.key_name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('key_name', self.server.key_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, key_name=self.server.key_name)

    def test_rebuild_with_keypair_name_pre_v254(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.53')

        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--key-name', self.server.key_name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('key_name', self.server.key_name)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

    def test_rebuild_with_no_keypair_name(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.54')

        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--no-key-name',
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, key_name=None)

    def test_rebuild_with_keypair_name_and_unset(self):
        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--key-name', self.server.key_name,
            '--no-key-name',
        ]
        verifylist = [
            ('server', self.server.id),
            ('key_name', self.server.key_name)
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser,
            self.cmd, arglist, verifylist)

    @mock.patch('openstackclient.compute.v2.server.io.open')
    def test_rebuild_with_user_data(self, mock_open):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.57')

        mock_file = mock.Mock(name='File')
        mock_open.return_value = mock_file
        mock_open.read.return_value = '#!/bin/sh'

        arglist = [
            self.server.id,
            '--user-data', 'userdata.sh',
        ]
        verifylist = [
            ('server', self.server.id),
            ('user_data', 'userdata.sh'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Ensure the userdata file is opened
        mock_open.assert_called_with('userdata.sh')

        # Ensure the userdata file is closed
        mock_file.close.assert_called_with()

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None,
            userdata=mock_file,)

    def test_rebuild_with_user_data_pre_257(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.56')

        arglist = [
            self.server.id,
            '--user-data', 'userdata.sh',
        ]
        verifylist = [
            ('server', self.server.id),
            ('user_data', 'userdata.sh'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

    def test_rebuild_with_no_user_data(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.54')

        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--no-user-data',
        ]
        verifylist = [
            ('server', self.server.id),
            ('no_user_data', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, userdata=None)

    def test_rebuild_with_no_user_data_pre_254(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.53')

        arglist = [
            self.server.id,
            '--no-user-data',
        ]
        verifylist = [
            ('server', self.server.id),
            ('no_user_data', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

    def test_rebuild_with_user_data_and_unset(self):
        arglist = [
            self.server.id,
            '--user-data', 'userdata.sh',
            '--no-user-data',
        ]
        self.assertRaises(
            utils.ParserException,
            self.check_parser,
            self.cmd, arglist, None)

    def test_rebuild_with_trusted_image_cert(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.63')

        arglist = [
            self.server.id,
            '--trusted-image-cert', 'foo',
            '--trusted-image-cert', 'bar',
        ]
        verifylist = [
            ('server', self.server.id),
            ('trusted_image_certs', ['foo', 'bar']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, trusted_image_certificates=['foo', 'bar'])

    def test_rebuild_with_trusted_image_cert_pre_v263(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.62')

        arglist = [
            self.server.id,
            '--trusted-image-cert', 'foo',
            '--trusted-image-cert', 'bar',
        ]
        verifylist = [
            ('server', self.server.id),
            ('trusted_image_certs', ['foo', 'bar']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

    def test_rebuild_with_no_trusted_image_cert(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.63')

        arglist = [
            self.server.id,
            '--no-trusted-image-certs',
        ]
        verifylist = [
            ('server', self.server.id),
            ('no_trusted_image_certs', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.servers_mock.get.assert_called_with(self.server.id)
        self.get_image_mock.assert_called_with(self.image.id)
        self.server.rebuild.assert_called_with(
            self.image, None, trusted_image_certificates=None)

    def test_rebuild_with_no_trusted_image_cert_pre_257(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.62')

        arglist = [
            self.server.id,
            '--no-trusted-image-certs',
        ]
        verifylist = [
            ('server', self.server.id),
            ('no_trusted_image_certs', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)


class TestEvacuateServer(TestServer):

    def setUp(self):
        super(TestEvacuateServer, self).setUp()
        # Return value for utils.find_resource for image
        self.image = image_fakes.FakeImage.create_one_image()
        self.images_mock.get.return_value = self.image

        # Fake the rebuilt new server.
        attrs = {
            'image': {
                'id': self.image.id
            },
            'networks': {},
            'adminPass': 'passw0rd',
        }
        new_server = compute_fakes.FakeServer.create_one_server(attrs=attrs)

        # Fake the server to be rebuilt. The IDs of them should be the same.
        attrs['id'] = new_server.id
        methods = {
            'evacuate': new_server,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=attrs,
            methods=methods
        )

        # Return value for utils.find_resource for server.
        self.servers_mock.get.return_value = self.server

        self.cmd = server.EvacuateServer(self.app, None)

    def _test_evacuate(self, args, verify_args, evac_args):
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.evacuate.assert_called_with(**evac_args)

    def test_evacuate(self):
        args = [
            self.server.id,
        ]
        verify_args = [
            ('server', self.server.id),
        ]
        evac_args = {
            'host': None, 'on_shared_storage': False, 'password': None,
        }
        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_with_password(self):
        args = [
            self.server.id,
            '--password', 'password',
        ]
        verify_args = [
            ('server', self.server.id),
            ('password', 'password'),
        ]
        evac_args = {
            'host': None, 'on_shared_storage': False, 'password': 'password',
        }
        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_with_host(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.29')

        host = 'target-host'
        args = [
            self.server.id,
            '--host', 'target-host',
        ]
        verify_args = [
            ('server', self.server.id),
            ('host', 'target-host'),
        ]
        evac_args = {'host': host, 'password': None}

        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_with_host_pre_v229(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.28')

        args = [
            self.server.id,
            '--host', 'target-host',
        ]
        verify_args = [
            ('server', self.server.id),
            ('host', 'target-host'),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

    def test_evacuate_without_share_storage(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.13')

        args = [
            self.server.id,
            '--shared-storage'
        ]
        verify_args = [
            ('server', self.server.id),
            ('shared_storage', True),
        ]
        evac_args = {
            'host': None, 'on_shared_storage': True, 'password': None,
        }
        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_without_share_storage_post_v213(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.14')

        args = [
            self.server.id,
            '--shared-storage'
        ]
        verify_args = [
            ('server', self.server.id),
            ('shared_storage', True),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_evacuate_with_wait_ok(self, mock_wait_for_status):
        args = [
            self.server.id,
            '--wait',
        ]
        verify_args = [
            ('server', self.server.id),
            ('wait', True),
        ]
        evac_args = {
            'host': None, 'on_shared_storage': False, 'password': None,
        }
        self._test_evacuate(args, verify_args, evac_args)
        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            self.server.id,
            callback=mock.ANY,
        )


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


class TestServerRescue(TestServer):

    def setUp(self):
        super(TestServerRescue, self).setUp()

        # Return value for utils.find_resource for image
        self.image = image_fakes.FakeImage.create_one_image()
        self.get_image_mock.return_value = self.image

        new_server = compute_fakes.FakeServer.create_one_server()
        attrs = {
            'id': new_server.id,
            'image': {
                'id': self.image.id,
            },
            'networks': {},
            'adminPass': 'passw0rd',
        }
        methods = {
            'rescue': new_server,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=attrs,
            methods=methods,
        )

        # Return value for utils.find_resource for server
        self.servers_mock.get.return_value = self.server

        self.cmd = server.RescueServer(self.app, None)

    def test_rescue_with_current_image(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.rescue.assert_called_with(image=None, password=None)

    def test_rescue_with_new_image(self):
        new_image = image_fakes.FakeImage.create_one_image()
        self.find_image_mock.return_value = new_image
        arglist = [
            '--image', new_image.id,
            self.server.id,
        ]
        verifylist = [
            ('image', new_image.id),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.find_image_mock.assert_called_with(new_image.id)
        self.server.rescue.assert_called_with(image=new_image, password=None)

    def test_rescue_with_current_image_and_password(self):
        password = 'password-xxx'
        arglist = [
            '--password', password,
            self.server.id,
        ]
        verifylist = [
            ('password', password),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test
        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.rescue.assert_called_with(image=None, password=password)


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.floating_ip_remove'
)
class TestServerRemoveFloatingIPCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestServerRemoveFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = server.RemoveFloatingIP(self.app, None)

    def test_server_remove_floating_ip(self, fip_mock):
        _floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

        arglist = [
            'server1',
            _floating_ip['ip'],
        ]
        verifylist = [
            ('server', 'server1'),
            ('ip_address', _floating_ip['ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(
            'server1',
            _floating_ip['ip'],
        )


class TestServerRemoveFloatingIPNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestServerRemoveFloatingIPNetwork, self).setUp()

        self.app.client_manager.network = mock.Mock()
        self.network = self.app.client_manager.network
        self.network.update_ip = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = server.RemoveFloatingIP(self.app, self.namespace)

    def test_server_remove_floating_ip_default(self):
        _server = compute_fakes.FakeServer.create_one_server()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network.find_ip = mock.Mock(return_value=_floating_ip)
        arglist = [
            _server.id,
            _floating_ip['ip'],
        ]
        verifylist = [
            ('server', _server.id),
            ('ip_address', _floating_ip['ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': None,
        }

        self.network.find_ip.assert_called_once_with(
            _floating_ip['ip'],
            ignore_missing=False,
        )
        self.network.update_ip.assert_called_once_with(
            _floating_ip,
            **attrs
        )


class TestServerRemovePort(TestServer):

    def setUp(self):
        super(TestServerRemovePort, self).setUp()

        # Get the command object to test
        self.cmd = server.RemovePort(self.app, None)

        # Set method to be tested.
        self.methods = {
            'interface_detach': None,
        }

        self.find_port = mock.Mock()
        self.app.client_manager.network.find_port = self.find_port

    def _test_server_remove_port(self, port_id):
        servers = self.setup_servers_mock(count=1)
        port = 'fake-port'

        arglist = [
            servers[0].id,
            port,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('port', port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].interface_detach.assert_called_once_with(port_id)
        self.assertIsNone(result)

    def test_server_remove_port(self):
        self._test_server_remove_port(self.find_port.return_value.id)
        self.find_port.assert_called_once_with(
            'fake-port', ignore_missing=False)

    def test_server_remove_port_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_remove_port('fake-port')
        self.find_port.assert_not_called()


class TestServerRemoveNetwork(TestServer):

    def setUp(self):
        super(TestServerRemoveNetwork, self).setUp()

        # Get the command object to test
        self.cmd = server.RemoveNetwork(self.app, None)

        # Set method to be tested.
        self.fake_inf = mock.Mock()
        self.methods = {
            'interface_list': [self.fake_inf],
            'interface_detach': None,
        }

        self.find_network = mock.Mock()
        self.app.client_manager.network.find_network = self.find_network

    def _test_server_remove_network(self, network_id):
        self.fake_inf.net_id = network_id
        self.fake_inf.port_id = 'fake-port'
        servers = self.setup_servers_mock(count=1)
        network = 'fake-network'

        arglist = [
            servers[0].id,
            network,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', network),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        servers[0].interface_list.assert_called_once_with()
        servers[0].interface_detach.assert_called_once_with('fake-port')
        self.assertIsNone(result)

    def test_server_remove_network(self):
        self._test_server_remove_network(self.find_network.return_value.id)
        self.find_network.assert_called_once_with(
            'fake-network', ignore_missing=False)

    def test_server_remove_network_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_remove_network('fake-network')
        self.find_network.assert_not_called()


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.security_group_find'
)
class TestServerRemoveSecurityGroup(TestServer):

    def setUp(self):
        super(TestServerRemoveSecurityGroup, self).setUp()

        self.security_group = \
            compute_fakes.FakeSecurityGroup.create_one_security_group()

        attrs = {
            'security_groups': [{'name': self.security_group['id']}]
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

    def test_server_remove_security_group(self, sg_find_mock):
        sg_find_mock.return_value = self.security_group
        arglist = [
            self.server.id,
            self.security_group['id']
        ]
        verifylist = [
            ('server', self.server.id),
            ('group', self.security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        sg_find_mock.assert_called_with(
            self.security_group['id'],
        )
        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.remove_security_group.assert_called_with(
            self.security_group['id'],
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

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.resize)
        self.servers_mock.confirm_resize.assert_called_with(self.server)
        self.assertNotCalled(self.servers_mock.revert_resize)
        self.assertIsNone(result)
        # A warning should have been logged for using --confirm.
        mock_warning.assert_called_once()
        self.assertIn('The --confirm option has been deprecated.',
                      str(mock_warning.call_args[0][0]))

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

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.assertNotCalled(self.servers_mock.resize)
        self.assertNotCalled(self.servers_mock.confirm_resize)
        self.servers_mock.revert_resize.assert_called_with(self.server)
        self.assertIsNone(result)
        # A warning should have been logged for using --revert.
        mock_warning.assert_called_once()
        self.assertIn('The --revert option has been deprecated.',
                      str(mock_warning.call_args[0][0]))

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
            callback=mock.ANY,
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
            callback=mock.ANY,
            **kwargs
        )

        self.servers_mock.resize.assert_called_with(
            self.server,
            self.flavors_get_return_value
        )


class TestServerResizeConfirm(TestServer):

    def setUp(self):
        super(TestServerResizeConfirm, self).setUp()

        methods = {
            'confirm_resize': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.confirm_resize.return_value = None

        # Get the command object to test
        self.cmd = server.ResizeConfirm(self.app, None)

    def test_resize_confirm(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.confirm_resize.assert_called_with()


# TODO(stephenfin): Remove in OSC 7.0
class TestServerMigrateConfirm(TestServer):

    def setUp(self):
        super().setUp()

        methods = {
            'confirm_resize': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.confirm_resize.return_value = None

        # Get the command object to test
        self.cmd = server.MigrateConfirm(self.app, None)

    def test_migrate_confirm(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.confirm_resize.assert_called_with()

        mock_warning.assert_called_once()
        self.assertIn(
            "The 'server migrate confirm' command has been deprecated",
            str(mock_warning.call_args[0][0])
        )


class TestServerConfirmMigration(TestServerResizeConfirm):

    def setUp(self):
        super().setUp()

        methods = {
            'confirm_resize': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.confirm_resize.return_value = None

        # Get the command object to test
        self.cmd = server.ConfirmMigration(self.app, None)

    def test_migration_confirm(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.confirm_resize.assert_called_with()


class TestServerResizeRevert(TestServer):

    def setUp(self):
        super(TestServerResizeRevert, self).setUp()

        methods = {
            'revert_resize': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.revert_resize.return_value = None

        # Get the command object to test
        self.cmd = server.ResizeRevert(self.app, None)

    def test_resize_revert(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.revert_resize.assert_called_with()


# TODO(stephenfin): Remove in OSC 7.0
class TestServerMigrateRevert(TestServer):

    def setUp(self):
        super().setUp()

        methods = {
            'revert_resize': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.revert_resize.return_value = None

        # Get the command object to test
        self.cmd = server.MigrateRevert(self.app, None)

    def test_migrate_revert(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.revert_resize.assert_called_with()

        mock_warning.assert_called_once()
        self.assertIn(
            "The 'server migrate revert' command has been deprecated",
            str(mock_warning.call_args[0][0])
        )


class TestServerRevertMigration(TestServer):

    def setUp(self):
        super().setUp()

        methods = {
            'revert_resize': None,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            methods=methods)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server

        self.servers_mock.revert_resize.return_value = None

        # Get the command object to test
        self.cmd = server.RevertMigration(self.app, None)

    def test_migration_revert(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(self.server.id)
        self.server.revert_resize.assert_called_with()


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

        self.attrs = {
            'api_version': None,
        }

        self.methods = {
            'update': None,
            'reset_state': None,
            'change_password': None,
            'clear_password': None,
            'add_tag': None,
            'set_tags': None,
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
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.servers_mock.set_meta.assert_called_once_with(
            self.fake_servers[0], parsed_args.properties)
        self.assertIsNone(result)

    def test_server_set_with_password(self):
        arglist = [
            '--password', 'foo',
            'foo_vm',
        ]
        verifylist = [
            ('password', 'foo'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.fake_servers[0].change_password.assert_called_once_with('foo')

    def test_server_set_with_no_password(self):
        arglist = [
            '--no-password',
            'foo_vm',
        ]
        verifylist = [
            ('no_password', True),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.fake_servers[0].clear_password.assert_called_once_with()

    # TODO(stephenfin): Remove this in a future major version
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

    def test_server_set_with_description_api_newer(self):

        # Description is supported for nova api version 2.19 or above
        self.fake_servers[0].api_version = 2.19

        arglist = [
            '--description', 'foo_description',
            'foo_vm',
        ]
        verifylist = [
            ('description', 'foo_description'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.19):
            result = self.cmd.take_action(parsed_args)
            self.fake_servers[0].update.assert_called_once_with(
                description='foo_description')
            self.assertIsNone(result)

    def test_server_set_with_description_api_older(self):

        # Description is not supported for nova api version below 2.19
        self.fake_servers[0].api_version = 2.18

        arglist = [
            '--description', 'foo_description',
            'foo_vm',
        ]
        verifylist = [
            ('description', 'foo_description'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.19):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)

    def test_server_set_with_tag(self):
        self.fake_servers[0].api_version = api_versions.APIVersion('2.26')

        arglist = [
            '--tag', 'tag1',
            '--tag', 'tag2',
            'foo_vm',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.fake_servers[0].add_tag.assert_has_calls([
            mock.call(tag='tag1'),
            mock.call(tag='tag2'),
        ])
        self.assertIsNone(result)

    def test_server_set_with_tag_pre_v226(self):
        self.fake_servers[0].api_version = api_versions.APIVersion('2.25')

        arglist = [
            '--tag', 'tag1',
            '--tag', 'tag2',
            'foo_vm',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required',
            str(ex))


class TestServerShelve(TestServer):

    def setUp(self):
        super(TestServerShelve, self).setUp()

        # Get the command object to test
        self.cmd = server.ShelveServer(self.app, None)

    def test_shelve(self):
        server_info = {'status': 'ACTIVE'}
        server_methods = {
            'shelve': None,
            'shelve_offload': None,
        }

        server = compute_fakes.FakeServer.create_one_server(
            attrs=server_info, methods=server_methods)
        self.servers_mock.get.return_value = server

        arglist = [server.name]
        verifylist = [
            ('servers', [server.name]),
            ('wait', False),
            ('offload', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.servers_mock.get.assert_called_once_with(server.name)
        server.shelve.assert_called_once_with()
        server.shelve_offload.assert_not_called()

    def test_shelve_already_shelved(self):
        server_info = {'status': 'SHELVED'}
        server_methods = {
            'shelve': None,
            'shelve_offload': None,
        }

        server = compute_fakes.FakeServer.create_one_server(
            attrs=server_info, methods=server_methods)
        self.servers_mock.get.return_value = server

        arglist = [server.name]
        verifylist = [
            ('servers', [server.name]),
            ('wait', False),
            ('offload', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.servers_mock.get.assert_called_once_with(server.name)
        server.shelve.assert_not_called()
        server.shelve_offload.assert_not_called()

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_shelve_with_wait(self, mock_wait_for_status):
        server_info = {'status': 'ACTIVE'}
        server_methods = {
            'shelve': None,
            'shelve_offload': None,
        }

        server = compute_fakes.FakeServer.create_one_server(
            attrs=server_info, methods=server_methods)
        self.servers_mock.get.return_value = server

        arglist = ['--wait', server.name]
        verifylist = [
            ('servers', [server.name]),
            ('wait', True),
            ('offload', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.servers_mock.get.assert_called_once_with(server.name)
        server.shelve.assert_called_once_with()
        server.shelve_offload.assert_not_called()
        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            server.id,
            callback=mock.ANY,
            success_status=('shelved', 'shelved_offloaded'),
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_shelve_offload(self, mock_wait_for_status):
        server_info = {'status': 'ACTIVE'}
        server_methods = {
            'shelve': None,
            'shelve_offload': None,
        }

        server = compute_fakes.FakeServer.create_one_server(
            attrs=server_info, methods=server_methods)
        self.servers_mock.get.return_value = server

        arglist = ['--offload', server.name]
        verifylist = [
            ('servers', [server.name]),
            ('wait', False),
            ('offload', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.servers_mock.get.assert_has_calls([
            mock.call(server.name),
            mock.call(server.name),
        ])
        server.shelve.assert_called_once_with()
        server.shelve_offload.assert_called_once_with()
        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            server.id,
            callback=mock.ANY,
            success_status=('shelved', 'shelved_offloaded'),
        )


class TestServerShow(TestServer):

    def setUp(self):
        super(TestServerShow, self).setUp()

        self.image = image_fakes.FakeImage.create_one_image()
        self.flavor = compute_fakes.FakeFlavor.create_one_flavor()
        self.topology = {
            'nodes': [{'vcpu_set': [0, 1]}, {'vcpu_set': [2, 3]}],
            'pagesize_kb': None,
        }
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
            'topology': self.topology,
        }
        self.server = compute_fakes.FakeServer.create_one_server(
            attrs=server_info, methods=server_method)

        # This is the return value for utils.find_resource()
        self.servers_mock.get.return_value = self.server
        self.get_image_mock.return_value = self.image
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
            server.PowerStateColumn(
                getattr(self.server, 'OS-EXT-STS:power_state')),
            format_columns.DictListColumn(self.server.networks),
            self.flavor.name + " (" + self.flavor.id + ")",
            self.server.id,
            self.image.name + " (" + self.image.id + ")",
            self.server.name,
            {'public': ['10.20.30.40', '2001:db8::f']},
            'tenant-id-xxx',
            format_columns.DictColumn({}),
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
            ('topology', False),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_show_embedded_flavor(self):
        # Tests using --os-compute-api-version >= 2.47 where the flavor
        # details are embedded in the server response body excluding the id.
        arglist = [
            self.server.name,
        ]
        verifylist = [
            ('diagnostics', False),
            ('topology', False),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.server.info['flavor'] = {
            'ephemeral': 0,
            'ram': 512,
            'original_name': 'm1.tiny',
            'vcpus': 1,
            'extra_specs': {},
            'swap': 0,
            'disk': 1
        }
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        # Since the flavor details are in a dict we can't be sure of the
        # ordering so just assert that one of the keys is in the output.
        self.assertIn('original_name', data[2]._value)

    def test_show_diagnostics(self):
        arglist = [
            '--diagnostics',
            self.server.name,
        ]
        verifylist = [
            ('diagnostics', True),
            ('topology', False),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(('test',), columns)
        self.assertEqual(('test',), data)

    def test_show_topology(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.78')

        arglist = [
            '--topology',
            self.server.name,
        ]
        verifylist = [
            ('diagnostics', False),
            ('topology', True),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.columns += ('topology',)
        self.data += (format_columns.DictColumn(self.topology),)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_show_topology_pre_v278(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.77')

        arglist = [
            '--topology',
            self.server.name,
        ]
        verifylist = [
            ('diagnostics', False),
            ('topology', True),
            ('server', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args)


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

    @mock.patch.object(common_utils, 'find_resource')
    def test_server_start_with_all_projects(self, mock_find_resource):
        servers = self.setup_servers_mock(count=1)
        mock_find_resource.side_effect = compute_fakes.FakeServer.get_servers(
            servers, 0,
        )

        arglist = [
            servers[0].id,
            '--all-projects',
        ]
        verifylist = [
            ('server', [servers[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        mock_find_resource.assert_called_once_with(
            mock.ANY, servers[0].id, all_tenants=True,
        )


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

    @mock.patch.object(common_utils, 'find_resource')
    def test_server_start_with_all_projects(self, mock_find_resource):
        servers = self.setup_servers_mock(count=1)
        mock_find_resource.side_effect = compute_fakes.FakeServer.get_servers(
            servers, 0,
        )

        arglist = [
            servers[0].id,
            '--all-projects',
        ]
        verifylist = [
            ('server', [servers[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        mock_find_resource.assert_called_once_with(
            mock.ANY, servers[0].id, all_tenants=True,
        )


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
            ('properties', ['key1', 'key2']),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.servers_mock.delete_meta.assert_called_once_with(
            self.fake_server, ['key1', 'key2'])
        self.assertIsNone(result)

    def test_server_unset_with_description_api_newer(self):

        # Description is supported for nova api version 2.19 or above
        self.app.client_manager.compute.api_version = 2.19

        arglist = [
            '--description',
            'foo_vm',
        ]
        verifylist = [
            ('description', True),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.19):
            result = self.cmd.take_action(parsed_args)
        self.servers_mock.update.assert_called_once_with(
            self.fake_server, description="")
        self.assertIsNone(result)

    def test_server_unset_with_description_api_older(self):

        # Description is not supported for nova api version below 2.19
        self.app.client_manager.compute.api_version = 2.18

        arglist = [
            '--description',
            'foo_vm',
        ]
        verifylist = [
            ('description', True),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(api_versions,
                               'APIVersion',
                               return_value=2.19):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)

    def test_server_unset_with_tag(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.26')

        arglist = [
            '--tag', 'tag1',
            '--tag', 'tag2',
            'foo_vm',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.servers_mock.delete_tag.assert_has_calls([
            mock.call(self.fake_server, tag='tag1'),
            mock.call(self.fake_server, tag='tag2'),
        ])

    def test_server_unset_with_tag_pre_v226(self):
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.25')

        arglist = [
            '--tag', 'tag1',
            '--tag', 'tag2',
            'foo_vm',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required',
            str(ex))


class TestServerUnshelve(TestServer):

    def setUp(self):
        super(TestServerUnshelve, self).setUp()

        # Get the command object to test
        self.cmd = server.UnshelveServer(self.app, None)

        # Set unshelve method to be tested.
        self.methods = {
            'unshelve': None,
        }
        self.attrs = {
            'status': 'SHELVED',
        }

    def test_unshelve_one_server(self):
        self.run_method_with_servers('unshelve', 1)

    def test_unshelve_multi_servers(self):
        self.run_method_with_servers('unshelve', 3)

    def test_unshelve_with_specified_az(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.77')

        server = compute_fakes.FakeServer.create_one_server(
            attrs=self.attrs, methods=self.methods)
        self.servers_mock.get.return_value = server
        arglist = [
            '--availability-zone', "foo-az",
            server.id,
        ]
        verifylist = [
            ('availability_zone', "foo-az"),
            ('server', [server.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_with(server.id)
        server.unshelve.assert_called_with(availability_zone="foo-az")

    def test_unshelve_with_specified_az_pre_v277(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.76')

        server = compute_fakes.FakeServer.create_one_server(
            attrs=self.attrs, methods=self.methods)
        arglist = [
            server.id,
            '--availability-zone', "foo-az",
        ]
        verifylist = [
            ('availability_zone', "foo-az"),
            ('server', [server.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)
        self.assertIn(
            '--os-compute-api-version 2.77 or greater is required', str(ex))

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_unshelve_with_wait(self, mock_wait_for_status):
        server = compute_fakes.FakeServer.create_one_server(
            attrs=self.attrs, methods=self.methods)
        self.servers_mock.get.return_value = server

        arglist = ['--wait', server.name]
        verifylist = [
            ('server', [server.name]),
            ('wait', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.servers_mock.get.assert_called_once_with(server.name)
        server.unshelve.assert_called_once_with()
        mock_wait_for_status.assert_called_once_with(
            self.servers_mock.get,
            server.id,
            callback=mock.ANY,
            success_status=('active', 'shutoff'),
        )


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
            'properties': '',
            'volumes_attached': [{"id": "6344fe9d-ef20-45b2-91a6"}],
        }
        _server = compute_fakes.FakeServer.create_one_server(attrs=server_info)
        find_resource.side_effect = [_server, _flavor]
        self.get_image_mock.return_value = _image

        # Prepare result data.
        info = {
            'id': _server.id,
            'name': _server.name,
            'image': '%s (%s)' % (_image.name, _image.id),
            'flavor': '%s (%s)' % (_flavor.name, _flavor.id),
            'OS-EXT-STS:power_state': server.PowerStateColumn(
                getattr(_server, 'OS-EXT-STS:power_state')),
            'properties': '',
            'volumes_attached': [{"id": "6344fe9d-ef20-45b2-91a6"}],
            'addresses': format_columns.DictListColumn(_server.networks),
            'project_id': 'tenant-id-xxx',
        }

        # Call _prep_server_detail().
        server_detail = server._prep_server_detail(
            self.app.client_manager.compute,
            self.app.client_manager.image,
            _server
        )
        # 'networks' is used to create _server. Remove it.
        server_detail.pop('networks')

        # Check the results.
        self.assertCountEqual(info, server_detail)
