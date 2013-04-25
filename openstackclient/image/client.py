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

API_NAME = "image"
API_VERSIONS = {
    "1": "glanceclient.v1.client.Client",
    "2": "glanceclient.v2.client.Client"
}


def make_client(instance):
    """Returns an image service client."""
    image_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)

    if not instance._url:
        instance._url = instance.get_endpoint_for_service_type(API_NAME)

    return image_client(instance._url, token=instance._token)
