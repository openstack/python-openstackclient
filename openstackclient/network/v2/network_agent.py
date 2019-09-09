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

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import sdk_utils


LOG = logging.getLogger(__name__)


class AliveColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return ":-)" if self._value else "XXX"


class AdminStateColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return 'UP' if self._value else 'DOWN'


_formatters = {
    'is_alive': AliveColumn,
    'alive': AliveColumn,
    'admin_state_up': AdminStateColumn,
    'is_admin_state_up': AdminStateColumn,
    'location': format_columns.DictColumn,
    'configurations': format_columns.DictColumn,
}


def _get_network_columns(item):
    column_map = {
        'is_admin_state_up': 'admin_state_up',
        'is_alive': 'alive',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


class AddNetworkToAgent(command.Command):
    _description = _("Add network to an agent")

    def get_parser(self, prog_name):
        parser = super(AddNetworkToAgent, self).get_parser(prog_name)
        parser.add_argument(
            '--dhcp',
            action='store_true',
            help=_('Add network to a DHCP agent'))
        parser.add_argument(
            'agent_id',
            metavar='<agent-id>',
            help=_('Agent to which a network is added (ID only)'))
        parser.add_argument(
            'network',
            metavar='<network>',
            help=_('Network to be added to an agent (name or ID)'))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        agent = client.get_agent(parsed_args.agent_id)
        network = client.find_network(
            parsed_args.network, ignore_missing=False)
        if parsed_args.dhcp:
            try:
                client.add_dhcp_agent_to_network(agent, network)
            except Exception:
                msg = 'Failed to add {} to {}'.format(
                    network.name, agent.agent_type)
                exceptions.CommandError(msg)


class AddRouterToAgent(command.Command):
    _description = _("Add router to an agent")

    def get_parser(self, prog_name):
        parser = super(AddRouterToAgent, self).get_parser(prog_name)
        parser.add_argument(
            '--l3',
            action='store_true',
            help=_('Add router to an L3 agent')
        )
        parser.add_argument(
            'agent_id',
            metavar='<agent-id>',
            help=_("Agent to which a router is added (ID only)")
        )
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router to be added to an agent (name or ID)")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        agent = client.get_agent(parsed_args.agent_id)
        router = client.find_router(parsed_args.router, ignore_missing=False)
        if parsed_args.l3:
            client.add_router_to_agent(agent, router)


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
                client.delete_agent(agent, ignore_missing=False)
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
            choices=["bgp", "dhcp", "open-vswitch", "linux-bridge", "ofa",
                     "l3", "loadbalancer", "metering", "metadata", "macvtap",
                     "nic"],
            help=_("List only agents with the specified agent type. "
                   "The supported agent types are: bgp, dhcp, open-vswitch, "
                   "linux-bridge, ofa, l3, loadbalancer, metering, "
                   "metadata, macvtap, nic.")
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_("List only agents running on the specified host")
        )
        agent_type_group = parser.add_mutually_exclusive_group()
        agent_type_group.add_argument(
            '--network',
            metavar='<network>',
            help=_('List agents hosting a network (name or ID)')
        )
        agent_type_group.add_argument(
            '--router',
            metavar='<router>',
            help=_('List agents hosting this router (name or ID)')
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
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
            'bgp': 'BGP dynamic routing agent',
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

        if parsed_args.network is not None:
            network = client.find_network(
                parsed_args.network, ignore_missing=False)
            data = client.network_hosting_dhcp_agents(network)
        elif parsed_args.router is not None:
            if parsed_args.long:
                columns += ('ha_state',)
                column_headers += ('HA State',)
            router = client.find_router(parsed_args.router,
                                        ignore_missing=False)
            data = client.routers_hosting_l3_agents(router)
        else:
            if parsed_args.agent_type is not None:
                filters['agent_type'] = key_value[parsed_args.agent_type]
            if parsed_args.host is not None:
                filters['host'] = parsed_args.host

            data = client.agents(**filters)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=_formatters,
                ) for s in data))


class RemoveNetworkFromAgent(command.Command):
    _description = _("Remove network from an agent.")

    def get_parser(self, prog_name):
        parser = super(RemoveNetworkFromAgent, self).get_parser(prog_name)
        parser.add_argument(
            '--dhcp',
            action='store_true',
            help=_('Remove network from DHCP agent'))
        parser.add_argument(
            'agent_id',
            metavar='<agent-id>',
            help=_('Agent to which a network is removed (ID only)'))
        parser.add_argument(
            'network',
            metavar='<network>',
            help=_('Network to be removed from an agent (name or ID)'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        agent = client.get_agent(parsed_args.agent_id)
        network = client.find_network(
            parsed_args.network, ignore_missing=False)
        if parsed_args.dhcp:
            try:
                client.remove_dhcp_agent_from_network(agent, network)
            except Exception:
                msg = 'Failed to remove {} to {}'.format(
                    network.name, agent.agent_type)
                exceptions.CommandError(msg)


class RemoveRouterFromAgent(command.Command):
    _description = _("Remove router from an agent")

    def get_parser(self, prog_name):
        parser = super(RemoveRouterFromAgent, self).get_parser(prog_name)
        parser.add_argument(
            '--l3',
            action='store_true',
            help=_('Remove router from an L3 agent')
        )
        parser.add_argument(
            'agent_id',
            metavar='<agent-id>',
            help=_("Agent from which router will be removed (ID only)")
        )
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_("Router to be removed from an agent (name or ID)")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        agent = client.get_agent(parsed_args.agent_id)
        router = client.find_router(parsed_args.router, ignore_missing=False)
        if parsed_args.l3:
            client.remove_router_from_agent(agent, router)


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
            attrs['description'] = parsed_args.description
        if parsed_args.enable:
            attrs['is_admin_state_up'] = True
            attrs['admin_state_up'] = True
        if parsed_args.disable:
            attrs['is_admin_state_up'] = False
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
