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


LOG = logging.getLogger(__name__)


# Initialize the list of Authentication plugins early in order
# to get the command-line options
PLUGIN_LIST = stevedore.ExtensionManager(
    base.PLUGIN_NAMESPACE,
    invoke_on_load=False,
    propagate_map_exceptions=True,
)
# TODO(dtroyer): add some method to list the plugins for the
#                --os_auth_plugin option

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


def _guess_authentication_method(options):
    """If no auth plugin was specified, pick one based on other options"""

    if options.os_url:
        # service token authentication, do nothing
        return
    auth_plugin = None
    if options.os_password:
        if options.os_identity_api_version == '3':
            auth_plugin = 'v3password'
        elif options.os_identity_api_version == '2.0':
            auth_plugin = 'v2password'
        else:
            # let keystoneclient figure it out itself
            auth_plugin = 'password'
    elif options.os_token:
        if options.os_identity_api_version == '3':
            auth_plugin = 'v3token'
        elif options.os_identity_api_version == '2.0':
            auth_plugin = 'v2token'
        else:
            # let keystoneclient figure it out itself
            auth_plugin = 'token'
    else:
        raise exc.CommandError(
            "Could not figure out which authentication method "
            "to use, please set --os-auth-plugin"
        )
    LOG.debug("No auth plugin selected, picking %s from other "
              "options" % auth_plugin)
    options.os_auth_plugin = auth_plugin


def build_auth_params(cmd_options):
    auth_params = {}
    if cmd_options.os_url:
        return {'token': cmd_options.os_token}
    if cmd_options.os_auth_plugin:
        auth_plugin = base.get_plugin_class(cmd_options.os_auth_plugin)
        plugin_options = auth_plugin.get_options()
        for option in plugin_options:
            option_name = 'os_' + option.dest
            LOG.debug('fetching option %s' % option_name)
            auth_params[option.dest] = getattr(cmd_options, option_name, None)
        # grab tenant from project for v2.0 API compatibility
        if cmd_options.os_auth_plugin.startswith("v2"):
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
        # delay the plugin choice, grab every option
        plugin_options = set([o.replace('-', '_') for o in OPTIONS_LIST])
        for option in plugin_options:
            option_name = 'os_' + option
            LOG.debug('fetching option %s' % option_name)
            auth_params[option] = getattr(cmd_options, option_name, None)
    return auth_params


def build_auth_plugins_option_parser(parser):
    """Auth plugins options builder

    Builds dynamically the list of options expected by each available
    authentication plugin.

    """
    available_plugins = [plugin.name for plugin in PLUGIN_LIST]
    parser.add_argument(
        '--os-auth-plugin',
        metavar='<OS_AUTH_PLUGIN>',
        default=utils.env('OS_AUTH_PLUGIN'),
        help='The authentication method to use. If this option is not set, '
             'openstackclient will attempt to guess the authentication method '
             'to use based on the other options. If this option is set, '
             'the --os-identity-api-version argument must be consistent '
             'with the version of the method.\nAvailable methods are ' +
             ', '.join(available_plugins),
        choices=available_plugins
    )
    # make sur we catch old v2.0 env values
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
