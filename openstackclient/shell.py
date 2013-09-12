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

"""Command-line interface to the OpenStack APIs"""

import argparse
import getpass
import logging
import os
import sys

from cliff import app
from cliff import command
from cliff import help

import openstackclient
from openstackclient.common import clientmanager
from openstackclient.common import commandmanager
from openstackclient.common import exceptions as exc
from openstackclient.common import openstackkeyring
from openstackclient.common import restapi
from openstackclient.common import utils


KEYRING_SERVICE = 'openstack'

DEFAULT_COMPUTE_API_VERSION = '2'
DEFAULT_IDENTITY_API_VERSION = '2.0'
DEFAULT_IMAGE_API_VERSION = '1'
DEFAULT_OBJECT_API_VERSION = '1'
DEFAULT_VOLUME_API_VERSION = '1'
DEFAULT_DOMAIN = 'default'


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


class OpenStackShell(app.App):

    CONSOLE_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'

    log = logging.getLogger(__name__)

    def __init__(self):
        # Patch command.Command to add a default auth_required = True
        command.Command.auth_required = True
        # But not help
        help.HelpCommand.auth_required = False

        super(OpenStackShell, self).__init__(
            description=__doc__.strip(),
            version=openstackclient.__version__,
            command_manager=commandmanager.CommandManager('openstack.cli'))

        # This is instantiated in initialize_app() only when using
        # password flow auth
        self.auth_client = None

        # NOTE(dtroyer): This hack changes the help action that Cliff
        #                automatically adds to the parser so we can defer
        #                its execution until after the api-versioned commands
        #                have been loaded.  There doesn't seem to be a
        #                way to edit/remove anything from an existing parser.

        # Replace the cliff-added help.HelpAction to defer its execution
        self.DeferredHelpAction = None
        for a in self.parser._actions:
            if type(a) == help.HelpAction:
                # Found it, save and replace it
                self.DeferredHelpAction = a

                # These steps are argparse-implementation-dependent
                self.parser._actions.remove(a)
                if self.parser._option_string_actions['-h']:
                    del self.parser._option_string_actions['-h']
                if self.parser._option_string_actions['--help']:
                    del self.parser._option_string_actions['--help']

                # Make a new help option to just set a flag
                self.parser.add_argument(
                    '-h', '--help',
                    action='store_true',
                    dest='deferred_help',
                    default=False,
                    help="show this help message and exit",
                )

    def build_option_parser(self, description, version):
        parser = super(OpenStackShell, self).build_option_parser(
            description,
            version)

        # Global arguments
        parser.add_argument(
            '--os-auth-url',
            metavar='<auth-url>',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)')
        parser.add_argument(
            '--os-project-name',
            metavar='<auth-project-name>',
            default=env('OS_PROJECT_NAME', default=env('OS_TENANT_NAME')),
            help='Authentication project name (Env: OS_PROJECT_NAME)',
        )
        parser.add_argument(
            '--os-tenant-name',
            metavar='<auth-tenant-name>',
            dest='os_project_name',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--os-project-id',
            metavar='<auth-project-id>',
            default=env('OS_PROJECT_ID', default=env('OS_TENANT_ID')),
            help='Authentication project ID (Env: OS_PROJECT_ID)',
        )
        parser.add_argument(
            '--os-tenant-id',
            metavar='<auth-tenant-id>',
            dest='os_project_id',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--os-username',
            metavar='<auth-username>',
            default=utils.env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)')
        parser.add_argument(
            '--os-password',
            metavar='<auth-password>',
            default=utils.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)')
        parser.add_argument(
            '--os-region-name',
            metavar='<auth-region-name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')
        parser.add_argument(
            '--os-default-domain',
            metavar='<auth-domain>',
            default=env(
                'OS_DEFAULT_DOMAIN',
                default=DEFAULT_DOMAIN),
            help='Default domain ID, default=' +
                 DEFAULT_DOMAIN +
                 ' (Env: OS_DEFAULT_DOMAIN)')
        parser.add_argument(
            '--os-identity-api-version',
            metavar='<identity-api-version>',
            default=env(
                'OS_IDENTITY_API_VERSION',
                default=DEFAULT_IDENTITY_API_VERSION),
            help='Identity API version, default=' +
                 DEFAULT_IDENTITY_API_VERSION +
                 ' (Env: OS_IDENTITY_API_VERSION)')
        parser.add_argument(
            '--os-compute-api-version',
            metavar='<compute-api-version>',
            default=env(
                'OS_COMPUTE_API_VERSION',
                default=DEFAULT_COMPUTE_API_VERSION),
            help='Compute API version, default=' +
                 DEFAULT_COMPUTE_API_VERSION +
                 ' (Env: OS_COMPUTE_API_VERSION)')
        parser.add_argument(
            '--os-image-api-version',
            metavar='<image-api-version>',
            default=env(
                'OS_IMAGE_API_VERSION',
                default=DEFAULT_IMAGE_API_VERSION),
            help='Image API version, default=' +
                 DEFAULT_IMAGE_API_VERSION +
                 ' (Env: OS_IMAGE_API_VERSION)')
        parser.add_argument(
            '--os-object-api-version',
            metavar='<object-api-version>',
            default=env(
                'OS_OBJECT_API_VERSION',
                default=DEFAULT_OBJECT_API_VERSION),
            help='Object API version, default=' +
                 DEFAULT_OBJECT_API_VERSION +
                 ' (Env: OS_OBJECT_API_VERSION)')
        parser.add_argument(
            '--os-volume-api-version',
            metavar='<volume-api-version>',
            default=env(
                'OS_VOLUME_API_VERSION',
                default=DEFAULT_VOLUME_API_VERSION),
            help='Volume API version, default=' +
                 DEFAULT_VOLUME_API_VERSION +
                 ' (Env: OS_VOLUME_API_VERSION)')
        parser.add_argument(
            '--os-token',
            metavar='<token>',
            default=env('OS_TOKEN'),
            help='Defaults to env[OS_TOKEN]')
        parser.add_argument(
            '--os-url',
            metavar='<url>',
            default=env('OS_URL'),
            help='Defaults to env[OS_URL]')

        env_os_keyring = env('OS_USE_KEYRING', default=False)
        if type(env_os_keyring) == str:
            if env_os_keyring.lower() in ['true', '1']:
                env_os_keyring = True
            else:
                env_os_keyring = False
        parser.add_argument('--os-use-keyring',
                            default=env_os_keyring,
                            action='store_true',
                            help='Use keyring to store password, '
                                 'default=False (Env: OS_USE_KEYRING)')

        return parser

    def authenticate_user(self):
        """Make sure the user has provided all of the authentication
        info we need.
        """
        self.log.debug('validating authentication options')
        if self.options.os_token or self.options.os_url:
            # Token flow auth takes priority
            if not self.options.os_token:
                raise exc.CommandError(
                    "You must provide a token via"
                    " either --os-token or env[OS_TOKEN]")

            if not self.options.os_url:
                raise exc.CommandError(
                    "You must provide a service URL via"
                    " either --os-url or env[OS_URL]")

        else:
            # Validate password flow auth
            if not self.options.os_username:
                raise exc.CommandError(
                    "You must provide a username via"
                    " either --os-username or env[OS_USERNAME]")

            self.get_password_from_keyring()
            if not self.options.os_password:
                # No password, if we've got a tty, try prompting for it
                if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
                    # Check for Ctl-D
                    try:
                        self.options.os_password = getpass.getpass()
                        self.set_password_in_keyring()
                    except EOFError:
                        pass
                # No password because we did't have a tty or the
                # user Ctl-D when prompted?
                if not self.options.os_password:
                    raise exc.CommandError(
                        "You must provide a password via"
                        " either --os-password, or env[OS_PASSWORD], "
                        " or prompted response")

            if not (self.options.os_project_id
                    or self.options.os_project_name):
                raise exc.CommandError(
                    "You must provide a project id via"
                    " either --os-project-id or via env[OS_PROJECT_ID]")

            if not self.options.os_auth_url:
                raise exc.CommandError(
                    "You must provide an auth url via"
                    " either --os-auth-url or via env[OS_AUTH_URL]")

        self.client_manager = clientmanager.ClientManager(
            token=self.options.os_token,
            url=self.options.os_url,
            auth_url=self.options.os_auth_url,
            project_name=self.options.os_project_name,
            project_id=self.options.os_project_id,
            username=self.options.os_username,
            password=self.options.os_password,
            region_name=self.options.os_region_name,
            api_version=self.api_version)
        return

    def init_keyring_backend(self):
        """Initialize openstack backend to use for keyring"""
        return openstackkeyring.os_keyring()

    def get_password_from_keyring(self):
        """Get password from keyring, if it's set"""
        if self.options.os_use_keyring:
            service = KEYRING_SERVICE
            backend = self.init_keyring_backend()
            if not self.options.os_password:
                password = backend.get_password(service,
                                                self.options.os_username)
                self.options.os_password = password

    def set_password_in_keyring(self):
        """Set password in keyring for this user"""
        if self.options.os_use_keyring:
            service = KEYRING_SERVICE
            backend = self.init_keyring_backend()
            if self.options.os_password:
                password = backend.get_password(service,
                                                self.options.os_username)
                # either password is not set in keyring, or it is different
                if password != self.options.os_password:
                    backend.set_password(service,
                                         self.options.os_username,
                                         self.options.os_password)

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        * authenticate against Identity if requested
        """

        super(OpenStackShell, self).initialize_app(argv)

        # Set requests logging to a useful level
        requests_log = logging.getLogger("requests")
        if self.options.debug:
            requests_log.setLevel(logging.DEBUG)
        else:
            requests_log.setLevel(logging.WARNING)

        # Save default domain
        self.default_domain = self.options.os_default_domain

        # Stash selected API versions for later
        self.api_version = {
            'compute': self.options.os_compute_api_version,
            'identity': self.options.os_identity_api_version,
            'image': self.options.os_image_api_version,
            'object-store': self.options.os_object_api_version,
            'volume': self.options.os_volume_api_version,
        }

        # Add the API version-specific commands
        for api in self.api_version.keys():
            version = '.v' + self.api_version[api].replace('.', '_')
            cmd_group = 'openstack.' + api.replace('-', '_') + version
            self.command_manager.add_command_group(cmd_group)

        # Commands that span multiple APIs
        self.command_manager.add_command_group(
            'openstack.common')

        # This is the naive extension implementation referred to in
        # blueprint 'client-extensions'
        # Extension modules can register their commands in an
        # 'openstack.extension' entry point group:
        # entry_points={
        #     'openstack.extension': [
        #         'list_repo=qaz.github.repo:ListRepo',
        #         'show_repo=qaz.github.repo:ShowRepo',
        #     ],
        # }
        self.command_manager.add_command_group(
            'openstack.extension')

        # Handle deferred help and exit
        if self.options.deferred_help:
            self.DeferredHelpAction(self.parser, self.parser, None, None)

        # Set up common client session
        self.restapi = restapi.RESTApi()

    def prepare_to_run_command(self, cmd):
        """Set up auth and API versions"""
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

        if cmd.auth_required:
            self.authenticate_user()
            self.restapi.set_auth(self.client_manager.identity.auth_token)
        return

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

    def interact(self):
        # NOTE(dtroyer): Maintain the old behaviour for interactive use as
        #                this path does not call prepare_to_run_command()
        self.authenticate_user()
        self.restapi.set_auth(self.client_manager.identity.auth_token)
        super(OpenStackShell, self).interact()


def main(argv=sys.argv[1:]):
    try:
        return OpenStackShell().run(argv)
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
