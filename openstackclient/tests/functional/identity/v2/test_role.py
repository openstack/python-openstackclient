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


class RoleTests(common.IdentityTests):

    def test_role_create(self):
        self._create_dummy_role()

    def test_role_delete(self):
        role_name = self._create_dummy_role(add_clean_up=False)
        raw_output = self.openstack('role delete %s' % role_name)
        self.assertEqual(0, len(raw_output))

    def test_role_list(self):
        self._create_dummy_role()
        raw_output = self.openstack('role list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_role_show(self):
        role_name = self._create_dummy_role()
        raw_output = self.openstack('role show %s' % role_name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)

    def test_role_add(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'role add '
            '--project %(project)s '
            '--user %(user)s '
            '%(role)s' % {'project': self.project_name,
                          'user': username,
                          'role': role_name})
        self.addCleanup(
            self.openstack,
            'role remove '
            '--project %(project)s '
            '--user %(user)s '
            '%(role)s' % {'project': self.project_name,
                          'user': username,
                          'role': role_name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)

    def test_role_remove(self):
        role_name = self._create_dummy_role()
        username = self._create_dummy_user()
        add_raw_output = self.openstack(
            'role add '
            '--project %(project)s '
            '--user %(user)s '
            '%(role)s' % {'project': self.project_name,
                          'user': username,
                          'role': role_name})
        del_raw_output = self.openstack(
            'role remove '
            '--project %(project)s '
            '--user %(user)s '
            '%(role)s' % {'project': self.project_name,
                          'user': username,
                          'role': role_name})
        items = self.parse_show(add_raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)
        self.assertEqual(0, len(del_raw_output))
