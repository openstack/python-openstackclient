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

import mock

from osc_lib import exceptions

from openstackclient.identity.v3 import project
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestProject(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestProject, self).setUp()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestProjectCreate(TestProject):

    domain = identity_fakes.FakeDomain.create_one_domain()

    columns = (
        'description',
        'domain_id',
        'enabled',
        'id',
        'is_domain',
        'name',
        'parent_id',
    )

    def setUp(self):
        super(TestProjectCreate, self).setUp()

        self.project = identity_fakes.FakeProject.create_one_project(
            attrs={'domain_id': self.domain.id})
        self.domains_mock.get.return_value = self.domain
        self.projects_mock.create.return_value = self.project
        self.datalist = (
            self.project.description,
            self.project.domain_id,
            True,
            self.project.id,
            False,
            self.project.name,
            self.project.parent_id,
        )
        # Get the command object to test
        self.cmd = project.CreateProject(self.app, None)

    def test_project_create_no_options(self):
        arglist = [
            self.project.name,
        ]
        verifylist = [
            ('parent', None),
            ('enable', False),
            ('disable', False),
            ('name', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': None,
            'description': None,
            'enabled': True,
            'parent': None,
        }
        # ProjectManager.create(name=, domain=, description=,
        #                       enabled=, **kwargs)
        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'parent_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.project.description,
            self.project.domain_id,
            True,
            self.project.id,
            False,
            self.project.name,
            self.project.parent_id,
        )
        self.assertEqual(datalist, data)

    def test_project_create_description(self):
        arglist = [
            '--description', 'new desc',
            self.project.name,
        ]
        verifylist = [
            ('description', 'new desc'),
            ('enable', False),
            ('disable', False),
            ('name', self.project.name),
            ('parent', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': None,
            'description': 'new desc',
            'enabled': True,
            'parent': None,
        }
        # ProjectManager.create(name=, domain=, description=,
        #                       enabled=, **kwargs)
        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_domain(self):
        arglist = [
            '--domain', self.project.domain_id,
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('enable', False),
            ('disable', False),
            ('name', self.project.name),
            ('parent', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': self.project.domain_id,
            'description': None,
            'enabled': True,
            'parent': None,
        }
        # ProjectManager.create(name=, domain=, description=,
        #                       enabled=, **kwargs)
        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_domain_no_perms(self):
        arglist = [
            '--domain', self.project.domain_id,
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('enable', False),
            ('disable', False),
            ('name', self.project.name),
            ('parent', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        mocker = mock.Mock()
        mocker.return_value = None

        with mock.patch("osc_lib.utils.find_resource", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': self.project.domain_id,
            'description': None,
            'enabled': True,
            'parent': None,
        }
        self.projects_mock.create.assert_called_with(
            **kwargs
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_enable(self):
        arglist = [
            '--enable',
            self.project.name,
        ]
        verifylist = [
            ('enable', True),
            ('disable', False),
            ('name', self.project.name),
            ('parent', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': None,
            'description': None,
            'enabled': True,
            'parent': None,
        }
        # ProjectManager.create(name=, domain=, description=,
        #                       enabled=, **kwargs)
        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_disable(self):
        arglist = [
            '--disable',
            self.project.name,
        ]
        verifylist = [
            ('enable', False),
            ('disable', True),
            ('name', self.project.name),
            ('parent', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': None,
            'description': None,
            'enabled': False,
            'parent': None,
        }
        # ProjectManager.create(name=, domain=,
        #                       description=, enabled=, **kwargs)
        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_property(self):
        arglist = [
            '--property', 'fee=fi',
            '--property', 'fo=fum',
            self.project.name,
        ]
        verifylist = [
            ('property', {'fee': 'fi', 'fo': 'fum'}),
            ('name', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.project.name,
            'domain': None,
            'description': None,
            'enabled': True,
            'parent': None,
            'fee': 'fi',
            'fo': 'fum',
        }
        # ProjectManager.create(name=, domain=, description=,
        #                       enabled=, **kwargs)
        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_project_create_parent(self):
        self.parent = identity_fakes.FakeProject.create_one_project()
        self.project = identity_fakes.FakeProject.create_one_project(
            attrs={'domain_id': self.domain.id, 'parent_id': self.parent.id})
        self.projects_mock.get.return_value = self.parent
        self.projects_mock.create.return_value = self.project

        arglist = [
            '--domain', self.project.domain_id,
            '--parent', self.parent.name,
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('parent', self.parent.name),
            ('enable', False),
            ('disable', False),
            ('name', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': self.project.name,
            'domain': self.project.domain_id,
            'parent': self.parent.id,
            'description': None,
            'enabled': True,
        }

        self.projects_mock.create.assert_called_with(
            **kwargs
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'parent_id',
        )
        self.assertEqual(columns, collist)
        datalist = (
            self.project.description,
            self.project.domain_id,
            self.project.enabled,
            self.project.id,
            self.project.is_domain,
            self.project.name,
            self.parent.id,
        )
        self.assertEqual(data, datalist)

    def test_project_create_invalid_parent(self):
        self.projects_mock.resource_class.__name__ = 'Project'
        self.projects_mock.get.side_effect = exceptions.NotFound(
            'Invalid parent')
        self.projects_mock.find.side_effect = exceptions.NotFound(
            'Invalid parent')

        arglist = [
            '--domain', self.project.domain_id,
            '--parent', 'invalid',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('parent', 'invalid'),
            ('enable', False),
            ('disable', False),
            ('name', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestProjectDelete(TestProject):

    project = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super(TestProjectDelete, self).setUp()

        # This is the return value for utils.find_resource()
        self.projects_mock.get.return_value = self.project
        self.projects_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = project.DeleteProject(self.app, None)

    def test_project_delete_no_options(self):
        arglist = [
            self.project.id,
        ]
        verifylist = [
            ('projects', [self.project.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.projects_mock.delete.assert_called_with(
            self.project.id,
        )
        self.assertIsNone(result)


class TestProjectList(TestProject):

    domain = identity_fakes.FakeDomain.create_one_domain()
    project = identity_fakes.FakeProject.create_one_project(
        attrs={'domain_id': domain.id})

    columns = (
        'ID',
        'Name',
    )
    datalist = (
        (
            project.id,
            project.name,
        ),
    )

    def setUp(self):
        super(TestProjectList, self).setUp()

        self.projects_mock.list.return_value = [self.project]

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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

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

        collist = ('ID', 'Name', 'Domain ID', 'Description', 'Enabled')
        self.assertEqual(collist, columns)
        datalist = ((
            self.project.id,
            self.project.name,
            self.project.domain_id,
            self.project.description,
            True,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_project_list_domain(self):
        arglist = [
            '--domain', self.project.domain_id,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
        ]

        self.domains_mock.get.return_value = self.domain

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.list.assert_called_with(
            domain=self.project.domain_id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_project_list_domain_no_perms(self):
        arglist = [
            '--domain', self.project.domain_id,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        mocker = mock.Mock()
        mocker.return_value = None

        with mock.patch("osc_lib.utils.find_resource", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        self.projects_mock.list.assert_called_with(
            domain=self.project.domain_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))


class TestProjectSet(TestProject):

    domain = identity_fakes.FakeDomain.create_one_domain()
    project = identity_fakes.FakeProject.create_one_project(
        attrs={'domain_id': domain.id})

    def setUp(self):
        super(TestProjectSet, self).setUp()

        self.domains_mock.get.return_value = self.domain

        self.projects_mock.get.return_value = self.project
        self.projects_mock.update.return_value = self.project

        # Get the command object to test
        self.cmd = project.SetProject(self.app, None)

    def test_project_set_no_options(self):
        arglist = [
            self.project.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('enable', False),
            ('disable', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_project_set_name(self):
        arglist = [
            '--name', 'qwerty',
            '--domain', self.project.domain_id,
            self.project.name,
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('domain', self.project.domain_id),
            ('enable', False),
            ('disable', False),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'qwerty',
        }
        # ProjectManager.update(project, name=, domain=, description=,
        #                       enabled=, **kwargs)
        self.projects_mock.update.assert_called_with(
            self.project.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_description(self):
        arglist = [
            '--domain', self.project.domain_id,
            '--description', 'new desc',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('description', 'new desc'),
            ('enable', False),
            ('disable', False),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': 'new desc',
        }
        self.projects_mock.update.assert_called_with(
            self.project.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_enable(self):
        arglist = [
            '--domain', self.project.domain_id,
            '--enable',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('enable', True),
            ('disable', False),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
        }
        self.projects_mock.update.assert_called_with(
            self.project.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_disable(self):
        arglist = [
            '--domain', self.project.domain_id,
            '--disable',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('enable', False),
            ('disable', True),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
        }
        self.projects_mock.update.assert_called_with(
            self.project.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_project_set_property(self):
        arglist = [
            '--domain', self.project.domain_id,
            '--property', 'fee=fi',
            '--property', 'fo=fum',
            self.project.name,
        ]
        verifylist = [
            ('domain', self.project.domain_id),
            ('property', {'fee': 'fi', 'fo': 'fum'}),
            ('project', self.project.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'fee': 'fi',
            'fo': 'fum',
        }
        self.projects_mock.update.assert_called_with(
            self.project.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestProjectShow(TestProject):

    domain = identity_fakes.FakeDomain.create_one_domain()

    def setUp(self):
        super(TestProjectShow, self).setUp()

        self.project = identity_fakes.FakeProject.create_one_project(
            attrs={'domain_id': self.domain.id})

        # Get the command object to test
        self.cmd = project.ShowProject(self.app, None)

    def test_project_show(self):

        self.projects_mock.get.side_effect = [Exception("Not found"),
                                              self.project]
        self.projects_mock.get.return_value = self.project

        arglist = [
            self.project.id,
        ]
        verifylist = [
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.identity.tokens.get_token_data.return_value = \
            {'token':
             {'project':
              {'domain': {},
               'name': parsed_args.project,
               'id': parsed_args.project
               }
              }
             }

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.projects_mock.get.assert_called_with(
            self.project.id,
            parents_as_list=False,
            subtree_as_list=False,
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'parent_id',
        )
        self.assertEqual(collist, columns)
        datalist = (
            self.project.description,
            self.project.domain_id,
            True,
            self.project.id,
            False,
            self.project.name,
            self.project.parent_id,
        )
        self.assertEqual(datalist, data)

    def test_project_show_parents(self):
        self.project = identity_fakes.FakeProject.create_one_project(
            attrs={
                'parent_id': self.project.parent_id,
                'parents': [{'project': {'id': self.project.parent_id}}]
            }
        )
        self.projects_mock.get.side_effect = [Exception("Not found"),
                                              self.project]
        self.projects_mock.get.return_value = self.project

        arglist = [
            self.project.id,
            '--parents',
        ]
        verifylist = [
            ('project', self.project.id),
            ('parents', True),
            ('children', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.identity.tokens.get_token_data.return_value = \
            {'token':
             {'project':
              {'domain': {},
               'name': parsed_args.project,
               'id': parsed_args.project
               }
              }
             }

        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_with(
            self.project.id,
            parents_as_list=True,
            subtree_as_list=False,
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'parent_id',
            'parents',
        )
        self.assertEqual(columns, collist)
        datalist = (
            self.project.description,
            self.project.domain_id,
            self.project.enabled,
            self.project.id,
            self.project.is_domain,
            self.project.name,
            self.project.parent_id,
            [self.project.parent_id],
        )
        self.assertEqual(data, datalist)

    def test_project_show_subtree(self):
        self.project = identity_fakes.FakeProject.create_one_project(
            attrs={
                'parent_id': self.project.parent_id,
                'subtree': [{'project': {'id': 'children-id'}}]
            }
        )
        self.projects_mock.get.side_effect = [Exception("Not found"),
                                              self.project]
        self.projects_mock.get.return_value = self.project

        arglist = [
            self.project.id,
            '--children',
        ]
        verifylist = [
            ('project', self.project.id),
            ('parents', False),
            ('children', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.identity.tokens.get_token_data.return_value = \
            {'token':
             {'project':
              {'domain': {},
               'name': parsed_args.project,
               'id': parsed_args.project
               }
              }
             }

        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_with(
            self.project.id,
            parents_as_list=False,
            subtree_as_list=True,
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'parent_id',
            'subtree',
        )
        self.assertEqual(columns, collist)
        datalist = (
            self.project.description,
            self.project.domain_id,
            self.project.enabled,
            self.project.id,
            self.project.is_domain,
            self.project.name,
            self.project.parent_id,
            ['children-id'],
        )
        self.assertEqual(data, datalist)

    def test_project_show_parents_and_children(self):
        self.project = identity_fakes.FakeProject.create_one_project(
            attrs={
                'parent_id': self.project.parent_id,
                'parents': [{'project': {'id': self.project.parent_id}}],
                'subtree': [{'project': {'id': 'children-id'}}]
            }
        )
        self.projects_mock.get.side_effect = [Exception("Not found"),
                                              self.project]
        self.projects_mock.get.return_value = self.project

        arglist = [
            self.project.id,
            '--parents',
            '--children',
        ]
        verifylist = [
            ('project', self.project.id),
            ('parents', True),
            ('children', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.identity.tokens.get_token_data.return_value = \
            {'token':
             {'project':
              {'domain': {},
               'name': parsed_args.project,
               'id': parsed_args.project
               }
              }
             }

        columns, data = self.cmd.take_action(parsed_args)
        self.projects_mock.get.assert_called_with(
            self.project.id,
            parents_as_list=True,
            subtree_as_list=True,
        )

        collist = (
            'description',
            'domain_id',
            'enabled',
            'id',
            'is_domain',
            'name',
            'parent_id',
            'parents',
            'subtree',
        )
        self.assertEqual(columns, collist)
        datalist = (
            self.project.description,
            self.project.domain_id,
            self.project.enabled,
            self.project.id,
            self.project.is_domain,
            self.project.name,
            self.project.parent_id,
            [self.project.parent_id],
            ['children-id'],
        )
        self.assertEqual(data, datalist)
