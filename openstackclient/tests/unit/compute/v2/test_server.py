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

import base64
import collections
import getpass
import json
import tempfile
from unittest import mock
import uuid

import iso8601
from openstack.compute.v2 import server_group as _server_group
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils as common_utils

from openstackclient.api import compute_v2
from openstackclient.compute.v2 import server
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as test_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes


class TestPowerStateColumn(test_utils.TestCase):
    def test_human_readable(self):
        self.assertEqual(
            'NOSTATE', server.PowerStateColumn(0x00).human_readable()
        )
        self.assertEqual(
            'Running', server.PowerStateColumn(0x01).human_readable()
        )
        self.assertEqual('', server.PowerStateColumn(0x02).human_readable())
        self.assertEqual(
            'Paused', server.PowerStateColumn(0x03).human_readable()
        )
        self.assertEqual(
            'Shutdown', server.PowerStateColumn(0x04).human_readable()
        )
        self.assertEqual('', server.PowerStateColumn(0x05).human_readable())
        self.assertEqual(
            'Crashed', server.PowerStateColumn(0x06).human_readable()
        )
        self.assertEqual(
            'Suspended', server.PowerStateColumn(0x07).human_readable()
        )
        self.assertEqual('N/A', server.PowerStateColumn(0x08).human_readable())


