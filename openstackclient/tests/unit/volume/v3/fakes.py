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

import copy
import random
import re
from unittest import mock
import uuid

from cinderclient import api_versions
from keystoneauth1 import discover
from openstack.block_storage.v3 import _proxy
from openstack.block_storage.v3 import availability_zone as _availability_zone
from openstack.block_storage.v3 import backup as _backup
from openstack.block_storage.v3 import extension as _extension
from openstack.block_storage.v3 import limits as _limits
from openstack.block_storage.v3 import resource_filter as _filters
from openstack.block_storage.v3 import volume as _volume
from openstack.compute.v2 import _proxy as _compute_proxy
from openstack.image.v2 import _proxy as _image_proxy

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_v2_fakes


class FakeVolumeClient:
    def __init__(self, **kwargs):
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.api_version = api_versions.APIVersion('3.0')

        self.backups = mock.Mock()
        self.backups.resource_class = fakes.FakeResource(None, {})
        self.cgsnapshots = mock.Mock()
        self.cgsnapshots.resource_class = fakes.FakeResource(None, {})
        self.consistencygroups = mock.Mock()
        self.consistencygroups.resource_class = fakes.FakeResource(None, {})
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
        self.qos_specs = mock.Mock()
        self.qos_specs.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.transfers = mock.Mock()
        self.transfers.resource_class = fakes.FakeResource(None, {})
        self.volume_snapshots = mock.Mock()
        self.volume_snapshots.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.workers = mock.Mock()
        self.workers.resource_class = fakes.FakeResource(None, {})


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.volume = FakeVolumeClient(
            endpoint=fakes.AUTH_URL, token=fakes.AUTH_TOKEN
        )
        self.volume_client = self.app.client_manager.volume

        # TODO(stephenfin): Rename to 'volume_client' once all commands are
        # migrated to SDK
        self.app.client_manager.sdk_connection.volume = mock.Mock(
            spec=_proxy.Proxy,
        )
        self.app.client_manager.sdk_connection.volume.api_version = '3'
        self.volume_sdk_client = self.app.client_manager.sdk_connection.volume

        self.set_volume_api_version()  # default to the lowest

    def set_volume_api_version(self, version: str = '3.0'):
        """Set a fake block storage API version.

        :param version: The fake microversion to "support". This should be a
            string of format '3.xx'.
        :returns: None
        """
        assert re.match(r'3.\d+', version)

        self.volume_client.api_version = api_versions.APIVersion(version)

        self.volume_sdk_client.default_microversion = version
        self.volume_sdk_client.get_endpoint_data.return_value = (
            discover.EndpointData(
                min_microversion='3.0',  # cinder has not bumped this yet
                max_microversion=version,
            )
        )


class TestVolume(
    identity_fakes.FakeClientMixin,
    FakeClientMixin,
    utils.TestCommand,
):
    def setUp(self):
        super().setUp()

        # avoid circular imports by defining this manually rather than using
        # openstackclient.tests.unit.compute.v2.fakes.FakeClientMixin
        self.app.client_manager.compute = mock.Mock(_compute_proxy.Proxy)
        self.compute_client = self.app.client_manager.compute

        # avoid circular imports by defining this manually rather than using
        # openstackclient.tests.unit.image.v2.fakes.FakeClientMixin
        self.app.client_manager.image = mock.Mock(spec=_image_proxy.Proxy)
        self.image_client = self.app.client_manager.image


# TODO(stephenfin): Check if the responses are actually the same
create_one_capability = volume_v2_fakes.create_one_capability
create_one_pool = volume_v2_fakes.create_one_pool
create_one_snapshot = volume_v2_fakes.create_one_snapshot
create_one_service = volume_v2_fakes.create_one_service


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


