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

"""Subnet action implementations"""

from openstackclient.common import command
from openstackclient.common import utils


def _format_allocation_pools(data):
    pool_formatted = ['%s-%s' % (pool.get('start', ''), pool.get('end', ''))
                      for pool in data]
    return ','.join(pool_formatted)


_formatters = {
    'allocation_pools': _format_allocation_pools,
    'dns_nameservers': utils.format_list,
    'host_routes': utils.format_list,
}


def _get_columns(item):
    columns = item.keys()
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


class DeleteSubnet(command.Command):
    """Delete subnet"""

    def get_parser(self, prog_name):
        parser = super(DeleteSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help="Subnet to delete (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        client.delete_subnet(
            client.find_subnet(parsed_args.subnet))


class ListSubnet(command.Lister):
    """List subnets"""

    def get_parser(self, prog_name):
        parser = super(ListSubnet, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        data = self.app.client_manager.network.subnets()

        headers = ('ID', 'Name', 'Network', 'Subnet')
        columns = ('id', 'name', 'network_id', 'cidr')
        if parsed_args.long:
            headers += ('Project', 'DHCP', 'Name Servers',
                        'Allocation Pools', 'Host Routes', 'IP Version',
                        'Gateway')
            columns += ('tenant_id', 'enable_dhcp', 'dns_nameservers',
                        'allocation_pools', 'host_routes', 'ip_version',
                        'gateway_ip')

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class ShowSubnet(command.ShowOne):
    """Show subnet details"""

    def get_parser(self, prog_name):
        parser = super(ShowSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'subnet',
            metavar="<subnet>",
            help="Subnet to show (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        obj = self.app.client_manager.network.find_subnet(parsed_args.subnet,
                                                          ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (columns, data)
