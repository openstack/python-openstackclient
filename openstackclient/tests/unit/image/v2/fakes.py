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

from openstack.image.v2 import _proxy
from openstack.image.v2 import cache
from openstack.image.v2 import image
from openstack.image.v2 import member
from openstack.image.v2 import metadef_namespace
from openstack.image.v2 import metadef_object
from openstack.image.v2 import metadef_property
from openstack.image.v2 import metadef_resource_type
from openstack.image.v2 import service_info as _service_info
from openstack.image.v2 import task

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.image = mock.Mock(spec=_proxy.Proxy)
        self.image_client = self.app.client_manager.image


class TestImagev2(
    identity_fakes.FakeClientMixin,
    FakeClientMixin,
    utils.TestCommand,
): ...


def create_one_image(attrs=None):
    """Create a fake image.

    :param attrs: A dictionary with all attributes of image
    :type attrs: dict
    :return: A fake Image object.
    :rtype: `openstack.image.v2.image.Image`
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


def create_images(attrs=None, count=2):
    """Create multiple fake images.

    :param attrs: A dictionary with all attributes of image
    :type attrs: dict
    :param count: The number of images to be faked
    :type count: int
    :return: A list of fake Image objects
    :rtype: list
    """
    images = []
    for n in range(0, count):
        images.append(create_one_image(attrs))

    return images


def create_one_image_member(attrs=None):
    """Create a fake image member.

    :param attrs: A dictionary with all attributes of image member
    :type attrs: dict
    :return: A fake Member object.
    :rtype: `openstack.image.v2.member.Member`
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


def create_one_import_info(attrs=None):
    """Create a fake import info.

    :param attrs: A dictionary with all attributes of import info
    :type attrs: dict
    :return: A fake Import object.
    :rtype: `openstack.image.v2.service_info.Import`
    """
    attrs = attrs or {}

    import_info = {
        'import-methods': {
            'description': 'Import methods available.',
            'type': 'array',
            'value': [
                'glance-direct',
                'web-download',
                'glance-download',
                'copy-image',
            ],
        }
    }
    import_info.update(attrs)

    return _service_info.Import(**import_info)


def create_one_stores_info(attrs=None):
    """Create a fake stores info.

    :param attrs: A dictionary with all attributes of stores
    :type attrs: dict
    :return: A fake Store object list.
    :rtype: `openstack.image.v2.service_info.Store`
    """
    attrs = attrs or {}

    stores_info = {
        "stores": [
            {
                "id": "reliable",
                "description": "More expensive store with data redundancy",
            },
            {
                "id": "fast",
                "description": "Provides quick access to your image data",
                "default": True,
            },
            {
                "id": "cheap",
                "description": "Less expensive store for seldom-used images",
            },
        ]
    }
    stores_info.update(attrs)

    return _service_info.Store(**stores_info)


def create_one_task(attrs=None):
    """Create a fake task.

    :param attrs: A dictionary with all attributes of task
    :type attrs: dict
    :return: A fake Task object.
    :rtype: `openstack.image.v2.task.Task`
    """
    attrs = attrs or {}

    # Set default attribute
    task_info = {
        'created_at': '2016-06-29T16:13:07Z',
        'expires_at': '2016-07-01T16:13:07Z',
        'id': str(uuid.uuid4()),
        'input': {
            'image_properties': {
                'container_format': 'ovf',
                'disk_format': 'vhd',
            },
            'import_from': 'https://apps.openstack.org/excellent-image',
            'import_from_format': 'qcow2',
        },
        'message': '',
        'owner': str(uuid.uuid4()),
        'result': {
            'image_id': str(uuid.uuid4()),
        },
        'schema': '/v2/schemas/task',
        'status': random.choice(
            [
                'pending',
                'processing',
                'success',
                'failure',
            ]
        ),
        # though not documented, the API only allows 'import'
        # https://github.com/openstack/glance/blob/24.0.0/glance/api/v2/tasks.py#L186-L190
        'type': 'import',
        'updated_at': '2016-06-29T16:13:07Z',
    }

    # Overwrite default attributes if there are some attributes set
    task_info.update(attrs)

    return task.Task(**task_info)


def create_tasks(attrs=None, count=2):
    """Create multiple fake tasks.

    :param attrs: A dictionary with all attributes of Task
    :type attrs: dict
    :param count: The number of tasks to be faked
    :type count: int
    :return: A list of fake Task objects
    :rtype: list
    """
    tasks = []
    for n in range(0, count):
        tasks.append(create_one_task(attrs))

    return tasks


def create_cache(attrs=None):
    attrs = attrs or {}
    cache_info = {
        'cached_images': [
            {
                'hits': 0,
                'image_id': '1a56983c-f71f-490b-a7ac-6b321a18935a',
                'last_accessed': 1671699579.444378,
                'last_modified': 1671699579.444378,
                'size': 0,
            },
        ],
        'queued_images': [
            '3a4560a1-e585-443e-9b39-553b46ec92d1',
            '6f99bf80-2ee6-47cf-acfe-1f1fabb7e810',
        ],
    }
    cache_info.update(attrs)

    return cache.Cache(**cache_info)


