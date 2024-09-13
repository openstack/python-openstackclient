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
import unittest

import fixtures
from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions as tempest_exceptions

from openstackclient.tests.functional import base

BASIC_LIST_HEADERS = ['ID', 'Name']


class IdentityTests(base.TestCase):
    """Functional tests for Identity commands."""

    USER_FIELDS = ['email', 'enabled', 'id', 'name', 'project_id', 'username']
    PROJECT_FIELDS = ['enabled', 'id', 'name', 'description']
    TOKEN_FIELDS = ['expires', 'id', 'project_id', 'user_id']
    ROLE_FIELDS = ['id', 'name', 'domain_id']
    SERVICE_FIELDS = ['id', 'enabled', 'name', 'type', 'description']
    ENDPOINT_FIELDS = [
        'id',
        'region',
        'service_id',
        'service_name',
        'service_type',
        'publicurl',
        'adminurl',
        'internalurl',
    ]

    EC2_CREDENTIALS_FIELDS = [
        'access',
        'project_id',
        'secret',
        'trust_id',
        'user_id',
    ]
    EC2_CREDENTIALS_LIST_HEADERS = [
        'Access',
        'Secret',
        'Project ID',
        'User ID',
    ]
    CATALOG_LIST_HEADERS = ['Name', 'Type', 'Endpoints']
    ENDPOINT_LIST_HEADERS = ['ID', 'Region', 'Service Name', 'Service Type']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create dummy project
        cls.project_name = data_utils.rand_name('TestProject')
        cls.project_description = data_utils.rand_name('description')
        try:
            cls.openstack(
                '--os-identity-api-version 2 '
                'project create '
                f'--description {cls.project_description} '
                '--enable '
                f'{cls.project_name}'
            )
        except tempest_exceptions.CommandFailed:
            # Good chance this is due to Identity v2 admin not being enabled
            # TODO(dtroyer): Actually determine if Identity v2 admin is
            #                enabled in the target cloud.  Tuens out OSC
            #                doesn't make this easy as it should (yet).
            raise unittest.case.SkipTest('No Identity v2 admin endpoint?')

    @classmethod
    def tearDownClass(cls):
        try:
            cls.openstack(
                '--os-identity-api-version 2 '
                f'project delete {cls.project_name}'
            )
        finally:
            super().tearDownClass()

    def setUp(self):
        super().setUp()
        # prepare v2 env
        ver_fixture = fixtures.EnvironmentVariable(
            'OS_IDENTITY_API_VERSION', '2.0'
        )
        self.useFixture(ver_fixture)
        auth_url = os.environ.get('OS_AUTH_URL')
        if auth_url:
            auth_url_fixture = fixtures.EnvironmentVariable(
                'OS_AUTH_URL', auth_url.replace('v3', 'v2.0')
            )
            self.useFixture(auth_url_fixture)

    def _create_dummy_project(self, add_clean_up=True):
        project_name = data_utils.rand_name('TestProject')
        project_description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'project create '
            f'--description {project_description} '
            f'--enable {project_name}'
        )
        project = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack, 'project delete {}'.format(project['id'])
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.PROJECT_FIELDS)
        return project_name

    def _create_dummy_user(self, add_clean_up=True):
        username = data_utils.rand_name('TestUser')
        password = data_utils.rand_name('password')
        email = data_utils.rand_name() + '@example.com'
        raw_output = self.openstack(
            'user create '
            f'--project {self.project_name} '
            f'--password {password} '
            f'--email {email} '
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

    def _create_dummy_ec2_credentials(self, add_clean_up=True):
        raw_output = self.openstack('ec2 credentials create')
        ec2_credentials = self.parse_show_as_object(raw_output)
        access_key = ec2_credentials['access']
        if add_clean_up:
            self.addCleanup(
                self.openstack, f'ec2 credentials delete {access_key}'
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.EC2_CREDENTIALS_FIELDS)
        return access_key

    def _create_dummy_token(self, add_clean_up=True):
        raw_output = self.openstack('token issue')
        token = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack, 'token revoke {}'.format(token['id'])
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.TOKEN_FIELDS)
        return token['id']

    def _create_dummy_service(self, add_clean_up=True):
        service_name = data_utils.rand_name('TestService')
        description = data_utils.rand_name('description')
        type_name = data_utils.rand_name('TestType')
        raw_output = self.openstack(
            'service create '
            f'--name {service_name} '
            f'--description {description} '
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

    def _create_dummy_endpoint(self, add_clean_up=True):
        region_id = data_utils.rand_name('TestRegion')
        service_name = self._create_dummy_service()
        public_url = data_utils.rand_url()
        admin_url = data_utils.rand_url()
        internal_url = data_utils.rand_url()
        raw_output = self.openstack(
            'endpoint create '
            f'--publicurl {public_url} '
            f'--adminurl {admin_url} '
            f'--internalurl {internal_url} '
            f'--region {region_id} '
            f'{service_name}'
        )
        endpoint = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack, 'endpoint delete {}'.format(endpoint['id'])
            )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_FIELDS)
        return endpoint['id']
