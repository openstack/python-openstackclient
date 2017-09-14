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


class NetworkRBACTests(common.NetworkTests):
    """Functional tests for network rbac"""
    OBJECT_ID = None
    ID = None
    HEADERS = ['ID']
    FIELDS = ['id']

    def setUp(self):
        super(NetworkRBACTests, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

        self.NET_NAME = uuid.uuid4().hex
        self.PROJECT_NAME = uuid.uuid4().hex

        cmd_output = json.loads(self.openstack(
            'network create -f json ' + self.NET_NAME
        ))
        self.addCleanup(self.openstack,
                        'network delete ' + cmd_output['id'])
        self.OBJECT_ID = cmd_output['id']

        cmd_output = json.loads(self.openstack(
            'network rbac create -f json ' +
            self.OBJECT_ID +
            ' --action access_as_shared' +
            ' --target-project admin' +
            ' --type network'
        ))
        self.addCleanup(self.openstack,
                        'network rbac delete ' + cmd_output['id'])
        self.ID = cmd_output['id']
        self.assertEqual(self.OBJECT_ID, cmd_output['object_id'])

    def test_network_rbac_list(self):
        cmd_output = json.loads(self.openstack('network rbac list -f json'))
        self.assertIn(self.ID, [rbac['ID'] for rbac in cmd_output])

    def test_network_rbac_show(self):
        cmd_output = json.loads(self.openstack(
            'network rbac show -f json ' + self.ID))
        self.assertEqual(self.ID, cmd_output['id'])

    def test_network_rbac_set(self):
        project_id = json.loads(self.openstack(
            'project create -f json ' + self.PROJECT_NAME))['id']
        self.openstack('network rbac set ' + self.ID +
                       ' --target-project ' + self.PROJECT_NAME)
        cmd_output_rbac = json.loads(self.openstack(
            'network rbac show -f json ' + self.ID))
        self.assertEqual(project_id, cmd_output_rbac['target_project_id'])
        raw_output_project = self.openstack(
            'project delete ' + self.PROJECT_NAME)
        self.assertEqual('', raw_output_project)
