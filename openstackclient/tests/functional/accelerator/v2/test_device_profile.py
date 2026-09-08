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

import json
import uuid

from openstackclient.tests.functional.accelerator.v2 import common


class TestDeviceProfile(common.AcceleratorTests):
    """Functional tests for accelerator device profile commands."""

    def test_device_profile(self):
        name = uuid.uuid4().hex
        groups = [
            {
                'resources:CUSTOM_ACCELERATOR_FPGA': '1',
                'trait:CUSTOM_FPGA_INTEL': 'required',
            }
        ]

        # create
        cmd_output = self.openstack(
            'accelerator device profile create '
            + name
            + ' '
            + "'"
            + json.dumps(groups)
            + "'",
            parse_output=True,
        )
        dp_uuid = cmd_output['uuid']
        self.addCleanup(
            self.openstack,
            'accelerator device profile delete ' + dp_uuid,
            fail_ok=True,
        )
        self.assertEqual(name, cmd_output['name'])
        self.assertEqual(groups, cmd_output['groups'])

        # show
        cmd_output = self.openstack(
            'accelerator device profile show ' + dp_uuid,
            parse_output=True,
        )
        self.assertEqual(name, cmd_output['name'])
        self.assertEqual(groups, cmd_output['groups'])

        # list
        cmd_output = self.openstack(
            'accelerator device profile list', parse_output=True
        )
        names = [dp['name'] for dp in cmd_output]
        self.assertIn(name, names)

        # list (long)
        cmd_output = self.openstack(
            'accelerator device profile list --long', parse_output=True
        )
        names = [dp['name'] for dp in cmd_output]
        self.assertIn(name, names)
        dp = next(dp for dp in cmd_output if dp['name'] == name)
        self.assertIn('created_at', dp)
        self.assertIn('updated_at', dp)

        # delete
        self.openstack('accelerator device profile delete ' + dp_uuid)

        cmd_output = self.openstack(
            'accelerator device profile list', parse_output=True
        )
        uuids = [dp['uuid'] for dp in cmd_output]
        self.assertNotIn(dp_uuid, uuids)
