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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from manilaclient import client

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

# global variables used when building the shell
DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_share_api_version'
API_NAME = 'share'

# Save the microversion if in use
_share_api_version = None


def make_client(instance: Any) -> 'client.Client':
    """Returns a manilaclient.client.Client instance."""
    from manilaclient import api_versions
    from manilaclient import client

    check_version = instance._api_version[API_NAME]
    if check_version.isdigit():
        check_version = f"{check_version}.0"

    version = api_versions.get_api_version(check_version)

    instance.setup_auth()

    LOG.debug('Instantiating Shared File System client: %s', client.Client)
    LOG.debug('Shared File System API version: %s', version)

    return client.Client(
        version,
        session=instance.session,
        endpoint_type=instance.interface,
        region_name=instance.region_name,
        auth=instance.auth,
        cacert=instance.cacert,
        cert=instance.cert,
        insecure=not instance.verify,
    )


def build_option_parser(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Hook to add global options"""
    parser.add_argument(
        '--os-share-api-version',
        metavar='<share-api-version>',
        default=utils.env('OS_SHARE_API_VERSION'),
        help=_(
            "Shared File System API version, default=%s "
            "(Env: OS_SHARE_API_VERSION)"
        )
        % DEFAULT_API_VERSION,
    )
    return parser


def check_api_version(check_version: str) -> bool:
    # Defer client imports until we actually need them
    from manilaclient import api_versions

    global _share_api_version

    # TODO(stephenfin): Other clients (novaclient, cinderclient, ...) do this
    # normalization for us
    if check_version.isdigit():
        check_version = f"{check_version}.0"

    _share_api_version = api_versions.get_api_version(check_version)

    # Bypass X.latest format microversion
    if not _share_api_version.is_latest():
        if _share_api_version > api_versions.APIVersion("2.0"):
            if not _share_api_version.matches(
                api_versions.MIN_VERSION,
                api_versions.MAX_VERSION,
            ):
                msg = _("versions supported by client: %(min)s - %(max)s") % {
                    "min": api_versions.MIN_VERSION,
                    "max": api_versions.MAX_VERSION,
                }
                raise exceptions.CommandError(msg)

            return True

    return False
