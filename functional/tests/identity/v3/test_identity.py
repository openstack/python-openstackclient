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

from tempest_lib.common.utils import data_utils

from functional.common import test


BASIC_LIST_HEADERS = ['ID', 'Name']


class IdentityTests(test.TestCase):
    """Functional tests for Identity commands. """

    DOMAIN_FIELDS = ['description', 'enabled', 'id', 'name', 'links']
    GROUP_FIELDS = ['description', 'domain_id', 'id', 'name', 'links']
    TOKEN_FIELDS = ['expires', 'id', 'project_id', 'user_id']
    USER_FIELDS = ['email', 'enabled', 'id', 'name', 'name',
                   'domain_id', 'default_project_id', 'description']
    PROJECT_FIELDS = ['description', 'id', 'domain_id',
                      'enabled', 'name', 'parent_id', 'links']
    ROLE_FIELDS = ['id', 'name', 'links']

    @classmethod
    def setUpClass(cls):
        if hasattr(super(IdentityTests, cls), 'setUpClass'):
            super(IdentityTests, cls).setUpClass()

        # prepare v3 env
        auth_url = os.environ.get('OS_AUTH_URL')
        auth_url = auth_url.replace('v2.0', 'v3')
        os.environ['OS_AUTH_URL'] = auth_url
        os.environ['OS_IDENTITY_API_VERSION'] = '3'
        os.environ['OS_USER_DOMAIN_ID'] = 'default'
        os.environ['OS_PROJECT_DOMAIN_ID'] = 'default'

        # create dummy domain
        cls.domain_name = data_utils.rand_name('TestDomain')
        cls.domain_description = data_utils.rand_name('description')
        cls.openstack(
            'domain create '
            '--description %(description)s '
            '--enable '
            '%(name)s' % {'description': cls.domain_description,
                          'name': cls.domain_name})

        # create dummy project
        cls.project_name = data_utils.rand_name('TestProject')
        cls.project_description = data_utils.rand_name('description')
        cls.openstack(
            'project create '
            '--domain %(domain)s '
            '--description %(description)s '
            '--enable '
            '%(name)s' % {'domain': cls.domain_name,
                          'description': cls.project_description,
                          'name': cls.project_name})

    @classmethod
    def tearDownClass(cls):
        cls.openstack('project delete %s' % cls.project_name)
        cls.openstack('domain set --disable %s' % cls.domain_name)
        cls.openstack('domain delete %s' % cls.domain_name)

        if hasattr(super(IdentityTests, cls), 'tearDownClass'):
            super(IdentityTests, cls).tearDownClass()

    def _create_dummy_user(self, add_clean_up=True):
        username = data_utils.rand_name('TestUser')
        password = data_utils.rand_name('password')
        email = data_utils.rand_name() + '@example.com'
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'user create '
            '--domain %(domain)s '
            '--project %(project)s '
            '--password %(password)s '
            '--email %(email)s '
            '--description %(description)s '
            '--enable '
            '%(name)s' % {'domain': self.domain_name,
                          'project': self.project_name,
                          'email': email,
                          'password': password,
                          'description': description,
                          'name': username})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'user delete %s' % self.parse_show_as_object(raw_output)['id'])
        return username

    def _create_dummy_role(self, add_clean_up=True):
        role_name = data_utils.rand_name('TestRole')
        raw_output = self.openstack('role create %s' % role_name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)
        role = self.parse_show_as_object(raw_output)
        self.assertEqual(role_name, role['name'])
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'role delete %s' % role['id'])
        return role_name

    def _create_dummy_group(self, add_clean_up=True):
        group_name = data_utils.rand_name('TestGroup')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'group create '
            '--domain %(domain)s '
            '--description %(description)s '
            '%(name)s' % {'domain': self.domain_name,
                          'description': description,
                          'name': group_name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.GROUP_FIELDS)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'group delete '
                '--domain %(domain)s '
                '%(name)s' % {'domain': self.domain_name,
                              'name': group_name})
        return group_name

    def _create_dummy_domain(self, add_clean_up=True):
        domain_name = data_utils.rand_name('TestDomain')
        domain_description = data_utils.rand_name('description')
        self.openstack(
            'domain create '
            '--description %(description)s '
            '--enable %(name)s' % {'description': domain_description,
                                   'name': domain_name})
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'domain delete %s' % domain_name
            )
            self.addCleanup(
                self.openstack,
                'domain set --disable %s' % domain_name
            )
        return domain_name

    def _create_dummy_project(self, add_clean_up=True):
        project_name = data_utils.rand_name('TestProject')
        project_description = data_utils.rand_name('description')
        self.openstack(
            'project create '
            '--domain %(domain)s '
            '--description %(description)s '
            '--enable %(name)s' % {'domain': self.domain_name,
                                   'description': project_description,
                                   'name': project_name})
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'project delete '
                '--domain %(domain)s '
                '%(name)s' % {'domain': self.domain_name,
                              'name': project_name})
        return project_name
