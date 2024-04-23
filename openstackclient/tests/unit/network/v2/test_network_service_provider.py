# Copyright (c) 2016, Intel Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from unittest import mock

from openstackclient.network.v2 import (
    network_service_provider as service_provider,
)
from openstackclient.tests.unit.network.v2 import fakes


class TestNetworkServiceProvider(fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()


class TestListNetworkServiceProvider(TestNetworkServiceProvider):
    provider_list = (
        fakes.FakeNetworkServiceProvider.create_network_service_providers(
            count=2
        )
    )

    columns = (
        'Service Type',
        'Name',
        'Default',
    )

    data = []

    for provider in provider_list:
        data.append(
            (
                provider.service_type,
                provider.name,
                provider.is_default,
            )
        )

    def setUp(self):
        super().setUp()
        self.network_client.service_providers = mock.Mock(
            return_value=self.provider_list
        )

        self.cmd = service_provider.ListNetworkServiceProvider(self.app, None)

    def test_network_service_provider_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.service_providers.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
