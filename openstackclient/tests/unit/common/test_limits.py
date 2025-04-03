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

from openstackclient.common import limits
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes


class TestComputeLimits(compute_fakes.TestComputev2):
    absolute_columns = ['Name', 'Value']
    rate_columns = ["Verb", "URI", "Value", "Remain", "Unit", "Next Available"]

    def setUp(self):
        super().setUp()
        self.app.client_manager.volume_endpoint_enabled = False

        self.fake_limits = compute_fakes.create_limits()

        self.absolute_data = [
            ('floating_ips', 10),
            ('floating_ips_used', 0),
            ('image_meta', 128),
            ('instances', 10),
            ('instances_used', 0),
            ('keypairs', 100),
            ('max_image_meta', 128),
            ('max_security_group_rules', 20),
            ('max_security_groups', 10),
            ('max_server_group_members', 10),
            ('max_server_groups', 10),
            ('max_server_meta', 128),
            ('max_total_cores', 20),
            ('max_total_floating_ips', 10),
            ('max_total_instances', 10),
            ('max_total_keypairs', 100),
            ('max_total_ram_size', 51200),
            ('personality', 5),
            ('personality_size', 10240),
            ('security_group_rules', 20),
            ('security_groups', 10),
            ('security_groups_used', 0),
            ('server_group_members', 10),
            ('server_groups', 10),
            ('server_groups_used', 0),
            ('server_meta', 128),
            ('total_cores', 20),
            ('total_cores_used', 0),
            ('total_floating_ips_used', 0),
            ('total_instances_used', 0),
            ('total_ram', 51200),
            ('total_ram_used', 0),
            ('total_security_groups_used', 0),
            ('total_server_groups_used', 0),
        ]
        self.rate_data = [
            ('POST', '*', 10, 2, 'MINUTE', '2011-12-15T22:42:45Z'),
            ('PUT', '*', 10, 2, 'MINUTE', '2011-12-15T22:42:45Z'),
            ('DELETE', '*', 100, 100, 'MINUTE', '2011-12-15T22:42:45Z'),
        ]

        self.compute_client.get_limits.return_value = self.fake_limits

    def test_compute_show_absolute(self):
        arglist = ['--absolute']
        verifylist = [('is_absolute', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.absolute_columns, columns)
        self.assertEqual(self.absolute_data, data)

    def test_compute_show_rate(self):
        arglist = ['--rate']
        verifylist = [('is_rate', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.rate_columns, columns)
        self.assertEqual(self.rate_data, data)


class TestVolumeLimits(volume_fakes.TestVolume):
    absolute_columns = ['Name', 'Value']
    rate_columns = ["Verb", "URI", "Value", "Remain", "Unit", "Next Available"]

    def setUp(self):
        super().setUp()
        self.app.client_manager.compute_endpoint_enabled = False

        self.fake_limits = volume_fakes.create_limits()

        self.absolute_data = [
            ('max_total_backup_gigabytes', 1000),
            ('max_total_backups', 10),
            ('max_total_snapshots', 10),
            ('max_total_volume_gigabytes', 1000),
            ('max_total_volumes', 10),
            ('total_backup_gigabytes_used', 0),
            ('total_backups_used', 0),
            ('total_gigabytes_used', 35),
            ('total_snapshots_used', 1),
            ('total_volumes_used', 4),
        ]
        self.rate_data = [
            ('POST', '*', 10, 2, 'MINUTE', '2011-12-15T22:42:45Z'),
            ('PUT', '*', 10, 2, 'MINUTE', '2011-12-15T22:42:45Z'),
            ('DELETE', '*', 100, 100, 'MINUTE', '2011-12-15T22:42:45Z'),
        ]

        self.volume_sdk_client.get_limits.return_value = self.fake_limits

    def test_volume_show_absolute(self):
        arglist = ['--absolute']
        verifylist = [('is_absolute', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.absolute_columns, columns)
        self.assertEqual(self.absolute_data, data)

    def test_volume_show_rate(self):
        arglist = ['--rate']
        verifylist = [('is_rate', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.rate_columns, columns)
        self.assertEqual(self.rate_data, data)
