#   Copyright 2016 IBM Corporation
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

import uuid

from openstackclient.compute.v2 import host
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils as tests_utils


def _generate_fake_host():
    return {
        'service_id': 1,
        'host': 'host1',
        'uuid': 'host-id-' + uuid.uuid4().hex,
        'vcpus': 10,
        'memory_mb': 100,
        'local_gb': 100,
        'vcpus_used': 5,
        'memory_mb_used': 50,
        'local_gb_used': 10,
        'hypervisor_type': 'xen',
        'hypervisor_version': 1,
        'hypervisor_hostname': 'devstack1',
        'free_ram_mb': 50,
        'free_disk_gb': 50,
        'current_workload': 10,
        'running_vms': 1,
        'cpu_info': '',
        'disk_available_least': 1,
        'host_ip': '10.10.10.10',
        'supported_instances': '',
        'metrics': '',
        'pci_stats': '',
        'extra_resources': '',
        'stats': '',
        'numa_topology': '',
        'ram_allocation_ratio': 1.0,
        'cpu_allocation_ratio': 1.0,
        'zone': 'zone-' + uuid.uuid4().hex,
        'host_name': 'name-' + uuid.uuid4().hex,
        'service': 'service-' + uuid.uuid4().hex,
        'cpu': 4,
        'disk_gb': 100,
        'project': 'project-' + uuid.uuid4().hex,
    }


class TestHostList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._host = _generate_fake_host()
        self.columns = ('Host Name', 'Service', 'Zone')
        self.data = [
            (
                self._host['host_name'],
                self._host['service'],
                self._host['zone'],
            )
        ]

        self.compute_client.get.return_value = fakes.FakeResponse(
            data={'hosts': [self._host]}
        )
        self.cmd = host.ListHost(self.app, None)

    def test_host_list_no_option(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.get.assert_called_with(
            '/os-hosts', microversion='2.1'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_host_list_with_option(self):
        arglist = [
            '--zone',
            self._host['zone'],
        ]
        verifylist = [
            ('zone', self._host['zone']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.get.assert_called_with(
            '/os-hosts', microversion='2.1'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestHostSet(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._host = _generate_fake_host()
        self.compute_client.put.return_value = fakes.FakeResponse()

        self.cmd = host.SetHost(self.app, None)

    def test_host_set_no_option(self):
        arglist = [
            self._host['host'],
        ]
        verifylist = [
            ('host', self._host['host']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)
        self.compute_client.put.assert_not_called()

    def test_host_set(self):
        arglist = [
            '--enable',
            '--disable-maintenance',
            self._host['host'],
        ]
        verifylist = [
            ('enable', True),
            ('enable_maintenance', False),
            ('host', self._host['host']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)
        self.compute_client.put.assert_called_with(
            f'/os-hosts/{self._host["host"]}',
            json={
                'maintenance_mode': 'disable',
                'status': 'enable',
            },
            microversion='2.1',
        )


class TestHostShow(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._host = _generate_fake_host()

        self.columns = (
            'Host',
            'Project',
            'CPU',
            'Memory MB',
            'Disk GB',
        )
        self.data = [
            (
                self._host['host'],
                self._host['project'],
                self._host['cpu'],
                self._host['memory_mb'],
                self._host['disk_gb'],
            )
        ]

        self.compute_client.get.return_value = fakes.FakeResponse(
            data={
                'host': [
                    {
                        'resource': {
                            'host': self._host['host'],
                            'project': self._host['project'],
                            'cpu': self._host['cpu'],
                            'memory_mb': self._host['memory_mb'],
                            'disk_gb': self._host['disk_gb'],
                        }
                    }
                ],
            }
        )

        self.cmd = host.ShowHost(self.app, None)

    def test_host_show_no_option(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_host_show_with_option(self):
        arglist = [
            self._host['host_name'],
        ]
        verifylist = [
            ('host', self._host['host_name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.get.assert_called_with(
            '/os-hosts/' + self._host['host_name'], microversion='2.1'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
