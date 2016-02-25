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

from openstackclient.network.v2 import floating_ip
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes


# Tests for Neutron network
#
class TestFloatingIPNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestFloatingIPNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestDeleteFloatingIPNetwork(TestFloatingIPNetwork):

    # The floating ip to be deleted.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()

    def setUp(self):
        super(TestDeleteFloatingIPNetwork, self).setUp()

        self.network.delete_ip = mock.Mock(return_value=None)
        self.network.find_ip = mock.Mock(return_value=self.floating_ip)

        # Get the command object to test
        self.cmd = floating_ip.DeleteFloatingIP(self.app, self.namespace)

    def test_floating_ip_delete(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.find_ip.assert_called_with(self.floating_ip.id)
        self.network.delete_ip.assert_called_with(self.floating_ip)
        self.assertIsNone(result)


class TestListFloatingIPNetwork(TestFloatingIPNetwork):

    # The floating ips to list up
    floating_ips = network_fakes.FakeFloatingIP.create_floating_ips(count=3)

    columns = (
        'ID',
        'Floating IP Address',
        'Fixed IP Address',
        'Port',
    )

    data = []
    for ip in floating_ips:
        data.append((
            ip.id,
            ip.floating_ip_address,
            ip.fixed_ip_address,
            ip.port_id,
        ))

    def setUp(self):
        super(TestListFloatingIPNetwork, self).setUp()

        self.network.ips = mock.Mock(return_value=self.floating_ips)

        # Get the command object to test
        self.cmd = floating_ip.ListFloatingIP(self.app, self.namespace)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFloatingIPNetwork(TestFloatingIPNetwork):

    # The floating ip to display.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'dns_domain',
        'dns_name',
        'fixed_ip_address',
        'floating_ip_address',
        'floating_network_id',
        'id',
        'port_id',
        'project_id',
        'router_id',
        'status',
    )

    data = (
        floating_ip.dns_domain,
        floating_ip.dns_name,
        floating_ip.fixed_ip_address,
        floating_ip.floating_ip_address,
        floating_ip.floating_network_id,
        floating_ip.id,
        floating_ip.port_id,
        floating_ip.tenant_id,
        floating_ip.router_id,
        floating_ip.status,
    )

    def setUp(self):
        super(TestShowFloatingIPNetwork, self).setUp()

        self.network.find_ip = mock.Mock(return_value=self.floating_ip)

        # Get the command object to test
        self.cmd = floating_ip.ShowFloatingIP(self.app, self.namespace)

    def test_floating_ip_show(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_ip.assert_called_with(
            self.floating_ip.id,
            ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


# Tests for Nova network
#
class TestFloatingIPCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFloatingIPCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestDeleteFloatingIPCompute(TestFloatingIPCompute):

    # The floating ip to be deleted.
    floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

    def setUp(self):
        super(TestDeleteFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.delete.return_value = None

        # Return value of utils.find_resource()
        self.compute.floating_ips.get.return_value = self.floating_ip

        # Get the command object to test
        self.cmd = floating_ip.DeleteFloatingIP(self.app, None)

    def test_floating_ip_delete(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.delete.assert_called_with(
            self.floating_ip.id
        )
        self.assertIsNone(result)


class TestListFloatingIPCompute(TestFloatingIPCompute):

    # The floating ips to be list up
    floating_ips = compute_fakes.FakeFloatingIP.create_floating_ips(count=3)

    columns = (
        'ID',
        'Floating IP Address',
        'Fixed IP Address',
        'Server',
        'Pool',
    )

    data = []
    for ip in floating_ips:
        data.append((
            ip.id,
            ip.ip,
            ip.fixed_ip,
            ip.instance_id,
            ip.pool,
        ))

    def setUp(self):
        super(TestListFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.list.return_value = self.floating_ips

        # Get the command object to test
        self.cmd = floating_ip.ListFloatingIP(self.app, None)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.list.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFloatingIPCompute(TestFloatingIPCompute):

    # The floating ip to display.
    floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        floating_ip.fixed_ip,
        floating_ip.id,
        floating_ip.instance_id,
        floating_ip.ip,
        floating_ip.pool,
    )

    def setUp(self):
        super(TestShowFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Return value of utils.find_resource()
        self.compute.floating_ips.get.return_value = self.floating_ip

        # Get the command object to test
        self.cmd = floating_ip.ShowFloatingIP(self.app, None)

    def test_floating_ip_show(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
