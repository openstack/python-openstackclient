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

import fixtures

from openstackclient.tests.functional import base


class ImageTests(base.TestCase):
    """Functional tests for image. """

    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(ImageTests, cls).setUpClass()
        json_output = json.loads(cls.openstack(
            '--os-image-api-version 1 '
            'image create -f json ' +
            cls.NAME
        ))
        cls.image_id = json_output["id"]
        cls.assertOutput(cls.NAME, json_output['name'])

    @classmethod
    def tearDownClass(cls):
        try:
            cls.openstack(
                '--os-image-api-version 1 '
                'image delete ' +
                cls.image_id
            )
        finally:
            super(ImageTests, cls).tearDownClass()

    def setUp(self):
        super(ImageTests, self).setUp()
        ver_fixture = fixtures.EnvironmentVariable(
            'OS_IMAGE_API_VERSION', '1'
        )
        self.useFixture(ver_fixture)

    def test_image_list(self):
        json_output = json.loads(self.openstack(
            'image list -f json '
        ))
        self.assertIn(
            self.NAME,
            [img['Name'] for img in json_output]
        )

    def test_image_attributes(self):
        """Test set, unset, show on attributes, tags and properties"""

        # Test explicit attributes
        self.openstack(
            'image set ' +
            '--min-disk 4 ' +
            '--min-ram 5 ' +
            '--disk-format qcow2 ' +
            '--public ' +
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
        ))
        self.assertEqual(
            4,
            json_output["min_disk"],
        )
        self.assertEqual(
            5,
            json_output["min_ram"],
        )
        self.assertEqual(
            'qcow2',
            json_output['disk_format'],
        )
        self.assertTrue(
            json_output["is_public"],
        )

        # Test properties
        self.openstack(
            'image set ' +
            '--property a=b ' +
            '--property c=d ' +
            '--public ' +
            self.NAME
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.NAME
        ))
        self.assertEqual(
            {'a': 'b', 'c': 'd'},
            json_output["properties"],
        )
