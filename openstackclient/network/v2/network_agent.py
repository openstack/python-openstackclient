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

"""Network agent action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import sdk_utils


LOG = logging.getLogger(__name__)


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


_formatters = {
    'admin_state_up': _format_admin_state,
    'is_admin_state_up': _format_admin_state,
    'configurations': utils.format_dict,
}


def _get_network_columns(item):
    column_map = {
        'is_admin_state_up': 'admin_state_up',
        'is_alive': 'alive',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


class DeleteNetworkAgent(command.Command):
    _description = _("Delete network agent(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteNetworkAgent, self).get_parser(prog_name)
        parser.add_argument(
            'network_agent',
            metavar="<network-agent>",
            nargs='+',
            help=(_("Network agent(s) to delete (ID only)"))
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for agent in parsed_args.network_agent:
            try:
                obj = client.get_agent(agent, ignore_missing=False)
                client.delete_agent(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete network agent with "
                            "ID '%(agent)s': %(e)s"),
                          {'agent': agent, 'e': e})

        if result > 0:
            total = len(parsed_args.network_agent)
            msg = (_("%(result)s of %(total)s network agents failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


# TODO(huanxuan): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListNetworkAgent(command.Lister):
    _description = _("List network agents")

    def get_parser(self, prog_name):
        parser = super(ListNetworkAgent, self).get_parser(prog_name)
        parser.add_argument(
            '--agent-type',
            metavar='<agent-type>',
            choices=["dhcp", "open-vswitch", "linux-bridge", "ofa", "l3",
                     "loadbalancer", "metering", "metadata", "macvtap", "nic"],
            help=_("List only agents with the specified agent type. "
                   "The supported agent types are: dhcp, open-vswitch, "
                   "linux-bridge, ofa, l3, loadbalancer, metering, "
                   "metadata, macvtap, nic.")
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_("List only agents running on the specified host")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'agent_type',
            'host',
            'availability_zone',
            'is_alive',
            'is_admin_state_up',
            'binary'
        )
        column_headers = (
            'ID',
            'Agent Type',
            'Host',
            'Availability Zone',
            'Alive',
            'State',
            'Binary'
        )

        key_value = {
            'dhcp': 'DHCP agent',
            'open-vswitch': 'Open vSwitch agent',
            'linux-bridge': 'Linux bridge agent',
            'ofa': 'OFA driver agent',
            'l3': 'L3 agent',
            'loadbalancer': 'Loadbalancer agent',
            'metering': 'Metering agent',
            'metadata': 'Metadata agent',
            'macvtap': 'Macvtap agent',
            'nic': 'NIC Switch agent'
        }

        filters = {}
        if parsed_args.agent_type is not None:
            filters['agent_type'] = key_value[parsed_args.agent_type]
        if parsed_args.host is not None:
            filters['host'] = parsed_args.host

        data = client.agents(**filters)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=_formatters,
                ) for s in data))


# TODO(huanxuan): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetworkAgent(command.Command):
    _description = _("Set network agent properties")

    def get_parser(self, prog_name):
        parser = super(SetNetworkAgent, self).get_parser(prog_name)
        parser.add_argument(
            'network_agent',
            metavar="<network-agent>",
            help=(_("Network agent to modify (ID only)"))
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Set network agent description")
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            help=_("Enable network agent")
        )
        admin_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable network agent")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.get_agent(parsed_args.network_agent)
        attrs = {}
        if parsed_args.description is not None:
            attrs['description'] = str(parsed_args.description)
        # TODO(huanxuan): Also update by the new attribute name
        # "is_admin_state_up" after sdk 0.9.12
        if parsed_args.enable:
            attrs['admin_state_up'] = True
        if parsed_args.disable:
            attrs['admin_state_up'] = False
        client.update_agent(obj, **attrs)


class ShowNetworkAgent(command.ShowOne):
    _description = _("Display network agent details")

    def get_parser(self, prog_name):
        parser = super(ShowNetworkAgent, self).get_parser(prog_name)
        parser.add_argument(
            'network_agent',
            metavar="<network-agent>",
            help=(_("Network agent to display (ID only)"))
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.get_agent(parsed_args.network_agent)
        display_columns, columns = _get_network_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters,)
        return display_columns, data
