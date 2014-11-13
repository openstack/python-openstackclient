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

"""Identity v3 IdentityProvider action implementations"""

import logging
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateIdentityProvider(show.ShowOne):
    """Create new identity provider"""

    log = logging.getLogger(__name__ + '.CreateIdentityProvider')

    def get_parser(self, prog_name):
        parser = super(CreateIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider_id',
            metavar='<identity-provider-id>',
            help='New identity provider ID (must be unique)'
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New identity provider description',
        )

        enable_identity_provider = parser.add_mutually_exclusive_group()
        enable_identity_provider.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable identity provider',
        )
        enable_identity_provider.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable the identity provider',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        idp = identity_client.federation.identity_providers.create(
            id=parsed_args.identity_provider_id,
            description=parsed_args.description,
            enabled=parsed_args.enabled)

        idp._info.pop('links', None)
        return zip(*sorted(six.iteritems(idp._info)))


class DeleteIdentityProvider(command.Command):
    """Delete an identity provider"""

    log = logging.getLogger(__name__ + '.DeleteIdentityProvider')

    def get_parser(self, prog_name):
        parser = super(DeleteIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider-id>',
            help='Identity provider ID to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        identity_client.federation.identity_providers.delete(
            parsed_args.identity_provider)
        return


class ListIdentityProvider(lister.Lister):
    """List identity providers"""

    log = logging.getLogger(__name__ + '.ListIdentityProvider')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        columns = ('ID', 'Enabled', 'Description')
        identity_client = self.app.client_manager.identity
        data = identity_client.federation.identity_providers.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetIdentityProvider(command.Command):
    """Set identity provider properties"""

    log = logging.getLogger(__name__ + '.SetIdentityProvider')

    def get_parser(self, prog_name):
        parser = super(SetIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider-id>',
            help='Identity provider ID to change',
        )

        enable_identity_provider = parser.add_mutually_exclusive_group()
        enable_identity_provider.add_argument(
            '--enable',
            action='store_true',
            help='Enable the identity provider',
        )
        enable_identity_provider.add_argument(
            '--disable',
            action='store_true',
            help='Disable the identity provider',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        federation_client = self.app.client_manager.identity.federation

        if parsed_args.enable is True:
            enabled = True
        elif parsed_args.disable is True:
            enabled = False
        else:
            sys.stdout.write("Identity Provider not updated, "
                             "no arguments present")
            return (None, None)

        identity_provider = federation_client.identity_providers.update(
            parsed_args.identity_provider, enabled=enabled)
        info = {}
        info.update(identity_provider._info)
        return zip(*sorted(six.iteritems(info)))


class ShowIdentityProvider(show.ShowOne):
    """Show identity provider details"""

    log = logging.getLogger(__name__ + '.ShowIdentityProvider')

    def get_parser(self, prog_name):
        parser = super(ShowIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider-id>',
            help='Identity provider ID to show',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        identity_provider = utils.find_resource(
            identity_client.federation.identity_providers,
            parsed_args.identity_provider)

        identity_provider._info.pop('links', None)
        return zip(*sorted(six.iteritems(identity_provider._info)))
