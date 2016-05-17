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

import copy
import mock

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.network.v2 import subnet as subnet_v2
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestSubnet(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSubnet, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestCreateSubnet(TestSubnet):

    # An IPv4 subnet to be created with mostly default values
    _subnet = network_fakes.FakeSubnet.create_one_subnet(
        attrs={
            'tenant_id': identity_fakes_v3.project_id,
        }
    )

    # Subnet pool to be used to create a subnet from a pool
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    # An IPv4 subnet to be created using a specific subnet pool
    _subnet_from_pool = network_fakes.FakeSubnet.create_one_subnet(
        attrs={
            'tenant_id': identity_fakes_v3.project_id,
            'subnetpool_id': _subnet_pool.id,
            'dns_nameservers': ['8.8.8.8',
                                '8.8.4.4'],
            'host_routes': [{'destination': '10.20.20.0/24',
                             'nexthop': '10.20.20.1'},
                            {'destination': '10.30.30.0/24',
                             'nexthop': '10.30.30.1'}],
        }
    )

    # An IPv6 subnet to be created with most options specified
    _subnet_ipv6 = network_fakes.FakeSubnet.create_one_subnet(
        attrs={
            'tenant_id': identity_fakes_v3.project_id,
            'cidr': 'fe80:0:0:a00a::/64',
            'enable_dhcp': True,
            'dns_nameservers': ['fe80:27ff:a00a:f00f::ffff',
                                'fe80:37ff:a00a:f00f::ffff'],
            'allocation_pools': [{'start': 'fe80::a00a:0:c0de:0:100',
                                  'end': 'fe80::a00a:0:c0de:0:f000'},
                                 {'start': 'fe80::a00a:0:c0de:1:100',
                                  'end': 'fe80::a00a:0:c0de:1:f000'}],
            'host_routes': [{'destination': 'fe80:27ff:a00a:f00f::/64',
                             'nexthop': 'fe80:27ff:a00a:f00f::1'},
                            {'destination': 'fe80:37ff:a00a:f00f::/64',
                             'nexthop': 'fe80:37ff:a00a:f00f::1'}],
            'ip_version': 6,
            'gateway_ip': 'fe80::a00a:0:c0de:0:1',
            'ipv6_address_mode': 'slaac',
            'ipv6_ra_mode': 'slaac',
            'subnetpool_id': 'None',
        }
    )

    # The network to be returned from find_network
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={
            'id': _subnet.network_id,
        }
    )

    columns = (
        'allocation_pools',
        'cidr',
        'dns_nameservers',
        'enable_dhcp',
        'gateway_ip',
        'host_routes',
        'id',
        'ip_version',
        'ipv6_address_mode',
        'ipv6_ra_mode',
        'name',
        'network_id',
        'project_id',
        'subnetpool_id',
    )

    data = (
        subnet_v2._format_allocation_pools(_subnet.allocation_pools),
        _subnet.cidr,
        utils.format_list(_subnet.dns_nameservers),
        _subnet.enable_dhcp,
        _subnet.gateway_ip,
        subnet_v2._format_host_routes(_subnet.host_routes),
        _subnet.id,
        _subnet.ip_version,
        _subnet.ipv6_address_mode,
        _subnet.ipv6_ra_mode,
        _subnet.name,
        _subnet.network_id,
        _subnet.project_id,
        _subnet.subnetpool_id,
    )

    data_subnet_pool = (
        subnet_v2._format_allocation_pools(_subnet_from_pool.allocation_pools),
        _subnet_from_pool.cidr,
        utils.format_list(_subnet_from_pool.dns_nameservers),
        _subnet_from_pool.enable_dhcp,
        _subnet_from_pool.gateway_ip,
        subnet_v2._format_host_routes(_subnet_from_pool.host_routes),
        _subnet_from_pool.id,
        _subnet_from_pool.ip_version,
        _subnet_from_pool.ipv6_address_mode,
        _subnet_from_pool.ipv6_ra_mode,
        _subnet_from_pool.name,
        _subnet_from_pool.network_id,
        _subnet_from_pool.project_id,
        _subnet_from_pool.subnetpool_id,
    )

    data_ipv6 = (
        subnet_v2._format_allocation_pools(_subnet_ipv6.allocation_pools),
        _subnet_ipv6.cidr,
        utils.format_list(_subnet_ipv6.dns_nameservers),
        _subnet_ipv6.enable_dhcp,
        _subnet_ipv6.gateway_ip,
        subnet_v2._format_host_routes(_subnet_ipv6.host_routes),
        _subnet_ipv6.id,
        _subnet_ipv6.ip_version,
        _subnet_ipv6.ipv6_address_mode,
        _subnet_ipv6.ipv6_ra_mode,
        _subnet_ipv6.name,
        _subnet_ipv6.network_id,
        _subnet_ipv6.project_id,
        _subnet_ipv6.subnetpool_id,
    )

    def setUp(self):
        super(TestCreateSubnet, self).setUp()

        # Get the command object to test
        self.cmd = subnet_v2.CreateSubnet(self.app, self.namespace)

        # Set identity client v3. And get a shortcut to Identity client.
        identity_client = identity_fakes_v3.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.projects
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.PROJECT),
            loaded=True,
        )

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity.domains
        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.DOMAIN),
            loaded=True,
        )

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Testing that a call without the required argument will fail and
        # throw a "ParserExecption"
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        # Mock create_subnet and find_network sdk calls to return the
        # values we want for this test
        self.network.create_subnet = mock.Mock(return_value=self._subnet)
        self._network.id = self._subnet.network_id
        self.network.find_network = mock.Mock(return_value=self._network)

        arglist = [
            "--subnet-range", self._subnet.cidr,
            "--network", self._subnet.network_id,
            self._subnet.name,
        ]
        verifylist = [
            ('name', self._subnet.name),
            ('subnet_range', self._subnet.cidr),
            ('network', self._subnet.network_id),
            ('ip_version', self._subnet.ip_version),
            ('gateway', 'auto'),

        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_subnet.assert_called_once_with(**{
            'cidr': self._subnet.cidr,
            'enable_dhcp': self._subnet.enable_dhcp,
            'ip_version': self._subnet.ip_version,
            'name': self._subnet.name,
            'network_id': self._subnet.network_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_from_subnet_pool_options(self):
        # Mock create_subnet, find_subnet_pool, and find_network sdk calls
        # to return the values we want for this test
        self.network.create_subnet = \
            mock.Mock(return_value=self._subnet_from_pool)
        self._network.id = self._subnet_from_pool.network_id
        self.network.find_network = mock.Mock(return_value=self._network)
        self.network.find_subnet_pool = \
            mock.Mock(return_value=self._subnet_pool)

        arglist = [
            self._subnet_from_pool.name,
            "--subnet-pool", self._subnet_from_pool.subnetpool_id,
            "--prefix-length", '24',
            "--network", self._subnet_from_pool.network_id,
            "--ip-version", str(self._subnet_from_pool.ip_version),
            "--gateway", self._subnet_from_pool.gateway_ip,
            "--dhcp",
        ]

        for dns_addr in self._subnet_from_pool.dns_nameservers:
            arglist.append('--dns-nameserver')
            arglist.append(dns_addr)

        for host_route in self._subnet_from_pool.host_routes:
            arglist.append('--host-route')
            value = 'gateway=' + host_route.get('nexthop', '') + \
                    ',destination=' + host_route.get('destination', '')
            arglist.append(value)

        verifylist = [
            ('name', self._subnet_from_pool.name),
            ('prefix_length', '24'),
            ('network', self._subnet_from_pool.network_id),
            ('ip_version', self._subnet_from_pool.ip_version),
            ('gateway', self._subnet_from_pool.gateway_ip),
            ('dns_nameservers', self._subnet_from_pool.dns_nameservers),
            ('dhcp', self._subnet_from_pool.enable_dhcp),
            ('host_routes', subnet_v2.convert_entries_to_gateway(
                self._subnet_from_pool.host_routes)),
            ('subnet_pool', self._subnet_from_pool.subnetpool_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_subnet.assert_called_once_with(**{
            'dns_nameservers': self._subnet_from_pool.dns_nameservers,
            'enable_dhcp': self._subnet_from_pool.enable_dhcp,
            'gateway_ip': self._subnet_from_pool.gateway_ip,
            'host_routes': self._subnet_from_pool.host_routes,
            'ip_version': self._subnet_from_pool.ip_version,
            'name': self._subnet_from_pool.name,
            'network_id': self._subnet_from_pool.network_id,
            'prefixlen': '24',
            'subnetpool_id': self._subnet_from_pool.subnetpool_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data_subnet_pool, data)

    def test_create_options_subnet_range_ipv6(self):
        # Mock create_subnet and find_network sdk calls to return the
        # values we want for this test
        self.network.create_subnet = mock.Mock(return_value=self._subnet_ipv6)
        self._network.id = self._subnet_ipv6.network_id
        self.network.find_network = mock.Mock(return_value=self._network)

        arglist = [
            self._subnet_ipv6.name,
            "--subnet-range", self._subnet_ipv6.cidr,
            "--network", self._subnet_ipv6.network_id,
            "--ip-version", str(self._subnet_ipv6.ip_version),
            "--ipv6-ra-mode", self._subnet_ipv6.ipv6_ra_mode,
            "--ipv6-address-mode", self._subnet_ipv6.ipv6_address_mode,
            "--gateway", self._subnet_ipv6.gateway_ip,
            "--dhcp",
        ]

        for dns_addr in self._subnet_ipv6.dns_nameservers:
            arglist.append('--dns-nameserver')
            arglist.append(dns_addr)

        for host_route in self._subnet_ipv6.host_routes:
            arglist.append('--host-route')
            value = 'gateway=' + host_route.get('nexthop', '') + \
                    ',destination=' + host_route.get('destination', '')
            arglist.append(value)

        for pool in self._subnet_ipv6.allocation_pools:
            arglist.append('--allocation-pool')
            value = 'start=' + pool.get('start', '') + \
                    ',end=' + pool.get('end', '')
            arglist.append(value)

        verifylist = [
            ('name', self._subnet_ipv6.name),
            ('subnet_range', self._subnet_ipv6.cidr),
            ('network', self._subnet_ipv6.network_id),
            ('ip_version', self._subnet_ipv6.ip_version),
            ('ipv6_ra_mode', self._subnet_ipv6.ipv6_ra_mode),
            ('ipv6_address_mode', self._subnet_ipv6.ipv6_address_mode),
            ('gateway', self._subnet_ipv6.gateway_ip),
            ('dns_nameservers', self._subnet_ipv6.dns_nameservers),
            ('dhcp', self._subnet_ipv6.enable_dhcp),
            ('host_routes', subnet_v2.convert_entries_to_gateway(
                self._subnet_ipv6.host_routes)),
            ('allocation_pools', self._subnet_ipv6.allocation_pools),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_subnet.assert_called_once_with(**{
            'cidr': self._subnet_ipv6.cidr,
            'dns_nameservers': self._subnet_ipv6.dns_nameservers,
            'enable_dhcp': self._subnet_ipv6.enable_dhcp,
            'gateway_ip': self._subnet_ipv6.gateway_ip,
            'host_routes': self._subnet_ipv6.host_routes,
            'ip_version': self._subnet_ipv6.ip_version,
            'ipv6_address_mode': self._subnet_ipv6.ipv6_address_mode,
            'ipv6_ra_mode': self._subnet_ipv6.ipv6_ra_mode,
            'name': self._subnet_ipv6.name,
            'network_id': self._subnet_ipv6.network_id,
            'allocation_pools': self._subnet_ipv6.allocation_pools,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data_ipv6, data)


class TestDeleteSubnet(TestSubnet):

    # The subnet to delete.
    _subnet = network_fakes.FakeSubnet.create_one_subnet()

    def setUp(self):
        super(TestDeleteSubnet, self).setUp()

        self.network.delete_subnet = mock.Mock(return_value=None)

        self.network.find_subnet = mock.Mock(return_value=self._subnet)

        # Get the command object to test
        self.cmd = subnet_v2.DeleteSubnet(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._subnet.name,
        ]
        verifylist = [
            ('subnet', self._subnet.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_subnet.assert_called_once_with(self._subnet)
        self.assertIsNone(result)


class TestListSubnet(TestSubnet):
    # The subnets going to be listed up.
    _subnet = network_fakes.FakeSubnet.create_subnets(count=3)

    columns = (
        'ID',
        'Name',
        'Network',
        'Subnet',
    )
    columns_long = columns + (
        'Project',
        'DHCP',
        'Name Servers',
        'Allocation Pools',
        'Host Routes',
        'IP Version',
        'Gateway',
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
            subnet.gateway_ip,
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

        self.network.subnets.assert_called_once_with()
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

        self.network.subnets.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_subnet_list_ip_version(self):
        arglist = [
            '--ip-version', str(4),
        ]
        verifylist = [
            ('ip_version', 4),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'ip_version': 4}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetSubnet(TestSubnet):

    _subnet = network_fakes.FakeSubnet.create_one_subnet()

    def setUp(self):
        super(TestSetSubnet, self).setUp()
        self.network.update_subnet = mock.Mock(return_value=None)
        self.network.find_subnet = mock.Mock(return_value=self._subnet)
        self.cmd = subnet_v2.SetSubnet(self.app, self.namespace)

    def test_set_this(self):
        arglist = [
            "--name", "new_subnet",
            "--dhcp",
            "--gateway", self._subnet.gateway_ip,
            self._subnet.name,
        ]
        verifylist = [
            ('name', "new_subnet"),
            ('dhcp', True),
            ('gateway', self._subnet.gateway_ip),
            ('subnet', self._subnet.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'enable_dhcp': True,
            'gateway_ip': self._subnet.gateway_ip,
            'name': "new_subnet",
        }
        self.network.update_subnet.assert_called_with(self._subnet, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            "--name", "new_subnet",
            "--no-dhcp",
            "--gateway", "none",
            self._subnet.name,
        ]
        verifylist = [
            ('name', "new_subnet"),
            ('no_dhcp', True),
            ('gateway', "none"),
            ('subnet', self._subnet.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'enable_dhcp': False,
            'gateway_ip': None,
            'name': "new_subnet",
        }
        self.network.update_subnet.assert_called_with(self._subnet, **attrs)
        self.assertIsNone(result)

    def test_set_nothing(self):
        arglist = [self._subnet.name, ]
        verifylist = [('subnet', self._subnet.name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_append_options(self):
        _testsubnet = network_fakes.FakeSubnet.create_one_subnet(
            {'dns_nameservers': ["10.0.0.1"]})
        self.network.find_subnet = mock.Mock(return_value=_testsubnet)
        arglist = [
            '--dns-nameserver', '10.0.0.2',
            _testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['10.0.0.2']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'dns_nameservers': ['10.0.0.2', '10.0.0.1'],
        }
        self.network.update_subnet.assert_called_once_with(
            _testsubnet, **attrs)
        self.assertIsNone(result)


class TestShowSubnet(TestSubnet):
    # The subnets to be shown
    _subnet = network_fakes.FakeSubnet.create_one_subnet()

    columns = (
        'allocation_pools',
        'cidr',
        'dns_nameservers',
        'enable_dhcp',
        'gateway_ip',
        'host_routes',
        'id',
        'ip_version',
        'ipv6_address_mode',
        'ipv6_ra_mode',
        'name',
        'network_id',
        'project_id',
        'subnetpool_id',
    )

    data = (
        subnet_v2._format_allocation_pools(_subnet.allocation_pools),
        _subnet.cidr,
        utils.format_list(_subnet.dns_nameservers),
        _subnet.enable_dhcp,
        _subnet.gateway_ip,
        utils.format_list(_subnet.host_routes),
        _subnet.id,
        _subnet.ip_version,
        _subnet.ipv6_address_mode,
        _subnet.ipv6_ra_mode,
        _subnet.name,
        _subnet.network_id,
        _subnet.tenant_id,
        _subnet.subnetpool_id,
    )

    def setUp(self):
        super(TestShowSubnet, self).setUp()

        # Get the command object to test
        self.cmd = subnet_v2.ShowSubnet(self.app, self.namespace)

        self.network.find_subnet = mock.Mock(return_value=self._subnet)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Testing that a call without the required argument will fail and
        # throw a "ParserExecption"
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._subnet.name,
        ]
        verifylist = [
            ('subnet', self._subnet.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_subnet.assert_called_once_with(
            self._subnet.name, ignore_missing=False)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
