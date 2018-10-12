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

from openstackclient.identity.v3 import endpoint
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestEndpoint(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestEndpoint, self).setUp()

        # Get a shortcut to the EndpointManager Mock
        self.endpoints_mock = self.app.client_manager.identity.endpoints
        self.endpoints_mock.reset_mock()
        self.ep_filter_mock = (
            self.app.client_manager.identity.endpoint_filter
        )
        self.ep_filter_mock.reset_mock()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.app.client_manager.identity.services
        self.services_mock.reset_mock()

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains
        self.domains_mock.reset_mock()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestEndpointCreate(TestEndpoint):

    service = identity_fakes.FakeService.create_one_service()

    columns = (
        'enabled',
        'id',
        'interface',
        'region',
        'service_id',
        'service_name',
        'service_type',
        'url',
    )

    def setUp(self):
        super(TestEndpointCreate, self).setUp()

        self.endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
            attrs={'service_id': self.service.id})
        self.endpoints_mock.create.return_value = self.endpoint

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service

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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'enabled': True,
            'region': None,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.endpoint.region,
            self.service.id,
            self.service.name,
            self.service.type,
            self.endpoint.url,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_region(self):
        arglist = [
            self.service.id,
            self.endpoint.interface,
            self.endpoint.url,
            '--region', self.endpoint.region,
        ]
        verifylist = [
            ('enabled', True),
            ('service', self.service.id),
            ('interface', self.endpoint.interface),
            ('url', self.endpoint.url),
            ('region', self.endpoint.region),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'enabled': True,
            'region': self.endpoint.region,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.endpoint.region,
            self.service.id,
            self.service.name,
            self.service.type,
            self.endpoint.url,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_enable(self):
        arglist = [
            self.service.id,
            self.endpoint.interface,
            self.endpoint.url,
            '--enable'
        ]
        verifylist = [
            ('enabled', True),
            ('service', self.service.id),
            ('interface', self.endpoint.interface),
            ('url', self.endpoint.url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'enabled': True,
            'region': None,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.endpoint.region,
            self.service.id,
            self.service.name,
            self.service.type,
            self.endpoint.url,
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

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': self.service.id,
            'url': self.endpoint.url,
            'interface': self.endpoint.interface,
            'enabled': False,
            'region': None,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.endpoint.region,
            self.service.id,
            self.service.name,
            self.service.type,
            self.endpoint.url,
        )
        self.assertEqual(datalist, data)


class TestEndpointDelete(TestEndpoint):

    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint()

    def setUp(self):
        super(TestEndpointDelete, self).setUp()

        # This is the return value for utils.find_resource(endpoint)
        self.endpoints_mock.get.return_value = self.endpoint
        self.endpoints_mock.delete.return_value = None

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

        self.endpoints_mock.delete.assert_called_with(
            self.endpoint.id,
        )
        self.assertIsNone(result)


class TestEndpointList(TestEndpoint):

    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

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
        super(TestEndpointList, self).setUp()

        self.endpoints_mock.list.return_value = [self.endpoint]

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service
        self.services_mock.list.return_value = [self.service]

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
        self.endpoints_mock.list.assert_called_with()

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.endpoint.region,
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
            '--service', self.service.id,
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
            'service': self.service.id,
        }
        self.endpoints_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.endpoint.region,
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
            '--interface', self.endpoint.interface,
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
        self.endpoints_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.endpoint.region,
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
            '--region', self.endpoint.region,
        ]
        verifylist = [
            ('region', self.endpoint.region),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'region': self.endpoint.region,
        }
        self.endpoints_mock.list.assert_called_with(**kwargs)

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.endpoint.region,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_project_with_project_domain(self):
        project = identity_fakes.FakeProject.create_one_project()
        domain = identity_fakes.FakeDomain.create_one_domain()

        self.ep_filter_mock.list_endpoints_for_project.return_value = [
            self.endpoint
        ]
        self.projects_mock.get.return_value = project

        arglist = [
            '--project', project.name,
            '--project-domain', domain.name
        ]
        verifylist = [
            ('project', project.name),
            ('project_domain', domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)
        self.ep_filter_mock.list_endpoints_for_project.assert_called_with(
            project=project.id
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (
                self.endpoint.id,
                self.endpoint.region,
                self.service.name,
                self.service.type,
                True,
                self.endpoint.interface,
                self.endpoint.url,
            ),
        )
        self.assertEqual(datalist, tuple(data))


class TestEndpointSet(TestEndpoint):

    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

    def setUp(self):
        super(TestEndpointSet, self).setUp()

        # This is the return value for utils.find_resource(endpoint)
        self.endpoints_mock.get.return_value = self.endpoint

        self.endpoints_mock.update.return_value = self.endpoint

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service

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

        kwargs = {
            'enabled': None,
            'interface': None,
            'region': None,
            'service': None,
            'url': None,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_interface(self):
        arglist = [
            '--interface', 'public',
            self.endpoint.id
        ]
        verifylist = [
            ('interface', 'public'),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': 'public',
            'url': None,
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_url(self):
        arglist = [
            '--url', 'http://localhost:5000',
            self.endpoint.id
        ]
        verifylist = [
            ('url', 'http://localhost:5000'),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': None,
            'url': 'http://localhost:5000',
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_service(self):
        arglist = [
            '--service', self.service.id,
            self.endpoint.id
        ]
        verifylist = [
            ('service', self.service.id),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': None,
            'url': None,
            'region': None,
            'service': self.service.id,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_region(self):
        arglist = [
            '--region', 'e-rzzz',
            self.endpoint.id
        ]
        verifylist = [
            ('region', 'e-rzzz'),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': None,
            'url': None,
            'region': 'e-rzzz',
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_enable(self):
        arglist = [
            '--enable',
            self.endpoint.id
        ]
        verifylist = [
            ('enabled', True),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': True,
            'interface': None,
            'url': None,
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_endpoint_set_disable(self):
        arglist = [
            '--disable',
            self.endpoint.id
        ]
        verifylist = [
            ('disabled', True),
            ('endpoint', self.endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'enabled': False,
            'interface': None,
            'url': None,
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            self.endpoint.id,
            **kwargs
        )
        self.assertIsNone(result)


class TestEndpointShow(TestEndpoint):

    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

    def setUp(self):
        super(TestEndpointShow, self).setUp()

        self.endpoints_mock.get.return_value = self.endpoint

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service

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
        self.endpoints_mock.get.assert_called_with(
            self.endpoint.id,
        )

        collist = (
            'enabled',
            'id',
            'interface',
            'region',
            'service_id',
            'service_name',
            'service_type',
            'url',
        )
        self.assertEqual(collist, columns)
        datalist = (
            True,
            self.endpoint.id,
            self.endpoint.interface,
            self.endpoint.region,
            self.service.id,
            self.service.name,
            self.service.type,
            self.endpoint.url,
        )
        self.assertEqual(datalist, data)


class TestEndpointCreateServiceWithoutName(TestEndpointCreate):

    service = identity_fakes.FakeService.create_one_service(
        attrs={'service_name': ''})

    def setUp(self):
        super(TestEndpointCreate, self).setUp()

        self.endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
            attrs={'service_id': self.service.id})

        self.endpoints_mock.create.return_value = self.endpoint

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)


class TestEndpointListServiceWithoutName(TestEndpointList):

    service = identity_fakes.FakeService.create_one_service(
        attrs={'service_name': ''})
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

    def setUp(self):
        super(TestEndpointList, self).setUp()

        self.endpoints_mock.list.return_value = [self.endpoint]

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service
        self.services_mock.list.return_value = [self.service]

        # Get the command object to test
        self.cmd = endpoint.ListEndpoint(self.app, None)


class TestEndpointShowServiceWithoutName(TestEndpointShow):

    service = identity_fakes.FakeService.create_one_service(
        attrs={'service_name': ''})
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

    def setUp(self):
        super(TestEndpointShow, self).setUp()

        self.endpoints_mock.get.return_value = self.endpoint

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = self.service

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)


class TestAddProjectToEndpoint(TestEndpoint):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

    new_ep_filter = identity_fakes.FakeEndpoint.create_one_endpoint_filter(
        attrs={'endpoint': endpoint.id,
               'project': project.id}
    )

    def setUp(self):
        super(TestAddProjectToEndpoint, self).setUp()

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
            project=self.project.id,
            endpoint=self.endpoint.id
        )
        self.assertIsNone(result)

    def test_add_project_to_endpoint_with_option(self):
        arglist = [
            self.endpoint.id,
            self.project.id,
            '--project-domain', self.domain.id,
        ]
        verifylist = [
            ('endpoint', self.endpoint.id),
            ('project', self.project.id),
            ('project_domain', self.domain.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.ep_filter_mock.add_endpoint_to_project.assert_called_with(
            project=self.project.id,
            endpoint=self.endpoint.id
        )
        self.assertIsNone(result)


class TestRemoveProjectEndpoint(TestEndpoint):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    service = identity_fakes.FakeService.create_one_service()
    endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(
        attrs={'service_id': service.id})

    def setUp(self):
        super(TestRemoveProjectEndpoint, self).setUp()

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
            '--project-domain', self.domain.id,
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
