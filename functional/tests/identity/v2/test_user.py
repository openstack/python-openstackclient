# Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest_lib.common.utils import data_utils

from functional.common import exceptions
from functional.tests.identity.v2 import test_identity


class UserTests(test_identity.IdentityTests):

    def test_user_create(self):
        self._create_dummy_user()

    def test_user_delete(self):
        username = self._create_dummy_user(add_clean_up=False)
        raw_output = self.openstack('user delete %s' % username)
        self.assertEqual(0, len(raw_output))

    def test_user_list(self):
        raw_output = self.openstack('user list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, test_identity.BASIC_LIST_HEADERS)

    def test_user_set(self):
        username = self._create_dummy_user()
        raw_output = self.openstack('user show %s' % username)
        user = self.parse_show_as_object(raw_output)
        new_username = data_utils.rand_name('NewTestUser')
        new_email = data_utils.rand_name() + '@example.com'
        raw_output = self.openstack('user set '
                                    '--email %(email)s '
                                    '--name %(new_name)s '
                                    '%(id)s' % {'email': new_email,
                                                'new_name': new_username,
                                                'id': user['id']})
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack('user show %s' % new_username)
        new_user = self.parse_show_as_object(raw_output)
        self.assertEqual(user['id'], new_user['id'])
        self.assertEqual(new_email, new_user['email'])

    def test_user_show(self):
        username = self._create_dummy_user()
        raw_output = self.openstack('user show %s' % username)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)

    def test_bad_user_command(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.openstack, 'user unlist')
