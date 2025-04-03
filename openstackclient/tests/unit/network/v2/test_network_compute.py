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

from unittest import mock

from osc_lib import exceptions

from openstackclient.api import compute_v2
from openstackclient.network.v2 import network
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


@mock.patch.object(compute_v2, 'create_network')
class TestCreateNetworkCompute(compute_fakes.TestComputev2):
    _network = compute_fakes.create_one_network()

    columns = (
        'bridge',
        'bridge_interface',
        'broadcast',
        'cidr',
        'cidr_v6',
        'created_at',
        'deleted',
        'deleted_at',
        'dhcp_server',
        'dhcp_start',
        'dns1',
        'dns2',
        'enable_dhcp',
        'gateway',
        'gateway_v6',
        'host',
        'id',
        'injected',
        'label',
        'mtu',
        'multi_host',
        'netmask',
        'netmask_v6',
        'priority',
        'project_id',
        'rxtx_base',
        'share_address',
        'updated_at',
        'vlan',
        'vpn_private_address',
        'vpn_public_address',
        'vpn_public_port',
    )

    data = (
        _network['bridge'],
        _network['bridge_interface'],
        _network['broadcast'],
        _network['cidr'],
        _network['cidr_v6'],
        _network['created_at'],
        _network['deleted'],
        _network['deleted_at'],
        _network['dhcp_server'],
        _network['dhcp_start'],
        _network['dns1'],
        _network['dns2'],
        _network['enable_dhcp'],
        _network['gateway'],
        _network['gateway_v6'],
        _network['host'],
        _network['id'],
        _network['injected'],
        _network['label'],
        _network['mtu'],
        _network['multi_host'],
        _network['netmask'],
        _network['netmask_v6'],
        _network['priority'],
        _network['project_id'],
        _network['rxtx_base'],
        _network['share_address'],
        _network['updated_at'],
        _network['vlan'],
        _network['vpn_private_address'],
        _network['vpn_public_address'],
        _network['vpn_public_port'],
    )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = network.CreateNetwork(self.app, None)

    def test_network_create_no_options(self, net_mock):
        net_mock.return_value = self._network
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_network_create_missing_options(self, net_mock):
        net_mock.return_value = self._network
        arglist = [
            self._network['label'],
        ]
        verifylist = [
            ('name', self._network['label']),
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_network_create_default_options(self, net_mock):
        net_mock.return_value = self._network
        arglist = [
            "--subnet",
            self._network['cidr'],
            self._network['label'],
        ]
        verifylist = [
            ('subnet', self._network['cidr']),
            ('name', self._network['label']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        net_mock.assert_called_once_with(
            self.compute_client,
            subnet=self._network['cidr'],
            name=self._network['label'],
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch.object(compute_v2, 'delete_network')
@mock.patch.object(compute_v2, 'find_network')
class TestDeleteNetworkCompute(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self._networks = compute_fakes.create_networks(count=3)

        self.cmd = network.DeleteNetwork(self.app, None)

    def test_network_delete_one(self, find_net_mock, delete_net_mock):
        find_net_mock.side_effect = self._networks
        delete_net_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._networks[0]['label'],
        ]
        verifylist = [
            ('network', [self._networks[0]['label']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        delete_net_mock.assert_called_once_with(
            self.compute_client,
            self._networks[0]['id'],
        )
        self.assertIsNone(result)

    def test_network_delete_multi(self, find_net_mock, delete_net_mock):
        find_net_mock.side_effect = self._networks
        delete_net_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._networks[0]['id'],
            self._networks[1]['id'],
        ]
        verifylist = [
            ('network', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        delete_net_mock.assert_has_calls(
            [
                mock.call(self.compute_client, self._networks[0]['id']),
                mock.call(self.compute_client, self._networks[1]['id']),
            ]
        )
        self.assertIsNone(result)

    def test_network_delete_multi_with_exception(
        self, find_net_mock, delete_net_mock
    ):
        find_net_mock.side_effect = [
            self._networks[0],
            exceptions.NotFound('foo'),
            self._networks[1],
        ]
        delete_net_mock.return_value = mock.Mock(return_value=None)

        arglist = [
            self._networks[0]['id'],
            'xxxx-yyyy-zzzz',
            self._networks[1]['id'],
        ]
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertEqual('1 of 3 networks failed to delete.', str(exc))

        find_net_mock.assert_has_calls(
            [
                mock.call(self.compute_client, self._networks[0]['id']),
                mock.call(self.compute_client, 'xxxx-yyyy-zzzz'),
                mock.call(self.compute_client, self._networks[1]['id']),
            ]
        )
        delete_net_mock.assert_has_calls(
            [
                mock.call(self.compute_client, self._networks[0]['id']),
                mock.call(self.compute_client, self._networks[1]['id']),
            ]
        )


@mock.patch.object(compute_v2, 'list_networks')
class TestListNetworkCompute(compute_fakes.TestComputev2):
    _networks = compute_fakes.create_networks(count=3)

    columns = (
        'ID',
        'Name',
        'Subnet',
    )

    data = []
    for net in _networks:
        data.append(
            (
                net['id'],
                net['label'],
                net['cidr'],
            )
        )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = network.ListNetwork(self.app, None)

    def test_network_list_no_options(self, net_mock):
        net_mock.return_value = self._networks
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        net_mock.assert_called_once_with(self.compute_client)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


@mock.patch.object(compute_v2, 'find_network')
class TestShowNetworkCompute(compute_fakes.TestComputev2):
    _network = compute_fakes.create_one_network()

    columns = (
        'bridge',
        'bridge_interface',
        'broadcast',
        'cidr',
        'cidr_v6',
        'created_at',
        'deleted',
        'deleted_at',
        'dhcp_server',
        'dhcp_start',
        'dns1',
        'dns2',
        'enable_dhcp',
        'gateway',
        'gateway_v6',
        'host',
        'id',
        'injected',
        'label',
        'mtu',
        'multi_host',
        'netmask',
        'netmask_v6',
        'priority',
        'project_id',
        'rxtx_base',
        'share_address',
        'updated_at',
        'vlan',
        'vpn_private_address',
        'vpn_public_address',
        'vpn_public_port',
    )

    data = (
        _network['bridge'],
        _network['bridge_interface'],
        _network['broadcast'],
        _network['cidr'],
        _network['cidr_v6'],
        _network['created_at'],
        _network['deleted'],
        _network['deleted_at'],
        _network['dhcp_server'],
        _network['dhcp_start'],
        _network['dns1'],
        _network['dns2'],
        _network['enable_dhcp'],
        _network['gateway'],
        _network['gateway_v6'],
        _network['host'],
        _network['id'],
        _network['injected'],
        _network['label'],
        _network['mtu'],
        _network['multi_host'],
        _network['netmask'],
        _network['netmask_v6'],
        _network['priority'],
        _network['project_id'],
        _network['rxtx_base'],
        _network['share_address'],
        _network['updated_at'],
        _network['vlan'],
        _network['vpn_private_address'],
        _network['vpn_public_address'],
        _network['vpn_public_port'],
    )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = network.ShowNetwork(self.app, None)

    def test_show_no_options(self, net_mock):
        net_mock.return_value = self._network
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_all_options(self, net_mock):
        net_mock.return_value = self._network
        arglist = [
            self._network['label'],
        ]
        verifylist = [
            ('network', self._network['label']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        net_mock.assert_called_once_with(
            self.compute_client, self._network['label']
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
