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
#

import copy
import uuid

import mock

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v1 import fakes as volume_fakes


image_id = 'im1'
image_name = 'graven'
image_owner = 'baal'
image_protected = False
image_public = True
image_properties = {
    'Alpha': 'a',
    'Beta': 'b',
    'Gamma': 'g',
}
image_properties_str = "Alpha='a', Beta='b', Gamma='g'"
image_data = 'line 1\nline 2\n'
image_size = 0

IMAGE = {
    'id': image_id,
    'name': image_name,
    'container_format': '',
    'disk_format': '',
    'owner': image_owner,
    'min_disk': 0,
    'min_ram': 0,
    'is_public': image_public,
    'protected': image_protected,
    'properties': image_properties,
    'size': image_size,
}

IMAGE_columns = tuple(sorted(IMAGE))
IMAGE_output = dict(IMAGE)
IMAGE_output['properties'] = image_properties_str
IMAGE_data = tuple((IMAGE_output[x] for x in sorted(IMAGE_output)))


class FakeImagev1Client(object):

    def __init__(self, **kwargs):
        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.version = 1.0


class TestImagev1(utils.TestCommand):

    def setUp(self):
        super(TestImagev1, self).setUp()

        self.app.client_manager.image = FakeImagev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.volume = volume_fakes.FakeVolumev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class FakeImage(object):
    """Fake one or more images."""

    @staticmethod
    def create_one_image(attrs=None):
        """Create a fake image.

        :param Dictionary attrs:
            A dictionary with all attrbutes of image
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
            'properties': {
                'Alpha': 'a',
                'Beta': 'b',
                'Gamma': 'g'},
        }

        # Overwrite default attributes if there are some attributes set
        image_info.update(attrs)

        image = fakes.FakeResource(
            info=copy.deepcopy(image_info),
            loaded=True)

        return image
