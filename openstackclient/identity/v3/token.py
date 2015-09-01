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

from openstackclient.common import utils
from openstackclient.identity import common


class AuthorizeRequestToken(show.ShowOne):
    """Authorize a request token"""

    log = logging.getLogger(__name__ + '.AuthorizeRequestToken')

    def get_parser(self, prog_name):
        parser = super(AuthorizeRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            help='Request token to authorize (ID only) (required)',
            required=True
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            action='append',
            default=[],
            help='Roles to authorize (name or ID) '
                 '(repeat to set multiple values) (required)',
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        # NOTE(stevemar): We want a list of role ids
        roles = []
        for role in parsed_args.role:
            role_id = utils.find_resource(
                identity_client.roles,
                role,
            ).id
            roles.append(role_id)

        verifier_pin = identity_client.oauth1.request_tokens.authorize(
            parsed_args.request_key,
            roles)

        return zip(*sorted(six.iteritems(verifier_pin._info)))


class CreateAccessToken(show.ShowOne):
    """Create an access token"""

    log = logging.getLogger(__name__ + '.CreateAccessToken')

    def get_parser(self, prog_name):
        parser = super(CreateAccessToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help='Consumer key (required)',
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help='Consumer secret (required)',
            required=True
        )
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            help='Request token to exchange for access token (required)',
            required=True
        )
        parser.add_argument(
            '--request-secret',
            metavar='<request-secret>',
            help='Secret associated with <request-key> (required)',
            required=True
        )
        parser.add_argument(
            '--verifier',
            metavar='<verifier>',
            help='Verifier associated with <request-key> (required)',
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
        return zip(*sorted(six.iteritems(access_token._info)))


class CreateRequestToken(show.ShowOne):
    """Create a request token"""

    log = logging.getLogger(__name__ + '.CreateRequestToken')

    def get_parser(self, prog_name):
        parser = super(CreateRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help='Consumer key (required)',
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help='Consumer secret (required)',
            required=True
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Project that consumer wants to access (name or ID)'
                 ' (required)',
            required=True
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain owning <project> (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        identity_client = self.app.client_manager.identity

        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project,
                                          domain_id=domain.id)
        else:
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project)

        token_client = identity_client.oauth1.request_tokens

        request_token = token_client.create(
            parsed_args.consumer_key,
            parsed_args.consumer_secret,
            project.id)
        return zip(*sorted(six.iteritems(request_token._info)))


class IssueToken(show.ShowOne):
    """Issue new token"""

    log = logging.getLogger(__name__ + '.IssueToken')

    def get_parser(self, prog_name):
        parser = super(IssueToken, self).get_parser(prog_name)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        token = self.app.client_manager.auth_ref.service_catalog.get_token()
        if 'tenant_id' in token:
            token['project_id'] = token.pop('tenant_id')
        return zip(*sorted(six.iteritems(token)))
