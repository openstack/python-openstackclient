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
        raw_output = self.openstack(
            'group list --domain %s' % self.domain_name)
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)
        self.assertIn(group_name, raw_output)

    def test_group_delete(self):
        group_name = self._create_dummy_group(add_clean_up=False)
        raw_output = self.openstack(
            'group delete '
            '--domain %(domain)s '
            '%(name)s' % {'domain': self.domain_name,
                          'name': group_name})
        self.assertEqual(0, len(raw_output))

    def test_group_show(self):
        group_name = self._create_dummy_group()
        raw_output = self.openstack(
            'group show '
            '--domain %(domain)s '
            '%(name)s' % {'domain': self.domain_name,
                          'name': group_name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.GROUP_FIELDS)

    def test_group_set(self):
        group_name = self._create_dummy_group()
        new_group_name = data_utils.rand_name('NewTestGroup')
        raw_output = self.openstack(
            'group set '
            '--domain %(domain)s '
            '--name %(new_group)s '
            '%(group)s' % {'domain': self.domain_name,
                           'new_group': new_group_name,
                           'group': group_name})
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            'group show '
            '--domain %(domain)s '
            '%(group)s' % {'domain': self.domain_name,
                           'group': new_group_name})
        group = self.parse_show_as_object(raw_output)
        self.assertEqual(new_group_name, group['name'])
        # reset group name to make sure it will be cleaned up
        raw_output = self.openstack(
            'group set '
            '--domain %(domain)s '
            '--name %(new_group)s '
            '%(group)s' % {'domain': self.domain_name,
                           'new_group': group_name,
                           'group': new_group_name})
        self.assertEqual(0, len(raw_output))

    def test_group_add_user(self):
        group_name = self._create_dummy_group()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'group add user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        self.addCleanup(
            self.openstack,
            'group remove user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        self.assertOutput('', raw_output)

    def test_group_contains_user(self):
        group_name = self._create_dummy_group()
        username = self._create_dummy_user()
        raw_output = self.openstack(
            'group add user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        self.addCleanup(
            self.openstack,
            'group remove user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        self.assertOutput('', raw_output)
        raw_output = self.openstack(
            'group contains user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        self.assertEqual(
            '%(user)s in group %(group)s\n' % {'user': username,
                                               'group': group_name},
            raw_output)

    def test_group_remove_user(self):
        group_name = self._create_dummy_group()
        username = self._create_dummy_user()
        add_raw_output = self.openstack(
            'group add user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        remove_raw_output = self.openstack(
            'group remove user '
            '--group-domain %(group_domain)s '
            '--user-domain %(user_domain)s '
            '%(group)s %(user)s' % {'group_domain': self.domain_name,
                                    'user_domain': self.domain_name,
                                    'group': group_name,
                                    'user': username})
        self.assertOutput('', add_raw_output)
        self.assertOutput('', remove_raw_output)
