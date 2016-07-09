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

"""Authentication Plugin Library"""

from keystoneauth1 import loading
from keystoneauth1 import token_endpoint

from openstackclient.i18n import _


class TokenEndpoint(loading.BaseLoader):
    """Auth plugin to handle traditional token/endpoint usage

    Keystoneauth contains a Token plugin class that now correctly
    handles the token/endpoint auth compatible with OSC.  However,
    the AdminToken loader deprecates the 'url' argument, which breaks
    OSC compatibility, so make one that works.
    """

    @property
    def plugin_class(self):
        return token_endpoint.Token

    def load_from_options(self, url, token, **kwargs):
        """A plugin for static authentication with an existing token

        :param string url: Service endpoint
        :param string token: Existing token
        """

        return super(TokenEndpoint, self).load_from_options(
            endpoint=url,
            token=token,
        )

    def get_options(self):
        """Return the legacy options"""

        options = [
            loading.Opt(
                'url',
                help=_('Specific service endpoint to use'),
            ),
            loading.Opt(
                'token',
                secret=True,
                help=_('Authentication token to use'),
            ),
        ]
        return options
