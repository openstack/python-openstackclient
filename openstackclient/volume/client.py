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
#

import logging

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '3'
API_VERSION_OPTION = 'os_volume_api_version'
API_NAME = "volume"
API_VERSIONS = {
    "1": "cinderclient.v1.client.Client",
    "2": "cinderclient.v2.client.Client",
    "3": "cinderclient.v3.client.Client",
}

# Save the microversion if in use
_volume_api_version = None


def make_client(instance):
    """Returns a volume service client."""

    # Defer client imports until we actually need them
    from cinderclient import extension
    from cinderclient.v3.contrib import list_extensions
    from cinderclient.v3 import volume_snapshots
    from cinderclient.v3 import volumes

    # Check whether the available cinderclient supports v1 or v2
    try:
        from cinderclient.v1 import services  # noqa
    except Exception:
        del API_VERSIONS['1']
    try:
        from cinderclient.v2 import services  # noqa
    except Exception:
        del API_VERSIONS['2']

    if _volume_api_version is not None:
        version = _volume_api_version
    else:
        version = instance._api_version[API_NAME]
        from cinderclient import api_versions

        # convert to APIVersion object
        version = api_versions.get_api_version(version)

    if version.ver_major == '1':
        # Monkey patch for v1 cinderclient
        volumes.Volume.NAME_ATTR = 'display_name'
        volume_snapshots.Snapshot.NAME_ATTR = 'display_name'

    volume_client = utils.get_client_class(
        API_NAME, version.ver_major, API_VERSIONS
    )
    LOG.debug('Instantiating volume client: %s', volume_client)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    extensions = [extension.Extension('list_extensions', list_extensions)]

    # Remember interface only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance.interface)

    endpoint_override = instance.sdk_connection.config.get_endpoint(
        'block-storage'
    )

    client = volume_client(
        session=instance.session,
        extensions=extensions,
        http_log_debug=http_log_debug,
        region_name=instance.region_name,
        endpoint_override=endpoint_override,
        api_version=version,
        **kwargs,
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-volume-api-version',
        metavar='<volume-api-version>',
        default=utils.env('OS_VOLUME_API_VERSION'),
        help=_('Volume API version, default=%s (Env: OS_VOLUME_API_VERSION)')
        % DEFAULT_API_VERSION,
    )
    return parser


def check_api_version(check_version):
    """Validate version supplied by user

    Returns:

    * True if version is OK
    * False if the version has not been checked and the previous plugin
      check should be performed
    * throws an exception if the version is no good
    """

    # Defer client imports until we actually need them
    from cinderclient import api_versions

    global _volume_api_version

    # Copy some logic from novaclient 3.3.0 for basic version detection
    # NOTE(dtroyer): This is only enough to resume operations using API
    # version 3.0 or any valid version supplied by the user.
    _volume_api_version = api_versions.get_api_version(check_version)

    # Bypass X.latest format microversion
    if not _volume_api_version.is_latest():
        if _volume_api_version > api_versions.APIVersion("3.0"):
            if not _volume_api_version.matches(
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
