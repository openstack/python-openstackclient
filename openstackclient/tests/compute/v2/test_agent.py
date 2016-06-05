#   Copyright 2016 Easystack. All rights reserved.
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

import mock

from mock import call
from openstackclient.common import exceptions
from openstackclient.compute.v2 import agent
from openstackclient.tests.compute.v2 import fakes as compute_fakes


class TestAgent(compute_fakes.TestComputev2):

    fake_agent = compute_fakes.FakeAgent.create_one_agent()

    columns = (
        'agent_id',
        'architecture',
        'hypervisor',
        'md5hash',
        'os',
        'url',
        'version',
    )

    data = (
        fake_agent.agent_id,
        fake_agent.architecture,
        fake_agent.hypervisor,
        fake_agent.md5hash,
        fake_agent.os,
        fake_agent.url,
        fake_agent.version,
    )

    def setUp(self):
        super(TestAgent, self).setUp()

        self.agents_mock = self.app.client_manager.compute.agents
        self.agents_mock.reset_mock()


class TestAgentCreate(TestAgent):

    def setUp(self):
        super(TestAgentCreate, self).setUp()

        self.agents_mock.create.return_value = self.fake_agent
        self.cmd = agent.CreateAgent(self.app, None)

    def test_agent_create(self):
        arglist = [
            self.fake_agent.os,
            self.fake_agent.architecture,
            self.fake_agent.version,
            self.fake_agent.url,
            self.fake_agent.md5hash,
            self.fake_agent.hypervisor,
        ]

        verifylist = [
            ('os', self.fake_agent.os),
            ('architecture', self.fake_agent.architecture),
            ('version', self.fake_agent.version),
            ('url', self.fake_agent.url),
            ('md5hash', self.fake_agent.md5hash),
            ('hypervisor', self.fake_agent.hypervisor),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.agents_mock.create.assert_called_with(parsed_args.os,
                                                   parsed_args.architecture,
                                                   parsed_args.version,
                                                   parsed_args.url,
                                                   parsed_args.md5hash,
                                                   parsed_args.hypervisor)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestAgentDelete(TestAgent):

    fake_agents = compute_fakes.FakeAgent.create_agents(count=2)

    def setUp(self):
        super(TestAgentDelete, self).setUp()

        self.agents_mock.get.return_value = self.fake_agents
        self.cmd = agent.DeleteAgent(self.app, None)

    def test_delete_one_agent(self):
        arglist = [
            self.fake_agents[0].agent_id
        ]

        verifylist = [
            ('id', [self.fake_agents[0].agent_id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.agents_mock.delete.assert_called_with(
            self.fake_agents[0].agent_id)
        self.assertIsNone(result)

    def test_delete_multiple_agents(self):
        arglist = []
        for n in self.fake_agents:
            arglist.append(n.agent_id)
        verifylist = [
            ('id', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self.fake_agents:
            calls.append(call(n.agent_id))
        self.agents_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_agents_exception(self):
        arglist = [
            self.fake_agents[0].agent_id,
            self.fake_agents[1].agent_id,
            'x-y-z',
        ]
        verifylist = [
            ('id', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ret_delete = [
            None,
            None,
            exceptions.NotFound('404')
        ]
        self.agents_mock.delete = mock.Mock(side_effect=ret_delete)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)
        calls = [
            call(self.fake_agents[0].agent_id),
            call(self.fake_agents[1].agent_id),
        ]
        self.agents_mock.delete.assert_has_calls(calls)


class TestAgentList(TestAgent):

    agents = compute_fakes.FakeAgent.create_agents(count=3)
    list_columns = (
        "Agent ID",
        "Hypervisor",
        "OS",
        "Architecture",
        "Version",
        "Md5Hash",
        "URL",
    )

    list_data = []
    for _agent in agents:
        list_data.append((
            _agent.agent_id,
            _agent.hypervisor,
            _agent.os,
            _agent.architecture,
            _agent.version,
            _agent.md5hash,
            _agent.url,
        ))

    def setUp(self):

        super(TestAgentList, self).setUp()

        self.agents_mock.list.return_value = self.agents
        self.cmd = agent.ListAgent(self.app, None)

    def test_agent_list(self):

        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, list(data))

    def test_agent_list_with_hypervisor(self):

        arglist = [
            '--hypervisor',
            'hypervisor',
        ]
        verifylist = [
            ('hypervisor', 'hypervisor'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.list_columns, columns)
        self.assertEqual(self.list_data, list(data))


class TestAgentSet(TestAgent):

    def setUp(self):
        super(TestAgentSet, self).setUp()

        self.agents_mock.update.return_value = self.fake_agent
        self.cmd = agent.SetAgent(self.app, None)

    def test_agent_set(self):
        arglist = [
            'id',
            'new-version',
            'new-url',
            'new-md5hash',
        ]

        verifylist = [
            ('id', 'id'),
            ('version', 'new-version'),
            ('url', 'new-url'),
            ('md5hash', 'new-md5hash'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.agents_mock.update.assert_called_with(parsed_args.id,
                                                   parsed_args.version,
                                                   parsed_args.url,
                                                   parsed_args.md5hash)
        self.assertIsNone(result)
