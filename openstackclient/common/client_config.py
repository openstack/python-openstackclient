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

from osc_lib.cli import client_config


# Sublcass OpenStackConfig in order to munge config values
# before auth plugins are loaded
class OSC_Config(client_config.OSC_Config):

    # TODO(dtroyer): Remove _auth_default_domain when the v3otp fix is
    #                backported to osc-lib, should be in release 1.3.0
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
                    auth_type in ("password", "v3password", "v3totp") and
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

    def load_auth_plugin(self, config):
        """Get auth plugin and validate args"""

        loader = self._get_auth_loader(config)
        config = self._validate_auth(config, loader)
        auth_plugin = loader.load_from_options(**config['auth'])
        return auth_plugin
