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

from openstackclient.tests.functional.volume.v2 import common


class TransferRequestTests(common.BaseVolumeTests):
    """Functional tests for transfer request. """

    API_VERSION = '2'

    def test_volume_transfer_request_accept(self):
        volume_name = uuid.uuid4().hex
        xfer_name = uuid.uuid4().hex

        # create a volume
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 1 ' +
            volume_name
        ))
        self.assertEqual(volume_name, cmd_output['name'])
        self.addCleanup(
            self.openstack,
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume delete ' +
            volume_name
        )
        self.wait_for_status("volume", volume_name, "available")

        # create volume transfer request for the volume
        # and get the auth_key of the new transfer request
        cmd_output = json.loads(self.openstack(
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume transfer request create -f json ' +
            ' --name ' + xfer_name + ' ' +
            volume_name
        ))
        self.assertEqual(xfer_name, cmd_output['name'])
        auth_key = cmd_output['auth_key']
        self.assertTrue(auth_key)

        # accept the volume transfer request
        cmd_output = json.loads(self.openstack(
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume transfer request accept -f json ' +
            '--auth-key ' + auth_key + ' ' +
            xfer_name
        ))
        self.assertEqual(xfer_name, cmd_output['name'])

    def test_volume_transfer_request_list_show(self):
        volume_name = uuid.uuid4().hex
        xfer_name = uuid.uuid4().hex

        # create a volume
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 1 ' +
            volume_name
        ))
        self.assertEqual(volume_name, cmd_output['name'])
        self.addCleanup(
            self.openstack,
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume delete ' +
            volume_name
        )
        self.wait_for_status("volume", volume_name, "available")

        cmd_output = json.loads(self.openstack(
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume transfer request create -f json ' +
            ' --name ' + xfer_name + ' ' +
            volume_name
        ))
        self.addCleanup(
            self.openstack,
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume transfer request delete ' +
            xfer_name
        )
        self.assertEqual(xfer_name, cmd_output['name'])
        auth_key = cmd_output['auth_key']
        self.assertTrue(auth_key)

        cmd_output = json.loads(self.openstack(
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume transfer request list -f json'
        ))
        self.assertIn(xfer_name, [req['Name'] for req in cmd_output])

        cmd_output = json.loads(self.openstack(
            '--os-volume-api-version ' + self.API_VERSION + ' ' +
            'volume transfer request show -f json ' +
            xfer_name
        ))
        self.assertEqual(xfer_name, cmd_output['name'])