class TestServer(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        # Set object attributes to be tested. Could be overwritten in subclass.
        self.attrs = {}

    def setup_sdk_servers_mock(self, count):
        servers = compute_fakes.create_sdk_servers(
            attrs=self.attrs,
            count=count,
        )

        # This is the return value for compute_client.find_server()
        self.compute_client.find_server.side_effect = servers

        return servers


class TestServerAddFixedIP(TestServer):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.AddFixedIP(self.app, None)

        # Mock network methods
        self.find_network = mock.Mock()
        self.app.client_manager.network.find_network = self.find_network

    def test_server_add_fixed_ip_pre_v249_with_tag(self):
        self.set_compute_api_version('2.48')

        servers = self.setup_sdk_servers_mock(count=1)
        network = compute_fakes.create_one_network()

        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            arglist = [
                servers[0].id,
                network['id'],
                '--fixed-ip-address',
                '5.6.7.8',
                '--tag',
                'tag1',
            ]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', '5.6.7.8'),
                ('tag', 'tag1'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            ex = self.assertRaises(
                exceptions.CommandError, self.cmd.take_action, parsed_args
            )
            self.assertIn(
                '--os-compute-api-version 2.49 or greater is required', str(ex)
            )

    def test_server_add_fixed_ip(self):
        self.set_compute_api_version('2.49')

        servers = self.setup_sdk_servers_mock(count=1)
        network = compute_fakes.create_one_network()
        interface = compute_fakes.create_one_server_interface()
        self.compute_client.create_server_interface.return_value = interface

        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            arglist = [servers[0].id, network['id']]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            expected_columns = (
                'Port ID',
                'Server ID',
                'Network ID',
                'MAC Address',
                'Port State',
                'Fixed IPs',
            )
            expected_data = (
                interface.port_id,
                interface.server_id,
                interface.net_id,
                interface.mac_addr,
                interface.port_state,
                format_columns.ListDictColumn(interface.fixed_ips),
            )

            columns, data = self.cmd.take_action(parsed_args)

            self.assertEqual(expected_columns, columns)
            self.assertEqual(expected_data, tuple(data))
            self.compute_client.create_server_interface.assert_called_once_with(
                servers[0].id, net_id=network['id']
            )

    def test_server_add_fixed_ip_with_fixed_ip(self):
        self.set_compute_api_version('2.49')

        servers = self.setup_sdk_servers_mock(count=1)
        network = compute_fakes.create_one_network()
        interface = compute_fakes.create_one_server_interface()
        self.compute_client.create_server_interface.return_value = interface

        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            arglist = [
                servers[0].id,
                network['id'],
                '--fixed-ip-address',
                '5.6.7.8',
            ]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', '5.6.7.8'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            expected_columns = (
                'Port ID',
                'Server ID',
                'Network ID',
                'MAC Address',
                'Port State',
                'Fixed IPs',
            )
            expected_data = (
                interface.port_id,
                interface.server_id,
                interface.net_id,
                interface.mac_addr,
                interface.port_state,
                format_columns.ListDictColumn(interface.fixed_ips),
            )

            columns, data = self.cmd.take_action(parsed_args)

            self.assertEqual(expected_columns, columns)
            self.assertEqual(expected_data, tuple(data))
            self.compute_client.create_server_interface.assert_called_once_with(
                servers[0].id,
                net_id=network['id'],
                fixed_ips=[{'ip_address': '5.6.7.8'}],
            )

    def test_server_add_fixed_ip_with_tag(self):
        self.set_compute_api_version('2.49')

        servers = self.setup_sdk_servers_mock(count=1)
        network = compute_fakes.create_one_network()
        interface = compute_fakes.create_one_server_interface()
        self.compute_client.create_server_interface.return_value = interface

        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            arglist = [
                servers[0].id,
                network['id'],
                '--fixed-ip-address',
                '5.6.7.8',
                '--tag',
                'tag1',
            ]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', '5.6.7.8'),
                ('tag', 'tag1'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            expected_columns = (
                'Port ID',
                'Server ID',
                'Network ID',
                'MAC Address',
                'Port State',
                'Fixed IPs',
                'Tag',
            )
            expected_data = (
                interface.port_id,
                interface.server_id,
                interface.net_id,
                interface.mac_addr,
                interface.port_state,
                format_columns.ListDictColumn(interface.fixed_ips),
                interface.tag,
            )

            columns, data = self.cmd.take_action(parsed_args)

            self.assertEqual(expected_columns, columns)
            self.assertEqual(expected_data, tuple(data))
            self.compute_client.create_server_interface.assert_called_once_with(
                servers[0].id,
                net_id=network['id'],
                fixed_ips=[{'ip_address': '5.6.7.8'}],
                tag='tag1',
            )

    def test_server_add_fixed_ip_with_fixed_ip_with_tag(self):
        self.set_compute_api_version('2.49')

        servers = self.setup_sdk_servers_mock(count=1)
        network = compute_fakes.create_one_network()
        interface = compute_fakes.create_one_server_interface()
        self.compute_client.create_server_interface.return_value = interface

        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            arglist = [
                servers[0].id,
                network['id'],
                '--fixed-ip-address',
                '5.6.7.8',
                '--tag',
                'tag1',
            ]
            verifylist = [
                ('server', servers[0].id),
                ('network', network['id']),
                ('fixed_ip_address', '5.6.7.8'),
                ('tag', 'tag1'),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            expected_columns = (
                'Port ID',
                'Server ID',
                'Network ID',
                'MAC Address',
                'Port State',
                'Fixed IPs',
                'Tag',
            )
            expected_data = (
                interface.port_id,
                interface.server_id,
                interface.net_id,
                interface.mac_addr,
                interface.port_state,
                format_columns.ListDictColumn(interface.fixed_ips),
                interface.tag,
            )

            columns, data = self.cmd.take_action(parsed_args)

            self.assertEqual(expected_columns, columns)
            self.assertEqual(expected_data, tuple(data))
            self.compute_client.create_server_interface.assert_called_once_with(
                servers[0].id,
                net_id=network['id'],
                fixed_ips=[{'ip_address': '5.6.7.8'}],
                tag='tag1',
            )


class TestServerAddFloatingIPCompute(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False
        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.cmd = server.AddFloatingIP(self.app, None)

    def test_server_add_floating_ip_default(self):
        arglist = [
            self.server.name,
            '1.2.3.4',
        ]
        verifylist = [
            ('server', self.server.name),
            ('ip_address', '1.2.3.4'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False
        )
        self.compute_client.add_floating_ip_to_server.assert_called_once_with(
            self.server, '1.2.3.4', fixed_address=None
        )

    def test_server_add_floating_ip_fixed(self):
        arglist = [
            '--fixed-ip-address',
            '5.6.7.8',
            self.server.name,
            '1.2.3.4',
        ]
        verifylist = [
            ('fixed_ip_address', '5.6.7.8'),
            ('server', self.server.name),
            ('ip_address', '1.2.3.4'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False
        )
        self.compute_client.add_floating_ip_to_server.assert_called_once_with(
            self.server, '1.2.3.4', fixed_address='5.6.7.8'
        )


class TestServerAddFloatingIPNetwork(
    TestServer,
    network_fakes.TestNetworkV2,
):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.network_client.update_ip = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = server.AddFloatingIP(self.app, None)

    def test_server_add_floating_ip(self):
        _port = network_fakes.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network_client.find_ip = mock.Mock(return_value=_floating_ip)
        self.network_client.ports = mock.Mock(return_value=[_port])
        arglist = [
            self.server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('server', self.server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': _port.id,
        }

        self.network_client.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network_client.ports.assert_called_once_with(
            device_id=self.server.id,
        )
        self.network_client.update_ip.assert_called_once_with(
            _floating_ip, **attrs
        )

    def test_server_add_floating_ip_no_ports(self):
        floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()

        self.network_client.find_ip = mock.Mock(return_value=floating_ip)
        self.network_client.ports = mock.Mock(return_value=[])

        arglist = [
            self.server.id,
            floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('server', self.server.id),
            ('ip_address', floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'No attached ports found to associate floating IP with', str(ex)
        )

        self.network_client.find_ip.assert_called_once_with(
            floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network_client.ports.assert_called_once_with(
            device_id=self.server.id,
        )

    def test_server_add_floating_ip_no_external_gateway(self, success=False):
        _port = network_fakes.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network_client.find_ip = mock.Mock(return_value=_floating_ip)
        return_value = [_port]
        # In the success case, we'll have two ports, where the first port is
        # not attached to an external gateway but the second port is.
        if success:
            return_value.append(_port)
        self.network_client.ports = mock.Mock(return_value=return_value)
        side_effect = [sdk_exceptions.NotFoundException()]
        if success:
            side_effect.append(None)
        self.network_client.update_ip = mock.Mock(side_effect=side_effect)
        arglist = [
            self.server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('server', self.server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        if success:
            self.cmd.take_action(parsed_args)
        else:
            self.assertRaises(
                sdk_exceptions.NotFoundException,
                self.cmd.take_action,
                parsed_args,
            )

        attrs = {
            'port_id': _port.id,
        }

        self.network_client.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network_client.ports.assert_called_once_with(
            device_id=self.server.id,
        )
        if success:
            self.assertEqual(2, self.network_client.update_ip.call_count)
            calls = [mock.call(_floating_ip, **attrs)] * 2
            self.network_client.update_ip.assert_has_calls(calls)
        else:
            self.network_client.update_ip.assert_called_once_with(
                _floating_ip, **attrs
            )

    def test_server_add_floating_ip_one_external_gateway(self):
        self.test_server_add_floating_ip_no_external_gateway(success=True)

    def test_server_add_floating_ip_with_fixed_ip(self):
        _port = network_fakes.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network_client.find_ip = mock.Mock(return_value=_floating_ip)
        self.network_client.ports = mock.Mock(return_value=[_port])
        # The user has specified a fixed ip that matches one of the ports
        # already attached to the instance.
        arglist = [
            '--fixed-ip-address',
            _port.fixed_ips[0]['ip_address'],
            self.server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('fixed_ip_address', _port.fixed_ips[0]['ip_address']),
            ('server', self.server.id),
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

        self.network_client.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network_client.ports.assert_called_once_with(
            device_id=self.server.id,
        )
        self.network_client.update_ip.assert_called_once_with(
            _floating_ip, **attrs
        )

    def test_server_add_floating_ip_with_fixed_ip_no_port_found(self):
        _port = network_fakes.create_one_port()
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network_client.find_ip = mock.Mock(return_value=_floating_ip)
        self.network_client.ports = mock.Mock(return_value=[_port])
        # The user has specified a fixed ip that does not match any of the
        # ports already attached to the instance.
        nonexistent_ip = '10.0.0.9'
        arglist = [
            '--fixed-ip-address',
            nonexistent_ip,
            self.server.id,
            _floating_ip['floating_ip_address'],
        ]
        verifylist = [
            ('fixed_ip_address', nonexistent_ip),
            ('server', self.server.id),
            ('ip_address', _floating_ip['floating_ip_address']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.network_client.find_ip.assert_called_once_with(
            _floating_ip['floating_ip_address'],
            ignore_missing=False,
        )
        self.network_client.ports.assert_called_once_with(
            device_id=self.server.id,
        )
        self.network_client.update_ip.assert_not_called()


class TestServerAddPort(TestServer):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.AddPort(self.app, None)

        self.find_port = mock.Mock()
        self.app.client_manager.network.find_port = self.find_port

    def _test_server_add_port(self, port_id):
        servers = self.setup_sdk_servers_mock(count=1)
        port = 'fake-port'

        arglist = [
            servers[0].id,
            port,
        ]
        verifylist = [('server', servers[0].id), ('port', port)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.create_server_interface.assert_called_once_with(
            servers[0], port_id=port_id
        )
        self.assertIsNone(result)

    def test_server_add_port(self):
        self._test_server_add_port(self.find_port.return_value.id)
        self.find_port.assert_called_once_with(
            'fake-port', ignore_missing=False
        )

    def test_server_add_port_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_add_port('fake-port')
        self.find_port.assert_not_called()

    def test_server_add_port_with_tag(self):
        self.set_compute_api_version('2.49')

        servers = self.setup_sdk_servers_mock(count=1)
        self.find_port.return_value.id = 'fake-port'
        arglist = [
            servers[0].id,
            'fake-port',
            '--tag',
            'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('port', 'fake-port'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.create_server_interface.assert_called_once_with(
            servers[0], port_id='fake-port', tag='tag1'
        )

    def test_server_add_port_with_tag_pre_v249(self):
        self.set_compute_api_version('2.48')

        servers = self.setup_sdk_servers_mock(count=1)
        self.find_port.return_value.id = 'fake-port'
        arglist = [
            servers[0].id,
            'fake-port',
            '--tag',
            'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('port', 'fake-port'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.49 or greater is required', str(ex)
        )


class TestServerVolume(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.volume = volume_fakes.create_one_sdk_volume()
        self.volume_sdk_client.find_volume.return_value = self.volume

        attrs = {
            'server_id': self.server.id,
            'volume_id': self.volume.id,
        }
        self.volume_attachment = compute_fakes.create_one_volume_attachment(
            attrs=attrs
        )

        self.compute_client.create_volume_attachment.return_value = (
            self.volume_attachment
        )


class TestServerAddVolume(TestServerVolume):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.AddServerVolume(self.app, None)

    def test_server_add_volume(self):
        self.set_compute_api_version('2.48')
        arglist = [
            '--device',
            '/dev/sdb',
            self.server.id,
            self.volume.id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('ID', 'Server ID', 'Volume ID', 'Device')
        expected_data = (
            self.volume_attachment.id,
            self.volume_attachment.server_id,
            self.volume_attachment.volume_id,
            '/dev/sdb',
        )

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)
        self.compute_client.create_volume_attachment.assert_called_once_with(
            self.server, volumeId=self.volume.id, device='/dev/sdb'
        )

    def test_server_add_volume_with_tag(self):
        self.set_compute_api_version('2.49')

        arglist = [
            '--device',
            '/dev/sdb',
            '--tag',
            'foo',
            self.server.id,
            self.volume.id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('tag', 'foo'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('ID', 'Server ID', 'Volume ID', 'Device', 'Tag')
        expected_data = (
            self.volume_attachment.id,
            self.volume_attachment.server_id,
            self.volume_attachment.volume_id,
            self.volume_attachment.device,
            self.volume_attachment.tag,
        )

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)
        self.compute_client.create_volume_attachment.assert_called_once_with(
            self.server,
            volumeId=self.volume.id,
            device='/dev/sdb',
            tag='foo',
        )

    def test_server_add_volume_with_tag_pre_v249(self):
        self.set_compute_api_version('2.48')

        arglist = [
            self.server.id,
            self.volume.id,
            '--tag',
            'foo',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('tag', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.49 or greater is required', str(ex)
        )

    def test_server_add_volume_with_enable_delete_on_termination(self):
        self.set_compute_api_version('2.79')

        self.volume_attachment.delete_on_termination = True
        arglist = [
            '--enable-delete-on-termination',
            '--device',
            '/dev/sdb',
            self.server.id,
            self.volume.id,
        ]

        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('enable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = (
            'ID',
            'Server ID',
            'Volume ID',
            'Device',
            'Tag',
            'Delete On Termination',
        )
        expected_data = (
            self.volume_attachment.id,
            self.volume_attachment.server_id,
            self.volume_attachment.volume_id,
            self.volume_attachment.device,
            self.volume_attachment.tag,
            self.volume_attachment.delete_on_termination,
        )

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)
        self.compute_client.create_volume_attachment.assert_called_once_with(
            self.server,
            volumeId=self.volume.id,
            device='/dev/sdb',
            delete_on_termination=True,
        )

    def test_server_add_volume_with_disable_delete_on_termination(self):
        self.set_compute_api_version('2.79')

        self.volume_attachment.delete_on_termination = False

        arglist = [
            '--disable-delete-on-termination',
            '--device',
            '/dev/sdb',
            self.server.id,
            self.volume.id,
        ]

        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('disable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = (
            'ID',
            'Server ID',
            'Volume ID',
            'Device',
            'Tag',
            'Delete On Termination',
        )
        expected_data = (
            self.volume_attachment.id,
            self.volume_attachment.server_id,
            self.volume_attachment.volume_id,
            self.volume_attachment.device,
            self.volume_attachment.tag,
            self.volume_attachment.delete_on_termination,
        )

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)
        self.compute_client.create_volume_attachment.assert_called_once_with(
            self.server,
            volumeId=self.volume.id,
            device='/dev/sdb',
            delete_on_termination=False,
        )

    def test_server_add_volume_with_enable_delete_on_termination_pre_v279(
        self,
    ):
        self.set_compute_api_version('2.78')

        arglist = [
            self.server.id,
            self.volume.id,
            '--enable-delete-on-termination',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('enable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.79 or greater is required', str(ex)
        )

    def test_server_add_volume_with_disable_delete_on_termination_pre_v279(
        self,
    ):
        self.set_compute_api_version('2.78')

        arglist = [
            self.server.id,
            self.volume.id,
            '--disable-delete-on-termination',
        ]
        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('disable_delete_on_termination', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.79 or greater is required', str(ex)
        )

    def test_server_add_volume_with_disable_and_enable_delete_on_termination(
        self,
    ):
        self.set_compute_api_version('2.78')

        arglist = [
            '--enable-delete-on-termination',
            '--disable-delete-on-termination',
            '--device',
            '/dev/sdb',
            self.server.id,
            self.volume.id,
        ]

        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
            ('device', '/dev/sdb'),
            ('enable_delete_on_termination', True),
            ('disable_delete_on_termination', True),
        ]
        ex = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertIn(
            'argument --disable-delete-on-termination: not allowed '
            'with argument --enable-delete-on-termination',
            str(ex),
        )


class TestServerRemoveVolume(TestServerVolume):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.RemoveServerVolume(self.app, None)

    def test_server_remove_volume(self):
        arglist = [
            self.server.id,
            self.volume.id,
        ]

        verifylist = [
            ('server', self.server.id),
            ('volume', self.volume.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.compute_client.delete_volume_attachment.assert_called_once_with(
            self.volume,
            self.server,
            ignore_missing=False,
        )


class TestServerAddNetwork(TestServer):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.AddNetwork(self.app, None)

        self.find_network = mock.Mock()
        self.app.client_manager.network.find_network = self.find_network

    def _test_server_add_network(self, net_id):
        servers = self.setup_sdk_servers_mock(count=1)
        network = 'fake-network'

        arglist = [
            servers[0].id,
            network,
        ]
        verifylist = [('server', servers[0].id), ('network', network)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.create_server_interface.assert_called_once_with(
            servers[0], net_id=net_id
        )
        self.assertIsNone(result)

    def test_server_add_network(self):
        self._test_server_add_network(self.find_network.return_value.id)
        self.find_network.assert_called_once_with(
            'fake-network', ignore_missing=False
        )

    def test_server_add_network_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_add_network('fake-network')
        self.find_network.assert_not_called()

    def test_server_add_network_with_tag(self):
        self.set_compute_api_version('2.49')

        servers = self.setup_sdk_servers_mock(count=1)
        self.find_network.return_value.id = 'fake-network'

        arglist = [
            servers[0].id,
            'fake-network',
            '--tag',
            'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', 'fake-network'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.create_server_interface.assert_called_once_with(
            servers[0], net_id='fake-network', tag='tag1'
        )

    def test_server_add_network_with_tag_pre_v249(self):
        self.set_compute_api_version('2.48')

        servers = self.setup_sdk_servers_mock(count=1)
        self.find_network.return_value.id = 'fake-network'

        arglist = [
            servers[0].id,
            'fake-network',
            '--tag',
            'tag1',
        ]
        verifylist = [
            ('server', servers[0].id),
            ('network', 'fake-network'),
            ('tag', 'tag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.49 or greater is required', str(ex)
        )


class TestServerAddSecurityGroup(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.add_security_group_to_server.return_value = None

        # Get the command object to test
        self.cmd = server.AddServerSecurityGroup(self.app, None)

    def test_server_add_security_group__nova_network(self):
        arglist = [self.server.id, 'fake_sg']
        verifylist = [
            ('server', self.server.id),
            ('security_groups', ['fake_sg']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            with mock.patch.object(
                compute_v2,
                'find_security_group',
                return_value={'name': 'fake_sg'},
            ) as mock_find_nova_net_sg:
                result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.add_security_group_to_server.assert_called_once_with(
            self.server, {'name': 'fake_sg'}
        )
        mock_find_nova_net_sg.assert_called_once_with(
            self.compute_client, 'fake_sg'
        )
        self.assertIsNone(result)

    def test_server_add_security_group(self):
        arglist = [self.server.id, 'fake_sg']
        verifylist = [
            ('server', self.server.id),
            ('security_groups', ['fake_sg']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.add_security_group_to_server.assert_called_once_with(
            self.server, {'name': 'fake_sg'}
        )
        self.assertIsNone(result)


class TestServerCreate(TestServer):
    columns = (
        'OS-DCF:diskConfig',
        'OS-EXT-AZ:availability_zone',
        'OS-EXT-SRV-ATTR:host',
        'OS-EXT-SRV-ATTR:hostname',
        'OS-EXT-SRV-ATTR:hypervisor_hostname',
        'OS-EXT-SRV-ATTR:instance_name',
        'OS-EXT-SRV-ATTR:kernel_id',
        'OS-EXT-SRV-ATTR:launch_index',
        'OS-EXT-SRV-ATTR:ramdisk_id',
        'OS-EXT-SRV-ATTR:reservation_id',
        'OS-EXT-SRV-ATTR:root_device_name',
        'OS-EXT-SRV-ATTR:user_data',
        'OS-EXT-STS:power_state',
        'OS-EXT-STS:task_state',
        'OS-EXT-STS:vm_state',
        'OS-SRV-USG:launched_at',
        'OS-SRV-USG:terminated_at',
        'accessIPv4',
        'accessIPv6',
        'addresses',
        'config_drive',
        'created',
        'description',
        'flavor',
        'hostId',
        'host_status',
        'id',
        'image',
        'key_name',
        'locked',
        'locked_reason',
        'name',
        'pinned_availability_zone',
        'progress',
        'project_id',
        'properties',
        'server_groups',
        'status',
        'tags',
        'trusted_image_certificates',
        'updated',
        'user_id',
        'volumes_attached',
    )

    def datalist(self):
        return (
            None,  # OS-DCF:diskConfig
            None,  # OS-EXT-AZ:availability_zone
            None,  # OS-EXT-SRV-ATTR:host
            None,  # OS-EXT-SRV-ATTR:hostname
            None,  # OS-EXT-SRV-ATTR:hypervisor_hostname
            None,  # OS-EXT-SRV-ATTR:instance_name
            None,  # OS-EXT-SRV-ATTR:kernel_id
            None,  # OS-EXT-SRV-ATTR:launch_index
            None,  # OS-EXT-SRV-ATTR:ramdisk_id
            None,  # OS-EXT-SRV-ATTR:reservation_id
            None,  # OS-EXT-SRV-ATTR:root_device_name
            None,  # OS-EXT-SRV-ATTR:user_data
            server.PowerStateColumn(
                self.server.power_state
            ),  # OS-EXT-STS:power_state
            None,  # OS-EXT-STS:task_state
            None,  # OS-EXT-STS:vm_state
            None,  # OS-SRV-USG:launched_at
            None,  # OS-SRV-USG:terminated_at
            None,  # accessIPv4
            None,  # accessIPv6
            server.AddressesColumn({}),  # addresses
            None,  # config_drive
            None,  # created
            None,  # description
            self.flavor.name + " (" + self.flavor.id + ")",  # flavor
            None,  # hostId
            None,  # host_status
            self.server.id,  # id
            self.image.name + " (" + self.image.id + ")",  # image
            None,  # key_name
            None,  # locked
            None,  # locked_reason
            self.server.name,
            None,  # pinned_availability_zone
            None,  # progress
            None,  # project_id
            format_columns.DictColumn({}),  # properties
            None,  # server_groups
            None,  # status
            format_columns.ListColumn([]),  # tags
            None,  # trusted_image_certificates
            None,  # updated
            None,  # user_id
            format_columns.ListDictColumn([]),  # volumes_attached
        )

    def setUp(self):
        super().setUp()

        self.image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = self.image
        self.image_client.get_image.return_value = self.image

        self.flavor = compute_fakes.create_one_flavor()
        self.compute_client.find_flavor.return_value = self.flavor

        attrs = {
            'addresses': {},
            'networks': {},
            'image': self.image,
            'flavor': self.flavor,
        }
        self.server = compute_fakes.create_one_sdk_server(attrs=attrs)

        self.compute_client.create_server.return_value = self.server
        self.compute_client.get_server.return_value = self.server

        self.volume = volume_fakes.create_one_volume()
        self.snapshot = volume_fakes.create_one_snapshot()

        # Get the command object to test
        self.cmd = server.CreateServer(self.app, None)

    def test_server_create_no_options(self):
        arglist = [
            self.server.name,
        ]
        verifylist = [
            ('server_name', self.server.name),
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_server_create_minimal(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_has_calls(
            [mock.call(self.flavor.id, ignore_missing=False)] * 2
        )
        self.image_client.find_image.assert_called_once_with(
            self.image.id, ignore_missing=False
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_options(self):
        server_group = sdk_fakes.generate_fake_resource(
            _server_group.ServerGroup
        )
        self.compute_client.find_server_group.return_value = server_group

        security_group = network_fakes.create_one_security_group()
        self.network_client.find_security_group.return_value = security_group

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--key-name',
            'keyname',
            '--property',
            'Beta=b',
            '--security-group',
            security_group.id,
            '--use-config-drive',
            '--password',
            'passw0rd',
            '--hint',
            'a=b',
            '--hint',
            'a=c',
            '--server-group',
            server_group.id,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('key_name', 'keyname'),
            ('properties', {'Beta': 'b'}),
            ('security_groups', [security_group.id]),
            ('hints', {'a': ['b', 'c']}),
            ('server_group', server_group.id),
            ('config_drive', True),
            ('password', 'passw0rd'),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_has_calls(
            [mock.call(self.flavor.id, ignore_missing=False)] * 2
        )
        self.network_client.find_security_group.assert_called_once_with(
            security_group.id, ignore_missing=False
        )
        self.image_client.find_image.assert_called_once_with(
            self.image.id, ignore_missing=False
        )
        self.compute_client.find_server_group.assert_called_once_with(
            server_group.id, ignore_missing=False
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            metadata={'Beta': 'b'},
            min_count=1,
            max_count=1,
            security_groups=[{'name': security_group.id}],
            key_name='keyname',
            admin_password='passw0rd',
            networks=[],
            scheduler_hints={'a': ['b', 'c'], 'group': server_group.id},
            config_drive=True,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_not_exist_security_group(self):
        self.network_client.find_security_group.side_effect = (
            sdk_exceptions.NotFoundException()
        )

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--key-name',
            'keyname',
            '--security-group',
            'not_exist_sg',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('key_name', 'keyname'),
            ('security_groups', ['not_exist_sg']),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            sdk_exceptions.NotFoundException, self.cmd.take_action, parsed_args
        )
        self.network_client.find_security_group.assert_called_once_with(
            'not_exist_sg', ignore_missing=False
        )

    def test_server_create_with_security_group_in_nova_network(self):
        sg_name = 'nova-net-sec-group'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--security-group',
            sg_name,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('security_groups', [sg_name]),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            with mock.patch.object(
                compute_v2,
                'find_security_group',
                return_value={'name': sg_name},
            ) as mock_find:
                columns, data = self.cmd.take_action(parsed_args)

        mock_find.assert_called_once_with(self.compute_client, sg_name)
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            security_groups=[{'name': sg_name}],
            networks=[],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_no_security_group(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--no-security-group',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('key_name', None),
            ('properties', None),
            ('security_groups', []),
            ('hints', {}),
            ('server_group', None),
            ('config_drive', False),
            ('password', None),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_has_calls(
            [mock.call(self.flavor.id, ignore_missing=False)] * 2
        )
        self.network_client.find_security_group.assert_not_called()
        self.image_client.find_image.assert_called_once_with(
            self.image.id, ignore_missing=False
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            security_groups=[],
            networks=[],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_network(self):
        network_net1 = network_fakes.create_one_network()
        network_net2 = network_fakes.create_one_network()
        network_auto = network_fakes.create_one_network({'name': 'auto'})
        port_port1 = network_fakes.create_one_port()
        port_port2 = network_fakes.create_one_port()

        def find_network(name_or_id, ignore_missing):
            assert ignore_missing is False
            return {
                network_net1.id: network_net1,
                network_net2.id: network_net2,
                network_auto.name: network_auto,
            }[name_or_id]

        def find_port(name_or_id, ignore_missing):
            assert ignore_missing is False
            return {
                port_port1.name: port_port1,
                port_port2.id: port_port2,
            }[name_or_id]

        self.app.client_manager.network.find_network.side_effect = find_network
        self.app.client_manager.network.find_port.side_effect = find_port

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--network',
            network_net1.id,
            '--nic',
            f'net-id={network_net2.id},v4-fixed-ip=10.0.0.2',
            '--port',
            port_port1.name,
            '--network',
            network_auto.name,
            '--nic',
            f'port-id={port_port2.id}',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'nics',
                [
                    {
                        'net-id': network_net1.id,
                        'port-id': '',
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                    },
                    {
                        'net-id': network_net2.id,
                        'port-id': '',
                        'v4-fixed-ip': '10.0.0.2',
                        'v6-fixed-ip': '',
                    },
                    {
                        'net-id': '',
                        'port-id': port_port1.name,
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                    },
                    {
                        'net-id': network_auto.name,
                        'port-id': '',
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                    },
                    {
                        'net-id': '',
                        'port-id': port_port2.id,
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                    },
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_has_calls(
            [
                mock.call(network_net1.id, ignore_missing=False),
                mock.call(network_net2.id, ignore_missing=False),
                mock.call(network_auto.name, ignore_missing=False),
            ]
        )
        self.network_client.find_port.assert_has_calls(
            [
                mock.call(port_port1.name, ignore_missing=False),
                mock.call(port_port2.id, ignore_missing=False),
            ]
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[
                {
                    'uuid': network_net1.id,
                },
                {
                    'uuid': network_net2.id,
                    'fixed': '10.0.0.2',
                },
                {
                    'port': port_port1.id,
                },
                {
                    'uuid': network_auto.id,
                },
                {
                    'port': port_port2.id,
                },
            ],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_network_tag(self):
        self.set_compute_api_version('2.43')

        network = network_fakes.create_one_network()
        self.app.client_manager.network.find_network.return_value = network

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            f'net-id={network.id},tag=foo',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'nics',
                [
                    {
                        'net-id': network.id,
                        'port-id': '',
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                        'tag': 'foo',
                    },
                ],
            ),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_called_once_with(
            network.id, ignore_missing=False
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[
                {
                    'uuid': network.id,
                    'tag': 'foo',
                },
            ],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_network_tag_pre_v243(self):
        self.set_compute_api_version('2.42')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'net-id=net1,tag=foo',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'nics',
                [
                    {
                        'net-id': 'net1',
                        'port-id': '',
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                        'tag': 'foo',
                    },
                ],
            ),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.network_client.find_network.assert_not_called()
        self.compute_client.create_server.assert_not_called()

    def _test_server_create_with_auto_network(self, arglist):
        # requires API microversion 2.37 or later
        self.set_compute_api_version('2.37')

        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('nics', ['auto']),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_not_called()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    # NOTE(stephenfin): '--auto-network' is an alias for '--nic auto' so the
    # tests are nearly identical

    def test_server_create_with_auto_network_legacy(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'auto',
            self.server.name,
        ]
        self._test_server_create_with_auto_network(arglist)

    def test_server_create_with_auto_network(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--auto-network',
            self.server.name,
        ]
        self._test_server_create_with_auto_network(arglist)

    def test_server_create_with_auto_network_pre_v237(self):
        # use an API microversion that's too old
        self.set_compute_api_version('2.36')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'auto',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('nics', ['auto']),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.37 or greater is required to support '
            'explicit auto-allocation of a network or to disable network '
            'allocation',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_auto_network_default(self):
        """Tests creating a server without specifying --nic using 2.37."""
        # requires API microversion 2.37 or later
        self.set_compute_api_version('2.37')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('nics', []),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_not_called()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def _test_server_create_with_none_network(self, arglist):
        # requires API microversion 2.37 or later
        self.set_compute_api_version('2.37')

        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('nics', ['none']),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_not_called()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='none',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    # NOTE(stephenfin): '--no-network' is an alias for '--nic none' so the
    # tests are nearly identical

    def test_server_create_with_none_network_legacy(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'none',
            self.server.name,
        ]
        self._test_server_create_with_none_network(arglist)

    def test_server_create_with_none_network(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--no-network',
            self.server.name,
        ]
        self._test_server_create_with_none_network(arglist)

    def test_server_create_with_none_network_pre_v237(self):
        # use an API microversion that's too old
        self.set_compute_api_version('2.36')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'none',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('nics', ['none']),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.37 or greater is required to support '
            'explicit auto-allocation of a network or to disable network '
            'allocation',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_conflicting_network_options(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'none',
            '--nic',
            'auto',
            '--nic',
            'port-id=port1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'nics',
                [
                    'none',
                    'auto',
                    {
                        'net-id': '',
                        'port-id': 'port1',
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                    },
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'Specifying a --nic of auto or none cannot be used with any '
            'other --nic, --network or --port value.',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_invalid_network_options(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'abcdefgh',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'Invalid argument abcdefgh; argument must be of form ',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_invalid_network_key(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'abcdefgh=12324',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'Invalid argument abcdefgh=12324; argument must be of form ',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_empty_network_key_value(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'net-id=',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'Invalid argument net-id=; argument must be of form ',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_only_network_key(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--nic',
            'net-id',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'Invalid argument net-id; argument must be of form ',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_network_in_nova_network(self):
        net_name = 'nova-net-net'
        net_id = uuid.uuid4().hex

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--network',
            net_name,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'nics',
                [
                    {
                        'net-id': net_name,
                        'port-id': '',
                        'v4-fixed-ip': '',
                        'v6-fixed-ip': '',
                    },
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            with mock.patch.object(
                compute_v2,
                'find_network',
                return_value={'id': net_id, 'name': net_name},
            ) as mock_find:
                columns, data = self.cmd.take_action(parsed_args)

        mock_find.assert_called_once_with(self.compute_client, net_name)
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[
                {
                    'uuid': net_id,
                },
            ],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_conflicting_net_port_filters(self):
        arglist = [
            '--image',
            'image1',
            '--flavor',
            'flavor1',
            '--nic',
            'net-id=abc,port-id=xyz',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn("either 'network' or 'port'", str(exc))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_conflicting_fixed_ip_filters(self):
        arglist = [
            '--image',
            'image1',
            '--flavor',
            'flavor1',
            '--nic',
            'net-id=abc,v4-fixed-ip=1.2.3.4,v6-fixed-ip=2001:db8:abcd',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn("either 'v4-fixed-ip' or 'v6-fixed-ip'", str(exc))
        self.compute_client.create_server.assert_not_called()

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_create_with_wait_ok(self, mock_wait_for_status):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--wait',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('wait', True),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
        )

        self.assertEqual(self.columns, columns)
        self.assertTupleEqual(self.datalist(), data)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_create_with_wait_fails(self, mock_wait_for_status):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--wait',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('wait', True),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
        )

    def test_server_create_userdata(self):
        user_data = b'#!/bin/sh'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--user-data',
            'userdata.sh',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('user_data', 'userdata.sh'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch(
            'openstackclient.compute.v2.server.open',
            mock.mock_open(read_data=user_data),
        ) as mock_file:
            columns, data = self.cmd.take_action(parsed_args)

        mock_file.assert_called_with('userdata.sh', 'rb')
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            user_data=base64.b64encode(user_data).decode('utf-8'),
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_volume(self):
        self.volume_client.volumes.get.return_value = self.volume

        arglist = [
            '--flavor',
            self.flavor.id,
            '--volume',
            self.volume.name,
            self.server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('volume', self.volume.name),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volumes.get.assert_called_once_with(
            self.volume.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id='',
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.volume.id,
                    'boot_index': 0,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                }
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_snapshot(self):
        self.volume_client.volume_snapshots.get.return_value = self.snapshot

        arglist = [
            '--flavor',
            self.flavor.id,
            '--snapshot',
            self.snapshot.name,
            self.server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('snapshot', self.snapshot.name),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volume_snapshots.get.assert_called_once_with(
            self.snapshot.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id='',
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.snapshot.id,
                    'boot_index': 0,
                    'source_type': 'snapshot',
                    'destination_type': 'volume',
                    'delete_on_termination': False,
                }
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device(self):
        block_device = f'uuid={self.volume.id},source_type=volume,boot_index=0'
        arglist = [
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        verifylist = [
            ('image', None),
            ('flavor', self.flavor.id),
            (
                'block_devices',
                [
                    {
                        'uuid': self.volume.id,
                        'source_type': 'volume',
                        'boot_index': '0',
                    },
                ],
            ),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # we don't do any validation of IDs when using the legacy option
        self.volume_client.volumes.get.assert_not_called()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id='',
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.volume.id,
                    'boot_index': 0,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                }
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_full(self):
        self.set_compute_api_version('2.67')

        self.volume_alt = volume_fakes.create_one_volume()
        block_device = (
            f'uuid={self.volume.id},source_type=volume,'
            f'destination_type=volume,disk_bus=ide,device_type=disk,'
            f'device_name=sdb,guest_format=ext4,volume_size=64,'
            f'volume_type=foo,boot_index=1,delete_on_termination=true,'
            f'tag=foo'
        )
        block_device_alt = f'uuid={self.volume_alt.id},source_type=volume'

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            '--block-device',
            block_device_alt,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_devices',
                [
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
                    {
                        'uuid': self.volume_alt.id,
                        'source_type': 'volume',
                    },
                ],
            ),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # we don't do any validation of IDs when using the legacy option
        self.volume_client.volumes.get.assert_not_called()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
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
                },
                {
                    'uuid': self.volume_alt.id,
                    'source_type': 'volume',
                    'destination_type': 'volume',
                },
            ],
            networks='auto',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_from_file(self):
        self.set_compute_api_version('2.67')

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
                '--image',
                self.image.id,
                '--flavor',
                self.flavor.id,
                '--block-device',
                fp.name,
                self.server.name,
            ]
            verifylist = [
                ('image', self.image.id),
                ('flavor', self.flavor.id),
                ('block_devices', [block_device]),
                ('server_name', self.server.name),
            ]
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # we don't do any validation of IDs when using the legacy option
        self.volume_client.volumes.get.assert_not_called()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
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
                },
            ],
            networks='auto',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_invalid_boot_index(self):
        block_device = (
            f'uuid={self.volume.name},source_type=volume,boot_index=foo'
        )
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn('The boot_index key of --block-device ', str(ex))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_invalid_source_type(self):
        block_device = f'uuid={self.volume.name},source_type=foo'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn('The source_type key of --block-device ', str(ex))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_invalid_destination_type(self):
        block_device = f'uuid={self.volume.name},destination_type=foo'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn('The destination_type key of --block-device ', str(ex))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_invalid_shutdown(self):
        block_device = f'uuid={self.volume.name},delete_on_termination=foo'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'The delete_on_termination key of --block-device ', str(ex)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_tag_pre_v242(self):
        self.set_compute_api_version('2.41')

        block_device = f'uuid={self.volume.name},tag=foo'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.42 or greater is required', str(ex)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_volume_type_pre_v267(self):
        self.set_compute_api_version('2.66')

        block_device = f'uuid={self.volume.name},volume_type=foo'
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device',
            block_device,
            self.server.name,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.67 or greater is required', str(ex)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_mapping(self):
        self.volume_client.volumes.get.return_value = self.volume

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vda=' + self.volume.name + ':::false',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_device_mapping',
                [
                    {
                        'device_name': 'vda',
                        'uuid': self.volume.name,
                        'source_type': 'volume',
                        'destination_type': 'volume',
                        'delete_on_termination': 'false',
                    }
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volumes.get.assert_called_once_with(
            self.volume.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'device_name': 'vda',
                    'uuid': self.volume.id,
                    'destination_type': 'volume',
                    'source_type': 'volume',
                    'delete_on_termination': 'false',
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping_min_input(self):
        self.volume_client.volumes.get.return_value = self.volume

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vdf=' + self.volume.name,
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_device_mapping',
                [
                    {
                        'device_name': 'vdf',
                        'uuid': self.volume.name,
                        'source_type': 'volume',
                        'destination_type': 'volume',
                    }
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volumes.get.assert_called_once_with(
            self.volume.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'device_name': 'vdf',
                    'uuid': self.volume.id,
                    'destination_type': 'volume',
                    'source_type': 'volume',
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping_default_input(self):
        self.volume_client.volumes.get.return_value = self.volume

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vdf=' + self.volume.name + ':::',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_device_mapping',
                [
                    {
                        'device_name': 'vdf',
                        'uuid': self.volume.name,
                        'source_type': 'volume',
                        'destination_type': 'volume',
                    }
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volumes.get.assert_called_once_with(
            self.volume.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'device_name': 'vdf',
                    'uuid': self.volume.id,
                    'destination_type': 'volume',
                    'source_type': 'volume',
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping_full_input(self):
        self.volume_client.volumes.get.return_value = self.volume

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vde=' + self.volume.name + ':volume:3:true',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_device_mapping',
                [
                    {
                        'device_name': 'vde',
                        'uuid': self.volume.name,
                        'source_type': 'volume',
                        'destination_type': 'volume',
                        'volume_size': '3',
                        'delete_on_termination': 'true',
                    }
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volumes.get.assert_called_once_with(
            self.volume.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'device_name': 'vde',
                    'uuid': self.volume.id,
                    'destination_type': 'volume',
                    'source_type': 'volume',
                    'delete_on_termination': 'true',
                    'volume_size': '3',
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping_snapshot(self):
        self.snapshot = volume_fakes.create_one_snapshot()
        self.volume_client.volume_snapshots.get.return_value = self.snapshot

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vds=' + self.snapshot.name + ':snapshot:5:true',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_device_mapping',
                [
                    {
                        'device_name': 'vds',
                        'uuid': self.snapshot.name,
                        'source_type': 'snapshot',
                        'volume_size': '5',
                        'destination_type': 'volume',
                        'delete_on_termination': 'true',
                    }
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volume_snapshots.get.assert_called_once_with(
            self.snapshot.name
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'device_name': 'vds',
                    'uuid': self.snapshot.id,
                    'destination_type': 'volume',
                    'source_type': 'snapshot',
                    'delete_on_termination': 'true',
                    'volume_size': '5',
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping_multiple(self):
        self.volume_client.volumes.get.return_value = self.volume

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vdb=' + self.volume.name + ':::false',
            '--block-device-mapping',
            'vdc=' + self.volume.name + ':::true',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            (
                'block_device_mapping',
                [
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
                ],
            ),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.volume_client.volumes.get.assert_has_calls(
            [mock.call(self.volume.name)] * 2
        )
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
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
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_block_device_mapping_invalid_format(self):
        # block device mapping don't contain equal sign "="
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'not_contain_equal_sign',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'argument --block-device-mapping: Invalid argument ', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

        # block device mapping don't contain device name "=uuid:::true"
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            '=uuid:::true',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'argument --block-device-mapping: Invalid argument ', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_block_device_mapping_no_uuid(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--block-device-mapping',
            'vdb=',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn(
            'argument --block-device-mapping: Invalid argument ', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_volume_boot_from_volume_conflict(self):
        # Tests that specifying --volume and --boot-from-volume results in
        # an error. Since --boot-from-volume requires --image or
        # --image-property but those are in a mutex group with --volume, we
        # only specify --volume and --boot-from-volume for this test since
        # the validation is not handled with argparse.
        arglist = [
            '--flavor',
            self.flavor.id,
            '--volume',
            'volume1',
            '--boot-from-volume',
            '1',
            self.server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('volume', 'volume1'),
            ('boot_from_volume', 1),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        # Assert it is the error we expect.
        self.assertIn(
            '--volume is not allowed with --boot-from-volume', str(ex)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_boot_from_volume_no_image(self):
        # Test --boot-from-volume option without --image or
        # --image-property.
        arglist = [
            '--flavor',
            self.flavor.id,
            '--boot-from-volume',
            '1',
            self.server.name,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('boot_from_volume', 1),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'An image (--image or --image-property) is required '
            'to support --boot-from-volume option',
            str(ex),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_image_property(self):
        image = image_fakes.create_one_image({'hypervisor_type': 'qemu'})
        self.image_client.images.return_value = [image]

        arglist = [
            '--image-property',
            'hypervisor_type=qemu',
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            ('image_properties', {'hypervisor_type': 'qemu'}),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.images.assert_called_once_with()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            block_device_mapping=[
                {
                    'uuid': image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_image_property_multi(self):
        image = image_fakes.create_one_image(
            {'hypervisor_type': 'qemu', 'hw_disk_bus': 'ide'}
        )
        self.image_client.images.return_value = [image]

        arglist = [
            '--image-property',
            'hypervisor_type=qemu',
            '--image-property',
            'hw_disk_bus=ide',
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            (
                'image_properties',
                {'hypervisor_type': 'qemu', 'hw_disk_bus': 'ide'},
            ),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.images.assert_called_once_with()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            block_device_mapping=[
                {
                    'uuid': image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_image_property_missed(self):
        image = image_fakes.create_one_image(
            {'hypervisor_type': 'qemu', 'hw_disk_bus': 'ide'}
        )
        self.image_client.images.return_value = [image]

        arglist = [
            '--image-property',
            'hypervisor_type=qemu',
            # note the mismatch in the 'hw_disk_bus' property
            '--image-property',
            'hw_disk_bus=virtio',
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            (
                'image_properties',
                {'hypervisor_type': 'qemu', 'hw_disk_bus': 'virtio'},
            ),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'No images match the property expected by --image-property',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_image_property_with_image_list(self):
        target_image = image_fakes.create_one_image(
            {
                'properties': {
                    'owner_specified.openstack.object': 'image/cirros'
                }
            }
        )
        another_image = image_fakes.create_one_image()
        self.image_client.images.return_value = [target_image, another_image]

        arglist = [
            '--image-property',
            'owner_specified.openstack.object=image/cirros',
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            (
                'image_properties',
                {'owner_specified.openstack.object': 'image/cirros'},
            ),
            ('flavor', self.flavor.id),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.images.assert_called_once_with()
        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=target_image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            block_device_mapping=[
                {
                    'uuid': target_image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_no_boot_device(self):
        block_device = f'uuid={self.volume.id},source_type=volume,boot_index=1'
        arglist = [
            '--block-device',
            block_device,
            '--flavor',
            self.flavor.id,
            self.server.name,
        ]
        verifylist = [
            ('image', None),
            ('flavor', self.flavor.id),
            (
                'block_devices',
                [
                    {
                        'uuid': self.volume.id,
                        'source_type': 'volume',
                        'boot_index': '1',
                    },
                ],
            ),
            ('server_name', self.server.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            'An image (--image, --image-property) or bootable volume '
            '(--volume, --snapshot, --block-device) is required',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_swap(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--swap',
            '1024',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('swap', 1024),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'boot_index': -1,
                    'source_type': 'blank',
                    'destination_type': 'local',
                    'guest_format': 'swap',
                    'volume_size': 1024,
                    'delete_on_termination': True,
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_ephemeral(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--ephemeral',
            'size=1024,format=ext4',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('ephemerals', [{'size': '1024', 'format': 'ext4'}]),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
                {
                    'boot_index': -1,
                    'source_type': 'blank',
                    'destination_type': 'local',
                    'guest_format': 'ext4',
                    'volume_size': '1024',
                    'delete_on_termination': True,
                },
            ],
            networks=[],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_ephemeral_missing_key(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--ephemeral',
            'format=ext3',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn('Argument parse failed', str(exc))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_ephemeral_invalid_key(self):
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--ephemeral',
            'size=1024,foo=bar',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn('Argument parse failed', str(exc))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_invalid_hint(self):
        # Not a key-value pair
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--hint',
            'a0cf03a5-d921-4877-bb5c-86d26cf818e1',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn('Argument parse failed', str(exc))
        self.compute_client.create_server.assert_not_called()

        # Empty key
        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--hint',
            '=a0cf03a5-d921-4877-bb5c-86d26cf818e1',
            self.server.name,
        ]
        exc = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )
        self.assertIn('Argument parse failed', str(exc))
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_description(self):
        # Description is supported for nova api version 2.19 or above
        self.set_compute_api_version('2.19')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--description',
            'description1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('description', 'description1'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks=[],
            description='description1',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_description_pre_v219(self):
        # Description is not supported for nova api version below 2.19
        self.set_compute_api_version('2.18')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--description',
            'description1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('description', 'description1'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_tag(self):
        self.set_compute_api_version('2.52')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--tag',
            'tag1',
            '--tag',
            'tag2',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('tags', ['tag1', 'tag2']),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            tags=['tag1', 'tag2'],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_tag_pre_v252(self):
        self.set_compute_api_version('2.51')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--tag',
            'tag1',
            '--tag',
            'tag2',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('tags', ['tag1', 'tag2']),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.52 or greater is required', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_host(self):
        # Explicit host is supported for nova api version 2.74 or above
        self.set_compute_api_version('2.74')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--host',
            'host1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('host', 'host1'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            host='host1',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_host_pre_v274(self):
        # Host is not supported for nova api version below 2.74
        self.set_compute_api_version('2.73')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--host',
            'host1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('host', 'host1'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.74 or greater is required', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_hypervisor_hostname(self):
        # Explicit hypervisor_hostname is supported for nova api version
        # 2.74 or above
        self.set_compute_api_version('2.74')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--hypervisor-hostname',
            'node1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('hypervisor_hostname', 'node1'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            hypervisor_hostname='node1',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_hypervisor_hostname_pre_v274(self):
        # Hypervisor_hostname is not supported for nova api version below 2.74
        self.set_compute_api_version('2.73')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--hypervisor-hostname',
            'node1',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('hypervisor_hostname', 'node1'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.74 or greater is required', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_hostname(self):
        self.set_compute_api_version('2.90')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--hostname',
            'hostname',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('hostname', 'hostname'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            hostname='hostname',
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_hostname_pre_v290(self):
        self.set_compute_api_version('2.89')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--hostname',
            'hostname',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('hostname', 'hostname'),
            ('config_drive', False),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.90 or greater is required', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_trusted_image_cert(self):
        self.set_compute_api_version('2.63')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('trusted_image_certs', ['foo', 'bar']),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_server.assert_called_once_with(
            name=self.server.name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            min_count=1,
            max_count=1,
            networks='auto',
            trusted_image_certificates=['foo', 'bar'],
            block_device_mapping=[
                {
                    'uuid': self.image.id,
                    'boot_index': 0,
                    'source_type': 'image',
                    'destination_type': 'local',
                    'delete_on_termination': True,
                },
            ],
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist(), data)

    def test_server_create_with_trusted_image_cert_pre_v263(self):
        self.set_compute_api_version('2.62')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('trusted_image_certs', ['foo', 'bar']),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.63 or greater is required', str(exc)
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_trusted_image_cert_from_volume(self):
        self.set_compute_api_version('2.63')

        arglist = [
            '--volume',
            'volume1',
            '--flavor',
            self.flavor.id,
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
            self.server.name,
        ]
        verifylist = [
            ('volume', 'volume1'),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('trusted_image_certs', ['foo', 'bar']),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--trusted-image-cert option is only supported for servers booted '
            'directly from images',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_trusted_image_cert_from_snapshot(self):
        self.set_compute_api_version('2.63')

        arglist = [
            '--snapshot',
            'snapshot1',
            '--flavor',
            self.flavor.id,
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
            self.server.name,
        ]
        verifylist = [
            ('snapshot', 'snapshot1'),
            ('flavor', self.flavor.id),
            ('config_drive', False),
            ('trusted_image_certs', ['foo', 'bar']),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--trusted-image-cert option is only supported for servers booted '
            'directly from images',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()

    def test_server_create_with_trusted_image_cert_boot_from_volume(self):
        self.set_compute_api_version('2.63')

        arglist = [
            '--image',
            self.image.id,
            '--flavor',
            self.flavor.id,
            '--boot-from-volume',
            '1',
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
            self.server.name,
        ]
        verifylist = [
            ('image', self.image.id),
            ('flavor', self.flavor.id),
            ('boot_from_volume', 1),
            ('config_drive', False),
            ('trusted_image_certs', ['foo', 'bar']),
            ('server_name', self.server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--trusted-image-cert option is only supported for servers booted '
            'directly from images',
            str(exc),
        )
        self.compute_client.create_server.assert_not_called()


class TestServerDelete(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.delete_server.return_value = None

        # Get the command object to test
        self.cmd = server.DeleteServer(self.app, None)

    def test_server_delete_no_options(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', [self.server.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False, all_projects=False
        )
        self.compute_client.delete_server.assert_called_once_with(
            self.server, force=False
        )
        self.assertIsNone(result)

    def test_server_delete_with_force(self):
        arglist = [
            self.server.id,
            '--force',
        ]
        verifylist = [
            ('server', [self.server.id]),
            ('force', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False, all_projects=False
        )
        self.compute_client.delete_server.assert_called_once_with(
            self.server, force=True
        )
        self.assertIsNone(result)

    def test_server_delete_multi_servers(self):
        servers = compute_fakes.create_sdk_servers(count=3)
        self.compute_client.find_server.return_value = None
        self.compute_client.find_server.side_effect = servers

        arglist = []
        verifylist = []
        for s in servers:
            arglist.append(s.id)
        verifylist = [
            ('server', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_has_calls(
            [
                mock.call(s.id, ignore_missing=False, all_projects=False)
                for s in servers
            ]
        )
        self.compute_client.delete_server.assert_has_calls(
            [mock.call(s, force=False) for s in servers]
        )
        self.assertIsNone(result)

    def test_server_delete_with_all_projects(self):
        arglist = [
            self.server.id,
            '--all-projects',
        ]
        verifylist = [
            ('server', [self.server.id]),
            ('all_projects', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False, all_projects=True
        )
        self.compute_client.delete_server.assert_called_once_with(
            self.server, force=False
        )
        self.assertIsNone(result)

    def test_server_delete_wait_ok(self):
        arglist = [
            self.server.id,
            '--wait',
        ]
        verifylist = [
            ('server', [self.server.id]),
            ('wait', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False, all_projects=False
        )
        self.compute_client.delete_server.assert_called_once_with(
            self.server, force=False
        )
        self.compute_client.wait_for_delete.assert_called_once_with(
            self.server,
            callback=mock.ANY,
        )
        self.assertIsNone(result)

    def test_server_delete_wait_fails(self):
        self.compute_client.wait_for_delete.side_effect = (
            sdk_exceptions.ResourceTimeout()
        )

        arglist = [
            self.server.id,
            '--wait',
        ]
        verifylist = [
            ('server', [self.server.id]),
            ('wait', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False, all_projects=False
        )
        self.compute_client.delete_server.assert_called_once_with(
            self.server, force=False
        )
        self.compute_client.wait_for_delete.assert_called_once_with(
            self.server,
            callback=mock.ANY,
        )


class TestServerDumpCreate(TestServer):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.CreateServerDump(self.app, None)

    def run_test_server_dump(self, server_count):
        servers = self.setup_sdk_servers_mock(server_count)

        arglist = []
        verifylist = []

        for s in servers:
            arglist.append(s.id)

        verifylist = [
            ('server', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        for s in servers:
            s.trigger_crash_dump.assert_called_once_with(self.compute_client)

    def test_server_dump_one_server(self):
        self.run_test_server_dump(1)

    def test_server_dump_multi_servers(self):
        self.run_test_server_dump(3)


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
        'Pinned Availability Zone',
        'Host',
        'Properties',
    )

    def setUp(self):
        super().setUp()

        # Default params of the core function of the command in the case of no
        # commandline option specified.
        self.kwargs = {
            'reservation_id': None,
            'ip': None,
            'ip6': None,
            'name': None,
            'status': None,
            'flavor': None,
            'image': None,
            'compute_host': None,
            'project_id': None,
            'all_projects': False,
            'user_id': None,
            'deleted': False,
            'changes-since': None,
            'changes-before': None,
        }

        # The fake servers' attributes. Use the original attributes names in
        # nova, not the ones printed by "server list" command.
        self.attrs = {
            'status': 'ACTIVE',
            'OS-EXT-STS:task_state': 'None',
            'OS-EXT-STS:power_state': 0x01,  # Running
            'networks': {'public': ['10.20.30.40', '2001:db8::5']},
            'OS-EXT-AZ:availability_zone': 'availability-zone-xxx',
            'OS-EXT-SRV-ATTR:host': 'host-name-xxx',
            'Metadata': format_columns.DictColumn({}),
        }

        self.image = image_fakes.create_one_image()

        self.image_client.find_image.return_value = self.image
        self.image_client.get_image.return_value = self.image

        self.flavor = compute_fakes.create_one_flavor()
        self.compute_client.find_flavor.return_value = self.flavor
        self.attrs['flavor'] = {'original_name': self.flavor.name}

        # The servers to be listed.
        self.servers = self.setup_sdk_servers_mock(3)
        self.compute_client.servers.return_value = self.servers

        # Get the command object to test
        self.cmd = server.ListServer(self.app, None)


class TestServerList(_TestServerList):
    def setUp(self):
        super().setUp()

        Image = collections.namedtuple('Image', 'id name')
        self.image_client.images.return_value = [
            Image(id=s.image['id'], name=self.image.name)
            # Image will be an empty string if boot-from-volume
            for s in self.servers
            if s.image
        ]

        Flavor = collections.namedtuple('Flavor', 'id name')
        self.compute_client.flavors.return_value = [
            Flavor(id=s.flavor['id'], name=self.flavor.name)
            for s in self.servers
        ]

        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
            )
            for s in self.servers
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

        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_called()
        self.compute_client.flavors.assert_called()
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
        self.compute_client.servers.return_value = []
        self.data = ()

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_not_called()
        self.compute_client.flavors.assert_not_called()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_long_option(self):
        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                getattr(s, 'task_state'),
                server.PowerStateColumn(getattr(s, 'power_state')),
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
                s.flavor['id'],
                getattr(s, 'availability_zone'),
                getattr(s, 'pinned_availability_zone', ''),
                server.HostColumn(getattr(s, 'hypervisor_hostname')),
                format_columns.DictColumn(s.metadata),
            )
            for s in self.servers
        )
        arglist = [
            '--long',
        ]
        verifylist = [
            ('all_projects', False),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.compute_client.servers.assert_called_with(**self.kwargs)
        image_ids = {s.image['id'] for s in self.servers if s.image}
        self.image_client.images.assert_called_once_with(
            id=f'in:{",".join(image_ids)}',
        )
        self.compute_client.flavors.assert_called_once_with(is_public=None)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_column_option(self):
        arglist = [
            '-c',
            'Project ID',
            '-c',
            'User ID',
            '-c',
            'Created At',
            '-c',
            'Security Groups',
            '-c',
            'Task State',
            '-c',
            'Power State',
            '-c',
            'Image ID',
            '-c',
            'Flavor ID',
            '-c',
            'Availability Zone',
            '-c',
            'Pinned Availability Zone',
            '-c',
            'Host',
            '-c',
            'Properties',
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertIn('Project ID', columns)
        self.assertIn('User ID', columns)
        self.assertIn('Created At', columns)
        self.assertIn('Security Groups', columns)
        self.assertIn('Task State', columns)
        self.assertIn('Power State', columns)
        self.assertIn('Image ID', columns)
        self.assertIn('Flavor ID', columns)
        self.assertIn('Availability Zone', columns)
        self.assertIn('Pinned Availability Zone', columns)
        self.assertIn('Host', columns)
        self.assertIn('Properties', columns)
        self.assertCountEqual(columns, set(columns))

    def test_server_list_no_name_lookup_option(self):
        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                s.flavor['id'],
            )
            for s in self.servers
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

        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_not_called()
        self.compute_client.flavors.assert_not_called()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_n_option(self):
        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                s.flavor['id'],
            )
            for s in self.servers
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

        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_not_called()
        self.compute_client.flavors.assert_not_called()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_name_lookup_one_by_one(self):
        arglist = ['--name-lookup-one-by-one']
        verifylist = [
            ('all_projects', False),
            ('no_name_lookup', False),
            ('name_lookup_one_by_one', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_not_called()
        self.compute_client.flavors.assert_not_called()
        self.image_client.get_image.assert_called()
        self.compute_client.find_flavor.assert_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_image(self):
        arglist = ['--image', self.image.id]
        verifylist = [('image', self.image.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.find_image.assert_called_with(
            self.image.id, ignore_missing=False
        )

        self.kwargs['image'] = self.image.id
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_not_called()
        self.compute_client.flavors.assert_called_once()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_flavor(self):
        arglist = ['--flavor', self.flavor.id]
        verifylist = [('flavor', self.flavor.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_has_calls(
            [mock.call(self.flavor.id, ignore_missing=False)]
        )

        self.kwargs['flavor'] = self.flavor.id
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.image_client.images.assert_called_once()
        self.compute_client.flavors.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_changes_since(self):
        arglist = ['--changes-since', '2016-03-04T06:27:59Z', '--deleted']
        verifylist = [
            ('changes_since', '2016-03-04T06:27:59Z'),
            ('deleted', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['changes-since'] = '2016-03-04T06:27:59Z'
        self.kwargs['deleted'] = True
        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    @mock.patch.object(iso8601, 'parse_date', side_effect=iso8601.ParseError)
    def test_server_list_with_invalid_changes_since(self, mock_parse_isotime):
        arglist = [
            '--changes-since',
            'Invalid time value',
        ]
        verifylist = [
            ('changes_since', 'Invalid time value'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'Invalid changes-since value: Invalid time value', str(e)
            )
        mock_parse_isotime.assert_called_once_with('Invalid time value')

    def test_server_list_with_tag(self):
        self.set_compute_api_version('2.26')

        arglist = [
            '--tag',
            'tag1',
            '--tag',
            'tag2',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['tags'] = 'tag1,tag2'

        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_tag_pre_v225(self):
        self.set_compute_api_version('2.25')

        arglist = [
            '--tag',
            'tag1',
            '--tag',
            'tag2',
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required', str(ex)
        )

    def test_server_list_with_not_tag(self):
        self.set_compute_api_version('2.26')
        arglist = [
            '--not-tag',
            'tag1',
            '--not-tag',
            'tag2',
        ]
        verifylist = [
            ('not_tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['not-tags'] = 'tag1,tag2'

        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_list_with_not_tag_pre_v226(self):
        self.set_compute_api_version('2.25')

        arglist = [
            '--not-tag',
            'tag1',
            '--not-tag',
            'tag2',
        ]
        verifylist = [
            ('not_tags', ['tag1', 'tag2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required', str(ex)
        )

    def test_server_list_with_availability_zone(self):
        arglist = [
            '--availability-zone',
            'test-az',
        ]
        verifylist = [
            ('availability_zone', 'test-az'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['availability_zone'] = 'test-az'
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_key_name(self):
        arglist = [
            '--key-name',
            'test-key',
        ]
        verifylist = [
            ('key_name', 'test-key'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['key_name'] = 'test-key'
        self.compute_client.servers.assert_called_with(**self.kwargs)
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

        self.kwargs['config_drive'] = True
        self.compute_client.servers.assert_called_with(**self.kwargs)
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

        self.kwargs['config_drive'] = False
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_progress(self):
        arglist = [
            '--progress',
            '100',
        ]
        verifylist = [
            ('progress', 100),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['progress'] = '100'
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_progress_invalid(self):
        arglist = [
            '--progress',
            '101',
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verify_args=[],
        )

    def test_server_list_with_vm_state(self):
        arglist = [
            '--vm-state',
            'active',
        ]
        verifylist = [
            ('vm_state', 'active'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['vm_state'] = 'active'
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_task_state(self):
        arglist = [
            '--task-state',
            'deleting',
        ]
        verifylist = [
            ('task_state', 'deleting'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['task_state'] = 'deleting'
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_with_power_state(self):
        arglist = [
            '--power-state',
            'running',
        ]
        verifylist = [
            ('power_state', 'running'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['power_state'] = 1
        self.compute_client.servers.assert_called_with(**self.kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_list_long_with_host_status_v216(self):
        self.set_compute_api_version('2.16')
        self.data1 = tuple(
            (
                s.id,
                s.name,
                s.status,
                getattr(s, 'task_state'),
                server.PowerStateColumn(getattr(s, 'power_state')),
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
                s.flavor['id'],
                getattr(s, 'availability_zone'),
                getattr(s, 'pinned_availability_zone', ''),
                server.HostColumn(getattr(s, 'hypervisor_hostname')),
                format_columns.DictColumn(s.metadata),
            )
            for s in self.servers
        )

        arglist = ['--long']
        verifylist = [
            ('long', True),
        ]

        # First test without host_status in the data -- the column should not
        # be present in this case.
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertEqual(self.columns_long, columns)
        self.assertEqual(tuple(self.data1), tuple(data))

        # Next test with host_status in the data -- the column should be
        # present in this case.
        self.compute_client.servers.reset_mock()

        self.attrs['host_status'] = 'UP'
        servers = self.setup_sdk_servers_mock(3)
        self.compute_client.servers.return_value = servers

        # Make sure the returned image and flavor IDs match the servers.
        Image = collections.namedtuple('Image', 'id name')
        self.image_client.images.return_value = [
            Image(id=s.image['id'], name=self.image.name)
            # Image will be an empty string if boot-from-volume
            for s in servers
            if s.image
        ]

        # Add the expected host_status column and data.
        columns_long = self.columns_long + ('Host Status',)
        self.data2 = tuple(
            (
                s.id,
                s.name,
                s.status,
                getattr(s, 'task_state'),
                server.PowerStateColumn(getattr(s, 'power_state')),
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                s.image['id'] if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
                s.flavor['id'],
                getattr(s, 'availability_zone'),
                getattr(s, 'pinned_availability_zone', ''),
                server.HostColumn(getattr(s, 'hypervisor_hostname')),
                format_columns.DictColumn(s.metadata),
                s.host_status,
            )
            for s in servers
        )

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertEqual(columns_long, columns)
        self.assertEqual(tuple(self.data2), tuple(data))


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
        'Pinned Availability Zone',
        'Host',
        'Properties',
    )

    def setUp(self):
        super().setUp()

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
        self.servers = self.setup_sdk_servers_mock(3)
        self.compute_client.servers.return_value = self.servers

        Image = collections.namedtuple('Image', 'id name')
        self.image_client.images.return_value = [
            Image(id=s.image['id'], name=self.image.name)
            # Image will be an empty string if boot-from-volume
            for s in self.servers
            if s.image
        ]

        # The flavor information is embedded, so now reason for this to be
        # called
        self.compute_client.flavors = mock.NonCallableMock()

        self.data = tuple(
            (
                s.id,
                s.name,
                s.status,
                server.AddressesColumn(s.addresses),
                # Image will be an empty string if boot-from-volume
                self.image.name if s.image else server.IMAGE_STRING_FOR_BFV,
                self.flavor.name,
            )
            for s in self.servers
        )

    def test_server_list_with_locked_pre_v273(self):
        arglist = ['--locked']
        verifylist = [('locked', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.73 or greater is required', str(ex)
        )

    def test_server_list_with_locked(self):
        self.set_compute_api_version('2.73')
        arglist = ['--locked']
        verifylist = [('locked', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['locked'] = True
        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))

    def test_server_list_with_unlocked_v273(self):
        self.set_compute_api_version('2.73')

        arglist = ['--unlocked']
        verifylist = [('unlocked', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['locked'] = False
        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))

    def test_server_list_with_locked_and_unlocked(self):
        self.set_compute_api_version('2.73')
        arglist = ['--locked', '--unlocked']
        verifylist = [('locked', True), ('unlocked', True)]

        ex = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertIn('Argument parse failed', str(ex))

    def test_server_list_with_changes_before(self):
        self.set_compute_api_version('2.66')
        arglist = ['--changes-before', '2016-03-05T06:27:59Z', '--deleted']
        verifylist = [
            ('changes_before', '2016-03-05T06:27:59Z'),
            ('deleted', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.kwargs['changes-before'] = '2016-03-05T06:27:59Z'
        self.kwargs['deleted'] = True

        self.compute_client.servers.assert_called_with(**self.kwargs)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))

    @mock.patch.object(iso8601, 'parse_date', side_effect=iso8601.ParseError)
    def test_server_list_with_invalid_changes_before(self, mock_parse_isotime):
        self.set_compute_api_version('2.66')
        arglist = [
            '--changes-before',
            'Invalid time value',
        ]
        verifylist = [
            ('changes_before', 'Invalid time value'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                'Invalid changes-before value: Invalid time value', str(e)
            )
        mock_parse_isotime.assert_called_once_with('Invalid time value')

    def test_server_with_changes_before_pre_v266(self):
        self.set_compute_api_version('2.65')

        arglist = ['--changes-before', '2016-03-05T06:27:59Z', '--deleted']
        verifylist = [
            ('changes_before', '2016-03-05T06:27:59Z'),
            ('deleted', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_server_list_v269_with_partial_constructs(self):
        self.set_compute_api_version('2.69')
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
                {"href": "http://fake/v2.1/", "rel": "self"},
                {"href": "http://fake", "rel": "bookmark"},
            ],
            "networks": {},
        }
        fake_server = compute_fakes.fakes.FakeResource(
            info=server_dict,
        )
        self.servers.append(fake_server)
        columns, data = self.cmd.take_action(parsed_args)
        # get the first three servers out since our interest is in the partial
        # server.
        next(data)
        next(data)
        next(data)
        partial_server = next(data)
        expected_row = (
            'server-id-95a56bfc4xxxxxx28d7e418bfd97813a',
            '',
            'UNKNOWN',
            server.AddressesColumn(''),
            '',
            '',
        )
        self.assertEqual(expected_row, partial_server)


class TestServerAction(compute_fakes.TestComputev2):
    def run_method_with_sdk_servers(self, method_name, server_count):
        servers = compute_fakes.create_sdk_servers(count=server_count)
        self.compute_client.find_server.side_effect = servers

        arglist = [s.id for s in servers]
        verifylist = [
            ('server', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = [mock.call(s.id) for s in servers]
        method = getattr(self.compute_client, method_name)
        method.assert_has_calls(calls)
        self.assertIsNone(result)


class TestServerLock(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.LockServer(self.app, None)

    def test_server_lock(self):
        self.run_method_with_sdk_servers('lock_server', 1)

    def test_server_lock_multi_servers(self):
        self.run_method_with_sdk_servers('lock_server', 3)

    def test_server_lock_with_reason(self):
        self.set_compute_api_version('2.73')

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.lock_server.return_value = None

        arglist = [
            self.server.id,
            '--reason',
            'blah',
        ]
        verifylist = [
            ('server', [self.server.id]),
            ('reason', 'blah'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            self.server.id,
            ignore_missing=False,
        )
        self.compute_client.lock_server.assert_called_with(
            self.server.id,
            locked_reason="blah",
        )

    def test_server_lock_with_reason_multi_servers(self):
        self.set_compute_api_version('2.73')

        server_a = compute_fakes.create_one_sdk_server()
        server_b = compute_fakes.create_one_sdk_server()

        self.compute_client.find_server.side_effect = [server_a, server_b]
        self.compute_client.lock_server.return_value = None
        arglist = [
            server_a.id,
            server_b.id,
            '--reason',
            'choo..choo',
        ]
        verifylist = [
            ('server', [server_a.id, server_b.id]),
            ('reason', 'choo..choo'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.assertEqual(2, self.compute_client.find_server.call_count)
        self.compute_client.lock_server.assert_has_calls(
            [
                mock.call(server_a.id, locked_reason="choo..choo"),
                mock.call(server_b.id, locked_reason="choo..choo"),
            ]
        )

    def test_server_lock_with_reason_pre_v273(self):
        self.set_compute_api_version('2.72')

        server = compute_fakes.create_one_sdk_server()

        arglist = [
            server.id,
            '--reason',
            "blah",
        ]
        verifylist = [
            ('server', [server.id]),
            ('reason', "blah"),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.73 or greater is required',
            str(ex),
        )


class TestServerMigrate(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.migrate_server.return_value = None
        self.compute_client.live_migrate_server.return_value = None

        # Get the command object to test
        self.cmd = server.MigrateServer(self.app, None)

    def test_server_migrate_no_options(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_called_once_with(
            self.server,
        )
        self.compute_client.live_migrate_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_migrate_with_host(self):
        # Tests that --host is allowed for a cold migration
        # for microversion 2.56 and greater.
        self.set_compute_api_version('2.56')

        arglist = [
            '--host',
            'fakehost',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_called_once_with(
            self.server, host='fakehost'
        )
        self.compute_client.live_migrate_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_migrate_with_block_migration(self):
        arglist = [
            '--block-migration',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', True),
            ('disk_overcommit', None),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_not_called()
        self.compute_client.live_migrate_server.assert_not_called()

    def test_server_migrate_with_disk_overcommit(self):
        arglist = [
            '--disk-overcommit',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', True),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_not_called()
        self.compute_client.live_migrate_server.assert_not_called()

    def test_server_migrate_with_host_pre_v256(self):
        # Tests that --host is not allowed for a cold migration
        # before microversion 2.56 (the test defaults to 2.1).
        self.set_compute_api_version('2.55')

        arglist = [
            '--host',
            'fakehost',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        # Make sure it's the error we expect.
        self.assertIn(
            '--os-compute-api-version 2.56 or greater is required '
            'to use --host without --live-migration.',
            str(ex),
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_not_called()
        self.compute_client.live_migrate_server.assert_not_called()

    def test_server_live_migrate(self):
        # Tests the --live-migration option without --host or --live.
        arglist = [
            '--live-migration',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('host', None),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.live_migrate_server.assert_called_once_with(
            self.server,
            block_migration=False,
            host=None,
            disk_overcommit=False,
        )
        self.compute_client.migrate_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_live_migrate_with_host(self):
        # This requires --os-compute-api-version >= 2.30 so the test uses 2.30.
        self.set_compute_api_version('2.30')

        arglist = [
            '--live-migration',
            '--host',
            'fakehost',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        # No disk_overcommit and block_migration defaults to auto with
        # microversion >= 2.25
        self.compute_client.live_migrate_server.assert_called_once_with(
            self.server,
            block_migration='auto',
            host='fakehost',
        )
        self.compute_client.migrate_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_live_migrate_with_host_pre_v230(self):
        # Tests that the --host option is not supported for --live-migration
        # before microversion 2.30 (the test defaults to 2.1).
        self.set_compute_api_version('2.29')

        arglist = [
            '--live-migration',
            '--host',
            'fakehost',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('host', 'fakehost'),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        # Make sure it's the error we expect.
        self.assertIn(
            '--os-compute-api-version 2.30 or greater is required '
            'when using --host',
            str(ex),
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_not_called()
        self.compute_client.live_migrate_server.assert_not_called()

    def test_server_block_live_migrate(self):
        self.set_compute_api_version('2.24')

        arglist = [
            '--live-migration',
            '--block-migration',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', True),
            ('block_migration', True),
            ('disk_overcommit', None),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        # No disk_overcommit and block_migration defaults to auto with
        # microversion >= 2.25
        self.compute_client.live_migrate_server.assert_called_once_with(
            self.server,
            block_migration=True,
            disk_overcommit=False,
            host=None,
        )
        self.compute_client.migrate_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_live_migrate_with_disk_overcommit(self):
        self.set_compute_api_version('2.24')

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
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.live_migrate_server.assert_called_once_with(
            self.server,
            block_migration=False,
            disk_overcommit=True,
            host=None,
        )
        self.compute_client.migrate_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_live_migrate_with_disk_overcommit_post_v224(self):
        self.set_compute_api_version('2.25')

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
        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        # There should be no 'disk_over_commit' value present
        self.compute_client.live_migrate_server.assert_called_once_with(
            self.server,
            block_migration='auto',
            host=None,
        )
        self.compute_client.migrate_server.assert_not_called()
        self.assertIsNone(result)

        # A warning should have been logged for using --disk-overcommit.
        mock_warning.assert_called_once()
        self.assertIn(
            'The --disk-overcommit and --no-disk-overcommit options ',
            str(mock_warning.call_args[0][0]),
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_migrate_with_wait(self, mock_wait_for_status):
        arglist = [
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_called_once_with(
            self.server,
        )
        self.compute_client.live_migrate_server.assert_not_called()
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            success_status=('active', 'verify_resize'),
            callback=mock.ANY,
        )
        self.assertIsNone(result)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_migrate_with_wait_fails(self, mock_wait_for_status):
        arglist = [
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('live_migration', False),
            ('block_migration', None),
            ('disk_overcommit', None),
            ('wait', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.migrate_server.assert_called_once_with(
            self.server,
        )
        self.compute_client.live_migrate_server.assert_not_called()
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            success_status=('active', 'verify_resize'),
            callback=mock.ANY,
        )


class TestServerReboot(TestServer):
    def setUp(self):
        super().setUp()

        self.compute_client.reboot_server.return_value = None

        self.cmd = server.RebootServer(self.app, None)

    def test_server_reboot(self):
        servers = self.setup_sdk_servers_mock(count=1)

        arglist = [
            servers[0].id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('reboot_type', 'SOFT'),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.reboot_server.assert_called_once_with(
            servers[0].id,
            'SOFT',
        )
        self.assertIsNone(result)

    def test_server_reboot_with_hard(self):
        servers = self.setup_sdk_servers_mock(count=1)

        arglist = [
            '--hard',
            servers[0].id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('reboot_type', 'HARD'),
            ('wait', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.reboot_server.assert_called_once_with(
            servers[0].id,
            'HARD',
        )
        self.assertIsNone(result)

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_reboot_with_wait(self, mock_wait_for_status):
        servers = self.setup_sdk_servers_mock(count=1)

        arglist = [
            '--wait',
            servers[0].id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('reboot_type', 'SOFT'),
            ('wait', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.compute_client.reboot_server.assert_called_once_with(
            servers[0].id,
            'SOFT',
        )
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            servers[0].id,
            callback=mock.ANY,
        )

    @mock.patch.object(server.LOG, 'error')
    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_reboot_with_wait_fails(
        self,
        mock_wait_for_status,
        mock_log,
    ):
        servers = self.setup_sdk_servers_mock(count=1)

        arglist = [
            '--wait',
            servers[0].id,
        ]
        verifylist = [
            ('server', servers[0].id),
            ('reboot_type', 'SOFT'),
            ('wait', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.reboot_server.assert_called_once_with(
            servers[0].id,
            'SOFT',
        )
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            servers[0].id,
            callback=mock.ANY,
        )


class TestServerPause(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.PauseServer(self.app, None)

    def test_server_pause_one_server(self):
        self.run_method_with_sdk_servers('pause_server', 1)

    def test_server_pause_multi_servers(self):
        self.run_method_with_sdk_servers('pause_server', 3)


class TestServerRebuild(TestServer):
    def setUp(self):
        super().setUp()

        self.image = image_fakes.create_one_image()
        self.image_client.get_image.return_value = self.image

        attrs = {
            'status': 'ACTIVE',
            'image': {'id': self.image.id},
        }
        self.server = compute_fakes.create_one_sdk_server(attrs=attrs)
        self.compute_client.find_server.return_value = self.server
        self.compute_client.rebuild_server.return_value = self.server

        self.cmd = server.RebuildServer(self.app, None)

    def test_rebuild_with_image_name(self):
        image_name = 'my-custom-image'
        image = image_fakes.create_one_image(attrs={'name': image_name})
        self.image_client.find_image.return_value = image

        arglist = [
            self.server.id,
            '--image',
            image_name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('image', image_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_called_with(
            image_name, ignore_missing=False
        )
        self.image_client.get_image.assert_called_with(self.image.id)
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, image
        )

    def test_rebuild_with_current_image(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [('server', self.server.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Get the command object to test.
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image
        )

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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn('The --image option is required', str(exc))

    def test_rebuild_with_name(self):
        name = 'test-server-xxx'
        arglist = [
            self.server.id,
            '--name',
            name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('name', name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, name=name
        )

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
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, preserve_ephemeral=True
        )

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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, preserve_ephemeral=False
        )

    def test_rebuild_with_password(self):
        password = 'password-xxx'
        arglist = [self.server.id, '--password', password]
        verifylist = [('server', self.server.id), ('password', password)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server,
            self.image,
            admin_password=password,
        )

    def test_rebuild_with_description(self):
        self.set_compute_api_version('2.19')

        description = 'description1'
        arglist = [self.server.id, '--description', description]
        verifylist = [('server', self.server.id), ('description', description)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, description=description
        )

    def test_rebuild_with_description_pre_v219(self):
        self.set_compute_api_version('2.18')

        description = 'description1'
        arglist = [self.server.id, '--description', description]
        verifylist = [('server', self.server.id), ('description', description)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

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
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image
        )

        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
            success_status=['active'],
        )

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
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_called_once_with(self.image.id)
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image
        )

        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
            success_status=['active'],
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_rebuild_with_wait_shutoff_status(self, mock_wait_for_status):
        self.server.status = 'SHUTOFF'
        arglist = [
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('wait', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image
        )

        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
            success_status=['shutoff'],
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_rebuild_with_wait_error_status(self, mock_wait_for_status):
        self.server.status = 'ERROR'
        arglist = [
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('wait', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image
        )

        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
            success_status=['active'],
        )

    def test_rebuild_wrong_status_fails(self):
        self.server.status = 'SHELVED'
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_called_once_with(self.image.id)
        self.compute_client.rebuild_server.assert_not_called()

    def test_rebuild_with_property(self):
        arglist = [
            self.server.id,
            '--property',
            'key1=value1',
            '--property',
            'key2=value2',
        ]
        expected_properties = {'key1': 'value1', 'key2': 'value2'}
        verifylist = [
            ('server', self.server.id),
            ('properties', expected_properties),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, metadata=expected_properties
        )

    def test_rebuild_with_keypair_name(self):
        self.set_compute_api_version('2.54')

        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--key-name',
            self.server.key_name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('key_name', self.server.key_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, key_name=self.server.key_name
        )

    def test_rebuild_with_keypair_name_pre_v254(self):
        self.set_compute_api_version('2.53')

        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--key-name',
            self.server.key_name,
        ]
        verifylist = [
            ('server', self.server.id),
            ('key_name', self.server.key_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_rebuild_with_no_keypair_name(self):
        self.set_compute_api_version('2.54')

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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, key_name=None
        )

    def test_rebuild_with_keypair_name_and_unset(self):
        self.server.key_name = 'mykey'
        arglist = [
            self.server.id,
            '--key-name',
            self.server.key_name,
            '--no-key-name',
        ]
        verifylist = [
            ('server', self.server.id),
            ('key_name', self.server.key_name),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_rebuild_with_user_data(self):
        self.set_compute_api_version('2.57')

        user_data = b'#!/bin/sh'
        arglist = [
            self.server.id,
            '--user-data',
            'userdata.sh',
        ]
        verifylist = [
            ('server', self.server.id),
            ('user_data', 'userdata.sh'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch(
            'openstackclient.compute.v2.server.open',
            mock.mock_open(read_data=user_data),
        ) as mock_file:
            self.cmd.take_action(parsed_args)

        # Ensure the userdata file is opened
        mock_file.assert_called_with('userdata.sh', 'rb')

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server,
            self.image,
            user_data=base64.b64encode(user_data).decode('utf-8'),
        )

    def test_rebuild_with_user_data_pre_v257(self):
        self.set_compute_api_version('2.56')

        arglist = [
            self.server.id,
            '--user-data',
            'userdata.sh',
        ]
        verifylist = [
            ('server', self.server.id),
            ('user_data', 'userdata.sh'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_rebuild_with_no_user_data(self):
        self.set_compute_api_version('2.54')

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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, user_data=None
        )

    def test_rebuild_with_no_user_data_pre_v254(self):
        self.set_compute_api_version('2.53')

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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_rebuild_with_user_data_and_unset(self):
        arglist = [
            self.server.id,
            '--user-data',
            'userdata.sh',
            '--no-user-data',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_rebuild_with_trusted_image_cert(self):
        self.set_compute_api_version('2.63')

        arglist = [
            self.server.id,
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
        ]
        verifylist = [
            ('server', self.server.id),
            ('trusted_image_certs', ['foo', 'bar']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, trusted_image_certificates=['foo', 'bar']
        )

    def test_rebuild_with_trusted_image_cert_pre_v263(self):
        self.set_compute_api_version('2.62')

        arglist = [
            self.server.id,
            '--trusted-image-cert',
            'foo',
            '--trusted-image-cert',
            'bar',
        ]
        verifylist = [
            ('server', self.server.id),
            ('trusted_image_certs', ['foo', 'bar']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_rebuild_with_no_trusted_image_cert(self):
        self.set_compute_api_version('2.63')

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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, trusted_image_certificates=None
        )

    def test_rebuild_with_no_trusted_image_cert_pre_v263(self):
        self.set_compute_api_version('2.62')

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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_rebuild_with_hostname(self):
        self.set_compute_api_version('2.90')

        arglist = [
            self.server.id,
            '--hostname',
            'new-hostname',
        ]
        verifylist = [
            ('server', self.server.id),
            ('hostname', 'new-hostname'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_not_called()
        self.image_client.get_image.assert_has_calls(
            [mock.call(self.image.id), mock.call(self.image.id)]
        )
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.image, hostname='new-hostname'
        )

    def test_rebuild_with_hostname_pre_v290(self):
        self.set_compute_api_version('2.89')

        arglist = [
            self.server.id,
            '--hostname',
            'new-hostname',
        ]
        verifylist = [('server', self.server.id), ('hostname', 'new-hostname')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestServerRebuildVolumeBacked(TestServer):
    def setUp(self):
        super().setUp()

        self.new_image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = self.new_image

        attrs = {
            'status': 'ACTIVE',
            'image': '',
        }
        self.server = compute_fakes.create_one_sdk_server(attrs=attrs)
        self.compute_client.find_server.return_value = self.server
        self.compute_client.rebuild_server.return_value = self.server

        self.cmd = server.RebuildServer(self.app, None)

    def test_rebuild_with_reimage_boot_volume(self):
        self.set_compute_api_version('2.93')

        arglist = [
            self.server.id,
            '--reimage-boot-volume',
            '--image',
            self.new_image.id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('reimage_boot_volume', True),
            ('image', self.new_image.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.image_client.find_image.assert_called_with(
            self.new_image.id, ignore_missing=False
        )
        self.image_client.get_image.assert_not_called()
        self.compute_client.rebuild_server.assert_called_once_with(
            self.server, self.new_image
        )

    def test_rebuild_with_no_reimage_boot_volume(self):
        self.set_compute_api_version('2.93')

        arglist = [
            self.server.id,
            '--no-reimage-boot-volume',
            '--image',
            self.new_image.id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('reimage_boot_volume', False),
            ('image', self.new_image.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn('--reimage-boot-volume is required', str(exc))

    def test_rebuild_with_reimage_boot_volume_pre_v293(self):
        self.set_compute_api_version('2.92')

        arglist = [
            self.server.id,
            '--reimage-boot-volume',
            '--image',
            self.new_image.id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('reimage_boot_volume', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.93 or greater is required', str(exc)
        )


class TestServerEvacuate(TestServer):
    def setUp(self):
        super().setUp()

        self.image = image_fakes.create_one_image()
        self.image_client.get_image.return_value = self.image

        attrs = {
            'image': self.image,
            'networks': {},
            'adminPass': 'passw0rd',
        }
        self.server = compute_fakes.create_one_sdk_server(attrs=attrs)
        attrs['id'] = self.server.id
        self.new_server = compute_fakes.create_one_sdk_server(attrs=attrs)

        # Return value for utils.find_resource for server.
        self.compute_client.find_server.return_value = self.server
        self.compute_client.get_server.return_value = self.server

        self.cmd = server.EvacuateServer(self.app, None)

    def _test_evacuate(self, args, verify_args, evac_args):
        parsed_args = self.check_parser(self.cmd, args, verify_args)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.evacuate_server.assert_called_once_with(
            self.server, **evac_args
        )
        self.compute_client.get_server.assert_called_once_with(self.server.id)

    def test_evacuate(self):
        args = [
            self.server.id,
        ]
        verify_args = [
            ('server', self.server.id),
        ]
        evac_args = {
            'host': None,
            'on_shared_storage': False,
            'admin_pass': None,
        }
        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_with_password(self):
        args = [
            self.server.id,
            '--password',
            'password',
        ]
        verify_args = [
            ('server', self.server.id),
            ('password', 'password'),
        ]
        evac_args = {
            'host': None,
            'on_shared_storage': False,
            'admin_pass': 'password',
        }
        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_with_host(self):
        self.set_compute_api_version('2.29')

        host = 'target-host'
        args = [
            self.server.id,
            '--host',
            'target-host',
        ]
        verify_args = [
            ('server', self.server.id),
            ('host', 'target-host'),
        ]
        evac_args = {'host': host, 'admin_pass': None}

        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_with_host_pre_v229(self):
        self.set_compute_api_version('2.28')

        args = [
            self.server.id,
            '--host',
            'target-host',
        ]
        verify_args = [
            ('server', self.server.id),
            ('host', 'target-host'),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_evacuate_without_share_storage(self):
        self.set_compute_api_version('2.13')

        args = [self.server.id, '--shared-storage']
        verify_args = [
            ('server', self.server.id),
            ('shared_storage', True),
        ]
        evac_args = {
            'host': None,
            'on_shared_storage': True,
            'admin_pass': None,
        }
        self._test_evacuate(args, verify_args, evac_args)

    def test_evacuate_without_share_storage_post_v213(self):
        self.set_compute_api_version('2.14')

        args = [self.server.id, '--shared-storage']
        verify_args = [
            ('server', self.server.id),
            ('shared_storage', True),
        ]
        parsed_args = self.check_parser(self.cmd, args, verify_args)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

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
            'host': None,
            'on_shared_storage': False,
            'admin_pass': None,
        }
        self._test_evacuate(args, verify_args, evac_args)
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
        )


class TestServerRemoveFixedIP(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()

        # Get the command object to test
        self.cmd = server.RemoveFixedIP(self.app, None)

    def test_server_remove_fixed_ip(self):
        arglist = [
            self.server.id,
            '1.2.3.4',
        ]
        verifylist = [
            ('server', self.server.id),
            ('ip_address', '1.2.3.4'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.remove_fixed_ip_from_server(self.server, '1.2.3.4')
        self.assertIsNone(result)


class TestServerRescue(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.cmd = server.RescueServer(self.app, None)

    def test_rescue(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.rescue_server.assert_called_once_with(
            self.server, admin_pass=None, image_ref=None
        )
        self.assertIsNone(result)

    def test_rescue_with_image(self):
        new_image = image_fakes.create_one_image()
        self.image_client.find_image.return_value = new_image
        arglist = [
            '--image',
            new_image.id,
            self.server.id,
        ]
        verifylist = [
            ('image', new_image.id),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.image_client.find_image.assert_called_with(
            new_image.id, ignore_missing=False
        )
        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.rescue_server.assert_called_once_with(
            self.server, admin_pass=None, image_ref=new_image.id
        )
        self.assertIsNone(result)

    def test_rescue_with_password(self):
        password = 'password-xxx'
        arglist = [
            '--password',
            password,
            self.server.id,
        ]
        verifylist = [
            ('password', password),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.rescue_server.assert_called_once_with(
            self.server, admin_pass=password, image_ref=None
        )
        self.assertIsNone(result)


class TestServerRemoveFloatingIPCompute(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False
        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.cmd = server.RemoveFloatingIP(self.app, None)

    def test_server_remove_floating_ip(self):
        arglist = [
            self.server.name,
            '1.2.3.4',
        ]
        verifylist = [
            ('server', self.server.name),
            ('ip_address', '1.2.3.4'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False
        )
        self.compute_client.remove_floating_ip_from_server.assert_called_once_with(
            self.server, '1.2.3.4'
        )


class TestServerRemoveFloatingIPNetwork(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.network_client.update_ip = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = server.RemoveFloatingIP(self.app, None)

    def test_server_remove_floating_ip_default(self):
        _floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()
        self.network_client.find_ip = mock.Mock(return_value=_floating_ip)
        arglist = [
            'fake_server',
            _floating_ip['ip'],
        ]
        verifylist = [
            ('server', 'fake_server'),
            ('ip_address', _floating_ip['ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': None,
        }

        self.network_client.find_ip.assert_called_once_with(
            _floating_ip['ip'],
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            _floating_ip, **attrs
        )


class TestServerRemovePort(TestServer):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.RemovePort(self.app, None)

        self.find_port = mock.Mock()
        self.app.client_manager.network.find_port = self.find_port

    def _test_server_remove_port(self, port_id):
        servers = self.setup_sdk_servers_mock(count=1)
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

        self.compute_client.delete_server_interface.assert_called_with(
            port_id, server=servers[0], ignore_missing=False
        )
        self.assertIsNone(result)

    def test_server_remove_port(self):
        self._test_server_remove_port(self.find_port.return_value.id)
        self.find_port.assert_called_once_with(
            'fake-port', ignore_missing=False
        )

    def test_server_remove_port_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_remove_port('fake-port')
        self.find_port.assert_not_called()


class TestServerRemoveNetwork(TestServer):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.RemoveNetwork(self.app, None)

        # Set method to be tested.
        self.fake_inf = mock.Mock()

        self.find_network = mock.Mock()
        self.app.client_manager.network.find_network = self.find_network
        self.compute_client.server_interfaces.return_value = [self.fake_inf]

    def _test_server_remove_network(self, network_id):
        self.fake_inf.net_id = network_id
        self.fake_inf.port_id = 'fake-port'
        servers = self.setup_sdk_servers_mock(count=1)
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

        self.compute_client.server_interfaces.assert_called_once_with(
            servers[0]
        )
        self.compute_client.delete_server_interface.assert_called_once_with(
            'fake-port', server=servers[0]
        )
        self.assertIsNone(result)

    def test_server_remove_network(self):
        self._test_server_remove_network(self.find_network.return_value.id)
        self.find_network.assert_called_once_with(
            'fake-network', ignore_missing=False
        )

    def test_server_remove_network_no_neutron(self):
        self.app.client_manager.network_endpoint_enabled = False
        self._test_server_remove_network('fake-network')
        self.find_network.assert_not_called()


class TestServerRemoveSecurityGroup(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.remove_security_group_from_server.return_value = (
            None
        )

        # Get the command object to test
        self.cmd = server.RemoveServerSecurityGroup(self.app, None)

    def test_server_remove_security_group__nova_network(self):
        arglist = [self.server.id, 'fake_sg']
        verifylist = [
            ('server', self.server.id),
            ('security_groups', ['fake_sg']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(
            self.app.client_manager,
            'is_network_endpoint_enabled',
            return_value=False,
        ):
            with mock.patch.object(
                compute_v2,
                'find_security_group',
                return_value={'name': 'fake_sg'},
            ) as mock_find_nova_net_sg:
                result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.remove_security_group_from_server.assert_called_once_with(
            self.server, {'name': 'fake_sg'}
        )
        mock_find_nova_net_sg.assert_called_once_with(
            self.compute_client, 'fake_sg'
        )
        self.assertIsNone(result)

    def test_server_remove_security_group(self):
        arglist = [self.server.id, 'fake_sg']
        verifylist = [
            ('server', self.server.id),
            ('security_groups', ['fake_sg']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.remove_security_group_from_server.assert_called_once_with(
            self.server, {'name': 'fake_sg'}
        )
        self.assertIsNone(result)


class TestServerResize(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.flavor = compute_fakes.create_one_flavor()
        self.compute_client.find_flavor.return_value = self.flavor
        self.compute_client.resize_server.return_value = None
        self.compute_client.revert_server_resize.return_value = None
        self.compute_client.confirm_server_resize.return_value = None

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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.find_flavor.assert_not_called()
        self.compute_client.resize_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_resize(self):
        arglist = [
            '--flavor',
            self.flavor.id,
            self.server.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('confirm', False),
            ('revert', False),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.find_flavor.assert_called_once_with(
            self.flavor.id, ignore_missing=False
        )
        self.compute_client.resize_server.assert_called_once_with(
            self.server, self.flavor
        )
        self.compute_client.confirm_server_resize.assert_not_called()
        self.compute_client.revert_server_resize.assert_not_called()
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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.find_flavor.assert_not_called()
        self.compute_client.resize_server.assert_not_called()
        self.compute_client.confirm_server_resize.assert_called_once_with(
            self.server
        )
        self.compute_client.revert_server_resize.assert_not_called()
        self.assertIsNone(result)

        # A warning should have been logged for using --confirm.
        mock_warning.assert_called_once()
        self.assertIn(
            'The --confirm option has been deprecated.',
            str(mock_warning.call_args[0][0]),
        )

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

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.find_flavor.assert_not_called()
        self.compute_client.resize_server.assert_not_called()
        self.compute_client.confirm_server_resize.assert_not_called()
        self.compute_client.revert_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)
        # A warning should have been logged for using --revert.
        mock_warning.assert_called_once()
        self.assertIn(
            'The --revert option has been deprecated.',
            str(mock_warning.call_args[0][0]),
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_server_resize_with_wait_ok(self, mock_wait_for_status):
        arglist = [
            '--flavor',
            self.flavor.id,
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('confirm', False),
            ('revert', False),
            ('wait', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.find_flavor.assert_called_once_with(
            self.flavor.id, ignore_missing=False
        )
        self.compute_client.resize_server.assert_called_once_with(
            self.server, self.flavor
        )
        self.compute_client.confirm_server_resize.assert_not_called()
        self.compute_client.revert_server_resize.assert_not_called()

        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            success_status=('active', 'verify_resize'),
            callback=mock.ANY,
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=False)
    def test_server_resize_with_wait_fails(self, mock_wait_for_status):
        arglist = [
            '--flavor',
            self.flavor.id,
            '--wait',
            self.server.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
            ('confirm', False),
            ('revert', False),
            ('wait', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.find_flavor.assert_called_once_with(
            self.flavor.id, ignore_missing=False
        )
        self.compute_client.resize_server.assert_called_once_with(
            self.server, self.flavor
        )
        self.compute_client.confirm_server_resize.assert_not_called()
        self.compute_client.revert_server_resize.assert_not_called()

        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            success_status=('active', 'verify_resize'),
            callback=mock.ANY,
        )


class TestServerResizeConfirm(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.confirm_server_resize.return_value = None

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
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.confirm_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)


# TODO(stephenfin): Remove in OSC 7.0
class TestServerMigrateConfirm(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.confirm_server_resize.return_value = None

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
            result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.confirm_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)

        mock_warning.assert_called_once()
        self.assertIn(
            "The 'server migrate confirm' command has been deprecated",
            str(mock_warning.call_args[0][0]),
        )


class TestServerConfirmMigration(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.confirm_server_resize.return_value = None

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
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.confirm_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)


class TestServerResizeRevert(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.revert_server_resize.return_value = None

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
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.revert_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)


# TODO(stephenfin): Remove in OSC 7.0
class TestServerMigrateRevert(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.revert_server_resize.return_value = None

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
            result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.revert_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)

        mock_warning.assert_called_once()
        self.assertIn(
            "The 'server migrate revert' command has been deprecated",
            str(mock_warning.call_args[0][0]),
        )


class TestServerRevertMigration(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server
        self.compute_client.revert_server_resize.return_value = None

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
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.revert_server_resize.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)


class TestServerRestore(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.RestoreServer(self.app, None)

    def test_server_restore_one_server(self):
        self.run_method_with_sdk_servers('restore_server', 1)

    def test_server_restore_multi_servers(self):
        self.run_method_with_sdk_servers('restore_server', 3)


class TestServerResume(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.ResumeServer(self.app, None)

    def test_server_resume_one_server(self):
        self.run_method_with_sdk_servers('resume_server', 1)

    def test_server_resume_multi_servers(self):
        self.run_method_with_sdk_servers('resume_server', 3)


class TestServerSet(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        # Get the command object to test
        self.cmd = server.SetServer(self.app, None)

    def test_server_set_no_option(self):
        arglist = [self.server.id]
        verifylist = [('server', self.server.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.update_server.assert_not_called()
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_state(self):
        arglist = [
            '--state',
            'active',
            self.server.id,
        ]
        verifylist = [
            ('state', 'active'),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.reset_server_state.assert_called_once_with(
            self.server, state='active'
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_invalid_state(self):
        arglist = [
            '--state',
            'foo_state',
            self.server.id,
        ]
        verifylist = [
            ('state', 'foo_state'),
            ('server', self.server.id),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_server_set_with_name(self):
        arglist = [
            '--name',
            'foo_name',
            self.server.id,
        ]
        verifylist = [
            ('name', 'foo_name'),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.update_server.assert_called_once_with(
            self.server, name='foo_name'
        )
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_property(self):
        arglist = [
            '--property',
            'key1=value1',
            '--property',
            'key2=value2',
            self.server.id,
        ]
        verifylist = [
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.set_server_metadata.assert_called_once_with(
            self.server, key1='value1', key2='value2'
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_password(self):
        arglist = [
            '--password',
            'foo',
            self.server.id,
        ]
        verifylist = [
            ('password', 'foo'),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.change_server_password.assert_called_once_with(
            self.server, 'foo'
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_no_password(self):
        arglist = [
            '--no-password',
            self.server.id,
        ]
        verifylist = [
            ('no_password', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.clear_server_password.assert_called_once_with(
            self.server
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    # TODO(stephenfin): Remove this in a future major version
    @mock.patch.object(
        getpass, 'getpass', return_value=mock.sentinel.fake_pass
    )
    def test_server_set_with_root_password(self, mock_getpass):
        arglist = [
            '--root-password',
            self.server.id,
        ]
        verifylist = [
            ('root_password', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.change_server_password.assert_called_once_with(
            self.server, mock.sentinel.fake_pass
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_description(self):
        self.set_compute_api_version('2.19')

        arglist = [
            '--description',
            'foo_description',
            self.server.id,
        ]
        verifylist = [
            ('description', 'foo_description'),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.update_server.assert_called_once_with(
            self.server, description='foo_description'
        )
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_description_pre_v219(self):
        self.set_compute_api_version('2.18')

        arglist = [
            '--description',
            'foo_description',
            self.server.id,
        ]
        verifylist = [
            ('description', 'foo_description'),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_server_set_with_tag(self):
        self.set_compute_api_version('2.26')

        arglist = [
            '--tag',
            'tag1',
            '--tag',
            'tag2',
            self.server.id,
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.add_tag_to_server.assert_has_calls(
            [
                mock.call(self.server, tag='tag1'),
                mock.call(self.server, tag='tag2'),
            ]
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_tag_pre_v226(self):
        self.set_compute_api_version('2.25')

        arglist = [
            '--tag',
            'tag1',
            '--tag',
            'tag2',
            self.server.id,
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required', str(ex)
        )

    def test_server_set_with_hostname(self):
        self.set_compute_api_version('2.90')

        arglist = [
            '--hostname',
            'foo-hostname',
            self.server.id,
        ]
        verifylist = [
            ('hostname', 'foo-hostname'),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.update_server.assert_called_once_with(
            self.server, hostname='foo-hostname'
        )
        self.compute_client.set_server_metadata.assert_not_called()
        self.compute_client.reset_server_state.assert_not_called()
        self.compute_client.change_server_password.assert_not_called()
        self.compute_client.clear_server_password.assert_not_called()
        self.compute_client.add_tag_to_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_set_with_hostname_pre_v290(self):
        self.set_compute_api_version('2.89')

        arglist = [
            '--hostname',
            'foo-hostname',
            self.server.id,
        ]
        verifylist = [
            ('hostname', 'foo-hostname'),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestServerShelve(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server(
            attrs={'status': 'ACTIVE'},
        )

        self.compute_client.find_server.return_value = self.server
        self.compute_client.shelve_server.return_value = None

        # Get the command object to test
        self.cmd = server.ShelveServer(self.app, None)

    def test_shelve(self):
        arglist = [self.server.name]
        verifylist = [
            ('servers', [self.server.name]),
            ('wait', False),
            ('offload', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.find_server.assert_called_with(
            self.server.name,
            ignore_missing=False,
        )
        self.compute_client.shelve_server.assert_called_with(self.server.id)
        self.compute_client.shelve_offload_server.assert_not_called()

    def test_shelve_already_shelved(self):
        self.server.status = 'SHELVED'

        arglist = [self.server.name]
        verifylist = [
            ('servers', [self.server.name]),
            ('wait', False),
            ('offload', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.find_server.assert_called_with(
            self.server.name,
            ignore_missing=False,
        )
        self.compute_client.shelve_server.assert_not_called()
        self.compute_client.shelve_offload_server.assert_not_called()

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_shelve_with_wait(self, mock_wait_for_status):
        arglist = ['--wait', self.server.name]
        verifylist = [
            ('servers', [self.server.name]),
            ('wait', True),
            ('offload', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.find_server.assert_called_with(
            self.server.name,
            ignore_missing=False,
        )
        self.compute_client.shelve_server.assert_called_with(self.server.id)
        self.compute_client.shelve_offload_server.assert_not_called()
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
            success_status=('shelved', 'shelved_offloaded'),
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_shelve_offload(self, mock_wait_for_status):
        arglist = ['--offload', self.server.name]
        verifylist = [
            ('servers', [self.server.name]),
            ('wait', False),
            ('offload', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        # one call to retrieve to retrieve the server state before shelving
        self.compute_client.find_server.assert_called_once_with(
            self.server.name,
            ignore_missing=False,
        )
        # one call to retrieve the server state before offloading
        self.compute_client.get_server.assert_called_once_with(self.server.id)
        # one call to shelve the server
        self.compute_client.shelve_server.assert_called_with(self.server.id)
        # one call to shelve offload the server
        self.compute_client.shelve_offload_server.assert_called_once_with(
            self.server.id,
        )
        # one call to wait for the shelve offload to complete
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
            callback=mock.ANY,
            success_status=('shelved', 'shelved_offloaded'),
        )


class TestServerShow(TestServer):
    def setUp(self):
        super().setUp()

        self.image = image_fakes.create_one_image()
        self.image_client.get_image.return_value = self.image

        self.flavor = compute_fakes.create_one_flavor()
        self.compute_client.find_flavor.return_value = self.flavor

        self.topology = {
            'nodes': [{'vcpu_set': [0, 1]}, {'vcpu_set': [2, 3]}],
            'pagesize_kb': None,
        }
        server_info = {
            'image': {'id': self.image.id},
            'flavor': {'id': self.flavor.id},
            'tenant_id': 'tenant-id-xxx',
            'addresses': {'public': ['10.20.30.40', '2001:db8::f']},
        }
        self.compute_client.get_server_diagnostics.return_value = {
            'test': 'test'
        }
        self.server = compute_fakes.create_one_sdk_server(
            attrs=server_info,
        )
        self.server.fetch_topology = mock.MagicMock(return_value=self.topology)
        self.compute_client.find_server.return_value = self.server

        # Get the command object to test
        self.cmd = server.ShowServer(self.app, None)

        self.columns = (
            'OS-DCF:diskConfig',
            'OS-EXT-AZ:availability_zone',
            'OS-EXT-SRV-ATTR:host',
            'OS-EXT-SRV-ATTR:hostname',
            'OS-EXT-SRV-ATTR:hypervisor_hostname',
            'OS-EXT-SRV-ATTR:instance_name',
            'OS-EXT-SRV-ATTR:kernel_id',
            'OS-EXT-SRV-ATTR:launch_index',
            'OS-EXT-SRV-ATTR:ramdisk_id',
            'OS-EXT-SRV-ATTR:reservation_id',
            'OS-EXT-SRV-ATTR:root_device_name',
            'OS-EXT-SRV-ATTR:user_data',
            'OS-EXT-STS:power_state',
            'OS-EXT-STS:task_state',
            'OS-EXT-STS:vm_state',
            'OS-SRV-USG:launched_at',
            'OS-SRV-USG:terminated_at',
            'accessIPv4',
            'accessIPv6',
            'addresses',
            'config_drive',
            'created',
            'description',
            'flavor',
            'hostId',
            'host_status',
            'id',
            'image',
            'key_name',
            'locked',
            'locked_reason',
            'name',
            'pinned_availability_zone',
            'progress',
            'project_id',
            'properties',
            'server_groups',
            'status',
            'tags',
            'trusted_image_certificates',
            'updated',
            'user_id',
            'volumes_attached',
        )

        self.data = (
            None,  # OS-DCF:diskConfig
            None,  # OS-EXT-AZ:availability_zone
            None,  # OS-EXT-SRV-ATTR:host
            None,  # OS-EXT-SRV-ATTR:hostname
            None,  # OS-EXT-SRV-ATTR:hypervisor_hostname
            None,  # OS-EXT-SRV-ATTR:instance_name
            None,  # OS-EXT-SRV-ATTR:kernel_id
            None,  # OS-EXT-SRV-ATTR:launch_index
            None,  # OS-EXT-SRV-ATTR:ramdisk_id
            None,  # OS-EXT-SRV-ATTR:reservation_id
            None,  # OS-EXT-SRV-ATTR:root_device_name
            None,  # OS-EXT-SRV-ATTR:user_data
            server.PowerStateColumn(
                self.server.power_state
            ),  # OS-EXT-STS:power_state  # noqa: E501
            None,  # OS-EXT-STS:task_state
            None,  # OS-EXT-STS:vm_state
            None,  # OS-SRV-USG:launched_at
            None,  # OS-SRV-USG:terminated_at
            None,  # accessIPv4
            None,  # accessIPv6
            server.AddressesColumn(
                {'public': ['10.20.30.40', '2001:db8::f']}
            ),  # addresses
            None,  # config_drive
            None,  # created
            None,  # description
            self.flavor.name + " (" + self.flavor.id + ")",  # flavor
            None,  # hostId
            None,  # host_status
            self.server.id,  # id
            self.image.name + " (" + self.image.id + ")",  # image
            None,  # key_name
            None,  # locked
            None,  # locked_reason
            self.server.name,
            None,  # pinned_availability_zone
            None,  # progress
            'tenant-id-xxx',  # project_id
            format_columns.DictColumn({}),  # properties
            None,  # server_groups
            None,  # status
            format_columns.ListColumn([]),  # tags
            None,  # trusted_image_certificates
            None,  # updated
            None,  # user_id
            format_columns.ListDictColumn([]),  # volumes_attached
        )
        self.assertEqual(len(self.columns), len(self.data))

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

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

        self.assertTupleEqual(self.columns, columns)
        self.assertTupleEqual(self.data, data)
        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False, details=True
        )
        self.compute_client.get_server.assert_not_called()

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
        self.server.flavor = {
            'ephemeral': 0,
            'ram': 512,
            'original_name': 'm1.tiny',
            'vcpus': 1,
            'extra_specs': {},
            'swap': 0,
            'disk': 1,
        }
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        # Since the flavor details are in a dict we can't be sure of the
        # ordering so just assert that one of the keys is in the output.
        self.assertIn('original_name', data[columns.index('flavor')]._value)
        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False, details=True
        )
        self.compute_client.get_server.assert_not_called()

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
        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False, details=True
        )
        self.compute_client.get_server_diagnostics.assert_called_once_with(
            self.server
        )
        self.compute_client.get_server.assert_not_called()

    def test_show_topology(self):
        self.set_compute_api_version('2.78')

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
        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False, details=True
        )
        self.server.fetch_topology.assert_called_once_with(self.compute_client)
        self.compute_client.get_server.assert_not_called()

    def test_show_topology_pre_v278(self):
        self.set_compute_api_version('2.77')

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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False, details=True
        )
        self.server.fetch_topology.assert_not_called()
        self.compute_client.get_server.assert_not_called()


@mock.patch('openstackclient.compute.v2.server.os.system')
class TestServerSsh(TestServer):
    def setUp(self):
        super().setUp()

        self.cmd = server.SshServer(self.app, None)

        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.username = 'cloud'

        self.attrs = {
            'addresses': {
                'public': [
                    {
                        'addr': '192.168.1.30',
                        'OS-EXT-IPS-MAC:mac_addr': '00:0c:29:0d:11:74',
                        'OS-EXT-IPS:type': 'fixed',
                        'version': 4,
                    },
                ],
            },
        }
        self.server = compute_fakes.create_one_sdk_server(
            attrs=self.attrs,
        )
        self.compute_client.find_server.return_value = self.server

    def test_server_ssh_no_opts(self, mock_exec):
        arglist = [
            self.server.name,
        ]
        verifylist = [
            ('server', self.server.name),
            ('login', None),
            ('port', None),
            ('identity', None),
            ('option', None),
            ('ipv4', False),
            ('ipv6', False),
            ('address_type', 'public'),
            ('verbose', False),
            ('ssh_args', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False
        )
        self.assertIsNone(result)
        mock_exec.assert_called_once_with('ssh 192.168.1.30 -l cloud')
        mock_warning.assert_not_called()

    def test_server_ssh_passthrough_opts(self, mock_exec):
        arglist = [
            self.server.name,
            '--',
            '-l',
            'username',
            '-p',
            '2222',
        ]
        verifylist = [
            ('server', self.server.name),
            ('login', None),
            ('port', None),
            ('identity', None),
            ('option', None),
            ('ipv4', False),
            ('ipv6', False),
            ('address_type', 'public'),
            ('verbose', False),
            ('ssh_args', ['-l', 'username', '-p', '2222']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False
        )
        self.assertIsNone(result)
        mock_exec.assert_called_once_with(
            'ssh 192.168.1.30 -l username -p 2222'
        )
        mock_warning.assert_not_called()

    def test_server_ssh_deprecated_opts(self, mock_exec):
        arglist = [
            self.server.name,
            '-l',
            'username',
            '-p',
            '2222',
        ]
        verifylist = [
            ('server', self.server.name),
            ('login', 'username'),
            ('port', 2222),
            ('identity', None),
            ('option', None),
            ('ipv4', False),
            ('ipv6', False),
            ('address_type', 'public'),
            ('verbose', False),
            ('ssh_args', []),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(self.cmd.log, 'warning') as mock_warning:
            result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.name, ignore_missing=False
        )
        self.assertIsNone(result)
        mock_exec.assert_called_once_with(
            'ssh 192.168.1.30 -p 2222 -l username'
        )
        mock_warning.assert_called_once()
        self.assertIn(
            'The ssh options have been deprecated.',
            mock_warning.call_args[0][0],
        )


class TestServerStart(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.StartServer(self.app, None)

    def test_server_start_one_server(self):
        self.run_method_with_sdk_servers('start_server', 1)

    def test_server_start_multi_servers(self):
        self.run_method_with_sdk_servers('start_server', 3)

    def test_server_start_with_all_projects(self):
        server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = server

        arglist = [
            server.id,
            '--all-projects',
        ]
        verifylist = [
            ('server', [server.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            server.id,
            ignore_missing=False,
            details=False,
            all_projects=True,
        )


class TestServerStop(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.StopServer(self.app, None)

    def test_server_stop_one_server(self):
        self.run_method_with_sdk_servers('stop_server', 1)

    def test_server_stop_multi_servers(self):
        self.run_method_with_sdk_servers('stop_server', 3)

    def test_server_start_with_all_projects(self):
        server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = server

        arglist = [
            server.id,
            '--all-projects',
        ]
        verifylist = [
            ('server', [server.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            server.id,
            ignore_missing=False,
            details=False,
            all_projects=True,
        )


class TestServerSuspend(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.SuspendServer(self.app, None)

    def test_server_suspend_one_server(self):
        self.run_method_with_sdk_servers('suspend_server', 1)

    def test_server_suspend_multi_servers(self):
        self.run_method_with_sdk_servers('suspend_server', 3)


class TestServerUnlock(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.UnlockServer(self.app, None)

    def test_server_unlock_one_server(self):
        self.run_method_with_sdk_servers('unlock_server', 1)

    def test_server_unlock_multi_servers(self):
        self.run_method_with_sdk_servers('unlock_server', 3)


class TestServerUnpause(TestServerAction):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = server.UnpauseServer(self.app, None)

    def test_server_unpause_one_server(self):
        self.run_method_with_sdk_servers('unpause_server', 1)

    def test_server_unpause_multi_servers(self):
        self.run_method_with_sdk_servers('unpause_server', 3)


class TestServerUnrescue(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.cmd = server.UnrescueServer(self.app, None)

    def test_rescue(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.unrescue_server.assert_called_once_with(
            self.server
        )
        self.assertIsNone(result)


class TestServerUnset(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        # Get the command object to test
        self.cmd = server.UnsetServer(self.app, None)

    def test_server_unset_no_option(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server(self.server.id, ignore_missing=False)
        self.compute_client.delete_server_metadata.assert_not_called()
        self.compute_client.update_server.assert_not_called()
        self.compute_client.remove_tag_from_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_unset_with_property(self):
        arglist = [
            '--property',
            'key1',
            '--property',
            'key2',
            self.server.id,
        ]
        verifylist = [
            ('properties', ['key1', 'key2']),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server(self.server.id, ignore_missing=False)
        self.compute_client.delete_server_metadata.assert_called_once_with(
            self.server,
            ['key1', 'key2'],
        )
        self.compute_client.update_server.assert_not_called()
        self.compute_client.remove_tag_from_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_unset_with_description(self):
        # Description is supported for nova api version 2.19 or above
        self.set_compute_api_version('2.19')

        arglist = [
            '--description',
            self.server.id,
        ]
        verifylist = [
            ('description', True),
            ('server', self.server.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server(self.server.id, ignore_missing=False)
        self.compute_client.update_server.assert_called_once_with(
            self.server, description=''
        )
        self.compute_client.delete_server_metadata.assert_not_called()
        self.compute_client.remove_tag_from_server.assert_not_called()
        self.assertIsNone(result)

    def test_server_unset_with_description_pre_v219(self):
        # Description is not supported for nova api version below 2.19
        self.set_compute_api_version('2.18')

        arglist = [
            '--description',
            self.server.id,
        ]
        verifylist = [
            ('description', True),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.19 or greater is required', str(ex)
        )

    def test_server_unset_with_tag(self):
        self.set_compute_api_version('2.26')

        arglist = [
            '--tag',
            'tag1',
            '--tag',
            'tag2',
            self.server.id,
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.find_server(self.server.id, ignore_missing=False)
        self.compute_client.remove_tag_from_server.assert_has_calls(
            [
                mock.call(self.server, 'tag1'),
                mock.call(self.server, 'tag2'),
            ]
        )
        self.compute_client.delete_server_metadata.assert_not_called()
        self.compute_client.update_server.assert_not_called()

    def test_server_unset_with_tag_pre_v226(self):
        self.set_compute_api_version('2.25')

        arglist = [
            '--tag',
            'tag1',
            '--tag',
            'tag2',
            self.server.id,
        ]
        verifylist = [
            ('tags', ['tag1', 'tag2']),
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.26 or greater is required', str(ex)
        )


class TestServerUnshelve(TestServer):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server(
            attrs={'status': 'SHELVED'},
        )

        self.compute_client.find_server.return_value = self.server
        self.compute_client.unshelve_server.return_value = None

        # Get the command object to test
        self.cmd = server.UnshelveServer(self.app, None)

    def test_unshelve(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', [self.server.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id,
            ignore_missing=False,
        )
        self.compute_client.unshelve_server.assert_called_once_with(
            self.server.id
        )

    def test_unshelve_with_az(self):
        self.set_compute_api_version('2.77')

        arglist = [
            '--availability-zone',
            'foo-az',
            self.server.id,
        ]
        verifylist = [
            ('availability_zone', 'foo-az'),
            ('server', [self.server.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id,
            ignore_missing=False,
        )
        self.compute_client.unshelve_server.assert_called_once_with(
            self.server.id,
            availability_zone='foo-az',
        )

    def test_unshelve_with_az_pre_v277(self):
        self.set_compute_api_version('2.76')

        arglist = [
            self.server.id,
            '--availability-zone',
            'foo-az',
        ]
        verifylist = [
            ('availability_zone', 'foo-az'),
            ('server', [self.server.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.77 or greater is required ',
            str(ex),
        )

    def test_unshelve_with_host(self):
        self.set_compute_api_version('2.91')

        arglist = [
            '--host',
            'server1',
            self.server.id,
        ]
        verifylist = [('host', 'server1'), ('server', [self.server.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id,
            ignore_missing=False,
        )
        self.compute_client.unshelve_server.assert_called_once_with(
            self.server.id,
            host='server1',
        )

    def test_unshelve_with_host_pre_v291(self):
        self.set_compute_api_version('2.90')

        arglist = [
            '--host',
            'server1',
            self.server.id,
        ]
        verifylist = [('host', 'server1'), ('server', [self.server.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.91 or greater is required '
            'to support the --host option',
            str(ex),
        )

    def test_unshelve_with_no_az(self):
        self.set_compute_api_version('2.91')

        arglist = [
            '--no-availability-zone',
            self.server.id,
        ]
        verifylist = [
            ('no_availability_zone', True),
            ('server', [self.server.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_once_with(
            self.server.id,
            ignore_missing=False,
        )
        self.compute_client.unshelve_server.assert_called_once_with(
            self.server.id,
            availability_zone=None,
        )

    def test_unshelve_with_no_az_pre_v291(self):
        self.set_compute_api_version('2.90')

        arglist = [
            '--no-availability-zone',
            self.server.id,
        ]
        verifylist = [
            ('no_availability_zone', True),
            ('server', [self.server.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-compute-api-version 2.91 or greater is required '
            'to support the --no-availability-zone option',
            str(ex),
        )

    def test_unshelve_with_no_az_and_az_conflict(self):
        self.set_compute_api_version('2.91')

        arglist = [
            '--availability-zone',
            "foo-az",
            '--no-availability-zone',
            self.server.id,
        ]
        verifylist = [
            ('availability_zone', "foo-az"),
            ('no_availability_zone', True),
            ('server', [self.server.id]),
        ]

        ex = self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertIn(
            'argument --no-availability-zone: not allowed '
            'with argument --availability-zone',
            str(ex),
        )

    @mock.patch.object(common_utils, 'wait_for_status', return_value=True)
    def test_unshelve_with_wait(self, mock_wait_for_status):
        arglist = [
            '--wait',
            self.server.name,
        ]
        verifylist = [
            ('server', [self.server.name]),
            ('wait', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.find_server.assert_called_with(
            self.server.name,
            ignore_missing=False,
        )
        self.compute_client.unshelve_server.assert_called_with(self.server.id)
        mock_wait_for_status.assert_called_once_with(
            self.compute_client.get_server,
            self.server.id,
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
        self.assertEqual(
            "192.168.0.3", server._get_ip_address(self.OLD, 'private', [4, 6])
        )
        self.assertEqual(
            "10.10.1.2", server._get_ip_address(self.NEW, 'fixed', [4, 6])
        )
        self.assertEqual(
            "10.10.1.2", server._get_ip_address(self.NEW, 'private', [4, 6])
        )
        self.assertEqual(
            "0:0:0:0:0:ffff:a0a:103",
            server._get_ip_address(self.NEW, 'public', [6]),
        )
        self.assertEqual(
            "0:0:0:0:0:ffff:a0a:103",
            server._get_ip_address(self.NEW, 'floating', [6]),
        )
        self.assertEqual(
            "124.12.125.4", server._get_ip_address(self.ODD, 'public', [4, 6])
        )
        self.assertEqual(
            "10.3.3.18", server._get_ip_address(self.ODD, 'private', [4, 6])
        )
        self.assertRaises(
            exceptions.CommandError,
            server._get_ip_address,
            self.NEW,
            'public',
            [4],
        )
        self.assertRaises(
            exceptions.CommandError,
            server._get_ip_address,
            self.NEW,
            'admin',
            [4],
        )
        self.assertRaises(
            exceptions.CommandError,
            server._get_ip_address,
            self.OLD,
            'public',
            [4, 6],
        )
        self.assertRaises(
            exceptions.CommandError,
            server._get_ip_address,
            self.OLD,
            'private',
            [6],
        )

    def test_prep_server_detail(self):
        _image = image_fakes.create_one_image()
        self.image_client.get_image.return_value = _image

        _flavor = compute_fakes.create_one_flavor()
        self.compute_client.find_flavor.return_value = _flavor

        server_info = {
            'image': {'id': _image.id},
            'flavor': {'id': _flavor.id},
            'tenant_id': 'tenant-id-xxx',
            'addresses': {'public': ['10.20.30.40', '2001:db8::f']},
            'links': 'http://xxx.yyy.com',
            'properties': '',
            'volumes_attached': [{"id": "6344fe9d-ef20-45b2-91a6"}],
        }
        _server = compute_fakes.create_one_sdk_server(server_info)
        self.compute_client.get_server.return_value = _server

        expected = {
            'OS-DCF:diskConfig': None,
            'OS-EXT-AZ:availability_zone': None,
            'OS-EXT-SRV-ATTR:host': None,
            'OS-EXT-SRV-ATTR:hostname': None,
            'OS-EXT-SRV-ATTR:hypervisor_hostname': None,
            'OS-EXT-SRV-ATTR:instance_name': None,
            'OS-EXT-SRV-ATTR:kernel_id': None,
            'OS-EXT-SRV-ATTR:launch_index': None,
            'OS-EXT-SRV-ATTR:ramdisk_id': None,
            'OS-EXT-SRV-ATTR:reservation_id': None,
            'OS-EXT-SRV-ATTR:root_device_name': None,
            'OS-EXT-SRV-ATTR:user_data': None,
            'OS-EXT-STS:power_state': server.PowerStateColumn(
                _server.power_state
            ),
            'OS-EXT-STS:task_state': None,
            'OS-EXT-STS:vm_state': None,
            'OS-SRV-USG:launched_at': None,
            'OS-SRV-USG:terminated_at': None,
            'accessIPv4': None,
            'accessIPv6': None,
            'addresses': server.AddressesColumn(_server.addresses),
            'config_drive': None,
            'created': None,
            'description': None,
            'flavor': f'{_flavor.name} ({_flavor.id})',
            'hostId': None,
            'host_status': None,
            'id': _server.id,
            'image': f'{_image.name} ({_image.id})',
            'key_name': None,
            'locked': None,
            'locked_reason': None,
            'name': _server.name,
            'pinned_availability_zone': None,
            'progress': None,
            'project_id': 'tenant-id-xxx',
            'properties': format_columns.DictColumn({}),
            'server_groups': None,
            'status': None,
            'tags': format_columns.ListColumn([]),
            'trusted_image_certificates': None,
            'updated': None,
            'user_id': None,
            'volumes_attached': format_columns.ListDictColumn([]),
        }

        actual = server._prep_server_detail(
            self.compute_client,
            self.image_client,
            _server,
        )

        self.assertCountEqual(expected, actual)
        # this should be called since we need the flavor (< 2.47)
        self.compute_client.find_flavor.assert_called_once_with(
            _flavor.id, ignore_missing=False
        )

    def test_prep_server_detail_v247(self):
        _image = image_fakes.create_one_image()
        self.image_client.get_image.return_value = _image

        _flavor = compute_fakes.create_one_flavor()
        self.compute_client.find_flavor.return_value = _flavor

        server_info = {
            'image': {'id': _image.id},
            'flavor': {
                'vcpus': _flavor.vcpus,
                'ram': _flavor.ram,
                'disk': _flavor.disk,
                'ephemeral': _flavor.ephemeral,
                'swap': _flavor.swap,
                'original_name': _flavor.name,
                'extra_specs': {},
            },
            'tenant_id': 'tenant-id-xxx',
            'addresses': {'public': ['10.20.30.40', '2001:db8::f']},
            'links': 'http://xxx.yyy.com',
            'properties': '',
            'volumes_attached': [{"id": "6344fe9d-ef20-45b2-91a6"}],
        }
        _server = compute_fakes.create_one_sdk_server(server_info)
        self.compute_client.get_server.return_value = _server

        expected = {
            'OS-DCF:diskConfig': None,
            'OS-EXT-AZ:availability_zone': None,
            'OS-EXT-SRV-ATTR:host': None,
            'OS-EXT-SRV-ATTR:hostname': None,
            'OS-EXT-SRV-ATTR:hypervisor_hostname': None,
            'OS-EXT-SRV-ATTR:instance_name': None,
            'OS-EXT-SRV-ATTR:kernel_id': None,
            'OS-EXT-SRV-ATTR:launch_index': None,
            'OS-EXT-SRV-ATTR:ramdisk_id': None,
            'OS-EXT-SRV-ATTR:reservation_id': None,
            'OS-EXT-SRV-ATTR:root_device_name': None,
            'OS-EXT-SRV-ATTR:user_data': None,
            'OS-EXT-STS:power_state': server.PowerStateColumn(
                _server.power_state
            ),
            'OS-EXT-STS:task_state': None,
            'OS-EXT-STS:vm_state': None,
            'OS-SRV-USG:launched_at': None,
            'OS-SRV-USG:terminated_at': None,
            'accessIPv4': None,
            'accessIPv6': None,
            'addresses': server.AddressesColumn(_server.addresses),
            'config_drive': None,
            'created': None,
            'description': None,
            'flavor': f'{_flavor.name} ({_flavor.id})',
            'hostId': None,
            'host_status': None,
            'id': _server.id,
            'image': f'{_image.name} ({_image.id})',
            'key_name': None,
            'locked': None,
            'locked_reason': None,
            'name': _server.name,
            'pinned_availability_zone': None,
            'progress': None,
            'project_id': 'tenant-id-xxx',
            'properties': format_columns.DictColumn({}),
            'server_groups': None,
            'status': None,
            'tags': format_columns.ListColumn([]),
            'trusted_image_certificates': None,
            'updated': None,
            'user_id': None,
            'volumes_attached': format_columns.ListDictColumn([]),
        }

        actual = server._prep_server_detail(
            self.compute_client,
            self.image_client,
            _server,
        )

        self.assertCountEqual(expected, actual)
        # this shouldn't be called since we have a full flavor (>= 2.47)
        self.compute_client.find_flavor.assert_not_called()
