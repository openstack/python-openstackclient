# Copyright (c) 2016 Juniper Networks Inc.
# All Rights Reserved.
#
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

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.network.v2 import (
    bgpvpn_network_association as _bgpvpn_network_association,
)
from osc_lib.cli import identity as osc_id
from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient import command
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('network_id', 'Network ID', column_util.LIST_BOTH),
)
_formatters: dict[str, Any] = {}


def _get_columns(
    item: _bgpvpn_network_association.BgpVpnNetworkAssociation,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    column_map: dict[str, str] = {}
    hidden_columns = ['location', 'name', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class CreateBgpvpnNetAssoc(command.ShowOne):
    _description = _("Create a BGP VPN network association")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        osc_id.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN to apply the network association (name or ID)"),
        )
        parser.add_argument(
            'resource',
            metavar="<network>",
            help=_("Network to associate the BGP VPN (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        network = client.find_network(
            parsed_args.resource, ignore_missing=False
        )
        body: dict[str, Any] = {'network_id': network['id']}
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = osc_id.find_project(
                self.app.client_manager.sdk_connection,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            body['project_id'] = project_id

        obj = client.create_bgpvpn_network_association(bgpvpn['id'], **body)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data


class DeleteBgpvpnNetAssoc(command.Command):
    _description = _(
        "Delete a BGP VPN network association(s) for a given BGP VPN"
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource_association_ids',
            metavar="<network association ID>",
            nargs="+",
            help=_("Network association ID(s) to remove"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the network association belongs to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        fails = 0
        for id in parsed_args.resource_association_ids:
            try:
                client.delete_bgpvpn_network_association(bgpvpn['id'], id)
                LOG.warning(
                    "Network association %(id)s deleted",
                    {'id': id},
                )
            except Exception as e:
                fails += 1
                LOG.error(
                    "Failed to delete network "
                    "association with ID '%(id)s': %(e)s",
                    {'id': id, 'e': e},
                )
        if fails > 0:
            msg = _(
                "Failed to delete %(fails)s of %(total)s "
                "network BGP VPN association(s)."
            ) % {
                'fails': fails,
                'total': len(parsed_args.resource_association_ids),
            }
            raise exceptions.CommandError(msg)


class ListBgpvpnNetAssoc(command.Lister):
    _description = _("List BGP VPN network associations for a given BGP VPN")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN listed associations belong to (name or ID)"),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output"),
        )
        parser.add_argument(
            '--property',
            metavar="<key=value>",
            help=_(
                "Filter property to apply on returned BGP VPNs (repeat to "
                "filter on multiple properties)"
            ),
            action=parseractions.KeyValueAction,
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        params = {}
        if parsed_args.property:
            params.update(parsed_args.property)
        objs = client.bgpvpn_network_associations(
            bgpvpn['id'], retrieve_all=True, **params
        )
        headers, columns = column_util.get_column_definitions(
            list(_attr_map), long_listing=parsed_args.long
        )
        return (
            headers,
            (
                osc_utils.get_dict_properties(
                    s, columns, formatters=_formatters
                )
                for s in objs
            ),
        )


class ShowBgpvpnNetAssoc(command.ShowOne):
    _description = _("Show information of a given BGP VPN network association")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource_association_id',
            metavar="<network association ID>",
            help=_("Network association ID to look up"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the association belongs to (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        obj = client.get_bgpvpn_network_association(
            bgpvpn['id'], parsed_args.resource_association_id
        )
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data
