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
from unittest import mock

from openstackclient.compute.v2 import hypervisor_stats
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes


class TestHypervisorStats(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.compute_client.get = mock.Mock()


# Not in fakes.py because hypervisor stats has been deprecated


def create_one_hypervisor_stats(attrs=None):
    """Create a fake hypervisor stats.

    :param dict attrs:
        A dictionary with all attributes
    :return:
        A dictionary that contains hypervisor stats information keys
    """
    attrs = attrs or {}

    # Set default attributes.
    stats_info = {
        'count': 2,
        'current_workload': 0,
        'disk_available_least': 50,
        'free_disk_gb': 100,
        'free_ram_mb': 23000,
        'local_gb': 100,
        'local_gb_used': 0,
        'memory_mb': 23800,
        'memory_mb_used': 1400,
        'running_vms': 3,
        'vcpus': 8,
        'vcpus_used': 3,
    }

    # Overwrite default attributes.
    stats_info.update(attrs)

    return stats_info


class TestHypervisorStatsShow(TestHypervisorStats):
    _stats = create_one_hypervisor_stats()

    def setUp(self):
        super().setUp()

        self.compute_client.get.return_value = fakes.FakeResponse(
            data={'hypervisor_statistics': self._stats}
        )

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
