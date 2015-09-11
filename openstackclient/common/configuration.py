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

"""Configuration action implementations"""

import logging

from cliff import show
import six

from openstackclient.common import utils

REDACTED = "<redacted>"


class ShowConfiguration(show.ShowOne):
    """Display configuration details"""

    log = logging.getLogger(__name__ + '.ShowConfiguration')

    def get_parser(self, prog_name):
        parser = super(ShowConfiguration, self).get_parser(prog_name)
        mask_group = parser.add_mutually_exclusive_group()
        mask_group.add_argument(
            "--mask",
            dest="mask",
            action="store_true",
            default=True,
            help="Attempt to mask passwords (default)",
        )
        mask_group.add_argument(
            "--unmask",
            dest="mask",
            action="store_false",
            help="Show password in clear text",
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        info = self.app.client_manager.get_configuration()
        for key, value in six.iteritems(info.pop('auth', {})):
            if parsed_args.mask:
                if 'password' in key.lower():
                    value = REDACTED
                if 'token' in key.lower():
                    value = REDACTED
            info['auth.' + key] = value
        return zip(*sorted(six.iteritems(info)))
