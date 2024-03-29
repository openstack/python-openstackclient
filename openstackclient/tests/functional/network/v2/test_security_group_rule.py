#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

from openstackclient.tests.functional.network.v2 import common


class SecurityGroupRuleTests(common.NetworkTests):
    """Functional tests for security group rule"""

    def setUp(self):
        super().setUp()

        self.SECURITY_GROUP_NAME = uuid.uuid4().hex

        # Create the security group to hold the rule
        cmd_output = self.openstack(
            'security group create ' + self.SECURITY_GROUP_NAME,
            parse_output=True,
        )
        self.addCleanup(
            self.openstack, 'security group delete ' + self.SECURITY_GROUP_NAME
        )
        self.assertEqual(self.SECURITY_GROUP_NAME, cmd_output['name'])

        # Create the security group rule.
        cmd_output = self.openstack(
            'security group rule create '
            + self.SECURITY_GROUP_NAME
            + ' '
            + '--protocol tcp --dst-port 80:80 '
            + '--ingress --ethertype IPv4 ',
            parse_output=True,
        )
        self.addCleanup(
            self.openstack, 'security group rule delete ' + cmd_output['id']
        )
        self.SECURITY_GROUP_RULE_ID = cmd_output['id']

    def test_security_group_rule_list(self):
        cmd_output = self.openstack(
            'security group rule list ' + self.SECURITY_GROUP_NAME,
            parse_output=True,
        )
        self.assertIn(
            self.SECURITY_GROUP_RULE_ID, [rule['ID'] for rule in cmd_output]
        )

    def test_security_group_rule_show(self):
        cmd_output = self.openstack(
            'security group rule show ' + self.SECURITY_GROUP_RULE_ID,
            parse_output=True,
        )
        self.assertEqual(self.SECURITY_GROUP_RULE_ID, cmd_output['id'])
