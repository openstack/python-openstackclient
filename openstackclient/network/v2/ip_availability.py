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

"""IP Availability Info implementations"""

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils


_formatters = {
    'location': format_columns.DictColumn,
    'subnet_ip_availability': format_columns.ListDictColumn,
}


def _get_columns(item):
    column_map = {
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


# TODO(ankur-gupta-f): Use the SDK resource mapped attribute names once
# the OSC minimum requirements include SDK 1.0.
class ListIPAvailability(command.Lister):
    _description = _("List IP availability for network")

    def get_parser(self, prog_name):
        parser = super(ListIPAvailability, self).get_parser(prog_name)
        parser.add_argument(
            '--ip-version',
            type=int,
            default=4,
            choices=[4, 6],
            metavar='<ip-version>',
            dest='ip_version',
            help=_("List IP availability of given IP version "
                   "networks (default is 4)"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List IP availability of given project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'network_id',
            'network_name',
            'total_ips',
            'used_ips',
        )
        column_headers = (
            'Network ID',
            'Network Name',
            'Total IPs',
            'Used IPs',
        )

        filters = {}
        if parsed_args.ip_version:
            filters['ip_version'] = parsed_args.ip_version

        if parsed_args.project:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['tenant_id'] = project_id
            filters['project_id'] = project_id
        data = client.network_ip_availabilities(**filters)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowIPAvailability(command.ShowOne):
    _description = _("Show network IP availability details")

    def get_parser(self, prog_name):
        parser = super(ShowIPAvailability, self).get_parser(prog_name)
        parser.add_argument(
            'network',
            metavar="<network>",
            help=_("Show IP availability for a specific network (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        network_id = client.find_network(parsed_args.network,
                                         ignore_missing=False).id
        obj = client.find_network_ip_availability(network_id,
                                                  ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)
