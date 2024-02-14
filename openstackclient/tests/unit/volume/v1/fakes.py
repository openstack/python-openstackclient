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
from unittest import mock
import uuid

from openstack.image.v1 import _proxy as image_v1_proxy

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class FakeVolumev1Client:
    def __init__(self, **kwargs):
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.qos_specs = mock.Mock()
        self.qos_specs.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.volume_encryption_types = mock.Mock()
        self.volume_encryption_types.resource_class = fakes.FakeResource(
            None, {}
        )
        self.transfers = mock.Mock()
        self.transfers.resource_class = fakes.FakeResource(None, {})
        self.volume_snapshots = mock.Mock()
        self.volume_snapshots.resource_class = fakes.FakeResource(None, {})
        self.backups = mock.Mock()
        self.backups.resource_class = fakes.FakeResource(None, {})
        self.restores = mock.Mock()
        self.restores.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.volume = FakeVolumev1Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.volume_client = self.app.client_manager.volume


class TestVolumev1(
    identity_fakes.FakeClientMixin,
    FakeClientMixin,
    utils.TestCommand,
):
    def setUp(self):
        super().setUp()

        # avoid circular imports by defining this manually rather than using
        # openstackclient.tests.unit.image.v1.fakes.FakeClientMixin
        self.app.client_manager.image = mock.Mock(spec=image_v1_proxy.Proxy)
        self.image_client = self.app.client_manager.image


def create_one_transfer(attrs=None):
    """Create a fake transfer.

    :param Dictionary attrs:
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

    :param Dictionary attrs:
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


def create_one_service(attrs=None):
    """Create a fake service.

    :param Dictionary attrs:
        A dictionary with all attributes of service
    :return:
        A FakeResource object with host, status, etc.
    """
    # Set default attribute
    service_info = {
        'host': 'host_test',
        'binary': 'cinder_test',
        'status': 'enabled',
        'disabled_reason': 'LongHoliday-GoldenWeek',
        'zone': 'fake_zone',
        'updated_at': 'fake_date',
        'state': 'fake_state',
    }

    # Overwrite default attributes if there are some attributes set
    attrs = attrs or {}

    service_info.update(attrs)

    service = fakes.FakeResource(None, service_info, loaded=True)

    return service


def create_services(attrs=None, count=2):
    """Create multiple fake services.

    :param Dictionary attrs:
        A dictionary with all attributes of service
    :param Integer count:
        The number of services to be faked
    :return:
        A list of FakeResource objects
    """
    services = []
    for n in range(0, count):
        services.append(create_one_service(attrs))

    return services


def get_services(services=None, count=2):
    """Get an iterable MagicMock object with a list of faked services.

    If services list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List services:
        A list of FakeResource objects faking services
    :param Integer count:
        The number of services to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        services
    """
    if services is None:
        services = create_services(count)

    return mock.Mock(side_effect=services)


def create_one_qos(attrs=None):
    """Create a fake Qos specification.

    :param Dictionary attrs:
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

    :param Dictionary attrs:
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

    :param Dictionary attrs:
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

    :param List volumes:
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


