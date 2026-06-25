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

from keystoneauth1 import discover
from openstack.block_storage import v3 as block_storage_v3
from openstack.compute import v2 as compute_v2
from openstack.image import v2 as image_v2

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        # TODO(stephenfin): Rename to 'volume_client' now that all commands are
        # migrated to SDK
        self.app.client_manager.volume = mock.Mock(spec=block_storage_v3.Proxy)
        self.app.client_manager.volume.api_version = '3'
        self.volume_sdk_client = self.app.client_manager.volume
        self.set_volume_api_version()  # default to the lowest

    def set_volume_api_version(self, version: str = '3.0'):
        """Set a fake block storage API version.

        :param version: The fake microversion to "support". This should be a
            string of format '3.xx'.
        :returns: None
        """
        assert re.match(r'3.\d+', version)

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
