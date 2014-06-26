#   Copyright 2013 Nebula Inc.
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

"""Test rest module"""

import json
import mock

import requests
import six

from openstackclient.common import restapi
from openstackclient.tests import utils

fake_user_agent = 'test_rapi'

fake_auth = '11223344556677889900'
fake_url = 'http://gopher.com'
fake_key = 'gopher'
fake_keys = 'gophers'
fake_gopher_mac = {
    'id': 'g1',
    'name': 'mac',
    'actor': 'Mel Blanc',
}
fake_gopher_tosh = {
    'id': 'g2',
    'name': 'tosh',
    'actor': 'Stan Freeberg',
}
fake_gopher_single = {
    fake_key: fake_gopher_mac,
}
fake_gopher_list = {
    fake_keys:
        [
            fake_gopher_mac,
            fake_gopher_tosh,
        ]
}
fake_headers = {
    'User-Agent': fake_user_agent,
}


class FakeResponse(requests.Response):
    def __init__(self, headers={}, status_code=200, data=None, encoding=None):
        super(FakeResponse, self).__init__()

        self.status_code = status_code

        self.headers.update(headers)
        self._content = json.dumps(data)
        if not isinstance(self._content, six.binary_type):
            self._content = self._content.encode()


@mock.patch('openstackclient.common.restapi.requests.Session')
class TestRESTApi(utils.TestCase):

    def test_request_get(self, session_mock):
        resp = FakeResponse(status_code=200, data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi(
            user_agent=fake_user_agent,
        )
        gopher = api.request('GET', fake_url)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers={},
            allow_redirects=True,
        )
        self.assertEqual(gopher.status_code, 200)
        self.assertEqual(gopher.json(), fake_gopher_single)

    def test_request_get_return_300(self, session_mock):
        resp = FakeResponse(status_code=300, data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi(
            user_agent=fake_user_agent,
        )
        gopher = api.request('GET', fake_url)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers={},
            allow_redirects=True,
        )
        self.assertEqual(gopher.status_code, 300)
        self.assertEqual(gopher.json(), fake_gopher_single)

    def test_request_get_fail_404(self, session_mock):
        resp = FakeResponse(status_code=404, data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi(
            user_agent=fake_user_agent,
        )
        self.assertRaises(requests.HTTPError, api.request, 'GET', fake_url)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers={},
            allow_redirects=True,
        )

    def test_request_get_auth(self, session_mock):
        resp = FakeResponse(data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
            headers=mock.MagicMock(return_value={}),
        )

        api = restapi.RESTApi(
            auth_header=fake_auth,
            user_agent=fake_user_agent,
        )
        gopher = api.request('GET', fake_url)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers={
                'X-Auth-Token': fake_auth,
            },
            allow_redirects=True,
        )
        self.assertEqual(gopher.json(), fake_gopher_single)

    def test_request_post(self, session_mock):
        resp = FakeResponse(data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi(
            user_agent=fake_user_agent,
        )
        data = fake_gopher_tosh
        gopher = api.request('POST', fake_url, json=data)
        session_mock.return_value.request.assert_called_with(
            'POST',
            fake_url,
            headers={
                'Content-Type': 'application/json',
            },
            allow_redirects=True,
            data=json.dumps(data),
        )
        self.assertEqual(gopher.json(), fake_gopher_single)

    # Methods
    # TODO(dtroyer): add the other method methods

    def test_delete(self, session_mock):
        resp = FakeResponse(status_code=200, data=None)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi()
        gopher = api.delete(fake_url)
        session_mock.return_value.request.assert_called_with(
            'DELETE',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
        )
        self.assertEqual(gopher.status_code, 200)

    # Commands

    def test_create(self, session_mock):
        resp = FakeResponse(data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi()
        data = fake_gopher_mac

        # Test no key
        gopher = api.create(fake_url, data=data)
        session_mock.return_value.request.assert_called_with(
            'POST',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            data=json.dumps(data),
        )
        self.assertEqual(gopher, fake_gopher_single)

        # Test with key
        gopher = api.create(fake_url, data=data, response_key=fake_key)
        session_mock.return_value.request.assert_called_with(
            'POST',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            data=json.dumps(data),
        )
        self.assertEqual(gopher, fake_gopher_mac)

    def test_list(self, session_mock):
        resp = FakeResponse(data=fake_gopher_list)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        # test base
        api = restapi.RESTApi()
        gopher = api.list(fake_url, response_key=fake_keys)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
        )
        self.assertEqual(gopher, [fake_gopher_mac, fake_gopher_tosh])

        # test body
        api = restapi.RESTApi()
        data = {'qwerty': 1}
        gopher = api.list(fake_url, response_key=fake_keys, data=data)
        session_mock.return_value.request.assert_called_with(
            'POST',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            data=json.dumps(data),
        )
        self.assertEqual(gopher, [fake_gopher_mac, fake_gopher_tosh])

        # test query params
        api = restapi.RESTApi()
        params = {'qaz': '123'}
        gophers = api.list(fake_url, response_key=fake_keys, params=params)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            params=params,
        )
        self.assertEqual(gophers, [fake_gopher_mac, fake_gopher_tosh])

    def test_set(self, session_mock):
        new_gopher = fake_gopher_single
        new_gopher[fake_key]['name'] = 'Chip'
        resp = FakeResponse(data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi()
        data = fake_gopher_mac
        data['name'] = 'Chip'

        # Test no data, no key
        gopher = api.set(fake_url)
        session_mock.return_value.request.assert_called_with(
            'PUT',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            json=None,
        )
        self.assertEqual(gopher, None)

        # Test data, no key
        gopher = api.set(fake_url, data=data)
        session_mock.return_value.request.assert_called_with(
            'PUT',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            data=json.dumps(data),
        )
        self.assertEqual(gopher, fake_gopher_single)

        # NOTE:(dtroyer): Key and no data is not tested as without data
        #                 the response_key is moot

        # Test data and key
        gopher = api.set(fake_url, data=data, response_key=fake_key)
        session_mock.return_value.request.assert_called_with(
            'PUT',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
            data=json.dumps(data),
        )
        self.assertEqual(gopher, fake_gopher_mac)

    def test_show(self, session_mock):
        resp = FakeResponse(data=fake_gopher_single)
        session_mock.return_value = mock.MagicMock(
            request=mock.MagicMock(return_value=resp),
        )

        api = restapi.RESTApi()

        # Test no key
        gopher = api.show(fake_url)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
        )
        self.assertEqual(gopher, fake_gopher_single)

        # Test with key
        gopher = api.show(fake_url, response_key=fake_key)
        session_mock.return_value.request.assert_called_with(
            'GET',
            fake_url,
            headers=mock.ANY,
            allow_redirects=True,
        )
        self.assertEqual(gopher, fake_gopher_mac)
