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
import os
import uuid

from openstackclient.tests.functional import base


class ImageTests(base.TestCase):
    """Functional tests for image. """

    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        os.environ['OS_IMAGE_API_VERSION'] = '1'
        cmd_output = json.loads(cls.openstack(
            'image create -f json ' + cls.NAME))
        cls.assertOutput(cls.NAME, cmd_output['name'])

    @classmethod
    def tearDownClass(cls):
        # Rename test
        raw_output = cls.openstack('image set --name ' + cls.OTHER_NAME + ' '
                                   + cls.NAME)
        cls.assertOutput('', raw_output)
        # Delete test
        raw_output = cls.openstack('image delete ' + cls.OTHER_NAME)
        cls.assertOutput('', raw_output)

    def test_image_list(self):
        cmd_output = json.loads(self.openstack('image list -f json'))
        col_names = [img['Name'] for img in cmd_output]
        self.assertIn(self.NAME, col_names)

    def test_image_show(self):
        cmd_output = json.loads(self.openstack(
            'image show -f json ' + self.NAME))
        self.assertEqual(self.NAME, cmd_output['name'])

    def test_image_set(self):
        self.openstack('image set --min-disk 4 --min-ram 5 ' +
                       '--disk-format qcow2 --public ' + self.NAME)
        cmd_output = json.loads(self.openstack(
            'image show -f json ' + self.NAME))
        self.assertEqual(self.NAME, cmd_output['name'])
        self.assertEqual(4, cmd_output['min_disk'])
        self.assertEqual(5, cmd_output['min_ram'])
        self.assertEqual('qcow2', cmd_output['disk_format'])
        self.assertEqual(True, cmd_output['is_public'])

    def test_image_metadata(self):
        self.openstack('image set --property a=b --property c=d ' + self.NAME)
        cmd_output = json.loads(self.openstack(
            'image show -f json ' + self.NAME))
        self.assertEqual(self.NAME, cmd_output['name'])
        self.assertEqual("a='b', c='d'", cmd_output['properties'])
