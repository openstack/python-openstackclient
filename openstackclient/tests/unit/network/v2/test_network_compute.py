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
from mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import network
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


# Tests for Nova network
#
class TestNetworkCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestNetworkCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestCreateNetworkCompute(TestNetworkCompute):

    # The network to create.
    _network = compute_fakes.FakeNetwork.create_one_network()

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
        _network.bridge,
        _network.bridge_interface,
        _network.broadcast,
        _network.cidr,
        _network.cidr_v6,
        _network.created_at,
        _network.deleted,
        _network.deleted_at,
        _network.dhcp_server,
        _network.dhcp_start,
        _network.dns1,
        _network.dns2,
        _network.enable_dhcp,
        _network.gateway,
        _network.gateway_v6,
        _network.host,
        _network.id,
        _network.injected,
        _network.label,
        _network.mtu,
        _network.multi_host,
        _network.netmask,
        _network.netmask_v6,
        _network.priority,
        _network.project_id,
        _network.rxtx_base,
        _network.share_address,
        _network.updated_at,
        _network.vlan,
        _network.vpn_private_address,
        _network.vpn_public_address,
        _network.vpn_public_port,
    )

    def setUp(self):
        super(TestCreateNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.networks.create.return_value = self._network

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should raise exception here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            "--subnet", self._network.cidr,
            self._network.label,
        ]
        verifylist = [
            ('subnet', self._network.cidr),
            ('name', self._network.label),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.networks.create.assert_called_once_with(**{
            'cidr': self._network.cidr,
            'label': self._network.label,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkCompute(TestNetworkCompute):

    def setUp(self):
        super(TestDeleteNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # The networks to delete
        self._networks = compute_fakes.FakeNetwork.create_networks(count=3)

        self.compute.networks.delete.return_value = None

        # Return value of utils.find_resource()
        self.compute.networks.get = \
            compute_fakes.FakeNetwork.get_networks(networks=self._networks)

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, None)

    def test_delete_one_network(self):
        arglist = [
            self._networks[0].label,
        ]
        verifylist = [
            ('network', [self._networks[0].label]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.networks.delete.assert_called_once_with(
            self._networks[0].id)
        self.assertIsNone(result)

    def test_delete_multiple_networks(self):
        arglist = []
        for n in self._networks:
            arglist.append(n.label)
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self._networks:
            calls.append(call(n.id))
        self.compute.networks.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_networks_exception(self):
        arglist = [
            self._networks[0].id,
            'xxxx-yyyy-zzzz',
            self._networks[1].id,
        ]
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception in utils.find_resource()
        # In compute v2, we use utils.find_resource() to find a network.
        # It calls get() several times, but find() only one time. So we
        # choose to fake get() always raise exception, then pass through.
        # And fake find() to find the real network or not.
        self.compute.networks.get.side_effect = Exception()
        ret_find = [
            self._networks[0],
            Exception(),
            self._networks[1],
        ]
        self.compute.networks.find.side_effect = ret_find

        # Fake exception in delete()
        ret_delete = [
            None,
            Exception(),
        ]
        self.compute.networks.delete = mock.Mock(side_effect=ret_delete)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        # The second call of utils.find_resource() should fail. So delete()
        # was only called twice.
        calls = [
            call(self._networks[0].id),
            call(self._networks[1].id),
        ]
        self.compute.networks.delete.assert_has_calls(calls)


class TestListNetworkCompute(TestNetworkCompute):

    # The networks going to be listed up.
    _networks = compute_fakes.FakeNetwork.create_networks(count=3)

    columns = (
        'ID',
        'Name',
        'Subnet',
    )

    data = []
    for net in _networks:
        data.append((
            net.id,
            net.label,
            net.cidr,
        ))

    def setUp(self):
        super(TestListNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.networks.list.return_value = self._networks

        # Get the command object to test
        self.cmd = network.ListNetwork(self.app, None)

    def test_network_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute.networks.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowNetworkCompute(TestNetworkCompute):

    # The network to show.
    _network = compute_fakes.FakeNetwork.create_one_network()

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
        _network.bridge,
        _network.bridge_interface,
        _network.broadcast,
        _network.cidr,
        _network.cidr_v6,
        _network.created_at,
        _network.deleted,
        _network.deleted_at,
        _network.dhcp_server,
        _network.dhcp_start,
        _network.dns1,
        _network.dns2,
        _network.enable_dhcp,
        _network.gateway,
        _network.gateway_v6,
        _network.host,
        _network.id,
        _network.injected,
        _network.label,
        _network.mtu,
        _network.multi_host,
        _network.netmask,
        _network.netmask_v6,
        _network.priority,
        _network.project_id,
        _network.rxtx_base,
        _network.share_address,
        _network.updated_at,
        _network.vlan,
        _network.vpn_private_address,
        _network.vpn_public_address,
        _network.vpn_public_port,
    )

    def setUp(self):
        super(TestShowNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Return value of utils.find_resource()
        self.compute.networks.get.return_value = self._network

        # Get the command object to test
        self.cmd = network.ShowNetwork(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._network.label,
        ]
        verifylist = [
            ('network', self._network.label),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
