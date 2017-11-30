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

import mock
import openstack
from osc_lib import exceptions

from openstackclient.network import common
from openstackclient.tests.unit import utils


def _add_common_argument(parser):
    parser.add_argument(
        'common',
        metavar='<common>',
        help='Common argument',
    )
    return parser


def _add_network_argument(parser):
    parser.add_argument(
        'network',
        metavar='<network>',
        help='Network argument',
    )
    return parser


def _add_compute_argument(parser):
    parser.add_argument(
        'compute',
        metavar='<compute>',
        help='Compute argument',
    )
    return parser


class FakeNetworkAndComputeCommand(common.NetworkAndComputeCommand):

    def update_parser_common(self, parser):
        return _add_common_argument(parser)

    def update_parser_network(self, parser):
        return _add_network_argument(parser)

    def update_parser_compute(self, parser):
        return _add_compute_argument(parser)

    def take_action_network(self, client, parsed_args):
        return client.network_action(parsed_args)

    def take_action_compute(self, client, parsed_args):
        return client.compute_action(parsed_args)


class FakeNetworkAndComputeLister(common.NetworkAndComputeLister):

    def update_parser_common(self, parser):
        return _add_common_argument(parser)

    def update_parser_network(self, parser):
        return _add_network_argument(parser)

    def update_parser_compute(self, parser):
        return _add_compute_argument(parser)

    def take_action_network(self, client, parsed_args):
        return client.network_action(parsed_args)

    def take_action_compute(self, client, parsed_args):
        return client.compute_action(parsed_args)


class FakeNetworkAndComputeShowOne(common.NetworkAndComputeShowOne):

    def update_parser_common(self, parser):
        return _add_common_argument(parser)

    def update_parser_network(self, parser):
        return _add_network_argument(parser)

    def update_parser_compute(self, parser):
        return _add_compute_argument(parser)

    def take_action_network(self, client, parsed_args):
        return client.network_action(parsed_args)

    def take_action_compute(self, client, parsed_args):
        return client.compute_action(parsed_args)


class TestNetworkAndCompute(utils.TestCommand):

    def setUp(self):
        super(TestNetworkAndCompute, self).setUp()

        self.namespace = argparse.Namespace()

        # Create network client mocks.
        self.app.client_manager.network = mock.Mock()
        self.network = self.app.client_manager.network
        self.network.network_action = mock.Mock(
            return_value='take_action_network')

        # Create compute client mocks.
        self.app.client_manager.compute = mock.Mock()
        self.compute = self.app.client_manager.compute
        self.compute.compute_action = mock.Mock(
            return_value='take_action_compute')

        # Subclasses can override the command object to test.
        self.cmd = FakeNetworkAndComputeCommand(self.app, self.namespace)

    def test_take_action_network(self):
        arglist = [
            'common',
            'network'
        ]
        verifylist = [
            ('common', 'common'),
            ('network', 'network')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.network_action.assert_called_with(parsed_args)
        self.assertEqual('take_action_network', result)

    def test_take_action_compute(self):
        arglist = [
            'common',
            'compute'
        ]
        verifylist = [
            ('common', 'common'),
            ('compute', 'compute')
        ]

        self.app.client_manager.network_endpoint_enabled = False
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.compute.compute_action.assert_called_with(parsed_args)
        self.assertEqual('take_action_compute', result)


class TestNetworkAndComputeCommand(TestNetworkAndCompute):

    def setUp(self):
        super(TestNetworkAndComputeCommand, self).setUp()
        self.cmd = FakeNetworkAndComputeCommand(self.app, self.namespace)


class TestNetworkAndComputeLister(TestNetworkAndCompute):

    def setUp(self):
        super(TestNetworkAndComputeLister, self).setUp()
        self.cmd = FakeNetworkAndComputeLister(self.app, self.namespace)


class TestNetworkAndComputeShowOne(TestNetworkAndCompute):

    def setUp(self):
        super(TestNetworkAndComputeShowOne, self).setUp()
        self.cmd = FakeNetworkAndComputeShowOne(self.app, self.namespace)

    def test_take_action_with_http_exception(self):
        with mock.patch.object(self.cmd, 'take_action_network') as m_action:
            m_action.side_effect = openstack.exceptions.HttpException("bar")
            self.assertRaisesRegex(exceptions.CommandError, "bar",
                                   self.cmd.take_action, mock.Mock())

        self.app.client_manager.network_endpoint_enabled = False
        with mock.patch.object(self.cmd, 'take_action_compute') as m_action:
            m_action.side_effect = openstack.exceptions.HttpException("bar")
            self.assertRaisesRegex(exceptions.CommandError, "bar",
                                   self.cmd.take_action, mock.Mock())
