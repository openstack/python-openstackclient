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
import traceback

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
from openstackclient.identity import client as identity_client


KEYRING_SERVICE = 'openstack'

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

        # Until we have command line arguments parsed, dump any stack traces
        self.dump_stack_trace = True

        # This is instantiated in initialize_app() only when using
        # password flow auth
        self.auth_client = None

        # Assume TLS host certificate verification is enabled
        self.verify = True

        # Get list of extension modules
        self.ext_modules = clientmanager.get_extension_modules(
            'openstack.cli.extension',
        )

        # Loop through extensions to get parser additions
        for mod in self.ext_modules:
            self.parser = mod.build_option_parser(self.parser)

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
                    help="Show this help message and exit",
                )

    def run(self, argv):
        try:
            return super(OpenStackShell, self).run(argv)
        except Exception as e:
            if not logging.getLogger('').handlers:
                logging.basicConfig()
            if self.dump_stack_trace:
                self.log.error(traceback.format_exc(e))
            else:
                self.log.error('Exception raised: ' + str(e))
            return 1

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
            '--os-domain-name',
            metavar='<auth-domain-name>',
            default=env('OS_DOMAIN_NAME'),
            help='Domain name of the requested domain-level '
                 'authorization scope (Env: OS_DOMAIN_NAME)',
        )
        parser.add_argument(
            '--os-domain-id',
            metavar='<auth-domain-id>',
            default=env('OS_DOMAIN_ID'),
            help='Domain ID of the requested domain-level '
                 'authorization scope (Env: OS_DOMAIN_ID)',
        )
        parser.add_argument(
            '--os-project-name',
            metavar='<auth-project-name>',
            default=env('OS_PROJECT_NAME', default=env('OS_TENANT_NAME')),
            help='Project name of the requested project-level '
                 'authorization scope (Env: OS_PROJECT_NAME)',
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
            help='Project ID of the requested project-level '
                 'authorization scope (Env: OS_PROJECT_ID)',
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
            '--os-user-domain-name',
            metavar='<auth-user-domain-name>',
            default=utils.env('OS_USER_DOMAIN_NAME'),
            help='Domain name of the user (Env: OS_USER_DOMAIN_NAME)')
        parser.add_argument(
            '--os-user-domain-id',
            metavar='<auth-user-domain-id>',
            default=utils.env('OS_USER_DOMAIN_ID'),
            help='Domain ID of the user (Env: OS_USER_DOMAIN_ID)')
        parser.add_argument(
            '--os-project-domain-name',
            metavar='<auth-project-domain-name>',
            default=utils.env('OS_PROJECT_DOMAIN_NAME'),
            help='Domain name of the project which is the requested '
                 'project-level authorization scope '
                 '(Env: OS_PROJECT_DOMAIN_NAME)')
        parser.add_argument(
            '--os-project-domain-id',
            metavar='<auth-project-domain-id>',
            default=utils.env('OS_PROJECT_DOMAIN_ID'),
            help='Domain ID of the project which is the requested '
                 'project-level authorization scope '
                 '(Env: OS_PROJECT_DOMAIN_ID)')
        parser.add_argument(
            '--os-region-name',
            metavar='<auth-region-name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')
        parser.add_argument(
            '--os-cacert',
            metavar='<ca-bundle-file>',
            default=env('OS_CACERT'),
            help='CA certificate bundle file (Env: OS_CACERT)')
        verify_group = parser.add_mutually_exclusive_group()
        verify_group.add_argument(
            '--verify',
            action='store_true',
            help='Verify server certificate (default)',
        )
        verify_group.add_argument(
            '--insecure',
            action='store_true',
            help='Disable server certificate verification',
        )
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

        parser.add_argument(
            '--os-identity-api-version',
            metavar='<identity-api-version>',
            default=env(
                'OS_IDENTITY_API_VERSION',
                default=identity_client.DEFAULT_IDENTITY_API_VERSION),
            help='Identity API version, default=' +
                 identity_client.DEFAULT_IDENTITY_API_VERSION +
                 ' (Env: OS_IDENTITY_API_VERSION)')

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

            if not ((self.options.os_project_id
                    or self.options.os_project_name) or
                    (self.options.os_domain_id
                    or self.options.os_domain_name)):
                raise exc.CommandError(
                    "You must provide authentication scope as a project "
                    "or a domain via --os-project-id or env[OS_PROJECT_ID], "
                    "--os-project-name or env[OS_PROJECT_NAME], "
                    "--os-domain-id or env[OS_DOMAIN_ID], or"
                    "--os-domain-name or env[OS_DOMAIN_NAME].")

            if not self.options.os_auth_url:
                raise exc.CommandError(
                    "You must provide an auth url via"
                    " either --os-auth-url or via env[OS_AUTH_URL]")

        self.client_manager = clientmanager.ClientManager(
            token=self.options.os_token,
            url=self.options.os_url,
            auth_url=self.options.os_auth_url,
            domain_id=self.options.os_domain_id,
            domain_name=self.options.os_domain_name,
            project_name=self.options.os_project_name,
            project_id=self.options.os_project_id,
            user_domain_id=self.options.os_user_domain_id,
            user_domain_name=self.options.os_user_domain_name,
            project_domain_id=self.options.os_project_domain_id,
            project_domain_name=self.options.os_project_domain_name,
            username=self.options.os_username,
            password=self.options.os_password,
            region_name=self.options.os_region_name,
            verify=self.verify,
            api_version=self.api_version,
        )
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
            self.dump_stack_trace = True
        else:
            requests_log.setLevel(logging.WARNING)
            self.dump_stack_trace = False

        # Save default domain
        self.default_domain = self.options.os_default_domain

        # Stash selected API versions for later
        self.api_version = {
            'identity': self.options.os_identity_api_version,
        }
        # Loop through extensions to get API versions
        for mod in self.ext_modules:
            ver = getattr(self.options, mod.API_VERSION_OPTION, None)
            if ver:
                self.api_version[mod.API_NAME] = ver
                self.log.debug('%s API version %s' % (mod.API_NAME, ver))

        # Add the API version-specific commands
        for api in self.api_version.keys():
            version = '.v' + self.api_version[api].replace('.', '_')
            cmd_group = 'openstack.' + api.replace('-', '_') + version
            self.log.debug('command group %s' % cmd_group)
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
        # call InitializeXxx() here
        # set up additional clients to stuff in to client_manager??

        # Handle deferred help and exit
        if self.options.deferred_help:
            self.DeferredHelpAction(self.parser, self.parser, None, None)

        # Set up common client session
        if self.options.os_cacert:
            self.verify = self.options.os_cacert
        else:
            self.verify = not self.options.insecure
        self.restapi = restapi.RESTApi(
            verify=self.verify,
            debug=self.options.debug,
        )

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
    return OpenStackShell().run(argv)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
