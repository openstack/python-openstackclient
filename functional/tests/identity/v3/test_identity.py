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
    PROJECT_FIELDS = ['description', 'id', 'domain_id', 'is_domain',
                      'enabled', 'name', 'parent_id', 'links']
    ROLE_FIELDS = ['id', 'name', 'links']
    SERVICE_FIELDS = ['id', 'enabled', 'name', 'type', 'description']
    REGION_FIELDS = ['description', 'enabled', 'parent_region',
                     'region', 'url']
    ENDPOINT_FIELDS = ['id', 'region', 'region_id', 'service_id',
                       'service_name', 'service_type', 'enabled',
                       'interface', 'url']

    REGION_LIST_HEADERS = ['Region', 'Parent Region', 'Description', 'URL']
    ENDPOINT_LIST_HEADERS = ['ID', 'Region', 'Service Name', 'Service Type',
                             'Enabled', 'Interface', 'URL']

    IDENTITY_PROVIDER_FIELDS = ['description', 'enabled', 'id', 'remote_ids']
    IDENTITY_PROVIDER_LIST_HEADERS = ['ID', 'Enabled', 'Description']

    @classmethod
    def setUpClass(cls):
        if hasattr(super(IdentityTests, cls), 'setUpClass'):
            super(IdentityTests, cls).setUpClass()

        # prepare v3 env
        auth_url = os.environ.get('OS_AUTH_URL')
        auth_url = auth_url.replace('v2.0', 'v3')
        os.environ['OS_AUTH_URL'] = auth_url
        os.environ['OS_IDENTITY_API_VERSION'] = '3'
        os.environ['OS_AUTH_TYPE'] = 'v3password'

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
        # delete dummy project
        cls.openstack('project delete %s' % cls.project_name)
        # disable and delete dummy domain
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
            '--project-domain %(project_domain)s '
            '--password %(password)s '
            '--email %(email)s '
            '--description %(description)s '
            '--enable '
            '%(name)s' % {'domain': self.domain_name,
                          'project': self.project_name,
                          'project_domain': self.domain_name,
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

    def _create_dummy_region(self, parent_region=None, add_clean_up=True):
        region_id = data_utils.rand_name('TestRegion')
        description = data_utils.rand_name('description')
        url = data_utils.rand_url()
        parent_region_arg = ''
        if parent_region is not None:
            parent_region_arg = '--parent-region %s' % parent_region
        raw_output = self.openstack(
            'region create '
            '%(parent_region_arg)s '
            '--description %(description)s '
            '--url %(url)s '
            '%(id)s' % {'parent_region_arg': parent_region_arg,
                        'description': description,
                        'url': url,
                        'id': region_id})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGION_FIELDS)
        if add_clean_up:
            self.addCleanup(self.openstack,
                            'region delete %s' % region_id)
        return region_id

    def _create_dummy_service(self, add_clean_up=True):
        service_name = data_utils.rand_name('TestService')
        description = data_utils.rand_name('description')
        type_name = data_utils.rand_name('TestType')
        raw_output = self.openstack(
            'service create '
            '--name %(name)s '
            '--description %(description)s '
            '--enable '
            '%(type)s' % {'name': service_name,
                          'description': description,
                          'type': type_name})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.SERVICE_FIELDS)
        if add_clean_up:
            service = self.parse_show_as_object(raw_output)
            self.addCleanup(self.openstack,
                            'service delete %s' % service['id'])
        return service_name

    def _create_dummy_endpoint(self, interface='public', add_clean_up=True):
        region_id = self._create_dummy_region()
        service_name = self._create_dummy_service()
        endpoint_url = data_utils.rand_url()
        raw_output = self.openstack(
            'endpoint create '
            '--region %(region)s '
            '--enable '
            '%(service)s '
            '%(interface)s '
            '%(url)s' % {'region': region_id,
                         'service': service_name,
                         'interface': interface,
                         'url': endpoint_url})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_FIELDS)
        endpoint = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'endpoint delete %s' % endpoint['id'])
        return endpoint['id']

    def _create_dummy_idp(self, add_clean_up=True):
        identity_provider = data_utils.rand_name('IdentityProvider')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'identity provider create '
            ' %(name)s '
            '--description %(description)s '
            '--enable ' % {'name': identity_provider,
                           'description': description})
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.IDENTITY_PROVIDER_FIELDS)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'identity provider delete %s' % identity_provider)
        return identity_provider
