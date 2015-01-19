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

"""Authentication Library"""

import argparse
import logging

from six.moves.urllib import parse as urlparse
import stevedore

from oslo.config import cfg

from keystoneclient.auth import base
from keystoneclient.auth.identity.generic import password as ksc_password

from openstackclient.common import exceptions as exc
from openstackclient.common import utils
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


# Initialize the list of Authentication plugins early in order
# to get the command-line options
PLUGIN_LIST = stevedore.ExtensionManager(
    base.PLUGIN_NAMESPACE,
    invoke_on_load=False,
    propagate_map_exceptions=True,
)

# Get the command line options so the help action has them available
OPTIONS_LIST = {}
for plugin in PLUGIN_LIST:
    for o in plugin.plugin.get_options():
        os_name = o.dest.lower().replace('_', '-')
        os_env_name = 'OS_' + os_name.upper().replace('-', '_')
        OPTIONS_LIST.setdefault(os_name, {'env': os_env_name, 'help': ''})
        # TODO(mhu) simplistic approach, would be better to only add
        # help texts if they vary from one auth plugin to another
        # also the text rendering is ugly in the CLI ...
        OPTIONS_LIST[os_name]['help'] += 'With %s: %s\n' % (
            plugin.name,
            o.help,
        )


def select_auth_plugin(options):
    """Pick an auth plugin based on --os-auth-type or other options"""

    auth_plugin_name = None

    if options.os_auth_type in [plugin.name for plugin in PLUGIN_LIST]:
        # A direct plugin name was given, use it
        return options.os_auth_type

    if options.os_url and options.os_token:
        # service token authentication
        auth_plugin_name = 'token_endpoint'
    elif options.os_username:
        if options.os_identity_api_version == '3':
            auth_plugin_name = 'v3password'
        elif options.os_identity_api_version == '2.0':
            auth_plugin_name = 'v2password'
        else:
            # let keystoneclient figure it out itself
            auth_plugin_name = 'osc_password'
    elif options.os_token:
        if options.os_identity_api_version == '3':
            auth_plugin_name = 'v3token'
        elif options.os_identity_api_version == '2.0':
            auth_plugin_name = 'v2token'
        else:
            # let keystoneclient figure it out itself
            auth_plugin_name = 'token'
    else:
        raise exc.CommandError(
            "Authentication type must be selected with --os-auth-type"
        )
    LOG.debug("Auth plugin %s selected" % auth_plugin_name)
    return auth_plugin_name


def build_auth_params(auth_plugin_name, cmd_options):
    auth_params = {}
    if auth_plugin_name:
        LOG.debug('auth_type: %s', auth_plugin_name)
        auth_plugin_class = base.get_plugin_class(auth_plugin_name)
        plugin_options = auth_plugin_class.get_options()
        for option in plugin_options:
            option_name = 'os_' + option.dest
            LOG.debug('fetching option %s' % option_name)
            auth_params[option.dest] = getattr(cmd_options, option_name, None)
        # grab tenant from project for v2.0 API compatibility
        if auth_plugin_name.startswith("v2"):
            auth_params['tenant_id'] = getattr(
                cmd_options,
                'os_project_id',
                None,
            )
            auth_params['tenant_name'] = getattr(
                cmd_options,
                'os_project_name',
                None,
            )
    else:
        LOG.debug('no auth_type')
        # delay the plugin choice, grab every option
        plugin_options = set([o.replace('-', '_') for o in OPTIONS_LIST])
        for option in plugin_options:
            option_name = 'os_' + option
            LOG.debug('fetching option %s' % option_name)
            auth_params[option] = getattr(cmd_options, option_name, None)
    return (auth_plugin_class, auth_params)


