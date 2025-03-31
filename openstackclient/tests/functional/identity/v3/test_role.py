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

    def test_role_create_with_description(self):
        role_name = data_utils.rand_name('TestRole')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            f'role create --description {description} {role_name}'
        )
        role = self.parse_show_as_object(raw_output)
        self.addCleanup(self.openstack, 'role delete {}'.format(role['id']))
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)
        self.assertEqual(description, role['description'])
        return role_name

    def test_role_delete(self):
        role_name = self._create_dummy_role(add_clean_up=False)
        raw_output = self.openstack(f'role delete {role_name}')
        self.assertEqual(0, len(raw_output))

    def test_role_list(self):
        self._create_dummy_role()
        raw_output = self.openstack('role list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_role_show(self):
        role_name = self._create_dummy_role()
        raw_output = self.openstack(f'role show {role_name}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)

    def test_role_set(self):
        role_name = self._create_dummy_role()
        new_role_name = data_utils.rand_name('NewTestRole')
        raw_output = self.openstack(
            f'role set --name {new_role_name} {role_name}'
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'role show {new_role_name}')
        role = self.parse_show_as_object(raw_output)
        self.assertEqual(new_role_name, role['name'])

    def test_role_set_description(self):
        role_name = self._create_dummy_role()
        description = data_utils.rand_name("NewDescription")
        raw_output = self.openstack(
            f'role set --description {description} {role_name}'
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'role show {role_name}')
        role = self.parse_show_as_object(raw_output)
        self.assertEqual(description, role['description'])

    def test_role_add(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--user {username} '
            f'--user-domain {self.domain_name} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--user {username} '
            f'--user-domain {self.domain_name} '
            f'{role_name}',
        )
        self.assertEqual(0, len(raw_output))

    def test_role_add_inherited(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--user {username} '
            f'--user-domain {self.domain_name} '
            '--inherited '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--user {username} '
            f'--user-domain {self.domain_name} '
            '--inherited '
            f'{role_name}',
        )
        self.assertEqual(0, len(raw_output))

    def test_role_remove(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        add_raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--user {username} '
            f'--user-domain {self.domain_name} '
            f'{role_name}'
        )
        remove_raw_output = self.openstack(
            'role remove '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--user {username} '
            f'--user-domain {self.domain_name} '
            f'{role_name}'
        )
        self.assertEqual(0, len(add_raw_output))
        self.assertEqual(0, len(remove_raw_output))

    def test_implied_role_list(self):
        raw_output = self.openstack('implied role list')
        default_roles = self.parse_listing(raw_output)
        self.assert_table_structure(
            default_roles, self.IMPLIED_ROLE_LIST_HEADERS
        )

        self._create_dummy_implied_role()
        raw_output = self.openstack('implied role list')
        current_roles = self.parse_listing(raw_output)
        self.assert_table_structure(
            current_roles, self.IMPLIED_ROLE_LIST_HEADERS
        )
        self.assertEqual(len(default_roles) + 1, len(current_roles))

    def test_implied_role_create(self):
        role_name = self._create_dummy_role()
        implied_role_name = self._create_dummy_role()
        self.openstack(
            'implied role create '
            f'--implied-role {implied_role_name} '
            f'{role_name}'
        )

    def test_implied_role_delete(self):
        implied_role_name, role_name = self._create_dummy_implied_role()
        raw_output = self.openstack(
            'implied role delete '
            f'--implied-role {implied_role_name} '
            f'{role_name}'
        )
        self.assertEqual(0, len(raw_output))
