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

import mock

from openstackclient.tests import fakes
from openstackclient.tests import utils

from openstackclient.tests.identity.v3 import fakes as identity_fakes

image_id = '0f41529e-7c12-4de8-be2d-181abb825b3c'
image_name = 'graven'
image_owner = 'baal'
image_protected = False
image_visibility = 'public'

IMAGE = {
    'id': image_id,
    'name': image_name,
    'owner': image_owner,
    'protected': image_protected,
    'visibility': image_visibility,
}

IMAGE_columns = tuple(sorted(IMAGE))
IMAGE_data = tuple((IMAGE[x] for x in sorted(IMAGE)))

member_status = 'pending'
MEMBER = {
    'member_id': identity_fakes.project_id,
    'image_id': image_id,
    'status': member_status,
}

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
                "integer"
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
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


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
