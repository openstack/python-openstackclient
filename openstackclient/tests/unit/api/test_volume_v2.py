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

"""Volume v2 API Library Tests"""

import http
from unittest import mock
import uuid

from openstack.block_storage.v2 import _proxy
from osc_lib import exceptions as osc_lib_exceptions

from openstackclient.api import volume_v2 as volume
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils


class TestConsistencyGroup(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.volume_sdk_client = mock.Mock(_proxy.Proxy)

    def test_find_consistency_group_by_id(self):
        cg_id = uuid.uuid4().hex
        cg_name = 'name-' + uuid.uuid4().hex
        data = {
            'consistencygroup': {
                'id': cg_id,
                'name': cg_name,
                'status': 'available',
                'availability_zone': 'az1',
                'created_at': '2015-09-16T09:28:52.000000',
                'description': 'description-' + uuid.uuid4().hex,
                'volume_types': ['123456'],
            }
        }
        self.volume_sdk_client.get.side_effect = [
            fakes.FakeResponse(data=data),
        ]

        result = volume.find_consistency_group(self.volume_sdk_client, cg_id)

        self.volume_sdk_client.get.assert_has_calls(
            [
                mock.call(f'/consistencygroups/{cg_id}'),
            ]
        )
        self.assertEqual(data['consistencygroup'], result)

    def test_find_consistency_group_by_name(self):
        cg_id = uuid.uuid4().hex
        cg_name = 'name-' + uuid.uuid4().hex
        data = {
            'consistencygroups': [
                {
                    'id': cg_id,
                    'name': cg_name,
                }
            ],
        }
        self.volume_sdk_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]

        result = volume.find_consistency_group(self.volume_sdk_client, cg_name)

        self.volume_sdk_client.get.assert_has_calls(
            [
                mock.call(f'/consistencygroups/{cg_name}'),
                mock.call('/consistencygroups'),
            ]
        )
        self.assertEqual(data['consistencygroups'][0], result)

    def test_find_consistency_group_not_found(self):
        data = {'consistencygroups': []}
        self.volume_sdk_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            volume.find_consistency_group,
            self.volume_sdk_client,
            'invalid-cg',
        )

    def test_find_consistency_group_by_name_duplicate(self):
        cg_name = 'name-' + uuid.uuid4().hex
        data = {
            'consistencygroups': [
                {
                    'id': uuid.uuid4().hex,
                    'name': cg_name,
                },
                {
                    'id': uuid.uuid4().hex,
                    'name': cg_name,
                },
            ],
        }
        self.volume_sdk_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]

        self.assertRaises(
            osc_lib_exceptions.NotFound,
            volume.find_consistency_group,
            self.volume_sdk_client,
            cg_name,
        )
