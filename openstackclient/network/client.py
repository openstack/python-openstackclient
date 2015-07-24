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

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_network_api_version'
API_NAME = "network"
API_VERSIONS = {
    "2": "neutronclient.v2_0.client.Client",
}
# Translate our API version to auth plugin version prefix
API_VERSION_MAP = {
    '2.0': 'v2.0',
    '2': 'v2.0',
}

NETWORK_API_TYPE = 'network'
NETWORK_API_VERSIONS = {
    '2': 'openstackclient.api.network_v2.APIv2',
}


def make_client(instance):
    """Returns an network service client"""
    network_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating network client: %s', network_client)

    endpoint = instance.get_endpoint_for_service_type(
        API_NAME,
        region_name=instance._region_name,
        interface=instance._interface,
    )

    # Remember endpoint_type only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = network_client(
        session=instance.session,
        region_name=instance._region_name,
        **kwargs
    )

    network_api = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        NETWORK_API_VERSIONS)
    LOG.debug('Instantiating network api: %s', network_client)

    # v2 is hard-coded until discovery is completed, neutron only has one atm
    client.api = network_api(
        session=instance.session,
        service_type=NETWORK_API_TYPE,
        endpoint='/'.join([
            endpoint,
            API_VERSION_MAP[instance._api_version[API_NAME]],
        ])
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-network-api-version',
        metavar='<network-api-version>',
        default=utils.env('OS_NETWORK_API_VERSION'),
        help='Network API version, default=' +
             DEFAULT_API_VERSION +
             ' (Env: OS_NETWORK_API_VERSION)')
    return parser
