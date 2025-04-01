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

from unittest import mock

from openstack.compute.v2 import server as _server
from openstack.test import fakes as sdk_fakes

from openstackclient.compute.v2 import console
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils


class TestConsoleLog(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._server = sdk_fakes.generate_fake_resource(_server.Server)
        self.compute_client.find_server.return_value = self._server

        self.cmd = console.ShowConsoleLog(self.app, None)

    def test_show_no_args(self):
        arglist = []
        verifylist = []
        self.assertRaises(
            utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show(self):
        arglist = ['fake_server']
        verifylist = [('server', 'fake_server')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        output = {'output': '1st line\n2nd line\n'}
        self.compute_client.get_server_console_output.return_value = output
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            name_or_id='fake_server', ignore_missing=False
        )
        self.compute_client.get_server_console_output.assert_called_with(
            self._server.id, length=None
        )
        stdout = self.app.stdout.content
        self.assertEqual(stdout[0], output['output'])

    def test_show_lines(self):
        arglist = ['fake_server', '--lines', '15']
        verifylist = [('server', 'fake_server'), ('lines', 15)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        output = {'output': '1st line\n2nd line'}
        self.compute_client.get_server_console_output.return_value = output
        self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            name_or_id='fake_server', ignore_missing=False
        )
        self.compute_client.get_server_console_output.assert_called_with(
            self._server.id, length=15
        )


class TestConsoleUrlShow(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._server = sdk_fakes.generate_fake_resource(_server.Server)
        self.compute_client.find_server.return_value = self._server

        fake_console_data = {
            'url': 'http://localhost',
            'protocol': 'fake_protocol',
            'type': 'fake_type',
        }
        self.compute_client.create_console = mock.Mock(
            return_value=fake_console_data
        )

        self.columns = (
            'protocol',
            'type',
            'url',
        )
        self.data = (
            fake_console_data['protocol'],
            fake_console_data['type'],
            fake_console_data['url'],
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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='novnc'
        )
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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='novnc'
        )
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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='xvpvnc'
        )
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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='spice-html5'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='rdp-html5'
        )
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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='serial'
        )
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
        self.compute_client.create_console.assert_called_once_with(
            self._server.id, console_type='webmks'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
