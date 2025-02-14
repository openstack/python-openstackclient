#   Copyright 2012-2013 OpenStack Foundation
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

import logging

from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

# global variables used when building the shell
DEFAULT_API_VERSION = '2.1'
API_VERSION_OPTION = 'os_compute_api_version'
API_NAME = 'compute'
API_VERSIONS = ('2', '2.1')


def make_client(instance):
    """Returns a compute service client."""
    LOG.debug(
        'Compute client initialized using OpenStack SDK: %s',
        instance.sdk_connection.compute,
    )
    return instance.sdk_connection.compute


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-compute-api-version',
        metavar='<compute-api-version>',
        default=utils.env('OS_COMPUTE_API_VERSION'),
        help=_("Compute API version, default=%s (Env: OS_COMPUTE_API_VERSION)")
        % DEFAULT_API_VERSION,
    )
    return parser
