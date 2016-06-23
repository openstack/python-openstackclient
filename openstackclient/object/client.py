#   Copyright 2013 Nebula Inc.
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

"""Object client"""

from osc_lib import utils

from openstackclient.api import object_store_v1

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_object_api_version'
API_NAME = 'object_store'
API_VERSIONS = {
    '1': 'openstackclient.object.client.ObjectClientv1',
}


def make_client(instance):
    """Returns an object-store API client."""

    endpoint = instance.get_endpoint_for_service_type(
        'object-store',
        region_name=instance.region_name,
        interface=instance.interface,
    )

    client = object_store_v1.APIv1(
        session=instance.session,
        service_type='object-store',
        endpoint=endpoint,
    )
    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-object-api-version',
        metavar='<object-api-version>',
        default=utils.env('OS_OBJECT_API_VERSION'),
        help='Object API version, default=' +
             DEFAULT_API_VERSION +
             ' (Env: OS_OBJECT_API_VERSION)')
    return parser
