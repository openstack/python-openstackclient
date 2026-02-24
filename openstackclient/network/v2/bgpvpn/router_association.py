# Copyright (c) 2016 Juniper networks Inc.
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
#

import logging

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
    ('tenant_id', 'Project', column_util.LIST_LONG_ONLY),
    ('router_id', 'Router ID', column_util.LIST_BOTH),
    (
        'advertise_extra_routes',
        'Advertise extra routes',
        column_util.LIST_LONG_ONLY,
    ),
)
_formatters: dict[str, osc_utils.FormatterT] = {}


def _get_columns(item):
    column_map: dict[str, str] = {}
    hidden_columns = ['location', 'name', 'project_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_common_parser(parser, action):
    """Adds to parser arguments common to create, set and unset commands.

    :params ArgumentParser parser: argparse object contains all command's
                                    arguments
    :params string action: 'create', 'set' or 'unset'
    """
    ADVERTISE_ROUTES = _("Routes will be advertised to the BGP VPN%s") % (
        _(' (default)') if action == 'create' else ""
    )
    NOT_ADVERTISE_ROUTES = _(
        "Routes from the router will not be advertised to the BGP VPN"
    )

    group_advertise_extra_routes = parser.add_mutually_exclusive_group()
    group_advertise_extra_routes.add_argument(
        '--advertise_extra_routes',
        action='store_true',
        help=NOT_ADVERTISE_ROUTES if action == 'unset' else ADVERTISE_ROUTES,
    )
    group_advertise_extra_routes.add_argument(
        '--no-advertise_extra_routes',
        action='store_true',
        help=ADVERTISE_ROUTES if action == 'unset' else NOT_ADVERTISE_ROUTES,
    )


def _args2body(action, args):
    attrs = {'advertise_extra_routes': False}
    if args.advertise_extra_routes:
        attrs['advertise_extra_routes'] = action != 'unset'
    elif args.no_advertise_extra_routes:
        attrs['advertise_extra_routes'] = action == 'unset'
    return attrs


class CreateBgpvpnRouterAssoc(command.ShowOne):
    _description = _("Create a BGP VPN router association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        osc_id.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN to apply the router association (name or ID)"),
        )
        parser.add_argument(
            'resource',
            metavar="<router>",
            help=_("Router to associate the BGP VPN (name or ID)"),
        )
        _get_common_parser(parser, 'create')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        router = client.find_router(parsed_args.resource, ignore_missing=False)
        body = {'router_id': router['id']}
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = osc_id.find_project(
                self.app.client_manager.sdk_connection,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            body['tenant_id'] = project_id

        body.update(_args2body('create', parsed_args))

        obj = client.create_bgpvpn_router_association(bgpvpn['id'], **body)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data


class SetBgpvpnRouterAssoc(command.Command):
    _description = _("Set BGP VPN router association properties")
    _action = 'set'

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource_association_id',
            metavar="<router association ID>",
            help=_("Router association ID to update"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the router association belongs to (name or ID)"),
        )
        _get_common_parser(parser, self._action)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        body = _args2body(self._action, parsed_args)
        client.update_bgpvpn_router_association(
            bgpvpn['id'], parsed_args.resource_association_id, **body
        )


class UnsetBgpvpnRouterAssoc(SetBgpvpnRouterAssoc):
    _description = _("Unset BGP VPN router association properties")
    _action = 'unset'


class DeleteBgpvpnRouterAssoc(command.Command):
    _description = _(
        "Delete a BGP VPN router association(s) for a given BGP VPN"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource_association_ids',
            metavar="<router association ID>",
            nargs="+",
            help=_("Router association ID(s) to remove"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the router association belongs to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        fails = 0
        for id in parsed_args.resource_association_ids:
            try:
                client.delete_bgpvpn_router_association(bgpvpn['id'], id)
                LOG.warning(
                    "Router association %(id)s deleted",
                    {'id': id},
                )
            except Exception as e:
                fails += 1
                LOG.error(
                    "Failed to delete router "
                    "association with ID '%(id)s': %(e)s",
                    {'id': id, 'e': e},
                )
        if fails > 0:
            msg = _(
                "Failed to delete %(fails)s of %(total)s "
                "router BGP VPN association(s)."
            ) % {
                'fails': fails,
                'total': len(parsed_args.resource_association_ids),
            }
            raise exceptions.CommandError(msg)


class ListBgpvpnRouterAssoc(command.Lister):
    _description = _("List BGP VPN router associations for a given BGP VPN")

    def get_parser(self, prog_name):
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

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        params = {}
        if parsed_args.property:
            params.update(parsed_args.property)
        objs = client.bgpvpn_router_associations(
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


class ShowBgpvpnRouterAssoc(command.ShowOne):
    _description = _("Show information of a given BGP VPN router association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'resource_association_id',
            metavar="<router association ID>",
            help=_("Router association ID to look up"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the association belongs to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        obj = client.get_bgpvpn_router_association(
            bgpvpn['id'], parsed_args.resource_association_id
        )
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data
