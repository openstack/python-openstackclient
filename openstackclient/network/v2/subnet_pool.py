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

"""Subnet pool action implementations"""

from openstackclient.common import command


class DeleteSubnetPool(command.Command):
    """Delete subnet pool"""

    def get_parser(self, prog_name):
        parser = super(DeleteSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar="<subnet-pool>",
            help=("Subnet pool to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(parsed_args.subnet_pool)
        client.delete_subnet_pool(obj)
