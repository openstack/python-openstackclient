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

"""Network action implementations"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from openstack import connection

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.identity import common as identity_common


def _format_admin_state(item):
    return 'UP' if item else 'DOWN'


def _format_router_external(item):
    return 'External' if item else 'Internal'


_formatters = {
    'subnets': utils.format_list,
    'admin_state_up': _format_admin_state,
    'router_external': _format_router_external,
}


def _make_client_sdk(instance):
    """Return a network proxy"""
    conn = connection.Connection(authenticator=instance.session.auth)
    return conn.network


class CreateNetwork(show.ShowOne):
    """Create new network"""

    log = logging.getLogger(__name__ + '.CreateNetwork')

    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New network name',
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            action='store_true',
            default=True,
            help='Enable network (default)',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Disable network',
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            dest='shared',
            action='store_true',
            default=None,
            help='Share the network between projects',
        )
        share_group.add_argument(
            '--no-share',
            dest='shared',
            action='store_false',
            help='Do not share the network between projects',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help="Owner's project (name or ID)")
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        self.app.client_manager.network = \
            _make_client_sdk(self.app.client_manager)
        client = self.app.client_manager.network
        body = self.get_body(parsed_args)
        obj = client.create_network(**body)
        columns = sorted(obj.keys())
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (tuple(columns), data)

    def get_body(self, parsed_args):
        body = {'name': str(parsed_args.name),
                'admin_state_up': parsed_args.admin_state}
        if parsed_args.shared is not None:
            body['shared'] = parsed_args.shared
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            body['tenant_id'] = project_id
        return body


class DeleteNetwork(command.Command):
    """Delete network(s)"""

    log = logging.getLogger(__name__ + '.DeleteNetwork')

    def get_parser(self, prog_name):
        parser = super(DeleteNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'networks',
            metavar="<network>",
            nargs="+",
            help=("Network to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        self.app.client_manager.network = \
            _make_client_sdk(self.app.client_manager)
        client = self.app.client_manager.network
        for network in parsed_args.networks:
            obj = client.find_network(network)
            client.delete_network(obj)
        return


class ListNetwork(lister.Lister):
    """List networks"""

    log = logging.getLogger(__name__ + '.ListNetwork')

    def get_parser(self, prog_name):
        parser = super(ListNetwork, self).get_parser(prog_name)
        parser.add_argument(
            '--external',
            action='store_true',
            default=False,
            help='List external networks',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        self.app.client_manager.network = \
            _make_client_sdk(self.app.client_manager)
        client = self.app.client_manager.network

        if parsed_args.long:
            columns = (
                'id',
                'name',
                'status',
                'tenant_id',
                'admin_state_up',
                'shared',
                'subnets',
                'provider_network_type',
                'router_external',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Project',
                'State',
                'Shared',
                'Subnets',
                'Network Type',
                'Router Type',
            )
        else:
            columns = (
                'id',
                'name',
                'subnets'
            )
            column_headers = (
                'ID',
                'Name',
                'Subnets',
            )

        if parsed_args.external:
            args = {'router:external': True}
        else:
            args = {}
        data = client.networks(**args)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters=_formatters,
                ) for s in data))


class SetNetwork(command.Command):
    """Set network properties"""

    log = logging.getLogger(__name__ + '.SetNetwork')

    def get_parser(self, prog_name):
        parser = super(SetNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'identifier',
            metavar="<network>",
            help=("Network to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set network name',
        )
        admin_group = parser.add_mutually_exclusive_group()
        admin_group.add_argument(
            '--enable',
            dest='admin_state',
            action='store_true',
            default=None,
            help='Enable network',
        )
        admin_group.add_argument(
            '--disable',
            dest='admin_state',
            action='store_false',
            help='Disable network',
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            dest='shared',
            action='store_true',
            default=None,
            help='Share the network between projects',
        )
        share_group.add_argument(
            '--no-share',
            dest='shared',
            action='store_false',
            help='Do not share the network between projects',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        self.app.client_manager.network = \
            _make_client_sdk(self.app.client_manager)
        client = self.app.client_manager.network
        obj = client.find_network(parsed_args.identifier, ignore_missing=False)

        if parsed_args.name is not None:
            obj.name = str(parsed_args.name)
        if parsed_args.admin_state is not None:
            obj.admin_state_up = parsed_args.admin_state
        if parsed_args.shared is not None:
            obj.shared = parsed_args.shared

        if not obj.is_dirty:
            msg = "Nothing specified to be set"
            raise exceptions.CommandError(msg)

        client.update_network(obj)
        return


class ShowNetwork(show.ShowOne):
    """Show network details"""

    log = logging.getLogger(__name__ + '.ShowNetwork')

    def get_parser(self, prog_name):
        parser = super(ShowNetwork, self).get_parser(prog_name)
        parser.add_argument(
            'identifier',
            metavar="<network>",
            help=("Network to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        self.app.client_manager.network = \
            _make_client_sdk(self.app.client_manager)
        client = self.app.client_manager.network
        obj = client.find_network(parsed_args.identifier, ignore_missing=False)
        columns = sorted(obj.keys())
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (tuple(columns), data)
