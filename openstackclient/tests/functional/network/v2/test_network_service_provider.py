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

from openstackclient.tests.functional import base


class TestNetworkServiceProvider(base.TestCase):
    """Functional tests for network service provider"""

    SERVICE_TYPE = 'L3_ROUTER_NAT'

    def test_network_service_provider_list(self):
        raw_output = self.openstack('network service provider list')
        self.assertIn(self.SERVICE_TYPE, raw_output)
