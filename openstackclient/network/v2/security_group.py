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

"""Security Group action implementations"""

from openstackclient.common import utils
from openstackclient.network import common


class DeleteSecurityGroup(common.NetworkAndComputeCommand):
    """Delete a security group"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Security group to delete (name or ID)',
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(parsed_args.group)
        client.delete_security_group(obj)

    def take_action_compute(self, client, parsed_args):
        data = utils.find_resource(
            client.security_groups,
            parsed_args.group,
        )
        client.security_groups.delete(data.id)
