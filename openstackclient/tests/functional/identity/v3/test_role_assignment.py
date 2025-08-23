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

from openstackclient.tests.functional.identity.v3 import common


class RoleAssignmentTests(common.IdentityTests):
    def test_role_assignment_list_no_filters(self):
        raw_output = self.openstack('role assignment list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_user_role_system(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        system = 'all'
        raw_output = self.openstack(
            f'role add --user {username} --system {system} {role_name}'
        )
        self.addCleanup(
            self.openstack,
            f'role remove --user {username} --system  {system} {role_name}',
        )
        self.assertEqual(0, len(raw_output))

        raw_output = self.openstack(f'role assignment list --user {username} ')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

        raw_output = self.openstack(
            f'role assignment list --role {role_name} '
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

        raw_output = self.openstack(f'role assignment list --system {system} ')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_group(self):
        role_name = self._create_dummy_role()
        group = self._create_dummy_group()
        system = 'all'
        raw_output = self.openstack(
            f'role add --group {group} --system {system} {role_name}'
        )
        self.addCleanup(
            self.openstack,
            f'role remove --group {group} --system {system} {role_name}',
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'role assignment list --group {group} ')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_group_domain(self):
        domain_name_A = self._create_dummy_domain()
        domain_name_B = self._create_dummy_domain()
        role_name = self._create_dummy_role()
        group_name = 'group_name'
        self.openstack(f'group create --domain {domain_name_A} {group_name}')
        self.addCleanup(
            self.openstack,
            f'group delete --domain {domain_name_A} {group_name}',
        )
        self.openstack(f'group create --domain {domain_name_B} {group_name}')
        self.addCleanup(
            self.openstack,
            f'group delete --domain {domain_name_B} {group_name}',
        )
        raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--group {group_name} --group-domain {domain_name_A} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {self.project_name} '
            f'--group {group_name} --group-domain {domain_name_A} '
            f'{role_name}',
        )
        self.assertEqual('', raw_output.strip())
        raw_output = self.openstack(
            f'role assignment list '
            f'--group {group_name} --group-domain {domain_name_A} '
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)
        raw_output = self.openstack(
            f'role assignment list '
            f'--group {group_name} --group-domain {domain_name_B} '
        )
        self.assertEqual('', raw_output.strip())

    def test_role_assignment_list_domain(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            f'--domain {self.domain_name} '
            f'--user {username} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--domain {self.domain_name} '
            f'--user {username} '
            f'{role_name}',
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            f'role assignment list --domain {self.domain_name} '
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_user_domain(self):
        domain_name_A = self._create_dummy_domain()
        domain_name_B = self._create_dummy_domain()
        role_name = self._create_dummy_role()
        username = 'username'
        self.openstack(f'user create --domain {domain_name_A} {username}')
        self.addCleanup(
            self.openstack, f'user delete --domain {domain_name_A} {username}'
        )
        self.openstack(f'user create --domain {domain_name_B} {username}')
        self.addCleanup(
            self.openstack, f'user delete --domain {domain_name_B} {username}'
        )
        raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--user {username} --user-domain {domain_name_A} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {self.project_name} '
            f'--user {username} --user-domain {domain_name_A} '
            f'{role_name}',
        )
        self.assertEqual('', raw_output.strip())
        raw_output = self.openstack(
            f'role assignment list '
            f'--user {username} --user-domain {domain_name_A} '
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)
        raw_output = self.openstack(
            f'role assignment list '
            f'--user {username} --user-domain {domain_name_B} '
        )
        self.assertEqual('', raw_output.strip())

    def test_role_assignment_list_role_domain(self):
        domain_name_A = self._create_dummy_domain()
        domain_name_B = self._create_dummy_domain()
        role_name = 'role_name'
        username = 'username'
        self.openstack(f'role create --domain {domain_name_A} {role_name}')
        self.addCleanup(
            self.openstack, f'role delete --domain {domain_name_A} {role_name}'
        )
        self.openstack(f'role create --domain {domain_name_B} {role_name}')
        self.addCleanup(
            self.openstack, f'role delete --domain {domain_name_B} {role_name}'
        )
        self.openstack(f'user create --domain {domain_name_A} {username}')
        self.addCleanup(
            self.openstack, f'user delete --domain {domain_name_A} {username}'
        )
        raw_output = self.openstack(
            'role add '
            f'--user {username} --domain {domain_name_A} '
            f'--role-domain {domain_name_A} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--user {username} --domain {domain_name_A} '
            f'--role-domain {domain_name_A} '
            f'{role_name}',
        )
        self.assertEqual('', raw_output.strip())
        raw_output = self.openstack(
            f'role assignment list '
            f'--role {role_name} --role-domain {domain_name_A}'
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)
        raw_output = self.openstack(
            f'role assignment list '
            f'--role {role_name} --role-domain {domain_name_B}'
        )
        items = self.parse_listing(raw_output)
        self.assertEqual('', raw_output.strip())

    def test_role_assignment_list_project(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--user {username} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {self.project_name} '
            f'--user {username} '
            f'{role_name}',
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            f'role assignment list --project {self.project_name} '
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_project_domain(self):
        domain_name_A = self._create_dummy_domain()
        domain_name_B = self._create_dummy_domain()
        role_name = self._create_dummy_role()
        project_name = 'project_name'
        username = 'username'
        self.openstack(
            f'project create --domain {domain_name_A} {project_name}'
        )
        self.addCleanup(
            self.openstack,
            f'project delete --domain {domain_name_A} {project_name}',
        )
        self.openstack(
            f'project create --domain {domain_name_B} {project_name}'
        )
        self.addCleanup(
            self.openstack,
            f'project delete --domain {domain_name_B} {project_name}',
        )
        self.openstack(f'user create --domain {domain_name_A} {username}')
        self.addCleanup(
            self.openstack, f'user delete --domain {domain_name_A} {username}'
        )
        raw_output = self.openstack(
            'role add '
            f'--project {project_name} --project-domain {domain_name_A} '
            f'--user {username} --user-domain {domain_name_A} '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {project_name} --project-domain {domain_name_A} '
            f'--user {username} --user-domain {domain_name_A} '
            f'{role_name}',
        )
        self.assertEqual('', raw_output.strip())
        raw_output = self.openstack(
            f'role assignment list '
            f'--project {project_name} --project-domain {domain_name_A} '
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)
        raw_output = self.openstack(
            f'role assignment list '
            f'--project {project_name} --project-domain {domain_name_B} '
        )
        self.assertEqual('', raw_output.strip())

    def test_role_assignment_list_effective(self):
        raw_output = self.openstack('role assignment list --effective')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_auth_user(self):
        raw_output = self.openstack('role assignment list --auth-user')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_auth_project(self):
        raw_output = self.openstack('role assignment list --auth-project')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_inherited(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            f'--project {self.project_name} '
            f'--user {username} '
            '--inherited '
            f'{role_name}'
        )
        self.addCleanup(
            self.openstack,
            'role remove '
            f'--project {self.project_name} '
            f'--user {username} '
            '--inherited '
            f'{role_name}',
        )
        self.assertEqual(0, len(raw_output))

        raw_output = self.openstack('role assignment list --inherited')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)

    def test_role_assignment_list_names(self):
        raw_output = self.openstack('role assignment list --names')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ROLE_ASSIGNMENT_LIST_HEADERS)
