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

"""Manage access to the clients, including authenticating when needed."""

import importlib
import logging
import sys
import typing as ty

from osc_lib import clientmanager
from osc_lib import shell
import stevedore


LOG = logging.getLogger(__name__)

PLUGIN_MODULES: list[ty.Any] = []

USER_AGENT = 'python-openstackclient'


class ClientManager(clientmanager.ClientManager):
    """Manages access to API clients, including authentication

    Wrap osc_lib's ClientManager to maintain compatibility for the existing
    plugin V2 interface.  Some currently private attributes become public
    in osc-lib so we need to maintain a transition period.
    """

    # A simple incrementing version for the plugin to know what is available
    PLUGIN_INTERFACE_VERSION = "2"

    # Let the commands set this
    _auth_required = False

    def __init__(
        self,
        cli_options=None,
        api_version=None,
        pw_func=None,
    ):
        super().__init__(
            cli_options=cli_options,
            api_version=api_version,
            pw_func=pw_func,
        )

        # TODO(dtroyer): For compatibility; mark this for removal when plugin
        #                interface v2 is removed
        self._region_name = self.region_name
        self._interface = self.interface
        self._cacert = self.cacert
        self._insecure = not self.verify
        # store original auth_type
        self._original_auth_type = cli_options.auth_type

    def setup_auth(self):
        """Set up authentication"""

        if self._auth_setup_completed:
            return

        # NOTE(dtroyer): Validate the auth args; this is protected with 'if'
        #                because openstack_config is an optional argument to
        #                CloudConfig.__init__() and we'll die if it was not
        #                passed.
        if (
            self._auth_required
            and self._cli_options._openstack_config is not None
        ):
            self._cli_options._openstack_config._pw_callback = (
                shell.prompt_for_password
            )
            try:
                # We might already get auth from SDK caching
                if not self._cli_options._auth:
                    self._cli_options._auth = (
                        self._cli_options._openstack_config.load_auth_plugin(
                            self._cli_options.config,
                        )
                    )
            except TypeError as e:
                self._fallback_load_auth_plugin(e)

        return super().setup_auth()

    def _fallback_load_auth_plugin(self, e):
        # NOTES(RuiChen): Hack to avoid auth plugins choking on data they don't
        #                 expect, delete fake token and endpoint, then try to
        #                 load auth plugin again with user specified options.
        #                 We know it looks ugly, but it's necessary.
        if self._cli_options.config['auth']['token'] == 'x':  # noqa: S105
            # restore original auth_type
            self._cli_options.config['auth_type'] = self._original_auth_type
            del self._cli_options.config['auth']['token']
            del self._cli_options.config['auth']['endpoint']
            self._cli_options._auth = (
                self._cli_options._openstack_config.load_auth_plugin(
                    self._cli_options.config,
                )
            )
        else:
            raise e

    def is_network_endpoint_enabled(self):
        """Check if the network endpoint is enabled"""
        # NOTE(dtroyer): is_service_available() can also return None if
        #                there is no Service Catalog, callers here are
        #                not expecting that so fold None into True to
        #                use Network API by default
        return self.is_service_available('network') is not False

    def is_compute_endpoint_enabled(self):
        """Check if Compute endpoint is enabled"""
        return self.is_service_available('compute') is not False

    # TODO(stephenfin): Drop volume_client argument in OSC 8.0 or later.
    def is_volume_endpoint_enabled(self, volume_client=None):
        """Check if volume endpoint is enabled"""
        # We check against the service type and all aliases defined by the
        # Service Types Authority
        # https://service-types.openstack.org/service-types.json
        return (
            self.is_service_available('block-storage') is not False
            or self.is_service_available('volume') is not False
            or self.is_service_available('volumev3') is not False
            or self.is_service_available('volumev2') is not False
            or self.is_service_available('block-store') is not False
        )


# Plugin Support


def _on_load_failure_callback(
    manager: stevedore.ExtensionManager,
    ep: importlib.metadata.EntryPoint,
    err: Exception,
) -> None:
    sys.stderr.write(
        f"WARNING: Failed to import plugin {ep.group}:{ep.name}: {err}.\n"
    )


def get_plugin_modules(group):
    """Find plugin entry points"""
    mod_list = []
    mgr = stevedore.ExtensionManager(
        group, on_load_failure_callback=_on_load_failure_callback
    )
    for ep in mgr:
        LOG.debug('Found plugin %s', ep.name)

        # Different versions of stevedore use different
        # implementations of EntryPoint from other libraries, which
        # are not API-compatible.
        try:
            module_name = ep.entry_point.module_name
        except AttributeError:
            try:
                module_name = ep.entry_point.module
            except AttributeError:
                module_name = ep.entry_point.value

        try:
            module = importlib.import_module(module_name)
        except Exception as err:
            sys.stderr.write(
                f"WARNING: Failed to import plugin {ep.group}:{ep.name}: "
                f"{err}.\n"
            )
            continue

        mod_list.append(module)
        init_func = getattr(module, 'Initialize', None)
        if init_func:
            init_func('x')

        # Add the plugin to the ClientManager
        setattr(
            clientmanager.ClientManager,
            module.API_NAME,
            clientmanager.ClientCache(
                getattr(sys.modules[module_name], 'make_client', None)
            ),
        )
    return mod_list


def build_plugin_option_parser(parser):
    """Add plugin options to the parser"""

    # Loop through extensions to get parser additions
    for mod in PLUGIN_MODULES:
        parser = mod.build_option_parser(parser)
    return parser


# Get list of base plugin modules
PLUGIN_MODULES = get_plugin_modules(
    'openstack.cli.base',
)
# Append list of external plugin modules
PLUGIN_MODULES.extend(
    get_plugin_modules(
        'openstack.cli.extension',
    )
)
