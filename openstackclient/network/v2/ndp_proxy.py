# Copyright (c) 2020 Troila.
# All Rights Reserved.
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

"""Router NDP proxy action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateNDPProxy(command.ShowOne):
    _description = _("Create NDP proxy")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router', metavar='<router>', help=_("The name or ID of a router")
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_("New NDP proxy name")
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            required=True,
            help=_(
                "The name or ID of the network port associated "
                "to the NDP proxy"
            ),
        )
        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            help=_(
                "The IPv6 address that is to be proxied. In case the port "
                "has multiple addresses assigned, use this option to "
                "select which address is to be used."
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                "Text to describe/contextualize the use of the "
                "NDP proxy configuration"
            ),
        )

        return parser

    def take_action(self, parsed_args):
        attrs = {'name': parsed_args.name}
        client = self.app.client_manager.network
        router = client.find_router(
            parsed_args.router,
            ignore_missing=False,
        )
        attrs['router_id'] = router.id

        if parsed_args.ip_address:
            attrs['ip_address'] = parsed_args.ip_address

        port = client.find_port(parsed_args.port, ignore_missing=False)
        attrs['port_id'] = port.id

        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description

        obj = client.create_ndp_proxy(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)


class DeleteNDPProxy(command.Command):
    _description = _("Delete NDP proxy")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'ndp_proxy',
            nargs="+",
            metavar="<ndp-proxy>",
            help=_("NDP proxy(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for ndp_proxy in parsed_args.ndp_proxy:
            try:
                obj = client.find_ndp_proxy(ndp_proxy, ignore_missing=False)
                client.delete_ndp_proxy(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete NDP proxy '%(ndp_proxy)s': %(e)s"),
                    {'ndp_proxy': ndp_proxy, 'e': e},
                )
        if result > 0:
            total = len(parsed_args.ndp_proxy)
            msg = _(
                "%(result)s of %(total)s NDP proxies failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListNDPProxy(command.Lister):
    _description = _("List NDP proxies")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--router',
            metavar='<router>',
            help=_(
                "List only NDP proxies belonging to this router (name or ID)"
            ),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_(
                "List only NDP proxies associated to this port (name or ID)"
            ),
        )
        parser.add_argument(
            '--ip-address',
            metavar='<ip-address>',
            help=_("List only NDP proxies associated to this IPv6 address"),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List only NDP proxies of given project (name or ID)"),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("List only NDP proxies of given name"),
        )

        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        identity_client = self.app.client_manager.identity

        columns = (
            'id',
            'name',
            'router_id',
            'ip_address',
            'project_id',
        )
        headers = (
            'ID',
            'Name',
            'Router ID',
            'IP Address',
            'Project',
        )

        query = {}

        if parsed_args.router:
            router = client.find_router(
                parsed_args.router, ignore_missing=False
            )
            query['router_id'] = router.id
        if parsed_args.port:
            port = client.find_port(parsed_args.port, ignore_missing=False)
            query['port_id'] = port.id
        if parsed_args.ip_address is not None:
            query['ip_address'] = parsed_args.ip_address
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            query['project_id'] = project_id
        if parsed_args.name:
            query['name'] = parsed_args.name

        data = client.ndp_proxies(**query)

        return (
            headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class SetNDPProxy(command.Command):
    _description = _("Set NDP proxy properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'ndp_proxy',
            metavar='<ndp-proxy>',
            help=_("The ID or name of the NDP proxy to update"),
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_("Set NDP proxy name")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                "Text to describe/contextualize the use of "
                "the NDP proxy configuration"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = {}
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name

        obj = client.find_ndp_proxy(
            parsed_args.ndp_proxy, ignore_missing=False
        )
        client.update_ndp_proxy(obj, **attrs)


class ShowNDPProxy(command.ShowOne):
    _description = _("Display NDP proxy details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'ndp_proxy',
            metavar="<ndp-proxy>",
            help=_("The ID or name of the NDP proxy"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_ndp_proxy(
            parsed_args.ndp_proxy, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return (display_columns, data)
