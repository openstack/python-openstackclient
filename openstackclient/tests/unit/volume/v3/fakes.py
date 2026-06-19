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

import re
from unittest import mock

from cinderclient import api_versions
from keystoneauth1 import discover
from openstack.block_storage import v3 as block_storage_v3
from openstack.compute import v2 as compute_v2
from openstack.image import v2 as image_v2

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class FakeVolumeClient:
    def __init__(self, **kwargs):
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']
        self.api_version = api_versions.APIVersion('3.0')

        self.clusters = mock.Mock()
        self.clusters.resource_class = fakes.FakeResource(None, {})
        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})
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
            spec=block_storage_v3.Proxy
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
        # TODO(stephenfin): Switch to spec_set once keystoneauth exposes
        # instance attributes as class attributes
        # https://review.opendev.org/c/openstack/keystoneauth/+/994090
        self.app.client_manager.compute = mock.Mock(spec=compute_v2.Proxy)
        self.compute_client = self.app.client_manager.compute

        # avoid circular imports by defining this manually rather than using
        # openstackclient.tests.unit.image.v2.fakes.FakeClientMixin
        # TODO(stephenfin): Switch to spec_set once keystoneauth exposes
        # instance attributes as class attributes
        # https://review.opendev.org/c/openstack/keystoneauth/+/994090
        self.app.client_manager.image = mock.Mock(spec=image_v2.Proxy)
        self.image_client = self.app.client_manager.image
