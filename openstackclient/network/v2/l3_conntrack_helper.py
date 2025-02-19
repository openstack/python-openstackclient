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

"""L3 Conntrack Helper action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


def _get_attrs(client, parsed_args):
    router = client.find_router(parsed_args.router, ignore_missing=False)
    attrs = {'router_id': router.id}
    if parsed_args.helper:
        attrs['helper'] = parsed_args.helper
    if parsed_args.protocol:
        attrs['protocol'] = parsed_args.protocol
    if parsed_args.port:
        attrs['port'] = parsed_args.port

    return attrs


class CreateConntrackHelper(command.ShowOne):
    _description = _("Create a new L3 conntrack helper")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_('Router for which conntrack helper will be created'),
        )
        parser.add_argument(
            '--helper',
            required=True,
            metavar='<helper>',
            help=_('The netfilter conntrack helper module'),
        )
        parser.add_argument(
            '--protocol',
            required=True,
            metavar='<protocol>',
            help=_(
                'The network protocol for the netfilter conntrack target rule'
            ),
        )
        parser.add_argument(
            '--port',
            required=True,
            metavar='<port>',
            type=int,
            help=_('The network port for the netfilter conntrack target rule'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        attrs = _get_attrs(client, parsed_args)
        obj = client.create_conntrack_helper(attrs.pop('router_id'), **attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteConntrackHelper(command.Command):
    _description = _("Delete L3 conntrack helper")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_('Router that the conntrack helper belongs to'),
        )
        parser.add_argument(
            'conntrack_helper_id',
            metavar='<conntrack-helper-id>',
            nargs='+',
            help=_('The ID of the conntrack helper(s) to delete'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        router = client.find_router(parsed_args.router, ignore_missing=False)
        for ct_helper in parsed_args.conntrack_helper_id:
            try:
                client.delete_conntrack_helper(
                    ct_helper, router.id, ignore_missing=False
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete L3 conntrack helper with "
                        "ID '%(ct_helper)s': %(e)s"
                    ),
                    {'ct_helper': ct_helper, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.conntrack_helper_id)
            msg = _(
                "%(result)s of %(total)s L3 conntrack helpers failed "
                "to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListConntrackHelper(command.Lister):
    _description = _("List L3 conntrack helpers")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_('Router that the conntrack helper belongs to'),
        )
        parser.add_argument(
            '--helper',
            metavar='<helper>',
            help=_('The netfilter conntrack helper module'),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            help=_(
                'The network protocol for the netfilter conntrack target rule'
            ),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            help=_('The network port for the netfilter conntrack target rule'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'router_id',
            'helper',
            'protocol',
            'port',
        )
        column_headers = (
            'ID',
            'Router ID',
            'Helper',
            'Protocol',
            'Port',
        )
        attrs = _get_attrs(client, parsed_args)
        data = client.conntrack_helpers(attrs.pop('router_id'), **attrs)

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


class SetConntrackHelper(command.Command):
    _description = _("Set L3 conntrack helper properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_('Router that the conntrack helper belongs to'),
        )
        parser.add_argument(
            'conntrack_helper_id',
            metavar='<conntrack-helper-id>',
            help=_('The ID of the conntrack helper(s)'),
        )
        parser.add_argument(
            '--helper',
            metavar='<helper>',
            help=_('The netfilter conntrack helper module'),
        )
        parser.add_argument(
            '--protocol',
            metavar='<protocol>',
            help=_(
                'The network protocol for the netfilter conntrack target rule'
            ),
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help=_('The network port for the netfilter conntrack target rule'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(client, parsed_args)
        if attrs:
            client.update_conntrack_helper(
                parsed_args.conntrack_helper_id,
                attrs.pop('router_id'),
                **attrs,
            )


class ShowConntrackHelper(command.ShowOne):
    _description = _("Display L3 conntrack helper details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'router',
            metavar='<router>',
            help=_('Router that the conntrack helper belongs to'),
        )
        parser.add_argument(
            'conntrack_helper_id',
            metavar='<conntrack-helper-id>',
            help=_('The ID of the conntrack helper'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        router = client.find_router(parsed_args.router, ignore_missing=False)
        obj = client.get_conntrack_helper(
            parsed_args.conntrack_helper_id, router.id
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)
