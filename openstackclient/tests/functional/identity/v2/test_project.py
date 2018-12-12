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

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v2 import common


class ProjectTests(common.IdentityTests):

    def test_project_create(self):
        project_name = data_utils.rand_name('TestProject')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'project create '
            '--description %(description)s '
            '--enable '
            '--property k1=v1 '
            '--property k2=v2 '
            '%(name)s' % {'description': description,
                          'name': project_name})
        self.addCleanup(
            self.openstack,
            'project delete %s' % project_name
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
            'project delete %s' % project_name)
        self.assertEqual(0, len(raw_output))

    def test_project_list(self):
        raw_output = self.openstack('project list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_project_set(self):
        project_name = self._create_dummy_project()
        new_project_name = data_utils.rand_name('NewTestProject')
        raw_output = self.openstack(
            'project set '
            '--name %(new_name)s '
            '--disable '
            '--property k0=v0 '
            '%(name)s' % {'new_name': new_project_name,
                          'name': project_name})
        self.assertEqual(0, len(raw_output))
        # check project details
        raw_output = self.openstack(
            'project show %s' % new_project_name
        )
        items = self.parse_show(raw_output)
        fields = list(self.PROJECT_FIELDS)
        fields.extend(['properties'])
        self.assert_show_fields(items, fields)
        project = self.parse_show_as_object(raw_output)
        self.assertEqual(new_project_name, project['name'])
        self.assertFalse(project['enabled'])
        self.assertEqual("k0='v0'", project['properties'])

    def test_project_show(self):
        project_name = self._create_dummy_project()
        raw_output = self.openstack(
            'project show %s' % project_name
        )
        items = self.parse_show(raw_output)
        fields = list(self.PROJECT_FIELDS)
        fields.extend(['properties'])
        self.assert_show_fields(items, fields)
