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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


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
        identity_client = self.app.client_manager.identity
        protocol = identity_client.federation.protocols.create(
            protocol_id=parsed_args.federation_protocol,
            identity_provider=parsed_args.identity_provider,
            mapping=parsed_args.mapping,
        )
        info = dict(protocol._info)
        # NOTE(marek-denis): Identity provider is not included in a response
        # from Keystone, however it should be listed to the user. Add it
        # manually to the output list, simply reusing value provided by the
        # user.
        info['identity_provider'] = parsed_args.identity_provider
        info['mapping'] = info.pop('mapping_id')
        info.pop('links', None)
        return zip(*sorted(info.items()))


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
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.federation_protocol:
            try:
                identity_client.federation.protocols.delete(
                    parsed_args.identity_provider, i
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
        identity_client = self.app.client_manager.identity

        protocols = identity_client.federation.protocols.list(
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
        identity_client = self.app.client_manager.identity

        protocol = identity_client.federation.protocols.update(
            parsed_args.identity_provider,
            parsed_args.federation_protocol,
            parsed_args.mapping,
        )
        info = dict(protocol._info)
        # NOTE(marek-denis): Identity provider is not included in a response
        # from Keystone, however it should be listed to the user. Add it
        # manually to the output list, simply reusing value provided by the
        # user.
        info['identity_provider'] = parsed_args.identity_provider
        info['mapping'] = info.pop('mapping_id')
        return zip(*sorted(info.items()))


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
        identity_client = self.app.client_manager.identity

        protocol = identity_client.federation.protocols.get(
            parsed_args.identity_provider, parsed_args.federation_protocol
        )
        info = dict(protocol._info)
        info['mapping'] = info.pop('mapping_id')
        info.pop('links', None)
        return zip(*sorted(info.items()))
