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

import logging
import six

from cliff import command
from cliff import show

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa


class IssueToken(show.ShowOne):
    """Issue new token"""

    log = logging.getLogger(__name__ + '.IssueToken')

    def get_parser(self, prog_name):
        parser = super(IssueToken, self).get_parser(prog_name)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        token = self.app.client_manager.auth_ref.service_catalog.get_token()
        token['project_id'] = token.pop('tenant_id')
        return zip(*sorted(six.iteritems(token)))


class RevokeToken(command.Command):
    """Revoke existing token"""

    log = logging.getLogger(__name__ + '.RevokeToken')

    def get_parser(self, prog_name):
        parser = super(RevokeToken, self).get_parser(prog_name)
        parser.add_argument(
            'token',
            metavar='<token>',
            help=_('Token to be deleted'),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        identity_client.tokens.delete(parsed_args.token)
        return
