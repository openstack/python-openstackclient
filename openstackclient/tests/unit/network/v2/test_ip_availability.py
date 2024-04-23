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

from osc_lib.cli import format_columns

from openstackclient.network.v2 import ip_availability
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestIPAvailability(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects

        self.project = identity_fakes.FakeProject.create_one_project()
        self.projects_mock.get.return_value = self.project


class TestListIPAvailability(TestIPAvailability):
    _ip_availability = network_fakes.create_ip_availability(count=3)
    columns = (
        'Network ID',
        'Network Name',
        'Total IPs',
        'Used IPs',
    )
    data = []
    for net in _ip_availability:
        data.append(
            (
                net.network_id,
                net.network_name,
                net.total_ips,
                net.used_ips,
            )
        )

    def setUp(self):
        super().setUp()

        self.cmd = ip_availability.ListIPAvailability(self.app, None)
        self.network_client.network_ip_availabilities = mock.Mock(
            return_value=self._ip_availability
        )

    def test_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'ip_version': 4}

        self.network_client.network_ip_availabilities.assert_called_once_with(
            **filters
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_list_ip_version(self):
        arglist = [
            '--ip-version',
            str(4),
        ]
        verifylist = [('ip_version', 4)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'ip_version': 4}

        self.network_client.network_ip_availabilities.assert_called_once_with(
            **filters
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_list_project(self):
        arglist = ['--project', self.project.name]
        verifylist = [('project', self.project.name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'project_id': self.project.id, 'ip_version': 4}

        self.network_client.network_ip_availabilities.assert_called_once_with(
            **filters
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))


class TestShowIPAvailability(TestIPAvailability):
    _network = network_fakes.create_one_network()
    _ip_availability = network_fakes.create_one_ip_availability(
        attrs={'network_id': _network.id}
    )

    columns = (
        'network_id',
        'network_name',
        'project_id',
        'subnet_ip_availability',
        'total_ips',
        'used_ips',
    )
    data = (
        _ip_availability.network_id,
        _ip_availability.network_name,
        _ip_availability.project_id,
        format_columns.ListDictColumn(_ip_availability.subnet_ip_availability),
        _ip_availability.total_ips,
        _ip_availability.used_ips,
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_network_ip_availability = mock.Mock(
            return_value=self._ip_availability
        )
        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )

        # Get the command object to test
        self.cmd = ip_availability.ShowIPAvailability(self.app, None)

    def test_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_all_options(self):
        arglist = [
            self._ip_availability.network_name,
        ]
        verifylist = [('network', self._ip_availability.network_name)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.find_network_ip_availability.assert_called_once_with(
            self._ip_availability.network_id, ignore_missing=False
        )
        self.network_client.find_network.assert_called_once_with(
            self._ip_availability.network_name, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)
