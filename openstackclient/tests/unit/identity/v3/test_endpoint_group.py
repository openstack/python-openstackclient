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

from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import endpoint as _endpoint
from openstack.identity.v3 import endpoint_group as _endpoint_group
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import region as _region
from openstack.identity.v3 import service as _service
from openstack.test import fakes as sdk_fakes

from openstackclient.identity.v3 import endpoint_group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestEndpointGroupCreate(identity_fakes.TestIdentity):
    endpoint_group_file_path = '/tmp/path/to/file'

    columns = (
        'description',
        'filters',
        'id',
        'name',
    )

    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.endpoint = sdk_fakes.generate_fake_resource(
            resource_type=_endpoint.Endpoint,
            service_id=self.service.id,
            interface='admin',
            region_id=self.region.id,
        )
        self.endpoint_group_filters = {
            'service_id': self.service.id,
            'region_id': self.region.id,
        }

        # Get the command object to test
        self.cmd = endpoint_group.CreateEndpointGroup(self.app, None)

    def test_endpointgroup_create_no_options(self):
        endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup, filters=self.endpoint_group_filters
        )

        self.identity_sdk_client.create_endpoint_group.return_value = (
            endpoint_group
        )

        arglist = [
            '--description',
            endpoint_group.description,
            endpoint_group.name,
            self.endpoint_group_file_path,
        ]
        verifylist = [
            ('name', endpoint_group.name),
            ('filters', self.endpoint_group_file_path),
            ('description', endpoint_group.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = self.endpoint_group_filters
        with mock.patch(
            "openstackclient.identity.v3.endpoint_group."
            "CreateEndpointGroup._read_filters",
            mocker,
        ):
            columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': endpoint_group.name,
            'filters': self.endpoint_group_filters,
            'description': endpoint_group.description,
        }

        self.identity_sdk_client.create_endpoint_group.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            endpoint_group.description,
            self.endpoint_group_filters,
            endpoint_group.id,
            endpoint_group.name,
        )
        self.assertEqual(datalist, data)


class TestEndpointGroupDelete(identity_fakes.TestIdentity):
    def setUp(self):
        super().setUp()

        self.endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup
        )

        self.identity_sdk_client.find_endpoint_group.return_value = (
            self.endpoint_group
        )
        self.identity_sdk_client.delete_endpoint_group.return_value = None

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

        self.identity_sdk_client.delete_endpoint_group.assert_called_with(
            self.endpoint_group.id,
        )
        self.assertIsNone(result)


