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
#

import mock

from openstackclient.compute.v2 import host
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestHost(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestHost, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.host_list'
)
class TestHostList(TestHost):

    host = compute_fakes.FakeHost.create_one_host()

    columns = (
        'Host Name',
        'Service',
        'Zone',
    )

    data = [(
        host['host_name'],
        host['service'],
        host['zone'],
    )]

    def setUp(self):
        super(TestHostList, self).setUp()

        self.cmd = host.ListHost(self.app, None)

    def test_host_list_no_option(self, h_mock):
        h_mock.return_value = [self.host]
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        h_mock.assert_called_with(None)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_host_list_with_option(self, h_mock):
        h_mock.return_value = [self.host]
        arglist = [
            '--zone', self.host['zone'],
        ]
        verifylist = [
            ('zone', self.host['zone']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        h_mock.assert_called_with(self.host['zone'])
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.host_set'
)
class TestHostSet(TestHost):

    def setUp(self):
        super(TestHostSet, self).setUp()

        self.host = compute_fakes.FakeHost.create_one_host()

        self.cmd = host.SetHost(self.app, None)

    def test_host_set_no_option(self, h_mock):
        h_mock.return_value = self.host
        h_mock.update.return_value = None
        arglist = [
            self.host['host'],
        ]
        verifylist = [
            ('host', self.host['host']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        h_mock.assert_called_with(self.host['host'])

    def test_host_set(self, h_mock):
        h_mock.return_value = self.host
        h_mock.update.return_value = None
        arglist = [
            '--enable',
            '--disable-maintenance',
            self.host['host'],
        ]
        verifylist = [
            ('enable', True),
            ('enable_maintenance', False),
            ('host', self.host['host']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        h_mock.assert_called_with(self.host['host'], status='enable',
                                  maintenance_mode='disable')


@mock.patch(
    'openstackclient.api.compute_v2.APIv2.host_show'
)
class TestHostShow(TestHost):

    host = compute_fakes.FakeHost.create_one_host()

    columns = (
        'Host',
        'Project',
        'CPU',
        'Memory MB',
        'Disk GB',
    )

    data = [(
        host['host'],
        host['project'],
        host['cpu'],
        host['memory_mb'],
        host['disk_gb'],
    )]

    def setUp(self):
        super(TestHostShow, self).setUp()

        self.cmd = host.ShowHost(self.app, None)

    def test_host_show_no_option(self, h_mock):
        h_mock.host_show.return_value = [self.host]
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_host_show_with_option(self, h_mock):
        h_mock.return_value = [self.host]
        arglist = [
            self.host['host_name'],
        ]
        verifylist = [
            ('host', self.host['host_name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        h_mock.assert_called_with(self.host['host_name'])
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
