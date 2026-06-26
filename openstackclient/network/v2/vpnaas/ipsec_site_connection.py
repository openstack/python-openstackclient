#    Copyright 2017 FUJITSU LIMITED
#    All Rights Reserved.
#
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

import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from openstack.network import v2 as network_v2
from osc_lib.cli import format_columns
from osc_lib.cli import identity as identity_utils
from osc_lib import exceptions
from osc_lib import utils
from osc_lib.utils import columns as column_util

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network.v2.vpnaas import utils as vpn_utils

_formatters = {'peer_cidrs': format_columns.ListColumn}

_attr_map = [
    ('id', 'ID', column_util.LIST_BOTH),
    ('name', 'Name', column_util.LIST_BOTH),
    ('peer_address', 'Peer Address', column_util.LIST_BOTH),
    ('auth_mode', 'Authentication Algorithm', column_util.LIST_BOTH),
    ('status', 'Status', column_util.LIST_BOTH),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('peer_cidrs', 'Peer CIDRs', column_util.LIST_LONG_ONLY),
    ('vpnservice_id', 'VPN Service', column_util.LIST_LONG_ONLY),
    ('ipsecpolicy_id', 'IPSec Policy', column_util.LIST_LONG_ONLY),
    ('ikepolicy_id', 'IKE Policy', column_util.LIST_LONG_ONLY),
    ('mtu', 'MTU', column_util.LIST_LONG_ONLY),
    ('initiator', 'Initiator', column_util.LIST_LONG_ONLY),
    ('is_admin_state_up', 'State', column_util.LIST_LONG_ONLY),
    ('description', 'Description', column_util.LIST_LONG_ONLY),
    ('psk', 'Pre-shared Key', column_util.LIST_LONG_ONLY),
    ('route_mode', 'Route Mode', column_util.LIST_LONG_ONLY),
    ('local_id', 'Local ID', column_util.LIST_LONG_ONLY),
    ('peer_id', 'Peer ID', column_util.LIST_LONG_ONLY),
    (
        'local_ep_group_id',
        'Local Endpoint Group ID',
        column_util.LIST_LONG_ONLY,
    ),
    ('peer_ep_group_id', 'Peer Endpoint Group ID', column_util.LIST_LONG_ONLY),
    ('dpd', 'DPD', column_util.LIST_LONG_ONLY),
]

_attr_map_dict = {
    'id': 'ID',
    'name': 'Name',
    'peer_address': 'Peer Address',
    'auth_mode': 'Authentication Algorithm',
    'status': 'Status',
    'peer_cidrs': 'Peer CIDRs',
    'vpnservice_id': 'VPN Service',
    'ipsecpolicy_id': 'IPSec Policy',
    'ikepolicy_id': 'IKE Policy',
    'mtu': 'MTU',
    'initiator': 'Initiator',
    'is_admin_state_up': 'State',
    'psk': 'Pre-shared Key',
    'route_mode': 'Route Mode',
    'local_id': 'Local ID',
    'peer_id': 'Peer ID',
    'local_ep_group_id': 'Local Endpoint Group ID',
    'peer_ep_group_id': 'Peer Endpoint Group ID',
    'description': 'Description',
    'project_id': 'Project',
    'dpd': 'DPD',
}


def _convert_to_lowercase(string: str) -> str:
    return string.lower()


def _get_common_parser(
    parser: argparse.ArgumentParser, is_create: bool = True
) -> argparse.ArgumentParser:
    parser.add_argument(
        '--description',
        metavar='<description>',
        help=_('Description for the connection'),
    )
    parser.add_argument(
        '--dpd',
        metavar="action=ACTION,interval=INTERVAL,timeout=TIMEOUT",
        type=vpn_utils.str2dict_type(
            optional_keys=['action', 'interval', 'timeout']
        ),
        help=vpn_utils.dpd_help("IPsec connection"),
    )
    parser.add_argument('--mtu', help=_('MTU size for the connection'))
    parser.add_argument(
        '--initiator',
        choices=['bi-directional', 'response-only'],
        type=_convert_to_lowercase,
        help=_('Initiator state'),
    )
    peer_group = parser.add_mutually_exclusive_group()
    peer_group.add_argument(
        '--peer-cidr',
        dest='peer_cidrs',
        help=_(
            'Remote subnet(s) in CIDR format. '
            'Cannot be specified when using endpoint groups. Only '
            'applicable, if subnet provided for VPN service.'
        ),
    )
    peer_group.add_argument(
        '--local-endpoint-group',
        help=_(
            'Local endpoint group (name or ID) with subnet(s) '
            'for IPsec connection'
        ),
    )
    parser.add_argument(
        '--peer-endpoint-group',
        help=_(
            'Peer endpoint group (name or ID) with CIDR(s) for '
            'IPSec connection'
        ),
    )
    admin_group = parser.add_mutually_exclusive_group()
    admin_group.add_argument(
        '--enable', action='store_true', help=_("Enable IPSec site connection")
    )
    admin_group.add_argument(
        '--disable',
        action='store_true',
        help=_("Disable IPSec site connection"),
    )
    parser.add_argument(
        '--local-id',
        help=_(
            'An ID to be used instead of the external IP '
            'address for a virtual router'
        ),
    )
    return parser


