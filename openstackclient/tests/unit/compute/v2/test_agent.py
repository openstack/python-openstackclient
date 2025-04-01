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

import http
import random
from unittest import mock
import uuid

from osc_lib import exceptions

from openstackclient.compute.v2 import agent
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils as tests_utils


def _generate_fake_agent():
    return {
        'agent_id': random.randint(1, 1000),
        'os': 'agent-os-' + uuid.uuid4().hex,
        'architecture': 'agent-architecture',
        'version': '8.0',
        'url': 'http://127.0.0.1',
        'md5hash': 'agent-md5hash',
        'hypervisor': 'hypervisor',
    }


class TestAgentCreate(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._agent = _generate_fake_agent()
        self.columns = (
            'agent_id',
            'architecture',
            'hypervisor',
            'md5hash',
            'os',
            'url',
            'version',
        )
        self.data = (
            self._agent['agent_id'],
            self._agent['architecture'],
            self._agent['hypervisor'],
            self._agent['md5hash'],
            self._agent['os'],
            self._agent['url'],
            self._agent['version'],
        )

        self.compute_client.post.return_value = fakes.FakeResponse(
            data={'agent': self._agent}
        )
        self.cmd = agent.CreateAgent(self.app, None)

    def test_agent_create(self):
        arglist = [
            self._agent['os'],
            self._agent['architecture'],
            self._agent['version'],
            self._agent['url'],
            self._agent['md5hash'],
            self._agent['hypervisor'],
        ]
        verifylist = [
            ('os', self._agent['os']),
            ('architecture', self._agent['architecture']),
            ('version', self._agent['version']),
            ('url', self._agent['url']),
            ('md5hash', self._agent['md5hash']),
            ('hypervisor', self._agent['hypervisor']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.post.assert_called_with(
            '/os-agents',
            json={
                'agent': {
                    'hypervisor': parsed_args.hypervisor,
                    'os': parsed_args.os,
                    'architecture': parsed_args.architecture,
                    'version': parsed_args.version,
                    'url': parsed_args.url,
                    'md5hash': parsed_args.md5hash,
                },
            },
            microversion='2.1',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestAgentDelete(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.compute_client.delete.return_value = fakes.FakeResponse(
            status_code=http.HTTPStatus.NO_CONTENT
        )

        self.cmd = agent.DeleteAgent(self.app, None)

    def test_delete_one_agent(self):
        arglist = ['123']
        verifylist = [
            ('id', ['123']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.delete.assert_called_once_with(
            '/os-agents/123',
            microversion='2.1',
        )
        self.assertIsNone(result)

    def test_delete_multiple_agents(self):
        arglist = ['1', '2', '3']
        verifylist = [
            ('id', ['1', '2', '3']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = [
            mock.call(f'/os-agents/{x}', microversion='2.1') for x in arglist
        ]
        self.compute_client.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_agents_exception(self):
        arglist = ['1', '2', '999']
        verifylist = [
            ('id', ['1', '2', '999']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_client.delete.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NO_CONTENT),
            fakes.FakeResponse(status_code=http.HTTPStatus.NO_CONTENT),
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
        ]

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        calls = [
            mock.call(f'/os-agents/{x}', microversion='2.1') for x in arglist
        ]
        self.compute_client.delete.assert_has_calls(calls)

    def test_agent_delete_no_input(self):
        arglist = []
        verifylist = None
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestAgentList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        _agents = [_generate_fake_agent() for _ in range(3)]

        self.columns = (
            "Agent ID",
            "Hypervisor",
            "OS",
            "Architecture",
            "Version",
            "Md5Hash",
            "URL",
        )
        self.data = [
            (
                _agent['agent_id'],
                _agent['hypervisor'],
                _agent['os'],
                _agent['architecture'],
                _agent['version'],
                _agent['md5hash'],
                _agent['url'],
            )
            for _agent in _agents
        ]

        self.compute_client.get.return_value = fakes.FakeResponse(
            data={'agents': _agents},
        )
        self.cmd = agent.ListAgent(self.app, None)

    def test_agent_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
        self.compute_client.get.assert_called_once_with(
            '/os-agents',
            microversion='2.1',
        )

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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
        self.compute_client.get.assert_called_once_with(
            '/os-agents?hypervisor=hypervisor',
            microversion='2.1',
        )


class TestAgentSet(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.agent = _generate_fake_agent()
        self.compute_client.get.return_value = fakes.FakeResponse(
            data={'agents': [self.agent]},
        )
        self.compute_client.put.return_value = fakes.FakeResponse()

        self.cmd = agent.SetAgent(self.app, None)

    def test_agent_set_nothing(self):
        arglist = [
            str(self.agent['agent_id']),
        ]
        verifylist = [
            ('id', self.agent['agent_id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.put.assert_called_once_with(
            f'/os-agents/{self.agent["agent_id"]}',
            json={
                'para': {
                    'version': self.agent['version'],
                    'url': self.agent['url'],
                    'md5hash': self.agent['md5hash'],
                },
            },
            microversion='2.1',
        )
        self.assertIsNone(result)

    def test_agent_set_version(self):
        arglist = [
            str(self.agent['agent_id']),
            '--agent-version',
            'new-version',
        ]

        verifylist = [
            ('id', self.agent['agent_id']),
            ('version', 'new-version'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.put.assert_called_once_with(
            f'/os-agents/{self.agent["agent_id"]}',
            json={
                'para': {
                    'version': parsed_args.version,
                    'url': self.agent['url'],
                    'md5hash': self.agent['md5hash'],
                },
            },
            microversion='2.1',
        )
        self.assertIsNone(result)

    def test_agent_set_url(self):
        arglist = [
            str(self.agent['agent_id']),
            '--url',
            'new-url',
        ]

        verifylist = [
            ('id', self.agent['agent_id']),
            ('url', 'new-url'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.put.assert_called_once_with(
            f'/os-agents/{self.agent["agent_id"]}',
            json={
                'para': {
                    'version': self.agent['version'],
                    'url': parsed_args.url,
                    'md5hash': self.agent['md5hash'],
                },
            },
            microversion='2.1',
        )
        self.assertIsNone(result)

    def test_agent_set_md5hash(self):
        arglist = [
            str(self.agent['agent_id']),
            '--md5hash',
            'new-md5hash',
        ]

        verifylist = [
            ('id', self.agent['agent_id']),
            ('md5hash', 'new-md5hash'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.put.assert_called_once_with(
            f'/os-agents/{self.agent["agent_id"]}',
            json={
                'para': {
                    'version': self.agent['version'],
                    'url': self.agent['url'],
                    'md5hash': parsed_args.md5hash,
                },
            },
            microversion='2.1',
        )
        self.assertIsNone(result)
