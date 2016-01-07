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

from openstackclient.compute.v2 import security_group
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests import utils


security_group_id = '11'
security_group_name = 'wide-open'
security_group_description = 'nothing but net'

security_group_rule_id = '1'
security_group_rule_cidr = '0.0.0.0/0'

SECURITY_GROUP_RULE = {
    'id': security_group_rule_id,
    'group': {},
    'ip_protocol': 'tcp',
    'ip_range': {'cidr': security_group_rule_cidr},
    'parent_group_id': security_group_id,
    'from_port': 0,
    'to_port': 0,
}

SECURITY_GROUP_RULE_ICMP = {
    'id': security_group_rule_id,
    'group': {},
    'ip_protocol': 'icmp',
    'ip_range': {'cidr': security_group_rule_cidr},
    'parent_group_id': security_group_id,
    'from_port': -1,
    'to_port': -1,
}

SECURITY_GROUP_RULE_REMOTE_GROUP = {
    'id': security_group_rule_id,
    'group': {"tenant_id": "14", "name": "default"},
    'ip_protocol': 'tcp',
    'ip_range': {},
    'parent_group_id': security_group_id,
    'from_port': 80,
    'to_port': 80,
}

SECURITY_GROUP = {
    'id': security_group_id,
    'name': security_group_name,
    'description': security_group_description,
    'tenant_id': identity_fakes.project_id,
    'rules': [SECURITY_GROUP_RULE,
              SECURITY_GROUP_RULE_ICMP,
              SECURITY_GROUP_RULE_REMOTE_GROUP],
}

security_group_2_id = '12'
security_group_2_name = 'he-shoots'
security_group_2_description = 'he scores'

SECURITY_GROUP_2_RULE = {
    'id': '2',
    'group': {},
    'ip_protocol': 'tcp',
    'ip_range': {},
    'parent_group_id': security_group_2_id,
    'from_port': 80,
    'to_port': 80,
}

SECURITY_GROUP_2 = {
    'id': security_group_2_id,
    'name': security_group_2_name,
    'description': security_group_2_description,
    'tenant_id': identity_fakes.project_id,
    'rules': [SECURITY_GROUP_2_RULE],
}


class FakeSecurityGroupRuleResource(fakes.FakeResource):

    def get_keys(self):
        return {'property': 'value'}


class TestSecurityGroupRule(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupRule, self).setUp()

        self.secgroups_mock = mock.Mock()
        self.secgroups_mock.resource_class = fakes.FakeResource(None, {})
        self.app.client_manager.compute.security_groups = self.secgroups_mock
        self.secgroups_mock.reset_mock()

        self.sg_rules_mock = mock.Mock()
        self.sg_rules_mock.resource_class = fakes.FakeResource(None, {})
        self.app.client_manager.compute.security_group_rules = \
            self.sg_rules_mock
        self.sg_rules_mock.reset_mock()


