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

import sys
import warnings

from osc_lib.api import auth
from osc_lib.command import commandmanager
from osc_lib import shell

import openstackclient
from openstackclient.common import clientmanager


DEFAULT_DOMAIN = 'default'


class OpenStackShell(shell.OpenStackShell):
    def __init__(self):
        super().__init__(
            description=__doc__.strip(),
            version=openstackclient.__version__,
            command_manager=commandmanager.CommandManager('openstack.cli'),
            deferred_help=True,
        )

        self.api_version = {}

        # Assume TLS host certificate verification is enabled
        self.verify = True

        # ignore warnings from openstacksdk since our users can't do anything
        # about them
        warnings.filterwarnings('ignore', module='openstack')

    def build_option_parser(self, description, version):
        parser = super().build_option_parser(description, version)
        parser = clientmanager.build_plugin_option_parser(parser)
        parser = auth.build_auth_plugins_option_parser(parser)
        return parser

    def _final_defaults(self):
        super()._final_defaults()

        # Set the default plugin to admin_token if endpoint and token are given
        if self.options.endpoint and self.options.token:
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

                # NOTE(stephenfin): API_VERSIONS has traditionally been a
                # dictionary but the values are only used internally and are
                # ignored for the modules using SDK. So we now support tuples
                # instead.
                mod_versions = getattr(mod, 'API_VERSIONS', None)
                if mod_versions is not None and not isinstance(
                    mod_versions, (dict, tuple)
                ):
                    raise TypeError(
                        f'Plugin {mod} has incompatible API_VERSIONS. '
                        f'Expected: tuple, dict. Got: {type(mod_versions)}. '
                        f'Please report this to your package maintainer.'
                    )

                if mod_versions and not skip_old_check:
                    if version_opt not in mod_versions:
                        sorted_versions = sorted(
                            list(mod.API_VERSIONS),
                            key=lambda s: list(map(int, s.split('.'))),
                        )
                        self.log.warning(
                            "%(name)s API version %(version)s is not in "
                            "supported versions: %(supported)s",
                            {
                                'name': api,
                                'version': version_opt,
                                'supported': ', '.join(sorted_versions),
                            },
                        )

                # Command groups deal only with major versions
                version = '.v' + version_opt.replace('.', '_').split('_')[0]
                cmd_group = 'openstack.' + api.replace('-', '_') + version
                self.command_manager.add_command_group(cmd_group)
                self.log.debug(
                    '%(name)s API version %(version)s, cmd group %(group)s',
                    {'name': api, 'version': version_opt, 'group': cmd_group},
                )

    def _load_commands(self):
        """Load commands via cliff/stevedore

        osc-lib has no opinion on what commands should be loaded
        """
        # Commands that span multiple APIs
        self.command_manager.add_command_group('openstack.common')

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
        self.command_manager.add_command_group('openstack.extension')

    def initialize_app(self, argv):
        super().initialize_app(argv)

        # Re-create the client_manager with our subclass
        self.client_manager = clientmanager.ClientManager(
            cli_options=self.cloud,
            api_version=self.api_version,
            pw_func=shell.prompt_for_password,
        )


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    return OpenStackShell().run(argv)


if __name__ == "__main__":
    sys.exit(main())
