#   Copyright 2021 Huawei, Inc. All rights reserved.
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

"""Node Local IP action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location', 'name', 'id', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateLocalIPAssociation(command.ShowOne):
    _description = _("Create Local IP Association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'local_ip',
            metavar='<local-ip>',
            help=_(
                "Local IP that the port association belongs to (Name or ID)"
            ),
        )
        parser.add_argument(
            'fixed_port',
            metavar='<fixed-port>',
            help=_("The ID or Name of Port to allocate Local IP Association"),
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='<fixed-ip>',
            help=_("Fixed IP for Local IP Association"),
        )

        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        attrs = {}
        port = client.find_port(parsed_args.fixed_port, ignore_missing=False)
        attrs['fixed_port_id'] = port.id
        if parsed_args.fixed_ip:
            attrs['fixed_ip'] = parsed_args.fixed_ip
        local_ip = client.find_local_ip(
            parsed_args.local_ip,
            ignore_missing=False,
        )
        obj = client.create_local_ip_association(local_ip.id, **attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteLocalIPAssociation(command.Command):
    _description = _("Delete Local IP association(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'local_ip',
            metavar="<local-ip>",
            help=_(
                "Local IP that the port association belongs to (Name or ID)"
            ),
        )
        parser.add_argument(
            'fixed_port_id',
            nargs="+",
            metavar="<fixed-port-id>",
            help=_("The fixed port ID of Local IP Association"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        local_ip = client.find_local_ip(
            parsed_args.local_ip,
            ignore_missing=False,
        )
        result = 0

        for fixed_port_id in parsed_args.fixed_port_id:
            try:
                client.delete_local_ip_association(
                    local_ip.id,
                    fixed_port_id,
                    ignore_missing=False,
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete Local IP Association with "
                        "fixed port "
                        "name or ID '%(fixed_port_id)s': %(e)s"
                    ),
                    {'fixed_port_id': fixed_port_id, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.fixed_port_id)
            msg = _(
                "%(result)s of %(total)s Local IP Associations failed "
                "to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListLocalIPAssociation(command.Lister):
    _description = _("List Local IP Associations")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'local_ip',
            metavar='<local-ip>',
            help=_("Local IP that port associations belongs to"),
        )
        parser.add_argument(
            '--fixed-port',
            metavar='<fixed-port>',
            help=_(
                "Filter the list result by the ID or name of the fixed port"
            ),
        )
        parser.add_argument(
            '--fixed-ip',
            metavar='<fixed-ip>',
            help=_("Filter the list result by fixed ip"),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_("Filter the list result by given host"),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'local_ip_id',
            'local_ip_address',
            'fixed_port_id',
            'fixed_ip',
            'host',
        )
        column_headers = (
            'Local IP ID',
            'Local IP Address',
            'Fixed port ID',
            'Fixed IP',
            'Host',
        )
        attrs = {}
        obj = client.find_local_ip(
            parsed_args.local_ip,
            ignore_missing=False,
        )
        if parsed_args.fixed_port:
            port = client.find_port(
                parsed_args.fixed_port, ignore_missing=False
            )
            attrs['fixed_port_id'] = port.id
        if parsed_args.fixed_ip:
            attrs['fixed_ip'] = parsed_args.fixed_ip
        if parsed_args.host:
            attrs['host'] = parsed_args.host

        data = client.local_ip_associations(obj, **attrs)

        return (
            column_headers,
            (
                utils.get_item_properties(s, columns, formatters={})
                for s in data
            ),
        )
