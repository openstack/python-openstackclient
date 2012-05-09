import logging

from keystoneclient.v2_0 import client as identity_client

LOG = logging.getLogger(__name__)


def make_client(instance):
    """Returns an identity service client.
    """
    if instance._url:
        LOG.debug('instantiating identity client: token flow')
        client = identity_client.Client(
            endpoint=instance._url,
            token=instance._token,
        )
    else:
        LOG.debug('instantiating identity client: password flow')
        client = identity_client.Client(
            username=instance._username,
            password=instance._password,
            tenant_name=instance._tenant_name,
            tenant_id=instance._tenant_id,
            auth_url=instance._auth_url,
            region_name=instance._region_name,
        )
    return client
