#   Copyright 2013 Nebula Inc.
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

"""Test module module"""

import mock

from openstackclient.common import module as osc_module
from openstackclient.tests import fakes
from openstackclient.tests import utils


# NOTE(dtroyer): module_1 must match the version list filter (not --all)
#                currently == '*client*'
module_name_1 = 'fakeclient'
module_version_1 = '0.1.2'
MODULE_1 = {
    '__version__': module_version_1,
}

module_name_2 = 'zlib'
module_version_2 = '1.1'
MODULE_2 = {
    '__version__': module_version_2,
}

MODULES = {
    module_name_1: fakes.FakeModule(module_name_1, module_version_1),
    module_name_2: fakes.FakeModule(module_name_2, module_version_2),
}


class TestCommandList(utils.TestCommand):

    def setUp(self):
        super(TestCommandList, self).setUp()

        self.app.command_manager = mock.Mock()
        self.app.command_manager.get_command_groups.return_value = ['test']
        self.app.command_manager.get_command_names.return_value = [
            'one',
            'cmd two',
        ]

        # Get the command object to test
        self.cmd = osc_module.ListCommand(self.app, None)

    def test_command_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Command Group', 'Commands')
        self.assertEqual(collist, columns)
        datalist = ((
            'test',
            ['one', 'cmd two'],
        ), )
        self.assertEqual(datalist, tuple(data))


@mock.patch.dict(
    'openstackclient.common.module.sys.modules',
    values=MODULES,
    clear=True,
)
class TestModuleList(utils.TestCommand):

    def setUp(self):
        super(TestModuleList, self).setUp()

        # Get the command object to test
        self.cmd = osc_module.ListModule(self.app, None)

    def test_module_list_no_options(self):
        arglist = []
        verifylist = [
            ('all', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Additional modules may be present, just check our additions
        self.assertTrue(module_name_1 in columns)
        self.assertTrue(module_version_1 in data)

    def test_module_list_all(self):
        arglist = [
            '--all',
        ]
        verifylist = [
            ('all', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Additional modules may be present, just check our additions
        self.assertTrue(module_name_1 in columns)
        self.assertTrue(module_name_2 in columns)
        self.assertTrue(module_version_1 in data)
        self.assertTrue(module_version_2 in data)
