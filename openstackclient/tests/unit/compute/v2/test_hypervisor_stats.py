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

from openstackclient.compute.v2 import hypervisor_stats
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestHypervisorStats(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestHypervisorStats, self).setUp()

        # Get a shortcut to the compute client hypervisors mock
        self.hypervisors_mock = self.app.client_manager.compute.hypervisors
        self.hypervisors_mock.reset_mock()


class TestHypervisorStatsShow(TestHypervisorStats):

    def setUp(self):
        super(TestHypervisorStatsShow, self).setUp()

        self.hypervisor_stats = \
            compute_fakes.FakeHypervisorStats.create_one_hypervisor_stats()

        self.hypervisors_mock.statistics.return_value =\
            self.hypervisor_stats

        self.cmd = hypervisor_stats.ShowHypervisorStats(self.app, None)

        self.columns = (
            'count',
            'current_workload',
            'disk_available_least',
            'free_disk_gb',
            'free_ram_mb',
            'local_gb',
            'local_gb_used',
            'memory_mb',
            'memory_mb_used',
            'running_vms',
            'vcpus',
            'vcpus_used',
        )

        self.data = (
            2,
            0,
            50,
            100,
            23000,
            100,
            0,
            23800,
            1400,
            3,
            8,
            3,
        )

    def test_hypervisor_show_stats(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
