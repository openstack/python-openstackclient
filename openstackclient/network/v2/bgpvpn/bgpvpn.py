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
#

import logging
import typing as ty

from osc_lib.cli import format_columns
from osc_lib.cli import identity as osc_id
from osc_lib.cli.parseractions import KeyValueAction
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

_attr_map = (
    ('id', 'ID', column_util.LIST_BOTH),
    ('project_id', 'Project', column_util.LIST_LONG_ONLY),
    ('name', 'Name', column_util.LIST_BOTH),
    ('type', 'Type', column_util.LIST_BOTH),
    ('route_targets', 'Route Targets', column_util.LIST_LONG_ONLY),
    ('import_targets', 'Import Targets', column_util.LIST_LONG_ONLY),
    ('export_targets', 'Export Targets', column_util.LIST_LONG_ONLY),
    (
        'route_distinguishers',
        'Route Distinguishers',
        column_util.LIST_LONG_ONLY,
    ),
    ('networks', 'Associated Networks', column_util.LIST_LONG_ONLY),
    ('routers', 'Associated Routers', column_util.LIST_LONG_ONLY),
    ('ports', 'Associated Ports', column_util.LIST_LONG_ONLY),
    ('vni', 'VNI', column_util.LIST_LONG_ONLY),
    ('local_pref', 'Local Pref', column_util.LIST_LONG_ONLY),
)
_formatters = {
    'route_targets': format_columns.ListColumn,
    'import_targets': format_columns.ListColumn,
    'export_targets': format_columns.ListColumn,
    'route_distinguishers': format_columns.ListColumn,
    'networks': format_columns.ListColumn,
    'routers': format_columns.ListColumn,
    'ports': format_columns.ListColumn,
}


