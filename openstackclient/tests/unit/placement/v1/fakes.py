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
from openstack.placement import v1 as placement_v1

from openstackclient.tests.unit import utils


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        # TODO(stephenfin): Switch to spec_set once keystoneauth exposes
        # instance attributes as class attributes
        # https://review.opendev.org/c/openstack/keystoneauth/+/994090
        self.app.client_manager.placement = mock.Mock(spec=placement_v1.Proxy)
        self.app.client_manager.sdk_connection.placement = (
            self.app.client_manager.placement
        )
        self.placement_client = self.app.client_manager.placement
        self.set_placement_api_version()  # default to the lowest

    def set_placement_api_version(self, version: str = '1.0'):
        """Set a fake server version.

        :param version: The fake microversion to "support". This should be a
            string of format '1.xx'.
        :returns: None
        """
        assert re.match(r'1.\d+', version)

        self.placement_client.default_microversion = version
        self.placement_client.get_endpoint_data.return_value = (
            discover.EndpointData(
                min_microversion='1.0',  # placement has not bumped this yet
                max_microversion=version,
            )
        )


class TestPlacement(FakeClientMixin, utils.TestCommand): ...
