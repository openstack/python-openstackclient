#   Copyright 2015 Mirantis, Inc.
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

from openstackclient.common import exceptions
from openstackclient.compute.v2 import service
from openstackclient.tests.compute.v2 import fakes as compute_fakes


class TestService(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestService, self).setUp()

        # Get a shortcut to the ServiceManager Mock
        self.service_mock = self.app.client_manager.compute.services
        self.service_mock.reset_mock()


class TestServiceDelete(TestService):

    def setUp(self):
        super(TestServiceDelete, self).setUp()

        self.service = compute_fakes.FakeService.create_one_service()

        self.service_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = service.DeleteService(self.app, None)

    def test_service_delete_no_options(self):
        arglist = [
            self.service.binary,
        ]
        verifylist = [
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.delete.assert_called_with(
            self.service.binary,
        )
        self.assertIsNone(result)


class TestServiceList(TestService):

    def setUp(self):
        super(TestServiceList, self).setUp()

        self.service = compute_fakes.FakeService.create_one_service()

        self.service_mock.list.return_value = [self.service]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list(self):
        arglist = [
            '--host', self.service.host,
            '--service', self.service.binary,
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.service_mock.list.assert_called_with(
            self.service.host,
            self.service.binary,
        )

        self.assertNotIn("Disabled Reason", columns)
        self.assertNotIn(self.service.disabled_reason, list(data)[0])

    def test_service_list_with_long_option(self):
        arglist = [
            '--host', self.service.host,
            '--service', self.service.binary,
            '--long'
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
            ('long', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertIn("Disabled Reason", columns)
        self.assertIn(self.service.disabled_reason, list(data)[0])


class TestServiceSet(TestService):

    def setUp(self):
        super(TestServiceSet, self).setUp()

        self.service = compute_fakes.FakeService.create_one_service()

        self.service_mock.enable.return_value = self.service
        self.service_mock.disable.return_value = self.service

        self.cmd = service.SetService(self.app, None)

    def test_set_nothing(self):
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
            self.service.host,
            self.service.binary
        )
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
            self.service.host,
            self.service.binary
        )
        self.assertIsNone(result)

    def test_service_set_disable_with_reason(self):
        reason = 'earthquake'
        arglist = [
            '--disable',
            '--disable-reason', reason,
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
            self.service.host,
            self.service.binary,
            reason
        )
        self.assertIsNone(result)

    def test_service_set_only_with_disable_reason(self):
        reason = 'earthquake'
        arglist = [
            '--disable-reason', reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_service_set_enable_with_disable_reason(self):
        reason = 'earthquake'
        arglist = [
            '--enable',
            '--disable-reason', reason,
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
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)
