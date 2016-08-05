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


LOG = logging.getLogger(__name__)


def _format_admin_state(state):
    return 'UP' if state else 'DOWN'


_formatters = {
    'admin_state_up': _format_admin_state,
    'configurations': utils.format_dict,
}


class DeleteNetworkAgent(command.Command):
    """Delete network agent(s)"""

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


class ListNetworkAgent(command.Lister):
    """List network agents"""

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'agent_type',
            'host',
            'availability_zone',
            'alive',
            'admin_state_up',
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
        data = client.agents()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters=_formatters,
                ) for s in data))


class ShowNetworkAgent(command.ShowOne):
    """Display network agent details"""

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
        obj = client.get_agent(parsed_args.network_agent, ignore_missing=False)
        columns = tuple(sorted(list(obj.keys())))
        data = utils.get_item_properties(obj, columns, formatters=_formatters,)
        return columns, data
