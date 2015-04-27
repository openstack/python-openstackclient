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

from functional.common import exceptions
from functional.common import test

BASIC_LIST_HEADERS = ['ID', 'Name']


class IdentityTests(test.TestCase):
    """Functional tests for Identity commands. """

    USER_FIELDS = ['email', 'enabled', 'id', 'name', 'project_id', 'username']
    PROJECT_FIELDS = ['enabled', 'id', 'name', 'description']
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

    def test_user_list(self):
        raw_output = self.openstack('user list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

    def test_user_show(self):
        raw_output = self.openstack('user show admin')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)

    def test_user_create(self):
        raw_output = self.openstack('user create mjordan --password bulls'
                                    ' --email hoops@example.com')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.USER_FIELDS)

    def test_user_delete(self):
        self.openstack('user create dummy')
        raw_output = self.openstack('user delete dummy')
        self.assertEqual(0, len(raw_output))

    def test_bad_user_command(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.openstack, 'user unlist')

    def test_project_list(self):
        raw_output = self.openstack('project list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, BASIC_LIST_HEADERS)

    def test_project_show(self):
        raw_output = self.openstack('project show admin')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.PROJECT_FIELDS)

    def test_project_create(self):
        raw_output = self.openstack('project create test-project')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.PROJECT_FIELDS)

    def test_project_delete(self):
        self.openstack('project create dummy-project')
        raw_output = self.openstack('project delete dummy-project')
        self.assertEqual(0, len(raw_output))

    def test_ec2_credentials_create(self):
        create_output = self.openstack('ec2 credentials create')
        create_items = self.parse_show(create_output)
        self.openstack(
            'ec2 credentials delete %s' % create_items[0]['access'],
        )
        self.assert_show_fields(create_items, self.EC2_CREDENTIALS_FIELDS)

    def test_ec2_credentials_delete(self):
        create_output = self.openstack('ec2 credentials create')
        create_items = self.parse_show(create_output)
        raw_output = self.openstack(
            'ec2 credentials delete %s' % create_items[0]['access'],
        )
        self.assertEqual(0, len(raw_output))

    def test_ec2_credentials_list(self):
        raw_output = self.openstack('ec2 credentials list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.EC2_CREDENTIALS_LIST_HEADERS)

    def test_ec2_credentials_show(self):
        create_output = self.openstack('ec2 credentials create')
        create_items = self.parse_show(create_output)
        show_output = self.openstack(
            'ec2 credentials show %s' % create_items[0]['access'],
        )
        items = self.parse_show(show_output)
        self.openstack(
            'ec2 credentials delete %s' % create_items[0]['access'],
        )
        self.assert_show_fields(items, self.EC2_CREDENTIALS_FIELDS)
