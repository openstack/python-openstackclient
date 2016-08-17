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
import mock
import random
import uuid

from osc_lib import utils as common_utils

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils


QUOTA = {
    "gigabytes": 1000,
    "volumes": 11,
    "snapshots": 10,
    "backups": 10,
    "backup_gigabytes": 1000,
    "per_volume_gigabytes": -1,
    "gigabytes_volume_type_backend": -1,
    "volumes_volume_type_backend": -1,
    "snapshots_volume_type_backend": -1,
}


class FakeTransfer(object):
    """Fake one or more Transfer."""

    @staticmethod
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

        transfer = fakes.FakeResource(
            None,
            transfer_info,
            loaded=True)

        return transfer

    @staticmethod
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
            transfers.append(FakeTransfer.create_one_transfer(attrs))

        return transfers

    @staticmethod
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
            transfers = FakeTransfer.create_transfers(count)

        return mock.Mock(side_effect=transfers)


class FakeTypeAccess(object):
    """Fake one or more volume type access."""

    @staticmethod
    def create_one_type_access(attrs=None):
        """Create a fake volume type access for project.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with  Volume_type_ID and Project_ID.
        """
        if attrs is None:
            attrs = {}

        # Set default attributes.
        type_access_attrs = {
            'volume_type_id': 'volume-type-id-' + uuid.uuid4().hex,
            'project_id': 'project-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        type_access_attrs.update(attrs)

        type_access = fakes.FakeResource(
            None,
            type_access_attrs,
            loaded=True)

        return type_access


class FakeService(object):
    """Fake one or more Services."""

    @staticmethod
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

        service = fakes.FakeResource(
            None,
            service_info,
            loaded=True)

        return service

    @staticmethod
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
            services.append(FakeService.create_one_service(attrs))

        return services


class FakeVolumeClient(object):

    def __init__(self, **kwargs):
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})
        self.volume_snapshots = mock.Mock()
        self.volume_snapshots.resource_class = fakes.FakeResource(None, {})
        self.backups = mock.Mock()
        self.backups.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.volume_type_access = mock.Mock()
        self.volume_type_access.resource_class = fakes.FakeResource(None, {})
        self.restores = mock.Mock()
        self.restores.resource_class = fakes.FakeResource(None, {})
        self.qos_specs = mock.Mock()
        self.qos_specs.resource_class = fakes.FakeResource(None, {})
        self.availability_zones = mock.Mock()
        self.availability_zones.resource_class = fakes.FakeResource(None, {})
        self.transfers = mock.Mock()
        self.transfers.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
        self.quotas = mock.Mock()
        self.quotas.resource_class = fakes.FakeResource(None, {})
        self.quota_classes = mock.Mock()
        self.quota_classes.resource_class = fakes.FakeResource(None, {})
        self.consistencygroups = mock.Mock()
        self.consistencygroups.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestVolume(utils.TestCommand):

    def setUp(self):
        super(TestVolume, self).setUp()

        self.app.client_manager.volume = FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.identity = identity_fakes.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.image = image_fakes.FakeImagev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )


class FakeVolume(object):
    """Fake one or more volumes.

    TODO(xiexs): Currently, only volume API v2 is supported by this class.
    """

    @staticmethod
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
            'name': 'volume-name' + uuid.uuid4().hex,
            'description': 'description' + uuid.uuid4().hex,
            'status': random.choice(['available', 'in_use']),
            'size': random.randint(1, 20),
            'volume_type':
                random.choice(['fake_lvmdriver-1', 'fake_lvmdriver-2']),
            'bootable':
                random.randint(0, 1),
            'metadata': {
                'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
                'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex,
                'key' + uuid.uuid4().hex: 'val' + uuid.uuid4().hex},
            'snapshot_id': random.randint(1, 5),
            'availability_zone': 'zone' + uuid.uuid4().hex,
            'attachments': [{
                'device': '/dev/' + uuid.uuid4().hex,
                'server_id': uuid.uuid4().hex,
            }, ],
        }

        # Overwrite default attributes if there are some attributes set
        volume_info.update(attrs)

        volume = fakes.FakeResource(
            None,
            volume_info,
            loaded=True)
        return volume

    @staticmethod
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
            volumes.append(FakeVolume.create_one_volume(attrs))

        return volumes

    @staticmethod
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
            volumes = FakeVolume.create_volumes(count)

        return mock.Mock(side_effect=volumes)

    @staticmethod
    def get_volume_columns(volume=None):
        """Get the volume columns from a faked volume object.

        :param volume:
            A FakeResource objects faking volume
        :return
            A tuple which may include the following keys:
            ('id', 'name', 'description', 'status', 'size', 'volume_type',
             'metadata', 'snapshot', 'availability_zone', 'attachments')
        """
        if volume is not None:
            return tuple(k for k in sorted(volume.keys()))
        return tuple([])

    @staticmethod
    def get_volume_data(volume=None):
        """Get the volume data from a faked volume object.

        :param volume:
            A FakeResource objects faking volume
        :return
            A tuple which may include the following values:
            ('ce26708d', 'fake_volume', 'fake description', 'available',
             20, 'fake_lvmdriver-1', "Alpha='a', Beta='b', Gamma='g'",
             1, 'nova', [{'device': '/dev/ice', 'server_id': '1233'}])
        """
        data_list = []
        if volume is not None:
            for x in sorted(volume.keys()):
                if x == 'tags':
                    # The 'tags' should be format_list
                    data_list.append(
                        common_utils.format_list(volume.info.get(x)))
                else:
                    data_list.append(volume.info.get(x))
        return tuple(data_list)


