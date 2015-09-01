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
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateProtocol(show.ShowOne):
    """Create new federation protocol"""

    log = logging.getLogger(__name__ + 'CreateProtocol')

    def get_parser(self, prog_name):
        parser = super(CreateProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help='New federation protocol name (must be unique per identity '
                 ' provider)')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help='Identity provider that will support the new federation '
                 ' protocol (name or ID) (required)')
        parser.add_argument(
            '--mapping',
            metavar='<mapping>',
            required=True,
            help='Mapping that is to be used (name or ID) (required)')

        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        protocol = identity_client.federation.protocols.create(
            protocol_id=parsed_args.federation_protocol,
            identity_provider=parsed_args.identity_provider,
            mapping=parsed_args.mapping)
        info = dict(protocol._info)
        # NOTE(marek-denis): Identity provider is not included in a response
        # from Keystone, however it should be listed to the user. Add it
        # manually to the output list, simply reusing value provided by the
        # user.
        info['identity_provider'] = parsed_args.identity_provider
        info['mapping'] = info.pop('mapping_id')
        info.pop('links', None)
        return zip(*sorted(six.iteritems(info)))


class DeleteProtocol(command.Command):
    """Delete federation protocol"""

    log = logging.getLogger(__name__ + '.DeleteProtocol')

    def get_parser(self, prog_name):
        parser = super(DeleteProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<federation-protocol>',
            help='Federation protocol to delete (name or ID)')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help='Identity provider that supports <federation-protocol> '
                 '(name or ID) (required)')

        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        identity_client.federation.protocols.delete(
            parsed_args.identity_provider, parsed_args.federation_protocol)
        return


class ListProtocols(lister.Lister):
    """List federation protocols"""

    log = logging.getLogger(__name__ + '.ListProtocols')

    def get_parser(self, prog_name):
        parser = super(ListProtocols, self).get_parser(prog_name)
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help='Identity provider to list (name or ID) (required)')

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        protocols = identity_client.federation.protocols.list(
            parsed_args.identity_provider)
        columns = ('id', 'mapping')
        response_attributes = ('id', 'mapping_id')
        items = [utils.get_item_properties(s, response_attributes)
                 for s in protocols]
        return (columns, items)


class SetProtocol(command.Command):
    """Set federation protocol properties"""

    log = logging.getLogger(__name__ + '.SetProtocol')

    def get_parser(self, prog_name):
        parser = super(SetProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help='Federation protocol to modify (name or ID)')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help='Identity provider that supports <federation-protocol> '
                 '(name or ID) (required)')
        parser.add_argument(
            '--mapping',
            metavar='<mapping>',
            help='Mapping that is to be used (name or ID)')
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if not parsed_args.mapping:
            self.app.log.error("No changes requested")
            return

        protocol = identity_client.federation.protocols.update(
            parsed_args.identity_provider, parsed_args.federation_protocol,
            parsed_args.mapping)
        info = dict(protocol._info)
        # NOTE(marek-denis): Identity provider is not included in a response
        # from Keystone, however it should be listed to the user. Add it
        # manually to the output list, simply reusing value provided by the
        # user.
        info['identity_provider'] = parsed_args.identity_provider
        info['mapping'] = info.pop('mapping_id')
        return zip(*sorted(six.iteritems(info)))


class ShowProtocol(show.ShowOne):
    """Display federation protocol details"""

    log = logging.getLogger(__name__ + '.ShowProtocol')

    def get_parser(self, prog_name):
        parser = super(ShowProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<federation-protocol>',
            help='Federation protocol to display (name or ID)')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            required=True,
            help=('Identity provider that supports <federation-protocol> '
                  '(name or ID) (required)'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        protocol = identity_client.federation.protocols.get(
            parsed_args.identity_provider, parsed_args.federation_protocol)
        info = dict(protocol._info)
        info['mapping'] = info.pop('mapping_id')
        info.pop('links', None)
        return zip(*sorted(six.iteritems(info)))
