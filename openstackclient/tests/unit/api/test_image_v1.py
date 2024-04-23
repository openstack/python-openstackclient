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

"""Image v1 API Library Tests"""

from keystoneauth1 import session
from requests_mock.contrib import fixture

from openstackclient.api import image_v1
from openstackclient.tests.unit import utils


FAKE_PROJECT = 'xyzpdq'
FAKE_URL = 'http://gopher.dev10.com'


class TestImageAPIv1(utils.TestCase):
    def setUp(self):
        super().setUp()

        sess = session.Session()
        self.api = image_v1.APIv1(session=sess, endpoint=FAKE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestImage(TestImageAPIv1):
    PUB_PROT = {
        'id': '1',
        'name': 'pub1',
        'is_public': True,
        'protected': True,
    }
    PUB_NOPROT = {
        'id': '2',
        'name': 'pub2-noprot',
        'is_public': True,
        'protected': False,
    }
    NOPUB_PROT = {
        'id': '3',
        'name': 'priv3',
        'is_public': False,
        'protected': True,
    }
    NOPUB_NOPROT = {
        'id': '4',
        'name': 'priv4-noprot',
        'is_public': False,
        'protected': False,
    }
    LIST_IMAGE_RESP = [
        PUB_PROT,
        PUB_NOPROT,
        NOPUB_PROT,
        NOPUB_NOPROT,
    ]

    def test_image_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/v1/images',
            json={'images': self.LIST_IMAGE_RESP},
            status_code=200,
        )
        ret = self.api.image_list()
        self.assertEqual(self.LIST_IMAGE_RESP, ret)

    def test_image_list_public(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/v1/images/detail',
            json={'images': self.LIST_IMAGE_RESP},
            status_code=200,
        )
        ret = self.api.image_list(public=True)
        self.assertEqual([self.PUB_PROT, self.PUB_NOPROT], ret)

    def test_image_list_private(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/v1/images/detail',
            json={'images': self.LIST_IMAGE_RESP},
            status_code=200,
        )
        ret = self.api.image_list(private=True)
        self.assertEqual([self.NOPUB_PROT, self.NOPUB_NOPROT], ret)
