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
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils


# NOTE(dtroyer): module_1 must match the version list filter (not --all)
#                currently == '*client*'
module_name_1 = 'fakeclient'
module_version_1 = '0.1.2'

module_name_2 = 'zlib'
module_version_2 = '1.1'

# module_3 match openstacksdk
module_name_3 = 'openstack'
module_version_3 = '0.9.13'

# module_4 match sub module of fakeclient
module_name_4 = 'fakeclient.submodule'
module_version_4 = '0.2.2'

# module_5 match private module
module_name_5 = '_private_module.lib'
module_version_5 = '0.0.1'

MODULES = {
    module_name_1: fakes.FakeModule(module_name_1, module_version_1),
    module_name_2: fakes.FakeModule(module_name_2, module_version_2),
    module_name_3: fakes.FakeModule(module_name_3, module_version_3),
    module_name_4: fakes.FakeModule(module_name_4, module_version_4),
    module_name_5: fakes.FakeModule(module_name_5, module_version_5),
}


class TestCommandList(utils.TestCommand):

    def setUp(self):
        super(TestCommandList, self).setUp()

        self.app.command_manager = mock.Mock()
        self.app.command_manager.get_command_groups.return_value = [
            'openstack.common'
        ]
        self.app.command_manager.get_command_names.return_value = [
            'limits show\nextension list'
        ]

        # Get the command object to test
        self.cmd = osc_module.ListCommand(self.app, None)

    def test_command_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # TODO(bapalm): Adjust this when cliff properly supports
        # handling the detection rather than using the hard-code below.
        collist = ('Command Group', 'Commands')
        self.assertEqual(collist, columns)
        datalist = ((
            'openstack.common',
            'limits show\nextension list'
        ),)

        self.assertEqual(datalist, tuple(data))

    def test_command_list_with_group_not_found(self):
        arglist = [
            '--group', 'not_exist',
        ]
        verifylist = [
            ('group', 'not_exist'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Command Group', 'Commands')
        self.assertEqual(collist, columns)
        self.assertEqual([], data)

    def test_command_list_with_group(self):
        arglist = [
            '--group', 'common',
        ]
        verifylist = [
            ('group', 'common'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Command Group', 'Commands')
        self.assertEqual(collist, columns)
        datalist = ((
            'openstack.common',
            'limits show\nextension list'
        ),)

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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Output xxxclient and openstacksdk, but not regular module, like: zlib
        self.assertIn(module_name_1, columns)
        self.assertIn(module_version_1, data)
        self.assertNotIn(module_name_2, columns)
        self.assertNotIn(module_version_2, data)
        self.assertIn(module_name_3, columns)
        self.assertIn(module_version_3, data)
        # Filter sub and private modules
        self.assertNotIn(module_name_4, columns)
        self.assertNotIn(module_version_4, data)
        self.assertNotIn(module_name_5, columns)
        self.assertNotIn(module_version_5, data)

    def test_module_list_all(self):
        arglist = [
            '--all',
        ]
        verifylist = [
            ('all', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Output xxxclient, openstacksdk and regular module, like: zlib
        self.assertIn(module_name_1, columns)
        self.assertIn(module_version_1, data)
        self.assertIn(module_name_2, columns)
        self.assertIn(module_version_2, data)
        self.assertIn(module_name_3, columns)
        self.assertIn(module_version_3, data)
        # Filter sub and private modules
        self.assertNotIn(module_name_4, columns)
        self.assertNotIn(module_version_4, data)
        self.assertNotIn(module_name_5, columns)
        self.assertNotIn(module_version_5, data)
