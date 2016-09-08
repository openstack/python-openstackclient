#   Copyright 2014 eBay Inc.
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

"""Identity v2 Token action implementations"""

from osc_lib.command import command
from osc_lib import exceptions
import six

from openstackclient.i18n import _


class IssueToken(command.ShowOne):
    """Issue new token"""

    # scoped token is optional
    required_scope = False

    def get_parser(self, prog_name):
        parser = super(IssueToken, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        auth_ref = self.app.client_manager.auth_ref
        if not auth_ref:
            raise exceptions.AuthorizationFailure(
                "Only an authorized user may issue a new token.")

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
        return zip(*sorted(six.iteritems(data)))


class RevokeToken(command.Command):
    """Revoke existing token"""

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

        identity_client.tokens.delete(parsed_args.token)
