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

from unittest import mock
from unittest.mock import call

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.network.v2 import router
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestRouter(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.projects_mock = self.identity_client.projects


class TestAddPortToRouter(TestRouter):
    '''Add port to Router'''

    _port = network_fakes.create_one_port()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'port': _port.id}
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_router = mock.Mock(return_value=self._router)
        self.network_client.find_port = mock.Mock(return_value=self._port)

        self.cmd = router.AddPortToRouter(self.app, None)

    def test_add_port_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_add_port_required_options(self):
        arglist = [
            self._router.id,
            self._router.port,
        ]
        verifylist = [
            ('router', self._router.id),
            ('port', self._router.port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.add_interface_to_router.assert_called_with(
            self._router,
            **{
                'port_id': self._router.port,
            },
        )
        self.assertIsNone(result)


class TestAddSubnetToRouter(TestRouter):
    '''Add subnet to Router'''

    _subnet = network_fakes.FakeSubnet.create_one_subnet()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'subnet': _subnet.id}
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_router = mock.Mock(return_value=self._router)
        self.network_client.find_subnet = mock.Mock(return_value=self._subnet)

        self.cmd = router.AddSubnetToRouter(self.app, None)

    def test_add_subnet_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_add_subnet_required_options(self):
        arglist = [
            self._router.id,
            self._router.subnet,
        ]
        verifylist = [
            ('router', self._router.id),
            ('subnet', self._router.subnet),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.add_interface_to_router.assert_called_with(
            self._router, **{'subnet_id': self._router.subnet}
        )

        self.assertIsNone(result)


class TestCreateRouter(TestRouter):
    # The new router created.
    new_router = network_fakes.FakeRouter.create_one_router()
    _extensions = {'fake': network_fakes.create_one_extension()}

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'description',
        'distributed',
        'external_gateway_info',
        'ha',
        'id',
        'name',
        'project_id',
        'routes',
        'status',
        'tags',
    )
    data = (
        router.AdminStateColumn(new_router.admin_state_up),
        format_columns.ListColumn(new_router.availability_zone_hints),
        format_columns.ListColumn(new_router.availability_zones),
        new_router.description,
        new_router.distributed,
        router.RouterInfoColumn(new_router.external_gateway_info),
        new_router.ha,
        new_router.id,
        new_router.name,
        new_router.project_id,
        router.RoutesColumn(new_router.routes),
        new_router.status,
        format_columns.ListColumn(new_router.tags),
    )

    def setUp(self):
        super().setUp()

        self.network_client.create_router = mock.Mock(
            return_value=self.new_router
        )
        self.network_client.set_tags = mock.Mock(return_value=None)
        self.network_client.find_extension = mock.Mock(
            side_effect=lambda name: self._extensions.get(name)
        )
        # Get the command object to test
        self.cmd = router.CreateRouter(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
        self.assertFalse(self.network_client.set_tags.called)

    def test_create_default_options(self):
        arglist = [
            self.new_router.name,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
            }
        )
        self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_gateway(self):
        _network = network_fakes.create_one_network()
        _subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network_client.find_network = mock.Mock(return_value=_network)
        self.network_client.find_subnet = mock.Mock(return_value=_subnet)
        arglist = [
            self.new_router.name,
            '--external-gateway',
            _network.name,
            '--enable-snat',
            '--fixed-ip',
            'ip-address=2001:db8::1',
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('external_gateways', [_network.name]),
            ('enable_snat', True),
            ('fixed_ips', [{'ip-address': '2001:db8::1'}]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'external_gateway_info': {
                    'network_id': _network.id,
                    'enable_snat': True,
                    'external_fixed_ips': [{'ip_address': '2001:db8::1'}],
                },
            }
        )
        self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def _test_create_with_ha_options(self, option, ha):
        arglist = [
            option,
            self.new_router.name,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', ha),
            ('no_ha', not ha),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'ha': ha,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_ha_option(self):
        self._test_create_with_ha_options('--ha', True)

    def test_create_with_no_ha_option(self):
        self._test_create_with_ha_options('--no-ha', False)

    def _test_create_with_distributed_options(self, option, distributed):
        arglist = [
            option,
            self.new_router.name,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', distributed),
            ('centralized', not distributed),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'distributed': distributed,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_distributed_option(self):
        self._test_create_with_distributed_options('--distributed', True)

    def test_create_with_centralized_option(self):
        self._test_create_with_distributed_options('--centralized', False)

    def test_create_with_AZ_hints(self):
        arglist = [
            self.new_router.name,
            '--availability-zone-hint',
            'fake-az',
            '--availability-zone-hint',
            'fake-az2',
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('availability_zone_hints', ['fake-az', 'fake-az2']),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'availability_zone_hints': ['fake-az', 'fake-az2'],
            }
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def _test_create_with_tag(self, add_tags=True):
        arglist = [self.new_router.name]
        if add_tags:
            arglist += ['--tag', 'red', '--tag', 'blue']
        else:
            arglist += ['--no-tag']
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
        ]
        if add_tags:
            verifylist.append(('tags', ['red', 'blue']))
        else:
            verifylist.append(('no_tag', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_router.assert_called_once_with(
            name=self.new_router.name, admin_state_up=True
        )
        if add_tags:
            self.network_client.set_tags.assert_called_once_with(
                self.new_router, tests_utils.CompareBySet(['red', 'blue'])
            )
        else:
            self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_tags(self):
        self._test_create_with_tag(add_tags=True)

    def test_create_with_no_tag(self):
        self._test_create_with_tag(add_tags=False)

    def test_create_with_flavor_id_id(self):
        _flavor = network_fakes.create_one_network_flavor()
        self.network_client.find_flavor = mock.Mock(return_value=_flavor)
        arglist = [
            self.new_router.name,
            '--flavor-id',
            _flavor.id,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('flavor_id', _flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'flavor_id': _flavor.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_flavor_id_name(self):
        _flavor = network_fakes.create_one_network_flavor()
        self.network_client.find_flavor = mock.Mock(return_value=_flavor)
        arglist = [self.new_router.name, '--flavor-id', _flavor.name]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('flavor_id', _flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'flavor_id': _flavor.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_flavor_id(self):
        _flavor = network_fakes.create_one_network_flavor()
        self.network_client.find_flavor = mock.Mock(return_value=_flavor)
        arglist = [
            self.new_router.name,
            '--flavor',
            _flavor.id,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('flavor', _flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'flavor_id': _flavor.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_flavor_name(self):
        _flavor = network_fakes.create_one_network_flavor()
        self.network_client.find_flavor = mock.Mock(return_value=_flavor)
        arglist = [self.new_router.name, '--flavor', _flavor.name]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('flavor', _flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                'flavor_id': _flavor.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_enable_default_route_bfd(self):
        self.network_client.find_extension = mock.Mock(
            return_value=network_fakes.create_one_extension(
                attrs={'name': 'external-gateway-multihoming'}
            )
        )
        arglist = [self.new_router.name, '--enable-default-route-bfd']
        verifylist = [
            ('name', self.new_router.name),
            ('enable_default_route_bfd', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            name=self.new_router.name,
            admin_state_up=True,
            enable_default_route_bfd=True,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_enable_default_route_bfd_no_extension(self):
        arglist = [self.new_router.name, '--enable-default-route-bfd']
        verifylist = [
            ('name', self.new_router.name),
            ('enable_default_route_bfd', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_create_with_enable_default_route_ecmp(self):
        self.network_client.find_extension = mock.Mock(
            return_value=network_fakes.create_one_extension(
                attrs={'name': 'external-gateway-multihoming'}
            )
        )
        arglist = [self.new_router.name, '--enable-default-route-ecmp']
        verifylist = [
            ('name', self.new_router.name),
            ('enable_default_route_ecmp', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.create_router.assert_called_once_with(
            name=self.new_router.name,
            admin_state_up=True,
            enable_default_route_ecmp=True,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_enable_default_route_ecmp_no_extension(self):
        arglist = [self.new_router.name, '--enable-default-route-ecmp']
        verifylist = [
            ('name', self.new_router.name),
            ('enable_default_route_ecmp', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_create_with_qos_policy(self):
        _network = network_fakes.create_one_network()
        self.network_client.find_network = mock.Mock(return_value=_network)
        _qos_policy = (
            network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=_qos_policy
        )
        arglist = [
            self.new_router.name,
            '--external-gateway',
            _network.id,
            '--qos-policy',
            _qos_policy.id,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('qos_policy', _qos_policy.id),
            ('external_gateways', [_network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        gw_info = {'network_id': _network.id, 'qos_policy_id': _qos_policy.id}
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self.new_router.name,
                **{'external_gateway_info': gw_info},
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_qos_policy_no_external_gateway(self):
        _qos_policy = (
            network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=_qos_policy
        )
        arglist = [
            self.new_router.name,
            '--qos-policy',
            _qos_policy.id,
        ]
        verifylist = [
            ('name', self.new_router.name),
            ('enable', True),
            ('distributed', False),
            ('ha', False),
            ('qos_policy', _qos_policy.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestDeleteRouter(TestRouter):
    # The routers to delete.
    _routers = network_fakes.FakeRouter.create_routers(count=2)

    def setUp(self):
        super().setUp()

        self.network_client.delete_router = mock.Mock(return_value=None)

        self.network_client.find_router = network_fakes.FakeRouter.get_routers(
            self._routers
        )

        # Get the command object to test
        self.cmd = router.DeleteRouter(self.app, None)

    def test_router_delete(self):
        arglist = [
            self._routers[0].name,
        ]
        verifylist = [
            ('router', [self._routers[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.delete_router.assert_called_once_with(
            self._routers[0]
        )
        self.assertIsNone(result)

    def test_multi_routers_delete(self):
        arglist = []
        verifylist = []

        for r in self._routers:
            arglist.append(r.name)
        verifylist = [
            ('router', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for r in self._routers:
            calls.append(call(r))
        self.network_client.delete_router.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_routers_delete_with_exception(self):
        arglist = [
            self._routers[0].name,
            'unexist_router',
        ]
        verifylist = [
            ('router', [self._routers[0].name, 'unexist_router']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._routers[0], exceptions.CommandError]
        self.network_client.find_router = mock.Mock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 routers failed to delete.', str(e))

        self.network_client.find_router.assert_any_call(
            self._routers[0].name, ignore_missing=False
        )
        self.network_client.find_router.assert_any_call(
            'unexist_router', ignore_missing=False
        )
        self.network_client.delete_router.assert_called_once_with(
            self._routers[0]
        )


class TestListRouter(TestRouter):
    # The routers going to be listed up.
    routers = network_fakes.FakeRouter.create_routers(count=3)
    extensions = network_fakes.create_one_extension()

    columns = (
        'ID',
        'Name',
        'Status',
        'State',
        'Project',
        'Distributed',
        'HA',
    )
    columns_long = columns + (
        'Routes',
        'External gateway info',
        'Availability zones',
        'Tags',
    )
    columns_long_no_az = columns + (
        'Routes',
        'External gateway info',
        'Tags',
    )

    data = []
    for r in routers:
        data.append(
            (
                r.id,
                r.name,
                r.status,
                router.AdminStateColumn(r.admin_state_up),
                r.project_id,
                r.distributed,
                r.ha,
            )
        )

    router_agent_data = []
    for r in routers:
        router_agent_data.append(
            (
                r.id,
                r.name,
                r.external_gateway_info,
            )
        )

    agents_columns = (
        'ID',
        'Name',
        'External Gateway Info',
    )

    data_long = []
    for i in range(0, len(routers)):
        r = routers[i]
        data_long.append(
            data[i]
            + (
                router.RoutesColumn(r.routes),
                router.RouterInfoColumn(r.external_gateway_info),
                format_columns.ListColumn(r.availability_zones),
                format_columns.ListColumn(r.tags),
            )
        )
    data_long_no_az = []
    for i in range(0, len(routers)):
        r = routers[i]
        data_long_no_az.append(
            data[i]
            + (
                router.RoutesColumn(r.routes),
                router.RouterInfoColumn(r.external_gateway_info),
                format_columns.ListColumn(r.tags),
            )
        )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = router.ListRouter(self.app, None)

        self.network_client.agent_hosted_routers = mock.Mock(
            return_value=self.routers
        )
        self.network_client.routers = mock.Mock(return_value=self.routers)
        self.network_client.find_extension = mock.Mock(
            return_value=self.extensions
        )
        self.network_client.find_router = mock.Mock(
            return_value=self.routers[0]
        )
        self._testagent = network_fakes.create_one_network_agent()
        self.network_client.get_agent = mock.Mock(return_value=self._testagent)
        self.network_client.get_router = mock.Mock(
            return_value=self.routers[0]
        )

    def test_router_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_router_list_no_ha_no_distributed(self):
        _routers = network_fakes.FakeRouter.create_routers(
            {'ha': None, 'distributed': None}, count=3
        )

        arglist = []
        verifylist = [
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(
            self.network_client, "routers", return_value=_routers
        ):
            columns, data = self.cmd.take_action(parsed_args)

        self.assertNotIn("is_distributed", columns)
        self.assertNotIn("is_ha", columns)

    def test_router_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, list(data))

    def test_router_list_long_no_az(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # to mock, that no availability zone
        self.network_client.find_extension = mock.Mock(return_value=None)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with()
        self.assertEqual(self.columns_long_no_az, columns)
        self.assertCountEqual(self.data_long_no_az, list(data))

    def test_list_name(self):
        test_name = "fakename"
        arglist = [
            '--name',
            test_name,
        ]
        verifylist = [
            ('long', False),
            ('name', test_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with(
            **{'name': test_name}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_router_list_enable(self):
        arglist = [
            '--enable',
        ]
        verifylist = [
            ('long', False),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with(
            **{'admin_state_up': True, 'is_admin_state_up': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_router_list_disable(self):
        arglist = [
            '--disable',
        ]
        verifylist = [('long', False), ('disable', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with(
            **{'admin_state_up': False, 'is_admin_state_up': False}
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_router_list_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project',
            project.id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'project_id': project.id}

        self.network_client.routers.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_router_list_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project',
            project.id,
            '--project-domain',
            project.domain_id,
        ]
        verifylist = [
            ('project', project.id),
            ('project_domain', project.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'project_id': project.id}

        self.network_client.routers.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_router_list_agents_no_args(self):
        arglist = [
            '--agents',
        ]
        verifylist = []

        # Missing required router ID should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_router_list_agents(self):
        arglist = [
            '--agent',
            self._testagent.id,
        ]
        verifylist = [
            ('agent', self._testagent.id),
        ]

        attrs = {
            self._testagent.id,
        }

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.agent_hosted_routers(*attrs)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_list_with_tag_options(self):
        arglist = [
            '--tags',
            'red,blue',
            '--any-tags',
            'red,green',
            '--not-tags',
            'orange,yellow',
            '--not-any-tags',
            'black,white',
        ]
        verifylist = [
            ('tags', ['red', 'blue']),
            ('any_tags', ['red', 'green']),
            ('not_tags', ['orange', 'yellow']),
            ('not_any_tags', ['black', 'white']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.routers.assert_called_once_with(
            **{
                'tags': 'red,blue',
                'any_tags': 'red,green',
                'not_tags': 'orange,yellow',
                'not_any_tags': 'black,white',
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))


class TestRemovePortFromRouter(TestRouter):
    '''Remove port from a Router'''

    _port = network_fakes.create_one_port()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'port': _port.id}
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_router = mock.Mock(return_value=self._router)
        self.network_client.find_port = mock.Mock(return_value=self._port)

        self.cmd = router.RemovePortFromRouter(self.app, None)

    def test_remove_port_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_remove_port_required_options(self):
        arglist = [
            self._router.id,
            self._router.port,
        ]
        verifylist = [
            ('router', self._router.id),
            ('port', self._router.port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.remove_interface_from_router.assert_called_with(
            self._router, **{'port_id': self._router.port}
        )
        self.assertIsNone(result)


class TestRemoveSubnetFromRouter(TestRouter):
    '''Remove subnet from Router'''

    _subnet = network_fakes.FakeSubnet.create_one_subnet()
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'subnet': _subnet.id}
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_router = mock.Mock(return_value=self._router)
        self.network_client.find_subnet = mock.Mock(return_value=self._subnet)

        self.cmd = router.RemoveSubnetFromRouter(self.app, None)

    def test_remove_subnet_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_remove_subnet_required_options(self):
        arglist = [
            self._router.id,
            self._router.subnet,
        ]
        verifylist = [
            ('subnet', self._router.subnet),
            ('router', self._router.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.remove_interface_from_router.assert_called_with(
            self._router, **{'subnet_id': self._router.subnet}
        )
        self.assertIsNone(result)


class TestAddExtraRoutesToRouter(TestRouter):
    _router = network_fakes.FakeRouter.create_one_router()

    def setUp(self):
        super().setUp()
        self.network_client.add_extra_routes_to_router = mock.Mock(
            return_value=self._router
        )
        self.cmd = router.AddExtraRoutesToRouter(self.app, None)
        self.network_client.find_router = mock.Mock(return_value=self._router)

    def test_add_no_extra_route(self):
        arglist = [
            self._router.id,
        ]
        verifylist = [
            ('router', self._router.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.add_extra_routes_to_router.assert_called_with(
            self._router, body={'router': {'routes': []}}
        )
        self.assertEqual(2, len(result))

    def test_add_one_extra_route(self):
        arglist = [
            self._router.id,
            '--route',
            'destination=dst1,gateway=gw1',
        ]
        verifylist = [
            ('router', self._router.id),
            ('routes', [{'destination': 'dst1', 'gateway': 'gw1'}]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.add_extra_routes_to_router.assert_called_with(
            self._router,
            body={
                'router': {
                    'routes': [
                        {'destination': 'dst1', 'nexthop': 'gw1'},
                    ]
                }
            },
        )
        self.assertEqual(2, len(result))

    def test_add_multiple_extra_routes(self):
        arglist = [
            self._router.id,
            '--route',
            'destination=dst1,gateway=gw1',
            '--route',
            'destination=dst2,gateway=gw2',
        ]
        verifylist = [
            ('router', self._router.id),
            (
                'routes',
                [
                    {'destination': 'dst1', 'gateway': 'gw1'},
                    {'destination': 'dst2', 'gateway': 'gw2'},
                ],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.add_extra_routes_to_router.assert_called_with(
            self._router,
            body={
                'router': {
                    'routes': [
                        {'destination': 'dst1', 'nexthop': 'gw1'},
                        {'destination': 'dst2', 'nexthop': 'gw2'},
                    ]
                }
            },
        )
        self.assertEqual(2, len(result))


class TestRemoveExtraRoutesFromRouter(TestRouter):
    _router = network_fakes.FakeRouter.create_one_router()

    def setUp(self):
        super().setUp()
        self.network_client.remove_extra_routes_from_router = mock.Mock(
            return_value=self._router
        )
        self.cmd = router.RemoveExtraRoutesFromRouter(self.app, None)
        self.network_client.find_router = mock.Mock(return_value=self._router)

    def test_remove_no_extra_route(self):
        arglist = [
            self._router.id,
        ]
        verifylist = [
            ('router', self._router.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.remove_extra_routes_from_router.assert_called_with(
            self._router, body={'router': {'routes': []}}
        )
        self.assertEqual(2, len(result))

    def test_remove_one_extra_route(self):
        arglist = [
            self._router.id,
            '--route',
            'destination=dst1,gateway=gw1',
        ]
        verifylist = [
            ('router', self._router.id),
            ('routes', [{'destination': 'dst1', 'gateway': 'gw1'}]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.remove_extra_routes_from_router.assert_called_with(
            self._router,
            body={
                'router': {
                    'routes': [
                        {'destination': 'dst1', 'nexthop': 'gw1'},
                    ]
                }
            },
        )
        self.assertEqual(2, len(result))

    def test_remove_multiple_extra_routes(self):
        arglist = [
            self._router.id,
            '--route',
            'destination=dst1,gateway=gw1',
            '--route',
            'destination=dst2,gateway=gw2',
        ]
        verifylist = [
            ('router', self._router.id),
            (
                'routes',
                [
                    {'destination': 'dst1', 'gateway': 'gw1'},
                    {'destination': 'dst2', 'gateway': 'gw2'},
                ],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.remove_extra_routes_from_router.assert_called_with(
            self._router,
            body={
                'router': {
                    'routes': [
                        {'destination': 'dst1', 'nexthop': 'gw1'},
                        {'destination': 'dst2', 'nexthop': 'gw2'},
                    ]
                }
            },
        )
        self.assertEqual(2, len(result))


class TestSetRouter(TestRouter):
    # The router to set.
    _default_route = {'destination': '10.20.20.0/24', 'nexthop': '10.20.30.1'}
    _network = network_fakes.create_one_network()
    _subnet = network_fakes.FakeSubnet.create_one_subnet(
        attrs={'network_id': _network.id}
    )
    _router = network_fakes.FakeRouter.create_one_router(
        attrs={'routes': [_default_route], 'tags': ['green', 'red']}
    )
    _extensions = {'fake': network_fakes.create_one_extension()}

    def setUp(self):
        super().setUp()
        self.network_client.update_router = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)
        self.network_client.find_router = mock.Mock(return_value=self._router)
        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )
        self.network_client.find_subnet = mock.Mock(return_value=self._subnet)
        self.network_client.find_extension = mock.Mock(
            side_effect=lambda name: self._extensions.get(name)
        )
        # Get the command object to test
        self.cmd = router.SetRouter(self.app, None)

    def test_set_this(self):
        arglist = [
            self._router.name,
            '--enable',
            '--distributed',
            '--name',
            'noob',
            '--no-ha',
            '--description',
            'router',
        ]
        verifylist = [
            ('router', self._router.name),
            ('enable', True),
            ('distributed', True),
            ('name', 'noob'),
            ('description', 'router'),
            ('no_ha', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': True,
            'distributed': True,
            'name': 'noob',
            'ha': False,
            'description': 'router',
        }
        self.network_client.update_router.assert_called_once_with(
            self._router, **attrs
        )
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            self._router.name,
            '--disable',
            '--centralized',
            '--ha',
        ]
        verifylist = [
            ('router', self._router.name),
            ('disable', True),
            ('centralized', True),
            ('ha', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'distributed': False,
            'ha': True,
        }
        self.network_client.update_router.assert_called_once_with(
            self._router, **attrs
        )
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

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_route(self):
        arglist = [
            self._router.name,
            '--route',
            'destination=10.20.30.0/24,gateway=10.20.30.1',
        ]
        verifylist = [
            ('router', self._router.name),
            (
                'routes',
                [{'destination': '10.20.30.0/24', 'gateway': '10.20.30.1'}],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        routes = [{'destination': '10.20.30.0/24', 'nexthop': '10.20.30.1'}]
        attrs = {'routes': routes + self._router.routes}
        self.network_client.update_router.assert_called_once_with(
            self._router, **attrs
        )
        self.assertIsNone(result)

    def test_set_no_route(self):
        arglist = [
            self._router.name,
            '--no-route',
        ]
        verifylist = [
            ('router', self._router.name),
            ('no_route', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'routes': [],
        }
        self.network_client.update_router.assert_called_once_with(
            self._router, **attrs
        )
        self.assertIsNone(result)

    def test_set_route_overwrite_route(self):
        _testrouter = network_fakes.FakeRouter.create_one_router(
            {'routes': [{"destination": "10.0.0.2", "nexthop": "1.1.1.1"}]}
        )
        self.network_client.find_router = mock.Mock(return_value=_testrouter)
        arglist = [
            _testrouter.name,
            '--route',
            'destination=10.20.30.0/24,gateway=10.20.30.1',
            '--no-route',
        ]
        verifylist = [
            ('router', _testrouter.name),
            (
                'routes',
                [{'destination': '10.20.30.0/24', 'gateway': '10.20.30.1'}],
            ),
            ('no_route', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'routes': [
                {'destination': '10.20.30.0/24', 'nexthop': '10.20.30.1'}
            ]
        }
        self.network_client.update_router.assert_called_once_with(
            _testrouter, **attrs
        )
        self.assertIsNone(result)

    def test_set_nothing(self):
        arglist = [
            self._router.name,
        ]
        verifylist = [
            ('router', self._router.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_router.called)
        self.assertFalse(self.network_client.set_tags.called)
        self.assertIsNone(result)

    def test_wrong_gateway_params(self):
        arglist = [
            "--fixed-ip",
            "subnet='abc'",
            self._router.id,
        ]
        verifylist = [
            ('fixed_ips', [{'subnet': "'abc'"}]),
            ('router', self._router.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_set_gateway_network_only(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            self._router.id,
        ]
        verifylist = [
            ('external_gateways', [self._network.id]),
            ('router', self._router.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_router.assert_called_with(
            self._router,
            **{'external_gateway_info': {'network_id': self._network.id}},
        )
        self.assertIsNone(result)

    def test_set_gateway_options_subnet_only(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            "--fixed-ip",
            "subnet='abc'",
            self._router.id,
            '--enable-snat',
        ]
        verifylist = [
            ('router', self._router.id),
            ('external_gateways', [self._network.id]),
            ('fixed_ips', [{'subnet': "'abc'"}]),
            ('enable_snat', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_router.assert_called_with(
            self._router,
            **{
                'external_gateway_info': {
                    'network_id': self._network.id,
                    'external_fixed_ips': [
                        {
                            'subnet_id': self._subnet.id,
                        }
                    ],
                    'enable_snat': True,
                }
            },
        )
        self.assertIsNone(result)

    def test_set_gateway_option_ipaddress_only(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            "--fixed-ip",
            "ip-address=10.0.1.1",
            self._router.id,
            '--enable-snat',
        ]
        verifylist = [
            ('router', self._router.id),
            ('external_gateways', [self._network.id]),
            ('fixed_ips', [{'ip-address': "10.0.1.1"}]),
            ('enable_snat', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_router.assert_called_with(
            self._router,
            **{
                'external_gateway_info': {
                    'network_id': self._network.id,
                    'external_fixed_ips': [
                        {
                            'ip_address': "10.0.1.1",
                        }
                    ],
                    'enable_snat': True,
                }
            },
        )
        self.assertIsNone(result)

    def test_set_gateway_options_subnet_ipaddress(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            "--fixed-ip",
            "subnet='abc',ip-address=10.0.1.1",
            self._router.id,
            '--enable-snat',
        ]
        verifylist = [
            ('router', self._router.id),
            ('external_gateways', [self._network.id]),
            ('fixed_ips', [{'subnet': "'abc'", 'ip-address': "10.0.1.1"}]),
            ('enable_snat', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_router.assert_called_with(
            self._router,
            **{
                'external_gateway_info': {
                    'network_id': self._network.id,
                    'external_fixed_ips': [
                        {
                            'subnet_id': self._subnet.id,
                            'ip_address': "10.0.1.1",
                        }
                    ],
                    'enable_snat': True,
                }
            },
        )
        self.assertIsNone(result)

    def _test_set_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['red', 'blue', 'green']
        else:
            arglist = ['--no-tag']
            verifylist = [('no_tag', True)]
            expected_args = []
        arglist.append(self._router.name)
        verifylist.append(('router', self._router.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_router.called)
        self.network_client.set_tags.assert_called_once_with(
            self._router, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_set_with_tags(self):
        self._test_set_tags(with_tags=True)

    def test_set_with_no_tag(self):
        self._test_set_tags(with_tags=False)

    def test_set_gateway_ip_qos(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        arglist = [
            "--external-gateway",
            self._network.id,
            "--qos-policy",
            qos_policy.id,
            self._router.id,
        ]
        verifylist = [
            ('router', self._router.id),
            ('external_gateways', [self._network.id]),
            ('qos_policy', qos_policy.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_router.assert_called_with(
            self._router,
            **{
                'external_gateway_info': {
                    'network_id': self._network.id,
                    'qos_policy_id': qos_policy.id,
                }
            },
        )
        self.assertIsNone(result)

    def test_unset_gateway_ip_qos(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            "--no-qos-policy",
            self._router.id,
        ]
        verifylist = [
            ('router', self._router.id),
            ('external_gateways', [self._network.id]),
            ('no_qos_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_router.assert_called_with(
            self._router,
            **{
                'external_gateway_info': {
                    'network_id': self._network.id,
                    'qos_policy_id': None,
                }
            },
        )
        self.assertIsNone(result)

    def test_set_unset_gateway_ip_qos(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        arglist = [
            "--external-gateway",
            self._network.id,
            "--qos-policy",
            qos_policy.id,
            "--no-qos-policy",
            self._router.id,
        ]
        verifylist = [
            ('router', self._router.id),
            ('external_gateways', [self._network.id]),
            ('qos_policy', qos_policy.id),
            ('no_qos_policy', True),
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_gateway_ip_qos_no_gateway(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        router = network_fakes.FakeRouter.create_one_router()
        self.network_client.find_router = mock.Mock(return_value=router)
        arglist = [
            "--qos-policy",
            qos_policy.id,
            router.id,
        ]
        verifylist = [
            ('router', router.id),
            ('qos_policy', qos_policy.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_gateway_ip_qos_no_gateway(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        router = network_fakes.FakeRouter.create_one_router()
        self.network_client.find_router = mock.Mock(return_value=router)
        arglist = [
            "--no-qos-policy",
            router.id,
        ]
        verifylist = [
            ('router', router.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestShowRouter(TestRouter):
    # The router to set.
    _router = network_fakes.FakeRouter.create_one_router()
    _port = network_fakes.create_one_port(
        {'device_owner': 'network:router_interface', 'device_id': _router.id}
    )
    setattr(
        _router,
        'interfaces_info',
        [
            {
                'port_id': _port.id,
                'ip_address': _port.fixed_ips[0]['ip_address'],
                'subnet_id': _port.fixed_ips[0]['subnet_id'],
            }
        ],
    )

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'description',
        'distributed',
        'external_gateway_info',
        'ha',
        'id',
        'interfaces_info',
        'name',
        'project_id',
        'routes',
        'status',
        'tags',
    )
    data = (
        router.AdminStateColumn(_router.admin_state_up),
        format_columns.ListColumn(_router.availability_zone_hints),
        format_columns.ListColumn(_router.availability_zones),
        _router.description,
        _router.distributed,
        router.RouterInfoColumn(_router.external_gateway_info),
        _router.ha,
        _router.id,
        router.RouterInfoColumn(_router.interfaces_info),
        _router.name,
        _router.project_id,
        router.RoutesColumn(_router.routes),
        _router.status,
        format_columns.ListColumn(_router.tags),
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_router = mock.Mock(return_value=self._router)
        self.network_client.ports = mock.Mock(return_value=[self._port])

        # Get the command object to test
        self.cmd = router.ShowRouter(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_all_options(self):
        arglist = [
            self._router.name,
        ]
        verifylist = [
            ('router', self._router.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_router.assert_called_once_with(
            self._router.name, ignore_missing=False
        )
        self.network_client.ports.assert_called_with(
            **{'device_id': self._router.id}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_show_no_ha_no_distributed(self):
        _router = network_fakes.FakeRouter.create_one_router(
            {'ha': None, 'distributed': None}
        )

        arglist = [
            _router.name,
        ]
        verifylist = [
            ('router', _router.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(
            self.network_client, "find_router", return_value=_router
        ):
            columns, data = self.cmd.take_action(parsed_args)

        self.assertNotIn("is_distributed", columns)
        self.assertNotIn("is_ha", columns)

    def test_show_no_extra_route_extension(self):
        _router = network_fakes.FakeRouter.create_one_router({'routes': None})

        arglist = [
            _router.name,
        ]
        verifylist = [
            ('router', _router.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        with mock.patch.object(
            self.network_client, "find_router", return_value=_router
        ):
            columns, data = self.cmd.take_action(parsed_args)

        self.assertIn("routes", columns)
        self.assertIsNone(list(data)[columns.index('routes')].human_readable())


class TestUnsetRouter(TestRouter):
    def setUp(self):
        super().setUp()
        self.fake_network = network_fakes.create_one_network()
        self.fake_qos_policy = (
            network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        )
        self._testrouter = network_fakes.FakeRouter.create_one_router(
            {
                'routes': [
                    {
                        "destination": "192.168.101.1/24",
                        "nexthop": "172.24.4.3",
                    },
                    {
                        "destination": "192.168.101.2/24",
                        "nexthop": "172.24.4.3",
                    },
                ],
                'tags': ['green', 'red'],
                'external_gateway_info': {
                    'network_id': self.fake_network.id,
                    'qos_policy_id': self.fake_qos_policy.id,
                },
            }
        )
        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network_client.find_router = mock.Mock(
            return_value=self._testrouter
        )
        self.network_client.update_router = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)
        self._extensions = {'fake': network_fakes.create_one_extension()}
        self.network_client.find_extension = mock.Mock(
            side_effect=lambda name: self._extensions.get(name)
        )
        self.network_client.remove_external_gateways = mock.Mock(
            return_value=None
        )
        # Get the command object to test
        self.cmd = router.UnsetRouter(self.app, None)

    def test_unset_router_params(self):
        arglist = [
            '--route',
            'destination=192.168.101.1/24,gateway=172.24.4.3',
            self._testrouter.name,
        ]
        verifylist = [
            (
                'routes',
                [{"destination": "192.168.101.1/24", "gateway": "172.24.4.3"}],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'routes': [
                {"destination": "192.168.101.2/24", "nexthop": "172.24.4.3"}
            ],
        }
        self.network_client.update_router.assert_called_once_with(
            self._testrouter, **attrs
        )
        self.assertIsNone(result)

    def test_unset_router_wrong_routes(self):
        arglist = [
            '--route',
            'destination=192.168.101.1/24,gateway=172.24.4.2',
            self._testrouter.name,
        ]
        verifylist = [
            (
                'routes',
                [{"destination": "192.168.101.1/24", "gateway": "172.24.4.2"}],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_router_external_gateway(self):
        arglist = [
            '--external-gateway',
            self._testrouter.name,
        ]
        verifylist = [('external_gateways', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {'external_gateway_info': {}}
        self.network_client.update_router.assert_called_once_with(
            self._testrouter, **attrs
        )
        self.assertIsNone(result)

    def test_unset_router_external_gateway_multiple_supported(self):
        # Add the relevant extension in order to test the alternate behavior.
        self._extensions = {
            'external-gateway-multihoming': network_fakes.create_one_extension(
                attrs={'name': 'external-gateway-multihoming'}
            )
        }
        arglist = [
            '--external-gateway',
            self._testrouter.name,
        ]
        verifylist = [('external_gateways', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        # The removal of all gateways should be requested using the multiple
        # gateways API.
        self.network_client.remove_external_gateways.assert_called_once_with(
            self._testrouter, body={'router': {'external_gateways': {}}}
        )
        # The compatibility API will also be called in order to potentially
        # unset other parameters along with external_gateway_info which
        # should already be empty at that point anyway.
        self.network_client.update_router.assert_called_once_with(
            self._testrouter, **{'external_gateway_info': {}}
        )
        self.assertIsNone(result)

    def _test_unset_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['green']
        else:
            arglist = ['--all-tag']
            verifylist = [('all_tag', True)]
            expected_args = []
        arglist.append(self._testrouter.name)
        verifylist.append(('router', self._testrouter.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_router.called)
        self.network_client.set_tags.assert_called_once_with(
            self._testrouter, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_unset_with_tags(self):
        self._test_unset_tags(with_tags=True)

    def test_unset_with_all_tag(self):
        self._test_unset_tags(with_tags=False)

    def test_unset_router_qos_policy(self):
        arglist = [
            '--qos-policy',
            self._testrouter.name,
        ]
        verifylist = [('qos_policy', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'external_gateway_info': {
                "network_id": self.fake_network.id,
                "qos_policy_id": None,
            }
        }
        self.network_client.update_router.assert_called_once_with(
            self._testrouter, **attrs
        )
        self.assertIsNone(result)

    def test_unset_gateway_ip_qos_no_network(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        router = network_fakes.FakeRouter.create_one_router()
        self.network_client.find_router = mock.Mock(return_value=router)
        arglist = [
            "--qos-policy",
            router.id,
        ]
        verifylist = [
            ('router', router.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_gateway_ip_qos_no_qos(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        router = network_fakes.FakeRouter.create_one_router(
            {"external_gateway_info": {"network_id": "fake-id"}}
        )
        self.network_client.find_router = mock.Mock(return_value=router)
        arglist = [
            "--qos-policy",
            router.id,
        ]
        verifylist = [
            ('router', router.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestGatewayOps(TestRouter):
    def setUp(self):
        super().setUp()
        self._networks = []
        self._network = network_fakes.create_one_network()
        self._networks.append(self._network)

        self._router = network_fakes.FakeRouter.create_one_router(
            {
                'external_gateway_info': {
                    'network_id': self._network.id,
                },
            }
        )
        self._subnet = network_fakes.FakeSubnet.create_one_subnet(
            attrs={'network_id': self._network.id}
        )
        self._extensions = {
            'external-gateway-multihoming': network_fakes.create_one_extension(
                attrs={'name': 'external-gateway-multihoming'}
            )
        }
        self.network_client.find_extension = mock.Mock(
            side_effect=lambda name: self._extensions.get(name)
        )
        self.network_client.find_router = mock.Mock(return_value=self._router)

        def _find_network(name_or_id, ignore_missing):
            for network in self._networks:
                if name_or_id in (network.id, network.name):
                    return network
            if ignore_missing:
                return None
            raise Exception('Test resource not found')

        self.network_client.find_network = mock.Mock(side_effect=_find_network)

        self.network_client.find_subnet = mock.Mock(return_value=self._subnet)
        self.network_client.add_external_gateways = mock.Mock(
            return_value=None
        )
        self.network_client.remove_external_gateways = mock.Mock(
            return_value=None
        )


class TestCreateMultipleGateways(TestGatewayOps):
    _columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'description',
        'distributed',
        'external_gateway_info',
        'ha',
        'id',
        'name',
        'project_id',
        'routes',
        'status',
        'tags',
    )

    def setUp(self):
        super().setUp()
        self._second_network = network_fakes.create_one_network()
        self._networks.append(self._second_network)

        self.network_client.create_router = mock.Mock(
            return_value=self._router
        )
        self.network_client.update_router = mock.Mock(return_value=None)
        self.network_client.update_external_gateways = mock.Mock(
            return_value=None
        )

        self._data = (
            router.AdminStateColumn(self._router.admin_state_up),
            format_columns.ListColumn(self._router.availability_zone_hints),
            format_columns.ListColumn(self._router.availability_zones),
            self._router.description,
            self._router.distributed,
            router.RouterInfoColumn(self._router.external_gateway_info),
            self._router.ha,
            self._router.id,
            self._router.name,
            self._router.project_id,
            router.RoutesColumn(self._router.routes),
            self._router.status,
            format_columns.ListColumn(self._router.tags),
        )
        self.cmd = router.CreateRouter(self.app, None)

    def test_create_one_gateway(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            self._router.name,
        ]
        verifylist = [
            ('name', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.update_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                        }
                    ]
                }
            },
        )
        self.assertEqual(self._columns, columns)
        self.assertCountEqual(self._data, data)

    def test_create_multiple_gateways(self):
        arglist = [
            self._router.name,
            "--external-gateway",
            self._network.id,
            "--external-gateway",
            self._network.id,
            "--external-gateway",
            self._second_network.id,
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.1',
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.2',
        ]
        verifylist = [
            ('name', self._router.name),
            (
                'external_gateways',
                [self._network.id, self._network.id, self._second_network.id],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # The router will not have a gateway after the create call, but it
        # will be added after the update call.
        self.network_client.create_router.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self._router.name,
            }
        )
        self.network_client.update_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.1',
                                }
                            ],
                        },
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.2',
                                }
                            ],
                        },
                        {
                            'network_id': self._second_network.id,
                        },
                    ]
                }
            },
        )
        self.assertEqual(self._columns, columns)
        self.assertCountEqual(self._data, data)


class TestUpdateMultipleGateways(TestGatewayOps):
    def setUp(self):
        super().setUp()
        self._second_network = network_fakes.create_one_network()
        self._networks.append(self._second_network)

        self.network_client.update_router = mock.Mock(return_value=None)
        self.network_client.update_external_gateways = mock.Mock(
            return_value=None
        )
        self.cmd = router.SetRouter(self.app, None)

    def test_update_one_gateway(self):
        arglist = [
            "--external-gateway",
            self._network.id,
            "--no-qos-policy",
            self._router.name,
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
            ('no_qos_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.update_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {'network_id': self._network.id, 'qos_policy_id': None}
                    ]
                }
            },
        )
        self.assertIsNone(result)

    def test_update_multiple_gateways(self):
        arglist = [
            self._router.name,
            "--external-gateway",
            self._network.id,
            "--external-gateway",
            self._network.id,
            "--external-gateway",
            self._second_network.id,
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.1',
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.2',
            "--no-qos-policy",
        ]
        verifylist = [
            ('router', self._router.name),
            (
                'external_gateways',
                [self._network.id, self._network.id, self._second_network.id],
            ),
            ('no_qos_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.update_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.1',
                                }
                            ],
                            'qos_policy_id': None,
                        },
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.2',
                                }
                            ],
                            'qos_policy_id': None,
                        },
                        {
                            'network_id': self._second_network.id,
                            'qos_policy_id': None,
                        },
                    ]
                }
            },
        )
        self.assertIsNone(result)


class TestAddGatewayRouter(TestGatewayOps):
    def setUp(self):
        super().setUp()
        # Get the command object to test
        self.cmd = router.AddGatewayToRouter(self.app, None)

        self.network_client.add_external_gateways.return_value = self._router

    def test_add_gateway_network_only(self):
        arglist = [
            self._router.name,
            self._network.id,
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.add_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [{'network_id': self._network.id}]
                }
            },
        )
        self.assertEqual(result[1][result[0].index('id')], self._router.id)

    def test_add_gateway_network_fixed_ip(self):
        arglist = [
            self._router.name,
            self._network.id,
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.1',
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.add_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.1',
                                }
                            ],
                        }
                    ]
                }
            },
        )
        self.assertEqual(result[1][result[0].index('id')], self._router.id)

    def test_add_gateway_network_multiple_fixed_ips(self):
        arglist = [
            self._router.name,
            self._network.id,
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.1',
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.2',
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
            (
                'fixed_ips',
                [
                    {'ip-address': '10.0.1.1', 'subnet': self._subnet.id},
                    {'ip-address': '10.0.1.2', 'subnet': self._subnet.id},
                ],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.add_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.1',
                                },
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.2',
                                },
                            ],
                        }
                    ]
                }
            },
        )
        self.assertEqual(result[1][result[0].index('id')], self._router.id)

    def test_add_gateway_network_only_no_extension(self):
        self._extensions = {}
        arglist = [
            self._router.name,
            self._network.id,
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestRemoveGatewayRouter(TestGatewayOps):
    def setUp(self):
        super().setUp()
        # Get the command object to test
        self.cmd = router.RemoveGatewayFromRouter(self.app, None)

        self.network_client.remove_external_gateways.return_value = (
            self._router
        )

    def test_remove_gateway_network_only(self):
        arglist = [
            self._router.name,
            self._network.id,
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.remove_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [{'network_id': self._network.id}]
                }
            },
        )
        self.assertEqual(result[1][result[0].index('id')], self._router.id)

    def test_remove_gateway_network_fixed_ip(self):
        arglist = [
            self._router.name,
            self._network.id,
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.1',
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.remove_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.1',
                                }
                            ],
                        }
                    ]
                }
            },
        )
        self.assertEqual(result[1][result[0].index('id')], self._router.id)

    def test_remove_gateway_network_multiple_fixed_ips(self):
        arglist = [
            self._router.name,
            self._network.id,
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.1',
            '--fixed-ip',
            f'subnet={self._subnet.id},ip-address=10.0.1.2',
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
            (
                'fixed_ips',
                [
                    {'ip-address': '10.0.1.1', 'subnet': self._subnet.id},
                    {'ip-address': '10.0.1.2', 'subnet': self._subnet.id},
                ],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.remove_external_gateways.assert_called_with(
            self._router,
            body={
                'router': {
                    'external_gateways': [
                        {
                            'network_id': self._network.id,
                            'external_fixed_ips': [
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.1',
                                },
                                {
                                    'subnet_id': self._subnet.id,
                                    'ip_address': '10.0.1.2',
                                },
                            ],
                        }
                    ]
                }
            },
        )
        self.assertEqual(result[1][result[0].index('id')], self._router.id)

    def test_remove_gateway_network_only_no_extension(self):
        self._extensions = {}
        arglist = [
            self._router.name,
            self._network.id,
        ]
        verifylist = [
            ('router', self._router.name),
            ('external_gateways', [self._network.id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
