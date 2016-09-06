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


class CatalogTests(common.IdentityTests):

    def test_catalog_list(self):
        raw_output = self.openstack('catalog list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.CATALOG_LIST_HEADERS)

    def test_catalog_show(self):
        """test catalog show command

        The output example:
        +-----------+-------------------------------------------+
        | Field     | Value                                     |
        +-----------+-------------------------------------------+
        | endpoints | test1                                     |
        |           |   publicURL: http://localhost:5000/v2.0   |
        |           |   internalURL: http://localhost:5000/v2.0 |
        |           |   adminURL: http://localhost:5000/v2.0    |
        |           |                                           |
        | name      | keystone                                  |
        | type      | identity                                  |
        +-----------+-------------------------------------------+
        """
        raw_output = self.openstack('catalog show %s' % 'identity')
        items = self.parse_show(raw_output)
        # items may have multiple endpoint urls with empty key
        self.assert_show_fields(items, ['endpoints', 'name', 'type', ''])
