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

from openstackclient.compute import client as compute_client
from openstackclient.identity import client as identity_client
from openstackclient.image import client as image_client
from openstackclient.object import client as object_client
from openstackclient.volume import client as volume_client


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
    compute = ClientCache(compute_client.make_client)
    identity = ClientCache(identity_client.make_client)
    image = ClientCache(image_client.make_client)
    object = ClientCache(object_client.make_client)
    volume = ClientCache(volume_client.make_client)

    def __init__(self, token=None, url=None, auth_url=None, project_name=None,
                 project_id=None, username=None, password=None,
                 region_name=None, api_version=None):
        self._token = token
        self._url = url
        self._auth_url = auth_url
        self._project_name = project_name
        self._project_id = project_id
        self._username = username
        self._password = password
        self._region_name = region_name
        self._api_version = api_version
        self._service_catalog = None

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
