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

from openstack import connection
from openstack import profile
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2.0'
API_VERSION_OPTION = 'os_network_api_version'
API_NAME = "network"
API_VERSIONS = {
    "2.0": "openstack.connection.Connection",
    "2": "openstack.connection.Connection",
}


def make_client(instance):
    """Returns a network proxy"""
    prof = profile.Profile()
    prof.set_region(API_NAME, instance.region_name)
    prof.set_version(API_NAME, instance._api_version[API_NAME])
    prof.set_interface(API_NAME, instance.interface)
    conn = connection.Connection(authenticator=instance.session.auth,
                                 verify=instance.session.verify,
                                 cert=instance.session.cert,
                                 profile=prof)
    LOG.debug('Connection: %s', conn)
    LOG.debug('Network client initialized using OpenStack SDK: %s',
              conn.network)
    return conn.network


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-network-api-version',
        metavar='<network-api-version>',
        default=utils.env('OS_NETWORK_API_VERSION'),
        help=_("Network API version, default=%s "
               "(Env: OS_NETWORK_API_VERSION)") % DEFAULT_API_VERSION
    )
    return parser
