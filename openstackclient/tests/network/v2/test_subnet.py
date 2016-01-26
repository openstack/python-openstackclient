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
from openstackclient.network.v2 import subnet as subnet_v2
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestSubnet(network_fakes.TestNetworkV2):
    def setUp(self):
        super(TestSubnet, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestListSubnet(TestSubnet):
    # The subnets going to be listed up.
    _subnet = network_fakes.FakeSubnet.create_subnets(count=3)

    columns = (
        'ID',
        'Name',
        'Network',
        'Subnet'
    )
    columns_long = columns + (
        'Project',
        'DHCP',
        'Name Servers',
        'Allocation Pools',
        'Host Routes',
        'IP Version',
        'Gateway'
    )

    data = []
    for subnet in _subnet:
        data.append((
            subnet.id,
            subnet.name,
            subnet.network_id,
            subnet.cidr,
        ))

    data_long = []
    for subnet in _subnet:
        data_long.append((
            subnet.id,
            subnet.name,
            subnet.network_id,
            subnet.cidr,
            subnet.tenant_id,
            subnet.enable_dhcp,
            utils.format_list(subnet.dns_nameservers),
            subnet_v2._format_allocation_pools(subnet.allocation_pools),
            utils.format_list(subnet.host_routes),
            subnet.ip_version,
            subnet.gateway_ip
        ))

    def setUp(self):
        super(TestListSubnet, self).setUp()

        # Get the command object to test
        self.cmd = subnet_v2.ListSubnet(self.app, self.namespace)

        self.network.subnets = mock.Mock(return_value=self._subnet)

    def test_subnet_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.subnets.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.subnets.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))
