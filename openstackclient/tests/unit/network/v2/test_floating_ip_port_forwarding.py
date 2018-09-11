# Copyright (c) 2018 China Telecom Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
from mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import floating_ip_port_forwarding
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes_v2
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestFloatingIPPortForwarding(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestFloatingIPPortForwarding, self).setUp()
        self.network = self.app.client_manager.network
        self.floating_ip = (network_fakes.FakeFloatingIP.
                            create_one_floating_ip())
        self.port = network_fakes.FakePort.create_one_port()
        self.project = identity_fakes_v2.FakeProject.create_one_project()
        self.network.find_port = mock.Mock(return_value=self.port)


class TestCreateFloatingIPPortForwarding(TestFloatingIPPortForwarding):

    def setUp(self):
        project_id = ''
        super(TestCreateFloatingIPPortForwarding, self).setUp()
        self.new_port_forwarding = (
            network_fakes.FakeFloatingIPPortForwarding.
            create_one_port_forwarding(
                attrs={
                    'internal_port_id': self.port.id,
                    'floatingip_id': self.floating_ip.id,
                }
            )
        )
        self.network.create_floating_ip_port_forwarding = mock.Mock(
            return_value=self.new_port_forwarding)

        self.network.find_ip = mock.Mock(
            return_value=self.floating_ip
        )

        # Get the command object to test
        self.cmd = floating_ip_port_forwarding.CreateFloatingIPPortForwarding(
            self.app, self.namespace)

        self.columns = (
            'external_port',
            'floatingip_id',
            'id',
            'internal_ip_address',
            'internal_port',
            'internal_port_id',
            'project_id',
            'protocol'
        )

        self.data = (
            self.new_port_forwarding.external_port,
            self.new_port_forwarding.floatingip_id,
            self.new_port_forwarding.id,
            self.new_port_forwarding.internal_ip_address,
            self.new_port_forwarding.internal_port,
            self.new_port_forwarding.internal_port_id,
            project_id,
            self.new_port_forwarding.protocol,
        )

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_all_options(self):
        arglist = [
            '--port', self.new_port_forwarding.internal_port_id,
            '--internal-protocol-port',
            str(self.new_port_forwarding.internal_port),
            '--external-protocol-port',
            str(self.new_port_forwarding.external_port),
            '--protocol', self.new_port_forwarding.protocol,
            self.new_port_forwarding.floatingip_id,
            '--internal-ip-address',
            self.new_port_forwarding.internal_ip_address,
        ]
        verifylist = [
            ('port', self.new_port_forwarding.internal_port_id),
            ('internal_protocol_port', self.new_port_forwarding.internal_port),
            ('external_protocol_port', self.new_port_forwarding.external_port),
            ('protocol', self.new_port_forwarding.protocol),
            ('floating_ip', self.new_port_forwarding.floatingip_id),
            ('internal_ip_address', self.new_port_forwarding.
                internal_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_floating_ip_port_forwarding.\
            assert_called_once_with(
                self.new_port_forwarding.floatingip_id,
                **{
                    'external_port': self.new_port_forwarding.external_port,
                    'internal_ip_address': self.new_port_forwarding.
                    internal_ip_address,
                    'internal_port': self.new_port_forwarding.internal_port,
                    'internal_port_id': self.new_port_forwarding.
                    internal_port_id,
                    'protocol': self.new_port_forwarding.protocol,
                })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteFloatingIPPortForwarding(TestFloatingIPPortForwarding):

    def setUp(self):
        super(TestDeleteFloatingIPPortForwarding, self).setUp()
        self._port_forwarding = (
            network_fakes.FakeFloatingIPPortForwarding.create_port_forwardings(
                count=2, attrs={
                    'floatingip_id': self.floating_ip.id,
                }
            )
        )
        self.network.delete_floating_ip_port_forwarding = mock.Mock(
            return_value=None
        )

        self.network.find_ip = mock.Mock(
            return_value=self.floating_ip
        )
        # Get the command object to test
        self.cmd = floating_ip_port_forwarding.DeleteFloatingIPPortForwarding(
            self.app, self.namespace)

    def test_port_forwarding_delete(self):
        arglist = [
            self.floating_ip.id,
            self._port_forwarding[0].id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('port_forwarding_id', [self._port_forwarding[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_floating_ip_port_forwarding.\
            assert_called_once_with(
                self.floating_ip.id,
                self._port_forwarding[0].id,
                ignore_missing=False
            )

        self.assertIsNone(result)

    def test_multi_port_forwardings_delete(self):
        arglist = []
        pf_id = []

        arglist.append(str(self.floating_ip))

        for a in self._port_forwarding:
            arglist.append(a.id)
            pf_id.append(a.id)

        verifylist = [
            ('floating_ip', str(self.floating_ip)),
            ('port_forwarding_id', pf_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._port_forwarding:
            calls.append(call(a.floatingip_id, a.id, ignore_missing=False))

        self.network.delete_floating_ip_port_forwarding.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_port_forwarding_delete_with_exception(self):
        arglist = [
            self.floating_ip.id,
            self._port_forwarding[0].id,
            'unexist_port_forwarding_id',
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('port_forwarding_id',
             [self._port_forwarding[0].id, 'unexist_port_forwarding_id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        delete_mock_result = [None, exceptions.CommandError]

        self.network.delete_floating_ip_port_forwarding = (
            mock.MagicMock(side_effect=delete_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 Port forwarding failed to delete.',
                str(e)
            )

        self.network.delete_floating_ip_port_forwarding.\
            assert_any_call(
                self.floating_ip.id,
                'unexist_port_forwarding_id',
                ignore_missing=False
            )
        self.network.delete_floating_ip_port_forwarding.\
            assert_any_call(
                self.floating_ip.id,
                self._port_forwarding[0].id,
                ignore_missing=False
            )


class TestListFloatingIPPortForwarding(TestFloatingIPPortForwarding):

    columns = (
        'ID',
        'Internal Port ID',
        'Internal IP Address',
        'Internal Port',
        'External Port',
        'Protocol'
    )

    def setUp(self):
        super(TestListFloatingIPPortForwarding, self).setUp()
        self.port_forwardings = (
            network_fakes.FakeFloatingIPPortForwarding.create_port_forwardings(
                count=3, attrs={
                    'internal_port_id': self.port.id,
                    'floatingip_id': self.floating_ip.id,
                }
            )
        )
        self.data = []
        for port_forwarding in self.port_forwardings:
            self.data.append((
                port_forwarding.id,
                port_forwarding.internal_port_id,
                port_forwarding.internal_ip_address,
                port_forwarding.internal_port,
                port_forwarding.external_port,
                port_forwarding.protocol,
            ))
        self.network.floating_ip_port_forwardings = mock.Mock(
            return_value=self.port_forwardings
        )
        self.network.find_ip = mock.Mock(
            return_value=self.floating_ip
        )
        # Get the command object to test
        self.cmd = floating_ip_port_forwarding.ListFloatingIPPortForwarding(
            self.app,
            self.namespace
        )

    def test_port_forwarding_list(self):
        arglist = [
            self.floating_ip.id
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.floating_ip_port_forwardings.assert_called_once_with(
            self.floating_ip,
            **{}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_port_forwarding_list_all_options(self):
        arglist = [
            '--port', self.port_forwardings[0].internal_port_id,
            '--external-protocol-port',
            str(self.port_forwardings[0].external_port),
            '--protocol', self.port_forwardings[0].protocol,
            self.port_forwardings[0].floatingip_id,
        ]

        verifylist = [
            ('port', self.port_forwardings[0].internal_port_id),
            ('external_protocol_port',
             str(self.port_forwardings[0].external_port)),
            ('protocol', self.port_forwardings[0].protocol),
            ('floating_ip', self.port_forwardings[0].floatingip_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        query = {
            'internal_port_id': self.port_forwardings[0].internal_port_id,
            'external_port': str(self.port_forwardings[0].external_port),
            'protocol': self.port_forwardings[0].protocol,
        }

        self.network.floating_ip_port_forwardings.assert_called_once_with(
            self.floating_ip,
            **query
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetFloatingIPPortForwarding(TestFloatingIPPortForwarding):

    # The Port Forwarding to set.
    def setUp(self):
        super(TestSetFloatingIPPortForwarding, self).setUp()
        self._port_forwarding = (
            network_fakes.FakeFloatingIPPortForwarding.
            create_one_port_forwarding(
                attrs={
                    'floatingip_id': self.floating_ip.id,
                }
            )
        )
        self.network.update_floating_ip_port_forwarding = mock.Mock(
            return_value=None
        )

        self.network.find_floating_ip_port_forwarding = mock.Mock(
            return_value=self._port_forwarding)
        self.network.find_ip = mock.Mock(
            return_value=self.floating_ip
        )
        # Get the command object to test
        self.cmd = floating_ip_port_forwarding.SetFloatingIPPortForwarding(
            self.app,
            self.namespace
        )

    def test_set_nothing(self):
        arglist = [
            self._port_forwarding.floatingip_id,
            self._port_forwarding.id,
        ]
        verifylist = [
            ('floating_ip', self._port_forwarding.floatingip_id),
            ('port_forwarding_id', self._port_forwarding.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_floating_ip_port_forwarding.assert_called_with(
            self._port_forwarding.floatingip_id,
            self._port_forwarding.id,
            **attrs
        )
        self.assertIsNone(result)

    def test_set_all_thing(self):
        arglist = [
            '--port', self.port.id,
            '--internal-ip-address', 'new_internal_ip_address',
            '--internal-protocol-port', '100',
            '--external-protocol-port', '200',
            '--protocol', 'tcp',
            self._port_forwarding.floatingip_id,
            self._port_forwarding.id,
        ]
        verifylist = [
            ('port', self.port.id),
            ('internal_ip_address', 'new_internal_ip_address'),
            ('internal_protocol_port', 100),
            ('external_protocol_port', 200),
            ('protocol', 'tcp'),
            ('floating_ip', self._port_forwarding.floatingip_id),
            ('port_forwarding_id', self._port_forwarding.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'internal_port_id': self.port.id,
            'internal_ip_address': 'new_internal_ip_address',
            'internal_port': 100,
            'external_port': 200,
            'protocol': 'tcp',
        }
        self.network.update_floating_ip_port_forwarding.assert_called_with(
            self._port_forwarding.floatingip_id,
            self._port_forwarding.id,
            **attrs
        )
        self.assertIsNone(result)


class TestShowFloatingIPPortForwarding(TestFloatingIPPortForwarding):

    # The port forwarding to show.
    columns = (
        'external_port',
        'floatingip_id',
        'id',
        'internal_ip_address',
        'internal_port',
        'internal_port_id',
        'project_id',
        'protocol',
    )

    def setUp(self):
        project_id = ''
        super(TestShowFloatingIPPortForwarding, self).setUp()
        self._port_forwarding = (
            network_fakes.FakeFloatingIPPortForwarding.
            create_one_port_forwarding(
                attrs={
                    'floatingip_id': self.floating_ip.id,
                }
            )
        )
        self.data = (
            self._port_forwarding.external_port,
            self._port_forwarding.floatingip_id,
            self._port_forwarding.id,
            self._port_forwarding.internal_ip_address,
            self._port_forwarding.internal_port,
            self._port_forwarding.internal_port_id,
            project_id,
            self._port_forwarding.protocol,
        )
        self.network.find_floating_ip_port_forwarding = mock.Mock(
            return_value=self._port_forwarding
        )
        self.network.find_ip = mock.Mock(
            return_value=self.floating_ip
        )
        # Get the command object to test
        self.cmd = floating_ip_port_forwarding.ShowFloatingIPPortForwarding(
            self.app,
            self.namespace
        )

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_default_options(self):
        arglist = [
            self._port_forwarding.floatingip_id,
            self._port_forwarding.id,
        ]
        verifylist = [
            ('floating_ip', self._port_forwarding.floatingip_id),
            ('port_forwarding_id', self._port_forwarding.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_floating_ip_port_forwarding.assert_called_once_with(
            self.floating_ip,
            self._port_forwarding.id,
            ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))
