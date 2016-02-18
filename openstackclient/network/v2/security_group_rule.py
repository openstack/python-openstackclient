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

"""Security Group Rule action implementations"""

from openstackclient.network import common


class DeleteSecurityGroupRule(common.NetworkAndComputeCommand):
    """Delete a security group rule"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'rule',
            metavar='<rule>',
            help='Security group rule to delete (ID only)',
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group_rule(parsed_args.rule)
        client.delete_security_group_rule(obj)

    def take_action_compute(self, client, parsed_args):
        client.security_group_rules.delete(parsed_args.rule)
