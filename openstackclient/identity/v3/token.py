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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


class AuthorizeRequestToken(command.ShowOne):
    _description = _("Authorize a request token")

    def get_parser(self, prog_name):
        parser = super(AuthorizeRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            required=True,
            help=_('Request token to authorize (ID only) (required)'),
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            action='append',
            default=[],
            required=True,
            help=_('Roles to authorize (name or ID) '
                   '(repeat option to set multiple values) (required)'),
        )
        return parser

    def take_action(self, parsed_args):
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


class CreateAccessToken(command.ShowOne):
    _description = _("Create an access token")

    def get_parser(self, prog_name):
        parser = super(CreateAccessToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help=_('Consumer key (required)'),
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help=_('Consumer secret (required)'),
            required=True
        )
        parser.add_argument(
            '--request-key',
            metavar='<request-key>',
            help=_('Request token to exchange for access token (required)'),
            required=True
        )
        parser.add_argument(
            '--request-secret',
            metavar='<request-secret>',
            help=_('Secret associated with <request-key> (required)'),
            required=True
        )
        parser.add_argument(
            '--verifier',
            metavar='<verifier>',
            help=_('Verifier associated with <request-key> (required)'),
            required=True
        )
        return parser

    def take_action(self, parsed_args):
        token_client = self.app.client_manager.identity.oauth1.access_tokens
        access_token = token_client.create(
            parsed_args.consumer_key, parsed_args.consumer_secret,
            parsed_args.request_key, parsed_args.request_secret,
            parsed_args.verifier)
        return zip(*sorted(six.iteritems(access_token._info)))


class CreateRequestToken(command.ShowOne):
    _description = _("Create a request token")

    def get_parser(self, prog_name):
        parser = super(CreateRequestToken, self).get_parser(prog_name)
        parser.add_argument(
            '--consumer-key',
            metavar='<consumer-key>',
            help=_('Consumer key (required)'),
            required=True
        )
        parser.add_argument(
            '--consumer-secret',
            metavar='<consumer-secret>',
            help=_('Consumer secret (required)'),
            required=True
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project that consumer wants to access (name or ID)'
                   ' (required)'),
            required=True
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <project> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
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


class IssueToken(command.ShowOne):
    _description = _("Issue new token")

    # scoped token is optional
    required_scope = False

    def get_parser(self, prog_name):
        parser = super(IssueToken, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        auth_ref = self.app.client_manager.auth_ref
        if not auth_ref:
            raise exceptions.AuthorizationFailure(
                _("Only an authorized user may issue a new token."))

        data = {}
        if auth_ref.auth_token:
            data['id'] = auth_ref.auth_token
        if auth_ref.expires:
            datetime_obj = auth_ref.expires
            expires_str = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S%z')
            data['expires'] = expires_str
        if auth_ref.project_id:
            data['project_id'] = auth_ref.project_id
        if auth_ref.user_id:
            data['user_id'] = auth_ref.user_id
        if auth_ref.domain_id:
            data['domain_id'] = auth_ref.domain_id
        if auth_ref.system_scoped:
            # NOTE(lbragstad): This could change in the future when, or if,
            # keystone supports the ability to scope to a subset of the entire
            # deployment system. When that happens, this will have to relay
            # scope information and IDs like we do for projects and domains.
            data['system'] = 'all'
        return zip(*sorted(six.iteritems(data)))


class RevokeToken(command.Command):
    _description = _("Revoke existing token")

    def get_parser(self, prog_name):
        parser = super(RevokeToken, self).get_parser(prog_name)
        parser.add_argument(
            'token',
            metavar='<token>',
            help=_('Token to be deleted'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        identity_client.tokens.revoke_token(parsed_args.token)
