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

import json as jsonutils
import mock
from requests_mock.contrib import fixture

from keystoneclient.auth.identity import v2 as auth_v2
from keystoneclient import service_catalog

from openstackclient.api import auth
from openstackclient.api import auth_plugin
from openstackclient.common import clientmanager
from openstackclient.common import exceptions as exc
from openstackclient.tests import fakes
from openstackclient.tests import utils


API_VERSION = {"identity": "2.0"}

AUTH_REF = {'version': 'v2.0'}
AUTH_REF.update(fakes.TEST_RESPONSE_DICT['access'])
SERVICE_CATALOG = service_catalog.ServiceCatalogV2(AUTH_REF)


# This is deferred in api.auth but we need it here...
auth.get_options_list()


class Container(object):
    attr = clientmanager.ClientCache(lambda x: object())

    def __init__(self):
        pass


class FakeOptions(object):
    def __init__(self, **kwargs):
        for option in auth.OPTIONS_LIST:
            setattr(self, option.replace('-', '_'), None)
        self.auth_type = None
        self.identity_api_version = '2.0'
        self.timing = None
        self.region_name = None
        self.interface = None
        self.url = None
        self.auth = {}
        self.default_domain = 'default'
        self.__dict__.update(kwargs)


class TestClientCache(utils.TestCase):

    def test_singleton(self):
        # NOTE(dtroyer): Verify that the ClientCache descriptor only invokes
        # the factory one time and always returns the same value after that.
        c = Container()
        self.assertEqual(c.attr, c.attr)


