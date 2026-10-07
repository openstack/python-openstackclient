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

from unittest import mock

from keystoneauth1 import discover
from openstack.accelerator import v2 as accelerator_v2

from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.accelerator = mock.Mock(
            spec=accelerator_v2.Proxy
        )
        self.accelerator_client = self.app.client_manager.accelerator
        self.set_accelerator_api_version()

    def set_accelerator_api_version(self, version: str = '2.0'):
        self.accelerator_client.default_microversion = version
        self.accelerator_client.get_endpoint_data.return_value = (
            discover.EndpointData(
                min_microversion='2.0',
                max_microversion=version,
            )
        )


class TestAccelerator(
    image_fakes.FakeClientMixin,
    FakeClientMixin,
    utils.TestCommand,
): ...
