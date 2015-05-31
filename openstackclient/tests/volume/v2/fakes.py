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
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests import utils

volume_id = "ce26708d-a7f8-4b4b-9861-4a80256615a6"
volume_name = "fake_volume"
volume_description = "fake description"
volume_status = "available"
volume_size = 20
volume_type = "fake_lvmdriver-1"
volume_metadata = {
    "foo": "bar"
}
volume_snapshot_id = 1
volume_availability_zone = "nova"
volume_attachments = ["fake_attachments"]

VOLUME = {
    "id": volume_id,
    "name": volume_name,
    "description": volume_description,
    "status": volume_status,
    "size": volume_size,
    "volume_type": volume_type,
    "metadata": volume_metadata,
    "snapshot_id": volume_snapshot_id,
    "availability_zone": volume_availability_zone,
    "attachments": volume_attachments
}

VOLUME_columns = tuple(sorted(VOLUME))
VOLUME_data = tuple((VOLUME[x] for x in sorted(VOLUME)))


snapshot_id = "cb2d364e-4d1c-451a-8c68-b5bbcb340fb2"
snapshot_name = "fake_snapshot"
snapshot_description = "fake description"
snapshot_size = 10
snapshot_metadata = {
    "foo": "bar"
}
snapshot_volume_id = "bdbae8dc-e6ca-43c0-8076-951cc1b093a4"

SNAPSHOT = {
    "id": snapshot_id,
    "name": snapshot_name,
    "description": snapshot_description,
    "size": snapshot_size,
    "metadata": snapshot_metadata
}

SNAPSHOT_columns = tuple(sorted(SNAPSHOT))
SNAPSHOT_data = tuple((SNAPSHOT[x] for x in sorted(SNAPSHOT)))


type_id = "5520dc9e-6f9b-4378-a719-729911c0f407"
type_description = "fake description"
type_name = "fake-lvmdriver-1"
type_extra_specs = {
    "foo": "bar"
}

TYPE = {
    'id': type_id,
    'name': type_name,
    'description': type_description,
    'extra_specs': type_extra_specs
}

TYPE_columns = tuple(sorted(TYPE))
TYPE_data = tuple((TYPE[x] for x in sorted(TYPE)))

backup_id = "3c409fe6-4d03-4a06-aeab-18bdcdf3c8f4"
backup_volume_id = "bdbae8dc-e6ca-43c0-8076-951cc1b093a4"
backup_name = "fake_backup"
backup_description = "fake description"
backup_object_count = None
backup_container = None
backup_size = 10

BACKUP = {
    "id": backup_id,
    "name": backup_name,
    "volume_id": backup_volume_id,
    "description": backup_description,
    "object_count": backup_object_count,
    "container": backup_container,
    "size": backup_size
}

BACKUP_columns = tuple(sorted(BACKUP))
BACKUP_data = tuple((BACKUP[x] for x in sorted(BACKUP)))


class FakeVolumeClient(object):
    def __init__(self, **kwargs):
        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})
        self.volume_snapshots = mock.Mock()
        self.volume_snapshots.resource_class = fakes.FakeResource(None, {})
        self.backups = mock.Mock()
        self.backups.resource_class = fakes.FakeResource(None, {})
        self.volume_types = mock.Mock()
        self.volume_types.resource_class = fakes.FakeResource(None, {})
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestVolume(utils.TestCommand):
    def setUp(self):
        super(TestVolume, self).setUp()

        self.app.client_manager.volume = FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN
        )