def check_valid_auth_options(options, auth_plugin_name):
    """Perform basic option checking, provide helpful error messages"""

    msg = ''
    if auth_plugin_name.endswith('password'):
        if not options.os_username:
            msg += _('Set a username with --os-username or OS_USERNAME\n')
        if not options.os_auth_url:
            msg += _('Set an authentication URL, with --os-auth-url or'
                     ' OS_AUTH_URL\n')
        if (not options.os_project_id and not options.os_domain_id and not
                options.os_domain_name and not options.os_project_name):
            msg += _('Set a scope, such as a project or domain, with '
                     '--os-project-name or OS_PROJECT_NAME')

    if msg:
        raise exc.CommandError('Missing parameter(s): \n%s' % msg)


def build_auth_plugins_option_parser(parser):
    """Auth plugins options builder

    Builds dynamically the list of options expected by each available
    authentication plugin.

    """
    available_plugins = [plugin.name for plugin in PLUGIN_LIST]
    parser.add_argument(
        '--os-auth-type',
        metavar='<auth-type>',
        default=utils.env('OS_AUTH_TYPE'),
        help='Select an auhentication type. Available types: ' +
             ', '.join(available_plugins) +
             '. Default: selected based on --os-username/--os-token' +
             ' (Env: OS_AUTH_TYPE)',
        choices=available_plugins
    )
    # make sure we catch old v2.0 env values
    envs = {
        'OS_PROJECT_NAME': utils.env(
            'OS_PROJECT_NAME',
            default=utils.env('OS_TENANT_NAME')
        ),
        'OS_PROJECT_ID': utils.env(
            'OS_PROJECT_ID',
            default=utils.env('OS_TENANT_ID')
        ),
    }
    for o in OPTIONS_LIST:
        # remove allusion to tenants from v2.0 API
        if 'tenant' not in o:
            parser.add_argument(
                '--os-' + o,
                metavar='<auth-%s>' % o,
                default=envs.get(OPTIONS_LIST[o]['env'],
                                 utils.env(OPTIONS_LIST[o]['env'])),
                help='%s\n(Env: %s)' % (OPTIONS_LIST[o]['help'],
                                        OPTIONS_LIST[o]['env']),
            )
    # add tenant-related options for compatibility
    # this is deprecated but still used in some tempest tests...
    parser.add_argument(
        '--os-tenant-name',
        metavar='<auth-tenant-name>',
        dest='os_project_name',
        default=utils.env('OS_TENANT_NAME'),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        '--os-tenant-id',
        metavar='<auth-tenant-id>',
        dest='os_project_id',
        default=utils.env('OS_TENANT_ID'),
        help=argparse.SUPPRESS,
    )
    return parser


class TokenEndpoint(base.BaseAuthPlugin):
    """Auth plugin to handle traditional token/endpoint usage

    Implements the methods required to handle token authentication
    with a user-specified token and service endpoint; no Identity calls
    are made for re-scoping, service catalog lookups or the like.

    The purpose of this plugin is to get rid of the special-case paths
    in the code to handle this authentication format. Its primary use
    is for bootstrapping the Keystone database.
    """

    def __init__(self, url, token, **kwargs):
        """A plugin for static authentication with an existing token

        :param string url: Service endpoint
        :param string token: Existing token
        """
        super(TokenEndpoint, self).__init__()
        self.endpoint = url
        self.token = token

    def get_endpoint(self, session, **kwargs):
        """Return the supplied endpoint"""
        return self.endpoint

    def get_token(self, session):
        """Return the supplied token"""
        return self.token

    def get_auth_ref(self, session, **kwargs):
        """Stub this method for compatibility"""
        return None

    # Override this because it needs to be a class method...
    @classmethod
    def get_options(self):
        options = super(TokenEndpoint, self).get_options()

        options.extend([
            # Maintain name 'url' for compatibility
            cfg.StrOpt('url',
                       help='Specific service endpoint to use'),
            cfg.StrOpt('token',
                       secret=True,
                       help='Authentication token to use'),
        ])

        return options


class OSCGenericPassword(ksc_password.Password):
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
            LOG.debug('Version URL updated: %s' % url)

        return super(OSCGenericPassword, self).create_plugin(
            session=session,
            version=version,
            url=url,
            raw_status=raw_status,
        )
