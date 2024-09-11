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
from unittest.mock import call
import uuid

from openstack.network.v2 import _proxy
from openstack.network.v2 import (
    default_security_group_rule as _default_security_group_rule,
)
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.network import utils as network_utils
from openstackclient.network.v2 import default_security_group_rule
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestDefaultSecurityGroupRule(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.app.client_manager.sdk_connection = mock.Mock()
        self.app.client_manager.sdk_connection.network = mock.Mock(
            spec=_proxy.Proxy,
        )
        self.sdk_client = self.app.client_manager.sdk_connection.network


class TestCreateDefaultSecurityGroupRule(TestDefaultSecurityGroupRule):
    expected_columns = (
        'description',
        'direction',
        'ether_type',
        'id',
        'port_range_max',
        'port_range_min',
        'protocol',
        'remote_address_group_id',
        'remote_group_id',
        'remote_ip_prefix',
        'used_in_default_sg',
        'used_in_non_default_sg',
    )

    expected_data = None

    def _setup_default_security_group_rule(self, attrs=None):
        default_security_group_rule_attrs = {
            'description': 'default-security-group-rule-description-'
            + uuid.uuid4().hex,
            'direction': 'ingress',
            'ether_type': 'IPv4',
            'id': 'default-security-group-rule-id-' + uuid.uuid4().hex,
            'port_range_max': None,
            'port_range_min': None,
            'protocol': None,
            'remote_group_id': None,
            'remote_address_group_id': None,
            'remote_ip_prefix': '0.0.0.0/0',
            'location': 'MUNCHMUNCHMUNCH',
            'used_in_default_sg': False,
            'used_in_non_default_sg': False,
        }
        attrs = attrs or {}
        # Overwrite default attributes.
        default_security_group_rule_attrs.update(attrs)
        self._default_sg_rule = sdk_fakes.generate_fake_resource(
            _default_security_group_rule.DefaultSecurityGroupRule,
            **default_security_group_rule_attrs,
        )

        self.sdk_client.create_default_security_group_rule.return_value = (
            self._default_sg_rule
        )
        self.expected_data = (
            self._default_sg_rule.description,
            self._default_sg_rule.direction,
            self._default_sg_rule.ether_type,
            self._default_sg_rule.id,
            self._default_sg_rule.port_range_max,
            self._default_sg_rule.port_range_min,
            self._default_sg_rule.protocol,
            self._default_sg_rule.remote_address_group_id,
            self._default_sg_rule.remote_group_id,
            self._default_sg_rule.remote_ip_prefix,
            self._default_sg_rule.used_in_default_sg,
            self._default_sg_rule.used_in_non_default_sg,
        )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = default_security_group_rule.CreateDefaultSecurityGroupRule(
            self.app, None
        )

    def test_create_all_remote_options(self):
        arglist = [
            '--remote-ip',
            '10.10.0.0/24',
            '--remote-group',
            'test-remote-group-id',
            '--remote-address-group',
            'test-remote-address-group-id',
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_create_bad_ethertype(self):
        arglist = [
            '--ethertype',
            'foo',
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_lowercase_ethertype(self):
        arglist = [
            '--ethertype',
            'ipv4',
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertEqual('IPv4', parsed_args.ethertype)

    def test_lowercase_v6_ethertype(self):
        arglist = [
            '--ethertype',
            'ipv6',
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertEqual('IPv6', parsed_args.ethertype)

    def test_proper_case_ethertype(self):
        arglist = [
            '--ethertype',
            'IPv6',
        ]
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.assertEqual('IPv6', parsed_args.ethertype)

    def test_create_all_port_range_options(self):
        arglist = [
            '--dst-port',
            '80:80',
            '--icmp-type',
            '3',
            '--icmp-code',
            '1',
        ]
        verifylist = [
            ('dst_port', (80, 80)),
            ('icmp_type', 3),
            ('icmp_code', 1),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_create_default_rule(self):
        self._setup_default_security_group_rule(
            {
                'protocol': 'tcp',
                'port_range_max': 443,
                'port_range_min': 443,
            }
        )
        arglist = [
            '--protocol',
            'tcp',
            '--dst-port',
            str(self._default_sg_rule.port_range_min),
        ]
        verifylist = [
            (
                'dst_port',
                (
                    self._default_sg_rule.port_range_min,
                    self._default_sg_rule.port_range_max,
                ),
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_max': self._default_sg_rule.port_range_max,
                'port_range_min': self._default_sg_rule.port_range_min,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def _test_create_protocol_any_helper(
        self, for_default_sg=False, for_custom_sg=False
    ):
        self._setup_default_security_group_rule(
            {
                'protocol': None,
                'remote_ip_prefix': '10.0.2.0/24',
            }
        )
        arglist = [
            '--protocol',
            'any',
            '--remote-ip',
            self._default_sg_rule.remote_ip_prefix,
        ]
        if for_default_sg:
            arglist.append('--for-default-sg')
        if for_custom_sg:
            arglist.append('--for-custom-sg')
        verifylist = [
            ('protocol', 'any'),
            ('remote_ip', self._default_sg_rule.remote_ip_prefix),
            ('for_default_sg', for_default_sg),
            ('for_custom_sg', for_custom_sg),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': for_default_sg,
                'used_in_non_default_sg': for_custom_sg,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_protocol_any_not_for_default_sg(self):
        self._test_create_protocol_any_helper()

    def test_create_protocol_any_for_default_sg(self):
        self._test_create_protocol_any_helper(for_default_sg=True)

    def test_create_protocol_any_for_custom_sg(self):
        self._test_create_protocol_any_helper(for_custom_sg=True)

    def test_create_protocol_any_for_default_and_custom_sg(self):
        self._test_create_protocol_any_helper(
            for_default_sg=True, for_custom_sg=True
        )

    def test_create_remote_address_group(self):
        self._setup_default_security_group_rule(
            {
                'protocol': 'icmp',
                'remote_address_group_id': 'remote-address-group-id',
            }
        )
        arglist = [
            '--protocol',
            'icmp',
            '--remote-address-group',
            self._default_sg_rule.remote_address_group_id,
        ]
        verifylist = [
            (
                'remote_address_group',
                self._default_sg_rule.remote_address_group_id,
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_address_group_id': self._default_sg_rule.remote_address_group_id,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_remote_group(self):
        self._setup_default_security_group_rule(
            {
                'protocol': 'tcp',
                'port_range_max': 22,
                'port_range_min': 22,
            }
        )
        arglist = [
            '--protocol',
            'tcp',
            '--dst-port',
            str(self._default_sg_rule.port_range_min),
            '--ingress',
            '--remote-group',
            'remote-group-id',
        ]
        verifylist = [
            (
                'dst_port',
                (
                    self._default_sg_rule.port_range_min,
                    self._default_sg_rule.port_range_max,
                ),
            ),
            ('ingress', True),
            ('remote_group', 'remote-group-id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_max': self._default_sg_rule.port_range_max,
                'port_range_min': self._default_sg_rule.port_range_min,
                'protocol': self._default_sg_rule.protocol,
                'remote_group_id': 'remote-group-id',
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_source_group(self):
        self._setup_default_security_group_rule(
            {
                'remote_group_id': 'remote-group-id',
            }
        )
        arglist = [
            '--ingress',
            '--remote-group',
            'remote-group-id',
        ]
        verifylist = [
            ('ingress', True),
            ('remote_group', 'remote-group-id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_group_id': 'remote-group-id',
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_source_ip(self):
        self._setup_default_security_group_rule(
            {
                'protocol': 'icmp',
                'remote_ip_prefix': '10.0.2.0/24',
            }
        )
        arglist = [
            '--protocol',
            self._default_sg_rule.protocol,
            '--remote-ip',
            self._default_sg_rule.remote_ip_prefix,
        ]
        verifylist = [
            ('protocol', self._default_sg_rule.protocol),
            ('remote_ip', self._default_sg_rule.remote_ip_prefix),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_remote_ip(self):
        self._setup_default_security_group_rule(
            {
                'protocol': 'icmp',
                'remote_ip_prefix': '10.0.2.0/24',
            }
        )
        arglist = [
            '--protocol',
            self._default_sg_rule.protocol,
            '--remote-ip',
            self._default_sg_rule.remote_ip_prefix,
        ]
        verifylist = [
            ('protocol', self._default_sg_rule.protocol),
            ('remote_ip', self._default_sg_rule.remote_ip_prefix),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_tcp_with_icmp_type(self):
        arglist = [
            '--protocol',
            'tcp',
            '--icmp-type',
            '15',
        ]
        verifylist = [
            ('protocol', 'tcp'),
            ('icmp_type', 15),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_create_icmp_code(self):
        arglist = [
            '--protocol',
            '1',
            '--icmp-code',
            '1',
        ]
        verifylist = [
            ('protocol', '1'),
            ('icmp_code', 1),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_create_icmp_code_zero(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': 15,
                'port_range_max': 0,
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--protocol',
            self._default_sg_rule.protocol,
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--icmp-code',
            str(self._default_sg_rule.port_range_max),
        ]
        verifylist = [
            ('protocol', self._default_sg_rule.protocol),
            ('icmp_code', self._default_sg_rule.port_range_max),
            ('icmp_type', self._default_sg_rule.port_range_min),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_code_greater_than_zero(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': 15,
                'port_range_max': 18,
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--protocol',
            self._default_sg_rule.protocol,
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--icmp-code',
            str(self._default_sg_rule.port_range_max),
        ]
        verifylist = [
            ('protocol', self._default_sg_rule.protocol),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', self._default_sg_rule.port_range_max),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_code_negative_value(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': 15,
                'port_range_max': None,
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--protocol',
            self._default_sg_rule.protocol,
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--icmp-code',
            '-2',
        ]
        verifylist = [
            ('protocol', self._default_sg_rule.protocol),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', -2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': 15,
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--protocol',
            self._default_sg_rule.protocol,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._default_sg_rule.protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_min': self._default_sg_rule.port_range_min,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type_zero(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': 0,
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--protocol',
            self._default_sg_rule.protocol,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._default_sg_rule.protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_min': self._default_sg_rule.port_range_min,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type_greater_than_zero(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': 13,  # timestamp
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--protocol',
            self._default_sg_rule.protocol,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._default_sg_rule.protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_min': self._default_sg_rule.port_range_min,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmp_type_negative_value(self):
        self._setup_default_security_group_rule(
            {
                'port_range_min': None,  # timestamp
                'protocol': 'icmp',
                'remote_ip_prefix': '0.0.0.0/0',
            }
        )
        arglist = [
            '--icmp-type',
            '-13',
            '--protocol',
            self._default_sg_rule.protocol,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', -13),
            ('icmp_code', None),
            ('protocol', self._default_sg_rule.protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_ipv6_icmp_type_code(self):
        self._setup_default_security_group_rule(
            {
                'ether_type': 'IPv6',
                'port_range_min': 139,
                'port_range_max': 2,
                'protocol': 'ipv6-icmp',
                'remote_ip_prefix': '::/0',
            }
        )
        arglist = [
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--icmp-code',
            str(self._default_sg_rule.port_range_max),
            '--protocol',
            self._default_sg_rule.protocol,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', self._default_sg_rule.port_range_max),
            ('protocol', self._default_sg_rule.protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_min': self._default_sg_rule.port_range_min,
                'port_range_max': self._default_sg_rule.port_range_max,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_icmpv6_type(self):
        self._setup_default_security_group_rule(
            {
                'ether_type': 'IPv6',
                'port_range_min': 139,
                'protocol': 'icmpv6',
                'remote_ip_prefix': '::/0',
            }
        )
        arglist = [
            '--icmp-type',
            str(self._default_sg_rule.port_range_min),
            '--protocol',
            self._default_sg_rule.protocol,
        ]
        verifylist = [
            ('dst_port', None),
            ('icmp_type', self._default_sg_rule.port_range_min),
            ('icmp_code', None),
            ('protocol', self._default_sg_rule.protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'port_range_min': self._default_sg_rule.port_range_min,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_create_with_description(self):
        self._setup_default_security_group_rule(
            {
                'description': 'Setting SGR',
            }
        )
        arglist = [
            '--description',
            self._default_sg_rule.description,
        ]
        verifylist = [
            ('description', self._default_sg_rule.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.create_default_security_group_rule.assert_called_once_with(
            **{
                'description': self._default_sg_rule.description,
                'direction': self._default_sg_rule.direction,
                'ethertype': self._default_sg_rule.ether_type,
                'protocol': self._default_sg_rule.protocol,
                'remote_ip_prefix': self._default_sg_rule.remote_ip_prefix,
                'used_in_default_sg': False,
                'used_in_non_default_sg': False,
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)


class TestDeleteDefaultSecurityGroupRule(TestDefaultSecurityGroupRule):
    # The default security group rules to be deleted.
    default_security_group_rule_attrs = {
        'direction': 'ingress',
        'ether_type': 'IPv4',
        'port_range_max': None,
        'port_range_min': None,
        'protocol': None,
        'remote_group_id': None,
        'remote_address_group_id': None,
        'remote_ip_prefix': '0.0.0.0/0',
        'location': 'MUNCHMUNCHMUNCH',
        'used_in_default_sg': False,
        'used_in_non_default_sg': False,
    }
    _default_sg_rules = list(
        sdk_fakes.generate_fake_resources(
            _default_security_group_rule.DefaultSecurityGroupRule,
            count=2,
            attrs=default_security_group_rule_attrs,
        )
    )

    def setUp(self):
        super().setUp()

        self.sdk_client.delete_default_security_group_rule.return_value = None

        # Get the command object to test
        self.cmd = default_security_group_rule.DeleteDefaultSecurityGroupRule(
            self.app, None
        )

    def test_default_security_group_rule_delete(self):
        arglist = [
            self._default_sg_rules[0].id,
        ]
        verifylist = [
            ('rule', [self._default_sg_rules[0].id]),
        ]
        self.sdk_client.find_default_security_group_rule.return_value = (
            self._default_sg_rules[0]
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.sdk_client.delete_default_security_group_rule.assert_called_once_with(
            self._default_sg_rules[0]
        )
        self.assertIsNone(result)

    def test_multi_default_security_group_rules_delete(self):
        arglist = []
        verifylist = []

        for s in self._default_sg_rules:
            arglist.append(s.id)
        verifylist = [
            ('rule', arglist),
        ]
        self.sdk_client.find_default_security_group_rule.side_effect = (
            self._default_sg_rules
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self._default_sg_rules:
            calls.append(call(s))
        self.sdk_client.delete_default_security_group_rule.assert_has_calls(
            calls
        )
        self.assertIsNone(result)

    def test_multi_default_security_group_rules_delete_with_exception(self):
        arglist = [
            self._default_sg_rules[0].id,
            'unexist_rule',
        ]
        verifylist = [
            ('rule', [self._default_sg_rules[0].id, 'unexist_rule']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [
            self._default_sg_rules[0],
            exceptions.CommandError,
        ]
        self.sdk_client.find_default_security_group_rule = mock.Mock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 default rules failed to delete.', str(e))

        self.sdk_client.find_default_security_group_rule.assert_any_call(
            self._default_sg_rules[0].id, ignore_missing=False
        )
        self.sdk_client.find_default_security_group_rule.assert_any_call(
            'unexist_rule', ignore_missing=False
        )
        self.sdk_client.delete_default_security_group_rule.assert_called_once_with(
            self._default_sg_rules[0]
        )


class TestListDefaultSecurityGroupRule(TestDefaultSecurityGroupRule):
    # The security group rule to be listed.
    _default_sg_rule_tcp = sdk_fakes.generate_fake_resource(
        _default_security_group_rule.DefaultSecurityGroupRule,
        **{'protocol': 'tcp', 'port_range_max': 80, 'port_range_min': 80},
    )
    _default_sg_rule_icmp = sdk_fakes.generate_fake_resource(
        _default_security_group_rule.DefaultSecurityGroupRule,
        **{'protocol': 'icmp', 'remote_ip_prefix': '10.0.2.0/24'},
    )
    _default_sg_rules = [
        _default_sg_rule_tcp,
        _default_sg_rule_icmp,
    ]

    expected_columns = (
        'ID',
        'IP Protocol',
        'Ethertype',
        'IP Range',
        'Port Range',
        'Direction',
        'Remote Security Group',
        'Remote Address Group',
        'Used in default Security Group',
        'Used in custom Security Group',
    )

    expected_data = []
    expected_data_no_group = []
    for _default_sg_rule in _default_sg_rules:
        expected_data.append(
            (
                _default_sg_rule.id,
                _default_sg_rule.protocol,
                _default_sg_rule.ether_type,
                _default_sg_rule.remote_ip_prefix,
                network_utils.format_network_port_range(_default_sg_rule),
                _default_sg_rule.direction,
                _default_sg_rule.remote_group_id,
                _default_sg_rule.remote_address_group_id,
                _default_sg_rule.used_in_default_sg,
                _default_sg_rule.used_in_non_default_sg,
            )
        )

    def setUp(self):
        super().setUp()

        self.sdk_client.default_security_group_rules.return_value = (
            self._default_sg_rules
        )

        # Get the command object to test
        self.cmd = default_security_group_rule.ListDefaultSecurityGroupRule(
            self.app, None
        )

    def test_list_default(self):
        self._default_sg_rule_tcp.port_range_min = 80
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.default_security_group_rules.assert_called_once_with(
            **{}
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, list(data))

    def test_list_with_protocol(self):
        self._default_sg_rule_tcp.port_range_min = 80
        arglist = [
            '--protocol',
            'tcp',
        ]
        verifylist = [
            ('protocol', 'tcp'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.default_security_group_rules.assert_called_once_with(
            **{
                'protocol': 'tcp',
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, list(data))

    def test_list_with_ingress(self):
        self._default_sg_rule_tcp.port_range_min = 80
        arglist = [
            '--ingress',
        ]
        verifylist = [
            ('ingress', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.default_security_group_rules.assert_called_once_with(
            **{
                'direction': 'ingress',
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, list(data))

    def test_list_with_wrong_egress(self):
        self._default_sg_rule_tcp.port_range_min = 80
        arglist = [
            '--egress',
        ]
        verifylist = [
            ('egress', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.default_security_group_rules.assert_called_once_with(
            **{
                'direction': 'egress',
            }
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, list(data))


class TestShowDefaultSecurityGroupRule(TestDefaultSecurityGroupRule):
    # The default security group rule to be shown.
    _default_sg_rule = sdk_fakes.generate_fake_resource(
        _default_security_group_rule.DefaultSecurityGroupRule
    )

    columns = (
        'description',
        'direction',
        'ether_type',
        'id',
        'port_range_max',
        'port_range_min',
        'protocol',
        'remote_address_group_id',
        'remote_group_id',
        'remote_ip_prefix',
        'used_in_default_sg',
        'used_in_non_default_sg',
    )

    data = (
        _default_sg_rule.description,
        _default_sg_rule.direction,
        _default_sg_rule.ether_type,
        _default_sg_rule.id,
        _default_sg_rule.port_range_max,
        _default_sg_rule.port_range_min,
        _default_sg_rule.protocol,
        _default_sg_rule.remote_address_group_id,
        _default_sg_rule.remote_group_id,
        _default_sg_rule.remote_ip_prefix,
        _default_sg_rule.used_in_default_sg,
        _default_sg_rule.used_in_non_default_sg,
    )

    def setUp(self):
        super().setUp()

        self.sdk_client.find_default_security_group_rule.return_value = (
            self._default_sg_rule
        )

        # Get the command object to test
        self.cmd = default_security_group_rule.ShowDefaultSecurityGroupRule(
            self.app, None
        )

    def test_show_no_options(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_show_all_options(self):
        arglist = [
            self._default_sg_rule.id,
        ]
        verifylist = [
            ('rule', self._default_sg_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.find_default_security_group_rule.assert_called_once_with(
            self._default_sg_rule.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
