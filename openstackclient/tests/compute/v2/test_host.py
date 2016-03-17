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

from openstackclient.compute.v2 import host
from openstackclient.tests.compute.v2 import fakes as compute_fakes


class TestHost(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestHost, self).setUp()

        # Get a shortcut to the FlavorManager Mock
        self.host_mock = self.app.client_manager.compute.hosts
        self.host_mock.reset_mock()


class TestHostSet(TestHost):

    def setUp(self):
        super(TestHostSet, self).setUp()

        self.host = compute_fakes.FakeHost.create_one_host()
        self.host_mock.get.return_value = self.host
        self.host_mock.update.return_value = None

        self.cmd = host.SetHost(self.app, None)

    def test_host_set_no_option(self):
        arglist = [
            str(self.host.id)
        ]
        verifylist = [
            ('host', str(self.host.id))
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        body = {}
        self.host_mock.update.assert_called_with(self.host.id, body)

    def test_host_set(self):
        arglist = [
            '--enable',
            '--disable-maintenance',
            str(self.host.id)
        ]
        verifylist = [
            ('enable', True),
            ('enable_maintenance', False),
            ('host', str(self.host.id))
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        body = {'status': True, 'maintenance_mode': False}
        self.host_mock.update.assert_called_with(self.host.id, body)
