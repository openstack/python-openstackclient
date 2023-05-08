#   Copyright 2016 EasyStack Corporation
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

import json
from unittest import mock

from novaclient import exceptions as nova_exceptions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.compute.v2 import hypervisor
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestHypervisor(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        # Create and get a shortcut to the compute client mock
        self.app.client_manager.sdk_connection = mock.Mock()
        self.sdk_client = self.app.client_manager.sdk_connection.compute
        self.sdk_client.reset_mock()


class TestHypervisorList(TestHypervisor):
    def setUp(self):
        super().setUp()

        # Fake hypervisors to be listed up
        self.hypervisors = compute_fakes.create_hypervisors()
        self.sdk_client.hypervisors.return_value = self.hypervisors

        self.columns = (
            "ID",
            "Hypervisor Hostname",
            "Hypervisor Type",
            "Host IP",
            "State",
        )
        self.columns_long = (
            "ID",
            "Hypervisor Hostname",
            "Hypervisor Type",
            "Host IP",
            "State",
            "vCPUs Used",
            "vCPUs",
            "Memory MB Used",
            "Memory MB",
        )
        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].name,
                self.hypervisors[0].hypervisor_type,
                self.hypervisors[0].host_ip,
                self.hypervisors[0].state,
            ),
            (
                self.hypervisors[1].id,
                self.hypervisors[1].name,
                self.hypervisors[1].hypervisor_type,
                self.hypervisors[1].host_ip,
                self.hypervisors[1].state,
            ),
        )

        self.data_long = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].name,
                self.hypervisors[0].hypervisor_type,
                self.hypervisors[0].host_ip,
                self.hypervisors[0].state,
                self.hypervisors[0].vcpus_used,
                self.hypervisors[0].vcpus,
                self.hypervisors[0].memory_used,
                self.hypervisors[0].memory_size,
            ),
            (
                self.hypervisors[1].id,
                self.hypervisors[1].name,
                self.hypervisors[1].hypervisor_type,
                self.hypervisors[1].host_ip,
                self.hypervisors[1].state,
                self.hypervisors[1].vcpus_used,
                self.hypervisors[1].vcpus,
                self.hypervisors[1].memory_used,
                self.hypervisors[1].memory_size,
            ),
        )
        # Get the command object to test
        self.cmd = hypervisor.ListHypervisor(self.app, None)

    def test_hypervisor_list_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.hypervisors.assert_called_with(details=True)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_hypervisor_list_matching_option_found(self):
        arglist = [
            '--matching',
            self.hypervisors[0].name,
        ]
        verifylist = [
            ('matching', self.hypervisors[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake the return value of search()
        self.sdk_client.hypervisors.return_value = [self.hypervisors[0]]

        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].name,
                self.hypervisors[1].hypervisor_type,
                self.hypervisors[1].host_ip,
                self.hypervisors[1].state,
            ),
        )

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.sdk_client.hypervisors.assert_called_with(
            hypervisor_hostname_pattern=self.hypervisors[0].name, details=True
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_hypervisor_list_matching_option_not_found(self):
        arglist = [
            '--matching',
            'xxx',
        ]
        verifylist = [
            ('matching', 'xxx'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception raised from search()
        self.sdk_client.hypervisors.side_effect = exceptions.NotFound(None)

        self.assertRaises(
            exceptions.NotFound, self.cmd.take_action, parsed_args
        )

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_hypervisor_list_with_matching_and_pagination_options(
        self, sm_mock
    ):
        arglist = [
            '--matching',
            self.hypervisors[0].name,
            '--limit',
            '1',
            '--marker',
            self.hypervisors[0].name,
        ]
        verifylist = [
            ('matching', self.hypervisors[0].name),
            ('limit', 1),
            ('marker', self.hypervisors[0].name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.assertIn(
            '--matching is not compatible with --marker or --limit', str(ex)
        )

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_hypervisor_list_long_option(self, sm_mock):
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

        self.sdk_client.hypervisors.assert_called_with(details=True)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, tuple(data))

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_hypervisor_list_with_limit(self, sm_mock):
        arglist = [
            '--limit',
            '1',
        ]
        verifylist = [
            ('limit', 1),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.sdk_client.hypervisors.assert_called_with(limit=1, details=True)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_hypervisor_list_with_limit_pre_v233(self, sm_mock):
        arglist = [
            '--limit',
            '1',
        ]
        verifylist = [
            ('limit', 1),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.assertIn(
            '--os-compute-api-version 2.33 or greater is required', str(ex)
        )

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_hypervisor_list_with_marker(self, sm_mock):
        arglist = [
            '--marker',
            'test_hyp',
        ]
        verifylist = [
            ('marker', 'test_hyp'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.sdk_client.hypervisors.assert_called_with(
            marker='test_hyp', details=True
        )

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_hypervisor_list_with_marker_pre_v233(self, sm_mock):
        arglist = [
            '--marker',
            'test_hyp',
        ]
        verifylist = [
            ('marker', 'test_hyp'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.assertIn(
            '--os-compute-api-version 2.33 or greater is required', str(ex)
        )


class TestHypervisorShow(TestHypervisor):
    def setUp(self):
        super().setUp()

        uptime_string = (
            ' 01:28:24 up 3 days, 11:15,  1 user, '
            ' load average: 0.94, 0.62, 0.50\n'
        )

        # Fake hypervisors to be listed up
        self.hypervisor = compute_fakes.create_one_hypervisor(
            attrs={
                'uptime': uptime_string,
            }
        )

        # Return value of compute_client.find_hypervisor
        self.sdk_client.find_hypervisor.return_value = self.hypervisor

        # Return value of compute_client.aggregates()
        self.sdk_client.aggregates.return_value = []

        # Return value of compute_client.get_hypervisor_uptime()
        uptime_info = {
            'status': self.hypervisor.status,
            'state': self.hypervisor.state,
            'id': self.hypervisor.id,
            'hypervisor_hostname': self.hypervisor.name,
            'uptime': uptime_string,
        }
        self.sdk_client.get_hypervisor_uptime.return_value = uptime_info

        self.columns_v288 = (
            'aggregates',
            'cpu_info',
            'host_ip',
            'host_time',
            'hypervisor_hostname',
            'hypervisor_type',
            'hypervisor_version',
            'id',
            'load_average',
            'service_host',
            'service_id',
            'state',
            'status',
            'uptime',
            'users',
        )

        self.data_v288 = (
            [],
            format_columns.DictColumn({'aaa': 'aaa'}),
            '192.168.0.10',
            '01:28:24',
            self.hypervisor.name,
            'QEMU',
            2004001,
            self.hypervisor.id,
            '0.94, 0.62, 0.50',
            'aaa',
            1,
            'up',
            'enabled',
            '3 days, 11:15',
            '1',
        )

        self.columns = (
            'aggregates',
            'cpu_info',
            'current_workload',
            'disk_available_least',
            'free_disk_gb',
            'free_ram_mb',
            'host_ip',
            'host_time',
            'hypervisor_hostname',
            'hypervisor_type',
            'hypervisor_version',
            'id',
            'load_average',
            'local_gb',
            'local_gb_used',
            'memory_mb',
            'memory_mb_used',
            'running_vms',
            'service_host',
            'service_id',
            'state',
            'status',
            'uptime',
            'users',
            'vcpus',
            'vcpus_used',
        )
        self.data = (
            [],
            format_columns.DictColumn({'aaa': 'aaa'}),
            0,
            50,
            50,
            1024,
            '192.168.0.10',
            '01:28:24',
            self.hypervisor.name,
            'QEMU',
            2004001,
            self.hypervisor.id,
            '0.94, 0.62, 0.50',
            50,
            0,
            1024,
            512,
            0,
            'aaa',
            1,
            'up',
            'enabled',
            '3 days, 11:15',
            '1',
            4,
            0,
        )

        # Get the command object to test
        self.cmd = hypervisor.ShowHypervisor(self.app, None)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_hypervisor_show(self, sm_mock):
        arglist = [
            self.hypervisor.name,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns_v288, columns)
        self.assertCountEqual(self.data_v288, data)

    @mock.patch.object(
        sdk_utils, 'supports_microversion', side_effect=[False, True, False]
    )
    def test_hypervisor_show_pre_v288(self, sm_mock):
        arglist = [
            self.hypervisor.name,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_hypervisor_show_pre_v228(self, sm_mock):
        # before microversion 2.28, nova returned a stringified version of this
        # field
        self.hypervisor.cpu_info = json.dumps(self.hypervisor.cpu_info)
        self.sdk_client.find_hypervisor.return_value = self.hypervisor

        arglist = [
            self.hypervisor.name,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    @mock.patch.object(
        sdk_utils, 'supports_microversion', side_effect=[False, True, False]
    )
    def test_hypervisor_show_uptime_not_implemented(self, sm_mock):
        arglist = [
            self.hypervisor.name,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.sdk_client.get_hypervisor_uptime.side_effect = (
            nova_exceptions.HTTPNotImplemented(501)
        )

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            'aggregates',
            'cpu_info',
            'current_workload',
            'disk_available_least',
            'free_disk_gb',
            'free_ram_mb',
            'host_ip',
            'hypervisor_hostname',
            'hypervisor_type',
            'hypervisor_version',
            'id',
            'local_gb',
            'local_gb_used',
            'memory_mb',
            'memory_mb_used',
            'running_vms',
            'service_host',
            'service_id',
            'state',
            'status',
            'vcpus',
            'vcpus_used',
        )
        expected_data = (
            [],
            format_columns.DictColumn({'aaa': 'aaa'}),
            0,
            50,
            50,
            1024,
            '192.168.0.10',
            self.hypervisor.name,
            'QEMU',
            2004001,
            self.hypervisor.id,
            50,
            0,
            1024,
            512,
            0,
            'aaa',
            1,
            'up',
            'enabled',
            4,
            0,
        )

        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, data)