class FakeAvailabilityZone(object):
    """Fake one or more volume availability zones (AZs)."""

    @staticmethod
    def create_one_availability_zone(attrs=None):
        """Create a fake AZ.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with zoneName, zoneState, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        availability_zone = {
            'zoneName': uuid.uuid4().hex,
            'zoneState': {'available': True},
        }

        # Overwrite default attributes.
        availability_zone.update(attrs)

        availability_zone = fakes.FakeResource(
            info=copy.deepcopy(availability_zone),
            loaded=True)
        return availability_zone

    @staticmethod
    def create_availability_zones(attrs=None, count=2):
        """Create multiple fake AZs.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of AZs to fake
        :return:
            A list of FakeResource objects faking the AZs
        """
        availability_zones = []
        for i in range(0, count):
            availability_zone = \
                FakeAvailabilityZone.create_one_availability_zone(attrs)
            availability_zones.append(availability_zone)

        return availability_zones


class FakeBackup(object):
    """Fake one or more backup."""

    @staticmethod
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
        }

        # Overwrite default attributes.
        backup_info.update(attrs)

        backup = fakes.FakeResource(
            info=copy.deepcopy(backup_info),
            loaded=True)
        return backup

    @staticmethod
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
            backup = FakeBackup.create_one_backup(attrs)
            backups.append(backup)

        return backups

    @staticmethod
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
            backups = FakeBackup.create_backups(count)

        return mock.Mock(side_effect=backups)


class FakeConsistencyGroup(object):
    """Fake one or more consistency group."""

    @staticmethod
    def create_one_consistency_group(attrs=None):
        """Create a fake consistency group.

        :param Dictionary attrs:
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
            info=copy.deepcopy(consistency_group_info),
            loaded=True)
        return consistency_group

    @staticmethod
    def create_consistency_groups(attrs=None, count=2):
        """Create multiple fake consistency groups.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of consistency groups to fake
        :return:
            A list of FakeResource objects faking the consistency groups
        """
        consistency_groups = []
        for i in range(0, count):
            consistency_group = (
                FakeConsistencyGroup.create_one_consistency_group(attrs))
            consistency_groups.append(consistency_group)

        return consistency_groups


class FakeExtension(object):
    """Fake one or more extension."""

    @staticmethod
    def create_one_extension(attrs=None):
        """Create a fake extension.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, namespace, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        extension_info = {
            'name': 'name-' + uuid.uuid4().hex,
            'namespace': ('http://docs.openstack.org/'
                          'block-service/ext/scheduler-hints/api/v2'),
            'description': 'description-' + uuid.uuid4().hex,
            'updated': '2013-04-18T00:00:00+00:00',
            'alias': 'OS-SCH-HNT',
            'links': ('[{"href":'
                      '"https://github.com/openstack/block-api", "type":'
                      ' "text/html", "rel": "describedby"}]'),
        }

        # Overwrite default attributes.
        extension_info.update(attrs)

        extension = fakes.FakeResource(
            info=copy.deepcopy(extension_info),
            loaded=True)
        return extension


class FakeQos(object):
    """Fake one or more Qos specification."""

    @staticmethod
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

        qos = fakes.FakeResource(
            info=copy.deepcopy(qos_info),
            loaded=True)
        return qos

    @staticmethod
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
            info=copy.deepcopy(qos_association_info),
            loaded=True)
        return qos_association

    @staticmethod
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
            qos = FakeQos.create_one_qos(attrs)
            qoses.append(qos)

        return qoses

    @staticmethod
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
            qoses = FakeQos.create_qoses(count)

        return mock.Mock(side_effect=qoses)


class FakeSnapshot(object):
    """Fake one or more snapshot."""

    @staticmethod
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
            "name": 'snapshot-name-' + uuid.uuid4().hex,
            "description": 'snapshot-description-' + uuid.uuid4().hex,
            "size": 10,
            "status": "available",
            "metadata": {"foo": "bar"},
            "created_at": "2015-06-03T18:49:19.000000",
            "volume_id": 'vloume-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        snapshot_info.update(attrs)

        snapshot = fakes.FakeResource(
            info=copy.deepcopy(snapshot_info),
            loaded=True)
        return snapshot

    @staticmethod
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
            snapshot = FakeSnapshot.create_one_snapshot(attrs)
            snapshots.append(snapshot)

        return snapshots

    @staticmethod
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
            snapshots = FakeSnapshot.create_snapshots(count)

        return mock.Mock(side_effect=snapshots)


class FakeType(object):
    """Fake one or more type."""

    @staticmethod
    def create_one_type(attrs=None, methods=None):
        """Create a fake type.

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
        type_info = {
            "id": 'type-id-' + uuid.uuid4().hex,
            "name": 'type-name-' + uuid.uuid4().hex,
            "description": 'type-description-' + uuid.uuid4().hex,
            "extra_specs": {"foo": "bar"},
            "is_public": True,
        }

        # Overwrite default attributes.
        type_info.update(attrs)

        volume_type = fakes.FakeResource(
            info=copy.deepcopy(type_info),
            methods=methods,
            loaded=True)
        return volume_type

    @staticmethod
    def create_types(attrs=None, count=2):
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
            volume_type = FakeType.create_one_type(attrs)
            volume_types.append(volume_type)

        return volume_types