def create_one_metadef_namespace(attrs=None):
    """Create a fake MetadefNamespace member.

    :param attrs: A dictionary with all attributes of metadef_namespace member
    :type attrs: dict
    :return: a list of MetadefNamespace objects
    :rtype: list of `metadef_namespace.MetadefNamespace`
    """
    attrs = attrs or {}

    metadef_namespace_list = {
        'created_at': '2022-08-17T11:30:22Z',
        'display_name': 'Flavor Quota',
        'namespace': 'OS::Compute::Quota',
        'owner': 'admin',
        # 'resource_type_associations': ['OS::Nova::Flavor'],
        # The part that receives the list type factor is not implemented.
        'visibility': 'public',
    }

    # Overwrite default attributes if there are some attributes set
    metadef_namespace_list.update(attrs)
    return metadef_namespace.MetadefNamespace(**metadef_namespace_list)


def create_one_metadef_property(attrs=None):
    attrs = attrs or {}

    metadef_property_list = {
        'name': 'cpu_cores',
        'title': 'vCPU Cores',
        'type': 'integer',
    }

    # Overwrite default attributes if there are some attributes set
    metadef_property_list.update(attrs)
    return metadef_property.MetadefProperty(**metadef_property_list)


def create_one_resource_type(attrs=None):
    """Create a fake MetadefResourceType member.

    :param attrs: A dictionary with all attributes of
        metadef_resource_type member
    :type attrs: dict
    :return: a fake MetadefResourceType object
    :rtype: A `metadef_resource_type.MetadefResourceType`
    """
    attrs = attrs or {}

    metadef_resource_type_info = {
        'name': 'OS::Compute::Quota',
        'properties_target': 'image',
    }

    metadef_resource_type_info.update(attrs)
    return metadef_resource_type.MetadefResourceType(
        **metadef_resource_type_info
    )


def create_resource_types(attrs=None, count=2):
    """Create multiple fake resource types.

    :param attrs: A dictionary with all attributes of
        metadef_resource_type member
    :type attrs: dict
    :return: A list of fake MetadefResourceType objects
    :rtype: list
    """
    metadef_resource_types = []
    for n in range(0, count):
        metadef_resource_types.append(create_one_resource_type(attrs))

    return metadef_resource_types


def create_one_metadef_object(attrs=None):
    """Create a fake MetadefNamespace member.

    :param attrs: A dictionary with all attributes of metadef_namespace member
    :type attrs: dict
    :return: a list of MetadefNamespace objects
    :rtype: list of `metadef_namespace.MetadefNamespace`
    """
    attrs = attrs or {}

    metadef_objects_list = {
        'created_at': '2014-09-19T18:20:56Z',
        'description': 'The CPU limits with control parameters.',
        'name': 'CPU Limits',
        'properties': {
            'quota:cpu_period': {
                'description': 'The enforcement interval',
                'maximum': 1000000,
                'minimum': 1000,
                'title': 'Quota: CPU Period',
                'type': 'integer',
            },
            'quota:cpu_quota': {
                'description': 'The maximum allowed bandwidth',
                'title': 'Quota: CPU Quota',
                'type': 'integer',
            },
            'quota:cpu_shares': {
                'description': 'The proportional weighted',
                'title': 'Quota: CPU Shares',
                'type': 'integer',
            },
        },
        'required': [],
        'schema': '/v2/schemas/metadefs/object',
        'updated_at': '2014-09-19T18:20:56Z',
    }

    # Overwrite default attributes if there are some attributes set
    metadef_objects_list.update(attrs)
    return metadef_object.MetadefObject(**metadef_objects_list)


def create_one_resource_type_association(attrs=None):
    """Create a fake MetadefResourceTypeAssociation.

    :param attrs: A dictionary with all attributes of
        metadef_resource_type_association member
    :type attrs: dict
    :return: A fake MetadefResourceTypeAssociation object
    :rtype: A `metadef_resource_type_association.
        MetadefResourceTypeAssociation`
    """
    attrs = attrs or {}

    metadef_resource_type_association_info = {
        'namespace_name': 'OS::Compute::Quota',
        'name': 'OS::Nova::Flavor',
    }

    metadef_resource_type_association_info.update(attrs)
    return metadef_resource_type.MetadefResourceTypeAssociation(
        **metadef_resource_type_association_info
    )


def create_resource_type_associations(attrs=None, count=2):
    """Create mutiple fake resource type associations/

    :param attrs: A dictionary with all attributes of
        metadef_resource_type_association member
    :type attrs: dict
    :return: A list of fake MetadefResourceTypeAssociation objects
    :rtype: list
    """
    resource_type_associations = []
    for n in range(0, count):
        resource_type_associations.append(
            create_one_resource_type_association(attrs)
        )

    return resource_type_associations
