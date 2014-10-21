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

from cliff import show


class AuthorizeRequestToken(show.ShowOne):
    """Authorize request token"""

    log = logging.getLogger(__name__ + '.AuthorizeRequestToken')

    def get_parser(self, prog_name):
        parser = super(AuthorizeRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            help='Request token key',
            required=True
        )
        parser.add_argument(
            '--role-ids',
            metavar='<role-ids>',
            help='Requested role IDs',
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        roles = []
        for r_id in parsed_args.role_ids.split():
            roles.append(r_id)

        verifier_pin = identity_client.oauth1.request_tokens.authorize(
            parsed_args.request_key,
            roles)
        info = {}
        info.update(verifier_pin._info)
        return zip(*sorted(six.iteritems(info)))


class CreateAccessToken(show.ShowOne):
    """Create access token"""

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
        token_client = self.app.client_manager.identity.oauth1.access_tokens
        access_token = token_client.create(
            parsed_args.consumer_key, parsed_args.consumer_secret,
            parsed_args.request_key, parsed_args.request_secret,
            parsed_args.verifier)
        info = {}
        info.update(access_token._info)
        return zip(*sorted(six.iteritems(info)))


class CreateRequestToken(show.ShowOne):
    """Create request token"""

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
            '--project-id',
            metavar='<project-id>',
            help='Requested project ID',
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        token_client = self.app.client_manager.identity.oauth1.request_tokens
        request_token = token_client.create(
            parsed_args.consumer_key,
            parsed_args.consumer_secret,
            parsed_args.project_id)
        info = {}
        info.update(request_token._info)
        return zip(*sorted(six.iteritems(info)))


class IssueToken(show.ShowOne):
    """Issue new token"""

    log = logging.getLogger(__name__ + '.IssueToken')

    def get_parser(self, prog_name):
        parser = super(IssueToken, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        token = self.app.client_manager.auth_ref.service_catalog.get_token()
        if 'tenant_id' in token:
            token['project_id'] = token.pop('tenant_id')
        return zip(*sorted(six.iteritems(token)))
