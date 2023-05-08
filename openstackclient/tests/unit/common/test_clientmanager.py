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

import copy

from keystoneauth1 import token_endpoint
from osc_lib.tests import utils as osc_lib_test_utils

from openstackclient.common import clientmanager
from openstackclient.tests.unit import fakes


class TestClientManager(osc_lib_test_utils.TestClientManager):
    def _clientmanager_class(self):
        """Allow subclasses to override the ClientManager class"""
        return clientmanager.ClientManager

    def test_client_manager_admin_token(self):
        token_auth = {
            'endpoint': fakes.AUTH_URL,
            'token': fakes.AUTH_TOKEN,
        }
        client_manager = self._make_clientmanager(
            auth_args=token_auth,
            auth_plugin_name='admin_token',
        )

        self.assertEqual(
            fakes.AUTH_URL,
            client_manager._cli_options.config['auth']['endpoint'],
        )
        self.assertEqual(
            fakes.AUTH_TOKEN,
            client_manager.auth.get_token(None),
        )
        self.assertIsInstance(
            client_manager.auth,
            token_endpoint.Token,
        )
        self.assertTrue(client_manager.is_network_endpoint_enabled())

    def test_client_manager_network_endpoint_disabled(self):
        auth_args = copy.deepcopy(self.default_password_auth)
        auth_args.update(
            {
                'user_domain_name': 'default',
                'project_domain_name': 'default',
            }
        )
        # v3 fake doesn't have network endpoint
        client_manager = self._make_clientmanager(
            auth_args=auth_args,
            identity_api_version='3',
            auth_plugin_name='v3password',
        )

        self.assertFalse(client_manager.is_service_available('network'))
        # This is True because ClientManager.auth_ref returns None in this
        # test; "no service catalog" means use Network API by default now
        self.assertTrue(client_manager.is_network_endpoint_enabled())
