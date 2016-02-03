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

"""Port action implementations"""

from openstackclient.common import command
from openstackclient.common import utils


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


_formatters = {
    'admin_state_up': _format_admin_state,
    'allowed_address_pairs': utils.format_list_of_dicts,
    'binding_profile': utils.format_dict,
    'binding_vif_details': utils.format_dict,
    'dns_assignment':  utils.format_list_of_dicts,
    'extra_dhcp_opts': utils.format_list_of_dicts,
    'fixed_ips':  utils.format_list_of_dicts,
    'security_groups': utils.format_list,
}


def _get_columns(item):
    columns = item.keys()
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    binding_columns = [
        'binding:host_id',
        'binding:profile',
        'binding:vif_details',
        'binding:vif_type',
        'binding:vnic_type',
    ]
    for binding_column in binding_columns:
        if binding_column in columns:
            columns.remove(binding_column)
            columns.append(binding_column.replace('binding:', 'binding_', 1))
    return sorted(columns)


class DeletePort(command.Command):
    """Delete port(s)"""

    def get_parser(self, prog_name):
        parser = super(DeletePort, self).get_parser(prog_name)
        parser.add_argument(
            'port',
            metavar="<port>",
            nargs="+",
            help=("Port(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        for port in parsed_args.port:
            res = client.find_port(port)
            client.delete_port(res)


class ShowPort(command.ShowOne):
    """Display port details"""

    def get_parser(self, prog_name):
        parser = super(ShowPort, self).get_parser(prog_name)
        parser.add_argument(
            'port',
            metavar="<port>",
            help="Port to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_port(parsed_args.port, ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (tuple(columns), data)
