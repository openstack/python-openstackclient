"""Manage access to the clients, including authenticating when needed.
"""

import logging

from openstackclient.common import exceptions as exc
from openstackclient.compute import client as compute_client

from keystoneclient.v2_0 import client as keystone_client

LOG = logging.getLogger(__name__)


class ClientCache(object):
    """Descriptor class for caching created client handles.
    """

    def __init__(self, factory):
        self.factory = factory
        self._handle = None

    def __get__(self, instance, owner):
        # Tell the ClientManager to login to keystone
        if self._handle is None:
            instance.init_token()
            self._handle = self.factory(instance)
        return self._handle


class ClientManager(object):
    """Manages access to API clients, including authentication.
    """

    compute = ClientCache(compute_client.make_client)

    def __init__(self, token=None, url=None,
                 auth_url=None,
                 tenant_name=None, tenant_id=None,
                 username=None, password=None,
                 region_name=None,
                 identity_api_version=None,
                 compute_api_version=None,
                 image_api_version=None,
                 ):
        self._token = token
        self._url = url
        self._auth_url = auth_url
        self._tenant_name = tenant_name
        self._tenant_id = tenant_id
        self._username = username
        self._password = password
        self._region_name = region_name
        self._identity_api_version = identity_api_version
        self._compute_api_version = compute_api_version
        self._image_api_version = image_api_version

    def init_token(self):
        """Return the auth token and endpoint.
        """
        if self._token:
            LOG.debug('using existing auth token')
            return

        LOG.debug('validating authentication options')
        if not self._username:
            raise exc.CommandError(
                "You must provide a username via"
                " either --os-username or env[OS_USERNAME]")

        if not self._password:
            raise exc.CommandError(
                "You must provide a password via"
                " either --os-password or env[OS_PASSWORD]")

        if not (self._tenant_id or self._tenant_name):
            raise exc.CommandError(
                "You must provide a tenant_id via"
                " either --os-tenant-id or via env[OS_TENANT_ID]")

        if not self._auth_url:
            raise exc.CommandError(
                "You must provide an auth url via"
                " either --os-auth-url or via env[OS_AUTH_URL]")

        kwargs = {
            'username': self._username,
            'password': self._password,
            'tenant_id': self._tenant_id,
            'tenant_name': self._tenant_name,
            'auth_url': self._auth_url
        }
        self._auth_client = keystone_client.Client(**kwargs)
        self._token = self._auth_client.auth_token
        return

    def get_endpoint_for_service_type(self, service_type):
        """Return the endpoint URL for the service type.
        """
        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self._auth_client and self._auth_client.service_catalog:
            endpoint = self._auth_client.service_catalog.url_for(
                service_type=service_type)
        else:
            # Hope we were given the correct URL.
            endpoint = self._url
        return endpoint
