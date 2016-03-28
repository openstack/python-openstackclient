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

from openstackclient.compute.v2 import security_group
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


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

        # Get a shortcut compute client security_groups mock
        self.secgroups_mock = self.app.client_manager.compute.security_groups
        self.secgroups_mock.reset_mock()

        # Get a shortcut compute client security_group_rules mock
        self.sg_rules_mock = \
            self.app.client_manager.compute.security_group_rules
        self.sg_rules_mock.reset_mock()


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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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
