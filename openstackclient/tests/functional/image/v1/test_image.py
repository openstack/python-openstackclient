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

from openstackclient.tests.functional.image import base


class ImageTests(base.BaseImageTests):
    """Functional tests for Image commands"""

    def setUp(self):
        super(ImageTests, self).setUp()
        if not self.haz_v1_api:
            self.skipTest('No Image v1 API present')

        self.name = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            '--os-image-api-version 1 '
            'image create -f json ' +
            self.name
        ))
        self.image_id = json_output["id"]
        self.assertOutput(self.name, json_output['name'])

        ver_fixture = fixtures.EnvironmentVariable(
            'OS_IMAGE_API_VERSION', '1'
        )
        self.useFixture(ver_fixture)

    def tearDown(self):
        try:
            self.openstack(
                '--os-image-api-version 1 '
                'image delete ' +
                self.image_id
            )
        finally:
            super(ImageTests, self).tearDown()

    def test_image_list(self):
        json_output = json.loads(self.openstack(
            'image list -f json '
        ))
        self.assertIn(
            self.name,
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
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
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
            self.name
        )
        json_output = json.loads(self.openstack(
            'image show -f json ' +
            self.name
        ))
        self.assertEqual(
            {'a': 'b', 'c': 'd'},
            json_output["properties"],
        )
