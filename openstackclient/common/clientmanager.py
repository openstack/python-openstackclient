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

from keystoneclient.auth import base
from keystoneclient import session
import requests

from openstackclient.api import auth
from openstackclient.identity import client as identity_client


LOG = logging.getLogger(__name__)

PLUGIN_MODULES = []


class ClientCache(object):
    """Descriptor class for caching created client handles."""
    def __init__(self, factory):
        self.factory = factory
        self._handle = None

    def __get__(self, instance, owner):
        # Tell the ClientManager to login to keystone
        if self._handle is None:
            self._handle = self.factory(instance)
        return self._handle


class ClientManager(object):
    """Manages access to API clients, including authentication."""
    identity = ClientCache(identity_client.make_client)

    def __getattr__(self, name):
        # this is for the auth-related parameters.
        if name in ['_' + o.replace('-', '_')
                    for o in auth.OPTIONS_LIST]:
            return self._auth_params[name[1:]]

    def __init__(
        self,
        auth_options,
        api_version=None,
        verify=True,
        pw_func=None,
    ):
        """Set up a ClientManager

        :param auth_options:
            Options collected from the command-line, environment, or wherever
        :param api_version:
            Dict of API versions: key is API name, value is the version
        :param verify:
            TLS certificate verification; may be a boolean to enable or disable
            server certificate verification, or a filename of a CA certificate
            bundle to be used in verification (implies True)
        :param pw_func:
            Callback function for asking the user for a password.  The function
            takes an optional string for the prompt ('Password: ' on None) and
            returns a string containig the password
        """

        # If no plugin is named by the user, select one based on
        # the supplied options
        if not auth_options.os_auth_plugin:
            auth_options.os_auth_plugin = auth.select_auth_plugin(auth_options)
        self._auth_plugin = auth_options.os_auth_plugin

        # Horrible hack alert...must handle prompt for null password if
        # password auth is requested.
        if (self._auth_plugin.endswith('password') and
                not auth_options.os_password):
            auth_options.os_password = pw_func()

        self._url = auth_options.os_url
        self._auth_params = auth.build_auth_params(auth_options)
        self._region_name = auth_options.os_region_name
        self._api_version = api_version
        self._auth_ref = None
        self.timing = auth_options.timing

        # For compatibility until all clients can be updated
        if 'project_name' in self._auth_params:
            self._project_name = self._auth_params['project_name']
        elif 'tenant_name' in self._auth_params:
            self._project_name = self._auth_params['tenant_name']

        # verify is the Requests-compatible form
        self._verify = verify
        # also store in the form used by the legacy client libs
        self._cacert = None
        if isinstance(verify, bool):
            self._insecure = not verify
        else:
            self._cacert = verify
            self._insecure = False

        # Get logging from root logger
        root_logger = logging.getLogger('')
        LOG.setLevel(root_logger.getEffectiveLevel())

        LOG.debug('Using auth plugin: %s' % self._auth_plugin)
        auth_plugin = base.get_plugin_class(self._auth_plugin)
        self.auth = auth_plugin.load_from_options(**self._auth_params)
        # needed by SAML authentication
        request_session = requests.session()
        self.session = session.Session(
            auth=self.auth,
            session=request_session,
            verify=verify,
        )

        return

    @property
    def auth_ref(self):
        """Dereference will trigger an auth if it hasn't already"""
        if not self._auth_ref:
            LOG.debug("Get auth_ref")
            self._auth_ref = self.auth.get_auth_ref(self.session)
        return self._auth_ref

    def get_endpoint_for_service_type(self, service_type, region_name=None):
        """Return the endpoint URL for the service type."""
        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self.auth_ref:
            endpoint = self.auth_ref.service_catalog.url_for(
                service_type=service_type,
                region_name=region_name,
            )
        else:
            # Get the passed endpoint directly from the auth plugin
            endpoint = self.auth.get_endpoint(self.session)
        return endpoint


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
            ClientCache(
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
