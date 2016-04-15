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

from openstackclient.common import utils
from openstackclient.network.v2 import port
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestPort(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestPort, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network

    def _get_common_cols_data(self, fake_port):
        columns = (
            'admin_state_up',
            'allowed_address_pairs',
            'binding_host_id',
            'binding_profile',
            'binding_vif_details',
            'binding_vif_type',
            'binding_vnic_type',
            'device_id',
            'device_owner',
            'dns_assignment',
            'dns_name',
            'extra_dhcp_opts',
            'fixed_ips',
            'id',
            'mac_address',
            'name',
            'network_id',
            'port_security_enabled',
            'project_id',
            'security_groups',
            'status',
        )

        data = (
            port._format_admin_state(fake_port.admin_state_up),
            utils.format_list_of_dicts(fake_port.allowed_address_pairs),
            fake_port.binding_host_id,
            utils.format_dict(fake_port.binding_profile),
            utils.format_dict(fake_port.binding_vif_details),
            fake_port.binding_vif_type,
            fake_port.binding_vnic_type,
            fake_port.device_id,
            fake_port.device_owner,
            utils.format_list_of_dicts(fake_port.dns_assignment),
            fake_port.dns_name,
            utils.format_list_of_dicts(fake_port.extra_dhcp_opts),
            utils.format_list_of_dicts(fake_port.fixed_ips),
            fake_port.id,
            fake_port.mac_address,
            fake_port.name,
            fake_port.network_id,
            fake_port.port_security_enabled,
            fake_port.project_id,
            utils.format_list(fake_port.security_groups),
            fake_port.status,
        )

        return columns, data


class TestCreatePort(TestPort):

    _port = network_fakes.FakePort.create_one_port()

    def setUp(self):
        super(TestCreatePort, self).setUp()

        self.network.create_port = mock.Mock(return_value=self._port)
        fake_net = network_fakes.FakeNetwork.create_one_network({
            'id': self._port.network_id,
        })
        self.network.find_network = mock.Mock(return_value=fake_net)
        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network.find_subnet = mock.Mock(return_value=self.fake_subnet)
        # Get the command object to test
        self.cmd = port.CreatePort(self.app, self.namespace)

    def test_create_default_options(self):
        arglist = [
            '--network', self._port.network_id,
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id,),
            ('enable', True),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_port.assert_called_once_with(**{
            'admin_state_up': True,
            'network_id': self._port.network_id,
            'name': 'test-port',
        })

        ref_columns, ref_data = self._get_common_cols_data(self._port)
        self.assertEqual(ref_columns, columns)
        self.assertEqual(ref_data, data)

    def test_create_full_options(self):
        arglist = [
            '--mac-address', 'aa:aa:aa:aa:aa:aa',
            '--fixed-ip', 'subnet=%s,ip-address=10.0.0.2'
            % self.fake_subnet.id,
            '--device', 'deviceid',
            '--device-owner', 'fakeowner',
            '--disable',
            '--vnic-type', 'macvtap',
            '--binding-profile', 'foo=bar',
            '--binding-profile', 'foo2=bar2',
            '--network', self._port.network_id,
            'test-port',

        ]
        verifylist = [
            ('mac_address', 'aa:aa:aa:aa:aa:aa'),
            (
                'fixed_ip',
                [{'subnet': self.fake_subnet.id, 'ip-address': '10.0.0.2'}]
            ),
            ('device', 'deviceid'),
            ('device_owner', 'fakeowner'),
            ('disable', True),
            ('vnic_type', 'macvtap'),
            ('binding_profile', {'foo': 'bar', 'foo2': 'bar2'}),
            ('network', self._port.network_id),
            ('name', 'test-port'),

        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_port.assert_called_once_with(**{
            'mac_address': 'aa:aa:aa:aa:aa:aa',
            'fixed_ips': [{'subnet_id': self.fake_subnet.id,
                           'ip_address': '10.0.0.2'}],
            'device_id': 'deviceid',
            'device_owner': 'fakeowner',
            'admin_state_up': False,
            'binding:vnic_type': 'macvtap',
            'binding:profile': {'foo': 'bar', 'foo2': 'bar2'},
            'network_id': self._port.network_id,
            'name': 'test-port',
        })

        ref_columns, ref_data = self._get_common_cols_data(self._port)
        self.assertEqual(ref_columns, columns)
        self.assertEqual(ref_data, data)


class TestDeletePort(TestPort):

    # The port to delete.
    _port = network_fakes.FakePort.create_one_port()

    def setUp(self):
        super(TestDeletePort, self).setUp()

        self.network.delete_port = mock.Mock(return_value=None)
        self.network.find_port = mock.Mock(return_value=self._port)
        # Get the command object to test
        self.cmd = port.DeletePort(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', [self._port.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_port.assert_called_once_with(self._port)
        self.assertIsNone(result)


class TestListPort(TestPort):

    _ports = network_fakes.FakePort.create_ports(count=3)

    columns = (
        'ID',
        'Name',
        'MAC Address',
        'Fixed IP Addresses',
    )

    data = []
    for prt in _ports:
        data.append((
            prt.id,
            prt.name,
            prt.mac_address,
            utils.format_list_of_dicts(prt.fixed_ips),
        ))

    def setUp(self):
        super(TestListPort, self).setUp()

        # Get the command object to test
        self.cmd = port.ListPort(self.app, self.namespace)
        self.network.ports = mock.Mock(return_value=self._ports)
        fake_router = network_fakes.FakeRouter.create_one_router({
            'id': 'fake-router-id',
        })
        self.network.find_router = mock.Mock(return_value=fake_router)

    def test_port_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ports.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_port_list_router_opt(self):
        arglist = [
            '--router', 'fake-router-name',
        ]

        verifylist = [
            ('router', 'fake-router-name')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ports.assert_called_once_with(**{
            'device_id': 'fake-router-id'
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetPort(TestPort):

    _port = network_fakes.FakePort.create_one_port()

    def setUp(self):
        super(TestSetPort, self).setUp()
        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network.find_subnet = mock.Mock(return_value=self.fake_subnet)
        self.network.find_port = mock.Mock(return_value=self._port)
        self.network.update_port = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = port.SetPort(self.app, self.namespace)

    def test_set_fixed_ip(self):
        arglist = [
            '--fixed-ip', 'ip-address=10.0.0.11',
            self._port.name,
        ]
        verifylist = [
            ('fixed_ip', [{'ip-address': '10.0.0.11'}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'fixed_ips': [{'ip_address': '10.0.0.11'}],
        }
        self.network.update_port.assert_called_once_with(self._port, **attrs)
        self.assertIsNone(result)

    def test_append_fixed_ip(self):
        _testport = network_fakes.FakePort.create_one_port(
            {'fixed_ips': [{'ip_address': '0.0.0.1'}]})
        self.network.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--fixed-ip', 'ip-address=10.0.0.12',
            _testport.name,
        ]
        verifylist = [
            ('fixed_ip', [{'ip-address': '10.0.0.12'}]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'fixed_ips': [
                {'ip_address': '10.0.0.12'}, {'ip_address': '0.0.0.1'}],
        }
        self.network.update_port.assert_called_once_with(_testport, **attrs)
        self.assertIsNone(result)

    def test_set_this(self):
        arglist = [
            '--disable',
            '--no-fixed-ip',
            '--no-binding-profile',
            self._port.name,
        ]
        verifylist = [
            ('disable', True),
            ('no_binding_profile', True),
            ('no_fixed_ip', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'binding:profile': {},
            'fixed_ips': [],
        }
        self.network.update_port.assert_called_once_with(self._port, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            '--enable',
            '--vnic-type', 'macvtap',
            '--binding-profile', 'foo=bar',
            '--host', 'binding-host-id-xxxx',
            '--name', 'newName',
            self._port.name,
        ]
        verifylist = [
            ('enable', True),
            ('vnic_type', 'macvtap'),
            ('binding_profile', {'foo': 'bar'}),
            ('host', 'binding-host-id-xxxx'),
            ('name', 'newName')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': True,
            'binding:vnic_type': 'macvtap',
            'binding:profile': {'foo': 'bar'},
            'binding:host_id': 'binding-host-id-xxxx',
            'name': 'newName',
        }
        self.network.update_port.assert_called_once_with(self._port, **attrs)
        self.assertIsNone(result)


class TestShowPort(TestPort):

    # The port to show.
    _port = network_fakes.FakePort.create_one_port()

    def setUp(self):
        super(TestShowPort, self).setUp()

        self.network.find_port = mock.Mock(return_value=self._port)

        # Get the command object to test
        self.cmd = port.ShowPort(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', self._port.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_port.assert_called_once_with(
            self._port.name, ignore_missing=False)

        ref_columns, ref_data = self._get_common_cols_data(self._port)
        self.assertEqual(ref_columns, columns)
        self.assertEqual(ref_data, data)
