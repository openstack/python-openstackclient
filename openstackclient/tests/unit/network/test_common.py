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


class FakeCreateNeutronCommandWithExtraArgs(
    common.NeutronCommandWithExtraArgs
):
    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--known-attribute',
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if 'known_attribute' in parsed_args:
            attrs['known_attribute'] = parsed_args.known_attribute
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        client.test_create_action(**attrs)


class TestNetworkAndCompute(utils.TestCommand):
    def setUp(self):
        super().setUp()

        # Create client mocks. Note that we intentionally do not use specced
        # mocks since we want to test fake methods.

        self.app.client_manager.network = mock.Mock()
        self.network_client = self.app.client_manager.network
        self.network_client.network_action = mock.Mock(
            return_value='take_action_network'
        )

        self.app.client_manager.compute = mock.Mock()
        self.compute_client = self.app.client_manager.compute
        self.compute_client.compute_action = mock.Mock(
            return_value='take_action_compute'
        )

        self.cmd = FakeNetworkAndComputeCommand(self.app, None)

    def test_take_action_network(self):
        arglist = ['common', 'network']
        verifylist = [('common', 'common'), ('network', 'network')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.network_action.assert_called_with(parsed_args)
        self.assertEqual('take_action_network', result)

    def test_take_action_compute(self):
        arglist = ['common', 'compute']
        verifylist = [('common', 'common'), ('compute', 'compute')]

        self.app.client_manager.network_endpoint_enabled = False
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.compute_client.compute_action.assert_called_with(parsed_args)
        self.assertEqual('take_action_compute', result)


class TestNetworkAndComputeCommand(TestNetworkAndCompute):
    def setUp(self):
        super().setUp()
        self.cmd = FakeNetworkAndComputeCommand(self.app, None)


class TestNetworkAndComputeLister(TestNetworkAndCompute):
    def setUp(self):
        super().setUp()
        self.cmd = FakeNetworkAndComputeLister(self.app, None)


class TestNetworkAndComputeShowOne(TestNetworkAndCompute):
    def setUp(self):
        super().setUp()
        self.cmd = FakeNetworkAndComputeShowOne(self.app, None)

    def test_take_action_with_http_exception(self):
        with mock.patch.object(self.cmd, 'take_action_network') as m_action:
            m_action.side_effect = openstack.exceptions.HttpException("bar")
            self.assertRaisesRegex(
                exceptions.CommandError,
                "bar",
                self.cmd.take_action,
                mock.Mock(),
            )

        self.app.client_manager.network_endpoint_enabled = False
        with mock.patch.object(self.cmd, 'take_action_compute') as m_action:
            m_action.side_effect = openstack.exceptions.HttpException("bar")
            self.assertRaisesRegex(
                exceptions.CommandError,
                "bar",
                self.cmd.take_action,
                mock.Mock(),
            )


class TestNeutronCommandWithExtraArgs(utils.TestCommand):
    def setUp(self):
        super().setUp()

        # Create client mocks. Note that we intentionally do not use specced
        # mocks since we want to test fake methods.

        self.app.client_manager.network = mock.Mock()
        self.network_client = self.app.client_manager.network
        self.network_client.test_create_action = mock.Mock()

        # Subclasses can override the command object to test.
        self.cmd = FakeCreateNeutronCommandWithExtraArgs(self.app, None)

    def test_create_extra_attributes_default_type(self):
        arglist = [
            '--known-attribute',
            'known-value',
            '--extra-property',
            'name=extra_name,value=extra_value',
        ]
        verifylist = [
            ('known_attribute', 'known-value'),
            (
                'extra_properties',
                [{'name': 'extra_name', 'value': 'extra_value'}],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.network_client.test_create_action.assert_called_with(
            known_attribute='known-value', extra_name='extra_value'
        )

    def test_create_extra_attributes_string(self):
        arglist = [
            '--known-attribute',
            'known-value',
            '--extra-property',
            'type=str,name=extra_name,value=extra_value',
        ]
        verifylist = [
            ('known_attribute', 'known-value'),
            (
                'extra_properties',
                [
                    {
                        'name': 'extra_name',
                        'type': 'str',
                        'value': 'extra_value',
                    }
                ],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.network_client.test_create_action.assert_called_with(
            known_attribute='known-value', extra_name='extra_value'
        )

    def test_create_extra_attributes_bool(self):
        arglist = [
            '--known-attribute',
            'known-value',
            '--extra-property',
            'type=bool,name=extra_name,value=TrUe',
        ]
        verifylist = [
            ('known_attribute', 'known-value'),
            (
                'extra_properties',
                [{'name': 'extra_name', 'type': 'bool', 'value': 'TrUe'}],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.network_client.test_create_action.assert_called_with(
            known_attribute='known-value', extra_name=True
        )

    def test_create_extra_attributes_int(self):
        arglist = [
            '--known-attribute',
            'known-value',
            '--extra-property',
            'type=int,name=extra_name,value=8',
        ]
        verifylist = [
            ('known_attribute', 'known-value'),
            (
                'extra_properties',
                [{'name': 'extra_name', 'type': 'int', 'value': '8'}],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.network_client.test_create_action.assert_called_with(
            known_attribute='known-value', extra_name=8
        )

    def test_create_extra_attributes_list(self):
        arglist = [
            '--known-attribute',
            'known-value',
            '--extra-property',
            'type=list,name=extra_name,value=v_1;v_2',
        ]
        verifylist = [
            ('known_attribute', 'known-value'),
            (
                'extra_properties',
                [{'name': 'extra_name', 'type': 'list', 'value': 'v_1;v_2'}],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.network_client.test_create_action.assert_called_with(
            known_attribute='known-value', extra_name=['v_1', 'v_2']
        )

    def test_create_extra_attributes_dict(self):
        arglist = [
            '--known-attribute',
            'known-value',
            '--extra-property',
            'type=dict,name=extra_name,value=n1:v1;n2:v2',
        ]
        verifylist = [
            ('known_attribute', 'known-value'),
            (
                'extra_properties',
                [
                    {
                        'name': 'extra_name',
                        'type': 'dict',
                        'value': 'n1:v1;n2:v2',
                    }
                ],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.network_client.test_create_action.assert_called_with(
            known_attribute='known-value', extra_name={'n1': 'v1', 'n2': 'v2'}
        )
