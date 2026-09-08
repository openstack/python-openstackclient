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

from openstackclient.tests.functional.accelerator.v2 import common


class TestDevice(common.AcceleratorTests):
    """Functional tests for accelerator device commands."""

    def test_device(self):
        # list
        cmd_output = self.openstack(
            'accelerator device list', parse_output=True
        )
        self.assertIsInstance(cmd_output, list)
        if not cmd_output:
            self.skipTest("No devices available to test")

        self.assertIn('uuid', cmd_output[0])
        self.assertIn('type', cmd_output[0])
        self.assertIn('vendor', cmd_output[0])

        # list (long)
        cmd_output = self.openstack(
            'accelerator device list --long', parse_output=True
        )
        self.assertIn('model', cmd_output[0])
        self.assertIn('vendor_board_info', cmd_output[0])

        # show
        device_uuid = cmd_output[0]['uuid']
        cmd_output = self.openstack(
            'accelerator device show ' + device_uuid, parse_output=True
        )
        self.assertEqual(device_uuid, cmd_output['uuid'])
        self.assertIn('type', cmd_output)
        self.assertIn('vendor', cmd_output)
        self.assertIn('hostname', cmd_output)
