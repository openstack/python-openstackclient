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

"""Object Store v1 API Library Tests"""

from unittest import mock

from keystoneauth1 import session
from requests_mock.contrib import fixture

from openstackclient.api import object_store_v1 as object_store
from openstackclient.tests.unit import utils


FAKE_ACCOUNT = 'q12we34r'
FAKE_AUTH = '11223344556677889900'
FAKE_URL = 'http://gopher.com/v1/' + FAKE_ACCOUNT

FAKE_CONTAINER = 'rainbarrel'
FAKE_OBJECT = 'spigot'

LIST_CONTAINER_RESP = [
    {
        "name": "qaz",
        "count": 0,
        "bytes": 0,
        "last_modified": "2020-05-16T05:52:07.377550",
    },
    {
        "name": "fred",
        "count": 0,
        "bytes": 0,
        "last_modified": "2020-05-16T05:55:07.377550",
    },
]

LIST_OBJECT_RESP = [
    {'name': 'fred', 'bytes': 1234, 'content_type': 'text'},
    {'name': 'wilma', 'bytes': 5678, 'content_type': 'text'},
]


class TestObjectAPIv1(utils.TestCase):
    def setUp(self):
        super().setUp()
        sess = session.Session()
        self.api = object_store.APIv1(session=sess, endpoint=FAKE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestContainer(TestObjectAPIv1):
    def setUp(self):
        super().setUp()

    def test_container_create(self):
        headers = {
            'x-trans-id': '1qaz2wsx',
        }
        self.requests_mock.register_uri(
            'PUT',
            FAKE_URL + '/qaz',
            headers=headers,
            status_code=201,
        )
        ret = self.api.container_create(container='qaz')
        data = {
            'account': FAKE_ACCOUNT,
            'container': 'qaz',
            'x-trans-id': '1qaz2wsx',
        }
        self.assertEqual(data, ret)

    def test_container_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/qaz',
            status_code=204,
        )
        ret = self.api.container_delete(container='qaz')
        self.assertIsNone(ret)

    def test_container_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL,
            json=LIST_CONTAINER_RESP,
            status_code=200,
        )
        ret = self.api.container_list()
        self.assertEqual(LIST_CONTAINER_RESP, ret)

    def test_container_list_prefix(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '?prefix=foo%2f&format=json',
            json=LIST_CONTAINER_RESP,
            status_code=200,
        )
        ret = self.api.container_list(
            prefix='foo/',
        )
        self.assertEqual(LIST_CONTAINER_RESP, ret)

    def test_container_list_marker_limit_end(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '?marker=next&limit=2&end_marker=stop&format=json',
            json=LIST_CONTAINER_RESP,
            status_code=200,
        )
        ret = self.api.container_list(
            marker='next',
            limit=2,
            end_marker='stop',
        )
        self.assertEqual(LIST_CONTAINER_RESP, ret)

    def test_container_list_full_listing(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '?limit=1&format=json',
            json=[LIST_CONTAINER_RESP[0]],
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL
            + '?marker={}&limit=1&format=json'.format(
                LIST_CONTAINER_RESP[0]['name']
            ),
            json=[LIST_CONTAINER_RESP[1]],
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL
            + '?marker={}&limit=1&format=json'.format(
                LIST_CONTAINER_RESP[1]['name']
            ),
            json=[],
            status_code=200,
        )
        ret = self.api.container_list(
            limit=1,
            full_listing=True,
        )
        self.assertEqual(LIST_CONTAINER_RESP, ret)

    def test_container_show(self):
        headers = {
            'X-Container-Meta-Owner': FAKE_ACCOUNT,
            'x-container-object-count': '1',
            'x-container-bytes-used': '577',
            'x-storage-policy': 'o1--sr-r3',
        }
        resp = {
            'account': FAKE_ACCOUNT,
            'container': 'qaz',
            'object_count': '1',
            'bytes_used': '577',
            'storage_policy': 'o1--sr-r3',
            'properties': {'Owner': FAKE_ACCOUNT},
        }
        self.requests_mock.register_uri(
            'HEAD',
            FAKE_URL + '/qaz',
            headers=headers,
            status_code=204,
        )
        ret = self.api.container_show(container='qaz')
        self.assertEqual(resp, ret)