def create_one_volume(attrs=None):
    """Create a fake volume.

    :param Dictionary attrs:
        A dictionary with all attributes of volume
    :return:
        A FakeResource object with id, name, status, etc.
    """
    attrs = attrs or {}

    # Set default attribute
    volume_info = {
        'id': 'volume-id' + uuid.uuid4().hex,
        'display_name': 'volume-name' + uuid.uuid4().hex,
        'display_description': 'description' + uuid.uuid4().hex,
        'status': 'available',
        'size': 10,
        'volume_type': random.choice(['fake_lvmdriver-1', 'fake_lvmdriver-2']),
        'bootable': 'true',
        'metadata': {
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
            'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
        },
        'snapshot_id': 'snapshot-id-' + uuid.uuid4().hex,
        'availability_zone': 'zone' + uuid.uuid4().hex,
        'attachments': [
            {
                'device': '/dev/' + uuid.uuid4().hex,
                'server_id': uuid.uuid4().hex,
            },
        ],
        'created_at': 'time-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes if there are some attributes set
    volume_info.update(attrs)

    volume = fakes.FakeResource(None, volume_info, loaded=True)
    return volume


def create_volumes(attrs=None, count=2):
    """Create multiple fake volumes.

    :param Dictionary attrs:
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


def create_one_volume_type(attrs=None, methods=None):
    """Create a fake volume type.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param Dictionary methods:
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


def create_volume_types(attrs=None, count=2):
    """Create multiple fake types.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of types to fake
    :return:
        A list of FakeResource objects faking the types
    """
    volume_types = []
    for i in range(0, count):
        volume_type = create_one_volume_type(attrs)
        volume_types.append(volume_type)

    return volume_types


def get_volume_types(volume_types=None, count=2):
    """Get an iterable MagicMock object with a list of faked types.

    If types list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List volume_types:
        A list of FakeResource objects faking types
    :param Integer count:
        The number of types to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        types
    """
    if volume_types is None:
        volume_types = create_volume_types(count)

    return mock.Mock(side_effect=volume_types)


def create_one_encryption_volume_type(attrs=None):
    """Create a fake encryption volume type.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with volume_type_id etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    encryption_info = {
        "volume_type_id": 'type-id-' + uuid.uuid4().hex,
        'provider': 'LuksEncryptor',
        'cipher': None,
        'key_size': None,
        'control_location': 'front-end',
    }

    # Overwrite default attributes.
    encryption_info.update(attrs)

    encryption_type = fakes.FakeResource(
        info=copy.deepcopy(encryption_info), loaded=True
    )
    return encryption_type


def create_one_snapshot(attrs=None):
    """Create a fake snapshot.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with id, name, description, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    snapshot_info = {
        "id": 'snapshot-id-' + uuid.uuid4().hex,
        "display_name": 'snapshot-name-' + uuid.uuid4().hex,
        "display_description": 'snapshot-description-' + uuid.uuid4().hex,
        "size": 10,
        "status": "available",
        "metadata": {"foo": "bar"},
        "created_at": "2015-06-03T18:49:19.000000",
        "volume_id": 'vloume-id-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    snapshot_info.update(attrs)

    snapshot_method = {'update': None}

    snapshot = fakes.FakeResource(
        info=copy.deepcopy(snapshot_info),
        methods=copy.deepcopy(snapshot_method),
        loaded=True,
    )
    return snapshot


def create_snapshots(attrs=None, count=2):
    """Create multiple fake snapshots.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of snapshots to fake
    :return:
        A list of FakeResource objects faking the snapshots
    """
    snapshots = []
    for i in range(0, count):
        snapshot = create_one_snapshot(attrs)
        snapshots.append(snapshot)

    return snapshots


def get_snapshots(snapshots=None, count=2):
    """Get an iterable MagicMock object with a list of faked snapshots.

    If snapshots list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List volumes:
        A list of FakeResource objects faking snapshots
    :param Integer count:
        The number of snapshots to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        snapshots
    """
    if snapshots is None:
        snapshots = create_snapshots(count)

    return mock.Mock(side_effect=snapshots)


def create_one_backup(attrs=None):
    """Create a fake backup.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with id, name, volume_id, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    backup_info = {
        "id": 'backup-id-' + uuid.uuid4().hex,
        "name": 'backup-name-' + uuid.uuid4().hex,
        "volume_id": 'volume-id-' + uuid.uuid4().hex,
        "snapshot_id": 'snapshot-id' + uuid.uuid4().hex,
        "description": 'description-' + uuid.uuid4().hex,
        "object_count": None,
        "container": 'container-' + uuid.uuid4().hex,
        "size": random.randint(1, 20),
        "status": "error",
        "availability_zone": 'zone' + uuid.uuid4().hex,
        "links": 'links-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    backup_info.update(attrs)

    backup = fakes.FakeResource(info=copy.deepcopy(backup_info), loaded=True)
    return backup


def create_backups(attrs=None, count=2):
    """Create multiple fake backups.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of backups to fake
    :return:
        A list of FakeResource objects faking the backups
    """
    backups = []
    for i in range(0, count):
        backup = create_one_backup(attrs)
        backups.append(backup)

    return backups


def get_backups(backups=None, count=2):
    """Get an iterable MagicMock object with a list of faked backups.

    If backups list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List volumes:
        A list of FakeResource objects faking backups
    :param Integer count:
        The number of backups to be faked
    :return
        An iterable Mock object with side_effect set to a list of faked
        backups
    """
    if backups is None:
        backups = create_backups(count)

    return mock.Mock(side_effect=backups)
