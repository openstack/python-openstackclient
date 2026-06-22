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


import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from osc_lib.cli import identity as identity_utils
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network.v2.dynamic_routing import bgp_peer


def _get_attrs(
    client_manager: Any, parsed_args: argparse.Namespace
) -> dict[str, Any]:
    attrs: dict[str, Any] = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if 'local_as' in parsed_args:
        attrs['local_as'] = parsed_args.local_as
    if 'ip_version' in parsed_args:
        attrs['ip_version'] = parsed_args.ip_version
    if parsed_args.advertise_tenant_networks:
        attrs['advertise_tenant_networks'] = True
    if parsed_args.no_advertise_tenant_networks:
        attrs['advertise_tenant_networks'] = False
    if parsed_args.advertise_floating_ip_host_routes:
        attrs['advertise_floating_ip_host_routes'] = True
    if parsed_args.no_advertise_floating_ip_host_routes:
        attrs['advertise_floating_ip_host_routes'] = False

    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id
    return attrs


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--advertise-floating-ip-host-routes',
        action='store_true',
        help=_(
            "Enable the advertisement of floating IP host routes "
            "by the BGP speaker. (default)"
        ),
    )
    parser.add_argument(
        '--no-advertise-floating-ip-host-routes',
        action='store_true',
        help=_(
            "Disable the advertisement of floating IP host routes "
            "by the BGP speaker."
        ),
    )
    parser.add_argument(
        '--advertise-tenant-networks',
        action='store_true',
        help=_(
            "Enable the advertisement of tenant network routes "
            "by the BGP speaker. (default)"
        ),
    )
    parser.add_argument(
        '--no-advertise-tenant-networks',
        action='store_true',
        help=_(
            "Disable the advertisement of tenant network routes "
            "by the BGP speaker."
        ),
    )


class AddNetworkToSpeaker(command.Command):
    _description = _("Add a network to a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("BGP speaker (name or ID)"),
        )
        parser.add_argument(
            'network',
            metavar='<network>',
            help=_("Network to add (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        ).id
        net_id = client.find_network(
            parsed_args.network, ignore_missing=False
        ).id
        client.add_gateway_network_to_speaker(speaker_id, net_id)


class AddPeerToSpeaker(command.Command):
    _description = _("Add a peer to a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("BGP speaker (name or ID)"),
        )
        parser.add_argument(
            'bgp_peer',
            metavar='<bgp-peer>',
            help=_("BGP Peer to add (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        )['id']
        peer_id = client.find_bgp_peer(
            parsed_args.bgp_peer, ignore_missing=False
        )['id']
        client.add_bgp_peer_to_speaker(speaker_id, peer_id)


class CreateBgpSpeaker(command.ShowOne):
    _description = _("Create a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("Name of the BGP speaker to create"),
        )
        parser.add_argument(
            '--local-as',
            metavar='<local-as>',
            required=True,
            help=_(
                "Local AS number. (Integer in [%(min_val)s, %(max_val)s] "
                "is allowed.)"
            )
            % {
                'min_val': bgp_peer.MIN_AS_NUM,
                'max_val': bgp_peer.MAX_AS_NUM,
            },
        )
        parser.add_argument(
            '--ip-version',
            type=int,
            choices=[4, 6],
            default=4,
            help=_("IP version for the BGP speaker (default is 4)"),
        )
        add_common_arguments(parser)
        identity_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_bgp_speaker(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, {}, ['location', 'tenant_id']
        )
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteBgpSpeaker(command.Command):
    _description = _("Delete a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar="<bgp-speaker>",
            help=_("BGP speaker to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        ).id
        client.delete_bgp_speaker(id)


class ListBgpSpeaker(command.Lister):
    _description = _("List BGP speakers")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--agent',
            metavar='<agent-id>',
            help=_("List BGP speakers hosted by an agent (ID only)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        data: Iterable[Any]
        if parsed_args.agent is not None:
            data = client.get_bgp_speakers_hosted_by_dragent(parsed_args.agent)
        else:
            data = client.bgp_speakers(retrieve_all=True)

        headers = ('ID', 'Name', 'Local AS', 'IP Version')
        columns = ('id', 'name', 'local_as', 'ip_version')
        return (headers, (utils.get_dict_properties(s, columns) for s in data))


class ListRoutesAdvertisedBySpeaker(command.Lister):
    _description = _("List routes advertised")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("BGP speaker (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        )['id']
        data = client.get_advertised_routes_of_speaker(speaker_id)
        headers = ('Destination', 'Nexthop')
        columns = ('destination', 'next_hop')
        return (
            headers,
            (
                utils.get_dict_properties(s, columns)
                for s in data['advertised_routes']
            ),
        )


class RemoveNetworkFromSpeaker(command.Command):
    _description = _("Remove a network from a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("BGP speaker (name or ID)"),
        )
        parser.add_argument(
            'network',
            metavar='<network>',
            help=_("Network to remove (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        )['id']
        net_id = client.find_network(
            parsed_args.network, ignore_missing=False
        )['id']
        client.remove_gateway_network_from_speaker(speaker_id, net_id)


class RemovePeerFromSpeaker(command.Command):
    _description = _("Remove a peer from a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar='<bgp-speaker>',
            help=_("BGP speaker (name or ID)"),
        )
        parser.add_argument(
            'bgp_peer',
            metavar='<bgp-peer>',
            help=_("BGP Peer to remove (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        speaker_id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        )['id']
        peer_id = client.find_bgp_peer(
            parsed_args.bgp_peer, ignore_missing=False
        )['id']
        client.remove_bgp_peer_from_speaker(speaker_id, peer_id)


class SetBgpSpeaker(command.Command):
    _description = _("Set BGP speaker properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar="<bgp-speaker>",
            help=_("BGP speaker to update (name or ID)"),
        )
        parser.add_argument('--name', help=_("New name for the BGP speaker"))
        add_common_arguments(parser)
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        id = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        ).id
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        client.update_bgp_speaker(id, **attrs)


class ShowBgpSpeaker(command.ShowOne):
    _description = _("Show a BGP speaker")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgp_speaker',
            metavar="<bgp-speaker>",
            help=_("BGP speaker to display (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        obj = client.find_bgp_speaker(
            parsed_args.bgp_speaker, ignore_missing=False
        )
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj, {}, ['location', 'tenant_id']
        )
        data = utils.get_dict_properties(obj, columns)
        return display_columns, data
