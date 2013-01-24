#   Copyright 2013 OpenStack, LLC.
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

import mock

from openstackclient.common import clientmanager
from openstackclient.compute import client as compute_client
from tests import utils


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.client = mock.MagicMock()
        self.servers = mock.MagicMock()

        self.client.auth_url = kwargs['auth_url']


class TestCompute(utils.TestCase):
    def setUp(self):
        super(TestCompute, self).setUp()

        self.auth_token = "foobar"
        self.auth_url = "http://0.0.0.0"

        api_version = {"compute": "2"}

        compute_client.API_VERSIONS = {
            "2": "tests.compute.test_compute.FakeClient"
        }

        self.cm = clientmanager.ClientManager(token=self.auth_token,
                                              url=self.auth_url,
                                              auth_url=self.auth_url,
                                              api_version=api_version)

    def test_make_client(self):
        test_servers = [
            ["id 1", "name 1", "status 1", "networks 1"],
            ["id 2", "name 2", "status 2", "networks 2"]
        ]

        self.cm.compute.servers.list.return_value = test_servers

        self.assertEqual(self.cm.compute.servers.list(), test_servers)
        self.assertEqual(self.cm.compute.client.auth_token, self.auth_token)
        self.assertEqual(self.cm.compute.client.auth_url, self.auth_url)
