# Copyright 2011 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Command-line interface to the OpenStack APIs
"""

import argparse
import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from keystoneclient.v2_0 import client as ksclient

from openstackclient.common import exceptions as exc
from openstackclient.common import utils


VERSION = '0.1'


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


class OpenStackShell(App):

    CONSOLE_MESSAGE_FORMAT = '%(levelname)s: %(message)s'

    log = logging.getLogger(__name__)

    def __init__(self):
        super(OpenStackShell, self).__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=CommandManager('openstack.cli'),
            )

        # This is instantiated in initialize_app() only when using
        # password flow auth
        self.auth_client = None

    def build_option_parser(self, description, version):
        parser = super(OpenStackShell, self).build_option_parser(
            description,
            version,
            )

        # Global arguments
        parser.add_argument('--os-auth-url', metavar='<auth-url>',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)')

        parser.add_argument('--os-tenant-name', metavar='<auth-tenant-name>',
            default=env('OS_TENANT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)')

        parser.add_argument('--os-tenant-id', metavar='<auth-tenant-id>',
            default=env('OS_TENANT_ID'),
            help='Authentication tenant ID (Env: OS_TENANT_ID)')

        parser.add_argument('--os-username', metavar='<auth-username>',
            default=utils.env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)')

        parser.add_argument('--os-password', metavar='<auth-password>',
            default=utils.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)')

        parser.add_argument('--os-region-name', metavar='<auth-region-name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')

        parser.add_argument('--os-identity-api-version',
            metavar='<identity-api-version>',
            default=env('OS_IDENTITY_API_VERSION', default='2.0'),
            help='Identity API version, default=2.0 '\
                                '(Env: OS_IDENTITY_API_VERSION)')

        parser.add_argument('--os-compute-api-version',
            metavar='<compute-api-version>',
            default=env('OS_COMPUTE_API_VERSION', default='2'),
            help='Compute API version, default=2 '\
                                '(Env: OS_COMPUTE_API_VERSION)')

        parser.add_argument('--os-image-api-version',
            metavar='<image-api-version>',
            default=env('OS_IMAGE_API_VERSION', default='1.0'),
            help='Image API version, default=1.0 '\
                                '(Env: OS_IMAGE_API_VERSION)')

        parser.add_argument('--os-token', metavar='<token>',
            default=env('OS_TOKEN'),
            help='Defaults to env[OS_TOKEN]')

        parser.add_argument('--os-url', metavar='<url>',
            default=env('OS_URL'),
            help='Defaults to env[OS_URL]')

        return parser

    def initialize_app(self):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        * authenticate against Identity if requested
        """

        super(OpenStackShell, self).initialize_app()

        # stash selected API versions for later
        # TODO(dtroyer): how do extenstions add their version requirements?
        self.api_version = {
            'compute': self.options.os_compute_api_version,
            'identity': self.options.os_identity_api_version,
            'image': self.options.os_image_api_version,
        }

        self.log.debug("API: Identity=%s Compute=%s Image=%s" % (
            self.api_version['identity'],
            self.api_version['compute'],
            self.api_version['image'])
        )

        # do checking of os_username, etc here
        if (self.options.os_token and self.options.os_url):
            # do token auth
            self.endpoint = self.options.os_url
            self.token = self.options.os_token
        else:
            if not self.options.os_username:
                raise exc.CommandError("You must provide a username via"
                        " either --os-username or env[OS_USERNAME]")

            if not self.options.os_password:
                raise exc.CommandError("You must provide a password via"
                        " either --os-password or env[OS_PASSWORD]")

            if not (self.options.os_tenant_id or self.options.os_tenant_name):
                raise exc.CommandError("You must provide a tenant_id via"
                        " either --os-tenant-id or via env[OS_TENANT_ID]")

            if not self.options.os_auth_url:
                raise exc.CommandError("You must provide an auth url via"
                        " either --os-auth-url or via env[OS_AUTH_URL]")
            kwargs = {
                'username': self.options.os_username,
                'password': self.options.os_password,
                'tenant_id': self.options.os_tenant_id,
                'tenant_name': self.options.os_tenant_name,
                'auth_url': self.options.os_auth_url
            }
            self.auth_client = ksclient.Client(
                username=kwargs.get('username'),
                password=kwargs.get('password'),
                tenant_id=kwargs.get('tenant_id'),
                tenant_name=kwargs.get('tenant_name'),
                auth_url=kwargs.get('auth_url'),
            )
            self.token = self.auth_client.auth_token
            # Since we don't know which command is being executed yet, defer
            # selection of a service API until later
            self.endpoint = None

        self.log.debug("token: %s" % self.token)
        self.log.debug("endpoint: %s" % self.endpoint)

    def prepare_to_run_command(self, cmd):
        """Set up auth and API versions"""
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

        self.log.debug("api: %s" % cmd.api)

        # See if we are using password flow auth, i.e. we have a
        # service catalog to select endpoints from
        if self.auth_client and self.auth_client.service_catalog:
            self.endpoint = self.auth_client.service_catalog.url_for(
                service_type=cmd.api)

        # self.endpoint == None here is an error...
        if not self.endpoint:
            raise RuntimeError('no endpoint found')

        # get a client for the desired api here

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    return OpenStackShell().run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
