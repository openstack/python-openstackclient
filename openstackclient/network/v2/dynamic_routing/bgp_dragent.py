#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


class AddBgpSpeakerToDRAgent(command.Command):
    """Add a BGP speaker to a dynamic routing agent"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'dragent_id',
            metavar='<agent-id>',
            help=_("ID of the dynamic routing agent"),
        )
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("ID or name of the BGP speaker"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        ).id
        client.add_bgp_speaker_to_dragent(parsed_args.dragent_id, speaker_id)


class RemoveBgpSpeakerFromDRAgent(command.Command):
    """Removes a BGP speaker from a dynamic routing agent"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'dragent_id',
            metavar='<agent-id>',
            help=_("ID of the dynamic routing agent"),
        )
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("ID or name of the BGP speaker"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        ).id
        client.remove_bgp_speaker_from_dragent(
            parsed_args.dragent_id, speaker_id
        )


class ListDRAgent(command.Lister):
    """List dynamic routing agents"""

    resource = 'agent'
    list_columns = ['id', 'host', 'admin_state_up', 'alive']
    unknown_parts_flag = False

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--bgp-speaker',
            metavar='<bgp-speaker>',
            help=_(
                "List dynamic routing agents hosting a "
                "BGP speaker (name or ID)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        if parsed_args.bgp_speaker is not None:
            speaker_id = client.find_bgp_speaker(
                parsed_args.bgp_speaker, ignore_missing=False
            ).id
            data = client.get_bgp_dragents_hosting_speaker(speaker_id)
        else:
            data = client.agents(agent_type='BGP dynamic routing agent')
        columns = (
            'id',
            'agent_type',
            'host',
            'availability_zone',
            'is_alive',
            'is_admin_state_up',
            'binary',
        )
        column_headers = (
            'ID',
            'Agent Type',
            'Host',
            'Availability Zone',
            'Alive',
            'State',
            'Binary',
        )
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )
