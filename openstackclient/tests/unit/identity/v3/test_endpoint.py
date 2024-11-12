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

from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import endpoint as _endpoint
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import region as _region
from openstack.identity.v3 import service as _service
from openstack.test import fakes as sdk_fakes

from openstackclient.identity.v3 import endpoint
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestEndpoint(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the EndpointManager Mock
        self.endpoints_mock = self.identity_client.endpoints
        self.endpoints_mock.reset_mock()
        self.ep_filter_mock = self.identity_client.endpoint_filter
        self.ep_filter_mock.reset_mock()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.identity_client.services
        self.services_mock.reset_mock()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()


class TestEndpointCreate(identity_fakes.TestIdentityv3):
    columns = (
        'enabled',
        'id',
        'interface',
        'region',
        'region_id',
        'service_id',
        'url',
        'service_name',
        'service_type',
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

        self.identity_sdk_client.create_endpoint.return_value = self.endpoint
        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)

    def test_endpoint_create_no_options(self):
        arglist = [
            self.service.id,
            self.endpoint.interface,
            self.endpoint.url,
        ]
        verifylist = [
            ('enabled', True),
            ('service', self.service.id),
            ('interface', self.endpoint.interface),
            ('url', self.endpoint.url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake endpoints come with a region ID by default, so set it to None
        setattr(self.endpoint, "region_id", None)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service_id': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_endpoint.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            None,
            None,
            self.service.id,
            self.endpoint.url,
            self.service.name,
            self.service.type,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_region(self):
        arglist = [
            self.service.id,
            self.endpoint.interface,
            self.endpoint.url,
            '--region',
            self.region.id,
        ]
        verifylist = [
            ('enabled', True),
            ('service', self.service.id),
            ('interface', self.endpoint.interface),
            ('url', self.endpoint.url),
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service_id': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'is_enabled': True,
            'region_id': self.region.id,
        }

        self.identity_sdk_client.create_endpoint.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.region.id,
            self.region.id,
            self.service.id,
            self.endpoint.url,
            self.service.name,
            self.service.type,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_enable(self):
        arglist = [
            self.service.id,
            self.endpoint.interface,
            self.endpoint.url,
            '--enable',
        ]
        verifylist = [
            ('enabled', True),
            ('service', self.service.id),
            ('interface', self.endpoint.interface),
            ('url', self.endpoint.url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake endpoints come with a region ID by default, so set it to None
        setattr(self.endpoint, "region_id", None)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service_id': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'is_enabled': True,
        }

        self.identity_sdk_client.create_endpoint.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            None,
            None,
            self.service.id,
            self.endpoint.url,
            self.service.name,
            self.service.type,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_disable(self):
        arglist = [
            self.service.id,
            self.endpoint.interface,
            self.endpoint.url,
            '--disable',
        ]
        verifylist = [
            ('enabled', False),
            ('service', self.service.id),
            ('interface', self.endpoint.interface),
            ('url', self.endpoint.url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake endpoints come with a region ID by default, so set it to None
        setattr(self.endpoint, "region_id", None)
        setattr(self.endpoint, "is_enabled", False)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service_id': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'is_enabled': False,
        }

        self.identity_sdk_client.create_endpoint.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            False,
            self.endpoint.id,
            self.endpoint.interface,
            None,
            None,
            self.service.id,
            self.endpoint.url,
            self.service.name,
            self.service.type,
        )
        self.assertEqual(datalist, data)


class TestEndpointDelete(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.endpoint = sdk_fakes.generate_fake_resource(_endpoint.Endpoint)

        self.identity_sdk_client.find_endpoint.return_value = self.endpoint
        self.identity_sdk_client.delete_endpoint.return_value = None

        # Get the command object to test
        self.cmd = endpoint.DeleteEndpoint(self.app, None)

    def test_endpoint_delete(self):
        arglist = [
            self.endpoint.id,
        ]
        verifylist = [
            ('endpoint', [self.endpoint.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.delete_endpoint.assert_called_with(
            self.endpoint.id,
        )
        self.assertIsNone(result)


class TestEndpointList(identity_fakes.TestIdentityv3):
    columns = (
        'ID',
        'Region',
        'Service Name',
        'Service Type',
        'Enabled',
        'Interface',
        'URL',
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

        self.identity_sdk_client.endpoints.return_value = [self.endpoint]
        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.services.return_value = [self.service]
        self.identity_sdk_client.get_region.return_value = self.region

        # Get the command object to test
        self.cmd = endpoint.ListEndpoint(self.app, None)

    def test_endpoint_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.endpoints.assert_called_with()

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.region.id,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_service(self):
        arglist = [
            '--service',
            self.service.id,
        ]
        verifylist = [
            ('service', self.service.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service_id': self.service.id,
        }
        self.identity_sdk_client.endpoints.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.region.id,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_interface(self):
        arglist = [
            '--interface',
            self.endpoint.interface,
        ]
        verifylist = [
            ('interface', self.endpoint.interface),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'interface': self.endpoint.interface,
        }
        self.identity_sdk_client.endpoints.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.region.id,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_region(self):
        arglist = [
            '--region',
            self.region.id,
        ]
        verifylist = [
            ('region', self.region.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'region_id': self.region.id,
        }
        self.identity_sdk_client.endpoints.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.region.id,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_project_with_project_domain(self):
        project = sdk_fakes.generate_fake_resource(_project.Project)
        domain = sdk_fakes.generate_fake_resource(_domain.Domain)

        self.identity_sdk_client.project_endpoints.return_value = [
            self.endpoint
        ]
        self.identity_sdk_client.find_project.return_value = project

        arglist = ['--project', project.name, '--project-domain', domain.name]
        verifylist = [
            ('project', project.name),
            ('project_domain', domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.project_endpoints.assert_called_with(
            project=project.id
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.region.id,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestEndpointSet(identity_fakes.TestIdentityv3):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.endpoint = sdk_fakes.generate_fake_resource(
            resource_type=_endpoint.Endpoint,
            service_id=self.service.id,
            interface='admin',
        )

        self.identity_sdk_client.find_endpoint.return_value = self.endpoint
        self.identity_sdk_client.update_endpoint.return_value = self.endpoint
        self.identity_sdk_client.find_service.return_value = self.service

        # Get the command object to test
        self.cmd = endpoint.SetEndpoint(self.app, None)

    def test_endpoint_set_no_options(self):
        arglist = [
            self.endpoint.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id
        )
        self.assertIsNone(result)

    def test_endpoint_set_interface(self):
        arglist = ['--interface', 'public', self.endpoint.id]
        verifylist = [
            ('interface', 'public'),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'interface': 'public',
        }
        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_url(self):
        arglist = ['--url', 'http://localhost:5000', self.endpoint.id]
        verifylist = [
            ('url', 'http://localhost:5000'),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'url': 'http://localhost:5000',
        }
        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_service(self):
        arglist = ['--service', self.service.id, self.endpoint.id]
        verifylist = [
            ('service', self.service.id),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service_id': self.service.id,
        }
        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_region(self):
        arglist = ['--region', 'e-rzzz', self.endpoint.id]
        verifylist = [
            ('region', 'e-rzzz'),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'region_id': 'e-rzzz',
        }
        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_enable(self):
        arglist = ['--enable', self.endpoint.id]
        verifylist = [
            ('enabled', True),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': True,
        }
        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id, **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_disable(self):
        arglist = ['--disable', self.endpoint.id]
        verifylist = [
            ('disabled', True),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_enabled': False,
        }
        self.identity_sdk_client.update_endpoint.assert_called_with(
            self.endpoint.id, **kwargs
        )
        self.assertIsNone(result)


class TestEndpointShow(identity_fakes.TestIdentityv3):
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

        self.identity_sdk_client.find_endpoint.return_value = self.endpoint

        self.identity_sdk_client.find_service.return_value = self.service
        self.identity_sdk_client.get_region.return_value = self.region

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)

    def test_endpoint_show(self):
        arglist = [
            self.endpoint.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)
        self.identity_sdk_client.find_endpoint.assert_called_with(
            self.endpoint.id,
        )

        collist = (
            'enabled',
            'id',
            'interface',
            'region',
            'region_id',
            'service_id',
            'url',
            'service_name',
            'service_type',
        )
        self.assertEqual(collist, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.region.id,
            self.region.id,
            self.service.id,
            self.endpoint.url,
            self.service.name,
            self.service.type,
        )
        self.assertEqual(datalist, data)


class TestEndpointCreateServiceWithoutName(TestEndpointCreate):
    service = sdk_fakes.generate_fake_resource(
        resource_type=_service.Service,
        name='',
    )
    region = sdk_fakes.generate_fake_resource(_region.Region)
    endpoint = sdk_fakes.generate_fake_resource(
        resource_type=_endpoint.Endpoint,
        service_id=service.id,
        interface='admin',
        region_id=region.id,
    )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)


class TestEndpointListServiceWithoutName(TestEndpointList):
    service = sdk_fakes.generate_fake_resource(
        resource_type=_service.Service,
        name='',
    )
    region = sdk_fakes.generate_fake_resource(_region.Region)
    endpoint = sdk_fakes.generate_fake_resource(
        resource_type=_endpoint.Endpoint,
        service_id=service.id,
        interface='admin',
        region_id=region.id,
    )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = endpoint.ListEndpoint(self.app, None)


class TestEndpointShowServiceWithoutName(TestEndpointShow):
    service = sdk_fakes.generate_fake_resource(
        resource_type=_service.Service,
        name='',
    )
    region = sdk_fakes.generate_fake_resource(_region.Region)
    endpoint = sdk_fakes.generate_fake_resource(
        resource_type=_endpoint.Endpoint,
        service_id=service.id,
        interface='admin',
        region_id=region.id,
    )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)


class TestAddProjectToEndpoint(TestEndpoint):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id}
    )

    new_ep_filter = identity_fakes.FakeEndpoint.create_one_endpoint_filter(
        attrs={'endpoint': endpoint.id, 'project': project.id}
    )

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.endpoints_mock.get.return_value = self.endpoint

        # Update the image_id in the MEMBER dict
        self.ep_filter_mock.create.return_value = self.new_ep_filter
        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain
        # Get the command object to test
        self.cmd = endpoint.AddProjectToEndpoint(self.app, None)

    def test_add_project_to_endpoint_no_option(self):
        arglist = [
            self.endpoint.id,
            self.project.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.ep_filter_mock.add_endpoint_to_project.assert_called_with(
            project=self.project.id, endpoint=self.endpoint.id
        )
        self.assertIsNone(result)

    def test_add_project_to_endpoint_with_option(self):
        arglist = [
            self.endpoint.id,
            self.project.id,
            '--project-domain',
            self.domain.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.ep_filter_mock.add_endpoint_to_project.assert_called_with(
            project=self.project.id, endpoint=self.endpoint.id
        )
        self.assertIsNone(result)


class TestRemoveProjectEndpoint(TestEndpoint):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id}
    )

    def setUp(self):
        super().setUp()

        # This is the return value for utils.find_resource()
        self.endpoints_mock.get.return_value = self.endpoint

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain
        self.ep_filter_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = endpoint.RemoveProjectFromEndpoint(self.app, None)

    def test_remove_project_endpoint_no_options(self):
        arglist = [
            self.endpoint.id,
            self.project.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.ep_filter_mock.delete_endpoint_from_project.assert_called_with(
            project=self.project.id,
            endpoint=self.endpoint.id,
        )
        self.assertIsNone(result)

    def test_remove_project_endpoint_with_options(self):
        arglist = [
            self.endpoint.id,
            self.project.id,
            '--project-domain',
            self.domain.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.ep_filter_mock.delete_endpoint_from_project.assert_called_with(
            project=self.project.id,
            endpoint=self.endpoint.id,
        )
        self.assertIsNone(result)