def _get_columns(item):
    column_map: dict[str, str] = {}
    hidden_columns = ['location', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_common_parser(parser, update=None):
    """Adds to parser arguments common to create, set and unset commands.

    :params ArgumentParser parser: argparse object contains all command's
        arguments
    :params string update: Determines if it is a create command (value: None),
        it is a set command (value: 'set') or if it is an unset command (value:
        'unset')
    """
    ADD_RT = _("Add Route Target to import/export list")
    REMOVE_RT = _("Remove Route Target from import/export list")
    ADD_IMPORT_RT = _("Add Route Target to import list")
    DEL_IMPORT_RT = _("Remove Route Target from import list")
    ADD_EXPORT_RT = _("Add Route Target to export list")
    DEL_EXPORT_RT = _("Remove Route Target from export list")
    ADD_RD = _(
        "Add Route Distinguisher to the list of Route Distinguishers "
        "from which a Route Distinguishers will be picked from to "
        "advertise a VPN route"
    )
    REMOVE_RD = _(
        "Remove Route Distinguisher from the list of Route "
        "Distinguishers from which a Route Distinguishers will be "
        "picked from to advertise a VPN route"
    )
    REPEAT_RT = _("repeat option for multiple Route Targets")
    REPEAT_RD = _("repeat option for multiple Route Distinguishers")

    def is_appended():
        return update is None or update == 'set'

    if update is None or update == 'set':
        parser.add_argument(
            '--name',
            metavar="<name>",
            help=_("Name of the BGP VPN"),
        )
    parser.add_argument(
        '--route-target',
        dest='route_targets',
        action='append',
        metavar="<route-target>",
        help=f"{ADD_RT if is_appended() else REMOVE_RT} ({REPEAT_RT})",
    )
    if update:
        parser.add_argument(
            '--no-route-target' if update == 'set' else '--all-route-target',
            dest='purge_route_target',
            action='store_true',
            help=_('Empty route target list'),
        )
    import_target_action = ADD_IMPORT_RT if is_appended() else DEL_IMPORT_RT
    parser.add_argument(
        '--import-target',
        dest='import_targets',
        action='append',
        metavar="<import-target>",
        help=f"{import_target_action} ({REPEAT_RT})",
    )
    if update:
        parser.add_argument(
            '--no-import-target' if update == 'set' else '--all-import-target',
            dest='purge_import_target',
            action='store_true',
            help=_('Empty import route target list'),
        )
    export_target_action = ADD_EXPORT_RT if is_appended() else DEL_EXPORT_RT
    parser.add_argument(
        '--export-target',
        dest='export_targets',
        action='append',
        metavar="<export-target>",
        help=f"{export_target_action} ({REPEAT_RT})",
    )
    if update:
        parser.add_argument(
            '--no-export-target' if update == 'set' else '--all-export-target',
            dest='purge_export_target',
            action='store_true',
            help=_('Empty export route target list'),
        )
    parser.add_argument(
        '--route-distinguisher',
        dest='route_distinguishers',
        action='append',
        metavar="<route-distinguisher>",
        help=f"{ADD_RD if is_appended() else REMOVE_RD} ({REPEAT_RD})",
    )
    if update:
        parser.add_argument(
            '--no-route-distinguisher'
            if update == 'set'
            else '--all-route-distinguisher',
            dest='purge_route_distinguisher',
            action='store_true',
            help=_('Empty route distinguisher list'),
        )
    parser.add_argument(
        '--vni',
        type=int,
        help=_(
            'VXLAN Network Identifier to be used for this BGPVPN '
            'when a VXLAN encapsulation is used'
        ),
    )
    parser.add_argument(
        '--local-pref',
        type=int,
        dest='local_pref',
        help=_(
            'Default BGP LOCAL_PREF to use in route advertisements'
            'towards this BGPVPN.'
        ),
    )


def _args2body(client_manager, id, action, args):

    if not (
        args.purge_route_target
        and args.purge_import_target
        and args.purge_export_target
        and args.purge_route_distinguisher
    ) and (
        args.route_targets
        or args.import_targets
        or args.export_targets
        or args.route_distinguishers
    ):
        bgpvpn = client_manager.network.get_bgpvpn(id)

    attrs: dict[str, ty.Any] = {}

    if 'name' in args and args.name is not None:
        attrs['name'] = str(args.name)

    if 'vni' in args and args.vni is not None:
        attrs['vni'] = args.vni

    if 'local_pref' in args and args.local_pref is not None:
        attrs['local_pref'] = args.local_pref

    if args.purge_route_target:
        attrs['route_targets'] = []
    elif args.route_targets:
        if action == 'set':
            attrs['route_targets'] = list(
                set(bgpvpn['route_targets']) | set(args.route_targets)
            )
        elif action == 'unset':
            attrs['route_targets'] = list(
                set(bgpvpn['route_targets']) - set(args.route_targets)
            )

    if args.purge_import_target:
        attrs['import_targets'] = []
    elif args.import_targets:
        if action == 'set':
            attrs['import_targets'] = list(
                set(bgpvpn['import_targets']) | set(args.import_targets)
            )
        elif action == 'unset':
            attrs['import_targets'] = list(
                set(bgpvpn['import_targets']) - set(args.import_targets)
            )

    if args.purge_export_target:
        attrs['export_targets'] = []
    elif args.export_targets:
        if action == 'set':
            attrs['export_targets'] = list(
                set(bgpvpn['export_targets']) | set(args.export_targets)
            )
        elif action == 'unset':
            attrs['export_targets'] = list(
                set(bgpvpn['export_targets']) - set(args.export_targets)
            )

    if args.purge_route_distinguisher:
        attrs['route_distinguishers'] = []
    elif args.route_distinguishers:
        if action == 'set':
            attrs['route_distinguishers'] = list(
                set(bgpvpn['route_distinguishers'])
                | set(args.route_distinguishers)
            )
        elif action == 'unset':
            attrs['route_distinguishers'] = list(
                set(bgpvpn['route_distinguishers'])
                - set(args.route_distinguishers)
            )

    return attrs


class CreateBgpvpn(command.ShowOne):
    _description = _("Create BGP VPN resource")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        osc_id.add_project_owner_option_to_parser(parser)
        _get_common_parser(parser)
        parser.add_argument(
            '--type',
            default='l3',
            choices=['l2', 'l3'],
            help=_(
                "BGP VPN type selection between IP VPN (l3) and Ethernet "
                "VPN (l2) (default: l3)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = str(parsed_args.name)
        if parsed_args.type is not None:
            attrs['type'] = parsed_args.type
        if parsed_args.route_targets is not None:
            attrs['route_targets'] = parsed_args.route_targets
        if parsed_args.import_targets is not None:
            attrs['import_targets'] = parsed_args.import_targets
        if parsed_args.export_targets is not None:
            attrs['export_targets'] = parsed_args.export_targets
        if parsed_args.route_distinguishers is not None:
            attrs['route_distinguishers'] = parsed_args.route_distinguishers
        if parsed_args.vni is not None:
            attrs['vni'] = parsed_args.vni
        if parsed_args.local_pref is not None:
            attrs['local_pref'] = parsed_args.local_pref
        if 'project' in parsed_args and parsed_args.project is not None:
            project_id = osc_id.find_project(
                self.app.client_manager.sdk_connection,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id
        obj = client.create_bgpvpn(**attrs)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data


class SetBgpvpn(command.Command):
    _description = _("Set BGP VPN properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN to update (name or ID)"),
        )
        _get_common_parser(parser, update='set')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)['id']
        body = _args2body(self.app.client_manager, id, 'set', parsed_args)
        client.update_bgpvpn(id, **body)


class UnsetBgpvpn(command.Command):
    _description = _("Unset BGP VPN properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN to update (name or ID)"),
        )
        _get_common_parser(parser, update='unset')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)['id']
        body = _args2body(self.app.client_manager, id, 'unset', parsed_args)
        client.update_bgpvpn(id, **body)


