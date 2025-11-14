# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

from openstack import exceptions as sdk_exc
from openstack.identity.v3 import user as _user
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.identity import common
from openstackclient.tests.unit import utils as test_utils


class TestFindSDKId(test_utils.TestCase):
    def setUp(self):
        super().setUp()
        self.user = sdk_fakes.generate_fake_resource(_user.User)
        self.identity_sdk_client = mock.Mock()
        self.identity_sdk_client.find_user = mock.Mock()

    def test_find_sdk_id_validate(self):
        self.identity_sdk_client.find_user.side_effect = [self.user]

        result = common._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=True,
        )
        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_no_validate(self):
        self.identity_sdk_client.find_user.side_effect = [self.user]

        result = common._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=False,
        )
        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_not_found_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        self.assertRaises(
            exceptions.CommandError,
            common._find_sdk_id,
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=True,
        )

    def test_find_sdk_id_not_found_no_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ResourceNotFound,
        ]

        result = common._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=False,
        )
        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_forbidden_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ForbiddenException,
        ]

        result = common._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=True,
        )

        self.assertEqual(self.user.id, result)

    def test_find_sdk_id_forbidden_no_validate(self):
        self.identity_sdk_client.find_user.side_effect = [
            sdk_exc.ForbiddenException,
        ]

        result = common._find_sdk_id(
            self.identity_sdk_client.find_user,
            name_or_id=self.user.id,
            validate_actor_existence=False,
        )

        self.assertEqual(self.user.id, result)