class TestObject(TestObjectAPIv1):
    def setUp(self):
        super().setUp()

    @mock.patch('openstackclient.api.object_store_v1.open')
    def base_object_create(self, file_contents, mock_open):
        mock_open.read.return_value = file_contents

        headers = {
            'etag': 'youreit',
            'x-trans-id': '1qaz2wsx',
        }
        # TODO(dtroyer): When requests_mock gains the ability to
        #                match against request.body add this check
        #                https://review.opendev.org/127316
        self.requests_mock.register_uri(
            'PUT',
            FAKE_URL + '/qaz/counter.txt',
            headers=headers,
            # body=file_contents,
            status_code=201,
        )
        ret = self.api.object_create(
            container='qaz',
            object='counter.txt',
        )
        data = {
            'account': FAKE_ACCOUNT,
            'container': 'qaz',
            'object': 'counter.txt',
            'etag': 'youreit',
            'x-trans-id': '1qaz2wsx',
        }
        self.assertEqual(data, ret)

    def test_object_create(self):
        self.base_object_create('111\n222\n333\n')
        self.base_object_create(bytes([0x31, 0x00, 0x0D, 0x0A, 0x7F, 0xFF]))

    def test_object_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/qaz/wsx',
            status_code=204,
        )
        ret = self.api.object_delete(
            container='qaz',
            object='wsx',
        )
        self.assertIsNone(ret)

    def test_object_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/qaz',
            json=LIST_OBJECT_RESP,
            status_code=200,
        )
        ret = self.api.object_list(container='qaz')
        self.assertEqual(LIST_OBJECT_RESP, ret)

    def test_object_list_delimiter(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/qaz?delimiter=%7C',
            json=LIST_OBJECT_RESP,
            status_code=200,
        )
        ret = self.api.object_list(
            container='qaz',
            delimiter='|',
        )
        self.assertEqual(LIST_OBJECT_RESP, ret)

    def test_object_list_prefix(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/qaz?prefix=foo%2f',
            json=LIST_OBJECT_RESP,
            status_code=200,
        )
        ret = self.api.object_list(
            container='qaz',
            prefix='foo/',
        )
        self.assertEqual(LIST_OBJECT_RESP, ret)

    def test_object_list_marker_limit_end(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/qaz?marker=next&limit=2&end_marker=stop',
            json=LIST_CONTAINER_RESP,
            status_code=200,
        )
        ret = self.api.object_list(
            container='qaz',
            marker='next',
            limit=2,
            end_marker='stop',
        )
        self.assertEqual(LIST_CONTAINER_RESP, ret)

    #     def test_list_objects_full_listing(self):
    #         sess = self.app.client_manager.session
    #
    #         def side_effect(*args, **kwargs):
    #             rv = sess.get().json.return_value
    #             sess.get().json.return_value = []
    #             sess.get().json.side_effect = None
    #             return rv
    #
    #         resp = [{'name': 'is-name'}]
    #         sess.get().json.return_value = resp
    #         sess.get().json.side_effect = side_effect
    #
    #         data = lib_object.list_objects(
    #             sess,
    #             fake_url,
    #             fake_container,
    #             full_listing=True,
    #         )
    #
    #         # Check expected values
    #         sess.get.assert_called_with(
    #             fake_url + '/' + fake_container,
    #             params={
    #                 'format': 'json',
    #                 'marker': 'is-name',
    #             }
    #         )
    #         self.assertEqual(resp, data)

    def test_object_show(self):
        headers = {
            'content-type': 'text/alpha',
            'content-length': '577',
            'last-modified': '20130101',
            'etag': 'qaz',
            'x-container-meta-owner': FAKE_ACCOUNT,
            'x-object-meta-wife': 'Wilma',
            'x-object-meta-Husband': 'fred',
            'x-tra-header': 'yabba-dabba-do',
        }
        resp = {
            'account': FAKE_ACCOUNT,
            'container': 'qaz',
            'object': FAKE_OBJECT,
            'content-type': 'text/alpha',
            'content-length': '577',
            'last-modified': '20130101',
            'etag': 'qaz',
            'properties': {'wife': 'Wilma', 'Husband': 'fred'},
        }
        self.requests_mock.register_uri(
            'HEAD',
            FAKE_URL + '/qaz/' + FAKE_OBJECT,
            headers=headers,
            status_code=204,
        )
        ret = self.api.object_show(
            container='qaz',
            object=FAKE_OBJECT,
        )
        self.assertEqual(resp, ret)
