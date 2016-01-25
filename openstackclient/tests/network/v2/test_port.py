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

from openstackclient.common import utils
from openstackclient.network.v2 import port
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestPort(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestPort, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestDeletePort(TestPort):

    # The port to delete.
    _port = network_fakes.FakePort.create_one_port()

    def setUp(self):
        super(TestDeletePort, self).setUp()

        self.network.delete_port = mock.Mock(return_value=None)
        self.network.find_port = mock.Mock(return_value=self._port)
        # Get the command object to test
        self.cmd = port.DeletePort(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', [self._port.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_port.assert_called_with(self._port)
        self.assertIsNone(result)


class TestShowPort(TestPort):

    # The port to show.
    _port = network_fakes.FakePort.create_one_port()

    columns = (
        'admin_state_up',
        'allowed_address_pairs',
        'binding_host_id',
        'binding_profile',
        'binding_vif_details',
        'binding_vif_type',
        'binding_vnic_type',
        'device_id',
        'device_owner',
        'dns_assignment',
        'dns_name',
        'extra_dhcp_opts',
        'fixed_ips',
        'id',
        'mac_address',
        'name',
        'network_id',
        'port_security_enabled',
        'project_id',
        'security_groups',
        'status',
    )

    data = (
        port._format_admin_state(_port.admin_state_up),
        utils.format_list_of_dicts(_port.allowed_address_pairs),
        _port.binding_host_id,
        utils.format_dict(_port.binding_profile),
        utils.format_dict(_port.binding_vif_details),
        _port.binding_vif_type,
        _port.binding_vnic_type,
        _port.device_id,
        _port.device_owner,
        utils.format_list_of_dicts(_port.dns_assignment),
        _port.dns_name,
        utils.format_list_of_dicts(_port.extra_dhcp_opts),
        utils.format_list_of_dicts(_port.fixed_ips),
        _port.id,
        _port.mac_address,
        _port.name,
        _port.network_id,
        _port.port_security_enabled,
        _port.project_id,
        utils.format_list(_port.security_groups),
        _port.status,
    )

    def setUp(self):
        super(TestShowPort, self).setUp()

        self.network.find_port = mock.Mock(return_value=self._port)

        # Get the command object to test
        self.cmd = port.ShowPort(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', self._port.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_port.assert_called_with(self._port.name,
                                                  ignore_missing=False)
        self.assertEqual(tuple(self.columns), columns)
        self.assertEqual(self.data, data)
