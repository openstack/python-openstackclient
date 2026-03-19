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

import json
import tempfile

from openstackclient.tests.functional.identity.v3 import common


class MappingTests(common.IdentityTests):
    def test_mapping_create(self):
        self._create_dummy_mapping()

    def test_mapping_delete(self):
        mapping = self._create_dummy_mapping(add_clean_up=False)
        raw_output = self.openstack(f'mapping delete {mapping}')
        self.assertEqual(0, len(raw_output))

    def test_mapping_multi_delete(self):
        mapping_1 = self._create_dummy_mapping(add_clean_up=False)
        mapping_2 = self._create_dummy_mapping(add_clean_up=False)
        raw_output = self.openstack(f'mapping delete {mapping_1} {mapping_2}')
        self.assertEqual(0, len(raw_output))

    def test_mapping_show(self):
        mapping = self._create_dummy_mapping(add_clean_up=True)
        raw_output = self.openstack(f'mapping show {mapping}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.MAPPING_FIELDS)

    def test_mapping_list(self):
        self._create_dummy_mapping(add_clean_up=True)
        raw_output = self.openstack('mapping list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.MAPPING_LIST_HEADERS)

    def test_mapping_set(self):
        mapping = self._create_dummy_mapping(add_clean_up=True)
        new_schema_version = '2.0'
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            NEW_RULES = [
                {
                    "local": [{"group": {"id": "85a868"}}],
                    "remote": [
                        {"type": "orgPersonType", "any_one_of": ["Employee"]},
                        {"type": "sn", "any_one_of": ["Young"]},
                    ],
                },
                {
                    "local": [
                        {"group": {"id": "0cd5e9"}},
                        {"user": {"name": "0cd5e9"}},
                    ],
                    "remote": [
                        {"type": "UserName"},
                        {
                            "type": "orgPersonType",
                            "not_any_of": ["Contractor", "SubContractor"],
                        },
                        {"type": "LastName", "any_one_of": ["Bo"]},
                    ],
                },
            ]
            f.write(json.dumps(NEW_RULES))
            f.flush()
            raw_output = self.openstack(
                f'mapping set {mapping} --rules {f.name} --schema-version {new_schema_version}'
            )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'mapping show {mapping}')
        updated_value = self.parse_show_as_object(raw_output)
        self.assertEqual('2.0', updated_value['schema_version'])
