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


import copy

from openstackclient.identity.v3 import endpoint
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes


class TestEndpoint(identity_fakes.TestIdentityv3):

    def setUp(self):
        super(TestEndpoint, self).setUp()

        # Get a shortcut to the EndpointManager Mock
        self.endpoints_mock = self.app.client_manager.identity.endpoints
        self.endpoints_mock.reset_mock()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.app.client_manager.identity.services
        self.services_mock.reset_mock()

    def get_fake_service_name(self):
        return identity_fakes.service_name


class TestEndpointCreate(TestEndpoint):

    def setUp(self):
        super(TestEndpointCreate, self).setUp()

        self.endpoints_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)

    def test_endpoint_create_no_options(self):
        arglist = [
            identity_fakes.service_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
        ]
        verifylist = [
            ('enabled', True),
            ('service', identity_fakes.service_id),
            ('interface', identity_fakes.endpoint_interface),
            ('url', identity_fakes.endpoint_url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': identity_fakes.service_id,
            'url': identity_fakes.endpoint_url,
            'interface': identity_fakes.endpoint_interface,
            'enabled': True,
            'region': None,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('enabled', 'id', 'interface', 'region', 'service_id',
                   'service_name', 'service_type', 'url')
        self.assertEqual(collist, columns)
        datalist = (
            True,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            identity_fakes.endpoint_url,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_region(self):
        arglist = [
            identity_fakes.service_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
            '--region', identity_fakes.endpoint_region,
        ]
        verifylist = [
            ('enabled', True),
            ('service', identity_fakes.service_id),
            ('interface', identity_fakes.endpoint_interface),
            ('url', identity_fakes.endpoint_url),
            ('region', identity_fakes.endpoint_region),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': identity_fakes.service_id,
            'url': identity_fakes.endpoint_url,
            'interface': identity_fakes.endpoint_interface,
            'enabled': True,
            'region': identity_fakes.endpoint_region,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('enabled', 'id', 'interface', 'region', 'service_id',
                   'service_name', 'service_type', 'url')
        self.assertEqual(collist, columns)
        datalist = (
            True,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            identity_fakes.endpoint_url,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_enable(self):
        arglist = [
            identity_fakes.service_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
            '--enable'
        ]
        verifylist = [
            ('enabled', True),
            ('service', identity_fakes.service_id),
            ('interface', identity_fakes.endpoint_interface),
            ('url', identity_fakes.endpoint_url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': identity_fakes.service_id,
            'url': identity_fakes.endpoint_url,
            'interface': identity_fakes.endpoint_interface,
            'enabled': True,
            'region': None,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('enabled', 'id', 'interface', 'region', 'service_id',
                   'service_name', 'service_type', 'url')
        self.assertEqual(collist, columns)
        datalist = (
            True,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            identity_fakes.endpoint_url,
        )
        self.assertEqual(datalist, data)

    def test_endpoint_create_disable(self):
        arglist = [
            identity_fakes.service_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
            '--disable',
        ]
        verifylist = [
            ('enabled', False),
            ('service', identity_fakes.service_id),
            ('interface', identity_fakes.endpoint_interface),
            ('url', identity_fakes.endpoint_url),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': identity_fakes.service_id,
            'url': identity_fakes.endpoint_url,
            'interface': identity_fakes.endpoint_interface,
            'enabled': False,
            'region': None,
        }

        self.endpoints_mock.create.assert_called_with(
            **kwargs
        )

        collist = ('enabled', 'id', 'interface', 'region', 'service_id',
                   'service_name', 'service_type', 'url')
        self.assertEqual(collist, columns)
        datalist = (
            True,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            identity_fakes.endpoint_url,
        )
        self.assertEqual(datalist, data)


class TestEndpointDelete(TestEndpoint):

    def setUp(self):
        super(TestEndpointDelete, self).setUp()

        # This is the return value for utils.find_resource(endpoint)
        self.endpoints_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )
        self.endpoints_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = endpoint.DeleteEndpoint(self.app, None)

    def test_endpoint_delete(self):
        arglist = [
            identity_fakes.endpoint_id,
        ]
        verifylist = [
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        self.endpoints_mock.delete.assert_called_with(
            identity_fakes.endpoint_id,
        )


class TestEndpointList(TestEndpoint):

    def setUp(self):
        super(TestEndpointList, self).setUp()

        self.endpoints_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ENDPOINT),
                loaded=True,
            ),
        ]

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.ListEndpoint(self.app, None)

    def test_endpoint_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.endpoints_mock.list.assert_called_with()

        collist = ('ID', 'Region', 'Service Name', 'Service Type',
                   'Enabled', 'Interface', 'URL')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_region,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            True,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
        ),)
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_service(self):
        arglist = [
            '--service', identity_fakes.service_id,
        ]
        verifylist = [
            ('service', identity_fakes.service_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'service': identity_fakes.service_id,
        }
        self.endpoints_mock.list.assert_called_with(**kwargs)

        collist = ('ID', 'Region', 'Service Name', 'Service Type',
                   'Enabled', 'Interface', 'URL')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_region,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            True,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
        ),)
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_interface(self):
        arglist = [
            '--interface', identity_fakes.endpoint_interface,
        ]
        verifylist = [
            ('interface', identity_fakes.endpoint_interface),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'interface': identity_fakes.endpoint_interface,
        }
        self.endpoints_mock.list.assert_called_with(**kwargs)

        collist = ('ID', 'Region', 'Service Name', 'Service Type',
                   'Enabled', 'Interface', 'URL')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_region,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            True,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
        ),)
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_region(self):
        arglist = [
            '--region', identity_fakes.endpoint_region,
        ]
        verifylist = [
            ('region', identity_fakes.endpoint_region),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'region': identity_fakes.endpoint_region,
        }
        self.endpoints_mock.list.assert_called_with(**kwargs)

        collist = ('ID', 'Region', 'Service Name', 'Service Type',
                   'Enabled', 'Interface', 'URL')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_region,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            True,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_url,
        ),)
        self.assertEqual(datalist, tuple(data))


