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

import logging

from osc_lib.cli import identity as identity_utils
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common
from openstackclient.network.v2 import port as osc_port
from openstackclient.network.v2.taas import tap_service

LOG = logging.getLogger(__name__)

TAP_MIRROR = 'tap_mirror'
TAP_MIRRORS = f'{TAP_MIRROR}s'

_attr_map = [
    ('id', 'ID', column_util.LIST_BOTH),
    ('tenant_id', 'Tenant', column_util.LIST_LONG_ONLY),
    ('name', 'Name', column_util.LIST_BOTH),
    ('port_id', 'Port', column_util.LIST_BOTH),
    ('directions', 'Directions', column_util.LIST_LONG_ONLY),
    ('remote_ip', 'Remote IP', column_util.LIST_BOTH),
    ('mirror_type', 'Mirror Type', column_util.LIST_LONG_ONLY),
]


def _get_columns(item):
    column_map: dict[str, str] = {}
    hidden_columns = ['location', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class CreateTapMirror(command.ShowOne):
    _description = _("Create a new tap mirror.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        identity_utils.add_project_owner_option_to_parser(parser)
        tap_service._add_updatable_args(parser)
        parser.add_argument(
            '--port',
            dest='port_id',
            required=True,
            metavar="PORT",
            help=_('Port (name or ID) to which the Tap Mirror is connected.'),
        )
        parser.add_argument(
            '--directions',
            dest='directions',
            action=osc_port.JSONKeyValueAction,
            required=True,
            help=_(
                'Dictionary of direction and tunnel_id. Valid directions are: '
                'IN and OUT.'
            ),
        )
        parser.add_argument(
            '--remote-ip',
            dest='remote_ip',
            required=True,
            help=_(
                'Remote IP address for the tap mirror (remote end of the '
                'GRE or ERSPAN v1 tunnel).'
            ),
        )
        parser.add_argument(
            '--mirror-type',
            dest='mirror_type',
            required=True,
            help=_('Mirror type. Valid values are: gre and erspanv1.'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.port_id is not None:
            port_id = client.find_port(
                parsed_args.port_id, ignore_missing=False
            ).id
            attrs['port_id'] = port_id
        if parsed_args.directions is not None:
            attrs['directions'] = parsed_args.directions
        if parsed_args.remote_ip is not None:
            attrs['remote_ip'] = parsed_args.remote_ip
        if parsed_args.mirror_type is not None:
            attrs['mirror_type'] = parsed_args.mirror_type
        if 'project' in parsed_args and parsed_args.project is not None:
            attrs['project_id'] = common.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
        obj = client.create_tap_mirror(**attrs)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class ListTapMirror(command.Lister):
    _description = _("List tap mirrors.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        identity_utils.add_project_owner_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        params = {}
        if parsed_args.project is not None:
            params['project_id'] = common.find_project(
                self.app.client_manager.identity,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
        objs = client.tap_mirrors(retrieve_all=True, params=params)
        headers, columns = column_util.get_column_definitions(
            _attr_map, long_listing=True
        )
        return (
            headers,
            (osc_utils.get_dict_properties(s, columns) for s in objs),
        )


class ShowTapMirror(command.ShowOne):
    _description = _("Show tap mirror details.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_MIRROR,
            metavar=f"<{TAP_MIRROR}>",
            help=_("Tap mirror to display (name or ID)."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        id = client.find_tap_mirror(
            parsed_args.tap_mirror, ignore_missing=False
        ).id
        obj = client.get_tap_mirror(id)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data


class DeleteTapMirror(command.Command):
    _description = _("Delete a tap mirror.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_MIRROR,
            metavar=f"<{TAP_MIRROR}>",
            nargs="+",
            help=_("Tap mirror to delete (name or ID)."),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        fails = 0
        for id_or_name in parsed_args.tap_mirror:
            try:
                id = client.find_tap_mirror(
                    id_or_name, ignore_missing=False
                ).id

                client.delete_tap_mirror(id)
                LOG.warning("Tap Mirror %(id)s deleted", {'id': id})
            except Exception as e:
                fails += 1
                LOG.error(
                    "Failed to delete Tap Mirror with name or ID "
                    "'%(id_or_name)s': %(e)s",
                    {'id_or_name': id_or_name, 'e': e},
                )
        if fails > 0:
            msg = _("Failed to delete %(fails)s of %(total)s Tap Mirror.") % {
                'fails': fails,
                'total': len(parsed_args.tap_mirror),
            }
            raise exceptions.CommandError(msg)


class UpdateTapMirror(command.ShowOne):
    _description = _("Update a tap mirror.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            TAP_MIRROR,
            metavar=f"<{TAP_MIRROR}>",
            help=_("Tap mirror to modify (name or ID)."),
        )
        tap_service._add_updatable_args(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        original_t_s = client.find_tap_mirror(
            parsed_args.tap_mirror, ignore_missing=False
        ).id
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        obj = client.update_tap_mirror(original_t_s, **attrs)
        display_columns, columns = tap_service._get_columns(obj)
        data = osc_utils.get_dict_properties(obj, columns)
        return display_columns, data
