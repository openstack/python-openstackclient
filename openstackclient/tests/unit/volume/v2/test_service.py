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

from osc_lib import exceptions

from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import service


class TestService(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ServiceManager Mock
        self.service_mock = self.volume_client.services
        self.service_mock.reset_mock()


class TestServiceList(TestService):
    # The service to be listed
    services = volume_fakes.create_one_service()

    def setUp(self):
        super().setUp()

        self.service_mock.list.return_value = [self.services]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list(self):
        arglist = [
            '--host',
            self.services.host,
            '--service',
            self.services.binary,
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

        datalist = (
            (
                self.services.binary,
                self.services.host,
                self.services.zone,
                self.services.status,
                self.services.state,
                self.services.updated_at,
            ),
        )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list services
        self.service_mock.list.assert_called_with(
            self.services.host,
            self.services.binary,
        )

        # checking if prohibited columns are present in output
        self.assertNotIn("Disabled Reason", columns)
        self.assertNotIn(self.services.disabled_reason, tuple(data))

    def test_service_list_with_long_option(self):
        arglist = [
            '--host',
            self.services.host,
            '--service',
            self.services.binary,
            '--long',
        ]
        verifylist = [
            ('host', self.services.host),
            ('service', self.services.binary),
            ('long', True),
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
            'Disabled Reason',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = (
            (
                self.services.binary,
                self.services.host,
                self.services.zone,
                self.services.status,
                self.services.state,
                self.services.updated_at,
                self.services.disabled_reason,
            ),
        )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        self.service_mock.list.assert_called_with(
            self.services.host,
            self.services.binary,
        )


class TestServiceSet(TestService):
    service = volume_fakes.create_one_service()

    def setUp(self):
        super().setUp()

        self.service_mock.enable.return_value = self.service
        self.service_mock.disable.return_value = self.service
        self.service_mock.disable_log_reason.return_value = self.service

        self.cmd = service.SetService(self.app, None)

    def test_service_set_nothing(self):
        arglist = [
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.service_mock.enable.assert_not_called()
        self.service_mock.disable.assert_not_called()
        self.service_mock.disable_log_reason.assert_not_called()
        self.assertIsNone(result)

    def test_service_set_enable(self):
        arglist = [
            '--enable',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.enable.assert_called_with(
            self.service.host, self.service.binary
        )
        self.service_mock.disable.assert_not_called()
        self.service_mock.disable_log_reason.assert_not_called()
        self.assertIsNone(result)

    def test_service_set_disable(self):
        arglist = [
            '--disable',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.disable.assert_called_with(
            self.service.host, self.service.binary
        )
        self.service_mock.enable.assert_not_called()
        self.service_mock.disable_log_reason.assert_not_called()
        self.assertIsNone(result)

    def test_service_set_disable_with_reason(self):
        reason = 'earthquake'
        arglist = [
            '--disable',
            '--disable-reason',
            reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable', True),
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.disable_log_reason.assert_called_with(
            self.service.host, self.service.binary, reason
        )
        self.assertIsNone(result)

    def test_service_set_only_with_disable_reason(self):
        reason = 'earthquake'
        arglist = [
            '--disable-reason',
            reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail("CommandError should be raised.")
        except exceptions.CommandError as e:
            self.assertEqual(
                "Cannot specify option --disable-reason without "
                "--disable specified.",
                str(e),
            )

    def test_service_set_enable_with_disable_reason(self):
        reason = 'earthquake'
        arglist = [
            '--enable',
            '--disable-reason',
            reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail("CommandError should be raised.")
        except exceptions.CommandError as e:
            self.assertEqual(
                "Cannot specify option --disable-reason without "
                "--disable specified.",
                str(e),
            )
