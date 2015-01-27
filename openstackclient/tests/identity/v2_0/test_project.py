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

from keystoneclient import exceptions as ksc_exc

from openstackclient.identity.v2_0 import project
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


class TestProject(identity_fakes.TestIdentityv2):

    def setUp(self):
        super(TestProject, self).setUp()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.app.client_manager.identity.tenants
        self.projects_mock.reset_mock()


class TestProjectCreate(TestProject):

    def setUp(self):
        super(TestProjectCreate, self).setUp()

        self.projects_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = project.CreateProject(self.app, None)

    def test_project_create_no_options(self):
        arglist = [
            identity_fakes.project_name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', False),
            ('name', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)

    def test_project_create_description(self):
        arglist = [
            '--description', 'new desc',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('name', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new desc',
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)

    def test_project_create_enable(self):
        arglist = [
            '--enable',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('enable', True),
            ('disable', False),
            ('name', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)

    def test_project_create_disable(self):
        arglist = [
            '--disable',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', True),
            ('name', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': False,
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)

    def test_project_create_property(self):
        arglist = [
            '--property', 'fee=fi',
            '--property', 'fo=fum',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('property', {'fee': 'fi', 'fo': 'fum'}),
            ('name', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
            'fee': 'fi',
            'fo': 'fum',
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)

    def test_project_create_or_show_exists(self):
        def _raise_conflict(*args, **kwargs):
            raise ksc_exc.Conflict(None)

        # need to make this throw an exception...
        self.projects_mock.create.side_effect = _raise_conflict

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        arglist = [
            '--or-show',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('name', identity_fakes.project_name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # ProjectManager.create(name, description, enabled)
        self.projects_mock.get.assert_called_with(identity_fakes.project_name)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)

    def test_project_create_or_show_not_exists(self):
        arglist = [
            '--or-show',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('name', identity_fakes.project_name),
            ('or_show', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            identity_fakes.project_name,
            **kwargs
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)


class TestProjectDelete(TestProject):

    def setUp(self):
        super(TestProjectDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.projects_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = project.DeleteProject(self.app, None)

    def test_project_delete_no_options(self):
        arglist = [
            identity_fakes.project_id,
        ]
        verifylist = [
            ('projects', [identity_fakes.project_id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        self.projects_mock.delete.assert_called_with(
            identity_fakes.project_id,
        )


class TestProjectList(TestProject):

    def setUp(self):
        super(TestProjectList, self).setUp()

        self.projects_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.PROJECT),
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
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.project_id,
            identity_fakes.project_name,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_project_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.project_id,
            identity_fakes.project_name,
            identity_fakes.project_description,
            True,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestProjectSet(TestProject):

    def setUp(self):
        super(TestProjectSet, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.projects_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = project.SetProject(self.app, None)

    def test_project_set_no_options(self):
        arglist = [
            identity_fakes.project_name,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
            ('enable', False),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

    def test_project_set_name(self):
        arglist = [
            '--name', 'qwerty',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('enable', False),
            ('disable', False),
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': identity_fakes.project_description,
            'enabled': True,
            'tenant_name': 'qwerty',
        }
        self.projects_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )

    def test_project_set_description(self):
        arglist = [
            '--description', 'new desc',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('enable', False),
            ('disable', False),
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': 'new desc',
            'enabled': True,
            'tenant_name': identity_fakes.project_name,
        }
        self.projects_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )

    def test_project_set_enable(self):
        arglist = [
            '--enable',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('enable', True),
            ('disable', False),
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': identity_fakes.project_description,
            'enabled': True,
            'tenant_name': identity_fakes.project_name,
        }
        self.projects_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )

    def test_project_set_disable(self):
        arglist = [
            '--disable',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', True),
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': identity_fakes.project_description,
            'enabled': False,
            'tenant_name': identity_fakes.project_name,
        }
        self.projects_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )

    def test_project_set_property(self):
        arglist = [
            '--property', 'fee=fi',
            '--property', 'fo=fum',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('property', {'fee': 'fi', 'fo': 'fum'}),
            ('project', identity_fakes.project_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'description': identity_fakes.project_description,
            'enabled': True,
            'tenant_name': identity_fakes.project_name,
            'fee': 'fi',
            'fo': 'fum',
        }
        self.projects_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )


class TestProjectShow(TestProject):

    def setUp(self):
        super(TestProjectShow, self).setUp()

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = project.ShowProject(self.app, None)

    def test_project_show(self):
        arglist = [
            identity_fakes.project_id,
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_with(
            identity_fakes.project_id,
        )

        collist = ('description', 'enabled', 'id', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.project_description,
            True,
            identity_fakes.project_id,
            identity_fakes.project_name,
        )
        self.assertEqual(datalist, data)
