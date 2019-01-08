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


class LimitTestCase(common.IdentityTests):

    def test_limit_create_with_service_name(self):
        registered_limit_id = self._create_dummy_registered_limit()
        raw_output = self.openstack(
            'registered limit show %s' % registered_limit_id,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        service_id = self._extract_value_from_items('service_id', items)
        resource_name = self._extract_value_from_items('resource_name', items)

        raw_output = self.openstack('service show %s' % service_id)
        items = self.parse_show(raw_output)
        service_name = self._extract_value_from_items('name', items)

        project_name = self._create_dummy_project()
        raw_output = self.openstack('project show %s' % project_name)
        items = self.parse_show(raw_output)
        project_id = self._extract_value_from_items('id', items)

        params = {
            'project_id': project_id,
            'service_name': service_name,
            'resource_name': resource_name,
            'resource_limit': 15
        }
        raw_output = self.openstack(
            'limit create'
            ' --project %(project_id)s'
            ' --service %(service_name)s'
            ' --resource-limit %(resource_limit)s'
            ' %(resource_name)s' % params,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        limit_id = self._extract_value_from_items('id', items)
        self.addCleanup(
            self.openstack,
            'limit delete %s' % limit_id,
            cloud=SYSTEM_CLOUD
        )

        self.assert_show_fields(items, self.LIMIT_FIELDS)

    def test_limit_create_with_project_name(self):
        registered_limit_id = self._create_dummy_registered_limit()
        raw_output = self.openstack(
            'registered limit show %s' % registered_limit_id,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        service_id = self._extract_value_from_items('service_id', items)
        resource_name = self._extract_value_from_items('resource_name', items)

        raw_output = self.openstack('service show %s' % service_id)
        items = self.parse_show(raw_output)
        service_name = self._extract_value_from_items('name', items)

        project_name = self._create_dummy_project()

        params = {
            'project_name': project_name,
            'service_name': service_name,
            'resource_name': resource_name,
            'resource_limit': 15
        }
        raw_output = self.openstack(
            'limit create'
            ' --project %(project_name)s'
            ' --service %(service_name)s'
            ' --resource-limit %(resource_limit)s'
            ' %(resource_name)s' % params,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        limit_id = self._extract_value_from_items('id', items)
        self.addCleanup(
            self.openstack,
            'limit delete %s' % limit_id,
            cloud=SYSTEM_CLOUD
        )

        self.assert_show_fields(items, self.LIMIT_FIELDS)
        registered_limit_id = self._create_dummy_registered_limit()

    def test_limit_create_with_service_id(self):
        self._create_dummy_limit()

    def test_limit_create_with_project_id(self):
        self._create_dummy_limit()

    def test_limit_create_with_options(self):
        registered_limit_id = self._create_dummy_registered_limit()
        region_id = self._create_dummy_region()

        params = {
            'region_id': region_id,
            'registered_limit_id': registered_limit_id
        }

        raw_output = self.openstack(
            'registered limit set'
            ' %(registered_limit_id)s'
            ' --region %(region_id)s' % params,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        service_id = self._extract_value_from_items('service_id', items)
        resource_name = self._extract_value_from_items('resource_name', items)

        project_name = self._create_dummy_project()
        raw_output = self.openstack('project show %s' % project_name)
        items = self.parse_show(raw_output)
        project_id = self._extract_value_from_items('id', items)
        description = data_utils.arbitrary_string()

        params = {
            'project_id': project_id,
            'service_id': service_id,
            'resource_name': resource_name,
            'resource_limit': 15,
            'region_id': region_id,
            'description': description
        }
        raw_output = self.openstack(
            'limit create'
            ' --project %(project_id)s'
            ' --service %(service_id)s'
            ' --resource-limit %(resource_limit)s'
            ' --region %(region_id)s'
            ' --description %(description)s'
            ' %(resource_name)s' % params,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        limit_id = self._extract_value_from_items('id', items)
        self.addCleanup(
            self.openstack,
            'limit delete %s' % limit_id,
            cloud=SYSTEM_CLOUD
        )

        self.assert_show_fields(items, self.LIMIT_FIELDS)

    def test_limit_show(self):
        limit_id = self._create_dummy_limit()
        raw_output = self.openstack(
            'limit show %s' % limit_id,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.LIMIT_FIELDS)

    def test_limit_set_description(self):
        limit_id = self._create_dummy_limit()

        params = {
            'description': data_utils.arbitrary_string(),
            'limit_id': limit_id
        }

        raw_output = self.openstack(
            'limit set'
            ' --description %(description)s'
            ' %(limit_id)s' % params,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.LIMIT_FIELDS)

    def test_limit_set_resource_limit(self):
        limit_id = self._create_dummy_limit()

        params = {
            'resource_limit': 5,
            'limit_id': limit_id
        }

        raw_output = self.openstack(
            'limit set'
            ' --resource-limit %(resource_limit)s'
            ' %(limit_id)s' % params,
            cloud=SYSTEM_CLOUD
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.LIMIT_FIELDS)

    def test_limit_list(self):
        self._create_dummy_limit()
        raw_output = self.openstack('limit list', cloud=SYSTEM_CLOUD)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.LIMIT_LIST_HEADERS)

    def test_limit_delete(self):
        limit_id = self._create_dummy_limit(add_clean_up=False)
        raw_output = self.openstack(
            'limit delete %s' % limit_id,
            cloud=SYSTEM_CLOUD)
        self.assertEqual(0, len(raw_output))
