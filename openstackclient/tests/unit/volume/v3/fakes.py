# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import random
from unittest import mock
import uuid

from cinderclient import api_versions
from openstack.block_storage.v3 import availability_zone as _availability_zone
from openstack.block_storage.v3 import block_storage_summary as _summary
from openstack.block_storage.v3 import extension as _extension

from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_v2_fakes


class FakeVolumeClient:
    def __init__(self, **kwargs):
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.api_version = api_versions.APIVersion('3.0')

        self.attachments = mock.Mock()
        self.attachments.resource_class = fakes.FakeResource(None, {})
        self.clusters = mock.Mock()
        self.clusters.resource_class = fakes.FakeResource(None, {})
        self.groups = mock.Mock()
        self.groups.resource_class = fakes.FakeResource(None, {})
        self.group_snapshots = mock.Mock()
        self.group_snapshots.resource_class = fakes.FakeResource(None, {})
        self.group_types = mock.Mock()
        self.group_types.resource_class = fakes.FakeResource(None, {})
        self.messages = mock.Mock()
        self.messages.resource_class = fakes.FakeResource(None, {})
        self.resource_filters = mock.Mock()
        self.resource_filters.resource_class = fakes.FakeResource(None, {})
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.workers = mock.Mock()
        self.workers.resource_class = fakes.FakeResource(None, {})


