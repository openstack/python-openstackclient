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

"""Manage access to the clients, including authenticating when needed."""

import logging
import pkg_resources
import sys

from osc_lib import clientmanager
from osc_lib import shell


LOG = logging.getLogger(__name__)

PLUGIN_MODULES = []

USER_AGENT = 'python-openstackclient'


class ClientManager(clientmanager.ClientManager):
    """Manages access to API clients, including authentication

    Wrap osc_lib's ClientManager to maintain compatibility for the existing
    plugin V2 interface.  Some currently private attributes become public
    in osc-lib so we need to maintain a transition period.
    """

    # A simple incrementing version for the plugin to know what is available
    PLUGIN_INTERFACE_VERSION = "2"

    def __init__(
        self,
        cli_options=None,
        api_version=None,
    ):
        super(ClientManager, self).__init__(
            cli_options=cli_options,
            api_version=api_version,
            # TODO(dtroyer): Remove this when osc-lib 1.2 is released
            pw_func=shell.prompt_for_password,
        )

        # TODO(dtroyer): For compatibility; mark this for removal when plugin
        #                interface v2 is removed
        self._region_name = self.region_name
        self._interface = self.interface
        self._cacert = self.cacert
        self._insecure = not self.verify

    def setup_auth(self):
        """Set up authentication"""

        if self._auth_setup_completed:
            return

        # NOTE(dtroyer): Validate the auth args; this is protected with 'if'
        #                because openstack_config is an optional argument to
        #                CloudConfig.__init__() and we'll die if it was not
        #                passed.
        if self._cli_options._openstack_config is not None:
            self._cli_options._openstack_config._pw_callback = \
                shell.prompt_for_password
            self._cli_options._auth = \
                self._cli_options._openstack_config.load_auth_plugin(
                    self._cli_options.config,
                )

        return super(ClientManager, self).setup_auth()

    def is_network_endpoint_enabled(self):
        """Check if the network endpoint is enabled"""

        # NOTE(dtroyer): is_service_available() can also return None if
        #                there is no Service Catalog, callers here are
        #                not expecting that so fold None into True to
        #                use Network API by default
        return self.is_service_available('network') is not False


# Plugin Support

def get_plugin_modules(group):
    """Find plugin entry points"""
    mod_list = []
    for ep in pkg_resources.iter_entry_points(group):
        LOG.debug('Found plugin %r', ep.name)

        __import__(ep.module_name)
        module = sys.modules[ep.module_name]
        mod_list.append(module)
        init_func = getattr(module, 'Initialize', None)
        if init_func:
            init_func('x')

        # Add the plugin to the ClientManager
        setattr(
            clientmanager.ClientManager,
            module.API_NAME,
            clientmanager.ClientCache(
                getattr(sys.modules[ep.module_name], 'make_client', None)
            ),
        )
    return mod_list


def build_plugin_option_parser(parser):
    """Add plugin options to the parser"""

    # Loop through extensions to get parser additions
    for mod in PLUGIN_MODULES:
        parser = mod.build_option_parser(parser)
    return parser


# Get list of base plugin modules
PLUGIN_MODULES = get_plugin_modules(
    'openstack.cli.base',
)
# Append list of external plugin modules
PLUGIN_MODULES.extend(get_plugin_modules(
    'openstack.cli.extension',
))
