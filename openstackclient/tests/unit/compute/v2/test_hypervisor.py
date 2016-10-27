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

import copy

from novaclient import exceptions as nova_exceptions
from osc_lib import exceptions

from openstackclient.compute.v2 import hypervisor
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes


class TestHypervisor(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestHypervisor, self).setUp()

        # Get a shortcut to the compute client hypervisors mock
        self.hypervisors_mock = self.app.client_manager.compute.hypervisors
        self.hypervisors_mock.reset_mock()

        # Get a shortcut to the compute client aggregates mock
        self.aggregates_mock = self.app.client_manager.compute.aggregates
        self.aggregates_mock.reset_mock()


class TestHypervisorList(TestHypervisor):

    def setUp(self):
        super(TestHypervisorList, self).setUp()

        # Fake hypervisors to be listed up
        self.hypervisors = compute_fakes.FakeHypervisor.create_hypervisors()
        self.hypervisors_mock.list.return_value = self.hypervisors

        self.columns = (
            "ID",
            "Hypervisor Hostname",
            "Hypervisor Type",
            "Host IP",
            "State"
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
            "Memory MB"
        )
        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].hypervisor_hostname,
                self.hypervisors[0].hypervisor_type,
                self.hypervisors[0].host_ip,
                self.hypervisors[0].state
            ),
            (
                self.hypervisors[1].id,
                self.hypervisors[1].hypervisor_hostname,
                self.hypervisors[1].hypervisor_type,
                self.hypervisors[1].host_ip,
                self.hypervisors[1].state
            ),
        )

        self.data_long = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].hypervisor_hostname,
                self.hypervisors[0].hypervisor_type,
                self.hypervisors[0].host_ip,
                self.hypervisors[0].state,
                self.hypervisors[0].vcpus_used,
                self.hypervisors[0].vcpus,
                self.hypervisors[0].memory_mb_used,
                self.hypervisors[0].memory_mb
            ),
            (
                self.hypervisors[1].id,
                self.hypervisors[1].hypervisor_hostname,
                self.hypervisors[1].hypervisor_type,
                self.hypervisors[1].host_ip,
                self.hypervisors[1].state,
                self.hypervisors[1].vcpus_used,
                self.hypervisors[1].vcpus,
                self.hypervisors[1].memory_mb_used,
                self.hypervisors[1].memory_mb
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

        self.hypervisors_mock.list.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_hypervisor_list_matching_option_found(self):
        arglist = [
            '--matching', self.hypervisors[0].hypervisor_hostname,
        ]
        verifylist = [
            ('matching', self.hypervisors[0].hypervisor_hostname),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake the return value of search()
        self.hypervisors_mock.search.return_value = [self.hypervisors[0]]
        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].hypervisor_hostname,
                self.hypervisors[1].hypervisor_type,
                self.hypervisors[1].host_ip,
                self.hypervisors[1].state,
            ),
        )

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.hypervisors_mock.search.assert_called_with(
            self.hypervisors[0].hypervisor_hostname
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_hypervisor_list_matching_option_not_found(self):
        arglist = [
            '--matching', 'xxx',
        ]
        verifylist = [
            ('matching', 'xxx'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception raised from search()
        self.hypervisors_mock.search.side_effect = exceptions.NotFound(None)

        self.assertRaises(exceptions.NotFound,
                          self.cmd.take_action,
                          parsed_args)

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

        self.hypervisors_mock.list.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, tuple(data))


class TestHypervisorShow(TestHypervisor):

    def setUp(self):
        super(TestHypervisorShow, self).setUp()

        # Fake hypervisors to be listed up
        self.hypervisor = compute_fakes.FakeHypervisor.create_one_hypervisor()

        # Return value of utils.find_resource()
        self.hypervisors_mock.get.return_value = self.hypervisor

        # Return value of compute_client.aggregates.list()
        self.aggregates_mock.list.return_value = []

        # Return value of compute_client.hypervisors.uptime()
        uptime_info = {
            'status': self.hypervisor.status,
            'state': self.hypervisor.state,
            'id': self.hypervisor.id,
            'hypervisor_hostname': self.hypervisor.hypervisor_hostname,
            'uptime': ' 01:28:24 up 3 days, 11:15,  1 user, '
                      ' load average: 0.94, 0.62, 0.50\n',
        }
        self.hypervisors_mock.uptime.return_value = fakes.FakeResource(
            info=copy.deepcopy(uptime_info),
            loaded=True
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
            {'aaa': 'aaa'},
            0,
            50,
            50,
            1024,
            '192.168.0.10',
            '01:28:24',
            self.hypervisor.hypervisor_hostname,
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

    def test_hypervisor_show(self):
        arglist = [
            self.hypervisor.hypervisor_hostname,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.hypervisor_hostname),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_hyprvisor_show_uptime_not_implemented(self):
        arglist = [
            self.hypervisor.hypervisor_hostname,
        ]
        verifylist = [
            ('hypervisor', self.hypervisor.hypervisor_hostname),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.hypervisors_mock.uptime.side_effect = (
            nova_exceptions.HTTPNotImplemented(501))

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
            {'aaa': 'aaa'},
            0,
            50,
            50,
            1024,
            '192.168.0.10',
            self.hypervisor.hypervisor_hostname,
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
        self.assertEqual(expected_data, data)
