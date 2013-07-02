#   Copyright 2012-2013 OpenStack, LLC.
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

    def _load_commands(self, group=None):
        if not group:
            self.commands['one'] = FAKE_CMD_ONE
            self.commands['two'] = FAKE_CMD_TWO
        else:
            self.commands['alpha'] = FAKE_CMD_ALPHA
            self.commands['beta'] = FAKE_CMD_BETA


class TestCommandManager(utils.TestCase):
    def test_add_command_group(self):
        mgr = FakeCommandManager('test')

        # Make sure add_command() still functions
        mock_cmd_one = mock.Mock()
        mgr.add_command('mock', mock_cmd_one)
        cmd_mock, name, args = mgr.find_command(['mock'])
        self.assertEqual(cmd_mock, mock_cmd_one)

        # Find a command added in initialization
        cmd_one, name, args = mgr.find_command(['one'])
        self.assertEqual(cmd_one, FAKE_CMD_ONE)

        # Load another command group
        mgr.add_command_group('latin')

        # Find a new command
        cmd_alpha, name, args = mgr.find_command(['alpha'])
        self.assertEqual(cmd_alpha, FAKE_CMD_ALPHA)

        # Ensure that the original commands were not overwritten
        cmd_two, name, args = mgr.find_command(['two'])
        self.assertEqual(cmd_two, FAKE_CMD_TWO)
