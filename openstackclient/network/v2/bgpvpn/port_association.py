# Copyright (c) 2017 Juniper networks Inc.
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
import typing as ty

from osc_lib.cli import format_columns
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
    ('port_id', 'Port ID', column_util.LIST_BOTH),
    (
        'prefix_routes',
        'Prefix Routes (BGP LOCAL_PREF)',
        column_util.LIST_LONG_ONLY,
    ),
    (
        'bgpvpn_routes',
        'BGP VPN Routes (BGP LOCAL_PREF)',
        column_util.LIST_LONG_ONLY,
    ),
    (
        'advertise_fixed_ips',
        "Advertise Port's Fixed IPs",
        column_util.LIST_LONG_ONLY,
    ),
)
_formatters = {
    'prefix_routes': format_columns.ListColumn,
    'bgpvpn_routes': format_columns.ListColumn,
}


def _get_columns(item):
    column_map: dict[str, str] = {}
    hidden_columns = ['location', 'name', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _transform_resource(data):
    """Transforms BGP VPN port association routes property.

    Separates the two route types and formats them with ListColumn.

    {'routes':
        [
            {'type': 'prefix', 'local_pref': 100, 'prefix': '8.8.8.0/27'},
            {'type': 'bgpvpn', 'local_pref': 50,
             'bgpvpn': '157d72a9-9968-48e7-8087-6c9a9bc7a181'},
        ],
    }

    to

    {
        'prefix_routes': ['8.8.8.0/27 (100)'],
        'bgpvpn_routes': ['157d72a9-9968-48e7-8087-6c9a9bc7a181 (50)'],
    }
    """
    for route in data.get('routes', []):
        local_pref = ''
        if route.get('local_pref'):
            local_pref = ' ({local_pref})'
        if route['type'] == 'prefix':
            data.setdefault('prefix_routes', []).append(
                '{}{}'.format(route['prefix'], local_pref)
            )
        elif route['type'] == 'bgpvpn':
            data.setdefault('bgpvpn_routes', []).append(
                '{}{}'.format(route['bgpvpn_id'], local_pref)
            )
        else:
            LOG.warning("Unknown route type %s (%s).", route['type'], route)
    data.pop('routes', None)
    return data


def _get_common_parser(parser, action):
    """Adds to parser arguments common to create, set and unset commands.

    :params ArgumentParser parser: argparse object contains all command's
                                    arguments
    :params string action: 'create', 'set' or 'unset'
    """
    ADVERTISE_ROUTE = _(
        "Fixed IPs of the port will be advertised to the BGP VPN%s"
    ) % (_(' (default)') if action == 'create' else "")
    NOT_ADVERTISE_ROUTE = _(
        "Fixed IPs of the port will not be advertised to the BGP VPN"
    )

    LOCAL_PREF_VALUE = _(
        ". Optionally, can control the value of the BGP "
        "LOCAL_PREF of the routes that will be "
        "advertised"
    )

    ADD_PREFIX_ROUTE = (
        _("Add prefix route in CIDR notation%s") % LOCAL_PREF_VALUE
    )
    REMOVE_PREFIX_ROUTE = _("Remove prefix route in CIDR notation")
    REPEAT_PREFIX_ROUTE = _("repeat option for multiple prefix routes")

    ADD_BGVPVPN_ROUTE = (
        _("Add BGP VPN route for route leaking%s") % LOCAL_PREF_VALUE
    )
    REMOVE_BGPVPN_ROUTE = _("Remove BGP VPN route")
    REPEAT_BGPVPN_ROUTE = _("repeat option for multiple BGP VPN routes")

    group_advertise_fixed_ips = parser.add_mutually_exclusive_group()
    group_advertise_fixed_ips.add_argument(
        '--advertise-fixed-ips',
        action='store_true',
        help=NOT_ADVERTISE_ROUTE if action == 'unset' else ADVERTISE_ROUTE,
    )
    group_advertise_fixed_ips.add_argument(
        '--no-advertise-fixed-ips',
        action='store_true',
        help=ADVERTISE_ROUTE if action == 'unset' else NOT_ADVERTISE_ROUTE,
    )

    if action in ['create', 'set']:
        parser.add_argument(
            '--prefix-route',
            metavar="prefix=<cidr>[,local_pref=<integer>]",
            dest='prefix_routes',
            action=parseractions.MultiKeyValueAction,
            required_keys=['prefix'],
            optional_keys=['local_pref'],
            help=f"{ADD_PREFIX_ROUTE} ({REPEAT_PREFIX_ROUTE})",
        )
        parser.add_argument(
            '--bgpvpn-route',
            metavar="bgpvpn=<BGP VPN ID or name>[,local_pref=<integer>]",
            dest='bgpvpn_routes',
            action=parseractions.MultiKeyValueAction,
            required_keys=['bgpvpn'],
            optional_keys=['local_pref'],
            help=f"{ADD_BGVPVPN_ROUTE} ({REPEAT_BGPVPN_ROUTE})",
        )
    else:
        parser.add_argument(
            '--prefix-route',
            metavar="<cidr>",
            dest='prefix_routes',
            action='append',
            help=f"{REMOVE_PREFIX_ROUTE} ({REPEAT_PREFIX_ROUTE})",
        )
        parser.add_argument(
            '--bgpvpn-route',
            metavar="<BGP VPN ID or name>",
            dest='bgpvpn_routes',
            action='append',
            help=f"{REMOVE_BGPVPN_ROUTE} ({REPEAT_BGPVPN_ROUTE})",
        )
    if action != 'create':
        parser.add_argument(
            '--no-prefix-route' if action == 'set' else '--all-prefix-routes',
            dest='purge_prefix_route',
            action='store_true',
            help=_('Empty prefix route list'),
        )
        parser.add_argument(
            '--no-bgpvpn-route' if action == 'set' else '--all-bgpvpn-routes',
            dest='purge_bgpvpn_route',
            action='store_true',
            help=_('Empty BGP VPN route list'),
        )


def _args2body(client, action, bgpvpn_id, args):
    attrs: dict[str, ty.Any] = {}

    if action != 'create':
        assoc = client.find_bgpvpn_port_association(
            args.port_association_id,
            bgpvpn_id=bgpvpn_id,
            ignore_missing=False,
        )
    else:
        assoc = {'routes': []}

    if args.advertise_fixed_ips:
        attrs['advertise_fixed_ips'] = action != 'unset'
    elif args.no_advertise_fixed_ips:
        attrs['advertise_fixed_ips'] = action == 'unset'

    prefix_routes: dict[str, ty.Any] | None = None
    if 'purge_prefix_route' in args and args.purge_prefix_route:
        prefix_routes = {}
    else:
        prefix_routes = {
            r['prefix']: r.get('local_pref')
            for r in assoc['routes']
            if r['type'] == 'prefix'
        }
        if args.prefix_routes:
            if action in ['create', 'set']:
                prefix_routes.update(
                    {
                        r['prefix']: r.get('local_pref')
                        for r in args.prefix_routes
                    }
                )
            elif action == 'unset':
                for prefix in args.prefix_routes:
                    prefix_routes.pop(prefix, None)

    bgpvpn_routes: dict[str, ty.Any] | None = None
    if 'purge_bgpvpn_route' in args and args.purge_bgpvpn_route:
        bgpvpn_routes = {}
    else:
        bgpvpn_routes = {
            r['bgpvpn_id']: r.get('local_pref')
            for r in assoc['routes']
            if r['type'] == 'bgpvpn'
        }
        if args.bgpvpn_routes:
            if action == 'unset':
                routes = [{'bgpvpn': bgpvpn} for bgpvpn in args.bgpvpn_routes]
            else:
                routes = args.bgpvpn_routes
            args_bgpvpn_routes = {
                client.find_bgpvpn(
                    r['bgpvpn'], ignore_missing=False
                ).id: r.get('local_pref')
                for r in routes
            }
            if action in ['create', 'set']:
                bgpvpn_routes.update(args_bgpvpn_routes)
            elif action == 'unset':
                for bgpvpn_id in args_bgpvpn_routes:
                    bgpvpn_routes.pop(bgpvpn_id, None)

    if prefix_routes is not None and not prefix_routes:
        attrs.setdefault('routes', [])
    elif prefix_routes is not None:
        for prefix, local_pref in prefix_routes.items():
            route: dict[str, ty.Any] = {
                'type': 'prefix',
                'prefix': prefix,
            }
            if local_pref:
                route['local_pref'] = int(local_pref)
            attrs.setdefault('routes', []).append(route)
    if bgpvpn_routes is not None and not bgpvpn_routes:
        attrs.setdefault('routes', [])
    elif bgpvpn_routes is not None:
        for bgpvpn_id, local_pref in bgpvpn_routes.items():
            route = {
                'type': 'bgpvpn',
                'bgpvpn_id': bgpvpn_id,
            }
            if local_pref:
                route['local_pref'] = int(local_pref)
            attrs.setdefault('routes', []).append(route)

    return attrs


class CreateBgpvpnPortAssoc(command.ShowOne):
    _description = _("Create a BGP VPN port association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        osc_id.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN to apply the port association (name or ID)"),
        )
        parser.add_argument(
            'port',
            metavar="<port>",
            help=_("Port to associate the BGP VPN (name or ID)"),
        )
        _get_common_parser(parser, 'create')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        port = client.find_port(parsed_args.port, ignore_missing=False)
        body: dict[str, ty.Any] = {'port_id': port['id']}
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = osc_id.find_project(
                self.app.client_manager.sdk_connection,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            body['project_id'] = project_id

        body.update(_args2body(client, 'create', bgpvpn['id'], parsed_args))

        obj = client.create_bgpvpn_port_association(bgpvpn['id'], **body)
        _transform_resource(obj)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data


class SetBgpvpnPortAssoc(command.Command):
    _description = _("Set BGP VPN port association properties")
    _action = 'set'

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'port_association_id',
            metavar="<port association ID>",
            help=_("Port association ID to update"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the port association belongs to (name or ID)"),
        )
        _get_common_parser(parser, self._action)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        body = _args2body(client, self._action, bgpvpn['id'], parsed_args)
        client.update_bgpvpn_port_association(
            bgpvpn['id'], parsed_args.port_association_id, **body
        )


class UnsetBgpvpnPortAssoc(SetBgpvpnPortAssoc):
    _description = _("Unset BGP VPN port association properties")
    _action = 'unset'


class DeleteBgpvpnPortAssoc(command.Command):
    _description = _(
        "Delete a BGP VPN port association(s) for a given BGP VPN"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'port_association_ids',
            metavar="<port association ID>",
            nargs="+",
            help=_("Port association ID(s) to remove"),
        )
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN the port association belongs to (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        bgpvpn = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)
        fails = 0
        for id in parsed_args.port_association_ids:
            try:
                client.delete_bgpvpn_port_association(bgpvpn['id'], id)
                LOG.warning(
                    "Port association %(id)s deleted",
                    {'id': id},
                )
            except Exception as e:
                fails += 1
                LOG.error(
                    "Failed to delete port "
                    "association with ID '%(id)s': %(e)s",
                    {'id': id, 'e': e},
                )
        if fails > 0:
            msg = _(
                "Failed to delete %(fails)s of %(total)s "
                "port BGP VPN association(s)."
            ) % {
                'fails': fails,
                'total': len(parsed_args.port_association_ids),
            }
            raise exceptions.CommandError(msg)


class ListBgpvpnPortAssoc(command.Lister):
    _description = _("List BGP VPN port associations for a given BGP VPN")

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
        objs = client.bgpvpn_port_associations(
            bgpvpn['id'], retrieve_all=True, **params
        )
        transformed_objs = [_transform_resource(obj) for obj in objs]
        headers, columns = column_util.get_column_definitions(
            list(_attr_map), long_listing=parsed_args.long
        )
        return (
            headers,
            (
                osc_utils.get_dict_properties(
                    s, columns, formatters=_formatters
                )
                for s in transformed_objs
            ),
        )


class ShowBgpvpnPortAssoc(command.ShowOne):
    _description = _("Show information of a given BGP VPN port association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'port_association_id',
            metavar="<port association ID>",
            help=_("Port association ID to look up"),
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
        obj = client.get_bgpvpn_port_association(
            bgpvpn['id'], parsed_args.port_association_id
        )
        _transform_resource(obj)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data
