# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ast
import json

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v3 import common


class AccessRuleTests(common.IdentityTests):
    ACCESS_RULE_FIELDS = [
        'ID',
        'Service',
        'Method',
        'Path',
    ]
    ACCESS_RULE_LIST_HEADERS = [
        'ID',
        'Service',
        'Method',
        'Path',
    ]

    def setUp(self):
        super().setUp()

        application_credential_name = data_utils.rand_name('name')
        access_rules = json.dumps(
            [
                {
                    'method': 'GET',
                    'path': '/v2.1/servers',
                    'service': 'compute',
                },
                {
                    'method': 'GET',
                    'path': '/v2.0/networks',
                    'service': 'networking',
                },
            ]
        )
        raw_output = self.openstack(
            f"application credential create {application_credential_name} "
            f"--access-rules '{access_rules}'"
        )
        # we immediately delete the application credential since it will leave
        # the access rules around
        self.openstack(
            f'application credential delete {application_credential_name}'
        )

        items = self.parse_show_as_object(raw_output)
        self.access_rule_ids = [
            x['id'] for x in ast.literal_eval(items['access_rules'])
        ]
        self.addCleanup(
            self.openstack,
            'access rule delete '
            + ' '.join([x for x in self.access_rule_ids]),
        )

    def test_access_rule(self):
        # list

        raw_output = self.openstack('access rule list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.ACCESS_RULE_LIST_HEADERS)

        # show

        raw_output = self.openstack(
            f'access rule show {self.access_rule_ids[0]}'
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ACCESS_RULE_FIELDS)
