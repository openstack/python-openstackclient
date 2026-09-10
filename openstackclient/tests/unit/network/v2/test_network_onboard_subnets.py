# Copyright (c) 2019 SUSE Linux Products GmbH
# All Rights Reserved
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
#

from openstack.network.v2 import network as _network
from openstack.network.v2 import subnet_pool as _subnet_pool

from openstackclient.network.v2 import subnet_onboard
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestNetworkOnboardSubnets(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._subnet_pool = _subnet_pool.SubnetPool(
            id='my_subnetpool_id', name='my_subnetpool'
        )
        self._network = _network.Network(id='my_network_id', name='my_network')

        self.network_client.find_subnet_pool.return_value = self._subnet_pool
        self.network_client.find_network.return_value = self._network

        self.cmd = subnet_onboard.NetworkOnboardSubnets(self.app, None)

    def test_onboard_subnets(self):
        arglist = ['my_network', 'my_subnetpool']
        verifylist = [
            ('network', 'my_network'),
            ('subnetpool', 'my_subnetpool'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_called_once_with(
            'my_network', ignore_missing=False
        )
        self.network_client.find_subnet_pool.assert_called_once_with(
            'my_subnetpool', ignore_missing=False
        )
        self.network_client.onboard_network_subnets.assert_called_once_with(
            self._subnet_pool, self._network
        )
