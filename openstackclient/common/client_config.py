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

"""OpenStackConfig subclass for argument compatibility"""

import logging

from os_client_config import config
from os_client_config import exceptions as occ_exceptions
from oslo_utils import strutils
import six


LOG = logging.getLogger(__name__)


# Sublcass OpenStackConfig in order to munge config values
# before auth plugins are loaded
class OSC_Config(config.OpenStackConfig):

    # TODO(dtroyer): Once os-client-config with pw_func argument is in
    #                global-requirements we can remove __init()__
    def __init__(
        self,
        config_files=None,
        vendor_files=None,
        override_defaults=None,
        force_ipv4=None,
        envvar_prefix=None,
        secure_files=None,
        pw_func=None,
    ):
        ret = super(OSC_Config, self).__init__(
            config_files=config_files,
            vendor_files=vendor_files,
            override_defaults=override_defaults,
            force_ipv4=force_ipv4,
            envvar_prefix=envvar_prefix,
            secure_files=secure_files,
        )

        # NOTE(dtroyer): This will be pushed down into os-client-config
        #                The default is there is no callback, the calling
        #                application must specify what to use, typically
        #                it will be osc_lib.shell.prompt_for_password()
        if '_pw_callback' not in vars(self):
            # Set the default if it doesn't already exist
            self._pw_callback = None
        if pw_func is not None:
            # Set the passed in value
            self._pw_callback = pw_func

        return ret

    def _auth_select_default_plugin(self, config):
        """Select a default plugin based on supplied arguments

        Migrated from auth.select_auth_plugin()
        """

        identity_version = config.get('identity_api_version', '')

        if config.get('username', None) and not config.get('auth_type', None):
            if identity_version == '3':
                config['auth_type'] = 'v3password'
            elif identity_version.startswith('2'):
                config['auth_type'] = 'v2password'
            else:
                # let keystoneauth figure it out itself
                config['auth_type'] = 'password'
        elif config.get('token', None) and not config.get('auth_type', None):
            if identity_version == '3':
                config['auth_type'] = 'v3token'
            elif identity_version.startswith('2'):
                config['auth_type'] = 'v2token'
            else:
                # let keystoneauth figure it out itself
                config['auth_type'] = 'token'
        else:
            # The ultimate default is similar to the original behaviour,
            # but this time with version discovery
            if not config.get('auth_type', None):
                config['auth_type'] = 'password'

        LOG.debug("Auth plugin %s selected" % config['auth_type'])
        return config

    def _auth_v2_arguments(self, config):
        """Set up v2-required arguments from v3 info

        Migrated from auth.build_auth_params()
        """

        if ('auth_type' in config and config['auth_type'].startswith("v2")):
            if 'project_id' in config['auth']:
                config['auth']['tenant_id'] = config['auth']['project_id']
            if 'project_name' in config['auth']:
                config['auth']['tenant_name'] = config['auth']['project_name']
        return config

    def _auth_v2_ignore_v3(self, config):
        """Remove v3 arguemnts if present for v2 plugin

        Migrated from clientmanager.setup_auth()
        """

        # NOTE(hieulq): If USER_DOMAIN_NAME, USER_DOMAIN_ID, PROJECT_DOMAIN_ID
        # or PROJECT_DOMAIN_NAME is present and API_VERSION is 2.0, then
        # ignore all domain related configs.
        if (config.get('identity_api_version', '').startswith('2') and
                config.get('auth_type', None).endswith('password')):
            domain_props = [
                'project_domain_id',
                'project_domain_name',
                'user_domain_id',
                'user_domain_name',
            ]
            for prop in domain_props:
                if config['auth'].pop(prop, None) is not None:
                    LOG.warning("Ignoring domain related config " +
                                prop + " because identity API version is 2.0")
        return config

    def _auth_default_domain(self, config):
        """Set a default domain from available arguments

        Migrated from clientmanager.setup_auth()
        """

        identity_version = config.get('identity_api_version', '')
        auth_type = config.get('auth_type', None)

        # TODO(mordred): This is a usability improvement that's broadly useful
        # We should port it back up into os-client-config.
        default_domain = config.get('default_domain', None)
        if (identity_version == '3' and
                not auth_type.startswith('v2') and
                default_domain):

            # NOTE(stevemar): If PROJECT_DOMAIN_ID or PROJECT_DOMAIN_NAME is
            # present, then do not change the behaviour. Otherwise, set the
            # PROJECT_DOMAIN_ID to 'OS_DEFAULT_DOMAIN' for better usability.
            if (
                    not config['auth'].get('project_domain_id') and
                    not config['auth'].get('project_domain_name')
            ):
                config['auth']['project_domain_id'] = default_domain

            # NOTE(stevemar): If USER_DOMAIN_ID or USER_DOMAIN_NAME is present,
            # then do not change the behaviour. Otherwise, set the
            # USER_DOMAIN_ID to 'OS_DEFAULT_DOMAIN' for better usability.
            # NOTE(aloga): this should only be set if there is a username.
            # TODO(dtroyer): Move this to os-client-config after the plugin has
            # been loaded so we can check directly if the options are accepted.
            if (
                    auth_type in ("password", "v3password", "v3totp") and
                    not config['auth'].get('user_domain_id') and
                    not config['auth'].get('user_domain_name')
            ):
                config['auth']['user_domain_id'] = default_domain
        return config

    def auth_config_hook(self, config):
        """Allow examination of config values before loading auth plugin

        OpenStackClient will override this to perform additional chacks
        on auth_type.
        """

        config = self._auth_select_default_plugin(config)
        config = self._auth_v2_arguments(config)
        config = self._auth_v2_ignore_v3(config)
        config = self._auth_default_domain(config)

        if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug("auth_config_hook(): %s",
                      strutils.mask_password(six.text_type(config)))
        return config

    def load_auth_plugin(self, config):
        """Get auth plugin and validate args"""

        loader = self._get_auth_loader(config)
        config = self._validate_auth(config, loader)
        auth_plugin = loader.load_from_options(**config['auth'])
        return auth_plugin

    def _validate_auth_ksc(self, config, cloud, fixed_argparse=None):
        """Old compatibility hack for OSC, no longer needed/wanted"""
        return config

    def _validate_auth(self, config, loader, fixed_argparse=None):
        """Validate auth plugin arguments"""
        # May throw a keystoneauth1.exceptions.NoMatchingPlugin

        plugin_options = loader.get_options()

        msgs = []
        prompt_options = []
        for p_opt in plugin_options:
            # if it's in config, win, move it and kill it from config dict
            # if it's in config.auth but not in config we're good
            # deprecated loses to current
            # provided beats default, deprecated or not
            winning_value = self._find_winning_auth_value(p_opt, config)
            if not winning_value:
                winning_value = self._find_winning_auth_value(
                    p_opt, config['auth'])

            # if the plugin tells us that this value is required
            # then error if it's doesn't exist now
            if not winning_value and p_opt.required:
                msgs.append(
                    'Missing value {auth_key}'
                    ' required for auth plugin {plugin}'.format(
                        auth_key=p_opt.name, plugin=config.get('auth_type'),
                    )
                )

            # Clean up after ourselves
            for opt in [p_opt.name] + [o.name for o in p_opt.deprecated]:
                opt = opt.replace('-', '_')
                config.pop(opt, None)
                config['auth'].pop(opt, None)

            if winning_value:
                # Prefer the plugin configuration dest value if the value's key
                # is marked as depreciated.
                if p_opt.dest is None:
                    config['auth'][p_opt.name.replace('-', '_')] = (
                        winning_value)
                else:
                    config['auth'][p_opt.dest] = winning_value

            # See if this needs a prompting
            if (
                    'prompt' in vars(p_opt) and
                    p_opt.prompt is not None and
                    p_opt.dest not in config['auth'] and
                    self._pw_callback is not None
            ):
                # Defer these until we know all required opts are present
                prompt_options.append(p_opt)

        if msgs:
            raise occ_exceptions.OpenStackConfigException('\n'.join(msgs))
        else:
            for p_opt in prompt_options:
                config['auth'][p_opt.dest] = self._pw_callback(p_opt.prompt)

        return config