class TestClientManager(utils.TestCase):
    def setUp(self):
        super(TestClientManager, self).setUp()
        self.mock = mock.Mock()
        self.requests = self.useFixture(fixture.Fixture())
        # fake v2password token retrieval
        self.stub_auth(json=fakes.TEST_RESPONSE_DICT)
        # fake v3password token retrieval
        self.stub_auth(json=fakes.TEST_RESPONSE_DICT_V3,
                       url='/'.join([fakes.AUTH_URL, 'auth/tokens']))
        # fake password version endpoint discovery
        self.stub_auth(json=fakes.TEST_VERSIONS,
                       url=fakes.AUTH_URL,
                       verb='GET')

    def test_client_manager_token_endpoint(self):

        client_manager = clientmanager.ClientManager(
            cli_options=FakeOptions(
                auth_type='token_endpoint',
                auth=dict(
                    token=fakes.AUTH_TOKEN,
                    url=fakes.AUTH_URL,
                ),
            ),
            api_version=API_VERSION,
            verify=True
        )
        client_manager.setup_auth()

        self.assertEqual(
            fakes.AUTH_URL,
            client_manager._url,
        )
        self.assertEqual(
            fakes.AUTH_TOKEN,
            client_manager.auth.get_token(None),
        )
        self.assertIsInstance(
            client_manager.auth,
            auth_plugin.TokenEndpoint,
        )
        self.assertFalse(client_manager._insecure)
        self.assertTrue(client_manager._verify)

    def test_client_manager_token(self):

        client_manager = clientmanager.ClientManager(
            cli_options=FakeOptions(
                auth=dict(
                    token=fakes.AUTH_TOKEN,
                    auth_url=fakes.AUTH_URL,
                ),
                auth_type='v2token',
                interface=fakes.INTERFACE,
                region_name=fakes.REGION_NAME,
            ),
            api_version=API_VERSION,
            verify=True
        )
        client_manager.setup_auth()

        self.assertEqual(
            fakes.AUTH_URL,
            client_manager._auth_url,
        )
        self.assertIsInstance(
            client_manager.auth,
            auth_v2.Token,
        )
        self.assertEqual(
            fakes.INTERFACE,
            client_manager._interface,
        )
        self.assertEqual(
            fakes.REGION_NAME,
            client_manager._region_name,
        )
        self.assertFalse(client_manager._insecure)
        self.assertTrue(client_manager._verify)

    def test_client_manager_password(self):

        client_manager = clientmanager.ClientManager(
            cli_options=FakeOptions(
                auth=dict(
                    auth_url=fakes.AUTH_URL,
                    username=fakes.USERNAME,
                    password=fakes.PASSWORD,
                    project_name=fakes.PROJECT_NAME,
                ),
            ),
            api_version=API_VERSION,
            verify=False,
        )
        client_manager.setup_auth()

        self.assertEqual(
            fakes.AUTH_URL,
            client_manager._auth_url,
        )
        self.assertEqual(
            fakes.USERNAME,
            client_manager._username,
        )
        self.assertEqual(
            fakes.PASSWORD,
            client_manager._password,
        )
        self.assertIsInstance(
            client_manager.auth,
            auth_v2.Password,
        )
        self.assertTrue(client_manager._insecure)
        self.assertFalse(client_manager._verify)

        # These need to stick around until the old-style clients are gone
        self.assertEqual(
            AUTH_REF,
            client_manager.auth_ref,
        )
        self.assertEqual(
            dir(SERVICE_CATALOG),
            dir(client_manager.auth_ref.service_catalog),
        )

    def stub_auth(self, json=None, url=None, verb=None, **kwargs):
        subject_token = fakes.AUTH_TOKEN
        base_url = fakes.AUTH_URL
        if json:
            text = jsonutils.dumps(json)
            headers = {'X-Subject-Token': subject_token,
                       'Content-Type': 'application/json'}
        if not url:
            url = '/'.join([base_url, 'tokens'])
        url = url.replace("/?", "?")
        if not verb:
            verb = 'POST'
        self.requests.register_uri(verb,
                                   url,
                                   headers=headers,
                                   text=text)

    def test_client_manager_password_verify_ca(self):

        client_manager = clientmanager.ClientManager(
            cli_options=FakeOptions(
                auth=dict(
                    auth_url=fakes.AUTH_URL,
                    username=fakes.USERNAME,
                    password=fakes.PASSWORD,
                    project_name=fakes.PROJECT_NAME,
                ),
                auth_type='v2password',
            ),
            api_version=API_VERSION,
            verify='cafile',
        )
        client_manager.setup_auth()

        self.assertFalse(client_manager._insecure)
        self.assertTrue(client_manager._verify)
        self.assertEqual('cafile', client_manager._cacert)

    def _select_auth_plugin(self, auth_params, api_version, auth_plugin_name):
        auth_params['auth_type'] = auth_plugin_name
        auth_params['identity_api_version'] = api_version
        client_manager = clientmanager.ClientManager(
            cli_options=FakeOptions(**auth_params),
            api_version=API_VERSION,
            verify=True
        )
        client_manager.setup_auth()

        self.assertEqual(
            auth_plugin_name,
            client_manager.auth_plugin_name,
        )

    def test_client_manager_select_auth_plugin(self):
        # test token auth
        params = dict(
            auth=dict(
                auth_url=fakes.AUTH_URL,
                token=fakes.AUTH_TOKEN,
            ),
        )
        self._select_auth_plugin(params, '2.0', 'v2token')
        self._select_auth_plugin(params, '3', 'v3token')
        self._select_auth_plugin(params, 'XXX', 'token')
        # test token/endpoint auth
        params = dict(
            auth_plugin='token_endpoint',
            auth=dict(
                url='test',
                token=fakes.AUTH_TOKEN,
            ),
        )
        self._select_auth_plugin(params, 'XXX', 'token_endpoint')
        # test password auth
        params = dict(
            auth=dict(
                auth_url=fakes.AUTH_URL,
                username=fakes.USERNAME,
                password=fakes.PASSWORD,
                project_name=fakes.PROJECT_NAME,
            ),
        )
        self._select_auth_plugin(params, '2.0', 'v2password')
        self._select_auth_plugin(params, '3', 'v3password')
        self._select_auth_plugin(params, 'XXX', 'password')

    def test_client_manager_select_auth_plugin_failure(self):
        client_manager = clientmanager.ClientManager(
            cli_options=FakeOptions(os_auth_plugin=''),
            api_version=API_VERSION,
            verify=True,
        )
        self.assertRaises(
            exc.CommandError,
            client_manager.setup_auth,
        )
