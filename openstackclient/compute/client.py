# Copyright 2012 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import logging

from novaclient import client as nova_client

LOG = logging.getLogger(__name__)


def make_client(instance):
    """Returns a compute service client.
    """
    LOG.debug('instantiating compute client')
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

    # Populate the Nova client to skip another auth query to Identity
    if instance._url:
        # token flow
        client.client.management_url = instance._url
    else:
        # password flow
        client.client.management_url = instance.get_endpoint_for_service_type(
            'compute')
        client.client.service_catalog = instance._service_catalog
    client.client.auth_token = instance._token
    return client
