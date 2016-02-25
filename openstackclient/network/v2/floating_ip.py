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

"""IP Floating action implementations"""

from openstackclient.common import utils
from openstackclient.network import common


def _get_columns(item):
    columns = item.keys()
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    return tuple(sorted(columns))


class DeleteFloatingIP(common.NetworkAndComputeCommand):
    """Delete floating IP"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'floating_ip',
            metavar="<floating-ip>",
            help=("Floating IP to delete (IP address or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_ip(parsed_args.floating_ip)
        client.delete_ip(obj)

    def take_action_compute(self, client, parsed_args):
        obj = utils.find_resource(
            client.floating_ips,
            parsed_args.floating_ip,
        )
        client.floating_ips.delete(obj.id)


class ListFloatingIP(common.NetworkAndComputeLister):
    """List floating IP(s)"""

    def take_action_network(self, client, parsed_args):
        columns = (
            'id',
            'floating_ip_address',
            'fixed_ip_address',
            'port_id',
        )
        headers = (
            'ID',
            'Floating IP Address',
            'Fixed IP Address',
            'Port',
        )

        query = {}
        data = client.ips(**query)

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))

    def take_action_compute(self, client, parsed_args):
        columns = (
            'ID',
            'IP',
            'Fixed IP',
            'Instance ID',
            'Pool',
        )
        headers = (
            'ID',
            'Floating IP Address',
            'Fixed IP Address',
            'Server',
            'Pool',
        )

        data = client.floating_ips.list()

        return (headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowFloatingIP(common.NetworkAndComputeShowOne):
    """Show floating IP details"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'floating_ip',
            metavar="<floating-ip>",
            help=("Floating IP to display (IP address or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_ip(parsed_args.floating_ip, ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = utils.find_resource(
            client.floating_ips,
            parsed_args.floating_ip,
        )
        columns = _get_columns(obj._info)
        data = utils.get_dict_properties(obj._info, columns)
        return (columns, data)
