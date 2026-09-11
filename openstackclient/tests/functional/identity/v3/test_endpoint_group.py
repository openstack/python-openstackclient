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

import json
import tempfile

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v3 import common


class EndpointGroupTests(common.IdentityTests):
    def test_endpoint_group_create(self):
        self._create_dummy_endpoint_group()

    def test_endpoint_group_delete(self):
        endpoint_group_id = self._create_dummy_endpoint_group(
            add_clean_up=False
        )
        raw_output = self.openstack(
            f'endpoint group delete {endpoint_group_id}'
        )
        self.assertEqual(0, len(raw_output))

    def test_endpoint_group_multi_delete(self):
        endpoint_group_1 = self._create_dummy_endpoint_group(
            add_clean_up=False
        )
        endpoint_group_2 = self._create_dummy_endpoint_group(
            add_clean_up=False
        )
        raw_output = self.openstack(
            f'endpoint group delete {endpoint_group_1} {endpoint_group_2}'
        )
        self.assertEqual(0, len(raw_output))

    def test_endpoint_group_list(self):
        endpoint_group_id = self._create_dummy_endpoint_group()
        raw_output = self.openstack('endpoint group list')
        self.assertIn(endpoint_group_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_GROUP_LIST_HEADERS)

    def test_endpoint_group_set(self):
        endpoint_group_id = self._create_dummy_endpoint_group()
        new_name = data_utils.rand_name()
        new_description = data_utils.arbitrary_string()
        NEW_FILTERS: dict[str, str] = {}
        # Create new filters file
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(json.dumps(NEW_FILTERS))
            f.flush()
            raw_output = self.openstack(
                f'endpoint group set {endpoint_group_id} '
                f'--name {new_name} '
                f'--description {new_description} '
                f'--filters {f.name}'
            )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'endpoint group show {endpoint_group_id}')
        endpoint_group = self.parse_show_as_object(raw_output)
        self.assertEqual(new_name, endpoint_group['name'])
        self.assertEqual(new_description, endpoint_group['description'])
        self.assertEqual(json.dumps(NEW_FILTERS), endpoint_group['filters'])

    def test_endpoint_group_show(self):
        endpoint_group_id = self._create_dummy_endpoint_group()
        raw_output = self.openstack(f'endpoint group show {endpoint_group_id}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_GROUP_FIELDS)

    def test_project_endpoint_group_add_remove_list(self):
        endpoint_group_id = self._create_dummy_endpoint_group()
        project_id = self._create_dummy_project()
        raw_output = self.openstack(
            f'endpoint group add project {endpoint_group_id} {project_id}'
        )
        self.assertEqual(0, len(raw_output))

        raw_output = self.openstack(
            f'endpoint group list --endpointgroup {endpoint_group_id}'
        )
        self.assertIn(project_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(
            items, self.ENDPOINT_GROUP_LIST_PROJECT_HEADERS
        )

        raw_output = self.openstack(
            f'endpoint group list --project {project_id}'
        )
        self.assertIn(endpoint_group_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_GROUP_LIST_HEADERS)

        raw_output = self.openstack(
            f'endpoint group remove project {endpoint_group_id} {project_id}'
        )
        self.assertEqual(0, len(raw_output))

        raw_output = self.openstack(
            f'endpoint group list --endpointgroup {endpoint_group_id}'
        )
        self.assertNotIn(project_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(
            items, self.ENDPOINT_GROUP_LIST_PROJECT_HEADERS
        )

        raw_output = self.openstack(
            f'endpoint group list --project {project_id}'
        )
        self.assertNotIn(endpoint_group_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_GROUP_LIST_HEADERS)
