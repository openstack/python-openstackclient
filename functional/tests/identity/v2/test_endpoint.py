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

from functional.tests.identity.v2 import test_identity


class EndpointTests(test_identity.IdentityTests):

    def test_endpoint_create(self):
        self._create_dummy_endpoint()

    def test_endpoint_delete(self):
        endpoint_id = self._create_dummy_endpoint(add_clean_up=False)
        raw_output = self.openstack(
            'endpoint delete %s' % endpoint_id)
        self.assertEqual(0, len(raw_output))

    def test_endpoint_list(self):
        endpoint_id = self._create_dummy_endpoint()
        raw_output = self.openstack('endpoint list')
        self.assertInOutput(endpoint_id, raw_output)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ENDPOINT_LIST_HEADERS)

    def test_endpoint_show(self):
        endpoint_id = self._create_dummy_endpoint()
        raw_output = self.openstack('endpoint show %s' % endpoint_id)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_FIELDS)
