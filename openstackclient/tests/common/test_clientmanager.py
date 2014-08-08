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

from openstackclient.common import clientmanager
from openstackclient.common import restapi
from openstackclient.tests import utils


AUTH_REF = {'a': 1}
AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"
USERNAME = "itchy"
PASSWORD = "scratchy"
SERVICE_CATALOG = {'sc': '123'}


def FakeMakeClient(instance):
    return FakeClient()


class FakeClient(object):
    auth_ref = AUTH_REF
    auth_token = AUTH_TOKEN
    service_catalog = SERVICE_CATALOG


class Container(object):
    attr = clientmanager.ClientCache(lambda x: object())

    def __init__(self):
        pass


class TestClientCache(utils.TestCase):

    def test_singleton(self):
        # NOTE(dtroyer): Verify that the ClientCache descriptor only invokes
        # the factory one time and always returns the same value after that.
        c = Container()
        self.assertEqual(c.attr, c.attr)


class TestClientManager(utils.TestCase):
    def setUp(self):
        super(TestClientManager, self).setUp()

        clientmanager.ClientManager.identity = \
            clientmanager.ClientCache(FakeMakeClient)

    def test_client_manager_token(self):

        client_manager = clientmanager.ClientManager(
            token=AUTH_TOKEN,
            url=AUTH_URL,
            verify=True,
        )

        self.assertEqual(
            AUTH_TOKEN,
            client_manager._token,
        )
        self.assertEqual(
            AUTH_URL,
            client_manager._url,
        )
        self.assertIsInstance(
            client_manager.session,
            restapi.RESTApi,
        )
        self.assertFalse(client_manager._insecure)
        self.assertTrue(client_manager._verify)

    def test_client_manager_password(self):

        client_manager = clientmanager.ClientManager(
            auth_url=AUTH_URL,
            username=USERNAME,
            password=PASSWORD,
            verify=False,
        )

        self.assertEqual(
            AUTH_URL,
            client_manager._auth_url,
        )
        self.assertEqual(
            USERNAME,
            client_manager._username,
        )
        self.assertEqual(
            PASSWORD,
            client_manager._password,
        )
        self.assertIsInstance(
            client_manager.session,
            restapi.RESTApi,
        )
        self.assertTrue(client_manager._insecure)
        self.assertFalse(client_manager._verify)

        # These need to stick around until the old-style clients are gone
        self.assertEqual(
            AUTH_REF,
            client_manager.auth_ref,
        )
        self.assertEqual(
            AUTH_TOKEN,
            client_manager._token,
        )
        self.assertEqual(
            SERVICE_CATALOG,
            client_manager._service_catalog,
        )

    def test_client_manager_password_verify_ca(self):

        client_manager = clientmanager.ClientManager(
            auth_url=AUTH_URL,
            username=USERNAME,
            password=PASSWORD,
            verify='cafile',
        )

        self.assertFalse(client_manager._insecure)
        self.assertTrue(client_manager._verify)
        self.assertEqual('cafile', client_manager._cacert)