def _get_common_attrs(
    network_client: network_v2.Proxy, parsed_args: argparse.Namespace
) -> dict[str, Any]:
    attrs: dict[str, Any] = {}
    if parsed_args.description:
        attrs['description'] = str(parsed_args.description)
    if parsed_args.mtu:
        attrs['mtu'] = parsed_args.mtu
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if parsed_args.initiator:
        attrs['initiator'] = parsed_args.initiator
    if parsed_args.dpd:
        vpn_utils.validate_dpd_dict(parsed_args.dpd)
        attrs['dpd'] = parsed_args.dpd
    if parsed_args.local_endpoint_group:
        _local_epg = network_client.find_vpn_endpoint_group(
            parsed_args.local_endpoint_group, ignore_missing=False
        ).id
        attrs['local_ep_group_id'] = _local_epg
    if parsed_args.peer_endpoint_group:
        _peer_epg = network_client.find_vpn_endpoint_group(
            parsed_args.peer_endpoint_group, ignore_missing=False
        ).id
        attrs['peer_ep_group_id'] = _peer_epg
    if parsed_args.peer_cidrs:
        attrs['peer_cidrs'] = parsed_args.peer_cidrs
    if parsed_args.local_id:
        attrs['local_id'] = parsed_args.local_id
    return attrs


class CreateIPsecSiteConnection(command.ShowOne):
    _description = _("Create an IPsec site connection")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            '--peer-id',
            required=True,
            help=_(
                'Peer router identity for authentication. Can be '
                'IPv4/IPv6 address, e-mail address, key id, or FQDN'
            ),
        )
        parser.add_argument(
            '--peer-address',
            required=True,
            help=_('Peer gateway public IPv4/IPv6 address or FQDN'),
        )
        parser.add_argument(
            '--psk', required=True, help=_('Pre-shared key string.')
        )
        parser.add_argument(
            '--vpnservice',
            metavar='VPNSERVICE',
            required=True,
            help=_(
                'VPN service instance associated with this '
                'connection (name or ID)'
            ),
        )
        parser.add_argument(
            '--ikepolicy',
            metavar='IKEPOLICY',
            required=True,
            help=_('IKE policy associated with this connection (name or ID)'),
        )
        parser.add_argument(
            '--ipsecpolicy',
            metavar='IPSECPOLICY',
            required=True,
            help=_(
                'IPsec policy associated with this connection (name or ID)'
            ),
        )
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Set friendly name for the connection'),
        )
        identity_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        attrs = _get_common_attrs(client, parsed_args)
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['project_id'] = identity_common.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
        if parsed_args.vpnservice:
            _vpnservice_id = client.find_vpn_service(
                parsed_args.vpnservice, ignore_missing=False
            )['id']
            attrs['vpnservice_id'] = _vpnservice_id
        if parsed_args.ikepolicy:
            _ikepolicy_id = client.find_vpn_ike_policy(
                parsed_args.ikepolicy, ignore_missing=False
            )['id']
            attrs['ikepolicy_id'] = _ikepolicy_id
        if parsed_args.ipsecpolicy:
            _ipsecpolicy_id = client.find_vpn_ipsec_policy(
                parsed_args.ipsecpolicy, ignore_missing=False
            )['id']
            attrs['ipsecpolicy_id'] = _ipsecpolicy_id
        if parsed_args.peer_id:
            attrs['peer_id'] = parsed_args.peer_id
        if parsed_args.peer_address:
            attrs['peer_address'] = parsed_args.peer_address
        if parsed_args.psk:
            attrs['psk'] = parsed_args.psk
        if parsed_args.name:
            attrs['name'] = parsed_args.name
        if bool(parsed_args.local_endpoint_group) != bool(
            parsed_args.peer_endpoint_group
        ):
            message = _("You must specify both local and peer endpoint groups")
            raise exceptions.CommandError(message)
        if not parsed_args.peer_cidrs and not parsed_args.local_endpoint_group:
            message = _("You must specify endpoint groups or peer CIDR(s)")
            raise exceptions.CommandError(message)
        obj = client.create_vpn_ipsec_site_connection(**attrs)
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj,
            _attr_map_dict,
            ['location', 'tenant_id', 'action', 'timeout', 'interval'],
        )
        data = utils.get_dict_properties(obj, columns, formatters=_formatters)
        return display_columns, data


