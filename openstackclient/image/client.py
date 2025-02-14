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
DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_image_api_version'
API_NAME = 'image'
API_VERSIONS = ('1', '2')


def make_client(instance):
    """Returns an image service client."""
    LOG.debug(
        'Image client initialized using OpenStack SDK: %s',
        instance.sdk_connection.image,
    )
    return instance.sdk_connection.image


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-image-api-version',
        metavar='<image-api-version>',
        default=utils.env('OS_IMAGE_API_VERSION'),
        help=_('Image API version, default=%s (Env: OS_IMAGE_API_VERSION)')
        % DEFAULT_API_VERSION,
    )
    return parser
