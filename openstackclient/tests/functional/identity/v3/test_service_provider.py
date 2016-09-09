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
from tempest.lib.common.utils import data_utils


class ServiceProviderTests(common.IdentityTests):
    # Introduce functional test cases for command 'Service Provider'

    def test_sp_create(self):
        self._create_dummy_sp(add_clean_up=True)

    def test_sp_delete(self):
        service_provider = self._create_dummy_sp(add_clean_up=False)
        raw_output = self.openstack('service provider delete %s'
                                    % service_provider)
        self.assertEqual(0, len(raw_output))

    def test_sp_multi_delete(self):
        sp1 = self._create_dummy_sp(add_clean_up=False)
        sp2 = self._create_dummy_sp(add_clean_up=False)
        raw_output = self.openstack(
            'service provider delete %s %s' % (sp1, sp2))
        self.assertEqual(0, len(raw_output))

    def test_sp_show(self):
        service_provider = self._create_dummy_sp(add_clean_up=True)
        raw_output = self.openstack('service provider show %s'
                                    % service_provider)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.SERVICE_PROVIDER_FIELDS)

    def test_sp_list(self):
        self._create_dummy_sp(add_clean_up=True)
        raw_output = self.openstack('service provider list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.SERVICE_PROVIDER_LIST_HEADERS)

    def test_sp_set(self):
        service_provider = self._create_dummy_sp(add_clean_up=True)
        new_description = data_utils.rand_name('newDescription')
        raw_output = self.openstack('service provider set '
                                    '%(service-provider)s '
                                    '--description %(description)s '
                                    % {'service-provider': service_provider,
                                       'description': new_description})
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack('service provider show %s'
                                    % service_provider)
        updated_value = self.parse_show_as_object(raw_output)
        self.assertIn(new_description, updated_value['description'])
