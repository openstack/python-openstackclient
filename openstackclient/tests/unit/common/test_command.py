#   Copyright 2016 NEC Corporation
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

import mock

from osc_lib import exceptions

from openstackclient.common import command
from openstackclient.tests.unit import fakes as test_fakes
from openstackclient.tests.unit import utils as test_utils


class FakeCommand(command.Command):

    def take_action(self, parsed_args):
        pass


class TestCommand(test_utils.TestCase):

    def test_command_has_logger(self):
        cmd = FakeCommand(mock.Mock(), mock.Mock())
        self.assertTrue(hasattr(cmd, 'log'))
        self.assertEqual('openstackclient.tests.unit.common.test_command.'
                         'FakeCommand', cmd.log.name)

    def test_validate_os_beta_command_enabled(self):
        cmd = FakeCommand(mock.Mock(), mock.Mock())
        cmd.app = mock.Mock()
        cmd.app.options = test_fakes.FakeOptions()

        # No exception is raised when enabled.
        cmd.app.options.os_beta_command = True
        cmd.validate_os_beta_command_enabled()

        cmd.app.options.os_beta_command = False
        self.assertRaises(exceptions.CommandError,
                          cmd.validate_os_beta_command_enabled)
