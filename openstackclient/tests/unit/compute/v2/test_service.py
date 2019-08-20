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

import mock
from mock import call
from novaclient import api_versions
from osc_lib import exceptions
import six

from openstackclient.compute.v2 import service
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestService(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestService, self).setUp()

        # Get a shortcut to the ServiceManager Mock
        self.service_mock = self.app.client_manager.compute.services
        self.service_mock.reset_mock()


class TestServiceDelete(TestService):

    services = compute_fakes.FakeService.create_services(count=2)

    def setUp(self):
        super(TestServiceDelete, self).setUp()

        self.service_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = service.DeleteService(self.app, None)

    def test_service_delete(self):
        arglist = [
            self.services[0].binary,
        ]
        verifylist = [
            ('service', [self.services[0].binary]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.delete.assert_called_with(
            self.services[0].binary,
        )
        self.assertIsNone(result)

    def test_multi_services_delete(self):
        arglist = []
        for s in self.services:
            arglist.append(s.binary)
        verifylist = [
            ('service', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self.services:
            calls.append(call(s.binary))
        self.service_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_services_delete_with_exception(self):
        arglist = [
            self.services[0].binary,
            'unexist_service',
        ]
        verifylist = [
            ('service', arglist)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        delete_mock_result = [None, exceptions.CommandError]
        self.service_mock.delete = (
            mock.Mock(side_effect=delete_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 compute services failed to delete.', str(e))

        self.service_mock.delete.assert_any_call(self.services[0].binary)
        self.service_mock.delete.assert_any_call('unexist_service')


class TestServiceList(TestService):

    service = compute_fakes.FakeService.create_one_service()

    columns = (
        'ID',
        'Binary',
        'Host',
        'Zone',
        'Status',
        'State',
        'Updated At',
    )
    columns_long = columns + (
        'Disabled Reason',
    )

    data = [(
        service.id,
        service.binary,
        service.host,
        service.zone,
        service.status,
        service.state,
        service.updated_at,
    )]
    data_long = [data[0] + (service.disabled_reason, )]

    def setUp(self):
        super(TestServiceList, self).setUp()

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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

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

        self.service_mock.list.assert_called_with(
            self.service.host,
            self.service.binary,
        )

        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


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
        try:
            self.cmd.take_action(parsed_args)
            self.fail("CommandError should be raised.")
        except exceptions.CommandError as e:
            self.assertEqual("Cannot specify option --disable-reason without "
                             "--disable specified.", str(e))

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
        try:
            self.cmd.take_action(parsed_args)
            self.fail("CommandError should be raised.")
        except exceptions.CommandError as e:
            self.assertEqual("Cannot specify option --disable-reason without "
                             "--disable specified.", str(e))

    def test_service_set_state_up(self):
        arglist = [
            '--up',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('up', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.11')
        result = self.cmd.take_action(parsed_args)
        self.service_mock.force_down.assert_called_once_with(
            self.service.host, self.service.binary, False)
        self.assertNotCalled(self.service_mock.enable)
        self.assertNotCalled(self.service_mock.disable)
        self.assertIsNone(result)

    def test_service_set_state_down(self):
        arglist = [
            '--down',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('down', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.11')
        result = self.cmd.take_action(parsed_args)
        self.service_mock.force_down.assert_called_once_with(
            self.service.host, self.service.binary, True)
        self.assertNotCalled(self.service_mock.enable)
        self.assertNotCalled(self.service_mock.disable)
        self.assertIsNone(result)

    def test_service_set_enable_and_state_down(self):
        arglist = [
            '--enable',
            '--down',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('down', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.11')
        result = self.cmd.take_action(parsed_args)
        self.service_mock.enable.assert_called_once_with(
            self.service.host, self.service.binary)
        self.service_mock.force_down.assert_called_once_with(
            self.service.host, self.service.binary, True)
        self.assertIsNone(result)

    def test_service_set_enable_and_state_down_with_exception(self):
        arglist = [
            '--enable',
            '--down',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('down', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.11')
        with mock.patch.object(self.service_mock, 'enable',
                               side_effect=Exception()):
            self.assertRaises(exceptions.CommandError,
                              self.cmd.take_action, parsed_args)
            self.service_mock.force_down.assert_called_once_with(
                self.service.host, self.service.binary, True)

    def test_service_set_2_53_disable_down(self):
        # Tests disabling and forcing down a compute service with microversion
        # 2.53 which requires looking up the service by host and binary.
        arglist = [
            '--disable',
            '--down',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable', True),
            ('down', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.53')
        service_id = '339478d0-0b95-4a94-be63-d5be05dfeb1c'
        self.service_mock.list.return_value = [mock.Mock(id=service_id)]
        result = self.cmd.take_action(parsed_args)
        self.service_mock.disable.assert_called_once_with(service_id)
        self.service_mock.force_down.assert_called_once_with(service_id, True)
        self.assertIsNone(result)

    def test_service_set_2_53_disable_reason(self):
        # Tests disabling with reason a compute service with microversion
        # 2.53 which requires looking up the service by host and binary.
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
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.53')
        service_id = '339478d0-0b95-4a94-be63-d5be05dfeb1c'
        self.service_mock.list.return_value = [mock.Mock(id=service_id)]
        result = self.cmd.take_action(parsed_args)
        self.service_mock.disable_log_reason.assert_called_once_with(
            service_id, reason)
        self.assertIsNone(result)

    def test_service_set_2_53_enable_up(self):
        # Tests enabling and bringing up a compute service with microversion
        # 2.53 which requires looking up the service by host and binary.
        arglist = [
            '--enable',
            '--up',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('up', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.53')
        service_id = '339478d0-0b95-4a94-be63-d5be05dfeb1c'
        self.service_mock.list.return_value = [mock.Mock(id=service_id)]
        result = self.cmd.take_action(parsed_args)
        self.service_mock.enable.assert_called_once_with(service_id)
        self.service_mock.force_down.assert_called_once_with(service_id, False)
        self.assertIsNone(result)

    def test_service_set_find_service_by_host_and_binary_no_results(self):
        # Tests that no compute services are found by host and binary.
        self.service_mock.list.return_value = []
        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd._find_service_by_host_and_binary,
                               self.service_mock, 'fake-host', 'nova-compute')
        self.assertIn('Compute service for host "fake-host" and binary '
                      '"nova-compute" not found.', six.text_type(ex))

    def test_service_set_find_service_by_host_and_binary_many_results(self):
        # Tests that more than one compute service is found by host and binary.
        self.service_mock.list.return_value = [mock.Mock(), mock.Mock()]
        ex = self.assertRaises(exceptions.CommandError,
                               self.cmd._find_service_by_host_and_binary,
                               self.service_mock, 'fake-host', 'nova-compute')
        self.assertIn('Multiple compute services found for host "fake-host" '
                      'and binary "nova-compute". Unable to proceed.',
                      six.text_type(ex))
