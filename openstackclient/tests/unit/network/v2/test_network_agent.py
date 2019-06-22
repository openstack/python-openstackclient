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

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.network.v2 import network_agent
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkAgent(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkAgent, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestAddNetworkToAgent(TestNetworkAgent):

    net = network_fakes.FakeNetwork.create_one_network()
    agent = network_fakes.FakeNetworkAgent.create_one_network_agent()

    def setUp(self):
        super(TestAddNetworkToAgent, self).setUp()

        self.network.get_agent = mock.Mock(return_value=self.agent)
        self.network.find_network = mock.Mock(return_value=self.net)
        self.network.name = self.network.find_network.name
        self.network.add_dhcp_agent_to_network = mock.Mock()
        self.cmd = network_agent.AddNetworkToAgent(
            self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_add_network_to_dhcp_agent(self):
        arglist = [
            '--dhcp',
            self.agent.id,
            self.net.id
        ]
        verifylist = [
            ('dhcp', True),
            ('agent_id', self.agent.id),
            ('network', self.net.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.network.add_dhcp_agent_to_network.assert_called_once_with(
            self.agent, self.net)


class TestAddRouterAgent(TestNetworkAgent):

    _router = network_fakes.FakeRouter.create_one_router()
    _agent = network_fakes.FakeNetworkAgent.create_one_network_agent()

    def setUp(self):
        super(TestAddRouterAgent, self).setUp()
        self.network.add_router_to_agent = mock.Mock()
        self.cmd = network_agent.AddRouterToAgent(self.app, self.namespace)
        self.network.get_agent = mock.Mock(return_value=self._agent)
        self.network.find_router = mock.Mock(return_value=self._router)

    def test_add_no_options(self):
        arglist = []
        verifylist = []

        # Missing agent ID will cause command to bail
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_add_router_required_options(self):
        arglist = [
            self._agent.id,
            self._router.id,
            '--l3',
        ]
        verifylist = [
            ('l3', True),
            ('agent_id', self._agent.id),
            ('router', self._router.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.add_router_to_agent.assert_called_with(
            self._agent, self._router)
        self.assertIsNone(result)


class TestDeleteNetworkAgent(TestNetworkAgent):

    network_agents = (
        network_fakes.FakeNetworkAgent.create_network_agents(count=2))

    def setUp(self):
        super(TestDeleteNetworkAgent, self).setUp()
        self.network.delete_agent = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = network_agent.DeleteNetworkAgent(self.app, self.namespace)

    def test_network_agent_delete(self):
        arglist = [
            self.network_agents[0].id,
        ]
        verifylist = [
            ('network_agent', [self.network_agents[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_agent.assert_called_once_with(
            self.network_agents[0].id, ignore_missing=False)
        self.assertIsNone(result)

    def test_multi_network_agents_delete(self):
        arglist = []

        for n in self.network_agents:
            arglist.append(n.id)
        verifylist = [
            ('network_agent', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self.network_agents:
            calls.append(call(n.id, ignore_missing=False))
        self.network.delete_agent.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_network_agents_delete_with_exception(self):
        arglist = [
            self.network_agents[0].id,
            'unexist_network_agent',
        ]
        verifylist = [
            ('network_agent',
             [self.network_agents[0].id, 'unexist_network_agent']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        delete_mock_result = [True, exceptions.CommandError]
        self.network.delete_agent = (
            mock.Mock(side_effect=delete_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 network agents failed to delete.', str(e))

        self.network.delete_agent.assert_any_call(
            self.network_agents[0].id, ignore_missing=False)
        self.network.delete_agent.assert_any_call(
            'unexist_network_agent', ignore_missing=False)


class TestListNetworkAgent(TestNetworkAgent):

    network_agents = (
        network_fakes.FakeNetworkAgent.create_network_agents(count=3))

    columns = (
        'ID',
        'Agent Type',
        'Host',
        'Availability Zone',
        'Alive',
        'State',
        'Binary'
    )
    data = []
    for agent in network_agents:
        data.append((
            agent.id,
            agent.agent_type,
            agent.host,
            agent.availability_zone,
            network_agent.AliveColumn(agent.alive),
            network_agent.AdminStateColumn(agent.admin_state_up),
            agent.binary,
        ))

    def setUp(self):
        super(TestListNetworkAgent, self).setUp()
        self.network.agents = mock.Mock(
            return_value=self.network_agents)

        _testagent = \
            network_fakes.FakeNetworkAgent.create_one_network_agent()
        self.network.get_agent = mock.Mock(return_value=_testagent)

        self._testnetwork = network_fakes.FakeNetwork.create_one_network()
        self.network.find_network = mock.Mock(return_value=self._testnetwork)
        self.network.network_hosting_dhcp_agents = mock.Mock(
            return_value=self.network_agents)

        self.network.get_agent = mock.Mock(return_value=_testagent)

        self._testrouter = \
            network_fakes.FakeRouter.create_one_router()
        self.network.find_router = mock.Mock(return_value=self._testrouter)
        self.network.routers_hosting_l3_agents = mock.Mock(
            return_value=self.network_agents)

        # Get the command object to test
        self.cmd = network_agent.ListNetworkAgent(self.app, self.namespace)

    def test_network_agents_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.agents.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_network_agents_list_agent_type(self):
        arglist = [
            '--agent-type', 'dhcp',
        ]
        verifylist = [
            ('agent_type', 'dhcp'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.agents.assert_called_once_with(**{
            'agent_type': 'DHCP agent',
        })
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_network_agents_list_host(self):
        arglist = [
            '--host', self.network_agents[0].host,
        ]
        verifylist = [
            ('host', self.network_agents[0].host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.agents.assert_called_once_with(**{
            'host': self.network_agents[0].host,
        })
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_network_agents_list_networks(self):
        arglist = [
            '--network', self._testnetwork.id,
        ]
        verifylist = [
            ('network', self._testnetwork.id),
        ]

        attrs = {self._testnetwork, }

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.network_hosting_dhcp_agents.assert_called_once_with(
            *attrs)
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_network_agents_list_routers(self):
        arglist = [
            '--router', self._testrouter.id,
        ]
        verifylist = [
            ('router', self._testrouter.id),
            ('long', False)
        ]

        attrs = {self._testrouter, }

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.routers_hosting_l3_agents.assert_called_once_with(
            *attrs)

        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_network_agents_list_routers_with_long_option(self):
        arglist = [
            '--router', self._testrouter.id,
            '--long',
        ]
        verifylist = [
            ('router', self._testrouter.id),
            ('long', True)
        ]

        attrs = {self._testrouter, }

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.routers_hosting_l3_agents.assert_called_once_with(
            *attrs)

        # Add a column 'HA State' and corresponding data.
        router_agent_columns = self.columns + ('HA State',)
        router_agent_data = [d + ('',) for d in self.data]

        self.assertEqual(router_agent_columns, columns)
        self.assertListItemEqual(router_agent_data, list(data))


class TestRemoveNetworkFromAgent(TestNetworkAgent):

    net = network_fakes.FakeNetwork.create_one_network()
    agent = network_fakes.FakeNetworkAgent.create_one_network_agent()

    def setUp(self):
        super(TestRemoveNetworkFromAgent, self).setUp()

        self.network.get_agent = mock.Mock(return_value=self.agent)
        self.network.find_network = mock.Mock(return_value=self.net)
        self.network.name = self.network.find_network.name
        self.network.remove_dhcp_agent_from_network = mock.Mock()
        self.cmd = network_agent.RemoveNetworkFromAgent(
            self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_agents_list_routers_no_arg(self):
        arglist = [
            '--routers',
        ]
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_from_dhcp_agent(self):
        arglist = [
            '--dhcp',
            self.agent.id,
            self.net.id
        ]
        verifylist = [
            ('dhcp', True),
            ('agent_id', self.agent.id),
            ('network', self.net.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.network.remove_dhcp_agent_from_network.assert_called_once_with(
            self.agent, self.net)


class TestRemoveRouterAgent(TestNetworkAgent):
    _router = network_fakes.FakeRouter.create_one_router()
    _agent = network_fakes.FakeNetworkAgent.create_one_network_agent()

    def setUp(self):
        super(TestRemoveRouterAgent, self).setUp()
        self.network.remove_router_from_agent = mock.Mock()
        self.cmd = network_agent.RemoveRouterFromAgent(self.app,
                                                       self.namespace)
        self.network.get_agent = mock.Mock(return_value=self._agent)
        self.network.find_router = mock.Mock(return_value=self._router)

    def test_remove_no_options(self):
        arglist = []
        verifylist = []

        # Missing agent ID will cause command to bail
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_remove_router_required_options(self):
        arglist = [
            '--l3',
            self._agent.id,
            self._router.id,
        ]
        verifylist = [
            ('l3', True),
            ('agent_id', self._agent.id),
            ('router', self._router.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.remove_router_from_agent.assert_called_with(
            self._agent, self._router)
        self.assertIsNone(result)


class TestSetNetworkAgent(TestNetworkAgent):

    _network_agent = (
        network_fakes.FakeNetworkAgent.create_one_network_agent())

    def setUp(self):
        super(TestSetNetworkAgent, self).setUp()
        self.network.update_agent = mock.Mock(return_value=None)
        self.network.get_agent = mock.Mock(return_value=self._network_agent)

        # Get the command object to test
        self.cmd = network_agent.SetNetworkAgent(self.app, self.namespace)

    def test_set_nothing(self):
        arglist = [
            self._network_agent.id,
        ]
        verifylist = [
            ('network_agent', self._network_agent.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_agent.assert_called_once_with(
            self._network_agent, **attrs)
        self.assertIsNone(result)

    def test_set_all(self):
        arglist = [
            '--description', 'new_description',
            '--enable',
            self._network_agent.id,
        ]
        verifylist = [
            ('description', 'new_description'),
            ('enable', True),
            ('disable', False),
            ('network_agent', self._network_agent.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'description': 'new_description',
            'admin_state_up': True,
            'is_admin_state_up': True,
        }
        self.network.update_agent.assert_called_once_with(
            self._network_agent, **attrs)
        self.assertIsNone(result)

    def test_set_with_disable(self):
        arglist = [
            '--disable',
            self._network_agent.id,
        ]
        verifylist = [
            ('enable', False),
            ('disable', True),
            ('network_agent', self._network_agent.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'is_admin_state_up': False,
        }
        self.network.update_agent.assert_called_once_with(
            self._network_agent, **attrs)
        self.assertIsNone(result)


class TestShowNetworkAgent(TestNetworkAgent):

    _network_agent = (
        network_fakes.FakeNetworkAgent.create_one_network_agent())

    columns = (
        'admin_state_up',
        'agent_type',
        'alive',
        'availability_zone',
        'binary',
        'configurations',
        'host',
        'id',
    )
    data = (
        network_agent.AdminStateColumn(_network_agent.admin_state_up),
        _network_agent.agent_type,
        network_agent.AliveColumn(_network_agent.is_alive),
        _network_agent.availability_zone,
        _network_agent.binary,
        format_columns.DictColumn(_network_agent.configurations),
        _network_agent.host,
        _network_agent.id,
    )

    def setUp(self):
        super(TestShowNetworkAgent, self).setUp()
        self.network.get_agent = mock.Mock(
            return_value=self._network_agent)

        # Get the command object to test
        self.cmd = network_agent.ShowNetworkAgent(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._network_agent.id,
        ]
        verifylist = [
            ('network_agent', self._network_agent.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.get_agent.assert_called_once_with(
            self._network_agent.id)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(list(self.data), list(data))
