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


class TestAcceleratorRequest(common.AcceleratorTests):
    """Functional tests for accelerator ARQ commands."""

    def setUp(self):
        super().setUp()
        self.dp_name = uuid.uuid4().hex
        groups = [{'resources:CUSTOM_ACCELERATOR_FPGA': '1'}]
        cmd_output = self.openstack(
            'accelerator device profile create '
            + self.dp_name
            + ' '
            + "'"
            + json.dumps(groups)
            + "'",
            parse_output=True,
        )
        self.dp_uuid = cmd_output['uuid']
        self.addCleanup(
            self.openstack,
            'accelerator device profile delete ' + self.dp_uuid,
            fail_ok=True,
        )

    def test_arq(self):
        # create
        cmd_output = self.openstack(
            'accelerator arq create ' + self.dp_name, parse_output=True
        )
        arq_uuid = cmd_output['uuid']
        self.addCleanup(
            self.openstack,
            'accelerator arq delete ' + arq_uuid,
            fail_ok=True,
        )
        self.assertEqual(self.dp_name, cmd_output['device_profile_name'])

        # show
        cmd_output = self.openstack(
            'accelerator arq show ' + arq_uuid, parse_output=True
        )
        self.assertEqual(arq_uuid, cmd_output['uuid'])
        self.assertEqual(self.dp_name, cmd_output['device_profile_name'])

        # list
        cmd_output = self.openstack('accelerator arq list', parse_output=True)
        uuids = [arq['uuid'] for arq in cmd_output]
        self.assertIn(arq_uuid, uuids)

        # list (long)
        cmd_output = self.openstack(
            'accelerator arq list --long', parse_output=True
        )
        uuids = [arq['uuid'] for arq in cmd_output]
        self.assertIn(arq_uuid, uuids)
        arq = next(a for a in cmd_output if a['uuid'] == arq_uuid)
        self.assertIn('device_rp_uuid', arq)
        self.assertIn('hostname', arq)

        # delete
        self.openstack('accelerator arq delete ' + arq_uuid)

        cmd_output = self.openstack('accelerator arq list', parse_output=True)
        uuids = [arq['uuid'] for arq in cmd_output]
        self.assertNotIn(arq_uuid, uuids)