class TestSecurityGroupRuleCreate(TestSecurityGroupRule):

    columns = (
        'id',
        'ip_protocol',
        'ip_range',
        'parent_group_id',
        'port_range',
        'remote_security_group',
    )

    def setUp(self):
        super(TestSecurityGroupRuleCreate, self).setUp()

        self.secgroups_mock.get.return_value = FakeSecurityGroupRuleResource(
            None,
            copy.deepcopy(SECURITY_GROUP),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroupRule(self.app, None)

    def test_security_group_rule_create_no_options(self):
        self.sg_rules_mock.create.return_value = FakeSecurityGroupRuleResource(
            None,
            copy.deepcopy(SECURITY_GROUP_RULE),
            loaded=True,
        )

        arglist = [
            security_group_name,
        ]
        verifylist = [
            ('group', security_group_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.sg_rules_mock.create.assert_called_with(
            security_group_id,
            'tcp',
            0,
            0,
            security_group_rule_cidr,
            None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            security_group_rule_id,
            'tcp',
            security_group_rule_cidr,
            security_group_id,
            '0:0',
            '',
        )
        self.assertEqual(datalist, data)

    def test_security_group_rule_create_ftp(self):
        sg_rule = copy.deepcopy(SECURITY_GROUP_RULE)
        sg_rule['from_port'] = 20
        sg_rule['to_port'] = 21
        self.sg_rules_mock.create.return_value = FakeSecurityGroupRuleResource(
            None,
            sg_rule,
            loaded=True,
        )

        arglist = [
            security_group_name,
            '--dst-port', '20:21',
        ]
        verifylist = [
            ('group', security_group_name),
            ('dst_port', (20, 21)),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.sg_rules_mock.create.assert_called_with(
            security_group_id,
            'tcp',
            20,
            21,
            security_group_rule_cidr,
            None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            security_group_rule_id,
            'tcp',
            security_group_rule_cidr,
            security_group_id,
            '20:21',
            '',
        )
        self.assertEqual(datalist, data)

    def test_security_group_rule_create_ssh(self):
        sg_rule = copy.deepcopy(SECURITY_GROUP_RULE)
        sg_rule['from_port'] = 22
        sg_rule['to_port'] = 22
        sg_rule['ip_range'] = {}
        sg_rule['group'] = {'name': security_group_name}
        self.sg_rules_mock.create.return_value = FakeSecurityGroupRuleResource(
            None,
            sg_rule,
            loaded=True,
        )

        arglist = [
            security_group_name,
            '--dst-port', '22',
            '--src-group', security_group_id,
        ]
        verifylist = [
            ('group', security_group_name),
            ('dst_port', (22, 22)),
            ('src_group', security_group_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.sg_rules_mock.create.assert_called_with(
            security_group_id,
            'tcp',
            22,
            22,
            security_group_rule_cidr,
            security_group_id,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            security_group_rule_id,
            'tcp',
            '',
            security_group_id,
            '22:22',
            security_group_name,
        )
        self.assertEqual(datalist, data)

    def test_security_group_rule_create_udp(self):
        sg_rule = copy.deepcopy(SECURITY_GROUP_RULE)
        sg_rule['ip_protocol'] = 'udp'
        self.sg_rules_mock.create.return_value = FakeSecurityGroupRuleResource(
            None,
            sg_rule,
            loaded=True,
        )

        arglist = [
            security_group_name,
            '--proto', 'udp',
        ]
        verifylist = [
            ('group', security_group_name),
            ('proto', 'udp'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.sg_rules_mock.create.assert_called_with(
            security_group_id,
            'udp',
            0,
            0,
            security_group_rule_cidr,
            None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            security_group_rule_id,
            'udp',
            security_group_rule_cidr,
            security_group_id,
            '0:0',
            '',
        )
        self.assertEqual(datalist, data)

    def test_security_group_rule_create_icmp(self):
        sg_rule_cidr = '10.0.2.0/24'
        sg_rule = copy.deepcopy(SECURITY_GROUP_RULE_ICMP)
        sg_rule['ip_range'] = {'cidr': sg_rule_cidr}
        self.sg_rules_mock.create.return_value = FakeSecurityGroupRuleResource(
            None,
            sg_rule,
            loaded=True,
        )

        arglist = [
            security_group_name,
            '--proto', 'ICMP',
            '--src-ip', sg_rule_cidr,
        ]
        verifylist = [
            ('group', security_group_name),
            ('proto', 'ICMP'),
            ('src_ip', sg_rule_cidr)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.sg_rules_mock.create.assert_called_with(
            security_group_id,
            'ICMP',
            -1,
            -1,
            sg_rule_cidr,
            None,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            security_group_rule_id,
            'icmp',
            sg_rule_cidr,
            security_group_id,
            '',
            '',
        )
        self.assertEqual(datalist, data)

    def test_security_group_rule_create_src_invalid(self):
        arglist = [
            security_group_name,
            '--proto', 'ICMP',
            '--src-ip', security_group_rule_cidr,
            '--src-group', security_group_id,
        ]

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])


class TestSecurityGroupRuleList(TestSecurityGroupRule):

    def setUp(self):
        super(TestSecurityGroupRuleList, self).setUp()

        security_group_mock = FakeSecurityGroupRuleResource(
            None,
            copy.deepcopy(SECURITY_GROUP),
            loaded=True,
        )

        security_group_2_mock = FakeSecurityGroupRuleResource(
            None,
            copy.deepcopy(SECURITY_GROUP_2),
            loaded=True,
        )

        self.secgroups_mock.get.return_value = security_group_mock
        self.secgroups_mock.list.return_value = [security_group_mock,
                                                 security_group_2_mock]

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroupRule(self.app, None)

    def test_security_group_rule_list(self):

        arglist = [
            security_group_name,
        ]
        verifylist = [
            ('group', security_group_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            'ID',
            'IP Protocol',
            'IP Range',
            'Port Range',
            'Remote Security Group',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            security_group_rule_id,
            'tcp',
            security_group_rule_cidr,
            '0:0',
            '',
        ), (
            security_group_rule_id,
            'icmp',
            security_group_rule_cidr,
            '',
            '',
        ), (
            security_group_rule_id,
            'tcp',
            '',
            '80:80',
            'default',
        ),)
        self.assertEqual(datalist, tuple(data))

    def test_security_group_rule_list_no_group(self):

        parsed_args = self.check_parser(self.cmd, [], [])

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            'ID',
            'IP Protocol',
            'IP Range',
            'Port Range',
            'Remote Security Group',
            'Security Group',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            security_group_rule_id,
            'tcp',
            security_group_rule_cidr,
            '0:0',
            '',
            security_group_id,
        ), (
            security_group_rule_id,
            'icmp',
            security_group_rule_cidr,
            '',
            '',
            security_group_id,
        ), (
            security_group_rule_id,
            'tcp',
            '',
            '80:80',
            'default',
            security_group_id,
        ), (
            '2',
            'tcp',
            '',
            '80:80',
            '',
            security_group_2_id,
        ),)
        self.assertEqual(datalist, tuple(data))
