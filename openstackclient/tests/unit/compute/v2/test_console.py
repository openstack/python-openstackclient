#   Copyright 2016 Huawei, Inc. All rights reserved.
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

from openstackclient.compute.v2 import console
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestConsole(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestConsole, self).setUp()
        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()


class TestConsoleUrlShow(TestConsole):

    def setUp(self):
        super(TestConsoleUrlShow, self).setUp()
        fake_console_data = {'remote_console': {'url': 'http://localhost',
                                                'protocol': 'fake_protocol',
                                                'type': 'fake_type'}}
        methods = {
            'get_console_url': fake_console_data
        }
        self.fake_server = compute_fakes.FakeServer.create_one_server(
            methods=methods)
        self.servers_mock.get.return_value = self.fake_server

        self.columns = (
            'protocol',
            'type',
            'url',
        )
        self.data = (
            fake_console_data['remote_console']['protocol'],
            fake_console_data['remote_console']['type'],
            fake_console_data['remote_console']['url']
        )

        self.cmd = console.ShowConsoleURL(self.app, None)

    def test_console_url_show_by_default(self):
        arglist = [
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'novnc'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with('novnc')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_console_url_show_with_novnc(self):
        arglist = [
            '--novnc',
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'novnc'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with('novnc')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_console_url_show_with_xvpvnc(self):
        arglist = [
            '--xvpvnc',
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'xvpvnc'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with('xvpvnc')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_console_url_show_with_spice(self):
        arglist = [
            '--spice',
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'spice-html5'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with(
            'spice-html5')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_console_url_show_compatible(self):
        methods = {
            'get_console_url': {'console': {'url': 'http://localhost',
                                            'type': 'fake_type'}},
        }
        old_fake_server = compute_fakes.FakeServer.create_one_server(
            methods=methods)
        old_columns = (
            'type',
            'url',
        )
        old_data = (
            methods['get_console_url']['console']['type'],
            methods['get_console_url']['console']['url']
        )
        arglist = [
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'novnc'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with mock.patch.object(self.servers_mock, 'get',
                               return_value=old_fake_server):
            columns, data = self.cmd.take_action(parsed_args)
            old_fake_server.get_console_url.assert_called_once_with('novnc')
            self.assertEqual(old_columns, columns)
            self.assertEqual(old_data, data)

    def test_console_url_show_with_rdp(self):
        arglist = [
            '--rdp',
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'rdp-html5'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with(
            'rdp-html5')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_console_url_show_with_serial(self):
        arglist = [
            '--serial',
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'serial'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with(
            'serial')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_console_url_show_with_mks(self):
        arglist = [
            '--mks',
            'foo_vm',
        ]
        verifylist = [
            ('url_type', 'webmks'),
            ('server', 'foo_vm'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.fake_server.get_console_url.assert_called_once_with('webmks')
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
