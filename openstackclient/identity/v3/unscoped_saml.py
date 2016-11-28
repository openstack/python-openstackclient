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
from osc_lib import utils

from openstackclient.i18n import _


class ListAccessibleDomains(command.Lister):
    _description = _("List accessible domains")

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
    _description = _("List accessible projects")

    def take_action(self, parsed_args):
        columns = ('ID', 'Domain ID', 'Enabled', 'Name')
        identity_client = self.app.client_manager.identity
        data = identity_client.federation.projects.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))
