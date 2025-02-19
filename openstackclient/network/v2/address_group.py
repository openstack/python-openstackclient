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

"""Address group action implementations"""

import logging

import netaddr
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common

LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


def _format_addresses(addresses):
    return [str(netaddr.IPNetwork(addr)) for addr in addresses]


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    attrs['name'] = parsed_args.name
    if parsed_args.description:
        attrs['description'] = parsed_args.description
    attrs['addresses'] = _format_addresses(parsed_args.address)
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    return attrs


class CreateAddressGroup(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create a new Address Group")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar="<name>", help=_("New address group name")
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_("New address group description"),
        )
        parser.add_argument(
            "--address",
            metavar="<ip-address>",
            action='append',
            default=[],
            help=_(
                "IP address or CIDR (repeat option to set multiple addresses)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        obj = client.create_address_group(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteAddressGroup(command.Command):
    _description = _("Delete address group(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'address_group',
            metavar="<address-group>",
            nargs='+',
            help=_("Address group(s) to delete (name or ID)"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for group in parsed_args.address_group:
            try:
                obj = client.find_address_group(group, ignore_missing=False)
                client.delete_address_group(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete address group with "
                        "name or ID '%(group)s': %(e)s"
                    ),
                    {'group': group, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.address_group)
            msg = _(
                "%(result)s of %(total)s address groups failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListAddressGroup(command.Lister):
    _description = _("List address groups")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List only address groups of given name in output"),
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_(
                "List address groups according to their project (name or ID)"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'name',
            'description',
            'project_id',
            'addresses',
        )
        column_headers = (
            'ID',
            'Name',
            'Description',
            'Project',
            'Addresses',
        )
        attrs = {}
        if parsed_args.name:
            attrs['name'] = parsed_args.name
        if 'project' in parsed_args and parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['project_id'] = project_id
        data = client.address_groups(**attrs)

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class SetAddressGroup(common.NeutronCommandWithExtraArgs):
    _description = _("Set address group properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'address_group',
            metavar="<address-group>",
            help=_("Address group to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar="<name>", help=_('Set address group name')
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_('Set address group description'),
        )
        parser.add_argument(
            "--address",
            metavar="<ip-address>",
            action='append',
            default=[],
            help=_(
                "IP address or CIDR (repeat option to set multiple addresses)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_address_group(
            parsed_args.address_group, ignore_missing=False
        )
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        if attrs:
            client.update_address_group(obj, **attrs)
        if parsed_args.address:
            client.add_addresses_to_address_group(
                obj, _format_addresses(parsed_args.address)
            )


class ShowAddressGroup(command.ShowOne):
    _description = _("Display address group details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'address_group',
            metavar="<address-group>",
            help=_("Address group to display (name or ID)"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_address_group(
            parsed_args.address_group, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class UnsetAddressGroup(command.Command):
    _description = _("Unset address group properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'address_group',
            metavar="<address-group>",
            help=_("Address group to modify (name or ID)"),
        )
        parser.add_argument(
            "--address",
            metavar="<ip-address>",
            action='append',
            default=[],
            help=_(
                "IP address or CIDR "
                "(repeat option to unset multiple addresses)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_address_group(
            parsed_args.address_group, ignore_missing=False
        )
        if parsed_args.address:
            client.remove_addresses_from_address_group(
                obj, _format_addresses(parsed_args.address)
            )
