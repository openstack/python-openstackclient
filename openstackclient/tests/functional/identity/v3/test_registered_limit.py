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

import os

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v3 import common

SYSTEM_CLOUD = os.environ.get('OS_SYSTEM_CLOUD', 'devstack-system-admin')


class RegisteredLimitTestCase(common.IdentityTests):
    def test_registered_limit_create_with_service_name(self):
        self._create_dummy_registered_limit()

    def test_registered_limit_create_with_service_id(self):
        service_name = self._create_dummy_service()
        raw_output = self.openstack(f'service show {service_name}')
        service_items = self.parse_show(raw_output)
        service_id = self._extract_value_from_items('id', service_items)

        raw_output = self.openstack(
            'registered limit create'
            ' --service {service_id}'
            ' --default-limit {default_limit}'
            ' {resource_name}'.format(
                service_id=service_id,
                default_limit=10,
                resource_name='cores',
            ),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        registered_limit_id = self._extract_value_from_items('id', items)
        self.addCleanup(
            self.openstack,
            f'registered limit delete {registered_limit_id}',
            cloud=SYSTEM_CLOUD,
        )

        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_create_with_options(self):
        service_name = self._create_dummy_service()
        region_id = self._create_dummy_region()
        params = {
            'service_name': service_name,
            'resource_name': 'cores',
            'default_limit': 10,
            'description': 'default limit for cores',
            'region_id': region_id,
        }

        raw_output = self.openstack(
            'registered limit create'
            ' --description \'{description}\''
            ' --region {region_id}'
            ' --service {service_name}'
            ' --default-limit {default_limit}'
            ' {resource_name}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        registered_limit_id = self._extract_value_from_items('id', items)
        self.addCleanup(
            self.openstack,
            f'registered limit delete {registered_limit_id}',
            cloud=SYSTEM_CLOUD,
        )

        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_show(self):
        registered_limit_id = self._create_dummy_registered_limit()
        raw_output = self.openstack(
            f'registered limit show {registered_limit_id}'
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_set_region_id(self):
        region_id = self._create_dummy_region()
        registered_limit_id = self._create_dummy_registered_limit()

        params = {
            'registered_limit_id': registered_limit_id,
            'region_id': region_id,
        }
        raw_output = self.openstack(
            'registered limit set'
            ' {registered_limit_id}'
            ' --region {region_id}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_set_description(self):
        registered_limit_id = self._create_dummy_registered_limit()
        params = {
            'registered_limit_id': registered_limit_id,
            'description': 'updated description',
        }
        raw_output = self.openstack(
            'registered limit set'
            ' {registered_limit_id}'
            ' --description \'{description}\''.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_set_service(self):
        registered_limit_id = self._create_dummy_registered_limit()
        service_name = self._create_dummy_service()
        params = {
            'registered_limit_id': registered_limit_id,
            'service': service_name,
        }
        raw_output = self.openstack(
            'registered limit set'
            ' {registered_limit_id}'
            ' --service {service}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_set_default_limit(self):
        registered_limit_id = self._create_dummy_registered_limit()
        params = {
            'registered_limit_id': registered_limit_id,
            'default_limit': 20,
        }
        raw_output = self.openstack(
            'registered limit set'
            ' {registered_limit_id}'
            ' --default-limit {default_limit}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_set_resource_name(self):
        registered_limit_id = self._create_dummy_registered_limit()
        resource_name = data_utils.rand_name('resource_name')
        params = {
            'registered_limit_id': registered_limit_id,
            'resource_name': resource_name,
        }
        raw_output = self.openstack(
            'registered limit set'
            ' {registered_limit_id}'
            ' --resource-name {resource_name}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)

    def test_registered_limit_list(self):
        self._create_dummy_registered_limit()
        raw_output = self.openstack('registered limit list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.REGISTERED_LIMIT_LIST_HEADERS)

    def test_registered_limit_delete(self):
        registered_limit_id = self._create_dummy_registered_limit(
            add_clean_up=False
        )
        raw_output = self.openstack(
            f'registered limit delete {registered_limit_id}',
            cloud=SYSTEM_CLOUD,
        )
        self.assertEqual(0, len(raw_output))
