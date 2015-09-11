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
            metavar='<name>',
            help='New identity provider name (must be unique)'
        )
        identity_remote_id_provider = parser.add_mutually_exclusive_group()
        identity_remote_id_provider.add_argument(
            '--remote-id',
            metavar='<remote-id>',
            action='append',
            help='Remote IDs to associate with the Identity Provider '
                 '(repeat to provide multiple values)'
        )
        identity_remote_id_provider.add_argument(
            '--remote-id-file',
            metavar='<file-name>',
            help='Name of a file that contains many remote IDs to associate '
                 'with the identity provider, one per line'
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
            help='Enable identity provider (default)',
        )
        enable_identity_provider.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable the identity provider',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.remote_id_file:
            file_content = utils.read_blob_file_contents(
                parsed_args.remote_id_file)
            remote_ids = file_content.splitlines()
            remote_ids = list(map(str.strip, remote_ids))
        else:
            remote_ids = (parsed_args.remote_id
                          if parsed_args.remote_id else None)
        idp = identity_client.federation.identity_providers.create(
            id=parsed_args.identity_provider_id,
            remote_ids=remote_ids,
            description=parsed_args.description,
            enabled=parsed_args.enabled)

        idp._info.pop('links', None)
        return zip(*sorted(six.iteritems(idp._info)))


class DeleteIdentityProvider(command.Command):
    """Delete identity provider"""

    log = logging.getLogger(__name__ + '.DeleteIdentityProvider')

    def get_parser(self, prog_name):
        parser = super(DeleteIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            help='Identity provider to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        identity_client.federation.identity_providers.delete(
            parsed_args.identity_provider)
        return


class ListIdentityProvider(lister.Lister):
    """List identity providers"""

    log = logging.getLogger(__name__ + '.ListIdentityProvider')

    @utils.log_method(log)
    def take_action(self, parsed_args):
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
            metavar='<identity-provider>',
            help='Identity provider to modify',
        )
        identity_remote_id_provider = parser.add_mutually_exclusive_group()
        identity_remote_id_provider.add_argument(
            '--remote-id',
            metavar='<remote-id>',
            action='append',
            help='Remote IDs to associate with the Identity Provider '
                 '(repeat to provide multiple values)'
        )
        identity_remote_id_provider.add_argument(
            '--remote-id-file',
            metavar='<file-name>',
            help='Name of a file that contains many remote IDs to associate '
                 'with the identity provider, one per line'
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

    @utils.log_method(log)
    def take_action(self, parsed_args):
        federation_client = self.app.client_manager.identity.federation

        # Basic argument checking
        if (not parsed_args.enable and not parsed_args.disable and not
                parsed_args.remote_id and not parsed_args.remote_id_file):
            self.log.error('No changes requested')
            return (None, None)

        # Always set remote_ids if either is passed in
        if parsed_args.remote_id_file:
            file_content = utils.read_blob_file_contents(
                parsed_args.remote_id_file)
            remote_ids = file_content.splitlines()
            remote_ids = list(map(str.strip, remote_ids))
        elif parsed_args.remote_id:
            remote_ids = parsed_args.remote_id

        # Setup keyword args for the client
        kwargs = {}
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False
        if parsed_args.remote_id_file or parsed_args.remote_id:
            kwargs['remote_ids'] = remote_ids

        identity_provider = federation_client.identity_providers.update(
            parsed_args.identity_provider, **kwargs)

        identity_provider._info.pop('links', None)
        return zip(*sorted(six.iteritems(identity_provider._info)))


class ShowIdentityProvider(show.ShowOne):
    """Display identity provider details"""

    log = logging.getLogger(__name__ + '.ShowIdentityProvider')

    def get_parser(self, prog_name):
        parser = super(ShowIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            help='Identity provider to display',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        identity_provider = utils.find_resource(
            identity_client.federation.identity_providers,
            parsed_args.identity_provider)

        identity_provider._info.pop('links', None)
        return zip(*sorted(six.iteritems(identity_provider._info)))
