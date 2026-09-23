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

import argparse
import logging
from typing import Any

from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_accelerator_api_version'
API_NAME = 'accelerator'
API_VERSIONS = ('2',)


def make_client(instance: Any) -> Any:
    """Returns an accelerator proxy"""
    LOG.debug(
        'Accelerator client initialized using OpenStack SDK: %s',
        instance.sdk_connection.accelerator,
    )
    return instance.sdk_connection.accelerator


def build_option_parser(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Hook to add global options"""
    parser.add_argument(
        '--os-accelerator-api-version',
        metavar='<accelerator-api-version>',
        default=utils.env('OS_ACCELERATOR_API_VERSION'),
        help=_(
            "Accelerator API version, default=%s "
            "(Env: OS_ACCELERATOR_API_VERSION)"
        )
        % DEFAULT_API_VERSION,
    )
    return parser


def check_api_version(check_version: str) -> bool:
    # SDK supports auto-negotiation for us: always return True
    return True
