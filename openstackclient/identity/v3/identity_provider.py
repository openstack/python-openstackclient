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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateIdentityProvider(command.ShowOne):
    """Create new identity provider"""

    def get_parser(self, prog_name):
        parser = super(CreateIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider_id',
            metavar='<name>',
            help=_('New identity provider name (must be unique)'),
        )
        identity_remote_id_provider = parser.add_mutually_exclusive_group()
        identity_remote_id_provider.add_argument(
            '--remote-id',
            metavar='<remote-id>',
            action='append',
            help=_('Remote IDs to associate with the Identity Provider '
                   '(repeat option to provide multiple values)'),
        )
        identity_remote_id_provider.add_argument(
            '--remote-id-file',
            metavar='<file-name>',
            help=_('Name of a file that contains many remote IDs to associate '
                   'with the identity provider, one per line'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New identity provider description'),
        )
        enable_identity_provider = parser.add_mutually_exclusive_group()
        enable_identity_provider.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help=_('Enable identity provider (default)'),
        )
        enable_identity_provider.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help=_('Disable the identity provider'),
        )
        return parser

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
        remote_ids = utils.format_list(idp._info.pop('remote_ids', []))
        idp._info['remote_ids'] = remote_ids
        return zip(*sorted(six.iteritems(idp._info)))


class DeleteIdentityProvider(command.Command):
    """Delete identity provider(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            nargs='+',
            help=_('Identity provider(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.identity_provider:
            try:
                identity_client.federation.identity_providers.delete(i)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete identity providers with "
                          "name or ID '%(provider)s': %(e)s")
                          % {'provider': i, 'e': e})

        if result > 0:
            total = len(parsed_args.identity_provider)
            msg = (_("%(result)s of %(total)s identity providers failed"
                   " to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListIdentityProvider(command.Lister):
    """List identity providers"""

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

    def get_parser(self, prog_name):
        parser = super(SetIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            help=_('Identity provider to modify'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set identity provider description'),
        )
        identity_remote_id_provider = parser.add_mutually_exclusive_group()
        identity_remote_id_provider.add_argument(
            '--remote-id',
            metavar='<remote-id>',
            action='append',
            help=_('Remote IDs to associate with the Identity Provider '
                   '(repeat option to provide multiple values)'),
        )
        identity_remote_id_provider.add_argument(
            '--remote-id-file',
            metavar='<file-name>',
            help=_('Name of a file that contains many remote IDs to associate '
                   'with the identity provider, one per line'),
        )
        enable_identity_provider = parser.add_mutually_exclusive_group()
        enable_identity_provider.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable the identity provider'),
        )
        enable_identity_provider.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable the identity provider'),
        )
        return parser

    def take_action(self, parsed_args):
        federation_client = self.app.client_manager.identity.federation

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
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False
        if parsed_args.remote_id_file or parsed_args.remote_id:
            kwargs['remote_ids'] = remote_ids

        federation_client.identity_providers.update(
            parsed_args.identity_provider,
            **kwargs
        )


class ShowIdentityProvider(command.ShowOne):
    """Display identity provider details"""

    def get_parser(self, prog_name):
        parser = super(ShowIdentityProvider, self).get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            help=_('Identity provider to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        idp = utils.find_resource(
            identity_client.federation.identity_providers,
            parsed_args.identity_provider,
            id=parsed_args.identity_provider)

        idp._info.pop('links', None)
        remote_ids = utils.format_list(idp._info.pop('remote_ids', []))
        idp._info['remote_ids'] = remote_ids
        return zip(*sorted(six.iteritems(idp._info)))
