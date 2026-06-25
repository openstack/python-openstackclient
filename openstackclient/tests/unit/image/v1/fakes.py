#   Copyright 2013 Nebula Inc.
#
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

from unittest import mock
import uuid

from openstack.block_storage import v2 as block_storage_v2
from openstack.image import v1 as image_v1
from openstack.image.v1 import image

from openstackclient.tests.unit import utils


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        # TODO(stephenfin): Switch to spec_set once keystoneauth exposes
        # instance attributes as class attributes
        # https://review.opendev.org/c/openstack/keystoneauth/+/994090
        self.app.client_manager.image = mock.Mock(spec=image_v1.Proxy)
        self.image_client = self.app.client_manager.image


class TestImagev1(FakeClientMixin, utils.TestCommand):
    def setUp(self):
        super().setUp()

        # TODO(stephenfin): Rename to 'volume_client' now that all commands are
        # migrated to SDK
        self.app.client_manager.sdk_connection.volume = mock.Mock(
            spec=block_storage_v2.Proxy
        )
        self.app.client_manager.sdk_connection.volume.api_version = '2'
        self.volume_sdk_client = self.app.client_manager.sdk_connection.volume


def create_one_image(attrs=None):
    """Create a fake image.

    :param Dictionary attrs:
        A dictionary with all attributes of image
    :return:
        A FakeResource object with id, name, owner, protected,
        visibility and tags attrs
    """
    attrs = attrs or {}

    # Set default attribute
    image_info = {
        'id': str(uuid.uuid4()),
        'name': 'image-name' + uuid.uuid4().hex,
        'owner': 'image-owner' + uuid.uuid4().hex,
        'container_format': '',
        'disk_format': '',
        'min_disk': 0,
        'min_ram': 0,
        'is_public': True,
        'protected': False,
        'properties': {'Alpha': 'a', 'Beta': 'b', 'Gamma': 'g'},
        'status': 'status' + uuid.uuid4().hex,
    }

    # Overwrite default attributes if there are some attributes set
    image_info.update(attrs)

    return image.Image(**image_info)
