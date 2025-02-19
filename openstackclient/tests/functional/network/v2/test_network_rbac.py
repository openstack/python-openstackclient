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

import uuid

from openstackclient.tests.functional.network.v2 import common


class NetworkRBACTests(common.NetworkTests):
    """Functional tests for network rbac"""

    OBJECT_ID: str
    ID: str
    HEADERS = ['ID']
    FIELDS = ['id']

    def setUp(self):
        super().setUp()

        self.NET_NAME = uuid.uuid4().hex
        self.PROJECT_NAME = uuid.uuid4().hex

        cmd_output = self.openstack(
            'network create ' + self.NET_NAME,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'network delete ' + cmd_output['id'])
        self.OBJECT_ID = cmd_output['id']

        cmd_output = self.openstack(
            'network rbac create '
            + self.OBJECT_ID
            + ' --action access_as_shared'
            + ' --target-project admin'
            + ' --type network',
            parse_output=True,
        )
        self.addCleanup(
            self.openstack, 'network rbac delete ' + cmd_output['id']
        )
        self.ID = cmd_output['id']
        self.assertEqual(self.OBJECT_ID, cmd_output['object_id'])

    def test_network_rbac_list(self):
        cmd_output = self.openstack('network rbac list', parse_output=True)
        self.assertIn(self.ID, [rbac['ID'] for rbac in cmd_output])

    def test_network_rbac_show(self):
        cmd_output = self.openstack(
            'network rbac show ' + self.ID,
            parse_output=True,
        )
        self.assertEqual(self.ID, cmd_output['id'])

    def test_network_rbac_set(self):
        project_id = self.openstack(
            'project create ' + self.PROJECT_NAME,
            parse_output=True,
        )['id']
        self.openstack(
            'network rbac set '
            + self.ID
            + ' --target-project '
            + self.PROJECT_NAME
        )
        cmd_output_rbac = self.openstack(
            'network rbac show ' + self.ID,
            parse_output=True,
        )
        self.assertEqual(project_id, cmd_output_rbac['target_project_id'])
        raw_output_project = self.openstack(
            'project delete ' + self.PROJECT_NAME
        )
        self.assertEqual('', raw_output_project)
