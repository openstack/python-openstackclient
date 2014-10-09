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
    """Create new Federation Protocol tied to an Identity Provider"""

    log = logging.getLogger(__name__ + 'CreateProtocol')

    def get_parser(self, prog_name):
        parser = super(CreateProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help='Protocol (must be unique per Identity Provider')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>',
            help=('Identity Provider you want to add the Protocol to '
                  '(must already exist)'), required=True)
        parser.add_argument(
            '--mapping',
            metavar='<mapping>', required=True,
            help='Mapping you want to be used (must already exist)')

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
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
        return zip(*sorted(six.iteritems(info)))


class DeleteProtocol(command.Command):
    """Delete Federation Protocol tied to a Identity Provider"""

    log = logging.getLogger(__name__ + '.DeleteProtocol')

    def get_parser(self, prog_name):
        parser = super(DeleteProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help='Protocol (must be unique per Identity Provider')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>', required=True,
            help='Identity Provider the Protocol is tied to')

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        identity_client.federation.protocols.delete(
            parsed_args.identity_provider, parsed_args.federation_protocol)
        return


class ListProtocols(lister.Lister):
    """List Protocols tied to an Identity Provider"""

    log = logging.getLogger(__name__ + '.ListProtocols')

    def get_parser(self, prog_name):
        parser = super(ListProtocols, self).get_parser(prog_name)
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>', required=True,
            help='Identity Provider the Protocol is tied to')

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
    """Set Protocol tied to an Identity Provider"""

    log = logging.getLogger(__name__ + '.SetProtocol')

    def get_parser(self, prog_name):
        parser = super(SetProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help='Protocol (must be unique per Identity Provider')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>', required=True,
            help=('Identity Provider you want to add the Protocol to '
                  '(must already exist)'))
        parser.add_argument(
            '--mapping',
            metavar='<mapping>', required=True,
            help='Mapping you want to be used (must already exist)')
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

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
    """Show Protocol tied to an Identity Provider"""

    log = logging.getLogger(__name__ + '.ShowProtocol')

    def get_parser(self, prog_name):
        parser = super(ShowProtocol, self).get_parser(prog_name)
        parser.add_argument(
            'federation_protocol',
            metavar='<name>',
            help='Protocol (must be unique per Identity Provider')
        parser.add_argument(
            '--identity-provider',
            metavar='<identity-provider>', required=True,
            help=('Identity Provider you want to add the Protocol to '
                  '(must already exist)'))
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        protocol = identity_client.federation.protocols.get(
            parsed_args.identity_provider, parsed_args.federation_protocol)
        info = dict(protocol._info)
        info['mapping'] = info.pop('mapping_id')
        return zip(*sorted(six.iteritems(info)))