class TestEndpointSet(TestEndpoint):

    def setUp(self):
        super(TestEndpointSet, self).setUp()

        # This is the return value for utils.find_resource(endpoint)
        self.endpoints_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        self.endpoints_mock.update.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.SetEndpoint(self.app, None)

    def test_endpoint_set_no_options(self):
        arglist = [
            identity_fakes.endpoint_id,
        ]
        verifylist = [
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        self.assertNotCalled(self.endpoints_mock.update)

    def test_endpoint_set_interface(self):
        arglist = [
            '--interface', 'public',
            identity_fakes.endpoint_id
        ]
        verifylist = [
            ('interface', 'public'),
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': 'public',
            'url': None,
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            identity_fakes.endpoint_id,
            **kwargs
        )

    def test_endpoint_set_url(self):
        arglist = [
            '--url', 'http://localhost:5000',
            identity_fakes.endpoint_id
        ]
        verifylist = [
            ('url', 'http://localhost:5000'),
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': None,
            'url': 'http://localhost:5000',
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            identity_fakes.endpoint_id,
            **kwargs
        )

    def test_endpoint_set_service(self):
        arglist = [
            '--service', identity_fakes.service_id,
            identity_fakes.endpoint_id
        ]
        verifylist = [
            ('service', identity_fakes.service_id),
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': None,
            'url': None,
            'region': None,
            'service': identity_fakes.service_id,
        }
        self.endpoints_mock.update.assert_called_with(
            identity_fakes.endpoint_id,
            **kwargs
        )

    def test_endpoint_set_region(self):
        arglist = [
            '--region', 'e-rzzz',
            identity_fakes.endpoint_id
        ]
        verifylist = [
            ('region', 'e-rzzz'),
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': None,
            'interface': None,
            'url': None,
            'region': 'e-rzzz',
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            identity_fakes.endpoint_id,
            **kwargs
        )

    def test_endpoint_set_enable(self):
        arglist = [
            '--enable',
            identity_fakes.endpoint_id
        ]
        verifylist = [
            ('enabled', True),
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': True,
            'interface': None,
            'url': None,
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            identity_fakes.endpoint_id,
            **kwargs
        )

    def test_endpoint_set_disable(self):
        arglist = [
            '--disable',
            identity_fakes.endpoint_id
        ]
        verifylist = [
            ('disabled', True),
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.run(parsed_args)
        self.assertEqual(0, result)

        # Set expected values
        kwargs = {
            'enabled': False,
            'interface': None,
            'url': None,
            'region': None,
            'service': None,
        }
        self.endpoints_mock.update.assert_called_with(
            identity_fakes.endpoint_id,
            **kwargs
        )


class TestEndpointShow(TestEndpoint):

    def setUp(self):
        super(TestEndpointShow, self).setUp()

        self.endpoints_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)

    def test_endpoint_show(self):
        arglist = [
            identity_fakes.endpoint_id,
        ]
        verifylist = [
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.endpoints_mock.get.assert_called_with(
            identity_fakes.endpoint_id,
        )

        collist = ('enabled', 'id', 'interface', 'region', 'service_id',
                   'service_name', 'service_type', 'url')
        self.assertEqual(collist, columns)
        datalist = (
            True,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_interface,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            self.get_fake_service_name(),
            identity_fakes.service_type,
            identity_fakes.endpoint_url,
        )
        self.assertEqual(datalist, data)


class TestEndpointCreateServiceWithoutName(TestEndpointCreate):

    def setUp(self):
        super(TestEndpointCreate, self).setUp()

        self.endpoints_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE_WITHOUT_NAME),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)

    def get_fake_service_name(self):
        return ''


class TestEndpointListServiceWithoutName(TestEndpointList):

    def setUp(self):
        super(TestEndpointList, self).setUp()

        self.endpoints_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ENDPOINT),
                loaded=True,
            ),
        ]

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE_WITHOUT_NAME),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.ListEndpoint(self.app, None)

    def get_fake_service_name(self):
        return ''


class TestEndpointShowServiceWithoutName(TestEndpointShow):

    def setUp(self):
        super(TestEndpointShow, self).setUp()

        self.endpoints_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        # This is the return value for common.find_resource(service)
        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE_WITHOUT_NAME),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)

    def get_fake_service_name(self):
        return ''
