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

from openstackclient.common import exceptions
from openstackclient.common import utils as osc_utils
from openstackclient.network.v2 import router
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestRouter(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestRouter, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestCreateRouter(TestRouter):

    # The new router created.
    new_router = network_fakes.FakeRouter.create_one_router()

    columns = (
        'admin_state_up',
        'distributed',
        'ha',
        'id',
        'name',
        'project_id',
    )
    data = (
        router._format_admin_state(new_router.admin_state_up),
        new_router.distributed,
        new_router.ha,
        new_router.id,
        new_router.name,
        new_router.tenant_id,
    )

    def setUp(self):
        super(TestCreateRouter, self).setUp()

        self.network.create_router = mock.Mock(return_value=self.new_router)

        # Get the command object to test
        self.cmd = router.CreateRouter(self.app, self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        try:
            self.check_parser(self.cmd, arglist, verifylist)
        except tests_utils.ParserException:
            pass

    def test_create_default_options(self):
        arglist = [
            self.new_router.name,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('admin_state_up', True),
            ('distributed', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_router.assert_called_with(**{
            'admin_state_up': True,
            'name': self.new_router.name,
            'distributed': False,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_AZ_hints(self):
        arglist = [
            self.new_router.name,
            '--availability-zone-hint', 'fake-az',
            '--availability-zone-hint', 'fake-az2',
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('availability_zone_hints', ['fake-az', 'fake-az2']),
            ('admin_state_up', True),
            ('distributed', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = (self.cmd.take_action(parsed_args))
        self.network.create_router.assert_called_with(**{
            'admin_state_up': True,
            'name': self.new_router.name,
            'distributed': False,
            'availability_zone_hints': ['fake-az', 'fake-az2'],
        })

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteRouter(TestRouter):

    # The router to delete.
    _router = network_fakes.FakeRouter.create_one_router()

    def setUp(self):
        super(TestDeleteRouter, self).setUp()

        self.network.delete_router = mock.Mock(return_value=None)

        self.network.find_router = mock.Mock(return_value=self._router)

        # Get the command object to test
        self.cmd = router.DeleteRouter(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._router.name,
        ]
        verifylist = [
            ('router', [self._router.name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.delete_router.assert_called_with(self._router)
        self.assertIsNone(result)


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
        'Availability zones'
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
                osc_utils.format_list(r.availability_zones),
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


class TestSetRouter(TestRouter):

    # The router to set.
    _router = network_fakes.FakeRouter.create_one_router()

    def setUp(self):
        super(TestSetRouter, self).setUp()

        self.network.update_router = mock.Mock(return_value=None)

        self.network.find_router = mock.Mock(return_value=self._router)

        # Get the command object to test
        self.cmd = router.SetRouter(self.app, self.namespace)

    def test_set_this(self):
        arglist = [
            self._router.name,
            '--enable',
            '--distributed',
            '--name', 'noob',
        ]
        verifylist = [
            ('router', self._router.name),
            ('admin_state_up', True),
            ('distributed', True),
            ('name', 'noob'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': True,
            'distributed': True,
            'name': 'noob',
        }
        self.network.update_router.assert_called_with(self._router, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            self._router.name,
            '--disable',
            '--centralized',
        ]
        verifylist = [
            ('router', self._router.name),
            ('admin_state_up', False),
            ('distributed', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'distributed': False,
        }
        self.network.update_router.assert_called_with(self._router, **attrs)
        self.assertIsNone(result)

    def test_set_distributed_centralized(self):
        arglist = [
            self._router.name,
            '--distributed',
            '--centralized',
        ]
        verifylist = [
            ('router', self._router.name),
            ('distributed', True),
            ('distributed', False),
        ]

        try:
            # Argument parse failing should bail here
            self.check_parser(self.cmd, arglist, verifylist)
        except tests_utils.ParserException:
            pass

    def test_set_nothing(self):
        arglist = [self._router.name, ]
        verifylist = [('router', self._router.name), ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)


class TestShowRouter(TestRouter):

    # The router to set.
    _router = network_fakes.FakeRouter.create_one_router()

    columns = (
        'admin_state_up',
        'distributed',
        'ha',
        'id',
        'name',
        'tenant_id',
    )

    data = (
        router._format_admin_state(_router.admin_state_up),
        _router.distributed,
        _router.ha,
        _router.id,
        _router.name,
        _router.tenant_id,
    )

    def setUp(self):
        super(TestShowRouter, self).setUp()

        self.network.find_router = mock.Mock(return_value=self._router)

        # Get the command object to test
        self.cmd = router.ShowRouter(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        try:
            # Missing required args should bail here
            self.check_parser(self.cmd, arglist, verifylist)
        except tests_utils.ParserException:
            pass

    def test_show_all_options(self):
        arglist = [
            self._router.name,
        ]
        verifylist = [
            ('router', self._router.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_router.assert_called_with(self._router.name,
                                                    ignore_missing=False)
        self.assertEqual(tuple(self.columns), columns)
        self.assertEqual(self.data, data)
