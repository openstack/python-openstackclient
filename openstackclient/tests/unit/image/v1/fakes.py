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

from openstack.image.v1 import _proxy
from openstack.image.v1 import image

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.image = mock.Mock(spec=_proxy.Proxy)
        self.image_client = self.app.client_manager.image


class TestImagev1(FakeClientMixin, utils.TestCommand):
    def setUp(self):
        super().setUp()

        self.app.client_manager.volume = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.volume_client = self.app.client_manager.volume


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