class TestEndpointGroupList(identity_fakes.TestIdentity):
    columns = (
        'ID',
        'Name',
        'Description',
    )

    def setUp(self):
        super().setUp()

        self.endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup
        )
        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)

        self.identity_sdk_client.endpoint_groups.return_value = [
            self.endpoint_group
        ]
        self.identity_sdk_client.find_endpoint_group.return_value = (
            self.endpoint_group
        )
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.endpoint_group_projects.return_value = [
            self.project
        ]
        self.identity_sdk_client.project_endpoint_groups.return_value = [
            self.endpoint_group
        ]

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
        self.identity_sdk_client.endpoint_groups.assert_called_with()

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
            '--endpointgroup',
            self.endpoint_group.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.endpoint_group_projects.assert_called_with(
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
        arglist = [
            '--project',
            self.project.name,
            '--domain',
            self.domain.name,
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
        self.identity_sdk_client.project_endpoint_groups.assert_called_with(
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


class TestEndpointGroupSet(identity_fakes.TestIdentity):
    endpoint_group_file_path = '/tmp/path/to/file'

    def setUp(self):
        super().setUp()

        self.region = sdk_fakes.generate_fake_resource(_region.Region)
        self.endpoint_group_filters_2 = {
            'region_id': self.region.id,
        }

        self.endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup
        )
        self.endpoint_group_2 = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup,
            filters=self.endpoint_group_filters_2,
        )

        self.identity_sdk_client.find_endpoint_group.return_value = (
            self.endpoint_group
        )
        self.identity_sdk_client.update_endpoint_group.return_value = (
            self.endpoint_group_2
        )

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

        kwargs = {'name': None, 'filters': None, 'description': ''}
        self.identity_sdk_client.update_endpoint_group.assert_called_with(
            self.endpoint_group.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_group_set_name(self):
        arglist = ['--name', 'qwerty', self.endpoint_group.id]
        verifylist = [
            ('name', 'qwerty'),
            ('endpointgroup', self.endpoint_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {'name': 'qwerty', 'filters': None, 'description': ''}
        self.identity_sdk_client.update_endpoint_group.assert_called_with(
            self.endpoint_group.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_group_set_filters(self):
        arglist = [
            '--filters',
            self.endpoint_group_file_path,
            self.endpoint_group.id,
        ]
        verifylist = [
            ('filters', self.endpoint_group_file_path),
            ('endpointgroup', self.endpoint_group.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        mocker = mock.Mock()
        mocker.return_value = self.endpoint_group_filters_2
        with mock.patch(
            "openstackclient.identity.v3.endpoint_group."
            "SetEndpointGroup._read_filters",
            mocker,
        ):
            result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': None,
            'filters': self.endpoint_group_filters_2,
            'description': '',
        }

        self.identity_sdk_client.update_endpoint_group.assert_called_with(
            self.endpoint_group.id, **kwargs
        )

        self.assertIsNone(result)

    def test_endpoint_group_set_description(self):
        arglist = ['--description', 'qwerty', self.endpoint_group.id]
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
        self.identity_sdk_client.update_endpoint_group.assert_called_with(
            self.endpoint_group.id, **kwargs
        )
        self.assertIsNone(result)


class TestAddProjectToEndpointGroup(identity_fakes.TestIdentity):
    def setUp(self):
        super().setUp()

        self.endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup
        )
        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)

        self.project_endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.ProjectEndpointGroup
        )

        self.identity_sdk_client.find_endpoint_group.return_value = (
            self.endpoint_group
        )
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.associate_project_with_endpoint_group.return_value = self.project_endpoint_group

        # Get the command object to test
        self.cmd = endpoint_group.AddProjectToEndpointGroup(self.app, None)

    def test_add_project_to_endpoint_group_no_option(self):
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
        self.identity_sdk_client.associate_project_with_endpoint_group.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)

    def test_add_project_to_endpoint_group_with_option(self):
        arglist = [
            self.endpoint_group.id,
            self.project.id,
            '--project-domain',
            self.domain.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.associate_project_with_endpoint_group.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)


class TestRemoveProjectEndpointGroup(identity_fakes.TestIdentity):
    def setUp(self):
        super().setUp()

        self.endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.EndpointGroup
        )
        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.domain = sdk_fakes.generate_fake_resource(_domain.Domain)

        self.project_endpoint_group = sdk_fakes.generate_fake_resource(
            _endpoint_group.ProjectEndpointGroup
        )

        self.identity_sdk_client.find_endpoint_group.return_value = (
            self.endpoint_group
        )
        self.identity_sdk_client.find_project.return_value = self.project
        self.identity_sdk_client.find_domain.return_value = self.domain
        self.identity_sdk_client.disassociate_project_from_endpoint_group.return_value = self.project_endpoint_group

        # Get the command object to test
        self.cmd = endpoint_group.RemoveProjectFromEndpointGroup(
            self.app, None
        )

    def test_remove_project_endpoint_group_no_options(self):
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

        self.identity_sdk_client.disassociate_project_from_endpoint_group.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)

    def test_remove_project_endpoint_group_with_options(self):
        arglist = [
            self.endpoint_group.id,
            self.project.id,
            '--project-domain',
            self.domain.id,
        ]
        verifylist = [
            ('endpointgroup', self.endpoint_group.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.disassociate_project_from_endpoint_group.assert_called_with(
            project=self.project.id,
            endpoint_group=self.endpoint_group.id,
        )
        self.assertIsNone(result)
