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

import argparse
import logging

from osc_lib import utils

from openstackclient.common import clientmanager
from openstackclient.i18n import _
from openstackclient.placement import api

LOG = logging.getLogger(__name__)

# global variables used when building the shell
DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_placement_api_version'
API_NAME = 'placement'
API_VERSIONS = ('1',)


def make_client(instance: clientmanager.ClientManager) -> api.SessionClient:
    """Returns a placement service client."""
    LOG.debug('Instantiating placement client: %s', api.SessionClient)
    return api.SessionClient(
        session=instance.session,
        ks_filter={
            'service_type': API_NAME,
            'region_name': instance._region_name,
            'interface': instance.interface,
        },
        api_version=instance._api_version[API_NAME],
    )


def build_option_parser(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Hook to add global options"""
    parser.add_argument(
        '--os-placement-api-version',
        metavar='<placement-api-version>',
        default=utils.env('OS_PLACEMENT_API_VERSION'),
        help=_(
            "Placement API version, default=%s (Env: OS_PLACEMENT_API_VERSION)"
        )
        % DEFAULT_API_VERSION,
    )
    return parser


def check_api_version(check_version: str) -> bool:
    # SDK supports auto-negotiation for us: always return True
    return True
