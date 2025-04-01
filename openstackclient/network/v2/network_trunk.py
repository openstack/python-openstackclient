# Copyright 2016 ZTE Corporation.
# All Rights Reserved
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
#

"""Network trunk and subports action implementations"""

import logging
import typing as ty

from cliff import columns as cliff_columns
from osc_lib.cli import format_columns
from osc_lib.cli import identity as identity_utils
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

TRUNK = 'trunk'
TRUNKS = 'trunks'
SUB_PORTS = 'sub_ports'


class AdminStateColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return 'UP' if self._value else 'DOWN'


class CreateNetworkTrunk(command.ShowOne):
    """Create a network trunk for a given project"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help=_("Name of the trunk to create")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("A description of the trunk"),
        )
        parser.add_argument(
            '--parent-port',
            metavar='<parent-port>',
            required=True,
            help=_("Parent port belonging to this trunk (name or ID)"),
        )
        parser.add_argument(
            '--subport',
            metavar='<port=,segmentation-type=,segmentation-id=>',
            action=parseractions.MultiKeyValueAction,
            dest='add_subports',
            optional_keys=['segmentation-id', 'segmentation-type'],
            required_keys=['port'],
            help=_(
                "Subport to add. Subport is of form "
                "'port=<name or ID>,segmentation-type=<segmentation-type>,"
                "segmentation-id=<segmentation-ID>' (repeat option "
                "to add multiple subports)"
            ),
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            action='store_true',
            default=True,
            help=_("Enable trunk (default)"),
        )
        admin_group.add_argument(
            '--disable', action='store_true', help=_("Disable trunk")
        )
        identity_utils.add_project_owner_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs_for_trunk(self.app.client_manager, parsed_args)
        obj = client.create_trunk(**attrs)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data


class DeleteNetworkTrunk(command.Command):
    """Delete a given network trunk"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trunk',
            metavar="<trunk>",
            nargs="+",
            help=_("Trunk(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0
        for trunk in parsed_args.trunk:
            try:
                trunk_id = client.find_trunk(trunk).id
                client.delete_trunk(trunk_id)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete trunk with name "
                        "or ID '%(trunk)s': %(e)s"
                    ),
                    {'trunk': trunk, 'e': e},
                )
        if result > 0:
            total = len(parsed_args.trunk)
            msg = _("%(result)s of %(total)s trunks failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListNetworkTrunk(command.Lister):
    """List all network trunks"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        data = client.trunks()
        headers: tuple[str, ...] = ('ID', 'Name', 'Parent Port', 'Description')
        columns: tuple[str, ...] = ('id', 'name', 'port_id', 'description')
        if parsed_args.long:
            headers += (
                'Status',
                'State',
                'Created At',
                'Updated At',
            )
            columns += ('status', 'admin_state_up', 'created_at', 'updated_at')
        return (
            headers,
            (
                osc_utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )


class SetNetworkTrunk(command.Command):
    """Set network trunk properties"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trunk', metavar="<trunk>", help=_("Trunk to modify (name or ID)")
        )
        parser.add_argument(
            '--name', metavar="<name>", help=_("Set trunk name")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("A description of the trunk"),
        )
        parser.add_argument(
            '--subport',
            metavar='<port=,segmentation-type=,segmentation-id=>',
            action=parseractions.MultiKeyValueAction,
            dest='set_subports',
            optional_keys=['segmentation-id', 'segmentation-type'],
            required_keys=['port'],
            help=_(
                "Subport to add. Subport is of form "
                "'port=<name or ID>,segmentation-type=<segmentation-type>,"
                "segmentation-id=<segmentation-ID>' (repeat option "
                "to add multiple subports)"
            ),
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable', action='store_true', help=_("Enable trunk")
        )
        admin_group.add_argument(
            '--disable', action='store_true', help=_("Disable trunk")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        trunk_id = client.find_trunk(parsed_args.trunk)
        attrs = _get_attrs_for_trunk(self.app.client_manager, parsed_args)
        try:
            client.update_trunk(trunk_id, **attrs)
        except Exception as e:
            msg = _("Failed to set trunk '%(t)s': %(e)s") % {
                't': parsed_args.trunk,
                'e': e,
            }
            raise exceptions.CommandError(msg)
        if parsed_args.set_subports:
            subport_attrs = _get_attrs_for_subports(
                self.app.client_manager, parsed_args
            )
            try:
                client.add_trunk_subports(trunk_id, subport_attrs)
            except Exception as e:
                msg = _("Failed to add subports to trunk '%(t)s': %(e)s") % {
                    't': parsed_args.trunk,
                    'e': e,
                }
                raise exceptions.CommandError(msg)


class ShowNetworkTrunk(command.ShowOne):
    """Show information of a given network trunk"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trunk', metavar="<trunk>", help=_("Trunk to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        trunk_id = client.find_trunk(parsed_args.trunk).id
        obj = client.get_trunk(trunk_id)
        display_columns, columns = _get_columns(obj)
        data = osc_utils.get_dict_properties(
            obj, columns, formatters=_formatters
        )
        return display_columns, data


class ListNetworkSubport(command.Lister):
    """List all subports for a given network trunk"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--trunk',
            required=True,
            metavar="<trunk>",
            help=_("List subports belonging to this trunk (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        trunk_id = client.find_trunk(parsed_args.trunk)
        data = client.get_trunk_subports(trunk_id)
        headers: tuple[str, ...] = (
            'Port',
            'Segmentation Type',
            'Segmentation ID',
        )
        columns: tuple[str, ...] = (
            'port_id',
            'segmentation_type',
            'segmentation_id',
        )
        return (
            headers,
            (
                osc_utils.get_dict_properties(
                    s,
                    columns,
                )
                for s in data[SUB_PORTS]
            ),
        )


class UnsetNetworkTrunk(command.Command):
    """Unset subports from a given network trunk"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trunk',
            metavar="<trunk>",
            help=_("Unset subports from this trunk (name or ID)"),
        )
        parser.add_argument(
            '--subport',
            metavar="<subport>",
            required=True,
            action='append',
            dest='unset_subports',
            help=_(
                "Subport to unset (name or ID of the port) "
                "(repeat option to unset multiple subports)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs_for_subports(self.app.client_manager, parsed_args)
        trunk_id = client.find_trunk(parsed_args.trunk)
        client.delete_trunk_subports(trunk_id, attrs)


_formatters = {
    'admin_state_up': AdminStateColumn,
    'sub_ports': format_columns.ListDictColumn,
}


def _get_columns(item):
    hidden_columns = ['location', 'tenant_id']
    return osc_utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


def _get_attrs_for_trunk(client_manager, parsed_args):
    attrs: dict[str, ty.Any] = {}
    if parsed_args.name is not None:
        attrs['name'] = str(parsed_args.name)
    if parsed_args.description is not None:
        attrs['description'] = str(parsed_args.description)
    if parsed_args.enable:
        attrs['admin_state_up'] = True
    if parsed_args.disable:
        attrs['admin_state_up'] = False
    if 'parent_port' in parsed_args and parsed_args.parent_port is not None:
        port_id = client_manager.network.find_port(parsed_args.parent_port)[
            'id'
        ]
        attrs['port_id'] = port_id
    if 'add_subports' in parsed_args and parsed_args.add_subports is not None:
        attrs[SUB_PORTS] = _format_subports(
            client_manager, parsed_args.add_subports
        )

    # "trunk set" command doesn't support setting project.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_utils.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    return attrs


def _format_subports(client_manager, subports):
    attrs = []
    for subport in subports:
        subport_attrs = {}
        if subport.get('port'):
            port_id = client_manager.network.find_port(subport['port'])['id']
            subport_attrs['port_id'] = port_id
        if subport.get('segmentation-id'):
            try:
                subport_attrs['segmentation_id'] = int(
                    subport['segmentation-id']
                )
            except ValueError:
                msg = (
                    _("Segmentation-id '%s' is not an integer")
                    % subport['segmentation-id']
                )
                raise exceptions.CommandError(msg)
        if subport.get('segmentation-type'):
            subport_attrs['segmentation_type'] = subport['segmentation-type']
        attrs.append(subport_attrs)
    return attrs


def _get_attrs_for_subports(client_manager, parsed_args):
    attrs = []
    if 'set_subports' in parsed_args and parsed_args.set_subports is not None:
        attrs = _format_subports(client_manager, parsed_args.set_subports)
    if (
        'unset_subports' in parsed_args
        and parsed_args.unset_subports is not None
    ):
        subports_list = []
        for subport in parsed_args.unset_subports:
            port_id = client_manager.network.find_port(subport)['id']
            subports_list.append({'port_id': port_id})
        attrs = subports_list
    return attrs


def _get_id(client, id_or_name, resource):
    return client.find_resource(resource, str(id_or_name))['id']
