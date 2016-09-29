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

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.network.v2 import subnet as subnet_v2
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestSubnet(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSubnet, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateSubnet(TestSubnet):

    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # An IPv4 subnet to be created with mostly default values
    _subnet = network_fakes.FakeSubnet.create_one_subnet(
        attrs={
            'tenant_id': project.id,
        }
    )

    # Subnet pool to be used to create a subnet from a pool
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    # An IPv4 subnet to be created using a specific subnet pool
    _subnet_from_pool = network_fakes.FakeSubnet.create_one_subnet(
        attrs={
            'tenant_id': project.id,
            'subnetpool_id': _subnet_pool.id,
            'dns_nameservers': ['8.8.8.8',
                                '8.8.4.4'],
            'host_routes': [{'destination': '10.20.20.0/24',
                             'nexthop': '10.20.20.1'},
                            {'destination': '10.30.30.0/24',
                             'nexthop': '10.30.30.1'}],
            'service_types': ['network:router_gateway',
                              'network:floatingip_agent_gateway'],
        }
    )

    # An IPv6 subnet to be created with most options specified
    _subnet_ipv6 = network_fakes.FakeSubnet.create_one_subnet(
        attrs={
            'tenant_id': project.id,
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
            'service_types': ['network:router_gateway',
                              'network:floatingip_agent_gateway'],
        }
    )

    # The network to be returned from find_network
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={
            'id': _subnet.network_id,
        }
    )

    # The network segment to be returned from find_segment
    _network_segment = \
        network_fakes.FakeNetworkSegment.create_one_network_segment(
            attrs={
                'network_id': _subnet.network_id,
            }
        )

    columns = (
        'allocation_pools',
        'cidr',
        'description',
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
        'segment_id',
        'service_types',
        'subnetpool_id',
    )

    data = (
        subnet_v2._format_allocation_pools(_subnet.allocation_pools),
        _subnet.cidr,
        _subnet.description,
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
        _subnet.segment_id,
        utils.format_list(_subnet.service_types),
        _subnet.subnetpool_id,
    )

    data_subnet_pool = (
        subnet_v2._format_allocation_pools(_subnet_from_pool.allocation_pools),
        _subnet_from_pool.cidr,
        _subnet_from_pool.description,
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
        _subnet_from_pool.segment_id,
        utils.format_list(_subnet_from_pool.service_types),
        _subnet_from_pool.subnetpool_id,
    )

    data_ipv6 = (
        subnet_v2._format_allocation_pools(_subnet_ipv6.allocation_pools),
        _subnet_ipv6.cidr,
        _subnet_ipv6.description,
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
        _subnet_ipv6.segment_id,
        utils.format_list(_subnet_ipv6.service_types),
        _subnet_ipv6.subnetpool_id,
    )

    def setUp(self):
        super(TestCreateSubnet, self).setUp()

        # Get the command object to test
        self.cmd = subnet_v2.CreateSubnet(self.app, self.namespace)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Mock SDK calls for all tests.
        self.network.find_network = mock.Mock(return_value=self._network)
        self.network.find_segment = mock.Mock(
            return_value=self._network_segment
        )
        self.network.find_subnet_pool = mock.Mock(
            return_value=self._subnet_pool
        )

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Testing that a call without the required argument will fail and
        # throw a "ParserExecption"
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        # Mock SDK calls for this test.
        self.network.create_subnet = mock.Mock(return_value=self._subnet)
        self._network.id = self._subnet.network_id

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
            'ip_version': self._subnet.ip_version,
            'name': self._subnet.name,
            'network_id': self._subnet.network_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_from_subnet_pool_options(self):
        # Mock SDK calls for this test.
        self.network.create_subnet = \
            mock.Mock(return_value=self._subnet_from_pool)
        self._network.id = self._subnet_from_pool.network_id

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

        for service_type in self._subnet_from_pool.service_types:
            arglist.append('--service-type')
            arglist.append(service_type)

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
            ('service_types', self._subnet_from_pool.service_types),
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
            'service_types': self._subnet_from_pool.service_types,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data_subnet_pool, data)

    def test_create_options_subnet_range_ipv6(self):
        # Mock SDK calls for this test.
        self.network.create_subnet = mock.Mock(return_value=self._subnet_ipv6)
        self._network.id = self._subnet_ipv6.network_id

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

        for service_type in self._subnet_ipv6.service_types:
            arglist.append('--service-type')
            arglist.append(service_type)

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
            ('service_types', self._subnet_ipv6.service_types),
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
            'service_types': self._subnet_ipv6.service_types,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data_ipv6, data)

    def test_create_with_network_segment(self):
        # Mock SDK calls for this test.
        self.network.create_subnet = mock.Mock(return_value=self._subnet)
        self._network.id = self._subnet.network_id

        arglist = [
            "--subnet-range", self._subnet.cidr,
            "--network-segment", self._network_segment.id,
            "--network", self._subnet.network_id,
            self._subnet.name,
        ]
        verifylist = [
            ('name', self._subnet.name),
            ('subnet_range', self._subnet.cidr),
            ('network_segment', self._network_segment.id),
            ('network', self._subnet.network_id),
            ('ip_version', self._subnet.ip_version),
            ('gateway', 'auto'),

        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_subnet.assert_called_once_with(**{
            'cidr': self._subnet.cidr,
            'ip_version': self._subnet.ip_version,
            'name': self._subnet.name,
            'network_id': self._subnet.network_id,
            'segment_id': self._network_segment.id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_description(self):
        # Mock SDK calls for this test.
        self.network.create_subnet = mock.Mock(return_value=self._subnet)
        self._network.id = self._subnet.network_id

        arglist = [
            "--subnet-range", self._subnet.cidr,
            "--network", self._subnet.network_id,
            "--description", self._subnet.description,
            self._subnet.name,
        ]
        verifylist = [
            ('name', self._subnet.name),
            ('description', self._subnet.description),
            ('subnet_range', self._subnet.cidr),
            ('network', self._subnet.network_id),
            ('ip_version', self._subnet.ip_version),
            ('gateway', 'auto'),

        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_subnet.assert_called_once_with(**{
            'cidr': self._subnet.cidr,
            'ip_version': self._subnet.ip_version,
            'name': self._subnet.name,
            'network_id': self._subnet.network_id,
            'description': self._subnet.description,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteSubnet(TestSubnet):

    # The subnets to delete.
    _subnets = network_fakes.FakeSubnet.create_subnets(count=2)

    def setUp(self):
        super(TestDeleteSubnet, self).setUp()

        self.network.delete_subnet = mock.Mock(return_value=None)

        self.network.find_subnet = (
            network_fakes.FakeSubnet.get_subnets(self._subnets))

        # Get the command object to test
        self.cmd = subnet_v2.DeleteSubnet(self.app, self.namespace)

    def test_subnet_delete(self):
        arglist = [
            self._subnets[0].name,
        ]
        verifylist = [
            ('subnet', [self._subnets[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_subnet.assert_called_once_with(self._subnets[0])
        self.assertIsNone(result)

    def test_multi_subnets_delete(self):
        arglist = []
        verifylist = []

        for s in self._subnets:
            arglist.append(s.name)
        verifylist = [
            ('subnet', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self._subnets:
            calls.append(call(s))
        self.network.delete_subnet.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_subnets_delete_with_exception(self):
        arglist = [
            self._subnets[0].name,
            'unexist_subnet',
        ]
        verifylist = [
            ('subnet',
             [self._subnets[0].name, 'unexist_subnet']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._subnets[0], exceptions.CommandError]
        self.network.find_subnet = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 subnets failed to delete.', str(e))

        self.network.find_subnet.assert_any_call(
            self._subnets[0].name, ignore_missing=False)
        self.network.find_subnet.assert_any_call(
            'unexist_subnet', ignore_missing=False)
        self.network.delete_subnet.assert_called_once_with(
            self._subnets[0]
        )


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
        'Service Types',
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
            utils.format_list(subnet.service_types),
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

    def test_subnet_list_dhcp(self):
        arglist = [
            '--dhcp',
        ]
        verifylist = [
            ('dhcp', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'enable_dhcp': True}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_no_dhcp(self):
        arglist = [
            '--no-dhcp',
        ]
        verifylist = [
            ('no_dhcp', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'enable_dhcp': False}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_service_type(self):
        arglist = [
            '--service-type', 'network:router_gateway',
        ]
        verifylist = [
            ('service_types', ['network:router_gateway']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        filters = {'service_types': ['network:router_gateway']}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'tenant_id': project.id}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_service_type_multiple(self):
        arglist = [
            '--service-type', 'network:router_gateway',
            '--service-type', 'network:floatingip_agent_gateway',
        ]
        verifylist = [
            ('service_types', ['network:router_gateway',
                               'network:floatingip_agent_gateway']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'service_types': ['network:router_gateway',
                                     'network:floatingip_agent_gateway']}
        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
            '--project-domain', project.domain_id,
        ]
        verifylist = [
            ('project', project.id),
            ('project_domain', project.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'tenant_id': project.id}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_network(self):
        network = network_fakes.FakeNetwork.create_one_network()
        self.network.find_network = mock.Mock(return_value=network)
        arglist = [
            '--network', network.id,
        ]
        verifylist = [
            ('network', network.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'network_id': network.id}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_gateway(self):
        subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network.find_network = mock.Mock(return_value=subnet)
        arglist = [
            '--gateway', subnet.gateway_ip,
        ]
        verifylist = [
            ('gateway', subnet.gateway_ip),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'gateway_ip': subnet.gateway_ip}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_name(self):
        subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network.find_network = mock.Mock(return_value=subnet)
        arglist = [
            '--name', subnet.name,
        ]
        verifylist = [
            ('name', subnet.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'name': subnet.name}

        self.network.subnets.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_list_subnet_range(self):
        subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network.find_network = mock.Mock(return_value=subnet)
        arglist = [
            '--subnet-range', subnet.cidr,
        ]
        verifylist = [
            ('subnet_range', subnet.cidr),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'cidr': subnet.cidr}

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
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_subnet.assert_called_with(self._subnet, **attrs)
        self.assertIsNone(result)

    def test_append_options(self):
        _testsubnet = network_fakes.FakeSubnet.create_one_subnet(
            {'dns_nameservers': ["10.0.0.1"],
             'service_types': ["network:router_gateway"]})
        self.network.find_subnet = mock.Mock(return_value=_testsubnet)
        arglist = [
            '--dns-nameserver', '10.0.0.2',
            '--service-type', 'network:floatingip_agent_gateway',
            _testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['10.0.0.2']),
            ('service_types', ['network:floatingip_agent_gateway']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'dns_nameservers': ['10.0.0.2', '10.0.0.1'],
            'service_types': ['network:floatingip_agent_gateway',
                              'network:router_gateway'],
        }
        self.network.update_subnet.assert_called_once_with(
            _testsubnet, **attrs)
        self.assertIsNone(result)

    def test_set_non_append_options(self):
        arglist = [
            "--description", "new_description",
            "--dhcp",
            "--gateway", self._subnet.gateway_ip,
            self._subnet.name,
        ]
        verifylist = [
            ('description', "new_description"),
            ('dhcp', True),
            ('gateway', self._subnet.gateway_ip),
            ('subnet', self._subnet.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'enable_dhcp': True,
            'gateway_ip': self._subnet.gateway_ip,
            'description': "new_description",
        }
        self.network.update_subnet.assert_called_with(self._subnet, **attrs)
        self.assertIsNone(result)

    def test_overwrite_options(self):
        _testsubnet = network_fakes.FakeSubnet.create_one_subnet(
            {'host_routes': [{'destination': '10.20.20.0/24',
                              'nexthop': '10.20.20.1'}],
             'allocation_pools': [{'start': '8.8.8.200',
                                   'end': '8.8.8.250'}], })
        self.network.find_subnet = mock.Mock(return_value=_testsubnet)
        arglist = [
            '--host-route', 'destination=10.30.30.30/24,gateway=10.30.30.1',
            '--no-host-route',
            '--allocation-pool', 'start=8.8.8.100,end=8.8.8.150',
            '--no-allocation-pool',
            _testsubnet.name,
        ]
        verifylist = [
            ('host_routes', [{
                "destination": "10.30.30.30/24", "gateway": "10.30.30.1"}]),
            ('allocation_pools', [{
                'start': '8.8.8.100', 'end': '8.8.8.150'}]),
            ('no_host_route', True),
            ('no_allocation_pool', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'host_routes': [{
                "destination": "10.30.30.30/24", "nexthop": "10.30.30.1"}],
            'allocation_pools': [{'start': '8.8.8.100', 'end': '8.8.8.150'}],
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
        'description',
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
        'segment_id',
        'service_types',
        'subnetpool_id',
    )

    data = (
        subnet_v2._format_allocation_pools(_subnet.allocation_pools),
        _subnet.cidr,
        _subnet.description,
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
        _subnet.segment_id,
        utils.format_list(_subnet.service_types),
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


class TestUnsetSubnet(TestSubnet):

    def setUp(self):
        super(TestUnsetSubnet, self).setUp()
        self._testsubnet = network_fakes.FakeSubnet.create_one_subnet(
            {'dns_nameservers': ['8.8.8.8',
                                 '8.8.8.4'],
             'host_routes': [{'destination': '10.20.20.0/24',
                              'nexthop': '10.20.20.1'},
                             {'destination': '10.30.30.30/24',
                              'nexthop': '10.30.30.1'}],
             'allocation_pools': [{'start': '8.8.8.100',
                                   'end': '8.8.8.150'},
                                  {'start': '8.8.8.160',
                                   'end': '8.8.8.170'}],
             'service_types': ['network:router_gateway',
                               'network:floatingip_agent_gateway'], })
        self.network.find_subnet = mock.Mock(return_value=self._testsubnet)
        self.network.update_subnet = mock.Mock(return_value=None)
        # Get the command object to test
        self.cmd = subnet_v2.UnsetSubnet(self.app, self.namespace)

    def test_unset_subnet_params(self):
        arglist = [
            '--dns-nameserver', '8.8.8.8',
            '--host-route', 'destination=10.30.30.30/24,gateway=10.30.30.1',
            '--allocation-pool', 'start=8.8.8.100,end=8.8.8.150',
            '--service-type', 'network:router_gateway',
            self._testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['8.8.8.8']),
            ('host_routes', [{
                "destination": "10.30.30.30/24", "gateway": "10.30.30.1"}]),
            ('allocation_pools', [{
                'start': '8.8.8.100', 'end': '8.8.8.150'}]),
            ('service_types', ['network:router_gateway']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'dns_nameservers': ['8.8.8.4'],
            'host_routes': [{
                "destination": "10.20.20.0/24", "nexthop": "10.20.20.1"}],
            'allocation_pools': [{'start': '8.8.8.160', 'end': '8.8.8.170'}],
            'service_types': ['network:floatingip_agent_gateway'],
        }
        self.network.update_subnet.assert_called_once_with(
            self._testsubnet, **attrs)
        self.assertIsNone(result)

    def test_unset_subnet_wrong_host_routes(self):
        arglist = [
            '--dns-nameserver', '8.8.8.8',
            '--host-route', 'destination=10.30.30.30/24,gateway=10.30.30.2',
            '--allocation-pool', 'start=8.8.8.100,end=8.8.8.150',
            self._testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['8.8.8.8']),
            ('host_routes', [{
                "destination": "10.30.30.30/24", "gateway": "10.30.30.2"}]),
            ('allocation_pools', [{
                'start': '8.8.8.100', 'end': '8.8.8.150'}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)

    def test_unset_subnet_wrong_allocation_pool(self):
        arglist = [
            '--dns-nameserver', '8.8.8.8',
            '--host-route', 'destination=10.30.30.30/24,gateway=10.30.30.1',
            '--allocation-pool', 'start=8.8.8.100,end=8.8.8.156',
            self._testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['8.8.8.8']),
            ('host_routes', [{
                "destination": "10.30.30.30/24", "gateway": "10.30.30.1"}]),
            ('allocation_pools', [{
                'start': '8.8.8.100', 'end': '8.8.8.156'}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)

    def test_unset_subnet_wrong_dns_nameservers(self):
        arglist = [
            '--dns-nameserver', '8.8.8.1',
            '--host-route', 'destination=10.30.30.30/24,gateway=10.30.30.1',
            '--allocation-pool', 'start=8.8.8.100,end=8.8.8.150',
            self._testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['8.8.8.1']),
            ('host_routes', [{
                "destination": "10.30.30.30/24", "gateway": "10.30.30.1"}]),
            ('allocation_pools', [{
                'start': '8.8.8.100', 'end': '8.8.8.150'}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)

    def test_unset_subnet_wrong_service_type(self):
        arglist = [
            '--dns-nameserver', '8.8.8.8',
            '--host-route', 'destination=10.30.30.30/24,gateway=10.30.30.1',
            '--allocation-pool', 'start=8.8.8.100,end=8.8.8.150',
            '--service-type', 'network:dhcp',
            self._testsubnet.name,
        ]
        verifylist = [
            ('dns_nameservers', ['8.8.8.8']),
            ('host_routes', [{
                "destination": "10.30.30.30/24", "gateway": "10.30.30.1"}]),
            ('allocation_pools', [{
                'start': '8.8.8.100', 'end': '8.8.8.150'}]),
            ('service_types', ['network:dhcp']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action, parsed_args)
