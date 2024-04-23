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

from unittest import mock

from keystoneauth1 import exceptions as ks_exc
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.identity.v2_0 import project
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes


class TestProject(identity_fakes.TestIdentityv2):
    fake_project = identity_fakes.FakeProject.create_one_project()
    fake_projects = identity_fakes.FakeProject.create_projects()

    columns = (
        'description',
        'enabled',
        'id',
        'name',
    )
    datalist = (
        fake_project.description,
        True,
        fake_project.id,
        fake_project.name,
    )
    datalists = (
        (
            fake_projects[0].description,
            True,
            fake_projects[0].id,
            fake_projects[0].name,
        ),
        (
            fake_projects[1].description,
            True,
            fake_projects[1].id,
            fake_projects[1].name,
        ),
    )

    def setUp(self):
        super().setUp()

        # Get a shortcut to the TenantManager Mock
        self.projects_mock = self.identity_client.tenants
        self.projects_mock.reset_mock()


class TestProjectCreate(TestProject):
    def setUp(self):
        super().setUp()

        self.projects_mock.create.return_value = self.fake_project

        # Get the command object to test
        self.cmd = project.CreateProject(self.app, None)

    def test_project_create_no_options(self):
        arglist = [
            self.fake_project.name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', False),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_description(self):
        arglist = [
            '--description',
            'new desc',
            self.fake_project.name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new desc',
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_enable(self):
        arglist = [
            '--enable',
            self.fake_project.name,
        ]
        verifylist = [
            ('enable', True),
            ('disable', False),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_disable(self):
        arglist = [
            '--disable',
            self.fake_project.name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', True),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': False,
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_property(self):
        arglist = [
            '--property',
            'fee=fi',
            '--property',
            'fo=fum',
            self.fake_project.name,
        ]
        verifylist = [
            ('property', {'fee': 'fi', 'fo': 'fum'}),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
            'fee': 'fi',
            'fo': 'fum',
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_or_show_exists(self):
        def _raise_conflict(*args, **kwargs):
            raise ks_exc.Conflict(None)

        # need to make this throw an exception...
        self.projects_mock.create.side_effect = _raise_conflict

        self.projects_mock.get.return_value = self.fake_project

        arglist = [
            '--or-show',
            self.fake_project.name,
        ]
        verifylist = [
            ('or_show', True),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # ProjectManager.create(name, description, enabled)
        self.projects_mock.get.assert_called_with(self.fake_project.name)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_or_show_not_exists(self):
        arglist = [
            '--or-show',
            self.fake_project.name,
        ]
        verifylist = [
            ('or_show', True),
            ('name', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': None,
            'enabled': True,
        }
        self.projects_mock.create.assert_called_with(
            self.fake_project.name, **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)


class TestProjectDelete(TestProject):
    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.projects_mock.get.return_value = self.fake_project
        self.projects_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = project.DeleteProject(self.app, None)

    def test_project_delete_no_options(self):
        arglist = [
            self.fake_project.id,
        ]
        verifylist = [
            ('projects', [self.fake_project.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.projects_mock.delete.assert_called_with(
            self.fake_project.id,
        )
        self.assertIsNone(result)

    @mock.patch.object(utils, 'find_resource')
    def test_delete_multi_projects_with_exception(self, find_mock):
        find_mock.side_effect = [self.fake_project, exceptions.CommandError]
        arglist = [
            self.fake_project.id,
            'unexist_project',
        ]
        verifylist = [
            ('projects', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 projects failed to delete.', str(e))

        find_mock.assert_any_call(self.projects_mock, self.fake_project.id)
        find_mock.assert_any_call(self.projects_mock, 'unexist_project')

        self.assertEqual(2, find_mock.call_count)
        self.projects_mock.delete.assert_called_once_with(self.fake_project.id)


class TestProjectList(TestProject):
    def setUp(self):
        super().setUp()

        self.projects_mock.list.return_value = [self.fake_project]

        # Get the command object to test
        self.cmd = project.ListProject(self.app, None)

    def test_project_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.fake_project.id,
                self.fake_project.name,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_project_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Name', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = (
            (
                self.fake_project.id,
                self.fake_project.name,
                self.fake_project.description,
                True,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_project_list_sort(self):
        self.projects_mock.list.return_value = self.fake_projects

        arglist = [
            '--sort',
            'name:asc',
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        (columns, data) = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Name')
        self.assertEqual(collist, columns)

        if self.fake_projects[0].name > self.fake_projects[1].name:
            datalists = (
                (self.fake_projects[1].id, self.fake_projects[1].name),
                (self.fake_projects[0].id, self.fake_projects[0].name),
            )
        else:
            datalists = (
                (self.fake_projects[0].id, self.fake_projects[0].name),
                (self.fake_projects[1].id, self.fake_projects[1].name),
            )

        self.assertEqual(datalists, tuple(data))


class TestProjectSet(TestProject):
    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_project
        self.projects_mock.update.return_value = self.fake_project

        # Get the command object to test
        self.cmd = project.SetProject(self.app, None)

    def test_project_set_no_options(self):
        arglist = [
            self.fake_project.name,
        ]
        verifylist = [
            ('project', self.fake_project.name),
            ('enable', False),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_project_set_unexist_project(self):
        arglist = [
            "unexist-project",
        ]
        verifylist = [
            ('project', "unexist-project"),
            ('name', None),
            ('description', None),
            ('enable', False),
            ('disable', False),
            ('property', None),
        ]
        self.projects_mock.get.side_effect = exceptions.NotFound(None)
        self.projects_mock.find.side_effect = exceptions.NotFound(None)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_project_set_name(self):
        arglist = [
            '--name',
            self.fake_project.name,
            self.fake_project.name,
        ]
        verifylist = [
            ('name', self.fake_project.name),
            ('enable', False),
            ('disable', False),
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.fake_project.description,
            'enabled': True,
            'tenant_name': self.fake_project.name,
        }
        self.projects_mock.update.assert_called_with(
            self.fake_project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_description(self):
        arglist = [
            '--description',
            self.fake_project.description,
            self.fake_project.name,
        ]
        verifylist = [
            ('description', self.fake_project.description),
            ('enable', False),
            ('disable', False),
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.fake_project.description,
            'enabled': True,
            'tenant_name': self.fake_project.name,
        }
        self.projects_mock.update.assert_called_with(
            self.fake_project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_enable(self):
        arglist = [
            '--enable',
            self.fake_project.name,
        ]
        verifylist = [
            ('enable', True),
            ('disable', False),
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.fake_project.description,
            'enabled': True,
            'tenant_name': self.fake_project.name,
        }
        self.projects_mock.update.assert_called_with(
            self.fake_project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_disable(self):
        arglist = [
            '--disable',
            self.fake_project.name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', True),
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.fake_project.description,
            'enabled': False,
            'tenant_name': self.fake_project.name,
        }
        self.projects_mock.update.assert_called_with(
            self.fake_project.id, **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_property(self):
        arglist = [
            '--property',
            'fee=fi',
            '--property',
            'fo=fum',
            self.fake_project.name,
        ]
        verifylist = [
            ('property', {'fee': 'fi', 'fo': 'fum'}),
            ('project', self.fake_project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': self.fake_project.description,
            'enabled': True,
            'tenant_name': self.fake_project.name,
            'fee': 'fi',
            'fo': 'fum',
        }
        self.projects_mock.update.assert_called_with(
            self.fake_project.id, **kwargs
        )
        self.assertIsNone(result)


class TestProjectShow(TestProject):
    fake_proj_show = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_proj_show

        # Get the command object to test
        self.cmd = project.ShowProject(self.app, None)

    def test_project_show(self):
        arglist = [
            self.fake_proj_show.id,
        ]
        verifylist = [
            ('project', self.fake_proj_show.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_with(
            self.fake_proj_show.id,
        )

        collist = ('description', 'enabled', 'id', 'name', 'properties')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_proj_show.description,
            True,
            self.fake_proj_show.id,
            self.fake_proj_show.name,
            format_columns.DictColumn({}),
        )
        self.assertCountEqual(datalist, data)


class TestProjectUnset(TestProject):
    attr = {'fee': 'fi', 'fo': 'fum'}
    fake_proj = identity_fakes.FakeProject.create_one_project(attr)

    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_proj

        # Get the command object to test
        self.cmd = project.UnsetProject(self.app, None)

    def test_project_unset_no_options(self):
        arglist = [
            self.fake_proj.name,
        ]
        verifylist = [
            ('project', self.fake_proj.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_project_unset_key(self):
        arglist = [
            '--property',
            'fee',
            '--property',
            'fo',
            self.fake_proj.name,
        ]
        verifylist = [
            ('property', ['fee', 'fo']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        # Set expected values
        kwargs = {
            'description': self.fake_proj.description,
            'enabled': True,
            'fee': None,
            'fo': None,
            'id': self.fake_proj.id,
            'name': self.fake_proj.name,
        }

        self.projects_mock.update.assert_called_with(
            self.fake_proj.id, **kwargs
        )
        self.assertIsNone(result)
