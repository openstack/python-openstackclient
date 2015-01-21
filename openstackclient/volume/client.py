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

from cinderclient import extension
from cinderclient.v1.contrib import list_extensions
from cinderclient.v1 import volume_snapshots
from cinderclient.v1 import volumes

from openstackclient.common import utils

# Monkey patch for v1 cinderclient
volumes.Volume.NAME_ATTR = 'display_name'
volume_snapshots.Snapshot.NAME_ATTR = 'display_name'

LOG = logging.getLogger(__name__)

DEFAULT_VOLUME_API_VERSION = '1'
API_VERSION_OPTION = 'os_volume_api_version'
API_NAME = "volume"
API_VERSIONS = {
    "1": "cinderclient.v1.client.Client"
}


def make_client(instance):
    """Returns a volume service client."""
    volume_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS
    )
    LOG.debug('Instantiating volume client: %s', volume_client)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    extensions = [extension.Extension('list_extensions', list_extensions)]

    client = volume_client(
        session=instance.session,
        extensions=extensions,
        http_log_debug=http_log_debug,
        region_name=instance._region_name,
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-volume-api-version',
        metavar='<volume-api-version>',
        default=utils.env(
            'OS_VOLUME_API_VERSION',
            default=DEFAULT_VOLUME_API_VERSION),
        help='Volume API version, default=' +
             DEFAULT_VOLUME_API_VERSION +
             ' (Env: OS_VOLUME_API_VERSION)')
    return parser
