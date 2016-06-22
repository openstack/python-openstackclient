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

import logging

from keystoneauth1 import loading
from keystoneauth1.loading._plugins.identity import generic as ksa_password
from keystoneauth1 import token_endpoint
from six.moves.urllib import parse as urlparse

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


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


class OSCGenericPassword(ksa_password.Password):
    """Auth plugin hack to work around broken Keystone configurations

    The default Keystone configuration uses http://localhost:xxxx in
    admin_endpoint and public_endpoint and are returned in the links.href
    attribute by the version routes.  Deployments that do not set these
    are unusable with newer keystoneclient version discovery.

    """

    def create_plugin(self, session, version, url, raw_status=None):
        """Handle default Keystone endpoint configuration

        Build the actual API endpoint from the scheme, host and port of the
        original auth URL and the rest from the returned version URL.
        """

        ver_u = urlparse.urlparse(url)

        # Only hack this if it is the default setting
        if ver_u.netloc.startswith('localhost'):
            auth_u = urlparse.urlparse(self.auth_url)
            # from original auth_url: scheme, netloc
            # from api_url: path, query (basically, the rest)
            url = urlparse.urlunparse((
                auth_u.scheme,
                auth_u.netloc,
                ver_u.path,
                ver_u.params,
                ver_u.query,
                ver_u.fragment,
            ))
            LOG.debug('Version URL updated: %s', url)

        return super(OSCGenericPassword, self).create_plugin(
            session=session,
            version=version,
            url=url,
            raw_status=raw_status,
        )
