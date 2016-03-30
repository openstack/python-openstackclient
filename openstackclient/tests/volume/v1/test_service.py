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


from openstackclient.tests.volume.v1 import fakes as service_fakes
from openstackclient.volume.v1 import service


class TestService(service_fakes.TestService):

    def setUp(self):
        super(TestService, self).setUp()

        # Get a shortcut to the ServiceManager Mock
        self.service_mock = self.app.client_manager.volume.services
        self.service_mock.reset_mock()


class TestServiceList(TestService):

    # The service to be listed
    services = service_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestServiceList, self).setUp()

        self.service_mock.list.return_value = [self.services]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list(self):
        arglist = [
            '--host', self.services.host,
            '--service', self.services.binary,
        ]
        verifylist = [
            ('host', self.services.host),
            ('service', self.services.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = ((
            self.services.binary,
            self.services.host,
            self.services.zone,
            self.services.status,
            self.services.state,
            self.services.updated_at,
        ), )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list services
        self.service_mock.list.assert_called_with(
            self.services.host,
            self.services.binary,
        )

        # checking if prohibited columns are present in output
        self.assertNotIn("Disabled Reason", columns)
        self.assertNotIn(self.services.disabled_reason,
                         tuple(data))

    def test_service_list_with_long_option(self):
        arglist = [
            '--host', self.services.host,
            '--service', self.services.binary,
            '--long'
        ]
        verifylist = [
            ('host', self.services.host),
            ('service', self.services.binary),
            ('long', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
            'Disabled Reason'
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = ((
            self.services.binary,
            self.services.host,
            self.services.zone,
            self.services.status,
            self.services.state,
            self.services.updated_at,
            self.services.disabled_reason,
        ), )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        self.service_mock.list.assert_called_with(
            self.services.host,
            self.services.binary,
        )
