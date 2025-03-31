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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common

LOG = logging.getLogger(__name__)


def _get_columns(item):
    column_map = {
        'is_enabled': 'enabled',
    }

    hidden_columns = ['location', 'name', 'tenant_id', 'project_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.driver is not None:
        attrs['driver'] = parsed_args.driver
    if parsed_args.metainfo is not None:
        attrs['metainfo'] = parsed_args.metainfo
    if parsed_args.enable:
        attrs['enabled'] = True
    if parsed_args.disable:
        attrs['enabled'] = False

    return attrs


# TODO(ndahiwade): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateNetworkFlavorProfile(
    command.ShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create new network flavor profile")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_("Description for the flavor profile"),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_("Enable the flavor profile"),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable the flavor profile"),
        )
        parser.add_argument(
            '--driver',
            help=_(
                "Python module path to driver. This becomes "
                "required if --metainfo is missing and vice-versa."
            ),
        )
        parser.add_argument(
            '--metainfo',
            help=_(
                "Metainfo for the flavor profile. This becomes "
                "required if --driver is missing and vice-versa."
            ),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        if parsed_args.driver is None and parsed_args.metainfo is None:
            msg = _("Either --driver or --metainfo or both are required")
            raise exceptions.CommandError(msg)

        obj = client.create_service_profile(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteNetworkFlavorProfile(command.Command):
    _description = _("Delete network flavor profile")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'flavor_profile',
            metavar='<flavor-profile>',
            nargs='+',
            help=_("Flavor profile(s) to delete (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for flavor_profile in parsed_args.flavor_profile:
            try:
                obj = client.find_service_profile(
                    flavor_profile, ignore_missing=False
                )
                client.delete_service_profile(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete flavor profile with "
                        "ID '%(flavor_profile)s': %(e)s"
                    ),
                    {"flavor_profile": flavor_profile, "e": e},
                )
        if result > 0:
            total = len(parsed_args.flavor_profile)
            msg = _(
                "%(result)s of %(total)s flavor_profiles failed to delete."
            ) % {"result": result, "total": total}
            raise exceptions.CommandError(msg)


class ListNetworkFlavorProfile(command.Lister):
    _description = _("List network flavor profile(s)")

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'driver',
            'is_enabled',
            'meta_info',
            'description',
        )
        column_headers = (
            'ID',
            'Driver',
            'Enabled',
            'Metainfo',
            'Description',
        )

        data = client.service_profiles()
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


# TODO(ndahiwade): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetworkFlavorProfile(common.NeutronCommandWithExtraArgs):
    _description = _("Set network flavor profile properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'flavor_profile',
            metavar="<flavor-profile>",
            help=_("Flavor profile to update (ID only)"),
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_("Description for the flavor profile"),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_("Enable the flavor profile"),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_("Disable the flavor profile"),
        )
        parser.add_argument(
            '--driver',
            help=_(
                "Python module path to driver. This becomes "
                "required if --metainfo is missing and vice-versa."
            ),
        )
        parser.add_argument(
            '--metainfo',
            help=_(
                "Metainfo for the flavor profile. This becomes "
                "required if --driver is missing and vice-versa."
            ),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_service_profile(
            parsed_args.flavor_profile, ignore_missing=False
        )
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        client.update_service_profile(obj, **attrs)


class ShowNetworkFlavorProfile(command.ShowOne):
    _description = _("Display network flavor profile details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'flavor_profile',
            metavar='<flavor-profile>',
            help=_("Flavor profile to display (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_service_profile(
            parsed_args.flavor_profile, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)
