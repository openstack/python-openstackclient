#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

import fixtures

from openstackclient.tests.functional import base


class HelpTests(base.TestCase):
    """Functional tests for openstackclient help output."""

    SERVER_COMMANDS = [
        ('server add security group', 'Add security group to server'),
        ('server add volume', 'Add volume to server'),
        ('server backup create', 'Create a server backup image'),
        ('server create', 'Create a new server'),
        ('server delete', 'Delete server(s)'),
        ('server dump create', 'Create a dump file in server(s)'),
        ('server image create',
         'Create a new server disk image from an existing server'),
        ('server list', 'List servers'),
        ('server lock',
         'Lock server(s). '
         'A non-admin user will not be able to execute actions'),
        ('server migrate', 'Migrate server to different host'),
        ('server pause', 'Pause server(s)'),
        ('server reboot', 'Perform a hard or soft server reboot'),
        ('server rebuild', 'Rebuild server'),
        ('server remove security group', 'Remove security group from server'),
        ('server remove volume', 'Remove volume from server'),
        ('server rescue', 'Put server in rescue mode'),
        ('server resize', 'Scale server to a new flavor'),
        ('server resume', 'Resume server(s)'),
        ('server set', 'Set server properties'),
        ('server shelve', 'Shelve server(s)'),
        ('server show', 'Show server details'),
        ('server ssh', 'SSH to server'),
        ('server start', 'Start server(s).'),
        ('server stop', 'Stop server(s).'),
        ('server suspend', 'Suspend server(s)'),
        ('server unlock', 'Unlock server(s)'),
        ('server unpause', 'Unpause server(s)'),
        ('server unrescue', 'Restore server from rescue mode'),
        ('server unset', 'Unset server properties'),
        ('server unshelve', 'Unshelve server(s)')
    ]

    def test_server_commands_main_help(self):
        """Check server commands in main help message."""
        raw_output = self.openstack('help')
        for command, description in self.SERVER_COMMANDS:
            msg = 'Command: %s not found in help output:\n%s' % (
                command, raw_output)
            self.assertIn(command, raw_output, msg)
            msg = 'Description: %s not found in help output:\n%s' % (
                description, raw_output)
            self.assertIn(description, raw_output, msg)

    def test_server_only_help(self):
        """Check list of server-related commands only."""
        raw_output = self.openstack('help server')
        for command in [row[0] for row in self.SERVER_COMMANDS]:
            self.assertIn(command, raw_output)

    def test_networking_commands_help(self):
        """Check networking related commands in help message."""
        raw_output = self.openstack('help network list')
        self.assertIn('List networks', raw_output)
        raw_output = self.openstack('network create --help')
        self.assertIn('Create new network', raw_output)

    def test_commands_help_no_auth(self):
        """Check help commands without auth info."""
        # Pop all auth info. os.environ will be changed in loop, so do not
        # replace os.environ.keys() to os.environ
        for key in os.environ.keys():
            if key.startswith('OS_'):
                self.useFixture(fixtures.EnvironmentVariable(key, None))

        raw_output = self.openstack('help')
        self.assertIn('usage: openstack', raw_output)
        raw_output = self.openstack('--help')
        self.assertIn('usage: openstack', raw_output)

        raw_output = self.openstack('help network list')
        self.assertIn('List networks', raw_output)
        raw_output = self.openstack('network list --help')
        self.assertIn('List networks', raw_output)

        raw_output = self.openstack('help volume list')
        self.assertIn('List volumes', raw_output)
        raw_output = self.openstack('volume list --help')
        self.assertIn('List volumes', raw_output)

        raw_output = self.openstack('help server list')
        self.assertIn('List servers', raw_output)
        raw_output = self.openstack('server list --help')
        self.assertIn('List servers', raw_output)

        raw_output = self.openstack('help user list')
        self.assertIn('List users', raw_output)
        raw_output = self.openstack('user list --help')
        self.assertIn('List users', raw_output)

        raw_output = self.openstack('help image list')
        self.assertIn('List available images', raw_output)
        raw_output = self.openstack('image list --help')
        self.assertIn('List available images', raw_output)

        raw_output = self.openstack('help container list')
        self.assertIn('List containers', raw_output)
        raw_output = self.openstack('container list --help')
        self.assertIn('List containers', raw_output)
