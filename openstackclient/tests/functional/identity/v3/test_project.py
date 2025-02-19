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


class ProjectTests(common.IdentityTests):
    def test_project_create(self):
        project_name = data_utils.rand_name('TestProject')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'project create '
            f'--domain {self.domain_name} '
            f'--description {description} '
            '--enable '
            '--property k1=v1 '
            '--property k2=v2 '
            f'{project_name}'
        )
        self.addCleanup(
            self.openstack,
            f'project delete --domain {self.domain_name} {project_name}',
        )
        items = self.parse_show(raw_output)
        show_fields = list(self.PROJECT_FIELDS)
        show_fields.extend(['k1', 'k2'])
        self.assert_show_fields(items, show_fields)
        project = self.parse_show_as_object(raw_output)
        self.assertEqual('v1', project['k1'])
        self.assertEqual('v2', project['k2'])

    def test_project_delete(self):
        project_name = self._create_dummy_project(add_clean_up=False)
        raw_output = self.openstack(
            f'project delete --domain {self.domain_name} {project_name}'
        )
        self.assertEqual(0, len(raw_output))

    def test_project_list(self):
        raw_output = self.openstack('project list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_project_list_with_domain(self):
        project_name = self._create_dummy_project()
        raw_output = self.openstack(
            f'project list --domain {self.domain_name}'
        )
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)
        self.assertIn(project_name, raw_output)
        self.assertGreater(len(items), 0)

    def test_project_set(self):
        project_name = self._create_dummy_project()
        new_project_name = data_utils.rand_name('NewTestProject')
        raw_output = self.openstack(
            'project set '
            f'--name {new_project_name} '
            '--disable '
            '--property k0=v0 '
            f'{project_name}'
        )
        self.assertEqual(0, len(raw_output))
        # check project details
        raw_output = self.openstack(
            f'project show --domain {self.domain_name} {new_project_name}'
        )
        items = self.parse_show(raw_output)
        fields = list(self.PROJECT_FIELDS)
        fields.extend(['k0'])
        self.assert_show_fields(items, fields)
        project = self.parse_show_as_object(raw_output)
        self.assertEqual(new_project_name, project['name'])
        self.assertEqual('False', project['enabled'])
        self.assertEqual('v0', project['k0'])
        # reset project to make sure it will be cleaned up
        self.openstack(
            f'project set --name {project_name} --enable {new_project_name}'
        )

    def test_project_show(self):
        raw_output = self.openstack(
            f'project show --domain {self.domain_name} {self.project_name}'
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.PROJECT_FIELDS)

    def test_project_show_with_parents_children(self):
        output = self.openstack(
            'project show '
            '--parents --children '
            f'--domain {self.domain_name} '
            f'{self.project_name}',
            parse_output=True,
        )
        for attr_name in self.PROJECT_FIELDS + ['parents', 'subtree']:
            self.assertIn(attr_name, output)
        self.assertEqual(self.project_name, output.get('name'))
