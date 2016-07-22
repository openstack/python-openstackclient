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

from keystoneauth1.loading import base
from osc_lib.api import auth
from osc_lib import clientmanager


LOG = logging.getLogger(__name__)

PLUGIN_MODULES = []

USER_AGENT = 'python-openstackclient'


# NOTE(dtroyer): Bringing back select_auth_plugin() and build_auth_params()
#                temporarily because osc-lib 0.3.0 removed it a wee bit early
def select_auth_plugin(options):
    """Pick an auth plugin based on --os-auth-type or other options"""

    auth_plugin_name = None

    # Do the token/url check first as this must override the default
    # 'password' set by os-client-config
    # Also, url and token are not copied into o-c-c's auth dict (yet?)
    if options.auth.get('url') and options.auth.get('token'):
        # service token authentication
        auth_plugin_name = 'token_endpoint'
    elif options.auth_type in auth.PLUGIN_LIST:
        # A direct plugin name was given, use it
        auth_plugin_name = options.auth_type
    elif options.auth.get('username'):
        if options.identity_api_version == '3':
            auth_plugin_name = 'v3password'
        elif options.identity_api_version.startswith('2'):
            auth_plugin_name = 'v2password'
        else:
            # let keystoneauth figure it out itself
            auth_plugin_name = 'password'
    elif options.auth.get('token'):
        if options.identity_api_version == '3':
            auth_plugin_name = 'v3token'
        elif options.identity_api_version.startswith('2'):
            auth_plugin_name = 'v2token'
        else:
            # let keystoneauth figure it out itself
            auth_plugin_name = 'token'
    else:
        # The ultimate default is similar to the original behaviour,
        # but this time with version discovery
        auth_plugin_name = 'password'
    LOG.debug("Auth plugin %s selected", auth_plugin_name)
    return auth_plugin_name


def build_auth_params(auth_plugin_name, cmd_options):
    if auth_plugin_name:
        LOG.debug('auth_type: %s', auth_plugin_name)
        auth_plugin_loader = base.get_plugin_loader(auth_plugin_name)
        auth_params = {
            opt.dest: opt.default
            for opt in base.get_plugin_options(auth_plugin_name)
        }
        auth_params.update(dict(cmd_options.auth))
        # grab tenant from project for v2.0 API compatibility
        if auth_plugin_name.startswith("v2"):
            if 'project_id' in auth_params:
                auth_params['tenant_id'] = auth_params['project_id']
                del auth_params['project_id']
            if 'project_name' in auth_params:
                auth_params['tenant_name'] = auth_params['project_name']
                del auth_params['project_name']
    else:
        LOG.debug('no auth_type')
        # delay the plugin choice, grab every option
        auth_plugin_loader = None
        auth_params = dict(cmd_options.auth)
        plugin_options = set(
            [o.replace('-', '_') for o in auth.get_options_list()]
        )
        for option in plugin_options:
            LOG.debug('fetching option %s', option)
            auth_params[option] = getattr(cmd_options.auth, option, None)
    return (auth_plugin_loader, auth_params)


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
        pw_func=None,
    ):
        super(ClientManager, self).__init__(
            cli_options=cli_options,
            api_version=api_version,
            pw_func=pw_func,
        )

        # TODO(dtroyer): For compatibility; mark this for removal when plugin
        #                interface v2 is removed
        self._region_name = self.region_name
        self._interface = self.interface
        self._cacert = self.cacert
        self._insecure = not self.verify

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
            ClientManager,
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
