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

import fixtures

from openstackclient.tests.functional.image import base


class ImageTests(base.BaseImageTests):
    """Functional tests for Image commands"""

    def setUp(self):
        super().setUp()

        if not self.haz_v1_api:
            self.skipTest('No Image v1 API present')

        ver_fixture = fixtures.EnvironmentVariable('OS_IMAGE_API_VERSION', '1')
        self.useFixture(ver_fixture)

        self.name = uuid.uuid4().hex
        output = self.openstack(
            'image create ' + self.name,
            parse_output=True,
        )
        self.image_id = output["id"]
        self.assertOutput(self.name, output['name'])

    def tearDown(self):
        try:
            self.openstack('image delete ' + self.image_id)
        finally:
            super().tearDown()

    def test_image_list(self):
        output = self.openstack('image list')
        self.assertIn(self.name, [img['Name'] for img in output])

    def test_image_attributes(self):
        """Test set, unset, show on attributes, tags and properties"""

        # Test explicit attributes
        self.openstack(
            'image set '
            + '--min-disk 4 '
            + '--min-ram 5 '
            + '--disk-format qcow2 '
            + '--public '
            + self.name
        )
        output = self.openstack(
            'image show ' + self.name,
            parse_output=True,
        )
        self.assertEqual(
            4,
            output["min_disk"],
        )
        self.assertEqual(
            5,
            output["min_ram"],
        )
        self.assertEqual(
            'qcow2',
            output['disk_format'],
        )
        self.assertTrue(
            output["is_public"],
        )

        # Test properties
        self.openstack(
            'image set '
            + '--property a=b '
            + '--property c=d '
            + '--public '
            + self.name
        )
        output = self.openstack(
            'image show ' + self.name,
            parse_output=True,
        )
        self.assertEqual(
            {'a': 'b', 'c': 'd'},
            output["properties"],
        )
