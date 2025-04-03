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

import json

from openstack.compute.v2 import hypervisor as _hypervisor
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.compute.v2 import hypervisor
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestHypervisorList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        # Fake hypervisors to be listed up
        self.hypervisors = list(
            sdk_fakes.generate_fake_resources(_hypervisor.Hypervisor, count=2)
        )
        self.compute_client.hypervisors.return_value = iter(self.hypervisors)

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

        self.compute_client.hypervisors.assert_called_with(details=True)
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
        self.compute_client.hypervisors.return_value = [self.hypervisors[0]]

        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].name,
                self.hypervisors[0].hypervisor_type,
                self.hypervisors[0].host_ip,
                self.hypervisors[0].state,
            ),
        )

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.hypervisors.assert_called_with(
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
        self.compute_client.hypervisors.side_effect = exceptions.NotFound(None)

        self.assertRaises(
            exceptions.NotFound, self.cmd.take_action, parsed_args
        )

    def test_hypervisor_list_with_matching_and_pagination_options(self):
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

    def test_hypervisor_list_long_option(self):
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

        self.compute_client.hypervisors.assert_called_with(details=True)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, tuple(data))

    def test_hypervisor_list_with_limit(self):
        self.set_compute_api_version('2.33')

        arglist = [
            '--limit',
            '1',
        ]
        verifylist = [
            ('limit', 1),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.hypervisors.assert_called_with(
            limit=1, details=True
        )

    def test_hypervisor_list_with_limit_pre_v233(self):
        self.set_compute_api_version('2.32')

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

    def test_hypervisor_list_with_marker(self):
        self.set_compute_api_version('2.33')

        arglist = [
            '--marker',
            'test_hyp',
        ]
        verifylist = [
            ('marker', 'test_hyp'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.hypervisors.assert_called_with(
            marker='test_hyp', details=True
        )

    def test_hypervisor_list_with_marker_pre_v233(self):
        self.set_compute_api_version('2.32')

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


class TestHypervisorShow(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        uptime_string = (
            ' 01:28:24 up 3 days, 11:15,  1 user, '
            ' load average: 0.94, 0.62, 0.50\n'
        )

        # Fake hypervisors to be listed up
        self.hypervisor = sdk_fakes.generate_fake_resource(
            _hypervisor.Hypervisor,
            uptime=uptime_string,
            service={"id": 1, "host": "aaa"},
            cpu_info={"aaa": "aaa"},
        )

        self.compute_client.find_hypervisor.return_value = self.hypervisor
        self.compute_client.get_hypervisor.return_value = self.hypervisor

        self.compute_client.aggregates.return_value = []

        uptime_info = {
            'status': self.hypervisor.status,
            'state': self.hypervisor.state,
            'id': self.hypervisor.id,
            'hypervisor_hostname': self.hypervisor.name,
            'uptime': uptime_string,
        }
        self.compute_client.get_hypervisor_uptime.return_value = uptime_info

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
            format_columns.DictColumn(self.hypervisor.cpu_info),
            self.hypervisor.host_ip,
            '01:28:24',
            self.hypervisor.name,
            self.hypervisor.hypervisor_type,
            self.hypervisor.hypervisor_version,
            self.hypervisor.id,
            '0.94, 0.62, 0.50',
            self.hypervisor.service_details["host"],
            self.hypervisor.service_details["id"],
            self.hypervisor.state,
            self.hypervisor.status,
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
            format_columns.DictColumn(self.hypervisor.cpu_info),
            self.hypervisor.current_workload,
            self.hypervisor.disk_available,
            self.hypervisor.local_disk_free,
            self.hypervisor.memory_free,
            self.hypervisor.host_ip,
            '01:28:24',
            self.hypervisor.name,
            self.hypervisor.hypervisor_type,
            self.hypervisor.hypervisor_version,
            self.hypervisor.id,
            '0.94, 0.62, 0.50',
            self.hypervisor.local_disk_size,
            self.hypervisor.local_disk_used,
            self.hypervisor.memory_size,
            self.hypervisor.memory_used,
            self.hypervisor.running_vms,
            self.hypervisor.service_details["host"],
            1,
            self.hypervisor.state,
            self.hypervisor.status,
            '3 days, 11:15',
            '1',
            self.hypervisor.vcpus,
            self.hypervisor.vcpus_used,
        )

        # Get the command object to test
        self.cmd = hypervisor.ShowHypervisor(self.app, None)

    def test_hypervisor_show(self):
        self.set_compute_api_version('2.88')

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

        self.compute_client.find_hypervisor.assert_called_once_with(
            self.hypervisor.name, ignore_missing=False, details=False
        )
        self.compute_client.get_hypervisor.assert_called_once_with(
            self.hypervisor.id
        )

    def test_hypervisor_show_pre_v288(self):
        self.set_compute_api_version('2.87')

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

        self.compute_client.find_hypervisor.assert_called_once_with(
            self.hypervisor.name, ignore_missing=False, details=False
        )
        self.compute_client.get_hypervisor.assert_called_once_with(
            self.hypervisor.id
        )

    def test_hypervisor_show_pre_v228(self):
        self.set_compute_api_version('2.27')

        # before microversion 2.28, nova returned a stringified version of this
        # field
        self.hypervisor.cpu_info = json.dumps(self.hypervisor.cpu_info)
        self.compute_client.find_hypervisor.return_value = self.hypervisor

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

        self.compute_client.find_hypervisor.assert_called_once_with(
            self.hypervisor.name, ignore_missing=False, details=False
        )
        self.compute_client.get_hypervisor.assert_called_once_with(
            self.hypervisor.id
        )

    def test_hypervisor_show_uptime_not_implemented(self):
        self.set_compute_api_version('2.87')

        arglist = [
            self.hypervisor.name,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_client.get_hypervisor_uptime.side_effect = (
            sdk_exceptions.HttpException(http_status=501)
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
            format_columns.DictColumn(self.hypervisor.cpu_info),
            self.hypervisor.current_workload,
            self.hypervisor.disk_available,
            self.hypervisor.local_disk_free,
            self.hypervisor.memory_free,
            self.hypervisor.host_ip,
            self.hypervisor.name,
            self.hypervisor.hypervisor_type,
            self.hypervisor.hypervisor_version,
            self.hypervisor.id,
            self.hypervisor.local_disk_size,
            self.hypervisor.local_disk_used,
            self.hypervisor.memory_size,
            self.hypervisor.memory_used,
            self.hypervisor.running_vms,
            self.hypervisor.service_details["host"],
            1,
            self.hypervisor.state,
            self.hypervisor.status,
            self.hypervisor.vcpus,
            self.hypervisor.vcpus_used,
        )

        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, data)

        self.compute_client.find_hypervisor.assert_called_once_with(
            self.hypervisor.name, ignore_missing=False, details=False
        )
        self.compute_client.get_hypervisor.assert_called_once_with(
            self.hypervisor.id
        )
