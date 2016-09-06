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

from openstackclient.identity.v2_0 import endpoint
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes


class TestEndpoint(identity_fakes.TestIdentityv2):

    fake_service = identity_fakes.FakeService.create_one_service()
    attr = {
        'service_name': fake_service.name,
        'service_id': fake_service.id,
    }
    fake_endpoint = identity_fakes.FakeEndpoint.create_one_endpoint(attr)

    def setUp(self):
        super(TestEndpoint, self).setUp()

        # Get a shortcut to the EndpointManager Mock
        self.endpoints_mock = self.app.client_manager.identity.endpoints
        self.endpoints_mock.reset_mock()

        # Get a shortcut to the ServiceManager Mock
        self.services_mock = self.app.client_manager.identity.services
        self.services_mock.reset_mock()


class TestEndpointCreate(TestEndpoint):

    def setUp(self):
        super(TestEndpointCreate, self).setUp()

        self.endpoints_mock.create.return_value = self.fake_endpoint

        self.services_mock.get.return_value = self.fake_service

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)

    def test_endpoint_create(self):
        arglist = [
            '--publicurl', self.fake_endpoint.publicurl,
            '--internalurl', self.fake_endpoint.internalurl,
            '--adminurl', self.fake_endpoint.adminurl,
            '--region', self.fake_endpoint.region,
            self.fake_service.id,
        ]
        verifylist = [
            ('adminurl', self.fake_endpoint.adminurl),
            ('internalurl', self.fake_endpoint.internalurl),
            ('publicurl', self.fake_endpoint.publicurl),
            ('region', self.fake_endpoint.region),
            ('service', self.fake_service.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # EndpointManager.create(region, service_id, publicurl, adminurl,
        #  internalurl)
        self.endpoints_mock.create.assert_called_with(
            self.fake_endpoint.region,
            self.fake_service.id,
            self.fake_endpoint.publicurl,
            self.fake_endpoint.adminurl,
            self.fake_endpoint.internalurl,
        )

        collist = ('adminurl', 'id', 'internalurl', 'publicurl',
                   'region', 'service_id', 'service_name', 'service_type')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_endpoint.adminurl,
            self.fake_endpoint.id,
            self.fake_endpoint.internalurl,
            self.fake_endpoint.publicurl,
            self.fake_endpoint.region,
            self.fake_endpoint.service_id,
            self.fake_endpoint.service_name,
            self.fake_endpoint.service_type,
        )

        self.assertEqual(datalist, data)


class TestEndpointDelete(TestEndpoint):

    def setUp(self):
        super(TestEndpointDelete, self).setUp()

        self.endpoints_mock.get.return_value = self.fake_endpoint
        self.endpoints_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = endpoint.DeleteEndpoint(self.app, None)

    def test_endpoint_delete_no_options(self):
        arglist = [
            self.fake_endpoint.id,
        ]
        verifylist = [
            ('endpoints', [self.fake_endpoint.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.endpoints_mock.delete.assert_called_with(
            self.fake_endpoint.id,
        )
        self.assertIsNone(result)


class TestEndpointList(TestEndpoint):

    def setUp(self):
        super(TestEndpointList, self).setUp()

        self.endpoints_mock.list.return_value = [self.fake_endpoint]

        self.services_mock.get.return_value = self.fake_service

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

        collist = ('ID', 'Region', 'Service Name', 'Service Type')
        self.assertEqual(collist, columns)
        datalist = ((
            self.fake_endpoint.id,
            self.fake_endpoint.region,
            self.fake_endpoint.service_name,
            self.fake_endpoint.service_type,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_endpoint_list_long(self):
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

        self.endpoints_mock.list.assert_called_with()

        collist = ('ID', 'Region', 'Service Name', 'Service Type',
                   'PublicURL', 'AdminURL', 'InternalURL')
        self.assertEqual(collist, columns)
        datalist = ((
            self.fake_endpoint.id,
            self.fake_endpoint.region,
            self.fake_endpoint.service_name,
            self.fake_endpoint.service_type,
            self.fake_endpoint.publicurl,
            self.fake_endpoint.adminurl,
            self.fake_endpoint.internalurl,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestEndpointShow(TestEndpoint):

    def setUp(self):
        super(TestEndpointShow, self).setUp()

        self.endpoints_mock.list.return_value = [self.fake_endpoint]

        self.services_mock.get.return_value = self.fake_service

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)

    def test_endpoint_show(self):
        arglist = [
            self.fake_endpoint.id,
        ]
        verifylist = [
            ('endpoint_or_service', self.fake_endpoint.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        # EndpointManager.list()
        self.endpoints_mock.list.assert_called_with()
        # ServiceManager.get(name)
        self.services_mock.get.assert_called_with(
            self.fake_endpoint.service_id,
        )

        collist = ('adminurl', 'id', 'internalurl', 'publicurl',
                   'region', 'service_id', 'service_name', 'service_type')
        self.assertEqual(collist, columns)
        datalist = (
            self.fake_endpoint.adminurl,
            self.fake_endpoint.id,
            self.fake_endpoint.internalurl,
            self.fake_endpoint.publicurl,
            self.fake_endpoint.region,
            self.fake_endpoint.service_id,
            self.fake_endpoint.service_name,
            self.fake_endpoint.service_type,
        )
        self.assertEqual(datalist, data)
