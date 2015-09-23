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

from openstackclient.common import exceptions
from openstackclient.common import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2'
API_VERSION_OPTION = 'os_compute_api_version'
API_NAME = 'compute'
API_VERSIONS = {
    "2": "novaclient.client",
}

# Save the microversion if in use
_compute_api_version = None


def make_client(instance):
    """Returns a compute service client."""

    # Defer client import until we actually need them
    from novaclient import client as nova_client

    if _compute_api_version is not None:
        version = _compute_api_version
    else:
        version = instance._api_version[API_NAME]

    LOG.debug('Instantiating compute client for V%s' % version)

    # Set client http_log_debug to True if verbosity level is high enough
    http_log_debug = utils.get_effective_log_level() <= logging.DEBUG

    extensions = [ext for ext in nova_client.discover_extensions(version)
                  if ext.name == "list_extensions"]

    # Remember interface only if it is set
    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = nova_client.Client(
        version,
        session=instance.session,
        extensions=extensions,
        http_log_debug=http_log_debug,
        timings=instance.timing,
        region_name=instance._region_name,
        **kwargs
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-compute-api-version',
        metavar='<compute-api-version>',
        default=utils.env('OS_COMPUTE_API_VERSION'),
        help='Compute API version, default=' +
             DEFAULT_API_VERSION +
             ' (Env: OS_COMPUTE_API_VERSION)')
    return parser


def check_api_version(check_version):
    """Validate version supplied by user

    Returns:
    * True if version is OK
    * False if the version has not been checked and the previous plugin
      check should be performed
    * throws an exception if the version is no good

    TODO(dtroyer): make the exception thrown a version-related one
    """

    # Defer client imports until we actually need them
    try:
        from novaclient import api_versions
    except ImportError:
        # Retain previous behaviour
        return False

    import novaclient

    global _compute_api_version

    # Copy some logic from novaclient 2.27.0 for basic version detection
    # NOTE(dtroyer): This is only enough to resume operations using API
    #                version 2.0 or any valid version supplied by the user.
    _compute_api_version = api_versions.get_api_version(check_version)

    if _compute_api_version > api_versions.APIVersion("2.0"):
        if not _compute_api_version.matches(
            novaclient.API_MIN_VERSION,
            novaclient.API_MAX_VERSION,
        ):
            raise exceptions.CommandError(
                "versions supported by client: %s - %s" % (
                    novaclient.API_MIN_VERSION.get_string(),
                    novaclient.API_MAX_VERSION.get_string(),
                ),
            )
    return True
