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


class RoleTests(common.IdentityTests):

    def test_role_create(self):
        self._create_dummy_role()

    def test_role_delete(self):
        role_name = self._create_dummy_role(add_clean_up=False)
        raw_output = self.openstack('role delete %s' % role_name)
        self.assertEqual(0, len(raw_output))

    def test_role_list(self):
        self._create_dummy_role()
        raw_output = self.openstack('role list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_role_list_with_user_project(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '%(role)s' % {'project': self.project_name,
                          'project_domain': self.domain_name,
                          'user': username,
                          'user_domain': self.domain_name,
                          'role': role_name})
        self.addCleanup(
            self.openstack,
            'role remove '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '%(role)s' % {'project': self.project_name,
                          'project_domain': self.domain_name,
                          'user': username,
                          'user_domain': self.domain_name,
                          'role': role_name})
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            'role list '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '' % {'project': self.project_name,
                  'project_domain': self.domain_name,
                  'user': username,
                  'user_domain': self.domain_name})
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)
        self.assertEqual(1, len(items))

    def test_role_show(self):
        role_name = self._create_dummy_role()
        raw_output = self.openstack('role show %s' % role_name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)

    def test_role_set(self):
        role_name = self._create_dummy_role()
        new_role_name = data_utils.rand_name('NewTestRole')
        raw_output = self.openstack(
            'role set --name %s %s' % (new_role_name, role_name))
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack('role show %s' % new_role_name)
        role = self.parse_show_as_object(raw_output)
        self.assertEqual(new_role_name, role['name'])

    def test_role_add(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '%(role)s' % {'project': self.project_name,
                          'project_domain': self.domain_name,
                          'user': username,
                          'user_domain': self.domain_name,
                          'role': role_name})
        self.addCleanup(
            self.openstack,
            'role remove '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '%(role)s' % {'project': self.project_name,
                          'project_domain': self.domain_name,
                          'user': username,
                          'user_domain': self.domain_name,
                          'role': role_name})
        self.assertEqual(0, len(raw_output))

    def test_role_remove(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        add_raw_output = self.openstack(
            'role add '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '%(role)s' % {'project': self.project_name,
                          'project_domain': self.domain_name,
                          'user': username,
                          'user_domain': self.domain_name,
                          'role': role_name})
        remove_raw_output = self.openstack(
            'role remove '
            '--project %(project)s '
            '--project-domain %(project_domain)s '
            '--user %(user)s '
            '--user-domain %(user_domain)s '
            '%(role)s' % {'project': self.project_name,
                          'project_domain': self.domain_name,
                          'user': username,
                          'user_domain': self.domain_name,
                          'role': role_name})
        self.assertEqual(0, len(add_raw_output))
        self.assertEqual(0, len(remove_raw_output))
