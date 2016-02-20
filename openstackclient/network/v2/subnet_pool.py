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
from openstackclient.common import utils


def _get_columns(item):
    columns = item.keys()
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


_formatters = {
    'prefixes': utils.format_list,
}


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


class ListSubnetPool(command.Lister):
    """List subnet pools"""

    def get_parser(self, prog_name):
        parser = super(ListSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        data = self.app.client_manager.network.subnet_pools()

        if parsed_args.long:
            headers = (
                'ID',
                'Name',
                'Prefixes',
                'Default Prefix Length',
                'Address Scope',
            )
            columns = (
                'id',
                'name',
                'prefixes',
                'default_prefixlen',
                'address_scope_id',
            )
        else:
            headers = (
                'ID',
                'Name',
                'Prefixes',
            )
            columns = (
                'id',
                'name',
                'prefixes',
            )

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowSubnetPool(command.ShowOne):
    """Display subnet pool details"""

    def get_parser(self, prog_name):
        parser = super(ShowSubnetPool, self).get_parser(prog_name)
        parser.add_argument(
            'subnet_pool',
            metavar="<subnet-pool>",
            help=("Subnet pool to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_subnet_pool(
            parsed_args.subnet_pool,
            ignore_missing=False
        )
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)
