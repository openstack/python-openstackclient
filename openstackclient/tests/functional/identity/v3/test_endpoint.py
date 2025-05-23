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


class EndpointTests(common.IdentityTests):
    def test_endpoint_create(self):
        self._create_dummy_endpoint(interface='public')
        self._create_dummy_endpoint(interface='admin')
        self._create_dummy_endpoint(interface='internal')

    def test_endpoint_delete(self):
        endpoint_id = self._create_dummy_endpoint(add_clean_up=False)
        raw_output = self.openstack(f'endpoint delete {endpoint_id}')
        self.assertEqual(0, len(raw_output))

    def test_endpoint_multi_delete(self):
        endpoint_1 = self._create_dummy_endpoint(add_clean_up=False)
        endpoint_2 = self._create_dummy_endpoint(add_clean_up=False)
        raw_output = self.openstack(
            f'endpoint delete {endpoint_1} {endpoint_2}'
        )
        self.assertEqual(0, len(raw_output))

    def test_endpoint_list(self):
        endpoint_id = self._create_dummy_endpoint()
        raw_output = self.openstack('endpoint list')
        self.assertIn(endpoint_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_LIST_HEADERS)

    def test_endpoint_list_filter(self):
        endpoint_id = self._create_dummy_endpoint(add_clean_up=False)
        project_id = self._create_dummy_project(add_clean_up=False)
        raw_output = self.openstack(
            f'endpoint add project {endpoint_id} {project_id}'
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'endpoint list --endpoint {endpoint_id}')
        self.assertIn(project_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_LIST_PROJECT_HEADERS)

        raw_output = self.openstack(f'endpoint list --project {project_id}')
        self.assertIn(endpoint_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_LIST_HEADERS)

    def test_endpoint_set(self):
        endpoint_id = self._create_dummy_endpoint()
        new_endpoint_url = data_utils.rand_url()
        raw_output = self.openstack(
            'endpoint set '
            '--interface {interface} '
            '--url {url} '
            '--disable '
            '{endpoint_id}'.format(
                interface='admin',
                url=new_endpoint_url,
                endpoint_id=endpoint_id,
            )
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'endpoint show {endpoint_id}')
        endpoint = self.parse_show_as_object(raw_output)
        self.assertEqual('admin', endpoint['interface'])
        self.assertEqual(new_endpoint_url, endpoint['url'])
        self.assertEqual('False', endpoint['enabled'])

    def test_endpoint_show(self):
        endpoint_id = self._create_dummy_endpoint()
        raw_output = self.openstack(f'endpoint show {endpoint_id}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_FIELDS)

    def test_endpoint_add_remove_project(self):
        endpoint_id = self._create_dummy_endpoint(add_clean_up=False)
        project_id = self._create_dummy_project(add_clean_up=False)
        raw_output = self.openstack(
            f'endpoint add project {endpoint_id} {project_id}'
        )
        self.assertEqual(0, len(raw_output))

        raw_output = self.openstack(
            f'endpoint remove project {endpoint_id} {project_id}'
        )
        self.assertEqual(0, len(raw_output))
