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


class CreateToken(show.ShowOne):
    """Issue token command"""

    log = logging.getLogger(__name__ + '.CreateToken')

    def get_parser(self, prog_name):
        parser = super(CreateToken, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        token = identity_client.service_catalog.get_token()
        token['project_id'] = token.pop('tenant_id')
        return zip(*sorted(six.iteritems(token)))


class DeleteToken(command.Command):
    """Revoke token command"""

    log = logging.getLogger(__name__ + '.DeleteToken')

    def get_parser(self, prog_name):
        parser = super(DeleteToken, self).get_parser(prog_name)
        parser.add_argument(
            'token',
            metavar='<token>',
            help='Token to be deleted',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        identity_client.tokens.delete(parsed_args.token)
        return
