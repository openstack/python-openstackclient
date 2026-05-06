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


from openstackclient.network import common
from openstackclient.tests.unit import utils


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


class TestNeutronCommandWithExtraArgs(utils.TestCommand):
    def setUp(self):
        super().setUp()

        # Create client mocks. Note that we intentionally do not use specced
        # mocks since we want to test fake methods.

        self.app.client_manager.network = mock.Mock()  # noqa: O401
        self.network_client = self.app.client_manager.network  # noqa: O401
        self.network_client.test_create_action = mock.Mock()  # noqa: O402

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
