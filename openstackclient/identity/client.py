#   Copyright 2012-2013 OpenStack, LLC.
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

import logging

from openstackclient.common import utils

LOG = logging.getLogger(__name__)

API_NAME = 'identity'
API_VERSIONS = {
    '2.0': 'keystoneclient.v2_0.client.Client',
    '3': 'keystoneclient.v3.client.Client',
}


def make_client(instance):
    """Returns an identity service client.
    """
    identity_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS,
    )
    if instance._url:
        LOG.debug('instantiating identity client: token flow')
        client = identity_client(
            endpoint=instance._url,
            token=instance._token,
        )
    else:
        LOG.debug('instantiating identity client: password flow')
        client = identity_client(
            username=instance._username,
            password=instance._password,
            tenant_name=instance._tenant_name,
            tenant_id=instance._tenant_id,
            auth_url=instance._auth_url,
            region_name=instance._region_name,
        )
    return client
