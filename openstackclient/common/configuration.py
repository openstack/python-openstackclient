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

from keystoneauth1.loading import base
from osc_lib.command import command
import six

from openstackclient.i18n import _

REDACTED = "<redacted>"


class ShowConfiguration(command.ShowOne):
    _description = _("Display configuration details")

    auth_required = False

    def get_parser(self, prog_name):
        parser = super(ShowConfiguration, self).get_parser(prog_name)
        mask_group = parser.add_mutually_exclusive_group()
        mask_group.add_argument(
            "--mask",
            dest="mask",
            action="store_true",
            default=True,
            help=_("Attempt to mask passwords (default)"),
        )
        mask_group.add_argument(
            "--unmask",
            dest="mask",
            action="store_false",
            help=_("Show password in clear text"),
        )
        return parser

    def take_action(self, parsed_args):

        info = self.app.client_manager.get_configuration()

        # Assume a default secret list in case we do not have an auth_plugin
        secret_opts = ["password", "token"]

        if getattr(self.app.client_manager, "auth_plugin_name", None):
            auth_plg_name = self.app.client_manager.auth_plugin_name
            secret_opts = [
                o.dest for o in base.get_plugin_options(auth_plg_name)
                if o.secret
            ]

        for key, value in six.iteritems(info.pop('auth', {})):
            if parsed_args.mask and key.lower() in secret_opts:
                value = REDACTED
            info['auth.' + key] = value

        return zip(*sorted(six.iteritems(info)))
