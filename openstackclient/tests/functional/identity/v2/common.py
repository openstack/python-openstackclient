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

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional import base

BASIC_LIST_HEADERS = ['ID', 'Name']


class IdentityTests(base.TestCase):
    """Functional tests for Identity commands. """

    USER_FIELDS = ['email', 'enabled', 'id', 'name', 'project_id',
                   'username', 'domain_id', 'default_project_id']
    PROJECT_FIELDS = ['enabled', 'id', 'name', 'description', 'domain_id']
    TOKEN_FIELDS = ['expires', 'id', 'project_id', 'user_id']
    ROLE_FIELDS = ['id', 'name', 'links', 'domain_id']
    SERVICE_FIELDS = ['id', 'enabled', 'name', 'type', 'description']
    ENDPOINT_FIELDS = ['id', 'region', 'service_id', 'service_name',
                       'service_type', 'enabled', 'publicurl',
                       'adminurl', 'internalurl']

    EC2_CREDENTIALS_FIELDS = ['access', 'project_id', 'secret',
                              'trust_id', 'user_id']
    EC2_CREDENTIALS_LIST_HEADERS = ['Access', 'Secret',
                                    'Project ID', 'User ID']
    CATALOG_LIST_HEADERS = ['Name', 'Type', 'Endpoints']
    ENDPOINT_LIST_HEADERS = ['ID', 'Region', 'Service Name', 'Service Type']

    @classmethod
    def setUpClass(cls):
        # prepare v2 env
        os.environ['OS_IDENTITY_API_VERSION'] = '2.0'
        auth_url = os.environ.get('OS_AUTH_URL')
        auth_url = auth_url.replace('v3', 'v2.0')
        os.environ['OS_AUTH_URL'] = auth_url

        # create dummy project
        cls.project_name = data_utils.rand_name('TestProject')
        cls.project_description = data_utils.rand_name('description')
        cls.openstack(
            'project create '
            '--description %(description)s '
            '--enable '
            '%(name)s' % {'description': cls.project_description,
                          'name': cls.project_name})

    @classmethod
    def tearDownClass(cls):
        cls.openstack('project delete %s' % cls.project_name)

    def _create_dummy_project(self, add_clean_up=True):
        project_name = data_utils.rand_name('TestProject')
        project_description = data_utils.rand_name('description')
        raw_output = self.openstack(
            'project create '
            '--description %(description)s '
            '--enable %(name)s' % {'description': project_description,
                                   'name': project_name})
        project = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'project delete %s' % project['id'])
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.PROJECT_FIELDS)
        return project_name

    def _create_dummy_user(self, add_clean_up=True):
        username = data_utils.rand_name('TestUser')
        password = data_utils.rand_name('password')
        email = data_utils.rand_name() + '@example.com'
        raw_output = self.openstack(
            'user create '
            '--project %(project)s '
            '--password %(password)s '
            '--email %(email)s '
            '--enable '
            '%(name)s' % {'project': self.project_name,
                          'email': email,
                          'password': password,
                          'name': username})
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'user delete %s' % self.parse_show_as_object(raw_output)['id'])
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)
        return username

    def _create_dummy_role(self, add_clean_up=True):
        role_name = data_utils.rand_name('TestRole')
        raw_output = self.openstack('role create %s' % role_name)
        role = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'role delete %s' % role['id'])
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
                self.openstack,
                'ec2 credentials delete %s' % access_key)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.EC2_CREDENTIALS_FIELDS)
        return access_key

    def _create_dummy_token(self, add_clean_up=True):
        raw_output = self.openstack('token issue')
        token = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(self.openstack,
                            'token revoke %s' % token['id'])
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.TOKEN_FIELDS)
        return token['id']

    def _create_dummy_service(self, add_clean_up=True):
        service_name = data_utils.rand_name('TestService')
        description = data_utils.rand_name('description')
        type_name = data_utils.rand_name('TestType')
        raw_output = self.openstack(
            'service create '
            '--name %(name)s '
            '--description %(description)s '
            '%(type)s' % {'name': service_name,
                          'description': description,
                          'type': type_name})
        if add_clean_up:
            service = self.parse_show_as_object(raw_output)
            self.addCleanup(self.openstack,
                            'service delete %s' % service['id'])
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
            '--publicurl %(publicurl)s '
            '--adminurl %(adminurl)s '
            '--internalurl %(internalurl)s '
            '--region %(region)s '
            '%(service)s' % {'publicurl': public_url,
                             'adminurl': admin_url,
                             'internalurl': internal_url,
                             'region': region_id,
                             'service': service_name})
        endpoint = self.parse_show_as_object(raw_output)
        if add_clean_up:
            self.addCleanup(
                self.openstack,
                'endpoint delete %s' % endpoint['id'])
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.ENDPOINT_FIELDS)
        return endpoint['id']
