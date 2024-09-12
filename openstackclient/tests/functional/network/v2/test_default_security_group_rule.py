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

import random

from openstackclient.tests.functional.network.v2 import common


class SecurityGroupRuleTests(common.NetworkTests):
    """Functional tests for security group rule"""

    def setUp(self):
        super().setUp()

        if not self.is_extension_enabled("security-groups-default-rules"):
            self.skipTest("No security-groups-default-rules extension present")

        self.port = random.randint(1, 65535)
        self.protocol = random.choice(["tcp", "udp"])
        self.direction = random.choice(["ingress", "egress"])
        # Create the default security group rule.
        cmd_output = self.openstack(
            'default security group rule create '
            f'--protocol {self.protocol} '
            f'--dst-port {self.port}:{self.port} '
            f'--{self.direction} --ethertype IPv4 ',
            parse_output=True,
        )
        self.addCleanup(
            self.openstack,
            'default security group rule delete ' + cmd_output['id'],
        )
        self.DEFAULT_SG_RULE_ID = cmd_output['id']

    def test_security_group_rule_list(self):
        cmd_output = self.openstack(
            'default security group rule list ',
            parse_output=True,
        )
        self.assertIn(
            self.DEFAULT_SG_RULE_ID, [rule['ID'] for rule in cmd_output]
        )

    def test_security_group_rule_show(self):
        cmd_output = self.openstack(
            'default security group rule show ' + self.DEFAULT_SG_RULE_ID,
            parse_output=True,
        )
        self.assertEqual(self.DEFAULT_SG_RULE_ID, cmd_output['id'])
        self.assertEqual(self.protocol, cmd_output['protocol'])
        self.assertEqual(self.port, cmd_output['port_range_min'])
        self.assertEqual(self.port, cmd_output['port_range_max'])
        self.assertEqual(self.direction, cmd_output['direction'])