class TestVolume(utils.TestCommand):
    def setUp(self):
        super().setUp()

        self.app.client_manager.volume = FakeVolumeClient(
            endpoint=fakes.AUTH_URL, token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.identity = identity_fakes.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL, token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.compute = compute_fakes.FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


# TODO(stephenfin): Check if the responses are actually the same
create_one_volume = volume_v2_fakes.create_one_volume
create_one_volume_type = volume_v2_fakes.create_one_volume_type


def create_one_availability_zone(attrs=None):
    """Create a fake AZ.

    :param dict attrs: A dictionary with all attributes
    :return: A fake
        openstack.block_storage.v3.availability_zone.AvailabilityZone object
    """
    attrs = attrs or {}

    # Set default attributes.
    availability_zone_info = {
        'name': uuid.uuid4().hex,
        'state': {'available': True},
    }

    # Overwrite default attributes.
    availability_zone_info.update(attrs)

    availability_zone = _availability_zone.AvailabilityZone(
        **availability_zone_info
    )
    return availability_zone


def create_availability_zones(attrs=None, count=2):
    """Create multiple fake AZs.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of availability zones to fake
    :return: A list of fake
        openstack.block_storage.v3.availability_zone.AvailabilityZone objects
    """
    availability_zones = []
    for i in range(0, count):
        availability_zone = create_one_availability_zone(attrs)
        availability_zones.append(availability_zone)

    return availability_zones


def create_one_extension(attrs=None):
    """Create a fake extension.

    :param dict attrs: A dictionary with all attributes
    :return: A fake
        openstack.block_storage.v3.extension.Extension object
    """
    attrs = attrs or {}

    # Set default attributes.
    extension_info = {
        'alias': 'OS-SCH-HNT',
        'description': 'description-' + uuid.uuid4().hex,
        'links': [
            {
                "href": "https://github.com/openstack/block-api",
                "type": "text/html",
                "rel": "describedby",
            }
        ],
        'name': 'name-' + uuid.uuid4().hex,
        'updated_at': '2013-04-18T00:00:00+00:00',
    }

    # Overwrite default attributes.
    extension_info.update(attrs)

    extension = _extension.Extension(**extension_info)
    return extension


def create_one_cluster(attrs=None):
    """Create a fake service cluster.

    :param attrs: A dictionary with all attributes of service cluster
    :return: A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    cluster_info = {
        'name': f'cluster-{uuid.uuid4().hex}',
        'binary': f'binary-{uuid.uuid4().hex}',
        'state': random.choice(['up', 'down']),
        'status': random.choice(['enabled', 'disabled']),
        'disabled_reason': None,
        'num_hosts': random.randint(1, 64),
        'num_down_hosts': random.randint(1, 64),
        'last_heartbeat': '2015-09-16T09:28:52.000000',
        'created_at': '2015-09-16T09:28:52.000000',
        'updated_at': '2015-09-16T09:28:52.000000',
        'replication_status': None,
        'frozen': False,
        'active_backend_id': None,
    }

    # Overwrite default attributes if there are some attributes set
    cluster_info.update(attrs)

    return fakes.FakeResource(None, cluster_info, loaded=True)


def create_clusters(attrs=None, count=2):
    """Create multiple fake service clusters.

    :param attrs: A dictionary with all attributes of service cluster
    :param count: The number of service clusters to be faked
    :return: A list of FakeResource objects
    """
    clusters = []
    for n in range(0, count):
        clusters.append(create_one_cluster(attrs))

    return clusters


def create_one_resource_filter(attrs=None):
    """Create a fake resource filter.

    :param attrs: A dictionary with all attributes of resource filter
    :return: A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    # Set default attribute

    resource_filter_info = {
        'filters': [
            'name',
            'status',
            'image_metadata',
            'bootable',
            'migration_status',
        ],
        'resource': 'volume',
    }

    # Overwrite default attributes if there are some attributes set
    resource_filter_info.update(attrs)

    return fakes.FakeResource(None, resource_filter_info, loaded=True)


def create_resource_filters(attrs=None, count=2):
    """Create multiple fake resource filters.

    :param attrs: A dictionary with all attributes of resource filter
    :param count: The number of resource filters to be faked
    :return: A list of FakeResource objects
    """
    resource_filters = []
    for n in range(0, count):
        resource_filters.append(create_one_resource_filter(attrs))

    return resource_filters


def create_one_volume_group(attrs=None):
    """Create a fake group.

    :param attrs: A dictionary with all attributes of group
    :return: A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    group_type = attrs.pop('group_type', None) or uuid.uuid4().hex
    volume_types = attrs.pop('volume_types', None) or [uuid.uuid4().hex]

    # Set default attribute
    group_info = {
        'id': uuid.uuid4().hex,
        'status': random.choice(
            [
                'available',
            ]
        ),
        'availability_zone': f'az-{uuid.uuid4().hex}',
        'created_at': '2015-09-16T09:28:52.000000',
        'name': 'first_group',
        'description': f'description-{uuid.uuid4().hex}',
        'group_type': group_type,
        'volume_types': volume_types,
        'volumes': [f'volume-{uuid.uuid4().hex}'],
        'group_snapshot_id': None,
        'source_group_id': None,
        'project_id': f'project-{uuid.uuid4().hex}',
    }

    # Overwrite default attributes if there are some attributes set
    group_info.update(attrs)

    group = fakes.FakeResource(None, group_info, loaded=True)
    return group


def create_volume_groups(attrs=None, count=2):
    """Create multiple fake groups.

    :param attrs: A dictionary with all attributes of group
    :param count: The number of groups to be faked
    :return: A list of FakeResource objects
    """
    groups = []
    for n in range(0, count):
        groups.append(create_one_volume_group(attrs))

    return groups


def create_one_volume_group_snapshot(attrs=None, methods=None):
    """Create a fake group snapshot.

    :param attrs: A dictionary with all attributes
    :param methods: A dictionary with all methods
    :return: A FakeResource object with id, name, description, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    group_snapshot_info = {
        'id': uuid.uuid4().hex,
        'name': f'group-snapshot-{uuid.uuid4().hex}',
        'description': f'description-{uuid.uuid4().hex}',
        'status': random.choice(['available']),
        'group_id': uuid.uuid4().hex,
        'group_type_id': uuid.uuid4().hex,
        'project_id': uuid.uuid4().hex,
    }

    # Overwrite default attributes if there are some attributes set
    group_snapshot_info.update(attrs)

    group_snapshot = fakes.FakeResource(
        None, group_snapshot_info, methods=methods, loaded=True
    )
    return group_snapshot


def create_volume_group_snapshots(attrs=None, count=2):
    """Create multiple fake group snapshots.

    :param attrs: A dictionary with all attributes of group snapshot
    :param count: The number of group snapshots to be faked
    :return: A list of FakeResource objects
    """
    group_snapshots = []
    for n in range(0, count):
        group_snapshots.append(create_one_volume_group_snapshot(attrs))

    return group_snapshots


def create_one_volume_group_type(attrs=None, methods=None):
    """Create a fake group type.

    :param attrs: A dictionary with all attributes of group type
    :param methods: A dictionary with all methods
    :return: A FakeResource object with id, name, description, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    group_type_info = {
        'id': uuid.uuid4().hex,
        'name': f'group-type-{uuid.uuid4().hex}',
        'description': f'description-{uuid.uuid4().hex}',
        'is_public': random.choice([True, False]),
        'group_specs': {},
    }

    # Overwrite default attributes if there are some attributes set
    group_type_info.update(attrs)

    group_type = fakes.FakeResource(
        None, group_type_info, methods=methods, loaded=True
    )
    return group_type


def create_volume_group_types(attrs=None, count=2):
    """Create multiple fake group types.

    :param attrs: A dictionary with all attributes of group type
    :param count: The number of group types to be faked
    :return: A list of FakeResource objects
    """
    group_types = []
    for n in range(0, count):
        group_types.append(create_one_volume_group_type(attrs))

    return group_types


def create_one_volume_message(attrs=None):
    """Create a fake message.

    :param attrs: A dictionary with all attributes of message
    :return: A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    message_info = {
        'created_at': '2016-02-11T11:17:37.000000',
        'event_id': f'VOLUME_{random.randint(1, 999999):06d}',
        'guaranteed_until': '2016-02-11T11:17:37.000000',
        'id': uuid.uuid4().hex,
        'message_level': 'ERROR',
        'request_id': f'req-{uuid.uuid4().hex}',
        'resource_type': 'VOLUME',
        'resource_uuid': uuid.uuid4().hex,
        'user_message': f'message-{uuid.uuid4().hex}',
    }

    # Overwrite default attributes if there are some attributes set
    message_info.update(attrs)

    return fakes.FakeResource(None, message_info, loaded=True)


def create_volume_messages(attrs=None, count=2):
    """Create multiple fake messages.

    :param attrs: A dictionary with all attributes of message
    :param count: The number of messages to be faked
    :return: A list of FakeResource objects
    """
    messages = []
    for n in range(0, count):
        messages.append(create_one_volume_message(attrs))

    return messages


def get_volume_messages(messages=None, count=2):
    """Get an iterable MagicMock object with a list of faked messages.

    If messages list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param messages: A list of FakeResource objects faking messages
    :param count: The number of messages to be faked
    :return An iterable Mock object with side_effect set to a list of faked
        messages
    """
    if messages is None:
        messages = create_volume_messages(count)

    return mock.Mock(side_effect=messages)


def create_one_volume_attachment(attrs=None):
    """Create a fake volume attachment.

    :param attrs: A dictionary with all attributes of volume attachment
    :return: A FakeResource object with id, status, etc.
    """
    attrs = attrs or {}

    attachment_id = uuid.uuid4().hex
    volume_id = attrs.pop('volume_id', None) or uuid.uuid4().hex
    server_id = attrs.pop('instance', None) or uuid.uuid4().hex

    # Set default attribute
    attachment_info = {
        'id': attachment_id,
        'volume_id': volume_id,
        'instance': server_id,
        'status': random.choice(
            [
                'attached',
                'attaching',
                'detached',
                'reserved',
                'error_attaching',
                'error_detaching',
                'deleted',
            ]
        ),
        'attach_mode': random.choice(['ro', 'rw']),
        'attached_at': '2015-09-16T09:28:52.000000',
        'detached_at': None,
        'connection_info': {
            'access_mode': 'rw',
            'attachment_id': attachment_id,
            'auth_method': 'CHAP',
            'auth_password': 'AcUZ8PpxLHwzypMC',
            'auth_username': '7j3EZQWT3rbE6pcSGKvK',
            'cacheable': False,
            'driver_volume_type': 'iscsi',
            'encrypted': False,
            'qos_specs': None,
            'target_discovered': False,
            'target_iqn': f'iqn.2010-10.org.openstack:volume-{attachment_id}',
            'target_lun': '1',
            'target_portal': '192.168.122.170:3260',
            'volume_id': volume_id,
        },
    }

    # Overwrite default attributes if there are some attributes set
    attachment_info.update(attrs)

    return fakes.FakeResource(None, attachment_info, loaded=True)


def create_volume_attachments(attrs=None, count=2):
    """Create multiple fake volume attachments.

    :param attrs: A dictionary with all attributes of volume attachment
    :param count: The number of volume attachments to be faked
    :return: A list of FakeResource objects
    """
    attachments = []

    for n in range(0, count):
        attachments.append(create_one_volume_attachment(attrs))

    return attachments


def get_volume_attachments(attachments=None, count=2):
    """Get an iterable MagicMock object with a list of faked volumes.

    If attachments list is provided, then initialize the Mock object with
    the list. Otherwise create one.

    :param attachments: A list of FakeResource objects faking volume
        attachments
    :param count: The number of volume attachments to be faked
    :return An iterable Mock object with side_effect set to a list of faked
        volume attachments
    """
    if attachments is None:
        attachments = create_volume_attachments(count)

    return mock.Mock(side_effect=attachments)


def create_service_log_level_entry(attrs=None):
    service_log_level_info = {
        'host': 'host_test',
        'binary': 'cinder-api',
        'prefix': 'cinder.api.common',
        'level': 'DEBUG',
    }
    # Overwrite default attributes if there are some attributes set
    attrs = attrs or {}

    service_log_level_info.update(attrs)

    service_log_level = fakes.FakeResource(
        None, service_log_level_info, loaded=True
    )
    return service_log_level


def create_cleanup_records():
    """Create fake service cleanup records.

    :return: A list of FakeResource objects
    """
    cleaning_records = []
    unavailable_records = []
    cleaning_work_info = {
        'id': 1,
        'host': 'devstack@fakedriver-1',
        'binary': 'cinder-volume',
        'cluster_name': 'fake_cluster',
    }
    unavailable_work_info = {
        'id': 2,
        'host': 'devstack@fakedriver-2',
        'binary': 'cinder-scheduler',
        'cluster_name': 'new_cluster',
    }
    cleaning_records.append(cleaning_work_info)
    unavailable_records.append(unavailable_work_info)

    cleaning = [
        fakes.FakeResource(None, obj, loaded=True) for obj in cleaning_records
    ]
    unavailable = [
        fakes.FakeResource(None, obj, loaded=True)
        for obj in unavailable_records
    ]

    return cleaning, unavailable


def create_one_manage_record(attrs=None, snapshot=False):
    manage_dict = {
        'reference': {'source-name': 'fake-volume'},
        'size': '1',
        'safe_to_manage': False,
        'reason_not_safe': 'already managed',
        'cinder_id': 'fake-volume',
        'extra_info': None,
    }
    if snapshot:
        manage_dict['source_reference'] = {'source-name': 'fake-source'}

    # Overwrite default attributes if there are some attributes set
    attrs = attrs or {}

    manage_dict.update(attrs)
    manage_record = fakes.FakeResource(None, manage_dict, loaded=True)
    return manage_record


def create_volume_manage_list_records(count=2):
    volume_manage_list = []
    for i in range(count):
        volume_manage_list.append(
            create_one_manage_record({'size': str(i + 1)})
        )

    return volume_manage_list


def create_snapshot_manage_list_records(count=2):
    snapshot_manage_list = []
    for i in range(count):
        snapshot_manage_list.append(
            create_one_manage_record({'size': str(i + 1)}, snapshot=True)
        )

    return snapshot_manage_list


def get_one_block_storage_summary(total_size, metadata=None):
    summary_dict = {
        'total_count': 2,
        'total_size': total_size,
    }
    if metadata:
        summary_dict['metadata'] = metadata
    block_storage_summary = _summary.BlockStorageSummary(**summary_dict)
    return block_storage_summary
