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

"""RBAC action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    if 'target_tenant' in columns:
        columns.remove('target_tenant')
        columns.append('target_project')
    return tuple(sorted(columns))


class ListNetworkRBAC(command.Lister):
    """List network RBAC policies"""

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'object_type',
            'object_id',
        )
        column_headers = (
            'ID',
            'Object Type',
            'Object ID',
        )

        data = client.rbac_policies()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowNetworkRBAC(command.ShowOne):
    """Display network RBAC policy details"""

    def get_parser(self, prog_name):
        parser = super(ShowNetworkRBAC, self).get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            help=_("RBAC policy (ID only)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_rbac_policy(parsed_args.rbac_policy,
                                      ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return columns, data
