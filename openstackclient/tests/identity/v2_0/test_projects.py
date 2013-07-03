#   Copyright 2013 Nebula Inc.
#
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

from openstackclient.identity.v2_0 import project
from openstackclient.tests import fakes
from openstackclient.tests.identity import fakes as identity_fakes
from openstackclient.tests import utils


IDENTITY_API_VERSION = "2.0"

user_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
user_name = 'paul'
user_description = 'Sir Paul'

project_id = '8-9-64'
project_name = 'beatles'
project_description = 'Fab Four'

USER = {
    'id': user_id,
    'name': user_name,
    'tenantId': project_id,
}

PROJECT = {
    'id': project_id,
    'name': project_name,
    'description': project_description,
    'enabled': True,
}


class TestProject(utils.TestCommand):

    def setUp(self):
        super(TestProject, self).setUp()
        self.app.client_manager.identity = \
            identity_fakes.FakeIdentityv2Client()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants


class TestProjectCreate(TestProject):

    def setUp(self):
        super(TestProjectCreate, self).setUp()

        self.projects_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = project.CreateProject(self.app, None)

    def test_project_create_no_options(self):
        arglist = [project_name]
        verifylist = [
            ('project_name', project_name),
            ('enable', False),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(project_name, **kwargs)

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(columns, collist)
        datalist = (project_description, True, project_id, project_name)
        self.assertEqual(data, datalist)

    def test_project_create_description(self):
        arglist = ['--description', 'new desc', project_name]
        verifylist = [('description', 'new desc')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new desc',
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(project_name, **kwargs)

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(columns, collist)
        datalist = (project_description, True, project_id, project_name)
        self.assertEqual(data, datalist)

    def test_project_create_enable(self):
        arglist = ['--enable', project_name]
        verifylist = [('enable', True), ('disable', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(project_name, **kwargs)

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(columns, collist)
        datalist = (project_description, True, project_id, project_name)
        self.assertEqual(data, datalist)

    def test_project_create_disable(self):
        arglist = ['--disable', project_name]
        verifylist = [('enable', False), ('disable', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': False,
        }
        self.projects_mock.create.assert_called_with(project_name, **kwargs)

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(columns, collist)
        datalist = (project_description, True, project_id, project_name)
        self.assertEqual(data, datalist)


class TestProjectDelete(TestProject):

    def setUp(self):
        super(TestProjectDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT),
            loaded=True,
        )
        self.projects_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = project.DeleteProject(self.app, None)

    def test_project_delete_no_options(self):
        arglist = [user_id]
        verifylist = [('project', user_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(result, 0)

        self.projects_mock.delete.assert_called_with(project_id)


class TestProjectList(TestProject):

    def setUp(self):
        super(TestProjectList, self).setUp()

        self.projects_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(PROJECT),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = project.ListProject(self.app, None)

    def test_project_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(columns, collist)
        datalist = ((project_id, project_name), )
        self.assertEqual(tuple(data), datalist)

    def test_project_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Description', 'Enabled')
        self.assertEqual(columns, collist)
        datalist = ((project_id, project_name, project_description, True), )
        self.assertEqual(tuple(data), datalist)


class TestProjectSet(TestProject):

    def setUp(self):
        super(TestProjectSet, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = project.SetProject(self.app, None)

    def test_project_set_no_options(self):
        arglist = [project_name]
        verifylist = [
            ('project', project_name),
            ('enable', False),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(result, 0)

        # Set expected values
        kwargs = {
            'description': project_description,
            'enabled': True,
            'tenant_name': project_name,
        }
        self.projects_mock.update.assert_called_with(project_id, **kwargs)

    def test_project_set_name(self):
        arglist = ['--name', 'qwerty', project_name]
        verifylist = [('name', 'qwerty')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(result, 0)

        # Set expected values
        kwargs = {
            'description': project_description,
            'enabled': True,
            'tenant_name': 'qwerty',
        }
        self.projects_mock.update.assert_called_with(project_id, **kwargs)

    def test_project_set_description(self):
        arglist = ['--description', 'new desc', project_name]
        verifylist = [('description', 'new desc')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(result, 0)

        # Set expected values
        kwargs = {
            'description': 'new desc',
            'enabled': True,
            'tenant_name': project_name,
        }
        self.projects_mock.update.assert_called_with(project_id, **kwargs)

    def test_project_set_enable(self):
        arglist = ['--enable', project_name]
        verifylist = [('enable', True), ('disable', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(result, 0)

        # Set expected values
        kwargs = {
            'description': project_description,
            'enabled': True,
            'tenant_name': project_name,
        }
        self.projects_mock.update.assert_called_with(project_id, **kwargs)

    def test_project_set_disable(self):
        arglist = ['--disable', project_name]
        verifylist = [('enable', False), ('disable', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(result, 0)

        # Set expected values
        kwargs = {
            'description': project_description,
            'enabled': False,
            'tenant_name': project_name,
        }
        self.projects_mock.update.assert_called_with(project_id, **kwargs)


class TestProjectShow(TestProject):

    def setUp(self):
        super(TestProjectShow, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(PROJECT),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = project.ShowProject(self.app, None)

    def test_project_show(self):
        arglist = [user_id]
        verifylist = [('project', user_id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_with(user_id)

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(columns, collist)
        datalist = (project_description, True, project_id, project_name)
        self.assertEqual(data, datalist)
