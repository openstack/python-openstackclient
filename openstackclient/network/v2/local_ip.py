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
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    network_client = client_manager.network

    if parsed_args.name:
        attrs['name'] = parsed_args.name
    if parsed_args.description:
        attrs['description'] = parsed_args.description
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id
    if parsed_args.network:
        network = network_client.find_network(
            parsed_args.network, ignore_missing=False
        )
        attrs['network_id'] = network.id
    if parsed_args.local_ip_address:
        attrs['local_ip_address'] = parsed_args.local_ip_address
    if parsed_args.local_port:
        port = network_client.find_port(
            parsed_args.local_port, ignore_missing=False
        )
        attrs['local_port_id'] = port.id
    if parsed_args.ip_mode:
        attrs['ip_mode'] = parsed_args.ip_mode
    return attrs


class CreateLocalIP(command.ShowOne):
    _description = _("Create Local IP")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--name', metavar="<name>", help=_("New Local IP name")
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_("Description for Local IP"),
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_("Network to allocate Local IP from (name or ID)"),
        )
        parser.add_argument(
            '--local-port',
            metavar='<local-port>',
            help=_("Port to allocate Local IP from (name or ID)"),
        )
        parser.add_argument(
            "--local-ip-address",
            metavar="<local-ip-address>",
            help=_("IP address or CIDR for Local IP"),
        )
        parser.add_argument(
            '--ip-mode',
            metavar='<ip-mode>',
            help=_("IP mode to use for Local IP"),
        )

        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)

        obj = client.create_local_ip(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteLocalIP(command.Command):
    _description = _("Delete Local IP(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'local_ip',
            metavar="<local-ip>",
            nargs='+',
            help=_("Local IP(s) to delete (name or ID)"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for lip in parsed_args.local_ip:
            try:
                obj = client.find_local_ip(lip, ignore_missing=False)
                client.delete_local_ip(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete Local IP with "
                        "name or ID '%(lip)s': %(e)s"
                    ),
                    {'lip': lip, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.local_ip)
            msg = _("%(result)s of %(total)s local IPs failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class SetLocalIP(command.Command):
    _description = _("Set Local IP properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'local_ip',
            metavar="<local-ip>",
            help=_("Local IP to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar="<name>", help=_('Set local IP name')
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help=_('Set Local IP description'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_local_ip(parsed_args.local_ip, ignore_missing=False)
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if attrs:
            client.update_local_ip(obj, **attrs)


class ListLocalIP(command.Lister):
    _description = _("List Local IPs")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List only Local IPs of given name in output"),
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_("List Local IPs according to their project (name or ID)"),
        )
        parser.add_argument(
            '--network',
            metavar='<network>',
            help=_("List Local IP(s) according to given network (name or ID)"),
        )
        parser.add_argument(
            '--local-port',
            metavar='<local-port>',
            help=_("List Local IP(s) according to given port (name or ID)"),
        )
        parser.add_argument(
            '--local-ip-address',
            metavar='<local-ip-address>',
            help=_("List Local IP(s) according to given Local IP Address"),
        )
        parser.add_argument(
            '--ip-mode',
            metavar='<ip_mode>',
            help=_("List Local IP(s) according to given IP mode"),
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
            'local_port_id',
            'network_id',
            'local_ip_address',
            'ip_mode',
        )
        column_headers = (
            'ID',
            'Name',
            'Description',
            'Project',
            'Local Port ID',
            'Network',
            'Local IP address',
            'IP mode',
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
        if parsed_args.network is not None:
            network = client.find_network(
                parsed_args.network, ignore_missing=False
            )
            attrs['network_id'] = network.id
        if parsed_args.local_port:
            port = client.find_port(
                parsed_args.local_port, ignore_missing=False
            )
            attrs['local_port_id'] = port.id
        if parsed_args.local_ip_address:
            attrs['local_ip_address'] = parsed_args.local_ip_address
        if parsed_args.ip_mode:
            attrs['ip_mode'] = parsed_args.ip_mode
        data = client.local_ips(**attrs)

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


class ShowLocalIP(command.ShowOne):
    _description = _("Display Local IP details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'local_ip',
            metavar="<local-ip>",
            help=_("Local IP to display (name or ID)"),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_local_ip(parsed_args.local_ip, ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)