class DeleteIPsecSiteConnection(command.Command):
    _description = _("Delete IPsec site connection(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'ipsec_site_connection',
            metavar='<ipsec-site-connection>',
            nargs='+',
            help=_('IPsec site connection to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        result = 0
        for ipsec_conn in parsed_args.ipsec_site_connection:
            try:
                ipsec_con_id = client.find_vpn_ipsec_site_connection(
                    ipsec_conn, ignore_missing=False
                )['id']
                client.delete_vpn_ipsec_site_connection(ipsec_con_id)
            except Exception as e:
                result += 1
                print(
                    f"Failed to delete IPsec site connection with "
                    f"name or ID {ipsec_conn}: {e}"
                )

        if result > 0:
            total = len(parsed_args.ipsec_site_connection)
            msg = _(
                "%(result)s of %(total)s IPsec site connection failed "
                "to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListIPsecSiteConnection(command.Lister):
    _description = _(
        "List IPsec site connections that belong to a given project"
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        client = self.app.client_manager.network
        obj = client.vpn_ipsec_site_connections()
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=parsed_args.long
        )
        return (
            headers,
            (
                utils.get_dict_properties(s, columns, formatters=_formatters)
                for s in obj
            ),
        )


class SetIPsecSiteConnection(command.Command):
    _description = _("Set IPsec site connection properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        _get_common_parser(parser)
        parser.add_argument(
            '--peer-id',
            help=_(
                'Peer router identity for authentication. Can be '
                'IPv4/IPv6 address, e-mail address, key id, or FQDN'
            ),
        )
        parser.add_argument(
            '--peer-address',
            help=_('Peer gateway public IPv4/IPv6 address or FQDN'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set friendly name for the connection'),
        )
        parser.add_argument(
            'ipsec_site_connection',
            metavar='<ipsec-site-connection>',
            help=_('IPsec site connection to set (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        attrs = _get_common_attrs(client, parsed_args)
        if parsed_args.peer_id:
            attrs['peer_id'] = parsed_args.peer_id
        if parsed_args.peer_address:
            attrs['peer_address'] = parsed_args.peer_address
        if parsed_args.name:
            attrs['name'] = parsed_args.name
        ipsec_conn_id = client.find_vpn_ipsec_site_connection(
            parsed_args.ipsec_site_connection, ignore_missing=False
        )['id']
        try:
            client.update_vpn_ipsec_site_connection(ipsec_conn_id, **attrs)
        except Exception as e:
            msg = _(
                "Failed to set IPsec site connection '%(ipsec_conn)s': %(e)s"
            ) % {'ipsec_conn': parsed_args.ipsec_site_connection, 'e': e}
            raise exceptions.CommandError(msg)


class ShowIPsecSiteConnection(command.ShowOne):
    _description = _("Show information of a given IPsec site connection")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'ipsec_site_connection',
            metavar='<ipsec-site-connection>',
            help=_('IPsec site connection to display (name or ID)'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        obj = client.find_vpn_ipsec_site_connection(
            parsed_args.ipsec_site_connection, ignore_missing=False
        )
        display_columns, columns = utils.get_osc_show_columns_for_sdk_resource(
            obj,
            _attr_map_dict,
            ['location', 'tenant_id', 'action', 'timeout', 'interval'],
        )
        data = utils.get_dict_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)
