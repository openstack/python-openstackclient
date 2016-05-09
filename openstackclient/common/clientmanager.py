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

import copy
import logging
import pkg_resources
import sys

from oslo_utils import strutils
import requests
import six

from openstackclient.api import auth
from openstackclient.common import exceptions
from openstackclient.common import session as osc_session
from openstackclient.identity import client as identity_client


LOG = logging.getLogger(__name__)

PLUGIN_MODULES = []

USER_AGENT = 'python-openstackclient'


class ClientCache(object):
    """Descriptor class for caching created client handles."""

    def __init__(self, factory):
        self.factory = factory
        self._handle = None

    def __get__(self, instance, owner):
        # Tell the ClientManager to login to keystone
        if self._handle is None:
            try:
                self._handle = self.factory(instance)
            except AttributeError as err:
                # Make sure the failure propagates. Otherwise, the plugin just
                # quietly isn't there.
                new_err = exceptions.PluginAttributeError(err)
                six.reraise(new_err.__class__, new_err, sys.exc_info()[2])
        return self._handle


class ClientManager(object):
    """Manages access to API clients, including authentication."""

    # A simple incrementing version for the plugin to know what is available
    PLUGIN_INTERFACE_VERSION = "2"

    identity = ClientCache(identity_client.make_client)

    def __getattr__(self, name):
        # this is for the auth-related parameters.
        if name in ['_' + o.replace('-', '_')
                    for o in auth.OPTIONS_LIST]:
            return self._auth_params[name[1:]]

        raise AttributeError(name)

    def __init__(
        self,
        cli_options=None,
        api_version=None,
        verify=True,
        pw_func=None,
    ):
        """Set up a ClientManager

        :param cli_options:
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
            returns a string containing the password
        """

        self._cli_options = cli_options
        self._api_version = api_version
        self._pw_callback = pw_func
        self._url = self._cli_options.auth.get('url')
        self._region_name = self._cli_options.region_name
        self._interface = self._cli_options.interface

        self.timing = self._cli_options.timing

        self._auth_ref = None
        self.session = None

        # verify is the Requests-compatible form
        self._verify = verify
        # also store in the form used by the legacy client libs
        self._cacert = None
        if isinstance(verify, bool):
            self._insecure = not verify
        else:
            self._cacert = verify
            self._insecure = False

        # Set up client certificate and key
        # NOTE(cbrandily): This converts client certificate/key to requests
        #                  cert argument: None (no client certificate), a path
        #                  to client certificate or a tuple with client
        #                  certificate/key paths.
        self._cert = self._cli_options.cert
        if self._cert and self._cli_options.key:
            self._cert = self._cert, self._cli_options.key

        # Get logging from root logger
        root_logger = logging.getLogger('')
        LOG.setLevel(root_logger.getEffectiveLevel())

        # NOTE(gyee): use this flag to indicate whether auth setup has already
        # been completed. If so, do not perform auth setup again. The reason
        # we need this flag is that we want to be able to perform auth setup
        # outside of auth_ref as auth_ref itself is a property. We can not
        # retrofit auth_ref to optionally skip scope check. Some operations
        # do not require a scoped token. In those cases, we call setup_auth
        # prior to dereferrencing auth_ref.
        self._auth_setup_completed = False

    def setup_auth(self, required_scope=True):
        """Set up authentication

        :param required_scope: indicate whether a scoped token is required

        This is deferred until authentication is actually attempted because
        it gets in the way of things that do not require auth.
        """

        if self._auth_setup_completed:
            return

        # If no auth type is named by the user, select one based on
        # the supplied options
        self.auth_plugin_name = auth.select_auth_plugin(self._cli_options)

        # Basic option checking to avoid unhelpful error messages
        auth.check_valid_auth_options(self._cli_options,
                                      self.auth_plugin_name,
                                      required_scope=required_scope)

        # Horrible hack alert...must handle prompt for null password if
        # password auth is requested.
        if (self.auth_plugin_name.endswith('password') and
                not self._cli_options.auth.get('password')):
            self._cli_options.auth['password'] = self._pw_callback()

        (auth_plugin, self._auth_params) = auth.build_auth_params(
            self.auth_plugin_name,
            self._cli_options,
        )

        # TODO(mordred): This is a usability improvement that's broadly useful
        # We should port it back up into os-client-config.
        default_domain = self._cli_options.default_domain
        # NOTE(stevemar): If PROJECT_DOMAIN_ID or PROJECT_DOMAIN_NAME is
        # present, then do not change the behaviour. Otherwise, set the
        # PROJECT_DOMAIN_ID to 'OS_DEFAULT_DOMAIN' for better usability.
        if (self._api_version.get('identity') == '3' and
            self.auth_plugin_name.endswith('password') and
            not self._auth_params.get('project_domain_id') and
            not self.auth_plugin_name.startswith('v2') and
                not self._auth_params.get('project_domain_name')):
            self._auth_params['project_domain_id'] = default_domain

        # NOTE(stevemar): If USER_DOMAIN_ID or USER_DOMAIN_NAME is present,
        # then do not change the behaviour. Otherwise, set the USER_DOMAIN_ID
        # to 'OS_DEFAULT_DOMAIN' for better usability.
        if (self._api_version.get('identity') == '3' and
            self.auth_plugin_name.endswith('password') and
            not self.auth_plugin_name.startswith('v2') and
            not self._auth_params.get('user_domain_id') and
                not self._auth_params.get('user_domain_name')):
            self._auth_params['user_domain_id'] = default_domain

        # NOTE(hieulq): If USER_DOMAIN_NAME, USER_DOMAIN_ID, PROJECT_DOMAIN_ID
        # or PROJECT_DOMAIN_NAME is present and API_VERSION is 2.0, then
        # ignore all domain related configs.
        if (self._api_version.get('identity') == '2.0' and
                self.auth_plugin_name.endswith('password')):
            domain_props = ['project_domain_name', 'project_domain_id',
                            'user_domain_name', 'user_domain_id']
            for prop in domain_props:
                if self._auth_params.pop(prop, None) is not None:
                    LOG.warning("Ignoring domain related configs " +
                                prop + " because identity API version is 2.0")

        # For compatibility until all clients can be updated
        if 'project_name' in self._auth_params:
            self._project_name = self._auth_params['project_name']
        elif 'tenant_name' in self._auth_params:
            self._project_name = self._auth_params['tenant_name']

        LOG.info('Using auth plugin: %s', self.auth_plugin_name)
        LOG.debug('Using parameters %s',
                  strutils.mask_password(self._auth_params))
        self.auth = auth_plugin.load_from_options(**self._auth_params)
        # needed by SAML authentication
        request_session = requests.session()
        self.session = osc_session.TimingSession(
            auth=self.auth,
            session=request_session,
            verify=self._verify,
            cert=self._cert,
            user_agent=USER_AGENT,
        )

        self._auth_setup_completed = True

    @property
    def auth_ref(self):
        """Dereference will trigger an auth if it hasn't already"""
        if not self._auth_ref:
            self.setup_auth()
            LOG.debug("Get auth_ref")
            self._auth_ref = self.auth.get_auth_ref(self.session)
        return self._auth_ref

    def is_network_endpoint_enabled(self):
        """Check if the network endpoint is enabled"""
        # Trigger authentication necessary to determine if the network
        # endpoint is enabled.
        if self.auth_ref:
            service_catalog = self.auth_ref.service_catalog
        else:
            service_catalog = None
        # Assume that the network endpoint is enabled.
        network_endpoint_enabled = True
        if service_catalog:
            if 'network' in service_catalog.get_endpoints():
                LOG.debug("Network endpoint in service catalog")
            else:
                LOG.debug("No network endpoint in service catalog")
                network_endpoint_enabled = False
        else:
            LOG.debug("No service catalog, assuming network endpoint enabled")
        return network_endpoint_enabled

    def get_endpoint_for_service_type(self, service_type, region_name=None,
                                      interface='public'):
        """Return the endpoint URL for the service type."""
        if not interface:
            interface = 'public'
        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self.auth_ref:
            endpoint = self.auth_ref.service_catalog.url_for(
                service_type=service_type,
                region_name=region_name,
                endpoint_type=interface,
            )
        else:
            # Get the passed endpoint directly from the auth plugin
            endpoint = self.auth.get_endpoint(self.session,
                                              interface=interface)
        return endpoint

    def get_configuration(self):
        return copy.deepcopy(self._cli_options.config)


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
