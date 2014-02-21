#   Copyright 2012-2013 OpenStack Foundation
#
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

"""Identity v3 Token action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class AuthenticateAccessToken(show.ShowOne):
    """Authenticate access token to receive keystone token"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.AuthenticateAccessToken')

    def get_parser(self, prog_name):
        parser = super(AuthenticateAccessToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help='Consumer key',
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help='Consumer secret',
            required=True
        )
        parser.add_argument(
            '--access-key',
            metavar='<access-key>',
            help='Access token key',
            required=True
        )
        parser.add_argument(
            '--access-secret',
            metavar='<access-secret>',
            help='Access token secret',
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        token_client = self.app.client_manager.identity.tokens
        keystone_token = token_client.authenticate_access_token(
            parsed_args.consumer_key, parsed_args.consumer_secret,
            parsed_args.access_key, parsed_args.access_secret)
        return zip(*sorted(six.iteritems(keystone_token)))


class AuthorizeRequestToken(show.ShowOne):
    """Authorize request token command"""

    log = logging.getLogger(__name__ + '.AuthorizeRequestToken')

    def get_parser(self, prog_name):
        parser = super(AuthorizeRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            help='Consumer key',
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        token_client = self.app.client_manager.identity.tokens

        verifier_pin = token_client.authorize_request_token(
            parsed_args.request_key)
        info = {}
        info.update(verifier_pin._info)
        return zip(*sorted(six.iteritems(info)))


class CreateAccessToken(show.ShowOne):
    """Create access token command"""

    log = logging.getLogger(__name__ + '.CreateAccessToken')

    def get_parser(self, prog_name):
        parser = super(CreateAccessToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help='Consumer key',
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help='Consumer secret',
            required=True
        )
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            help='Request token key',
            required=True
        )
        parser.add_argument(
            '--request-secret',
            metavar='<request-secret>',
            help='Request token secret',
            required=True
        )
        parser.add_argument(
            '--verifier',
            metavar='<verifier>',
            help='Verifier Pin',
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        token_client = self.app.client_manager.identity.tokens
        access_token = token_client.create_access_token(
            parsed_args.consumer_key, parsed_args.consumer_secret,
            parsed_args.request_key, parsed_args.request_secret,
            parsed_args.verifier)
        return zip(*sorted(six.iteritems(access_token)))


class CreateRequestToken(show.ShowOne):
    """Create request token command"""

    log = logging.getLogger(__name__ + '.CreateRequestToken')

    def get_parser(self, prog_name):
        parser = super(CreateRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help='Consumer key',
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help='Consumer secret',
            required=True
        )
        parser.add_argument(
            '--role-ids',
            metavar='<role-ids>',
            help='Requested role IDs',
        )
        parser.add_argument(
            '--project-id',
            metavar='<project-id>',
            help='Requested project ID',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        token_client = self.app.client_manager.identity.tokens
        request_token = token_client.create_request_token(
            parsed_args.consumer_key,
            parsed_args.consumer_secret,
            parsed_args.role_ids,
            parsed_args.project_id)
        return zip(*sorted(six.iteritems(request_token)))


class CreateToken(show.ShowOne):
    """Create token command"""

    log = logging.getLogger(__name__ + '.CreateToken')

    def get_parser(self, prog_name):
        parser = super(CreateToken, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        token = identity_client.service_catalog.get_token()
        if 'tenant_id' in token:
            token['project_id'] = token.pop('tenant_id')
        return zip(*sorted(six.iteritems(token)))


class DeleteAccessToken(command.Command):
    """Delete access token command"""

    log = logging.getLogger(__name__ + '.DeleteAccessToken')

    def get_parser(self, prog_name):
        parser = super(DeleteAccessToken, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user',
        )
        parser.add_argument(
            'access_key',
            metavar='<access-key>',
            help='Access token to be deleted',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user).id
        identity_client.tokens.delete_access_token(user,
                                                   parsed_args.access_key)
        return


class ListAccessToken(lister.Lister):
    """List access tokens command"""

    log = logging.getLogger(__name__ + '.ListAccessToken')

    def get_parser(self, prog_name):
        parser = super(ListAccessToken, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user).id

        columns = ('ID', 'Consumer ID', 'Expires At',
                   'Project Id', 'Authorizing User Id')
        data = identity_client.tokens.list_access_tokens(user)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))
