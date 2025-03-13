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

"""Flavor action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common

LOG = logging.getLogger(__name__)


def _get_columns(item):
    column_map = {
        'is_enabled': 'enabled',
    }

    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    attrs['name'] = parsed_args.name
    attrs['service_type'] = parsed_args.service_type
    if parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.enable:
        attrs['enabled'] = True
    if parsed_args.disable:
        attrs['enabled'] = False
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    return attrs


class AddNetworkFlavorToProfile(command.Command):
    _description = _("Add a service profile to a network flavor")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'flavor', metavar="<flavor>", help=_("Network flavor (name or ID)")
        )
        parser.add_argument(
            'service_profile',
            metavar="<service-profile>",
            help=_("Service profile (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj_flavor = client.find_flavor(
            parsed_args.flavor, ignore_missing=False
        )
        obj_service_profile = client.find_service_profile(
            parsed_args.service_profile, ignore_missing=False
        )
        client.associate_flavor_with_service_profile(
            obj_flavor, obj_service_profile
        )


# TODO(dasanind): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateNetworkFlavor(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create new network flavor")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar="<name>", help=_("Name for the flavor")
        )
        parser.add_argument(
            '--service-type',
            metavar="<service-type>",
            required=True,
            help=_(
                'Service type to which the flavor applies. For example: VPN '
                '(See openstack network service provider list for loaded '
                'examples.)'
            ),
        )
        parser.add_argument(
            '--description', help=_('Description for the flavor')
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_("Enable the flavor (default)"),
        )
        enable_group.add_argument(
            '--disable', action='store_true', help=_("Disable the flavor")
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        obj = client.create_flavor(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteNetworkFlavor(command.Command):
    _description = _("Delete network flavors")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            nargs='+',
            help=_('Flavor(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for flavor in parsed_args.flavor:
            try:
                obj = client.find_flavor(flavor, ignore_missing=False)
                client.delete_flavor(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete flavor with "
                        "name or ID '%(flavor)s': %(e)s"
                    ),
                    {"flavor": flavor, "e": e},
                )
        if result > 0:
            total = len(parsed_args.flavor)
            msg = _("%(result)s of %(total)s flavors failed to delete.") % {
                "result": result,
                "total": total,
            }
            raise exceptions.CommandError(msg)


class ListNetworkFlavor(command.Lister):
    _description = _("List network flavors")

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = ('id', 'name', 'is_enabled', 'service_type', 'description')
        column_headers = (
            'ID',
            'Name',
            'Enabled',
            'Service Type',
            'Description',
        )

        data = client.flavors()
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


class RemoveNetworkFlavorFromProfile(command.Command):
    _description = _("Remove service profile from network flavor")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'flavor', metavar="<flavor>", help=_("Network flavor (name or ID)")
        )
        parser.add_argument(
            'service_profile',
            metavar="<service-profile>",
            help=_("Service profile (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj_flavor = client.find_flavor(
            parsed_args.flavor, ignore_missing=False
        )
        obj_service_profile = client.find_service_profile(
            parsed_args.service_profile, ignore_missing=False
        )
        client.disassociate_flavor_from_service_profile(
            obj_flavor, obj_service_profile
        )


# TODO(dasanind): Use only the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetworkFlavor(common.NeutronCommandWithExtraArgs):
    _description = _("Set network flavor properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar="<flavor>",
            help=_("Flavor to update (name or ID)"),
        )
        parser.add_argument(
            '--description', help=_('Set network flavor description')
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--disable', action='store_true', help=_("Disable network flavor")
        )
        enable_group.add_argument(
            '--enable', action='store_true', help=_("Enable network flavor")
        )
        parser.add_argument(
            '--name', metavar="<name>", help=_('Set flavor name')
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_flavor(parsed_args.flavor, ignore_missing=False)
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.enable:
            attrs['enabled'] = True
        if parsed_args.disable:
            attrs['enabled'] = False
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        client.update_flavor(obj, **attrs)


class ShowNetworkFlavor(command.ShowOne):
    _description = _("Display network flavor details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_('Flavor to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_flavor(parsed_args.flavor, ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data
