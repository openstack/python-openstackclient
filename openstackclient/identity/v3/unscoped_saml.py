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

"""Identity v3 unscoped SAML auth action implementations.

The first step of federated auth is to fetch an unscoped token. From there,
the user can list domains and projects they are allowed to access, and request
a scoped token."""

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


UNSCOPED_AUTH_PLUGINS = ['v3unscopedsaml', 'v3unscopedadfs', 'v3oidc']


def auth_with_unscoped_saml(func):
    """Check the unscoped federated context"""

    def _decorated(self, parsed_args):
        auth_plugin_name = self.app.client_manager.auth_plugin_name
        if auth_plugin_name in UNSCOPED_AUTH_PLUGINS:
            return func(self, parsed_args)
        else:
            msg = (_('This command requires the use of an unscoped SAML '
                     'authentication plugin. Please use argument '
                     '--os-auth-type with one of the following '
                     'plugins: %s') % ', '.join(UNSCOPED_AUTH_PLUGINS))
            raise exceptions.CommandError(msg)
    return _decorated


class ListAccessibleDomains(command.Lister):
    """List accessible domains"""

    @auth_with_unscoped_saml
    def take_action(self, parsed_args):
        columns = ('ID', 'Enabled', 'Name', 'Description')
        identity_client = self.app.client_manager.identity
        data = identity_client.federation.domains.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ListAccessibleProjects(command.Lister):
    """List accessible projects"""

    @auth_with_unscoped_saml
    def take_action(self, parsed_args):
        columns = ('ID', 'Domain ID', 'Enabled', 'Name')
        identity_client = self.app.client_manager.identity
        data = identity_client.federation.projects.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))
