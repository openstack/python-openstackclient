import logging

from novaclient import client as nova_client

LOG = logging.getLogger(__name__)


def make_client(instance):
    """Returns a compute service client.
    """
    LOG.debug('instantiating compute client')
    # FIXME(dhellmann): Where is the endpoint value used?
    # url = instance.get_endpoint_for_service_type('compute')
    client = nova_client.Client(
        version=instance._compute_api_version,
        username=instance._username,
        api_key=instance._password,
        project_id=instance._tenant_name,
        auth_url=instance._auth_url,
        # FIXME(dhellmann): add constructor argument for this
        insecure=False,
        region_name=instance._region_name,
        # FIXME(dhellmann): get endpoint_type from option?
        endpoint_type='publicURL',
        # FIXME(dhellmann): add extension discovery
        extensions=[],
        service_type='compute',
        # FIXME(dhellmann): what is service_name?
        service_name='',
        )
    client.authenticate()
    return client
