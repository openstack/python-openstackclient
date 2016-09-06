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

from openstackclient.tests.functional.identity.v2 import common


class ServiceTests(common.IdentityTests):

    def test_service_create(self):
        self._create_dummy_service()

    def test_service_delete(self):
        service_name = self._create_dummy_service(add_clean_up=False)
        raw_output = self.openstack('service delete %s' % service_name)
        self.assertEqual(0, len(raw_output))

    def test_service_multi_delete(self):
        service_name_1 = self._create_dummy_service(add_clean_up=False)
        service_name_2 = self._create_dummy_service(add_clean_up=False)
        raw_output = self.openstack(
            'service delete ' + service_name_1 + ' ' + service_name_2)
        self.assertEqual(0, len(raw_output))

    def test_service_list(self):
        self._create_dummy_service()
        raw_output = self.openstack('service list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_service_show(self):
        service_name = self._create_dummy_service()
        raw_output = self.openstack(
            'service show %s' % service_name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.SERVICE_FIELDS)
