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

from openstackclient.network.v2 import security_group_rule
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestSecurityGroupRuleNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroupRuleNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    # The security group rule to be created.
    _security_group_rule = None

    # The security group that will contain the rule created.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    expected_columns = (
        'description',
        'direction',
        'ether_type',
        'id',
        'port_range_max',
        'port_range_min',
        'project_id',
        'protocol',
        'remote_group_id',
        'remote_ip_prefix',
        'security_group_id',
    )

    expected_data = None

    def _setup_security_group_rule(self, attrs=None):
        self._security_group_rule = \
            network_fakes.FakeSecurityGroupRule.create_one_security_group_rule(
                attrs)
        self.network.create_security_group_rule = mock.Mock(
            return_value=self._security_group_rule)
        self.expected_data = (
            self._security_group_rule.description,
            self._security_group_rule.direction,
            self._security_group_rule.ether_type,
            self._security_group_rule.id,
            self._security_group_rule.port_range_max,
            self._security_group_rule.port_range_min,
            self._security_group_rule.project_id,
            self._security_group_rule.protocol,
            self._security_group_rule.remote_group_id,
            self._security_group_rule.remote_ip_prefix,
            self._security_group_rule.security_group_id,
        )

    def setUp(self):
        super(TestCreateSecurityGroupRuleNetwork, self).setUp()

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = security_group_rule.CreateSecurityGroupRule(
            self.app, self.namespace)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_all_remote_options(self):
        arglist = [
            '--remote-ip', '10.10.0.0/24',
            '--remote-group', self._security_group.id,
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_bad_ethertype(self):
        arglist = [
            '--ethertype', 'foo',
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_lowercase_ethertype(self):
        arglist = [
            '--ethertype', 'ipv4',
            self._security_group.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertEqual('IPv4', parsed_args.ethertype)

    def test_lowercase_v6_ethertype(self):
        arglist = [
            '--ethertype', 'ipv6',
            self._security_group.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertEqual('IPv6', parsed_args.ethertype)

    def test_proper_case_ethertype(self):
        arglist = [
            '--ethertype', 'IPv6',
            self._security_group.id,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertEqual('IPv6', parsed_args.ethertype)

    def test_create_all_protocol_options(self):
        arglist = [
            '--protocol', 'tcp',
            '--proto', 'tcp',
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_all_port_range_options(self):
        arglist = [
            '--dst-port', '80:80',
            '--icmp-type', '3',
            '--icmp-code', '1',
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (80, 80)),
            ('icmp_type', 3),
            ('icmp_code', 1),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_create_default_rule(self):
        self._setup_security_group_rule({
            'protocol': 'tcp',
            'port_range_max': 443,
            'port_range_min': 443,
        })
        arglist = [
            '--protocol', 'tcp',
            '--dst-port', str(self._security_group_rule.port_range_min),
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (self._security_group_rule.port_range_min,
                          self._security_group_rule.port_range_max)),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_max': self._security_group_rule.port_range_max,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_proto_option(self):
        self._setup_security_group_rule({
            'protocol': 'icmp',
            'remote_ip_prefix': '10.0.2.0/24',
        })
        arglist = [
            '--proto', self._security_group_rule.protocol,
            '--remote-ip', self._security_group_rule.remote_ip_prefix,
            self._security_group.id,
        ]
        verifylist = [
            ('proto', self._security_group_rule.protocol),
            ('protocol', None),
            ('remote_ip', self._security_group_rule.remote_ip_prefix),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_protocol_any(self):
        self._setup_security_group_rule({
            'protocol': None,
            'remote_ip_prefix': '10.0.2.0/24',
        })
        arglist = [
            '--proto', 'any',
            '--remote-ip', self._security_group_rule.remote_ip_prefix,
            self._security_group.id,
        ]
        verifylist = [
            ('proto', 'any'),
            ('protocol', None),
            ('remote_ip', self._security_group_rule.remote_ip_prefix),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_remote_group(self):
        self._setup_security_group_rule({
            'protocol': 'tcp',
            'port_range_max': 22,
            'port_range_min': 22,
        })
        arglist = [
            '--protocol', 'tcp',
            '--dst-port', str(self._security_group_rule.port_range_min),
            '--ingress',
            '--remote-group', self._security_group.name,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (self._security_group_rule.port_range_min,
                          self._security_group_rule.port_range_max)),
            ('ingress', True),
            ('remote_group', self._security_group.name),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_max': self._security_group_rule.port_range_max,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_group_id': self._security_group.id,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_source_group(self):
        self._setup_security_group_rule({
            'remote_group_id': self._security_group.id,
        })
        arglist = [
            '--ingress',
            '--remote-group', self._security_group.name,
            self._security_group.id,
        ]
        verifylist = [
            ('ingress', True),
            ('remote_group', self._security_group.name),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_group_id': self._security_group_rule.remote_group_id,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_source_ip(self):
        self._setup_security_group_rule({
            'protocol': 'icmp',
            'remote_ip_prefix': '10.0.2.0/24',
        })
        arglist = [
            '--protocol', self._security_group_rule.protocol,
            '--remote-ip', self._security_group_rule.remote_ip_prefix,
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', self._security_group_rule.protocol),
            ('remote_ip', self._security_group_rule.remote_ip_prefix),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_remote_ip(self):
        self._setup_security_group_rule({
            'protocol': 'icmp',
            'remote_ip_prefix': '10.0.2.0/24',
        })
        arglist = [
            '--protocol', self._security_group_rule.protocol,
            '--remote-ip', self._security_group_rule.remote_ip_prefix,
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', self._security_group_rule.protocol),
            ('remote_ip', self._security_group_rule.remote_ip_prefix),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_network_options(self):
        self._setup_security_group_rule({
            'direction': 'egress',
            'ether_type': 'IPv6',
            'port_range_max': 443,
            'port_range_min': 443,
            'protocol': '6',
            'remote_group_id': None,
            'remote_ip_prefix': '::/0',
        })
        arglist = [
            '--dst-port', str(self._security_group_rule.port_range_min),
            '--egress',
            '--ethertype', self._security_group_rule.ether_type,
            '--project', self.project.name,
            '--project-domain', self.domain.name,
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (self._security_group_rule.port_range_min,
                          self._security_group_rule.port_range_max)),
            ('egress', True),
            ('ethertype', self._security_group_rule.ether_type),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_max': self._security_group_rule.port_range_max,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
            'tenant_id': self.project.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_tcp_with_icmp_type(self):
        arglist = [
            '--protocol', 'tcp',
            '--icmp-type', '15',
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', 'tcp'),
            ('icmp_type', 15),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_create_icmp_code(self):
        arglist = [
            '--protocol', '1',
            '--icmp-code', '1',
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', '1'),
            ('icmp_code', 1),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_create_icmp_code_zero(self):
        self._setup_security_group_rule({
            'port_range_min': 15,
            'port_range_max': 0,
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--protocol', self._security_group_rule.protocol,
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--icmp-code', str(self._security_group_rule.port_range_max),
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', self._security_group_rule.protocol),
            ('icmp_code', self._security_group_rule.port_range_max),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_code_greater_than_zero(self):
        self._setup_security_group_rule({
            'port_range_min': 15,
            'port_range_max': 18,
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--protocol', self._security_group_rule.protocol,
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--icmp-code', str(self._security_group_rule.port_range_max),
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', self._security_group_rule.protocol),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', self._security_group_rule.port_range_max),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_code_negative_value(self):
        self._setup_security_group_rule({
            'port_range_min': 15,
            'port_range_max': None,
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--protocol', self._security_group_rule.protocol,
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--icmp-code', '-2',
            self._security_group.id,
        ]
        verifylist = [
            ('protocol', self._security_group_rule.protocol),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', -2),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type(self):
        self._setup_security_group_rule({
            'port_range_min': 15,
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type_zero(self):
        self._setup_security_group_rule({
            'port_range_min': 0,
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type_greater_than_zero(self):
        self._setup_security_group_rule({
            'port_range_min': 13,     # timestamp
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type_negative_value(self):
        self._setup_security_group_rule({
            'port_range_min': None,     # timestamp
            'protocol': 'icmp',
            'remote_ip_prefix': '0.0.0.0/0',
        })
        arglist = [
            '--icmp-type', '-13',
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', -13),
            ('icmp_code', None),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_ipv6_icmp_type_code(self):
        self._setup_security_group_rule({
            'ether_type': 'IPv6',
            'port_range_min': 139,
            'port_range_max': 2,
            'protocol': 'ipv6-icmp',
            'remote_ip_prefix': '::/0',
        })
        arglist = [
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--icmp-code', str(self._security_group_rule.port_range_max),
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', self._security_group_rule.port_range_max),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_min': self._security_group_rule.port_range_min,
            'port_range_max': self._security_group_rule.port_range_max,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmpv6_type(self):
        self._setup_security_group_rule({
            'ether_type': 'IPv6',
            'port_range_min': 139,
            'protocol': 'icmpv6',
            'remote_ip_prefix': '::/0',
        })
        arglist = [
            '--icmp-type', str(self._security_group_rule.port_range_min),
            '--protocol', self._security_group_rule.protocol,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._security_group_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._security_group_rule.protocol),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_with_description(self):
        self._setup_security_group_rule({
            'description': 'Setting SGR',
        })
        arglist = [
            '--description', self._security_group_rule.description,
            self._security_group.id,
        ]
        verifylist = [
            ('description', self._security_group_rule.description),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_security_group_rule.assert_called_once_with(**{
            'description': self._security_group_rule.description,
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ether_type,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)


class TestDeleteSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group rules to be deleted.
    _security_group_rules = \
        network_fakes.FakeSecurityGroupRule.create_security_group_rules(
            count=2)

    def setUp(self):
        super(TestDeleteSecurityGroupRuleNetwork, self).setUp()

        self.network.delete_security_group_rule = mock.Mock(return_value=None)

        self.network.find_security_group_rule = (
            network_fakes.FakeSecurityGroupRule.get_security_group_rules(
                self._security_group_rules)
        )

        # Get the command object to test
        self.cmd = security_group_rule.DeleteSecurityGroupRule(
            self.app, self.namespace)

    def test_security_group_rule_delete(self):
        arglist = [
            self._security_group_rules[0].id,
        ]
        verifylist = [
            ('rule', [self._security_group_rules[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_security_group_rule.assert_called_once_with(
            self._security_group_rules[0])
        self.assertIsNone(result)

    def test_multi_security_group_rules_delete(self):
        arglist = []
        verifylist = []

        for s in self._security_group_rules:
            arglist.append(s.id)
        verifylist = [
            ('rule', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self._security_group_rules:
            calls.append(call(s))
        self.network.delete_security_group_rule.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_security_group_rules_delete_with_exception(self):
        arglist = [
            self._security_group_rules[0].id,
            'unexist_rule',
        ]
        verifylist = [
            ('rule',
             [self._security_group_rules[0].id, 'unexist_rule']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [
            self._security_group_rules[0], exceptions.CommandError]
        self.network.find_security_group_rule = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 rules failed to delete.', str(e))

        self.network.find_security_group_rule.assert_any_call(
            self._security_group_rules[0].id, ignore_missing=False)
        self.network.find_security_group_rule.assert_any_call(
            'unexist_rule', ignore_missing=False)
        self.network.delete_security_group_rule.assert_called_once_with(
            self._security_group_rules[0]
        )


class TestListSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group to hold the rules.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    # The security group rule to be listed.
    _security_group_rule_tcp = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule({
            'protocol': 'tcp',
            'port_range_max': 80,
            'port_range_min': 80,
            'security_group_id': _security_group.id,
        })
    _security_group_rule_icmp = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule({
            'protocol': 'icmp',
            'remote_ip_prefix': '10.0.2.0/24',
            'security_group_id': _security_group.id,
        })
    _security_group.security_group_rules = [_security_group_rule_tcp._info,
                                            _security_group_rule_icmp._info]
    _security_group_rules = [_security_group_rule_tcp,
                             _security_group_rule_icmp]

    expected_columns_with_group_and_long = (
        'ID',
        'IP Protocol',
        'Ethertype',
        'IP Range',
        'Port Range',
        'Direction',
        'Remote Security Group',
    )
    expected_columns_no_group = (
        'ID',
        'IP Protocol',
        'Ethertype',
        'IP Range',
        'Port Range',
        'Remote Security Group',
        'Security Group',
    )

    expected_data_with_group_and_long = []
    expected_data_no_group = []
    for _security_group_rule in _security_group_rules:
        expected_data_with_group_and_long.append((
            _security_group_rule.id,
            _security_group_rule.protocol,
            _security_group_rule.ether_type,
            _security_group_rule.remote_ip_prefix,
            security_group_rule._format_network_port_range(
                _security_group_rule),
            _security_group_rule.direction,
            _security_group_rule.remote_group_id,
        ))
        expected_data_no_group.append((
            _security_group_rule.id,
            _security_group_rule.protocol,
            _security_group_rule.ether_type,
            _security_group_rule.remote_ip_prefix,
            security_group_rule._format_network_port_range(
                _security_group_rule),
            _security_group_rule.remote_group_id,
            _security_group_rule.security_group_id,
        ))

    def setUp(self):
        super(TestListSecurityGroupRuleNetwork, self).setUp()

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)
        self.network.security_group_rules = mock.Mock(
            return_value=self._security_group_rules)

        # Get the command object to test
        self.cmd = security_group_rule.ListSecurityGroupRule(
            self.app, self.namespace)

    def test_list_default(self):
        self._security_group_rule_tcp.port_range_min = 80
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_group_rules.assert_called_once_with(**{})
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))

    def test_list_with_group_and_long(self):
        self._security_group_rule_tcp.port_range_min = 80
        arglist = [
            '--long',
            self._security_group.id,
        ]
        verifylist = [
            ('long', True),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_group_rules.assert_called_once_with(**{
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(self.expected_columns_with_group_and_long, columns)
        self.assertEqual(self.expected_data_with_group_and_long, list(data))

    def test_list_with_ignored_options(self):
        self._security_group_rule_tcp.port_range_min = 80
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_group_rules.assert_called_once_with(**{})
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))

    def test_list_with_protocol(self):
        self._security_group_rule_tcp.port_range_min = 80
        arglist = [
            '--protocol', 'tcp',
        ]
        verifylist = [
            ('protocol', 'tcp'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_group_rules.assert_called_once_with(**{
            'protocol': 'tcp',
        })
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))

    def test_list_with_ingress(self):
        self._security_group_rule_tcp.port_range_min = 80
        arglist = [
            '--ingress',
        ]
        verifylist = [
            ('ingress', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_group_rules.assert_called_once_with(**{
            'direction': 'ingress',
        })
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))

    def test_list_with_wrong_egress(self):
        self._security_group_rule_tcp.port_range_min = 80
        arglist = [
            '--egress',
        ]
        verifylist = [
            ('egress', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_group_rules.assert_called_once_with(**{
            'direction': 'egress',
        })
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))


class TestShowSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group rule to be shown.
    _security_group_rule = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    columns = (
        'description',
        'direction',
        'ether_type',
        'id',
        'port_range_max',
        'port_range_min',
        'project_id',
        'protocol',
        'remote_group_id',
        'remote_ip_prefix',
        'security_group_id',
    )

    data = (
        _security_group_rule.description,
        _security_group_rule.direction,
        _security_group_rule.ether_type,
        _security_group_rule.id,
        _security_group_rule.port_range_max,
        _security_group_rule.port_range_min,
        _security_group_rule.project_id,
        _security_group_rule.protocol,
        _security_group_rule.remote_group_id,
        _security_group_rule.remote_ip_prefix,
        _security_group_rule.security_group_id,
    )

    def setUp(self):
        super(TestShowSecurityGroupRuleNetwork, self).setUp()

        self.network.find_security_group_rule = mock.Mock(
            return_value=self._security_group_rule)

        # Get the command object to test
        self.cmd = security_group_rule.ShowSecurityGroupRule(
            self.app, self.namespace)

    def test_show_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_show_all_options(self):
        arglist = [
            self._security_group_rule.id,
        ]
        verifylist = [
            ('rule', self._security_group_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_security_group_rule.assert_called_once_with(
            self._security_group_rule.id, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
