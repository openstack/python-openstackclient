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

from openstackclient.tests.functional.image import base


class CacheTests(base.BaseImageTests):
    """Functional tests for Cache commands"""

    def test_cached_image(self):
        """Test cached image operations including queue and clear"""
        # Create test image
        name = uuid.uuid4().hex
        output = self.openstack(
            f'image create {name}',
            parse_output=True,
        )
        image_id = output["id"]
        self.assertOutput(name, output['name'])

        # Register cleanup for created image
        self.addCleanup(
            self.openstack, 'cached image delete ' + image_id, fail_ok=True
        )
        self.addCleanup(self.openstack, 'image delete ' + image_id)

        # Queue image for caching
        self.openstack('cached image queue ' + image_id)

        # Verify queuing worked
        cache_output = self.openstack('cached image list', parse_output=True)
        self.assertIsInstance(cache_output, list)
        image_ids = [img['ID'] for img in cache_output]
        self.assertIn(image_id, image_ids)

        # Clear cached images
        self.openstack('cached image clear')

        # Verify clearing worked
        output = self.openstack('cached image list', parse_output=True)
        if output:
            image_ids = [img['ID'] for img in output]
            self.assertNotIn(image_id, image_ids)
