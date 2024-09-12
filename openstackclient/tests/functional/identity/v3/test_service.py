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


class ServiceTests(common.IdentityTests):
    def test_service_create(self):
        self._create_dummy_service()

    def test_service_delete(self):
        service_name = self._create_dummy_service(add_clean_up=False)
        raw_output = self.openstack(f'service delete {service_name}')
        self.assertEqual(0, len(raw_output))

    def test_service_multi_delete(self):
        service_1 = self._create_dummy_service(add_clean_up=False)
        service_2 = self._create_dummy_service(add_clean_up=False)
        raw_output = self.openstack(f'service delete {service_1} {service_2}')
        self.assertEqual(0, len(raw_output))

    def test_service_list(self):
        self._create_dummy_service()
        raw_output = self.openstack('service list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_service_set(self):
        service_name = self._create_dummy_service()
        # set service
        new_service_name = data_utils.rand_name('NewTestService')
        new_service_description = data_utils.rand_name('description')
        new_service_type = data_utils.rand_name('NewTestType')
        raw_output = self.openstack(
            'service set '
            f'--type {new_service_type} '
            f'--name {new_service_name} '
            f'--description {new_service_description} '
            '--disable '
            f'{service_name}'
        )
        self.assertEqual(0, len(raw_output))
        # get service details
        raw_output = self.openstack(f'service show {new_service_name}')
        # assert service details
        service = self.parse_show_as_object(raw_output)
        self.assertEqual(new_service_type, service['type'])
        self.assertEqual(new_service_name, service['name'])
        self.assertEqual(new_service_description, service['description'])

    def test_service_show(self):
        service_name = self._create_dummy_service()
        raw_output = self.openstack(f'service show {service_name}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.SERVICE_FIELDS)
