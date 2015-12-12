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

from openstackclient.network.v2 import router
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestRouter(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestRouter, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestListRouter(TestRouter):

    # The routers going to be listed up.
    routers = network_fakes.FakeRouter.create_routers(count=3)

    columns = (
        'ID',
        'Name',
        'Status',
        'State',
        'Distributed',
        'HA',
        'Project',
    )
    columns_long = columns + (
        'Routes',
        'External gateway info',
    )

    data = []
    for r in routers:
        data.append((
            r.id,
            r.name,
            r.status,
            router._format_admin_state(r.admin_state_up),
            r.distributed,
            r.ha,
            r.tenant_id,
        ))
    data_long = []
    for i in range(0, len(routers)):
        r = routers[i]
        data_long.append(
            data[i] + (
                r.routes,
                router._format_external_gateway_info(r.external_gateway_info),
            )
        )

    def setUp(self):
        super(TestListRouter, self).setUp()

        # Get the command object to test
        self.cmd = router.ListRouter(self.app, self.namespace)

        self.network.routers = mock.Mock(return_value=self.routers)

    def test_router_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.routers.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_router_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.routers.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))
