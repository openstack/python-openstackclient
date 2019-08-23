#   Copyright 2012-2013 OpenStack Foundation
#   Copyright 2015 Dean Troyer
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

import locale
import sys

from osc_lib.api import auth
from osc_lib.command import commandmanager
from osc_lib import shell
import six

import openstackclient
from openstackclient.common import clientmanager


DEFAULT_DOMAIN = 'default'


class OpenStackShell(shell.OpenStackShell):

    def __init__(self):

        super(OpenStackShell, self).__init__(
            description=__doc__.strip(),
            version=openstackclient.__version__,
            command_manager=commandmanager.CommandManager('openstack.cli'),
            deferred_help=True)

        self.api_version = {}

        # Assume TLS host certificate verification is enabled
        self.verify = True

    def build_option_parser(self, description, version):
        parser = super(OpenStackShell, self).build_option_parser(
            description,
            version)
        parser = clientmanager.build_plugin_option_parser(parser)
        parser = auth.build_auth_plugins_option_parser(parser)
        return parser

    def _final_defaults(self):
        super(OpenStackShell, self)._final_defaults()

        # Set the default plugin to admin_token if endpoint and token are given
        if (self.options.endpoint and self.options.token):
            # Use token authentication
            self._auth_type = 'admin_token'
        else:
            self._auth_type = 'password'

    def _load_plugins(self):
        """Load plugins via stevedore

        osc-lib has no opinion on what plugins should be loaded
        """
        # Loop through extensions to get API versions
        for mod in clientmanager.PLUGIN_MODULES:
            default_version = getattr(mod, 'DEFAULT_API_VERSION', None)
            # Only replace the first instance of "os", some service names will
            # have "os" in their name, like: "antiddos"
            option = mod.API_VERSION_OPTION.replace('os_', '', 1)
            version_opt = str(self.cloud.config.get(option, default_version))
            if version_opt:
                api = mod.API_NAME
                self.api_version[api] = version_opt

                # Add a plugin interface to let the module validate the version
                # requested by the user
                skip_old_check = False
                mod_check_api_version = getattr(mod, 'check_api_version', None)
                if mod_check_api_version:
                    # this throws an exception if invalid
                    skip_old_check = mod_check_api_version(version_opt)

                mod_versions = getattr(mod, 'API_VERSIONS', None)
                if not skip_old_check and mod_versions:
                    if version_opt not in mod_versions:
                        sorted_versions = sorted(
                            mod.API_VERSIONS.keys(),
                            key=lambda s: list(map(int, s.split('.'))))
                        self.log.warning(
                            "%s version %s is not in supported versions: %s"
                            % (api, version_opt, ', '.join(sorted_versions)))

                # Command groups deal only with major versions
                version = '.v' + version_opt.replace('.', '_').split('_')[0]
                cmd_group = 'openstack.' + api.replace('-', '_') + version
                self.command_manager.add_command_group(cmd_group)
                self.log.debug(
                    '%(name)s API version %(version)s, cmd group %(group)s',
                    {'name': api, 'version': version_opt, 'group': cmd_group}
                )

    def _load_commands(self):
        """Load commands via cliff/stevedore

        osc-lib has no opinion on what commands should be loaded
        """
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

    def initialize_app(self, argv):
        super(OpenStackShell, self).initialize_app(argv)

        # Re-create the client_manager with our subclass
        self.client_manager = clientmanager.ClientManager(
            cli_options=self.cloud,
            api_version=self.api_version,
            pw_func=shell.prompt_for_password,
        )

    def prepare_to_run_command(self, cmd):
        """Set up auth and API versions"""

        # TODO(dtroyer): Move this to osc-lib, remove entire method when 1.4.0
        #                release is minimum version is in global-requirements
        # NOTE(dtroyer): If auth is not required for a command, skip
        #                get_one_Cloud()'s validation to avoid loading plugins
        validate = cmd.auth_required

        # Force skipping auth for commands that do not need it
        # NOTE(dtroyer): This is here because ClientManager does not have
        #                visibility into the Command object to get
        #                auth_required. It needs to move into osc-lib
        self.client_manager._auth_required = cmd.auth_required

        # Validate auth options
        self.cloud = self.cloud_config.get_one_cloud(
            cloud=self.options.cloud,
            argparse=self.options,
            validate=validate,
        )
        # Push the updated args into ClientManager
        self.client_manager._cli_options = self.cloud

        return super(OpenStackShell, self).prepare_to_run_command(cmd)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
        if six.PY2:
            # Emulate Py3, decode argv into Unicode based on locale so that
            # commands always see arguments as text instead of binary data
            encoding = locale.getpreferredencoding()
            if encoding:
                argv = map(lambda arg: arg.decode(encoding), argv)

    return OpenStackShell().run(argv)


if __name__ == "__main__":
    sys.exit(main())
