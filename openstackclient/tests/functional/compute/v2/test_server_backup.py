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

import uuid

from openstackclient.tests.functional.compute.v2 import common


class TestServerBackup(common.ComputeTestCase):
    """Functional tests for server backup create"""

    def test_server_backup_defaults(self):
        """Test server backup create with default options"""
        cmd_output = self.server_create()
        server_name = cmd_output['name']

        image = self.openstack(
            f'server backup create --wait {server_name}',
            parse_output=True,
        )
        image_id = image['id']
        self.addCleanup(self.openstack, f'image delete {image_id}')

        self.assertIsNotNone(image_id)
        self.assertIsNotNone(image.get('name'))
        self.assertEqual(server_name, image['name'])
        self.assertEqual('active', image['status'])

    def test_server_backup_options(self):
        """Test server backup create with explicit name, type, and rotate"""
        cmd_output = self.server_create()
        server_name = cmd_output['name']
        backup_name = uuid.uuid4().hex

        image = self.openstack(
            f'server backup create'
            f' --name {backup_name}'
            f' --type daily'
            f' --rotate 2'
            f' --wait'
            f' {server_name}',
            parse_output=True,
        )
        image_id = image['id']
        self.addCleanup(self.openstack, f'image delete {image_id}')

        self.assertEqual(backup_name, image['name'])
        self.assertEqual('active', image['status'])

    def test_server_backup_rotate(self):
        """Regression test for bug #2110035: second backup with same name

        Prior to the fix, the second backup create with the same name would
        fail because the rotate parameter was not passed correctly to Nova.
        """
        cmd_output = self.server_create()
        server_name = cmd_output['name']
        backup_name = uuid.uuid4().hex

        image1 = self.openstack(
            f'server backup create'
            f' --name {backup_name}'
            f' --rotate 2'
            f' --wait'
            f' {server_name}',
            parse_output=True,
        )
        image1_id = image1['id']
        self.addCleanup(
            self.openstack, f'image delete {image1_id}', fail_ok=True
        )

        image2 = self.openstack(
            f'server backup create'
            f' --name {backup_name}'
            f' --rotate 2'
            f' --wait'
            f' {server_name}',
            parse_output=True,
        )
        image2_id = image2['id']
        self.addCleanup(
            self.openstack, f'image delete {image2_id}', fail_ok=True
        )

        self.assertEqual('active', image1['status'])
        self.assertEqual('active', image2['status'])