def create_one_consistency_group(attrs=None):
    """Create a fake consistency group.

    :param dict attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with id, name, description, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    consistency_group_info = {
        "id": 'backup-id-' + uuid.uuid4().hex,
        "name": 'backup-name-' + uuid.uuid4().hex,
        "description": 'description-' + uuid.uuid4().hex,
        "status": "error",
        "availability_zone": 'zone' + uuid.uuid4().hex,
        "created_at": 'time-' + uuid.uuid4().hex,
        "volume_types": ['volume-type1'],
    }

    # Overwrite default attributes.
    consistency_group_info.update(attrs)

    consistency_group = fakes.FakeResource(
        info=copy.deepcopy(consistency_group_info), loaded=True
    )
    return consistency_group


def create_consistency_groups(attrs=None, count=2):
    """Create multiple fake consistency groups.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of consistency groups to fake
    :return:
        A list of FakeResource objects faking the consistency groups
    """
    consistency_groups = []
    for i in range(0, count):
        consistency_group = create_one_consistency_group(attrs)
        consistency_groups.append(consistency_group)

    return consistency_groups


def get_consistency_groups(consistency_groups=None, count=2):
    """Note:

    Get an iterable MagicMock object with a list of faked
    consistency_groups.

    If consistency_groups list is provided, then initialize
    the Mock object with the list. Otherwise create one.

    :param List consistency_groups:
        A list of FakeResource objects faking consistency_groups
    :param Integer count:
        The number of consistency_groups to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        consistency_groups
    """
    if consistency_groups is None:
        consistency_groups = create_consistency_groups(count)

    return mock.Mock(side_effect=consistency_groups)


def create_one_consistency_group_snapshot(attrs=None):
    """Create a fake consistency group snapshot.

    :param dict attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with id, name, description, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    consistency_group_snapshot_info = {
        "id": 'id-' + uuid.uuid4().hex,
        "name": 'backup-name-' + uuid.uuid4().hex,
        "description": 'description-' + uuid.uuid4().hex,
        "status": "error",
        "consistencygroup_id": 'consistency-group-id' + uuid.uuid4().hex,
        "created_at": 'time-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    consistency_group_snapshot_info.update(attrs)

    consistency_group_snapshot = fakes.FakeResource(
        info=copy.deepcopy(consistency_group_snapshot_info), loaded=True
    )
    return consistency_group_snapshot


def create_consistency_group_snapshots(attrs=None, count=2):
    """Create multiple fake consistency group snapshots.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of consistency group snapshots to fake
    :return:
        A list of FakeResource objects faking the
        consistency group snapshots
    """
    consistency_group_snapshots = []
    for i in range(0, count):
        consistency_group_snapshot = create_one_consistency_group_snapshot(
            attrs,
        )
        consistency_group_snapshots.append(consistency_group_snapshot)

    return consistency_group_snapshots


def get_consistency_group_snapshots(snapshots=None, count=2):
    """Get an iterable MagicMock object with a list of faked cgsnapshots.

    If consistenct group snapshots list is provided, then initialize
    the Mock object with the list. Otherwise create one.

    :param List snapshots:
        A list of FakeResource objects faking consistency group snapshots
    :param Integer count:
        The number of consistency group snapshots to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        consistency groups
    """
    if snapshots is None:
        snapshots = create_consistency_group_snapshots(count)

    return mock.Mock(side_effect=snapshots)


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


def create_one_backup(attrs=None):
    """Create a fake backup.

    :param dict attrs:
        A dictionary with all attributes
    :return: A fake
        openstack.block_storage.v3.backup.Backup object
    """
    attrs = attrs or {}

    # Set default attributes.
    backup_info = {
        "availability_zone": 'zone' + uuid.uuid4().hex,
        "container": 'container-' + uuid.uuid4().hex,
        "created_at": 'time-' + uuid.uuid4().hex,
        "data_timestamp": 'time-' + uuid.uuid4().hex,
        "description": 'description-' + uuid.uuid4().hex,
        "encryption_key_id": None,
        "fail_reason": "Service not found for creating backup.",
        "has_dependent_backups": False,
        "id": 'backup-id-' + uuid.uuid4().hex,
        "is_incremental": False,
        "metadata": {},
        "name": 'backup-name-' + uuid.uuid4().hex,
        "object_count": None,
        "project_id": uuid.uuid4().hex,
        "size": random.randint(1, 20),
        "snapshot_id": 'snapshot-id' + uuid.uuid4().hex,
        "status": "error",
        "updated_at": 'time-' + uuid.uuid4().hex,
        "user_id": uuid.uuid4().hex,
        "volume_id": 'volume-id-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    backup_info.update(attrs)

    backup = _backup.Backup(**backup_info)
    return backup


def create_backup_record():
    """Gets a fake backup record for a given backup.

    :return: An "exported" backup record.
    """

    return {
        'backup_service': 'cinder.backup.drivers.swift.SwiftBackupDriver',
        'backup_url': 'eyJzdGF0dXMiOiAiYXZh',
    }


def import_backup_record():
    """Creates a fake backup record import response from a backup.

    :return: The fake backup object that was encoded.
    """
    return {
        'backup': {
            'id': 'backup.id',
            'name': 'backup.name',
            'links': [
                {'href': 'link1', 'rel': 'self'},
                {'href': 'link2', 'rel': 'bookmark'},
            ],
        },
    }


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


def create_limits(attrs=None):
    """Create a fake limits object."""
    attrs = attrs or {}

    limits_attrs = {
        'absolute': {
            'totalSnapshotsUsed': 1,
            'maxTotalBackups': 10,
            'maxTotalVolumeGigabytes': 1000,
            'maxTotalSnapshots': 10,
            'maxTotalBackupGigabytes': 1000,
            'totalBackupGigabytesUsed': 0,
            'maxTotalVolumes': 10,
            'totalVolumesUsed': 4,
            'totalBackupsUsed': 0,
            'totalGigabytesUsed': 35,
        },
        'rate': [
            {
                "uri": "*",
                "limit": [
                    {
                        "value": 10,
                        "verb": "POST",
                        "remaining": 2,
                        "unit": "MINUTE",
                        "next-available": "2011-12-15T22:42:45Z",
                    },
                    {
                        "value": 10,
                        "verb": "PUT",
                        "remaining": 2,
                        "unit": "MINUTE",
                        "next-available": "2011-12-15T22:42:45Z",
                    },
                    {
                        "value": 100,
                        "verb": "DELETE",
                        "remaining": 100,
                        "unit": "MINUTE",
                        "next-available": "2011-12-15T22:42:45Z",
                    },
                ],
            }
        ],
    }
    limits_attrs.update(attrs)

    limits = _limits.Limit(**limits_attrs)
    return limits


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

    return _filters.ResourceFilter(**resource_filter_info)


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


def create_one_transfer(attrs=None):
    """Create a fake transfer.

    :param dict attrs:
        A dictionary with all attributes of Transfer Request
    :return:
        A FakeResource object with volume_id, name, id.
    """
    # Set default attribute
    transfer_info = {
        'volume_id': 'volume-id-' + uuid.uuid4().hex,
        'name': 'fake_transfer_name',
        'id': 'id-' + uuid.uuid4().hex,
        'links': 'links-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes if there are some attributes set
    attrs = attrs or {}

    transfer_info.update(attrs)

    transfer = fakes.FakeResource(None, transfer_info, loaded=True)

    return transfer


def create_transfers(attrs=None, count=2):
    """Create multiple fake transfers.

    :param dict attrs:
        A dictionary with all attributes of transfer
    :param Integer count:
        The number of transfers to be faked
    :return:
        A list of FakeResource objects
    """
    transfers = []
    for n in range(0, count):
        transfers.append(create_one_transfer(attrs))

    return transfers


def get_transfers(transfers=None, count=2):
    """Get an iterable MagicMock object with a list of faked transfers.

    If transfers list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List transfers:
        A list of FakeResource objects faking transfers
    :param Integer count:
        The number of transfers to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        transfers
    """
    if transfers is None:
        transfers = create_transfers(count)

    return mock.Mock(side_effect=transfers)


def create_one_volume(attrs=None):
    """Create a fake volume.

    :param dict attrs:
        A dictionary with all attributes of volume
    :return:
        A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    volume_info = {
        'id': 'volume-id' + uuid.uuid4().hex,
        'name': 'volume-name' + uuid.uuid4().hex,
        'description': 'description' + uuid.uuid4().hex,
        'status': random.choice(['available', 'in_use']),
        'size': random.randint(1, 20),
        'volume_type': random.choice(['fake_lvmdriver-1', 'fake_lvmdriver-2']),
        'bootable': random.randint(0, 1),
        'metadata': {
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
        },
        'snapshot_id': random.randint(1, 5),
        'availability_zone': 'zone' + uuid.uuid4().hex,
        'attachments': [
            {
                'device': '/dev/' + uuid.uuid4().hex,
                'server_id': uuid.uuid4().hex,
            },
        ],
    }

    # Overwrite default attributes if there are some attributes set
    volume_info.update(attrs)

    volume = fakes.FakeResource(None, volume_info, loaded=True)
    return volume


def create_volumes(attrs=None, count=2):
    """Create multiple fake volumes.

    :param dict attrs:
        A dictionary with all attributes of volume
    :param Integer count:
        The number of volumes to be faked
    :return:
        A list of FakeResource objects
    """
    volumes = []
    for n in range(0, count):
        volumes.append(create_one_volume(attrs))

    return volumes


def get_volumes(volumes=None, count=2):
    """Get an iterable MagicMock object with a list of faked volumes.

    If volumes list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List volumes:
        A list of FakeResource objects faking volumes
    :param Integer count:
        The number of volumes to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        volumes
    """
    if volumes is None:
        volumes = create_volumes(count)

    return mock.Mock(side_effect=volumes)


def create_one_sdk_volume(attrs=None):
    """Create a fake volume.

    :param dict attrs:
        A dictionary with all attributes of volume
    :return:
        A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    volume_info = {
        'id': 'volume-id' + uuid.uuid4().hex,
        'name': 'volume-name' + uuid.uuid4().hex,
        'description': 'description' + uuid.uuid4().hex,
        'status': random.choice(['available', 'in_use']),
        'size': random.randint(1, 20),
        'volume_type': random.choice(['fake_lvmdriver-1', 'fake_lvmdriver-2']),
        'bootable': random.choice(['true', 'false']),
        'metadata': {
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
        },
        'snapshot_id': random.randint(1, 5),
        'availability_zone': 'zone' + uuid.uuid4().hex,
        'attachments': [
            {
                'device': '/dev/' + uuid.uuid4().hex,
                'server_id': uuid.uuid4().hex,
            },
        ],
    }

    # Overwrite default attributes if there are some attributes set
    volume_info.update(attrs)
    return _volume.Volume(**volume_info)


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


def create_one_qos(attrs=None):
    """Create a fake Qos specification.

    :param dict attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with id, name, consumer, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    qos_info = {
        "id": 'qos-id-' + uuid.uuid4().hex,
        "name": 'qos-name-' + uuid.uuid4().hex,
        "consumer": 'front-end',
        "specs": {"foo": "bar", "iops": "9001"},
    }

    # Overwrite default attributes.
    qos_info.update(attrs)

    qos = fakes.FakeResource(info=copy.deepcopy(qos_info), loaded=True)
    return qos


def create_one_qos_association(attrs=None):
    """Create a fake Qos specification association.

    :param dict attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with id, name, association_type, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    qos_association_info = {
        "id": 'type-id-' + uuid.uuid4().hex,
        "name": 'type-name-' + uuid.uuid4().hex,
        "association_type": 'volume_type',
    }

    # Overwrite default attributes.
    qos_association_info.update(attrs)

    qos_association = fakes.FakeResource(
        info=copy.deepcopy(qos_association_info), loaded=True
    )
    return qos_association


def create_qoses(attrs=None, count=2):
    """Create multiple fake Qos specifications.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of Qos specifications to fake
    :return:
        A list of FakeResource objects faking the Qos specifications
    """
    qoses = []
    for i in range(0, count):
        qos = create_one_qos(attrs)
        qoses.append(qos)

    return qoses


def get_qoses(qoses=None, count=2):
    """Get an iterable MagicMock object with a list of faked qoses.

    If qoses list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List qoses:
        A list of FakeResource objects faking qoses
    :param Integer count:
        The number of qoses to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        qoses
    """
    if qoses is None:
        qoses = create_qoses(count)

    return mock.Mock(side_effect=qoses)


def create_one_volume_type(attrs=None, methods=None):
    """Create a fake volume type.

    :param dict attrs:
        A dictionary with all attributes
    :param dict methods:
        A dictionary with all methods
    :return:
        A FakeResource object with id, name, description, etc.
    """
    attrs = attrs or {}
    methods = methods or {}

    # Set default attributes.
    volume_type_info = {
        "id": 'type-id-' + uuid.uuid4().hex,
        "name": 'type-name-' + uuid.uuid4().hex,
        "description": 'type-description-' + uuid.uuid4().hex,
        "extra_specs": {"foo": "bar"},
        "is_public": True,
    }

    # Overwrite default attributes.
    volume_type_info.update(attrs)

    volume_type = fakes.FakeResource(
        info=copy.deepcopy(volume_type_info), methods=methods, loaded=True
    )
    return volume_type


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
