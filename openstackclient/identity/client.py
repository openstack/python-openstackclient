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
