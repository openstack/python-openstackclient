# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

"""Metering Label Implementations"""

import logging

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import sdk_utils

LOG = logging.getLogger(__name__)


_formatters = {
    'location': format_columns.DictColumn,
}


def _get_columns(item):
    column_map = {
        'is_shared': 'shared',
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


def _get_attrs(client_manager, parsed_args):
    attrs = {}

    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.project is not None and 'project' in parsed_args:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id
    if parsed_args.share:
        attrs['shared'] = True
    if parsed_args.no_share:
        attrs['shared'] = False
    if parsed_args.name is not None:
        attrs['name'] = parsed_args.name

    return attrs


# TODO(ankur-gupta-f): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateMeter(command.ShowOne):
    _description = _("Create network meter")

    def get_parser(self, prog_name):
        parser = super(CreateMeter, self).get_parser(prog_name)

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Create description for meter")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )

        identity_common.add_project_domain_option_to_parser(parser)
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Share meter between projects")
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("Do not share meter between projects")
        )
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of meter'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_metering_label(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)

        return (display_columns, data)


# TODO(ankur-gupta-f): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class DeleteMeter(command.Command):
    _description = _("Delete network meter")

    def get_parser(self, prog_name):
        parser = super(DeleteMeter, self).get_parser(prog_name)

        parser.add_argument(
            'meter',
            metavar='<meter>',
            nargs='+',
            help=_('Meter to delete (name or ID)')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for meter in parsed_args.meter:
            try:
                obj = client.find_metering_label(meter, ignore_missing=False)
                client.delete_metering_label(obj)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete meter with "
                            "ID '%(meter)s': %(e)s"),
                          {"meter": meter, "e": e})
        if result > 0:
            total = len(parsed_args.meter)
            msg = (_("%(result)s of %(total)s meters failed "
                     "to delete.") % {"result": result, "total": total})
            raise exceptions.CommandError(msg)


class ListMeter(command.Lister):
    _description = _("List network meters")

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'name',
            'description',
            'shared',
        )
        column_headers = (
            'ID',
            'Name',
            'Description',
            'Shared',
        )

        data = client.metering_labels()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowMeter(command.ShowOne):
    _description = _("Show network meter")

    def get_parser(self, prog_name):
        parser = super(ShowMeter, self).get_parser(prog_name)
        parser.add_argument(
            'meter',
            metavar='<meter>',
            help=_('Meter to display (name or ID)')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_metering_label(parsed_args.meter,
                                         ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return display_columns, data
