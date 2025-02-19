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

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional.identity.v3 import common


class GroupTests(common.IdentityTests):
    def test_group_create(self):
        self._create_dummy_group()

    def test_group_list(self):
        group_name = self._create_dummy_group()
        raw_output = self.openstack('group list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)
        self.assertIn(group_name, raw_output)

    def test_group_list_with_domain(self):
        group_name = self._create_dummy_group()
        raw_output = self.openstack(f'group list --domain {self.domain_name}')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)
        self.assertIn(group_name, raw_output)

    def test_group_delete(self):
        group_name = self._create_dummy_group(add_clean_up=False)
        raw_output = self.openstack(
            f'group delete --domain {self.domain_name} {group_name}'
        )
        self.assertEqual(0, len(raw_output))

    def test_group_show(self):
        group_name = self._create_dummy_group()
        raw_output = self.openstack(
            f'group show --domain {self.domain_name} {group_name}'
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.GROUP_FIELDS)

    def test_group_set(self):
        group_name = self._create_dummy_group()
        new_group_name = data_utils.rand_name('NewTestGroup')
        raw_output = self.openstack(
            'group set '
            f'--domain {self.domain_name} '
            f'--name {new_group_name} '
            f'{group_name}'
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            f'group show --domain {self.domain_name} {new_group_name}'
        )
        group = self.parse_show_as_object(raw_output)
        self.assertEqual(new_group_name, group['name'])
        # reset group name to make sure it will be cleaned up
        raw_output = self.openstack(
            'group set '
            f'--domain {self.domain_name} '
            f'--name {group_name} '
            f'{new_group_name}'
        )
        self.assertEqual(0, len(raw_output))

    def test_group_add_user(self):
        group_name = self._create_dummy_group()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'group add user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}'
        )
        self.addCleanup(
            self.openstack,
            'group remove user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}',
        )
        self.assertOutput('', raw_output)

    def test_group_contains_user(self):
        group_name = self._create_dummy_group()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'group add user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}'
        )
        self.addCleanup(
            self.openstack,
            'group remove user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}',
        )
        self.assertOutput('', raw_output)
        raw_output = self.openstack(
            'group contains user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}'
        )
        self.assertEqual(
            f'{username} in group {group_name}\n',
            raw_output,
        )

    def test_group_remove_user(self):
        group_name = self._create_dummy_group()
        username = self._create_dummy_user()
        add_raw_output = self.openstack(
            'group add user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}'
        )
        remove_raw_output = self.openstack(
            'group remove user '
            f'--group-domain {self.domain_name} '
            f'--user-domain {self.domain_name} '
            f'{group_name} {username}'
        )
        self.assertOutput('', add_raw_output)
        self.assertOutput('', remove_raw_output)
