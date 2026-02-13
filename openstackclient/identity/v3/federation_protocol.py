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


"""Identity v3 Protocols actions implementations"""

import logging

from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_protocol(protocol):
    columns = ('name', 'idp_id', 'mapping_id')
    column_headers = ('id', 'identity_provider', 'mapping')
    return (
        column_headers,
        utils.get_item_properties(protocol, columns),
    )


class CreateProtocol(command.ShowOne):
    _description = _("Create new federation protocol")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help=_(
                'New federation protocol name (must be unique '
                'per identity provider)'
            ),
        )
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help=_(
                'Identity provider that will support the new federation '
                ' protocol (name or ID) (required)'
            ),
        )
        parser.add_argument(
            '--mapping',
            metavar='<mapping>',
            required=True,
            help=_('Mapping that is to be used (name or ID) (required)'),
        )

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        protocol = identity_client.create_federation_protocol(
            name=parsed_args.federation_protocol,
            idp_id=parsed_args.identity_provider,
            mapping_id=parsed_args.mapping,
        )

        return _format_protocol(protocol)


class DeleteProtocol(command.Command):
    _description = _("Delete federation protocol(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<federation-protocol>',
            nargs='+',
            help=_('Federation protocol(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help=_(
                'Identity provider that supports <federation-protocol> '
                '(name or ID) (required)'
            ),
        )

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        result = 0
        for i in parsed_args.federation_protocol:
            try:
                identity_client.delete_federation_protocol(
                    idp_id=parsed_args.identity_provider,
                    protocol=i,
                    ignore_missing=False,
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete federation protocol "
                        "with name or ID '%(protocol)s': %(e)s"
                    ),
                    {'protocol': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.federation_protocol)
            msg = _(
                "%(result)s of %(total)s federation protocols failed"
                " to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListProtocols(command.Lister):
    _description = _("List federation protocols")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help=_('Identity provider to list (name or ID) (required)'),
        )

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        protocols = identity_client.federation_protocols(
            parsed_args.identity_provider
        )
        columns = ('id', 'mapping')
        response_attributes = ('id', 'mapping_id')
        items = [
            utils.get_item_properties(s, response_attributes)
            for s in protocols
        ]
        return (columns, items)


class SetProtocol(command.Command):
    _description = _("Set federation protocol properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help=_('Federation protocol to modify (name or ID)'),
        )
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help=_(
                'Identity provider that supports <federation-protocol> '
                '(name or ID) (required)'
            ),
        )
        parser.add_argument(
            '--mapping',
            metavar='<mapping>',
            help=_('Mapping that is to be used (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {'idp_id': parsed_args.identity_provider}
        if parsed_args.federation_protocol:
            kwargs['name'] = parsed_args.federation_protocol
        if parsed_args.mapping:
            kwargs['mapping_id'] = parsed_args.mapping

        protocol = identity_client.update_federation_protocol(**kwargs)
        return _format_protocol(protocol)


class ShowProtocol(command.ShowOne):
    _description = _("Display federation protocol details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<federation-protocol>',
            help=_('Federation protocol to display (name or ID)'),
        )
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help=_(
                'Identity provider that supports <federation-protocol> '
                '(name or ID) (required)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        protocol = identity_client.get_federation_protocol(
            idp_id=parsed_args.identity_provider,
            protocol=parsed_args.federation_protocol,
        )
        return _format_protocol(protocol)
