#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock

from openstackclient.compute.v2 import security_group
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


security_group_id = '11'
security_group_name = 'wide-open'
security_group_description = 'nothing but net'

SECURITY_GROUP = {
    'id': security_group_id,
    'name': security_group_name,
    'description': security_group_description,
    'tenant_id': identity_fakes.project_id,
}


class FakeSecurityGroupResource(fakes.FakeResource):

    def get_keys(self):
        return {'property': 'value'}


class TestSecurityGroup(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroup, self).setUp()

        self.secgroups_mock = mock.Mock()
        self.secgroups_mock.resource_class = fakes.FakeResource(None, {})
        self.app.client_manager.compute.security_groups = self.secgroups_mock
        self.secgroups_mock.reset_mock()

        self.projects_mock = mock.Mock()
        self.projects_mock.resource_class = fakes.FakeResource(None, {})
        self.app.client_manager.identity.projects = self.projects_mock
        self.projects_mock.reset_mock()


class TestSecurityGroupCreate(TestSecurityGroup):

    def setUp(self):
        super(TestSecurityGroupCreate, self).setUp()

        self.secgroups_mock.create.return_value = FakeSecurityGroupResource(
            None,
            copy.deepcopy(SECURITY_GROUP),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, None)

    def test_security_group_create_no_options(self):
        arglist = [
            security_group_name,
        ]
        verifylist = [
            ('name', security_group_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.secgroups_mock.create.assert_called_with(
            security_group_name,
            security_group_name,
        )

        collist = (
            'description',
            'id',
            'name',
            'tenant_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            security_group_description,
            security_group_id,
            security_group_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)

    def test_security_group_create_description(self):
        arglist = [
            security_group_name,
            '--description', security_group_description,
        ]
        verifylist = [
            ('name', security_group_name),
            ('description', security_group_description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # SecurityGroupManager.create(name, description)
        self.secgroups_mock.create.assert_called_with(
            security_group_name,
            security_group_description,
        )

        collist = (
            'description',
            'id',
            'name',
            'tenant_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            security_group_description,
            security_group_id,
            security_group_name,
            identity_fakes.project_id,
        )
        self.assertEqual(datalist, data)


class TestSecurityGroupList(TestSecurityGroup):

    def setUp(self):
        super(TestSecurityGroupList, self).setUp()

        self.secgroups_mock.list.return_value = [
            FakeSecurityGroupResource(
                None,
                copy.deepcopy(SECURITY_GROUP),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, None)

    def test_security_group_list_no_options(self):
        self.projects_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.PROJECT),
                loaded=True,
            ),
        ]

        arglist = []
        verifylist = [
            ('all_projects', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'search_opts': {
                'all_tenants': False,
            },
        }

        self.secgroups_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'Description',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            security_group_id,
            security_group_name,
            security_group_description,
        ), )
        self.assertEqual(datalist, tuple(data))
