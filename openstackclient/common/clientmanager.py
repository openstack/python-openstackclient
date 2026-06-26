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

import argparse
from collections.abc import Callable
import importlib
import logging
import sys
from typing import Any, Protocol, TypeVar, runtime_checkable

from keystoneauth1 import access as ksa_access
from openstack.block_storage import v2 as volume_v2
from openstack.block_storage import v3 as volume_v3
from openstack.compute import v2 as compute_v2
from openstack.image import v2 as image_v2
from openstack.network import v2 as network_v2
from osc_lib.cli import client_config
from osc_lib import clientmanager
from osc_lib import shell
import stevedore

from openstackclient.api import object_store_v1

LOG = logging.getLogger(__name__)
PLUGIN_MODULES: list[Any] = []
USER_AGENT = 'python-openstackclient'


class ClientManager(clientmanager.ClientManager):
    """Manages access to API clients, including authentication

    Wrap osc_lib's ClientManager to maintain compatibility for the existing
    plugin V2 interface.  Some currently private attributes become public
    in osc-lib so we need to maintain a transition period.
    """

    # we know this will be set by us and will not be nullable
    auth_ref: ksa_access.AccessInfo

    # this is a hack to keep mypy happy: the actual attributes are set in
    # get_plugin_modules below
    # TODO(stephenfin): Change the types of identity, object store and share
    # once we've migrated everything to SDK
    compute: compute_v2.Proxy
    identity: Any
    image: image_v2.Proxy
    network: network_v2.Proxy
    object_store: object_store_v1.APIv1
    share: Any
    volume: volume_v2.Proxy | volume_v3.Proxy

    def __init__(
        self,
        cli_options: Any = None,
        api_version: Any = None,
        pw_func: Any = None,
    ) -> None:
        super().__init__(
            cli_options=cli_options,
            api_version=api_version,
            pw_func=pw_func,
        )

        # TODO(dtroyer): For compatibility; mark this for removal when plugin
        # interface v2 is removed
        self._region_name = self.region_name
        self._interface = self.interface
        self._cacert = self.cacert
        self._insecure = not self.verify
        # store original auth_type
        self._original_auth_type = cli_options.auth_type

    def setup_auth(self) -> None:
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
            if not isinstance(
                self._cli_options._openstack_config, client_config.OSC_Config
            ):
                # programmer error
                raise TypeError('unexpected type for _openstack_config')

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

    def _fallback_load_auth_plugin(self, e: Exception) -> None:
        # NOTES(RuiChen): Hack to avoid auth plugins choking on data they don't
        #                 expect, delete fake token and endpoint, then try to
        #                 load auth plugin again with user specified options.
        #                 We know it looks ugly, but it's necessary.
        if self._cli_options.config['auth']['token'] == 'x':  # noqa: S105
            # restore original auth_type
            self._cli_options.config['auth_type'] = self._original_auth_type
            del self._cli_options.config['auth']['token']
            del self._cli_options.config['auth']['endpoint']

            if not isinstance(
                self._cli_options._openstack_config, client_config.OSC_Config
            ):
                # programmer error
                raise TypeError('unexpected type for _openstack_config')

            self._cli_options._auth = (
                self._cli_options._openstack_config.load_auth_plugin(
                    self._cli_options.config,
                )
            )
        else:
            raise e

    def is_network_endpoint_enabled(self) -> bool:
        """Check if the network endpoint is enabled"""
        # NOTE(dtroyer): is_service_available() can also return None if
        #                there is no Service Catalog, callers here are
        #                not expecting that so fold None into True to
        #                use Network API by default
        return (
            self.is_service_available(
                'network', self.region_name, self.interface
            )
            is not False
        )

    def is_compute_endpoint_enabled(self) -> bool:
        """Check if Compute endpoint is enabled"""
        return (
            self.is_service_available(
                'compute', self.region_name, self.interface
            )
            is not False
        )

    # TODO(stephenfin): Drop volume_client argument in OSC 8.0 or later.
    def is_volume_endpoint_enabled(self, volume_client: Any = None) -> bool:
        """Check if volume endpoint is enabled"""
        # We check against the service type and all aliases defined by the
        # Service Types Authority
        # https://service-types.openstack.org/service-types.json
        return (
            self.is_service_available(
                'block-storage', self.region_name, self.interface
            )
            is not False
            or self.is_service_available(
                'volume', self.region_name, self.interface
            )
            is not False
            or self.is_service_available(
                'volumev3', self.region_name, self.interface
            )
            is not False
            or self.is_service_available(
                'volumev2', self.region_name, self.interface
            )
            is not False
            or self.is_service_available(
                'block-store', self.region_name, self.interface
            )
            is not False
        )


# Plugin Support

ArgumentParserT = TypeVar('ArgumentParserT', bound=argparse.ArgumentParser)


@runtime_checkable  # Optional: allows usage with isinstance()
class PluginModule(Protocol):
    DEFAULT_API_VERSION: str
    API_VERSION_OPTION: str
    API_NAME: str
    API_VERSIONS: tuple[str]

    make_client: Callable[..., Any]
    build_option_parser: Callable[[ArgumentParserT], ArgumentParserT]
    check_api_version: Callable[[str], bool]


def _on_load_failure_callback(
    manager: stevedore.ExtensionManager[PluginModule],
    ep: importlib.metadata.EntryPoint,
    err: BaseException,
) -> None:
    sys.stderr.write(
        f"WARNING: Failed to import plugin {ep.group}:{ep.name}: {err}.\n"
    )


def get_plugin_modules(group: str) -> list[Any]:
    """Find plugin entry points"""
    mod_list = []
    mgr: stevedore.ExtensionManager[PluginModule]
    mgr = stevedore.ExtensionManager(
        group, on_load_failure_callback=_on_load_failure_callback
    )
    for ep in mgr:
        LOG.debug('Found plugin %s', ep.name)

        module_name = ep.entry_point.module

        try:
            module = importlib.import_module(module_name)
        except Exception as err:
            sys.stderr.write(
                f"WARNING: Failed to import plugin "
                f"{ep.module_name}:{ep.name}: {err}.\n"
            )
            continue

        mod_list.append(module)

        # Add the plugin to the ClientManager
        setattr(
            clientmanager.ClientManager,
            module.API_NAME,
            clientmanager.ClientCache(
                getattr(sys.modules[module_name], 'make_client', None)
            ),
        )
    return mod_list


def build_plugin_option_parser(
    parser: ArgumentParserT,
) -> ArgumentParserT:
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
