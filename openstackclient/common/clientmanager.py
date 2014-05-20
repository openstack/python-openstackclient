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

    def __init__(self, token=None, url=None, auth_url=None,
                 domain_id=None, domain_name=None,
                 project_name=None, project_id=None,
                 username=None, password=None,
                 user_domain_id=None, user_domain_name=None,
                 project_domain_id=None, project_domain_name=None,
                 region_name=None, api_version=None, verify=True):
        self._token = token
        self._url = url
        self._auth_url = auth_url
        self._domain_id = domain_id
        self._domain_name = domain_name
        self._project_name = project_name
        self._project_id = project_id
        self._username = username
        self._password = password
        self._user_domain_id = user_domain_id
        self._user_domain_name = user_domain_name
        self._project_domain_id = project_domain_id
        self._project_domain_name = project_domain_name
        self._region_name = region_name
        self._api_version = api_version
        self._service_catalog = None

        # verify is the Requests-compatible form
        self._verify = verify
        # also store in the form used by the legacy client libs
        self._cacert = None
        if verify is True or verify is False:
            self._insecure = not verify
        else:
            self._cacert = verify
            self._insecure = True

        self.auth_ref = None

        if not self._url:
            # Populate other password flow attributes
            self.auth_ref = self.identity.auth_ref
            self._token = self.identity.auth_token
            self._service_catalog = self.identity.service_catalog

        return

    def get_endpoint_for_service_type(self, service_type):
        """Return the endpoint URL for the service type."""
        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self._service_catalog:
            endpoint = self._service_catalog.url_for(
                service_type=service_type)
        else:
            # Hope we were given the correct URL.
            endpoint = self._url
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
            ep.name,
            ClientCache(
                getattr(sys.modules[ep.module_name], 'make_client', None)
            ),
        )
    return mod_list
