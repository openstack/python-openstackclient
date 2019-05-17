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

from openstackclient.identity.v3 import endpoint_group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestEndpointGroup(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestEndpointGroup, self).setUp()

        # Get a shortcut to the EndpointManager Mock
        self.endpoint_groups_mock = (
            self.app.client_manager.identity.endpoint_groups
        )
        self.endpoint_groups_mock.reset_mock()
        self.epf_mock = (
            self.app.client_manager.identity.endpoint_filter
        )
        self.epf_mock.reset_mock()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.app.client_manager.identity.services
        self.services_mock.reset_mock()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestEndpointGroupCreate(TestEndpointGroup):

    columns = (
        'description',
        'filters',
        'id',
        'name',
    )

    def setUp(self):
        super(TestEndpointGroupCreate, self).setUp()

        self.endpoint_group = (
            identity_fakes.FakeEndpointGroup.create_one_endpointgroup(
                attrs={'filters': identity_fakes.endpoint_group_filters}))

        self.endpoint_groups_mock.create.return_value = self.endpoint_group

        # Get the command object to test
        self.cmd = endpoint_group.CreateEndpointGroup(self.app, None)

    def test_endpointgroup_create_no_options(self):
        arglist = [
            '--description', self.endpoint_group.description,
            self.endpoint_group.name,
            identity_fakes.endpoint_group_file_path,
        ]
        verifylist = [
            ('name', self.endpoint_group.name),
            ('filters', identity_fakes.endpoint_group_file_path),
            ('description', self.endpoint_group.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = identity_fakes.endpoint_group_filters
        with mock.patch("openstackclient.identity.v3.endpoint_group."
                        "CreateEndpointGroup._read_filters", mocker):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': self.endpoint_group.name,
            'filters': identity_fakes.endpoint_group_filters,
            'description': self.endpoint_group.description,
        }

        self.endpoint_groups_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            self.endpoint_group.description,
            identity_fakes.endpoint_group_filters,
            self.endpoint_group.id,
            self.endpoint_group.name,
        )
        self.assertEqual(datalist, data)


