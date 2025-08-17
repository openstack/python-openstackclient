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


class CatalogTests(common.IdentityTests):
    """Functional tests for catalog commands"""

    def test_catalog(self):
        """Test catalog list and show functionality"""
        # Create a test service for isolated testing
        _dummy_service_name = self._create_dummy_service(add_clean_up=True)

        # list catalogs
        raw_output = self.openstack('catalog list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, ['Name', 'Type', 'Endpoints'])

        # Verify created service appears in catalog
        service_names = [
            item.get('Name') for item in items if item.get('Name')
        ]
        self.assertIn(
            _dummy_service_name,
            service_names,
            "Created dummy service should be present in catalog",
        )

        # show service (by name)
        raw_output = self.openstack(f'catalog show {_dummy_service_name}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, ['endpoints', 'name', 'type', 'id'])

        # Extract the type from the dummy service
        _dummy_service_type = next(
            (item['type'] for item in items if 'type' in item), None
        )

        # show service (by type)
        raw_output = self.openstack(f'catalog show {_dummy_service_type}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, ['endpoints', 'name', 'type', 'id'])

        # show service (non-existent)
        result = self.openstack(
            'catalog show nonexistent-service-xyz', fail_ok=True
        )
        self.assertEqual(
            '',
            result.strip(),
            "Non-existent service should return empty result",
        )
