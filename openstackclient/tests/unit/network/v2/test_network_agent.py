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
from osc_lib import utils

from openstackclient.network.v2 import network_agent
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkAgent(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkAgent, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestDeleteNetworkAgent(TestNetworkAgent):

    network_agents = (
        network_fakes.FakeNetworkAgent.create_network_agents(count=2))

    def setUp(self):
        super(TestDeleteNetworkAgent, self).setUp()
        self.network.delete_agent = mock.Mock(return_value=None)
        self.network.get_agent = (
            network_fakes.FakeNetworkAgent.get_network_agents(
                agents=self.network_agents)
        )

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
        self.network.get_agent.assert_called_once_with(
            self.network_agents[0].id, ignore_missing=False)
        self.network.delete_agent.assert_called_once_with(
            self.network_agents[0])
        self.assertIsNone(result)

    def test_multi_network_agents_delete(self):
        arglist = []
        verifylist = []

        for n in self.network_agents:
            arglist.append(n.id)
        verifylist = [
            ('network_agent', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self.network_agents:
            calls.append(call(n))
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

        find_mock_result = [self.network_agents[0], exceptions.CommandError]
        self.network.get_agent = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 network agents failed to delete.', str(e))

        self.network.get_agent.assert_any_call(
            self.network_agents[0].id, ignore_missing=False)
        self.network.get_agent.assert_any_call(
            'unexist_network_agent', ignore_missing=False)
        self.network.delete_agent.assert_called_once_with(
            self.network_agents[0]
        )


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
            agent.alive,
            network_agent._format_admin_state(agent.admin_state_up),
            agent.binary,
        ))

    def setUp(self):
        super(TestListNetworkAgent, self).setUp()
        self.network.agents = mock.Mock(
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
        self.assertEqual(self.data, list(data))


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
        network_agent._format_admin_state(_network_agent.admin_state_up),
        _network_agent.agent_type,
        _network_agent.alive,
        _network_agent.availability_zone,
        _network_agent.binary,
        utils.format_dict(_network_agent.configurations),
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
            self._network_agent.id, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))
