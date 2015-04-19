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

DEFAULT_COMPUTE_API_VERSION = '2'
API_VERSION_OPTION = 'os_compute_api_version'
API_NAME = 'compute'
API_VERSIONS = {
    "2": "novaclient.client",
}


def make_client(instance):
    """Returns a compute service client."""

    # Defer client imports until we actually need them
    from novaclient import client as nova_client
    from novaclient import extension
    try:
        from novaclient.v2.contrib import list_extensions
    except ImportError:
        from novaclient.v1_1.contrib import list_extensions

    compute_client = nova_client.get_client_class(
        instance._api_version[API_NAME],
    )
    LOG.debug('Instantiating compute client: %s', compute_client)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    extensions = [extension.Extension('list_extensions', list_extensions)]

    client = compute_client(
        session=instance.session,
        extensions=extensions,
        http_log_debug=http_log_debug,
        timings=instance.timing,
        region_name=instance._region_name,
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-compute-api-version',
        metavar='<compute-api-version>',
        default=utils.env(
            'OS_COMPUTE_API_VERSION',
            default=DEFAULT_COMPUTE_API_VERSION),
        help='Compute API version, default=' +
             DEFAULT_COMPUTE_API_VERSION +
             ' (Env: OS_COMPUTE_API_VERSION)')
    return parser
