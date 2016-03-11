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

from openstackclient.network.v2 import security_group_rule
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestSecurityGroupRuleNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroupRuleNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestSecurityGroupRuleCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupRuleCompute, self).setUp()

        # Get a shortcut to the network client
        self.compute = self.app.client_manager.compute


class TestCreateSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group rule to be created.
    _security_group_rule = None

    # The security group that will contain the rule created.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    expected_columns = (
        'direction',
        'ethertype',
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
            self._security_group_rule.direction,
            self._security_group_rule.ethertype,
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

        # Get the command object to test
        self.cmd = security_group_rule.CreateSecurityGroupRule(
            self.app, self.namespace)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_source_group_and_ip(self):
        arglist = [
            '--src-ip', '10.10.0.0/24',
            '--src-group', self._security_group.id,
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_bad_protocol(self):
        arglist = [
            '--protocol', 'foo',
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_default_rule(self):
        self._setup_security_group_rule({
            'port_range_max': 443,
            'port_range_min': 443,
        })
        arglist = [
            '--dst-port', str(self._security_group_rule.port_range_min),
            self._security_group.id,
        ]
        verifylist = [
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ethertype,
            'port_range_max': self._security_group_rule.port_range_max,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(tuple(self.expected_columns), columns)
        self.assertEqual(self.expected_data, data)

    def test_create_source_group(self):
        self._setup_security_group_rule({
            'port_range_max': 22,
            'port_range_min': 22,
            'remote_group_id': self._security_group.id,
        })
        arglist = [
            '--dst-port', str(self._security_group_rule.port_range_min),
            '--src-group', self._security_group.id,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (self._security_group_rule.port_range_min,
                          self._security_group_rule.port_range_max)),
            ('src_group', self._security_group.id),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ethertype,
            'port_range_max': self._security_group_rule.port_range_max,
            'port_range_min': self._security_group_rule.port_range_min,
            'protocol': self._security_group_rule.protocol,
            'remote_group_id': self._security_group_rule.remote_group_id,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(tuple(self.expected_columns), columns)
        self.assertEqual(self.expected_data, data)

    def test_create_source_ip(self):
        self._setup_security_group_rule({
            'protocol': 'icmp',
            'port_range_max': -1,
            'port_range_min': -1,
            'remote_ip_prefix': '10.0.2.0/24',
        })
        arglist = [
            '--proto', self._security_group_rule.protocol,
            '--src-ip', self._security_group_rule.remote_ip_prefix,
            self._security_group.id,
        ]
        verifylist = [
            ('proto', self._security_group_rule.protocol),
            ('src_ip', self._security_group_rule.remote_ip_prefix),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group_rule.assert_called_once_with(**{
            'direction': self._security_group_rule.direction,
            'ethertype': self._security_group_rule.ethertype,
            'protocol': self._security_group_rule.protocol,
            'remote_ip_prefix': self._security_group_rule.remote_ip_prefix,
            'security_group_id': self._security_group.id,
        })
        self.assertEqual(tuple(self.expected_columns), columns)
        self.assertEqual(self.expected_data, data)


class TestCreateSecurityGroupRuleCompute(TestSecurityGroupRuleCompute):

    # The security group rule to be created.
    _security_group_rule = None

    # The security group that will contain the rule created.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    def _setup_security_group_rule(self, attrs=None):
        self._security_group_rule = \
            compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule(
                attrs)
        self.compute.security_group_rules.create.return_value = \
            self._security_group_rule
        expected_columns, expected_data = \
            security_group_rule._format_security_group_rule_show(
                self._security_group_rule._info)
        return expected_columns, expected_data

    def setUp(self):
        super(TestCreateSecurityGroupRuleCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.get.return_value = self._security_group

        # Get the command object to test
        self.cmd = security_group_rule.CreateSecurityGroupRule(self.app, None)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_source_group_and_ip(self):
        arglist = [
            '--src-ip', '10.10.0.0/24',
            '--src-group', self._security_group.id,
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_bad_protocol(self):
        arglist = [
            '--protocol', 'foo',
            self._security_group.id,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_default_rule(self):
        expected_columns, expected_data = self._setup_security_group_rule()
        dst_port = str(self._security_group_rule.from_port) + ':' + \
            str(self._security_group_rule.to_port)
        arglist = [
            '--dst-port', dst_port,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (self._security_group_rule.from_port,
                          self._security_group_rule.to_port)),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_group_rules.create.assert_called_once_with(
            self._security_group.id,
            self._security_group_rule.ip_protocol,
            self._security_group_rule.from_port,
            self._security_group_rule.to_port,
            self._security_group_rule.ip_range['cidr'],
            None,
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)

    def test_create_source_group(self):
        expected_columns, expected_data = self._setup_security_group_rule({
            'from_port': 22,
            'to_port': 22,
            'group': {'name': self._security_group.id},
        })
        arglist = [
            '--dst-port', str(self._security_group_rule.from_port),
            '--src-group', self._security_group.id,
            self._security_group.id,
        ]
        verifylist = [
            ('dst_port', (self._security_group_rule.from_port,
                          self._security_group_rule.to_port)),
            ('src_group', self._security_group.id),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_group_rules.create.assert_called_once_with(
            self._security_group.id,
            self._security_group_rule.ip_protocol,
            self._security_group_rule.from_port,
            self._security_group_rule.to_port,
            self._security_group_rule.ip_range['cidr'],
            self._security_group.id,
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)

    def test_create_source_ip(self):
        expected_columns, expected_data = self._setup_security_group_rule({
            'ip_protocol': 'icmp',
            'from_port': -1,
            'to_port': -1,
            'ip_range': {'cidr': '10.0.2.0/24'},
        })
        arglist = [
            '--proto', self._security_group_rule.ip_protocol,
            '--src-ip', self._security_group_rule.ip_range['cidr'],
            self._security_group.id,
        ]
        verifylist = [
            ('proto', self._security_group_rule.ip_protocol),
            ('src_ip', self._security_group_rule.ip_range['cidr']),
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_group_rules.create.assert_called_once_with(
            self._security_group.id,
            self._security_group_rule.ip_protocol,
            self._security_group_rule.from_port,
            self._security_group_rule.to_port,
            self._security_group_rule.ip_range['cidr'],
            None,
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)


class TestDeleteSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group rule to be deleted.
    _security_group_rule = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    def setUp(self):
        super(TestDeleteSecurityGroupRuleNetwork, self).setUp()

        self.network.delete_security_group_rule = mock.Mock(return_value=None)

        self.network.find_security_group_rule = mock.Mock(
            return_value=self._security_group_rule)

        # Get the command object to test
        self.cmd = security_group_rule.DeleteSecurityGroupRule(
            self.app, self.namespace)

    def test_security_group_rule_delete(self):
        arglist = [
            self._security_group_rule.id,
        ]
        verifylist = [
            ('rule', self._security_group_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_security_group_rule.assert_called_once_with(
            self._security_group_rule)
        self.assertIsNone(result)


class TestDeleteSecurityGroupRuleCompute(TestSecurityGroupRuleCompute):

    # The security group rule to be deleted.
    _security_group_rule = \
        compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    def setUp(self):
        super(TestDeleteSecurityGroupRuleCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group_rule.DeleteSecurityGroupRule(self.app, None)

    def test_security_group_rule_delete(self):
        arglist = [
            self._security_group_rule.id,
        ]
        verifylist = [
            ('rule', self._security_group_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.security_group_rules.delete.assert_called_once_with(
            self._security_group_rule.id)
        self.assertIsNone(result)


class TestShowSecurityGroupRuleNetwork(TestSecurityGroupRuleNetwork):

    # The security group rule to be shown.
    _security_group_rule = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    columns = (
        'direction',
        'ethertype',
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
        _security_group_rule.direction,
        _security_group_rule.ethertype,
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
        self.assertEqual(tuple(self.columns), columns)
        self.assertEqual(self.data, data)


class TestShowSecurityGroupRuleCompute(TestSecurityGroupRuleCompute):

    # The security group rule to be shown.
    _security_group_rule = \
        compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    columns, data = \
        security_group_rule._format_security_group_rule_show(
            _security_group_rule._info)

    def setUp(self):
        super(TestShowSecurityGroupRuleCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Build a security group fake customized for this test.
        security_group_rules = [self._security_group_rule._info]
        security_group = fakes.FakeResource(
            info=copy.deepcopy({'rules': security_group_rules}),
            loaded=True)
        security_group.rules = security_group_rules
        self.compute.security_groups.list.return_value = [security_group]

        # Get the command object to test
        self.cmd = security_group_rule.ShowSecurityGroupRule(self.app, None)

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

        self.compute.security_groups.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
