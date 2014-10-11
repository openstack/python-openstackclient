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

    def __init__(self, auth_options, api_version=None, verify=True):

        if not auth_options.os_auth_plugin:
            auth._guess_authentication_method(auth_options)

        self._auth_plugin = auth_options.os_auth_plugin
        self._url = auth_options.os_url
        self._auth_params = auth.build_auth_params(auth_options)
        self._region_name = auth_options.os_region_name
        self._api_version = api_version
        self._service_catalog = None
        self.timing = auth_options.timing

        # For compatability until all clients can be updated
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

        self.session = None
        if not self._url:
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

        self.auth_ref = None
        if not self._auth_plugin.endswith("token") and not self._url:
            LOG.debug("Populate other password flow attributes")
            self.auth_ref = self.session.auth.get_auth_ref(self.session)
            self._token = self.session.auth.get_token(self.session)
            self._service_catalog = self.auth_ref.service_catalog
        else:
            self._token = self._auth_params.get('token')

        return

    def get_endpoint_for_service_type(self, service_type, region_name=None):
        """Return the endpoint URL for the service type."""
        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self._service_catalog:
            endpoint = self._service_catalog.url_for(
                service_type=service_type, region_name=region_name)
        else:
            # Hope we were given the correct URL.
            endpoint = self._auth_url or self._url
        return endpoint


def get_extension_modules(group):
    """Add extension clients"""
    mod_list = []
    for ep in pkg_resources.iter_entry_points(group):
        LOG.debug('found extension %r', ep.name)

        __import__(ep.module_name)
        module = sys.modules[ep.module_name]
        mod_list.append(module)
        init_func = getattr(module, 'Initialize', None)
        if init_func:
            init_func('x')

        setattr(
            ClientManager,
            module.API_NAME,
            ClientCache(
                getattr(sys.modules[ep.module_name], 'make_client', None)
            ),
        )
    return mod_list
