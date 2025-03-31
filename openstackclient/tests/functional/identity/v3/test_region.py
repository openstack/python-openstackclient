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

from openstackclient.tests.functional.identity.v3 import common


class RegionTests(common.IdentityTests):
    def test_region_create(self):
        self._create_dummy_region()

    def test_region_create_with_parent_region(self):
        parent_region_id = self._create_dummy_region()
        self._create_dummy_region(parent_region=parent_region_id)

    def test_region_delete(self):
        region_id = self._create_dummy_region(add_clean_up=False)
        raw_output = self.openstack(f'region delete {region_id}')
        self.assertEqual(0, len(raw_output))

    def test_region_multi_delete(self):
        region_1 = self._create_dummy_region(add_clean_up=False)
        region_2 = self._create_dummy_region(add_clean_up=False)
        raw_output = self.openstack(f'region delete {region_1} {region_2}')
        self.assertEqual(0, len(raw_output))

    def test_region_list(self):
        raw_output = self.openstack('region list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.REGION_LIST_HEADERS)

    def test_region_set(self):
        # prepare region with parent-region
        parent_region_id = self._create_dummy_region()
        new_parent_region_id = self._create_dummy_region()
        region_id = self._create_dummy_region(parent_region_id)
        # check region details
        raw_output = self.openstack(f'region show {region_id}')
        region = self.parse_show_as_object(raw_output)
        self.assertEqual(parent_region_id, region['parent_region'])
        self.assertEqual(region_id, region['region'])
        # update parent-region
        raw_output = self.openstack(
            f'region set --parent-region {new_parent_region_id} {region_id}'
        )
        self.assertEqual(0, len(raw_output))
        # check updated region details
        raw_output = self.openstack(f'region show {region_id}')
        region = self.parse_show_as_object(raw_output)
        self.assertEqual(new_parent_region_id, region['parent_region'])
        self.assertEqual(region_id, region['region'])

    def test_region_show(self):
        region_id = self._create_dummy_region()
        raw_output = self.openstack(f'region show {region_id}')
        region = self.parse_show_as_object(raw_output)
        self.assertEqual(region_id, region['region'])
        self.assertEqual('None', region['parent_region'])
