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

"""Test Object API library module"""

from __future__ import unicode_literals

import mock


from openstackclient.object.v1.lib import container as lib_container
from openstackclient.tests.common import test_restapi as restapi
from openstackclient.tests import fakes
from openstackclient.tests import utils


fake_auth = '11223344556677889900'
fake_url = 'http://gopher.com'

fake_container = 'rainbarrel'


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.endpoint = fake_url
        self.token = fake_auth


class TestObject(utils.TestCommand):

    def setUp(self):
        super(TestObject, self).setUp()
        self.app.client_manager = fakes.FakeClientManager()
        self.app.client_manager.object = FakeClient()
        self.app.restapi = mock.MagicMock()


class TestObjectListContainers(TestObject):

    def test_list_containers_no_options(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.request.return_value = restapi.FakeResponse(data=resp)

        data = lib_container.list_containers(
            self.app.restapi,
            self.app.client_manager.object.endpoint,
        )

        # Check expected values
        self.app.restapi.request.assert_called_with(
            'GET',
            fake_url + '?format=json',
        )
        self.assertEqual(data, resp)

    def test_list_containers_marker(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.request.return_value = restapi.FakeResponse(data=resp)

        data = lib_container.list_containers(
            self.app.restapi,
            self.app.client_manager.object.endpoint,
            marker='next',
        )

        # Check expected values
        self.app.restapi.request.assert_called_with(
            'GET',
            fake_url + '?format=json&marker=next',
        )
        self.assertEqual(data, resp)

    def test_list_containers_limit(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.request.return_value = restapi.FakeResponse(data=resp)

        data = lib_container.list_containers(
            self.app.restapi,
            self.app.client_manager.object.endpoint,
            limit=5,
        )

        # Check expected values
        self.app.restapi.request.assert_called_with(
            'GET',
            fake_url + '?format=json&limit=5',
        )
        self.assertEqual(data, resp)

    def test_list_containers_end_marker(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.request.return_value = restapi.FakeResponse(data=resp)

        data = lib_container.list_containers(
            self.app.restapi,
            self.app.client_manager.object.endpoint,
            end_marker='last',
        )

        # Check expected values
        self.app.restapi.request.assert_called_with(
            'GET',
            fake_url + '?format=json&end_marker=last',
        )
        self.assertEqual(data, resp)

    def test_list_containers_prefix(self):
        resp = [{'name': 'is-name'}]
        self.app.restapi.request.return_value = restapi.FakeResponse(data=resp)

        data = lib_container.list_containers(
            self.app.restapi,
            self.app.client_manager.object.endpoint,
            prefix='foo/',
        )

        # Check expected values
        self.app.restapi.request.assert_called_with(
            'GET',
            fake_url + '?format=json&prefix=foo/',
        )
        self.assertEqual(data, resp)

    def test_list_containers_full_listing(self):

        def side_effect(*args, **kwargs):
            rv = self.app.restapi.request.return_value
            self.app.restapi.request.return_value = restapi.FakeResponse(
                data=[],
            )
            self.app.restapi.request.side_effect = None
            return rv

        resp = [{'name': 'is-name'}]
        self.app.restapi.request.return_value = restapi.FakeResponse(data=resp)
        self.app.restapi.request.side_effect = side_effect

        data = lib_container.list_containers(
            self.app.restapi,
            self.app.client_manager.object.endpoint,
            full_listing=True,
        )

        # Check expected values
        self.app.restapi.request.assert_called_with(
            'GET',
            fake_url + '?format=json&marker=is-name',
        )
        self.assertEqual(data, resp)
