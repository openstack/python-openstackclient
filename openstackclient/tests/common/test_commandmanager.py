#   Copyright 2012-2013 OpenStack Foundation
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

from openstackclient.common import commandmanager
from openstackclient.tests import utils


class FakeCommand(object):
    @classmethod
    def load(cls):
        return cls

    def __init__(self):
        return

FAKE_CMD_ONE = FakeCommand
FAKE_CMD_TWO = FakeCommand
FAKE_CMD_ALPHA = FakeCommand
FAKE_CMD_BETA = FakeCommand


class FakeCommandManager(commandmanager.CommandManager):
    commands = {}

    def load_commands(self, namespace):
        if namespace == 'test':
            self.commands['one'] = FAKE_CMD_ONE
            self.commands['two'] = FAKE_CMD_TWO
            self.group_list.append(namespace)
        elif namespace == 'greek':
            self.commands['alpha'] = FAKE_CMD_ALPHA
            self.commands['beta'] = FAKE_CMD_BETA
            self.group_list.append(namespace)


class TestCommandManager(utils.TestCase):
    def test_add_command_group(self):
        mgr = FakeCommandManager('test')

        # Make sure add_command() still functions
        mock_cmd_one = mock.Mock()
        mgr.add_command('mock', mock_cmd_one)
        cmd_mock, name, args = mgr.find_command(['mock'])
        self.assertEqual(mock_cmd_one, cmd_mock)

        # Find a command added in initialization
        cmd_one, name, args = mgr.find_command(['one'])
        self.assertEqual(FAKE_CMD_ONE, cmd_one)

        # Load another command group
        mgr.add_command_group('greek')

        # Find a new command
        cmd_alpha, name, args = mgr.find_command(['alpha'])
        self.assertEqual(FAKE_CMD_ALPHA, cmd_alpha)

        # Ensure that the original commands were not overwritten
        cmd_two, name, args = mgr.find_command(['two'])
        self.assertEqual(FAKE_CMD_TWO, cmd_two)

    def test_get_command_groups(self):
        mgr = FakeCommandManager('test')

        # Make sure add_command() still functions
        mock_cmd_one = mock.Mock()
        mgr.add_command('mock', mock_cmd_one)
        cmd_mock, name, args = mgr.find_command(['mock'])
        self.assertEqual(mock_cmd_one, cmd_mock)

        # Load another command group
        mgr.add_command_group('greek')

        gl = mgr.get_command_groups()
        self.assertEqual(['test', 'greek'], gl)

    def test_get_command_names(self):
        mock_cmd_one = mock.Mock()
        mock_cmd_one.name = 'one'
        mock_cmd_two = mock.Mock()
        mock_cmd_two.name = 'cmd two'
        mock_pkg_resources = mock.Mock(
            return_value=[mock_cmd_one, mock_cmd_two],
        )
        with mock.patch(
            'pkg_resources.iter_entry_points',
            mock_pkg_resources,
        ) as iter_entry_points:
            mgr = commandmanager.CommandManager('test')
            assert iter_entry_points.called_once_with('test')
            cmds = mgr.get_command_names('test')
            self.assertEqual(['one', 'cmd two'], cmds)
