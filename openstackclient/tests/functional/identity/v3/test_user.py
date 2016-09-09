#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v3 import common


class UserTests(common.IdentityTests):

    def test_user_create(self):
        self._create_dummy_user()

    def test_user_delete(self):
        username = self._create_dummy_user(add_clean_up=False)
        raw_output = self.openstack('user delete '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': username})
        self.assertEqual(0, len(raw_output))

    def test_user_list(self):
        raw_output = self.openstack('user list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_user_set(self):
        username = self._create_dummy_user()
        raw_output = self.openstack('user show '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': username})
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
        raw_output = self.openstack('user show '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': new_username})
        updated_user = self.parse_show_as_object(raw_output)
        self.assertEqual(user['id'], updated_user['id'])
        self.assertEqual(new_email, updated_user['email'])

    def test_user_set_default_project_id(self):
        username = self._create_dummy_user()
        project_name = self._create_dummy_project()
        # get original user details
        raw_output = self.openstack('user show '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': username})
        user = self.parse_show_as_object(raw_output)
        # update user
        raw_output = self.openstack('user set '
                                    '--project %(project)s '
                                    '--project-domain %(project_domain)s '
                                    '%(id)s' % {'project': project_name,
                                                'project_domain':
                                                    self.domain_name,
                                                'id': user['id']})
        self.assertEqual(0, len(raw_output))
        # get updated user details
        raw_output = self.openstack('user show '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': username})
        updated_user = self.parse_show_as_object(raw_output)
        # get project details
        raw_output = self.openstack('project show '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': project_name})
        project = self.parse_show_as_object(raw_output)
        # check updated user details
        self.assertEqual(user['id'], updated_user['id'])
        self.assertEqual(project['id'], updated_user['default_project_id'])

    def test_user_show(self):
        username = self._create_dummy_user()
        raw_output = self.openstack('user show '
                                    '--domain %(domain)s '
                                    '%(name)s' % {'domain': self.domain_name,
                                                  'name': username})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)
