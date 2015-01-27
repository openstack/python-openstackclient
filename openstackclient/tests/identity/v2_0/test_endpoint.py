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

from openstackclient.identity.v2_0 import endpoint
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes


class TestEndpoint(identity_fakes.TestIdentityv2):

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

        self.endpoints_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.CreateEndpoint(self.app, None)

    def test_endpoint_create(self):
        arglist = [
            '--publicurl', identity_fakes.endpoint_publicurl,
            '--internalurl', identity_fakes.endpoint_internalurl,
            '--adminurl', identity_fakes.endpoint_adminurl,
            '--region', identity_fakes.endpoint_region,
            identity_fakes.endpoint_name,
        ]
        verifylist = [
            ('adminurl', identity_fakes.endpoint_adminurl),
            ('internalurl', identity_fakes.endpoint_internalurl),
            ('publicurl', identity_fakes.endpoint_publicurl),
            ('region', identity_fakes.endpoint_region),
            ('service', identity_fakes.service_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # EndpointManager.create(region, service_id, publicurl, adminurl,
        #  internalurl)
        self.endpoints_mock.create.assert_called_with(
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            identity_fakes.endpoint_publicurl,
            identity_fakes.endpoint_adminurl,
            identity_fakes.endpoint_internalurl,
        )

        collist = ('adminurl', 'id', 'internalurl', 'publicurl',
                   'region', 'service_id', 'service_name', 'service_type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.endpoint_adminurl,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_internalurl,
            identity_fakes.endpoint_publicurl,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )

        self.assertEqual(datalist, data)


class TestEndpointDelete(TestEndpoint):

    def setUp(self):
        super(TestEndpointDelete, self).setUp()

        self.endpoints_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        self.endpoints_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = endpoint.DeleteEndpoint(self.app, None)

    def test_endpoint_delete_no_options(self):
        arglist = [
            identity_fakes.endpoint_id,
        ]
        verifylist = [
            ('endpoint', identity_fakes.endpoint_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

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

        collist = ('ID', 'Region', 'Service Name', 'Service Type')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_region,
            identity_fakes.service_name,
            identity_fakes.service_type,
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

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.endpoints_mock.list.assert_called_with()

        collist = ('ID', 'Region', 'Service Name', 'Service Type',
                   'PublicURL', 'AdminURL', 'InternalURL')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_region,
            identity_fakes.service_name,
            identity_fakes.service_type,
            identity_fakes.endpoint_publicurl,
            identity_fakes.endpoint_adminurl,
            identity_fakes.endpoint_internalurl,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestEndpointShow(TestEndpoint):

    def setUp(self):
        super(TestEndpointShow, self).setUp()

        self.endpoints_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ENDPOINT),
                loaded=True,
            ),
        ]

        self.services_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.SERVICE),
            loaded=True,
        )

        # Get the command object to test
        self.cmd = endpoint.ShowEndpoint(self.app, None)

    def test_endpoint_show(self):
        arglist = [
            identity_fakes.endpoint_name,
        ]
        verifylist = [
            ('endpoint_or_service', identity_fakes.endpoint_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # EndpointManager.list()
        self.endpoints_mock.list.assert_called_with()
        # ServiceManager.get(name)
        self.services_mock.get.assert_called_with(
            identity_fakes.service_name,
        )

        collist = ('adminurl', 'id', 'internalurl', 'publicurl',
                   'region', 'service_id', 'service_name', 'service_type')
        self.assertEqual(collist, columns)
        datalist = (
            identity_fakes.endpoint_adminurl,
            identity_fakes.endpoint_id,
            identity_fakes.endpoint_internalurl,
            identity_fakes.endpoint_publicurl,
            identity_fakes.endpoint_region,
            identity_fakes.service_id,
            identity_fakes.service_name,
            identity_fakes.service_type,
        )
        self.assertEqual(datalist, data)
