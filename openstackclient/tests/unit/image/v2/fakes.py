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

import random
from unittest import mock
import uuid

from openstack.image.v2 import image
from openstack.image.v2 import member

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils

image_id = '0f41529e-7c12-4de8-be2d-181abb825b3c'
image_name = 'graven'


class FakeImagev2Client(object):

    def __init__(self, **kwargs):
        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})
        self.image_members = mock.Mock()
        self.image_members.resource_class = fakes.FakeResource(None, {})
        self.image_tags = mock.Mock()
        self.image_tags.resource_class = fakes.FakeResource(None, {})

        self.find_image = mock.Mock()
        self.find_image.resource_class = fakes.FakeResource(None, {})

        self.get_image = mock.Mock()
        self.get_image.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.version = 2.0


class TestImagev2(utils.TestCommand):

    def setUp(self):
        super(TestImagev2, self).setUp()

        self.app.client_manager.image = FakeImagev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.identity = identity_fakes.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class FakeImage(object):
    """Fake one or more images.

    TODO(xiexs): Currently, only image API v2 is supported by this class.
    """

    @staticmethod
    def create_one_image(attrs=None):
        """Create a fake image.

        :param Dictionary attrs:
            A dictionary with all attrbutes of image
        :return:
            A FakeResource object with id, name, owner, protected,
            visibility, tags and size attrs
        """
        attrs = attrs or {}

        # Set default attribute
        image_info = {
            'id': str(uuid.uuid4()),
            'name': 'image-name' + uuid.uuid4().hex,
            'owner_id': 'image-owner' + uuid.uuid4().hex,
            'is_protected': bool(random.choice([0, 1])),
            'visibility': random.choice(['public', 'private']),
            'tags': [uuid.uuid4().hex for r in range(2)],
        }

        # Overwrite default attributes if there are some attributes set
        image_info.update(attrs)

        return image.Image(**image_info)

    @staticmethod
    def create_images(attrs=None, count=2):
        """Create multiple fake images.

        :param Dictionary attrs:
            A dictionary with all attributes of image
        :param Integer count:
            The number of images to be faked
        :return:
            A list of FakeResource objects
        """
        images = []
        for n in range(0, count):
            images.append(FakeImage.create_one_image(attrs))

        return images

    @staticmethod
    def create_one_image_member(attrs=None):
        """Create a fake image member.

        :param Dictionary attrs:
            A dictionary with all attributes of image member
        :return:
            A FakeResource object with member_id, image_id and so on
        """
        attrs = attrs or {}

        # Set default attribute
        image_member_info = {
            'member_id': 'member-id-' + uuid.uuid4().hex,
            'image_id': 'image-id-' + uuid.uuid4().hex,
            'status': 'pending',
        }

        # Overwrite default attributes if there are some attributes set
        image_member_info.update(attrs)

        return member.Member(**image_member_info)
