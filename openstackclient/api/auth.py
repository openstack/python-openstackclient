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

import stevedore

from keystoneclient.auth import base

from openstackclient.common import exceptions as exc
from openstackclient.common import utils
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)

# Initialize the list of Authentication plugins early in order
# to get the command-line options
PLUGIN_LIST = None

# List of plugin command line options
OPTIONS_LIST = {}


def get_plugin_list():
    """Gather plugin list and cache it"""

    global PLUGIN_LIST

    if PLUGIN_LIST is None:
        PLUGIN_LIST = stevedore.ExtensionManager(
            base.PLUGIN_NAMESPACE,
            invoke_on_load=False,
            propagate_map_exceptions=True,
        )
    return PLUGIN_LIST


def get_options_list():
    """Gather plugin options so the help action has them available"""

    global OPTIONS_LIST

    if not OPTIONS_LIST:
        for plugin in get_plugin_list():
            for o in plugin.plugin.get_options():
                os_name = o.dest.lower().replace('_', '-')
                os_env_name = 'OS_' + os_name.upper().replace('-', '_')
                OPTIONS_LIST.setdefault(
                    os_name, {'env': os_env_name, 'help': ''},
                )
                # TODO(mhu) simplistic approach, would be better to only add
                # help texts if they vary from one auth plugin to another
                # also the text rendering is ugly in the CLI ...
                OPTIONS_LIST[os_name]['help'] += 'With %s: %s\n' % (
                    plugin.name,
                    o.help,
                )
    return OPTIONS_LIST


def select_auth_plugin(options):
    """Pick an auth plugin based on --os-auth-type or other options"""

    auth_plugin_name = None

    # Do the token/url check first as this must override the default
    # 'password' set by os-client-config
    # Also, url and token are not copied into o-c-c's auth dict (yet?)
    if options.auth.get('url', None) and options.auth.get('token', None):
        # service token authentication
        auth_plugin_name = 'token_endpoint'
    elif options.auth_type in [plugin.name for plugin in PLUGIN_LIST]:
        # A direct plugin name was given, use it
        auth_plugin_name = options.auth_type
    elif options.auth.get('username', None):
        if options.identity_api_version == '3':
            auth_plugin_name = 'v3password'
        elif options.identity_api_version.startswith('2'):
            auth_plugin_name = 'v2password'
        else:
            # let keystoneclient figure it out itself
            auth_plugin_name = 'osc_password'
    elif options.auth.get('token', None):
        if options.identity_api_version == '3':
            auth_plugin_name = 'v3token'
        elif options.identity_api_version.startswith('2'):
            auth_plugin_name = 'v2token'
        else:
            # let keystoneclient figure it out itself
            auth_plugin_name = 'token'
    else:
        # The ultimate default is similar to the original behaviour,
        # but this time with version discovery
        auth_plugin_name = 'osc_password'
    LOG.debug("Auth plugin %s selected" % auth_plugin_name)
    return auth_plugin_name


def build_auth_params(auth_plugin_name, cmd_options):

    auth_params = dict(cmd_options.auth)
    if auth_plugin_name:
        LOG.debug('auth_type: %s', auth_plugin_name)
        auth_plugin_class = base.get_plugin_class(auth_plugin_name)
        # grab tenant from project for v2.0 API compatibility
        if auth_plugin_name.startswith("v2"):
            if 'project_id' in auth_params:
                auth_params['tenant_id'] = auth_params['project_id']
                del auth_params['project_id']
            if 'project_name' in auth_params:
                auth_params['tenant_name'] = auth_params['project_name']
                del auth_params['project_name']
    else:
        LOG.debug('no auth_type')
        # delay the plugin choice, grab every option
        auth_plugin_class = None
        plugin_options = set([o.replace('-', '_') for o in get_options_list()])
        for option in plugin_options:
            LOG.debug('fetching option %s' % option)
            auth_params[option] = getattr(cmd_options.auth, option, None)
    return (auth_plugin_class, auth_params)


def check_valid_auth_options(options, auth_plugin_name):
    """Perform basic option checking, provide helpful error messages"""

    msg = ''
    if auth_plugin_name.endswith('password'):
        if not options.auth.get('username', None):
            msg += _('Set a username with --os-username, OS_USERNAME,'
                     ' or auth.username\n')
        if not options.auth.get('auth_url', None):
            msg += _('Set an authentication URL, with --os-auth-url,'
                     ' OS_AUTH_URL or auth.auth_url\n')
        if (not options.auth.get('project_id', None) and not
                options.auth.get('domain_id', None) and not
                options.auth.get('domain_name', None) and not
                options.auth.get('project_name', None) and not
                options.auth.get('tenant_id', None) and not
                options.auth.get('tenant_name', None)):
            msg += _('Set a scope, such as a project or domain, set a '
                     'project scope with --os-project-name, OS_PROJECT_NAME '
                     'or auth.project_name, set a domain scope with '
                     '--os-domain-name, OS_DOMAIN_NAME or auth.domain_name')
    elif auth_plugin_name.endswith('token'):
        if not options.auth.get('token', None):
            msg += _('Set a token with --os-token, OS_TOKEN or auth.token\n')
        if not options.auth.get('auth_url', None):
            msg += _('Set a service AUTH_URL, with --os-auth-url, '
                     'OS_AUTH_URL or auth.auth_url\n')
    elif auth_plugin_name == 'token_endpoint':
        if not options.auth.get('token', None):
            msg += _('Set a token with --os-token, OS_TOKEN or auth.token\n')
        if not options.auth.get('url', None):
            msg += _('Set a service URL, with --os-url, OS_URL or auth.url\n')

    if msg:
        raise exc.CommandError('Missing parameter(s): \n%s' % msg)


def build_auth_plugins_option_parser(parser):
    """Auth plugins options builder

    Builds dynamically the list of options expected by each available
    authentication plugin.

    """
    available_plugins = [plugin.name for plugin in get_plugin_list()]
    parser.add_argument(
        '--os-auth-type',
        metavar='<auth-type>',
        dest='auth_type',
        default=utils.env('OS_AUTH_TYPE'),
        help='Select an authentication type. Available types: ' +
             ', '.join(available_plugins) +
             '. Default: selected based on --os-username/--os-token' +
             ' (Env: OS_AUTH_TYPE)',
        choices=available_plugins
    )
    # Maintain compatibility with old tenant env vars
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
    for o in get_options_list():
        # Remove tenant options from KSC plugins and replace them below
        if 'tenant' not in o:
            parser.add_argument(
                '--os-' + o,
                metavar='<auth-%s>' % o,
                dest=o.replace('-', '_'),
                default=envs.get(
                    OPTIONS_LIST[o]['env'],
                    utils.env(OPTIONS_LIST[o]['env']),
                ),
                help='%s\n(Env: %s)' % (
                    OPTIONS_LIST[o]['help'],
                    OPTIONS_LIST[o]['env'],
                ),
            )
    # add tenant-related options for compatibility
    # this is deprecated but still used in some tempest tests...
    parser.add_argument(
        '--os-tenant-name',
        metavar='<auth-tenant-name>',
        dest='os_project_name',
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        '--os-tenant-id',
        metavar='<auth-tenant-id>',
        dest='os_project_id',
        help=argparse.SUPPRESS,
    )
    return parser
