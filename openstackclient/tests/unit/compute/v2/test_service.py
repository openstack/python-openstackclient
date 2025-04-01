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

from unittest import mock

from openstack.compute.v2 import service as _service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.compute.v2 import service
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestServiceDelete(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.services = list(
            sdk_fakes.generate_fake_resources(_service.Service, count=2)
        )

        self.compute_client.delete_service.return_value = None

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

        self.compute_client.delete_service.assert_called_with(
            self.services[0].binary, ignore_missing=False
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
            calls.append(mock.call(s.binary, ignore_missing=False))
        self.compute_client.delete_service.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_services_delete_with_exception(self):
        arglist = [
            self.services[0].binary,
            'unexist_service',
        ]
        verifylist = [('service', arglist)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        delete_mock_result = [None, exceptions.CommandError]
        self.compute_client.delete_service = mock.Mock(
            side_effect=delete_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 compute services failed to delete.', str(e)
            )

        self.compute_client.delete_service.assert_any_call(
            self.services[0].binary, ignore_missing=False
        )
        self.compute_client.delete_service.assert_any_call(
            'unexist_service', ignore_missing=False
        )


class TestServiceList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.compute_client.services.return_value = [self.service]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list(self):
        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
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

        self.compute_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )

        expected_columns = (
            'ID',
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
        )
        expected_data = [
            (
                self.service.id,
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
            )
        ]

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, list(data))

    def test_service_list_with_long_option(self):
        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
            '--long',
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )

        expected_columns = (
            'ID',
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
            'Disabled Reason',
        )
        expected_data = [
            (
                self.service.id,
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
                self.service.disabled_reason,
            )
        ]

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, list(data))

    def test_service_list_with_long_option_2_11(self):
        self.set_compute_api_version('2.11')

        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
            '--long',
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )

        # In 2.11 there is also a forced_down column.
        expected_columns = (
            'ID',
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
            'Disabled Reason',
            'Forced Down',
        )
        expected_data = [
            (
                self.service.id,
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
                self.service.disabled_reason,
                self.service.is_forced_down,
            )
        ]

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, list(data))


class TestServiceSet(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)

        self.compute_client.enable_service.return_value = self.service
        self.compute_client.disable_service.return_value = self.service

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

        self.compute_client.enable_service.assert_not_called()
        self.compute_client.disable_service.assert_not_called()
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

        self.compute_client.enable_service.assert_called_with(
            None, self.service.host, self.service.binary
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

        self.compute_client.disable_service.assert_called_with(
            None, self.service.host, self.service.binary, None
        )
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

        self.compute_client.disable_service.assert_called_with(
            None, self.service.host, self.service.binary, reason
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

    def test_service_set_state_up(self):
        self.set_compute_api_version('2.11')

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
        result = self.cmd.take_action(parsed_args)
        self.compute_client.update_service_forced_down.assert_called_once_with(
            None, self.service.host, self.service.binary, False
        )
        self.assertNotCalled(self.compute_client.enable_service)
        self.assertNotCalled(self.compute_client.disable_service)
        self.assertIsNone(result)

    def test_service_set_state_down(self):
        self.set_compute_api_version('2.11')

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
        result = self.cmd.take_action(parsed_args)
        self.compute_client.update_service_forced_down.assert_called_once_with(
            None, self.service.host, self.service.binary, True
        )
        self.assertNotCalled(self.compute_client.enable_service)
        self.assertNotCalled(self.compute_client.disable_service)
        self.assertIsNone(result)

    def test_service_set_enable_and_state_down(self):
        self.set_compute_api_version('2.11')

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
        result = self.cmd.take_action(parsed_args)
        self.compute_client.enable_service.assert_called_once_with(
            None, self.service.host, self.service.binary
        )
        self.compute_client.update_service_forced_down.assert_called_once_with(
            None, self.service.host, self.service.binary, True
        )
        self.assertIsNone(result)

    def test_service_set_enable_and_state_down_with_exception(self):
        self.set_compute_api_version('2.11')

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

        with mock.patch.object(
            self.compute_client, 'enable_service', side_effect=Exception()
        ):
            self.assertRaises(
                exceptions.CommandError, self.cmd.take_action, parsed_args
            )
            self.compute_client.update_service_forced_down.assert_called_once_with(
                None, self.service.host, self.service.binary, True
            )

    def test_service_set_disable_down(self):
        # Tests disabling and forcing down a compute service with microversion
        # 2.53 which requires looking up the service by host and binary.
        self.set_compute_api_version('2.53')

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
        service_id = '339478d0-0b95-4a94-be63-d5be05dfeb1c'
        self.compute_client.services.return_value = [mock.Mock(id=service_id)]
        result = self.cmd.take_action(parsed_args)
        self.compute_client.disable_service.assert_called_once_with(
            service_id, self.service.host, self.service.binary, None
        )
        self.compute_client.update_service_forced_down.assert_called_once_with(
            service_id, self.service.host, self.service.binary, True
        )
        self.assertIsNone(result)

    def test_service_set_disable_reason(self):
        # Tests disabling with reason a compute service with microversion
        # 2.53 which requires looking up the service by host and binary.
        self.set_compute_api_version('2.53')

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
        service_id = '339478d0-0b95-4a94-be63-d5be05dfeb1c'
        self.compute_client.services.return_value = [mock.Mock(id=service_id)]
        result = self.cmd.take_action(parsed_args)
        self.compute_client.disable_service.assert_called_once_with(
            service_id, self.service.host, self.service.binary, reason
        )
        self.assertIsNone(result)

    def test_service_set_enable_up(self):
        # Tests enabling and bringing up a compute service with microversion
        # 2.53 which requires looking up the service by host and binary.
        self.set_compute_api_version('2.53')

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
        service_id = '339478d0-0b95-4a94-be63-d5be05dfeb1c'
        self.compute_client.services.return_value = [mock.Mock(id=service_id)]
        result = self.cmd.take_action(parsed_args)
        self.compute_client.enable_service.assert_called_once_with(
            service_id, self.service.host, self.service.binary
        )
        self.compute_client.update_service_forced_down.assert_called_once_with(
            service_id, self.service.host, self.service.binary, False
        )
        self.assertIsNone(result)

    def test_service_set_find_service_by_host_and_binary_no_results(self):
        # Tests that no compute services are found by host and binary.
        self.compute_client.services.return_value = []
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd._find_service_by_host_and_binary,
            self.compute_client,
            'fake-host',
            'nova-compute',
        )
        self.assertIn(
            'Compute service for host "fake-host" and binary '
            '"nova-compute" not found.',
            str(ex),
        )

    def test_service_set_find_service_by_host_and_binary_many_results(self):
        # Tests that more than one compute service is found by host and binary.
        self.compute_client.services.return_value = [
            mock.Mock(),
            mock.Mock(),
        ]
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd._find_service_by_host_and_binary,
            self.compute_client,
            'fake-host',
            'nova-compute',
        )
        self.assertIn(
            'Multiple compute services found for host "fake-host" '
            'and binary "nova-compute". Unable to proceed.',
            str(ex),
        )
