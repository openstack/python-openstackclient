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

from unittest import mock

from osc_lib import exceptions

from openstackclient.api import compute_v2
from openstackclient.network import utils as network_utils
from openstackclient.network.v2 import security_group_rule
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils


@mock.patch.object(compute_v2, 'create_security_group_rule')
class TestCreateSecurityGroupRuleCompute(compute_fakes.TestComputev2):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    # The security group rule to be created.
    _security_group_rule = None

    # The security group that will contain the rule created.
    _security_group = compute_fakes.create_one_security_group()

    def _setup_security_group_rule(self, attrs=None):
        self._security_group_rule = (
            compute_fakes.create_one_security_group_rule(attrs)
        )
        (
            expected_columns,
            expected_data,
        ) = network_utils.format_security_group_rule_show(
            self._security_group_rule
        )
        return expected_columns, expected_data

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        compute_v2.find_security_group = mock.Mock(
            return_value=self._security_group,
        )

        # Get the command object to test
        self.cmd = security_group_rule.CreateSecurityGroupRule(self.app, None)

    def test_security_group_rule_create_no_options(self, sgr_mock):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_security_group_rule_create_all_remote_options(self, sgr_mock):
        arglist = [
            '--remote-ip',
            '10.10.0.0/24',
            '--remote-group',
            self._security_group['id'],
            self._security_group['id'],
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_security_group_rule_create_bad_protocol(self, sgr_mock):
        arglist = [
            '--protocol',
            'foo',
            self._security_group['id'],
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_security_group_rule_create_all_protocol_options(self, sgr_mock):
        arglist = [
            '--protocol',
            'tcp',
            '--proto',
            'tcp',
            self._security_group['id'],
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_security_group_rule_create_network_options(self, sgr_mock):
        arglist = [
            '--ingress',
            '--ethertype',
            'IPv4',
            '--icmp-type',
            '3',
            '--icmp-code',
            '11',
            '--project',
            self.project.name,
            '--project-domain',
            self.domain.name,
            self._security_group['id'],
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_security_group_rule_create_default_rule(self, sgr_mock):
        expected_columns, expected_data = self._setup_security_group_rule()
        sgr_mock.return_value = self._security_group_rule
        dst_port = (
            str(self._security_group_rule['from_port'])
            + ':'
            + str(self._security_group_rule['to_port'])
        )
        arglist = [
            '--dst-port',
            dst_port,
            self._security_group['id'],
        ]
        verifylist = [
            (
                'dst_port',
                (
                    self._security_group_rule['from_port'],
                    self._security_group_rule['to_port'],
                ),
            ),
            ('group', self._security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sgr_mock.assert_called_once_with(
            self.compute_client,
            security_group_id=self._security_group['id'],
            ip_protocol=self._security_group_rule['ip_protocol'],
            from_port=self._security_group_rule['from_port'],
            to_port=self._security_group_rule['to_port'],
            remote_ip=self._security_group_rule['ip_range']['cidr'],
            remote_group=None,
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)

    def test_security_group_rule_create_remote_group(self, sgr_mock):
        expected_columns, expected_data = self._setup_security_group_rule(
            {
                'from_port': 22,
                'to_port': 22,
                'group': {'name': self._security_group['name']},
            }
        )
        sgr_mock.return_value = self._security_group_rule
        arglist = [
            '--dst-port',
            str(self._security_group_rule['from_port']),
            '--remote-group',
            self._security_group['name'],
            self._security_group['id'],
        ]
        verifylist = [
            (
                'dst_port',
                (
                    self._security_group_rule['from_port'],
                    self._security_group_rule['to_port'],
                ),
            ),
            ('remote_group', self._security_group['name']),
            ('group', self._security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sgr_mock.assert_called_once_with(
            self.compute_client,
            security_group_id=self._security_group['id'],
            ip_protocol=self._security_group_rule['ip_protocol'],
            from_port=self._security_group_rule['from_port'],
            to_port=self._security_group_rule['to_port'],
            remote_ip=self._security_group_rule['ip_range']['cidr'],
            remote_group=self._security_group['id'],
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)

    def test_security_group_rule_create_remote_ip(self, sgr_mock):
        expected_columns, expected_data = self._setup_security_group_rule(
            {
                'ip_protocol': 'icmp',
                'from_port': -1,
                'to_port': -1,
                'ip_range': {'cidr': '10.0.2.0/24'},
            }
        )
        sgr_mock.return_value = self._security_group_rule
        arglist = [
            '--protocol',
            self._security_group_rule['ip_protocol'],
            '--remote-ip',
            self._security_group_rule['ip_range']['cidr'],
            self._security_group['id'],
        ]
        verifylist = [
            ('protocol', self._security_group_rule['ip_protocol']),
            ('remote_ip', self._security_group_rule['ip_range']['cidr']),
            ('group', self._security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sgr_mock.assert_called_once_with(
            self.compute_client,
            security_group_id=self._security_group['id'],
            ip_protocol=self._security_group_rule['ip_protocol'],
            from_port=self._security_group_rule['from_port'],
            to_port=self._security_group_rule['to_port'],
            remote_ip=self._security_group_rule['ip_range']['cidr'],
            remote_group=None,
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)

    def test_security_group_rule_create_proto_option(self, sgr_mock):
        expected_columns, expected_data = self._setup_security_group_rule(
            {
                'ip_protocol': 'icmp',
                'from_port': -1,
                'to_port': -1,
                'ip_range': {'cidr': '10.0.2.0/24'},
            }
        )
        sgr_mock.return_value = self._security_group_rule
        arglist = [
            '--proto',
            self._security_group_rule['ip_protocol'],
            '--remote-ip',
            self._security_group_rule['ip_range']['cidr'],
            self._security_group['id'],
        ]
        verifylist = [
            ('proto', self._security_group_rule['ip_protocol']),
            ('protocol', None),
            ('remote_ip', self._security_group_rule['ip_range']['cidr']),
            ('group', self._security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        sgr_mock.assert_called_once_with(
            self.compute_client,
            security_group_id=self._security_group['id'],
            ip_protocol=self._security_group_rule['ip_protocol'],
            from_port=self._security_group_rule['from_port'],
            to_port=self._security_group_rule['to_port'],
            remote_ip=self._security_group_rule['ip_range']['cidr'],
            remote_group=None,
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)


@mock.patch.object(compute_v2, 'delete_security_group_rule')
class TestDeleteSecurityGroupRuleCompute(compute_fakes.TestComputev2):
    # The security group rule to be deleted.
    _security_group_rules = compute_fakes.create_security_group_rules(count=2)

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Get the command object to test
        self.cmd = security_group_rule.DeleteSecurityGroupRule(self.app, None)

    def test_security_group_rule_delete(self, sgr_mock):
        arglist = [
            self._security_group_rules[0]['id'],
        ]
        verifylist = [
            ('rule', [self._security_group_rules[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        sgr_mock.assert_called_once_with(
            self.compute_client, self._security_group_rules[0]['id']
        )
        self.assertIsNone(result)

    def test_security_group_rule_delete_multi(self, sgr_mock):
        arglist = [
            self._security_group_rules[0]['id'],
            self._security_group_rules[1]['id'],
        ]
        verifylist = [
            ('rule', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        sgr_mock.assert_has_calls(
            [
                mock.call(
                    self.compute_client,
                    self._security_group_rules[0]['id'],
                ),
                mock.call(
                    self.compute_client,
                    self._security_group_rules[1]['id'],
                ),
            ]
        )
        self.assertIsNone(result)

    def test_security_group_rule_delete_multi_with_exception(self, sgr_mock):
        arglist = [
            self._security_group_rules[0]['id'],
            'unexist_rule',
        ]
        verifylist = [
            ('rule', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        sgr_mock.side_effect = [None, exceptions.NotFound('foo')]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 rules failed to delete.', str(e))

        sgr_mock.assert_has_calls(
            [
                mock.call(
                    self.compute_client,
                    self._security_group_rules[0]['id'],
                ),
                mock.call(self.compute_client, 'unexist_rule'),
            ]
        )


class TestListSecurityGroupRuleCompute(compute_fakes.TestComputev2):
    # The security group to hold the rules.
    _security_group = compute_fakes.create_one_security_group()

    # The security group rule to be listed.
    _security_group_rule_tcp = compute_fakes.create_one_security_group_rule(
        {
            'ip_protocol': 'tcp',
            'ethertype': 'IPv4',
            'from_port': 80,
            'to_port': 80,
            'group': {'name': _security_group['name']},
        }
    )
    _security_group_rule_icmp = compute_fakes.create_one_security_group_rule(
        {
            'ip_protocol': 'icmp',
            'ethertype': 'IPv4',
            'from_port': -1,
            'to_port': -1,
            'ip_range': {'cidr': '10.0.2.0/24'},
            'group': {'name': _security_group['name']},
        }
    )
    _security_group['rules'] = [
        _security_group_rule_tcp,
        _security_group_rule_icmp,
    ]

    expected_columns_with_group = (
        'ID',
        'IP Protocol',
        'Ethertype',
        'IP Range',
        'Port Range',
        'Direction',
        'Remote Security Group',
    )
    expected_columns_no_group = expected_columns_with_group + (
        'Security Group',
    )

    expected_data_with_group = []
    expected_data_no_group = []
    for _security_group_rule in _security_group['rules']:
        rule = network_utils.transform_compute_security_group_rule(
            _security_group_rule
        )
        expected_rule_with_group = (
            rule['id'],
            rule['ip_protocol'],
            rule['ethertype'],
            rule['ip_range'],
            rule['port_range'],
            rule['remote_security_group'],
        )
        expected_rule_no_group = expected_rule_with_group + (
            _security_group_rule['parent_group_id'],
        )
        expected_data_with_group.append(expected_rule_with_group)
        expected_data_no_group.append(expected_rule_no_group)

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        compute_v2.find_security_group = mock.Mock(
            return_value=self._security_group,
        )
        compute_v2.list_security_groups = mock.Mock(
            return_value=[self._security_group],
        )

        # Get the command object to test
        self.cmd = security_group_rule.ListSecurityGroupRule(self.app, None)

    def test_security_group_rule_list_default(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)
        compute_v2.list_security_groups.assert_called_once_with(
            self.compute_client, all_projects=False
        )
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))

    def test_security_group_rule_list_with_group(self):
        arglist = [
            self._security_group['id'],
        ]
        verifylist = [
            ('group', self._security_group['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        compute_v2.find_security_group.assert_called_once_with(
            self.compute_client, self._security_group['id']
        )
        self.assertEqual(self.expected_columns_with_group, columns)
        self.assertEqual(self.expected_data_with_group, list(data))

    def test_security_group_rule_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        compute_v2.list_security_groups.assert_called_once_with(
            self.compute_client, all_projects=True
        )
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))

    def test_security_group_rule_list_with_ignored_options(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        compute_v2.list_security_groups.assert_called_once_with(
            self.compute_client, all_projects=False
        )
        self.assertEqual(self.expected_columns_no_group, columns)
        self.assertEqual(self.expected_data_no_group, list(data))


class TestShowSecurityGroupRuleCompute(compute_fakes.TestComputev2):
    # The security group rule to be shown.
    _security_group_rule = compute_fakes.create_one_security_group_rule()

    columns, data = network_utils.format_security_group_rule_show(
        _security_group_rule
    )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Build a security group fake customized for this test.
        security_group_rules = [self._security_group_rule]
        security_group = {'rules': security_group_rules}
        compute_v2.list_security_groups = mock.Mock(
            return_value=[security_group],
        )

        # Get the command object to test
        self.cmd = security_group_rule.ShowSecurityGroupRule(self.app, None)

    def test_security_group_rule_show_no_options(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_security_group_rule_show_all_options(self):
        arglist = [
            self._security_group_rule['id'],
        ]
        verifylist = [
            ('rule', self._security_group_rule['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        compute_v2.list_security_groups.assert_called_once_with(
            self.compute_client
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
