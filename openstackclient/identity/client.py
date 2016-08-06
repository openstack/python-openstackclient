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

from keystoneclient.v2_0 import client as identity_client_v2
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '3'
API_VERSION_OPTION = 'os_identity_api_version'
API_NAME = 'identity'
API_VERSIONS = {
    '2.0': 'openstackclient.identity.client.IdentityClientv2',
    '2': 'openstackclient.identity.client.IdentityClientv2',
    '3': 'keystoneclient.v3.client.Client',
}

# Translate our API version to auth plugin version prefix
AUTH_VERSIONS = {
    '2.0': 'v2',
    '2': 'v2',
    '3': 'v3',
}


def make_client(instance):
    """Returns an identity service client."""
    identity_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating identity client: %s', identity_client)

    # Remember interface only if interface is set
    kwargs = utils.build_kwargs_dict('interface', instance.interface)

    client = identity_client(
        session=instance.session,
        region_name=instance.region_name,
        **kwargs
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-identity-api-version',
        metavar='<identity-api-version>',
        default=utils.env('OS_IDENTITY_API_VERSION'),
        help=_('Identity API version, default=%s '
               '(Env: OS_IDENTITY_API_VERSION)') % DEFAULT_API_VERSION,
    )
    return parser


class IdentityClientv2(identity_client_v2.Client):
    """Tweak the earlier client class to deal with some changes"""

    def __getattr__(self, name):
        # Map v3 'projects' back to v2 'tenants'
        if name == "projects":
            return self.tenants
        else:
            raise AttributeError(name)
