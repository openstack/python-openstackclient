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

from openstackclient.tests.functional.network.v2 import common


class SecurityGroupTests(common.NetworkTests):
    """Functional tests for security group"""

    def setUp(self):
        super(SecurityGroupTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

        self.NAME = uuid.uuid4().hex
        self.OTHER_NAME = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'security group create -f json ' +
            self.NAME
        ))
        self.addCleanup(self.openstack,
                        'security group delete ' + cmd_output['id'])
        self.assertEqual(self.NAME, cmd_output['name'])

    def test_security_group_list(self):
        cmd_output = json.loads(self.openstack('security group list -f json'))
        self.assertIn(self.NAME, [sg['Name'] for sg in cmd_output])

    def test_security_group_set(self):
        other_name = uuid.uuid4().hex
        raw_output = self.openstack(
            'security group set --description NSA --name ' +
            other_name + ' ' + self.NAME
        )
        self.assertEqual('', raw_output)

        cmd_output = json.loads(self.openstack(
            'security group show -f json ' + other_name))
        self.assertEqual('NSA', cmd_output['description'])

    def test_security_group_show(self):
        cmd_output = json.loads(self.openstack(
            'security group show -f json ' + self.NAME))
        self.assertEqual(self.NAME, cmd_output['name'])
