#   Copyright 2013 Nebula Inc.
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

"""Object client"""

import logging

from openstackclient.common import utils

LOG = logging.getLogger(__name__)

API_NAME = 'object-store'
API_VERSIONS = {
    '1': 'openstackclient.object.client.ObjectClientv1',
}


def make_client(instance):
    """Returns an object service client."""
    object_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    if instance._url:
        endpoint = instance._url
    else:
        endpoint = instance.get_endpoint_for_service_type(API_NAME)
    LOG.debug('instantiating object client')
    client = object_client(
        endpoint=endpoint,
        token=instance._token,
    )
    return client


class ObjectClientv1(object):

    def __init__(
        self,
        endpoint_type='publicURL',
        endpoint=None,
        token=None,
    ):
        self.endpoint_type = endpoint_type
        self.endpoint = endpoint
        self.token = token
