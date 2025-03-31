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

import fixtures
from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional import base


BASIC_LIST_HEADERS = ['ID', 'Name']
SYSTEM_CLOUD = os.environ.get('OS_SYSTEM_CLOUD', 'devstack-system-admin')


class IdentityTests(base.TestCase):
    """Functional tests for Identity commands."""

    DOMAIN_FIELDS = ['description', 'enabled', 'id', 'name']
    GROUP_FIELDS = ['description', 'domain_id', 'id', 'name']
    TOKEN_FIELDS = ['expires', 'id', 'project_id', 'user_id']
    USER_FIELDS = [
        'email',
        'enabled',
        'id',
        'name',
        'domain_id',
        'default_project_id',
        'description',
        'password_expires_at',
    ]
    PROJECT_FIELDS = [
        'description',
        'id',
        'domain_id',
        'is_domain',
        'enabled',
        'name',
        'parent_id',
    ]
    ROLE_FIELDS = ['id', 'name', 'domain_id', 'description']
    SERVICE_FIELDS = ['id', 'enabled', 'name', 'type', 'description']
    REGION_FIELDS = ['description', 'parent_region', 'region']
    ENDPOINT_FIELDS = [
        'id',
        'region',
        'region_id',
        'service_id',
        'service_name',
        'service_type',
        'enabled',
        'interface',
        'url',
    ]

    REGION_LIST_HEADERS = ['Region', 'Parent Region', 'Description']
    ENDPOINT_LIST_HEADERS = [
        'ID',
        'Region',
        'Service Name',
        'Service Type',
        'Enabled',
        'Interface',
        'URL',
    ]
    ENDPOINT_LIST_PROJECT_HEADERS = ['ID', 'Name']

    IDENTITY_PROVIDER_FIELDS = [
        'description',
        'enabled',
        'id',
        'remote_ids',
        'domain_id',
    ]
    IDENTITY_PROVIDER_LIST_HEADERS = ['ID', 'Enabled', 'Description']

    SERVICE_PROVIDER_FIELDS = [
        'auth_url',
        'description',
        'enabled',
        'id',
        'relay_state_prefix',
        'sp_url',
    ]
    SERVICE_PROVIDER_LIST_HEADERS = [
        'ID',
        'Enabled',
        'Description',
        'Auth URL',
    ]
    IMPLIED_ROLE_LIST_HEADERS = [
        'Prior Role ID',
        'Prior Role Name',
        'Implied Role ID',
        'Implied Role Name',
    ]
    ROLE_ASSIGNMENT_LIST_HEADERS = [
        'Role',
        'User',
        'Group',
        'Project',
        'Domain',
        'System',
        'Inherited',
    ]
    REGISTERED_LIMIT_FIELDS = [
        'id',
        'service_id',
        'resource_name',
        'default_limit',
        'description',
        'region_id',
    ]
    REGISTERED_LIMIT_LIST_HEADERS = [
        'ID',
        'Service ID',
        'Resource Name',
        'Default Limit',
        'Description',
        'Region ID',
    ]
    LIMIT_FIELDS = [
        'id',
        'project_id',
        'service_id',
        'resource_name',
        'resource_limit',
        'description',
        'region_id',
    ]
    LIMIT_LIST_HEADERS = [
        'ID',
        'Project ID',
        'Service ID',
        'Resource Name',
        'Resource Limit',
        'Description',
        'Region ID',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create dummy domain
        cls.domain_name = data_utils.rand_name('TestDomain')
        cls.domain_description = data_utils.rand_name('description')
        cls.openstack(
            '--os-identity-api-version 3 '
            'domain create '
            f'--description {cls.domain_description} '
            '--enable '
            f'{cls.domain_name}'
        )

        # create dummy project
        cls.project_name = data_utils.rand_name('TestProject')
        cls.project_description = data_utils.rand_name('description')
        cls.openstack(
            '--os-identity-api-version 3 '
            'project create '
            f'--domain {cls.domain_name} '
            f'--description {cls.project_description} '
            '--enable '
            f'{cls.project_name}'
        )

    @classmethod
    def tearDownClass(cls):
        try:
            # delete dummy project
            cls.openstack(
                '--os-identity-api-version 3 '
                f'project delete {cls.project_name}'
            )
            # disable and delete dummy domain
            cls.openstack(
                '--os-identity-api-version 3 '
                f'domain set --disable {cls.domain_name}'
            )
            cls.openstack(
                f'--os-identity-api-version 3 domain delete {cls.domain_name}'
            )
        finally:
            super().tearDownClass()

    def setUp(self):
        super().setUp()
        # prepare v3 env
        ver_fixture = fixtures.EnvironmentVariable(
            'OS_IDENTITY_API_VERSION', '3'
        )
        self.useFixture(ver_fixture)
        auth_url = os.environ.get('OS_AUTH_URL')
        if auth_url:
            auth_url_fixture = fixtures.EnvironmentVariable(
                'OS_AUTH_URL', auth_url.replace('v2.0', 'v3')
            )
            self.useFixture(auth_url_fixture)

    def _create_dummy_user(self, add_clean_up=True):
        username = data_utils.rand_name('TestUser')
        password = data_utils.rand_name('password')
        email = data_utils.rand_name() + '@example.com'
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'user create '
            f'--domain {self.domain_name} '
            f'--project {self.project_name} '
            f'--project-domain {self.domain_name} '
            f'--password {password} '
            f'--email {email} '
            f'--description {description} '
            '--enable '
            f'{username}'
        )
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'user delete {}'.format(
                    self.parse_show_as_object(raw_output)['id']
                ),
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)
        return username

    def _create_dummy_role(self, add_clean_up=True):
        role_name = data_utils.rand_name('TestRole')
        raw_output = self.openstack(f'role create {role_name}')
        role = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack, 'role delete {}'.format(role['id'])
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ROLE_FIELDS)
        self.assertEqual(role_name, role['name'])
        return role_name

    def _create_dummy_implied_role(self, add_clean_up=True):
        role_name = self._create_dummy_role(add_clean_up)
        implied_role_name = self._create_dummy_role(add_clean_up)
        self.openstack(
            'implied role create '
            f'--implied-role {implied_role_name} '
            f'{role_name}'
        )

        return implied_role_name, role_name

    def _create_dummy_group(self, add_clean_up=True):
        group_name = data_utils.rand_name('TestGroup')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'group create '
            f'--domain {self.domain_name} '
            f'--description {description} '
            f'{group_name}'
        )
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                f'group delete --domain {self.domain_name} {group_name}',
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.GROUP_FIELDS)
        return group_name

    def _create_dummy_domain(self, add_clean_up=True):
        domain_name = data_utils.rand_name('TestDomain')
        domain_description = data_utils.rand_name('description')
        self.openstack(
            'domain create '
            f'--description {domain_description} '
            f'--enable {domain_name}'
        )
        if add_clean_up:
            self.addCleanup(self.openstack, f'domain delete {domain_name}')
            self.addCleanup(
                self.openstack, f'domain set --disable {domain_name}'
            )
        return domain_name

    def _create_dummy_project(self, add_clean_up=True):
        project_name = data_utils.rand_name('TestProject')
        project_description = data_utils.rand_name('description')
        self.openstack(
            'project create '
            f'--domain {self.domain_name} '
            f'--description {project_description} '
            f'--enable {project_name}'
        )
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                f'project delete --domain {self.domain_name} {project_name}',
            )
        return project_name

    def _create_dummy_region(self, parent_region=None, add_clean_up=True):
        region_id = data_utils.rand_name('TestRegion')
        description = data_utils.rand_name('description')
        parent_region_arg = ''
        if parent_region is not None:
            parent_region_arg = f'--parent-region {parent_region}'
        raw_output = self.openstack(
            'region create '
            f'{parent_region_arg} '
            f'--description {description} '
            f'{region_id}'
        )
        if add_clean_up:
            self.addCleanup(self.openstack, f'region delete {region_id}')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.REGION_FIELDS)
        return region_id

    def _create_dummy_service(self, add_clean_up=True):
        service_name = data_utils.rand_name('TestService')
        description = data_utils.rand_name('description')
        type_name = data_utils.rand_name('TestType')
        raw_output = self.openstack(
            'service create '
            f'--name {service_name} '
            f'--description {description} '
            '--enable '
            f'{type_name}'
        )
        if add_clean_up:
            service = self.parse_show_as_object(raw_output)
            self.addCleanup(
                self.openstack, 'service delete {}'.format(service['id'])
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.SERVICE_FIELDS)
        return service_name

    def _create_dummy_endpoint(self, interface='public', add_clean_up=True):
        region_id = self._create_dummy_region()
        service_name = self._create_dummy_service()
        endpoint_url = data_utils.rand_url()
        raw_output = self.openstack(
            'endpoint create '
            f'--region {region_id} '
            '--enable '
            f'{service_name} '
            f'{interface} '
            f'{endpoint_url}'
        )
        endpoint = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack, 'endpoint delete {}'.format(endpoint['id'])
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_FIELDS)
        return endpoint['id']

    def _create_dummy_idp(self, add_clean_up=True):
        identity_provider = data_utils.rand_name('IdentityProvider')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'identity provider create '
            f' {identity_provider} '
            f'--description {description} '
            '--enable '
        )
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                f'identity provider delete {identity_provider}',
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.IDENTITY_PROVIDER_FIELDS)
        return identity_provider

    def _create_dummy_sp(self, add_clean_up=True):
        service_provider = data_utils.rand_name('ServiceProvider')
        description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'service provider create '
            f' {service_provider} '
            f'--description {description} '
            '--auth-url https://sp.example.com:35357 '
            '--service-provider-url https://sp.example.com:5000 '
            '--enable '
        )
        if add_clean_up:
            self.addCleanup(
                self.openstack, f'service provider delete {service_provider}'
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.SERVICE_PROVIDER_FIELDS)
        return service_provider

    def _create_dummy_registered_limit(self, add_clean_up=True):
        service_name = self._create_dummy_service()
        resource_name = data_utils.rand_name('resource_name')
        params = {
            'service_name': service_name,
            'default_limit': 10,
            'resource_name': resource_name,
        }
        raw_output = self.openstack(
            'registered limit create'
            ' --service {service_name}'
            ' --default-limit {default_limit}'
            ' {resource_name}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        registered_limit_id = self._extract_value_from_items('id', items)

        if add_clean_up:
            self.addCleanup(
                self.openstack,
                f'registered limit delete {registered_limit_id}',
                cloud=SYSTEM_CLOUD,
            )

        self.assert_show_fields(items, self.REGISTERED_LIMIT_FIELDS)
        return registered_limit_id

    def _extract_value_from_items(self, key, items):
        for d in items:
            for k, v in d.items():
                if k == key:
                    return v

    def _create_dummy_limit(self, add_clean_up=True):
        registered_limit_id = self._create_dummy_registered_limit()

        raw_output = self.openstack(
            f'registered limit show {registered_limit_id}',
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        resource_name = self._extract_value_from_items('resource_name', items)
        service_id = self._extract_value_from_items('service_id', items)
        resource_limit = 15

        project_name = self._create_dummy_project()
        raw_output = self.openstack(f'project show {project_name}')
        items = self.parse_show(raw_output)
        project_id = self._extract_value_from_items('id', items)

        params = {
            'project_id': project_id,
            'service_id': service_id,
            'resource_name': resource_name,
            'resource_limit': resource_limit,
        }

        raw_output = self.openstack(
            'limit create'
            ' --project {project_id}'
            ' --service {service_id}'
            ' --resource-limit {resource_limit}'
            ' {resource_name}'.format(**params),
            cloud=SYSTEM_CLOUD,
        )
        items = self.parse_show(raw_output)
        limit_id = self._extract_value_from_items('id', items)

        if add_clean_up:
            self.addCleanup(
                self.openstack,
                f'limit delete {limit_id}',
                cloud=SYSTEM_CLOUD,
            )

        self.assert_show_fields(items, self.LIMIT_FIELDS)
        return limit_id
