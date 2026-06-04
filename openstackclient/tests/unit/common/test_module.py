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

"""Test module module"""

import sys
from unittest import mock

from openstackclient.common import module as osc_module
from openstackclient.tests.unit import utils


class FakeModule:
    def __init__(self, name):
        self.name = name


# NOTE(dtroyer): module_1 must match the version list filter (not --all)
#                currently == '*client*'
module_name_1 = 'fakeclient'
package_name_1 = 'python-fakeclient'
package_version_1 = '0.1.2'

# module_2 match openstacksdk
module_name_2 = 'openstack'
package_name_2 = 'openstacksdk'
package_version_2 = '0.9.13'

# module_3 match sub module of fakeclient
module_name_3 = 'fakeclient.submodule'
package_name_3 = 'python-fakeclient'
package_version_3 = '0.2.2'

# module_4 match non-client package
module_name_4 = 'requests'
package_name_4 = 'requests'
package_version_4 = '2.34.2'

# module_5 match private module
module_name_5 = '_private_module.lib'

MODULES = {
    'sys': sys,
    module_name_1: FakeModule(module_name_1),
    module_name_2: FakeModule(module_name_2),
    module_name_3: FakeModule(module_name_3),
    module_name_4: FakeModule(module_name_4),
    module_name_5: FakeModule(module_name_5),
}
PACKAGES = {
    module_name_1: [package_name_1],
    module_name_2: [package_name_2],
    module_name_3: [package_name_3],
    module_name_4: [package_name_4],
}


def fake_metadata_version(package):
    if package == package_name_1:
        return package_version_1
    if package == package_name_2:
        return package_version_2
    if package == package_name_3:
        return package_version_3
    if package == package_name_4:
        return package_version_4

    raise Exception('unrecognised package')


class TestCommandList(utils.TestCommand):
    def setUp(self):
        super().setUp()

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
        datalist = (('openstack.common', 'limits show\nextension list'),)

        self.assertEqual(datalist, tuple(data))

    def test_command_list_with_group_not_found(self):
        arglist = [
            '--group',
            'not_exist',
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
            '--group',
            'common',
        ]
        verifylist = [
            ('group', 'common'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Command Group', 'Commands')
        self.assertEqual(collist, columns)
        datalist = (('openstack.common', 'limits show\nextension list'),)

        self.assertEqual(datalist, tuple(data))


class TestModuleList(utils.TestCommand):
    def setUp(self):
        super().setUp()

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
        with (
            mock.patch(
                'openstackclient.common.module.importlib.metadata.packages_distributions',
                return_value=PACKAGES,
            ),
            mock.patch(
                'openstackclient.common.module.importlib.metadata.version',
                side_effect=fake_metadata_version,
            ),
            mock.patch.dict(
                'openstackclient.common.module.sys.modules',
                values=MODULES,
                clear=True,
            ),
        ):
            columns, data = self.cmd.take_action(parsed_args)

        # Output xxxclient and openstacksdk, but not regular module, like: zlib
        self.assertIn(module_name_1, columns)
        self.assertIn(package_version_1, data)
        self.assertIn(module_name_2, columns)
        self.assertIn(package_version_2, data)
        # Filter sub and private modules
        self.assertNotIn(module_name_3, columns)
        self.assertNotIn(module_name_5, columns)

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
        with (
            mock.patch(
                'openstackclient.common.module.importlib.metadata.packages_distributions',
                return_value=PACKAGES,
            ),
            mock.patch(
                'openstackclient.common.module.importlib.metadata.version',
                side_effect=fake_metadata_version,
            ),
            mock.patch.dict(
                'openstackclient.common.module.sys.modules',
                values=MODULES,
                clear=True,
            ),
        ):
            columns, data = self.cmd.take_action(parsed_args)

        # Output xxxclient, openstacksdk and regular modules like requests
        self.assertIn(module_name_1, columns)
        self.assertIn(package_version_1, data)
        self.assertIn(module_name_2, columns)
        self.assertIn(package_version_2, data)
        self.assertIn(module_name_4, columns)
        self.assertIn(package_version_4, data)
        # Filter sub and private modules
        self.assertNotIn(module_name_3, columns)
        self.assertNotIn(module_name_5, columns)
