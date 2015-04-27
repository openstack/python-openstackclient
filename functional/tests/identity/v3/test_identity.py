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
import uuid

from functional.common import exceptions
from functional.common import test

BASIC_LIST_HEADERS = ['ID', 'Name']


class IdentityTests(test.TestCase):
    """Functional tests for Identity commands. """

    DOMAIN_FIELDS = ['description', 'enabled', 'id', 'name', 'links']
    GROUP_FIELDS = ['description', 'domain_id', 'id', 'name', 'links']
    TOKEN_FIELDS = ['expires', 'id', 'project_id', 'user_id']

    def _create_dummy_group(self):
        name = uuid.uuid4().hex
        self.openstack('group create ' + name)
        return name

    def _create_dummy_domain(self):
        name = uuid.uuid4().hex
        self.openstack('domain create ' + name)
        return name

    def setUp(self):
        super(IdentityTests, self).setUp()
        auth_url = os.environ.get('OS_AUTH_URL')
        auth_url = auth_url.replace('v2.0', 'v3')
        os.environ['OS_AUTH_URL'] = auth_url
        os.environ['OS_IDENTITY_API_VERSION'] = '3'
        os.environ['OS_USER_DOMAIN_ID'] = 'default'
        os.environ['OS_PROJECT_DOMAIN_ID'] = 'default'

    def test_group_create(self):
        raw_output = self.openstack('group create ' + uuid.uuid4().hex)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.GROUP_FIELDS)

    def test_group_list(self):
        self._create_dummy_group()
        raw_output = self.openstack('group list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

    def test_group_delete(self):
        name = self._create_dummy_group()
        raw_output = self.openstack('group delete ' + name)
        self.assertEqual(0, len(raw_output))

    def test_group_show(self):
        name = self._create_dummy_group()
        raw_output = self.openstack('group show ' + name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.GROUP_FIELDS)

    def test_domain_create(self):
        raw_output = self.openstack('domain create ' + uuid.uuid4().hex)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.DOMAIN_FIELDS)

    def test_domain_list(self):
        self._create_dummy_domain()
        raw_output = self.openstack('domain list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

    def test_domain_delete(self):
        name = self._create_dummy_domain()
        self.assertRaises(exceptions.CommandFailed,
                          self.openstack, 'domain delete ' + name)

    def test_domain_show(self):
        name = self._create_dummy_domain()
        raw_output = self.openstack('domain show ' + name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.DOMAIN_FIELDS)

    def test_token_issue(self):
        raw_output = self.openstack('token issue')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.TOKEN_FIELDS)
