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

"""API Test Fakes"""

from keystoneauth1 import session
from requests_mock.contrib import fixture

from openstackclient.tests.unit import utils


RESP_ITEM_1 = {
    'id': '1',
    'name': 'alpha',
    'status': 'UP',
    'props': {'a': 1, 'b': 2},
}
RESP_ITEM_2 = {
    'id': '2',
    'name': 'beta',
    'status': 'DOWN',
    'props': {'a': 2, 'b': 2},
}
RESP_ITEM_3 = {
    'id': '3',
    'name': 'delta',
    'status': 'UP',
    'props': {'a': 3, 'b': 1},
}

LIST_RESP = [RESP_ITEM_1, RESP_ITEM_2]

LIST_BODY = {
    'p1': 'xxx',
    'p2': 'yyy',
}


class TestSession(utils.TestCase):
    BASE_URL = 'https://api.example.com:1234/vX'

    def setUp(self):
        super().setUp()
        self.sess = session.Session()
        self.requests_mock = self.useFixture(fixture.Fixture())