class DeleteBgpvpn(command.Command):
    _description = _("Delete BGP VPN resource(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgpvpns',
            metavar="<bgpvpn>",
            nargs="+",
            help=_("BGP VPN(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fails = 0
        for id_or_name in parsed_args.bgpvpns:
            try:
                id = client.find_bgpvpn(id_or_name, ignore_missing=False)['id']
                client.delete_bgpvpn(id)
                LOG.warning("BGP VPN %(id)s deleted", {'id': id})
            except Exception as e:
                fails += 1
                LOG.error(
                    "Failed to delete BGP VPN with name or ID "
                    "'%(id_or_name)s': %(e)s",
                    {'id_or_name': id_or_name, 'e': e},
                )
        if fails > 0:
            msg = _("Failed to delete %(fails)s of %(total)s BGP VPN.") % {
                'fails': fails,
                'total': len(parsed_args.bgpvpns),
            }
            raise exceptions.CommandError(msg)


class ListBgpvpn(command.Lister):
    _description = _("List BGP VPN resources")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        osc_id.add_project_owner_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            help=_("List additional fields in output"),
        )
        parser.add_argument(
            '--property',
            metavar="<key=value>",
            default=dict(),
            help=_(
                "Filter property to apply on returned BGP VPNs (repeat to "
                "filter on multiple properties)"
            ),
            action=KeyValueAction,
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        params = {}
        if parsed_args.project is not None:
            project_id = osc_id.find_project(
                self.app.client_manager.sdk_connection,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            params['tenant_id'] = project_id
        if parsed_args.property:
            params.update(parsed_args.property)
        objs = client.bgpvpns(**params)
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


class ShowBgpvpn(command.ShowOne):
    _description = _("Show information of a given BGP VPN")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bgpvpn',
            metavar="<bgpvpn>",
            help=_("BGP VPN to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_bgpvpn(parsed_args.bgpvpn, ignore_missing=False)['id']
        obj = client.get_bgpvpn(id)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data
