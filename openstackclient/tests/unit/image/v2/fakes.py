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
import random
import uuid

from glanceclient.v2 import schemas
import mock
from osc_lib.cli import format_columns
import warlock

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils

image_id = '0f41529e-7c12-4de8-be2d-181abb825b3c'
image_name = 'graven'
image_owner = 'baal'
image_protected = False
image_visibility = 'public'
image_tags = []
image_size = 0

IMAGE = {
    'id': image_id,
    'name': image_name,
    'owner': image_owner,
    'protected': image_protected,
    'visibility': image_visibility,
    'tags': image_tags,
    'size': image_size
}

IMAGE_columns = tuple(sorted(IMAGE))
IMAGE_data = tuple((IMAGE[x] for x in sorted(IMAGE)))

IMAGE_SHOW = copy.copy(IMAGE)
IMAGE_SHOW['tags'] = format_columns.ListColumn(IMAGE_SHOW['tags'])
IMAGE_SHOW_data = tuple((IMAGE_SHOW[x] for x in sorted(IMAGE_SHOW)))

# Just enough v2 schema to do some testing
IMAGE_schema = {
    "additionalProperties": {
        "type": "string"
    },
    "name": "image",
    "links": [
        {
            "href": "{self}",
            "rel": "self"
        },
        {
            "href": "{file}",
            "rel": "enclosure"
        },
        {
            "href": "{schema}",
            "rel": "describedby"
        }
    ],
    "properties": {
        "id": {
            "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",  # noqa
            "type": "string",
            "description": "An identifier for the image"
        },
        "name": {
            "type": [
                "null",
                "string"
            ],
            "description": "Descriptive name for the image",
            "maxLength": 255
        },
        "owner": {
            "type": [
                "null",
                "string"
            ],
            "description": "Owner of the image",
            "maxLength": 255
        },
        "protected": {
            "type": "boolean",
            "description": "If true, image will not be deletable."
        },
        "self": {
            "type": "string",
            "description": "(READ-ONLY)"
        },
        "schema": {
            "type": "string",
            "description": "(READ-ONLY)"
        },
        "size": {
            "type": [
                "null",
                "integer",
                "string"
            ],
            "description": "Size of image file in bytes (READ-ONLY)"
        },
        "status": {
            "enum": [
                "queued",
                "saving",
                "active",
                "killed",
                "deleted",
                "pending_delete"
            ],
            "type": "string",
            "description": "Status of the image (READ-ONLY)"
        },
        "tags": {
            "items": {
                "type": "string",
                "maxLength": 255
            },
            "type": "array",
            "description": "List of strings related to the image"
        },
        "visibility": {
            "enum": [
                "public",
                "private"
            ],
            "type": "string",
            "description": "Scope of image accessibility"
        },
    }
}


class FakeImagev2Client(object):

    def __init__(self, **kwargs):
        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})
        self.image_members = mock.Mock()
        self.image_members.resource_class = fakes.FakeResource(None, {})
        self.image_tags = mock.Mock()
        self.image_tags.resource_class = fakes.FakeResource(None, {})
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
            'owner': 'image-owner' + uuid.uuid4().hex,
            'protected': bool(random.choice([0, 1])),
            'visibility': random.choice(['public', 'private']),
            'tags': [uuid.uuid4().hex for r in range(2)],
        }

        # Overwrite default attributes if there are some attributes set
        image_info.update(attrs)

        # Set up the schema
        model = warlock.model_factory(
            IMAGE_schema,
            schemas.SchemaBasedModel,
        )

        return model(**image_info)

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
    def get_images(images=None, count=2):
        """Get an iterable MagicMock object with a list of faked images.

        If images list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List images:
            A list of FakeResource objects faking images
        :param Integer count:
            The number of images to be faked
        :return:
            An iterable Mock object with side_effect set to a list of faked
            images
        """
        if images is None:
            images = FakeImage.create_images(count)

        return mock.Mock(side_effect=images)

    @staticmethod
    def get_image_columns(image=None):
        """Get the image columns from a faked image object.

        :param image:
            A FakeResource objects faking image
        :return:
            A tuple which may include the following keys:
            ('id', 'name', 'owner', 'protected', 'visibility', 'tags')
        """
        if image is not None:
            return tuple(sorted(image))
        return IMAGE_columns

    @staticmethod
    def get_image_data(image=None):
        """Get the image data from a faked image object.

        :param image:
            A FakeResource objects faking image
        :return:
            A tuple which may include the following values:
            ('image-123', 'image-foo', 'admin', False, 'public', 'bar, baz')
        """
        data_list = []
        if image is not None:
            for x in sorted(image.keys()):
                if x == 'tags':
                    # The 'tags' should be format_list
                    data_list.append(
                        format_columns.ListColumn(getattr(image, x)))
                else:
                    data_list.append(getattr(image, x))
        return tuple(data_list)

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

        image_member = fakes.FakeModel(
            copy.deepcopy(image_member_info))

        return image_member
