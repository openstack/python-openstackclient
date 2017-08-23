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

import json

from openstackclient.tests.functional.network.v2 import common


class TestNetworkServiceProvider(common.NetworkTests):
    """Functional tests for network service provider"""

    def setUp(self):
        super(TestNetworkServiceProvider, self).setUp()
        # Nothing in this class works with Nova Network
        if not self.haz_network:
            self.skipTest("No Network service present")

    def test_network_service_provider_list(self):
        cmd_output = json.loads(self.openstack(
            'network service provider list -f json'))
        self.assertIn('L3_ROUTER_NAT', [x['Service Type'] for x in cmd_output])
