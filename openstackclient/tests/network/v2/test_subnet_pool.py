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

from openstackclient.network.v2 import subnet_pool
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestSubnetPool(network_fakes.TestNetworkV2):
    def setUp(self):
        super(TestSubnetPool, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestDeleteSubnetPool(TestSubnetPool):

    # The subnet pool to delete.
    _subnet_pool = network_fakes.FakeSubnetPool.create_one_subnet_pool()

    def setUp(self):
        super(TestDeleteSubnetPool, self).setUp()

        self.network.delete_subnet_pool = mock.Mock(return_value=None)

        self.network.find_subnet_pool = mock.Mock(
            return_value=self._subnet_pool
        )

        # Get the command object to test
        self.cmd = subnet_pool.DeleteSubnetPool(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._subnet_pool.name,
        ]
        verifylist = [
            ('subnet_pool', self._subnet_pool.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_subnet_pool.assert_called_with(self._subnet_pool)
        self.assertIsNone(result)


class TestListSubnetPool(TestSubnetPool):
    # The subnet pools going to be listed up.
    _subnet_pools = network_fakes.FakeSubnetPool.create_subnet_pools(count=3)

    columns = (
        'ID',
        'Name',
        'Prefixes',
    )
    columns_long = columns + (
        'Default Prefix Length',
        'Address Scope',
    )

    data = []
    for pool in _subnet_pools:
        data.append((
            pool.id,
            pool.name,
            pool.prefixes,
        ))

    data_long = []
    for pool in _subnet_pools:
        data_long.append((
            pool.id,
            pool.name,
            pool.prefixes,
            pool.default_prefixlen,
            pool.address_scope_id,
        ))

    def setUp(self):
        super(TestListSubnetPool, self).setUp()

        # Get the command object to test
        self.cmd = subnet_pool.ListSubnetPool(self.app, self.namespace)

        self.network.subnet_pools = mock.Mock(return_value=self._subnet_pools)

    def test_subnet_pool_list_no_option(self):
        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.subnet_pools.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_subnet_pool_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.subnet_pools.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))
