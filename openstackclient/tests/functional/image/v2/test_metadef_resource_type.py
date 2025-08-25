# Licensed under the Apache License, Version 2.0 (the "License"); you may
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


class ImageMetadefResourceTypeTests(base.BaseImageTests):
    """Functional tests for image metadef resource type commands."""

    def setUp(self):
        super().setUp()

        # Create unique namespace name using UUID
        self.namespace_name = 'test-mdef-ns-' + uuid.uuid4().hex
        self.resource_type_name = 'test-mdef-rt-' + uuid.uuid4().hex

        # Create namespace
        self.openstack('image metadef namespace create ' + self.namespace_name)
        self.addCleanup(
            self.openstack,
            'image metadef namespace delete ' + self.namespace_name,
        )

    def test_metadef_resource_type(self):
        """Test image metadef resource type commands"""

        self.openstack(
            'image metadef resource type association create '
            f'{self.namespace_name} {self.resource_type_name}',
        )
        self.addCleanup(
            self.openstack,
            'image metadef resource type association delete '
            f'{self.namespace_name} {self.resource_type_name}',
        )

        output = self.openstack(
            'image metadef resource type list',
            parse_output=True,
        )

        self.assertIn(
            self.resource_type_name, [item['Name'] for item in output]
        )
