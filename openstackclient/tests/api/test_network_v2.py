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

"""Network v2 API Library Tests"""

from requests_mock.contrib import fixture

from keystoneclient import session
from openstackclient.api import network_v2 as network
from openstackclient.tests import utils


FAKE_PROJECT = 'xyzpdq'
FAKE_URL = 'http://gopher.com/v2/' + FAKE_PROJECT


class TestNetworkAPIv2(utils.TestCase):

    def setUp(self):
        super(TestNetworkAPIv2, self).setUp()
        sess = session.Session()
        self.api = network.APIv2(session=sess, endpoint=FAKE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestNetwork(TestNetworkAPIv2):

    LIST_NETWORK_RESP = [
        {'id': '1', 'name': 'p1', 'description': 'none', 'enabled': True},
        {'id': '2', 'name': 'p2', 'description': 'none', 'enabled': False},
        {'id': '3', 'name': 'p3', 'description': 'none', 'enabled': True},
    ]

    def test_network_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/networks',
            json={'networks': self.LIST_NETWORK_RESP},
            status_code=200,
        )
        ret = self.api.network_list()
        self.assertEqual(self.LIST_NETWORK_RESP, ret)
