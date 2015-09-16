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

import os
import uuid

from functional.common import test


class ImageTests(test.TestCase):
    """Functional tests for image. """

    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        os.environ['OS_IMAGE_API_VERSION'] = '1'
        opts = cls.get_show_opts(cls.FIELDS)
        raw_output = cls.openstack('image create ' + cls.NAME + opts)
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        # Rename test
        opts = cls.get_show_opts(cls.FIELDS)
        raw_output = cls.openstack(
            'image set --name ' + cls.OTHER_NAME + ' ' + cls.NAME + opts)
        cls.assertOutput(cls.OTHER_NAME + "\n", raw_output)
        # Delete test
        raw_output = cls.openstack('image delete ' + cls.OTHER_NAME)
        cls.assertOutput('', raw_output)

    def test_image_list(self):
        opts = self.get_list_opts(self.HEADERS)
        raw_output = self.openstack('image list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_image_show(self):
        opts = self.get_show_opts(self.FIELDS)
        raw_output = self.openstack('image show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)

    def test_image_set(self):
        opts = self.get_show_opts([
            "disk_format", "is_public", "min_disk", "min_ram", "name"])
        raw_output = self.openstack('image set --min-disk 4 --min-ram 5 ' +
                                    '--disk-format qcow2  --public ' +
                                    self.NAME + opts)
        self.assertEqual("qcow2\nTrue\n4\n5\n" + self.NAME + '\n', raw_output)

    def test_image_metadata(self):
        opts = self.get_show_opts(["name", "properties"])
        raw_output = self.openstack(
            'image set --property a=b --property c=d ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\na='b', c='d'\n", raw_output)
