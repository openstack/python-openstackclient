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

DEFAULT_NETWORK_API_VERSION = '2'
API_VERSION_OPTION = 'os_network_api_version'
API_NAME = "network"
API_VERSIONS = {
    "2": "neutronclient.v2_0.client.Client",
}


def make_client(instance):
    """Returns an network service client."""
    network_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating network client: %s', network_client)

    if not instance._url:
        instance._url = instance.get_endpoint_for_service_type(
            "network", region_name=instance._region_name)
    return network_client(
        username=instance._username,
        tenant_name=instance._project_name,
        password=instance._password,
        region_name=instance._region_name,
        auth_url=instance._auth_url,
        endpoint_url=instance._url,
        token=instance.auth.get_token(instance.session),
        insecure=instance._insecure,
        ca_cert=instance._cacert,
    )


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-network-api-version',
        metavar='<network-api-version>',
        default=utils.env(
            'OS_NETWORK_API_VERSION',
            default=DEFAULT_NETWORK_API_VERSION),
        help='Network API version, default=' +
             DEFAULT_NETWORK_API_VERSION +
             ' (Env: OS_NETWORK_API_VERSION)')
    return parser