class TestEndpointGroupDelete(TestEndpointGroup):

    endpoint_group = (
        identity_fakes.FakeEndpointGroup.create_one_endpointgroup())

    def setUp(self):
        super(TestEndpointGroupDelete, self).setUp()

        # This is the return value for utils.find_resource(endpoint)
        self.endpoint_groups_mock.get.return_value = self.endpoint_group
        self.endpoint_groups_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = endpoint_group.DeleteEndpointGroup(self.app, None)

    def test_endpointgroup_delete(self):
        arglist = [
            self.endpoint_group.id,
        ]
        verifylist = [
            ('endpointgroup', [self.endpoint_group.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.endpoint_groups_mock.delete.assert_called_with(
            self.endpoint_group.id,
        )
        self.assertIsNone(result)


class TestEndpointGroupList(TestEndpointGroup):

    endpoint_group = (
        identity_fakes.FakeEndpointGroup.create_one_endpointgroup())
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()

    columns = (
        'ID',
        'Name',
        'Description',
    )

    def setUp(self):
        super(TestEndpointGroupList, self).setUp()

        self.endpoint_groups_mock.list.return_value = [self.endpoint_group]
        self.endpoint_groups_mock.get.return_value = self.endpoint_group
        self.epf_mock.list_projects_for_endpoint_group.return_value = [
            self.project]
        self.epf_mock.list_endpoint_groups_for_project.return_value = [
            self.endpoint_group]

        # Get the command object to test
        self.cmd = endpoint_group.ListEndpointGroup(self.app, None)

    def test_endpoint_group_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.endpoint_groups_mock.list.assert_called_with()

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint_group.id,
                self.endpoint_group.name,
                self.endpoint_group.description,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_group_list_projects_by_endpoint_group(self):
        arglist = [
            '--endpointgroup', self.endpoint_group.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.epf_mock.list_projects_for_endpoint_group.assert_called_with(
            endpoint_group=self.endpoint_group.id
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.project.id,
                self.project.name,
                self.project.description,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_group_list_by_project(self):
        self.epf_mock.list_endpoints_for_project.return_value = [
            self.endpoint_group
        ]
        self.projects_mock.get.return_value = self.project

        arglist = [
            '--project', self.project.name,
            '--domain', self.domain.name
        ]
        verifylist = [
            ('project', self.project.name),
            ('domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.epf_mock.list_endpoint_groups_for_project.assert_called_with(
            project=self.project.id
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint_group.id,
                self.endpoint_group.name,
                self.endpoint_group.description,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestEndpointGroupSet(TestEndpointGroup):

    endpoint_group = (
        identity_fakes.FakeEndpointGroup.create_one_endpointgroup())

    def setUp(self):
        super(TestEndpointGroupSet, self).setUp()

        # This is the return value for utils.find_resource(endpoint)
        self.endpoint_groups_mock.get.return_value = self.endpoint_group

        self.endpoint_groups_mock.update.return_value = self.endpoint_group

        # Get the command object to test
        self.cmd = endpoint_group.SetEndpointGroup(self.app, None)

    def test_endpoint_group_set_no_options(self):
        arglist = [
            self.endpoint_group.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': None,
            'filters': None,
            'description': ''
        }
        self.endpoint_groups_mock.update.assert_called_with(
            self.endpoint_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_group_set_name(self):
        arglist = [
            '--name', 'qwerty',
            self.endpoint_group.id
        ]
        verifylist = [
            ('name', 'qwerty'),
            ('endpointgroup', self.endpoint_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': 'qwerty',
            'filters': None,
            'description': ''
        }
        self.endpoint_groups_mock.update.assert_called_with(
            self.endpoint_group.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_group_set_filters(self):
        arglist = [
            '--filters', identity_fakes.endpoint_group_file_path,
            self.endpoint_group.id,
        ]
        verifylist = [
            ('filters', identity_fakes.endpoint_group_file_path),
            ('endpointgroup', self.endpoint_group.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = identity_fakes.endpoint_group_filters_2
        with mock.patch("openstackclient.identity.v3.endpoint_group."
                        "SetEndpointGroup._read_filters", mocker):
            result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': None,
            'filters': identity_fakes.endpoint_group_filters_2,
            'description': '',
        }

        self.endpoint_groups_mock.update.assert_called_with(
            self.endpoint_group.id,
            **kwargs
        )

        self.assertIsNone(result)

    def test_endpoint_group_set_description(self):
        arglist = [
            '--description', 'qwerty',
            self.endpoint_group.id
        ]
        verifylist = [
            ('description', 'qwerty'),
            ('endpointgroup', self.endpoint_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': None,
            'filters': None,
            'description': 'qwerty',
        }
        self.endpoint_groups_mock.update.assert_called_with(
            self.endpoint_group.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestAddProjectToEndpointGroup(TestEndpointGroup):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    endpoint_group = (
        identity_fakes.FakeEndpointGroup.create_one_endpointgroup())

    new_ep_filter = (
        identity_fakes.FakeEndpointGroup.create_one_endpointgroup_filter(
            attrs={'endpointgroup': endpoint_group.id,
                   'project': project.id}))

    def setUp(self):
        super(TestAddProjectToEndpointGroup, self).setUp()

        # This is the return value for utils.find_resource()
        self.endpoint_groups_mock.get.return_value = self.endpoint_group

        # Update the image_id in the MEMBER dict
        self.epf_mock.create.return_value = self.new_ep_filter
        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = endpoint_group.AddProjectToEndpointGroup(self.app, None)

    def test_add_project_to_endpoint_no_option(self):
        arglist = [
            self.endpoint_group.id,
            self.project.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.epf_mock.add_endpoint_group_to_project.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)

    def test_add_project_to_endpoint_with_option(self):
        arglist = [
            self.endpoint_group.id,
            self.project.id,
            '--project-domain', self.domain.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.epf_mock.add_endpoint_group_to_project.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)


class TestRemoveProjectEndpointGroup(TestEndpointGroup):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    endpoint_group = (
        identity_fakes.FakeEndpointGroup.create_one_endpointgroup())

    def setUp(self):
        super(TestRemoveProjectEndpointGroup, self).setUp()

        # This is the return value for utils.find_resource()
        self.endpoint_groups_mock.get.return_value = self.endpoint_group

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain
        self.epf_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = endpoint_group.RemoveProjectFromEndpointGroup(
            self.app, None)

    def test_remove_project_endpoint_no_options(self):
        arglist = [
            self.endpoint_group.id,
            self.project.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.epf_mock.delete_endpoint_group_from_project.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)

    def test_remove_project_endpoint_with_options(self):
        arglist = [
            self.endpoint_group.id,
            self.project.id,
            '--project-domain', self.domain.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.epf_mock.delete_endpoint_group_from_project.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)
