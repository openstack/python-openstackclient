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


class PolicyTests(common.IdentityTests):
    def test_policy_create(self):
        self._create_dummy_policy()

    def test_policy_delete(self):
        policy = self._create_dummy_policy(add_clean_up=False)
        raw_output = self.openstack(f'policy delete {policy}')
        self.assertEqual(0, len(raw_output))

    def test_policy_multi_delete(self):
        policy_1 = self._create_dummy_policy(add_clean_up=False)
        policy_2 = self._create_dummy_policy(add_clean_up=False)
        raw_output = self.openstack(f'policy delete {policy_1} {policy_2}')
        self.assertEqual(0, len(raw_output))

    def test_policy_show(self):
        policy = self._create_dummy_policy(add_clean_up=True)
        raw_output = self.openstack(f'policy show {policy}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.POLICY_FIELDS)

    def test_policy_list(self):
        self._create_dummy_policy(add_clean_up=True)
        raw_output = self.openstack('policy list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.POLICY_LIST_HEADERS)

    def test_policy_list_long(self):
        self._create_dummy_policy(add_clean_up=True)
        raw_output = self.openstack('policy list --long')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.POLICY_LIST_LONG_HEADERS)

    def test_policy_set(self):
        policy = self._create_dummy_policy(add_clean_up=True)
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
                f'policy set {policy} --rules {f.name} --type text/json'
            )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(f'policy show {policy}')
        updated_value = self.parse_show_as_object(raw_output)
        self.assertEqual('text/json', updated_value['type'])
