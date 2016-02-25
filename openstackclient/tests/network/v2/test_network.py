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

import copy
import mock

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.network.v2 import network
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes_v2
from openstackclient.tests.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


# Tests for Neutron network
#
class TestNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestCreateNetworkIdentityV3(TestNetwork):

    # The new network created.
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={
            'tenant_id': identity_fakes_v3.project_id,
            'availability_zone_hints': ["nova"],
        }
    )

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'id',
        'name',
        'project_id',
        'router_external',
        'status',
        'subnets',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        utils.format_list(_network.availability_zone_hints),
        utils.format_list(_network.availability_zones),
        _network.id,
        _network.name,
        _network.project_id,
        network._format_router_external(_network.router_external),
        _network.status,
        utils.format_list(_network.subnets),
    )

    def setUp(self):
        super(TestCreateNetworkIdentityV3, self).setUp()

        self.network.create_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, self.namespace)

        # Set identity client v3. And get a shortcut to Identity client.
        identity_client = identity_fakes_v3.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.projects
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.PROJECT),
            loaded=True,
        )

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity.domains
        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.DOMAIN),
            loaded=True,
        )

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('name', self._network.name),
            ('admin_state', True),
            ('shared', None),
            ('project', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_with(**{
            'admin_state_up': True,
            'name': self._network.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            "--disable",
            "--share",
            "--project", identity_fakes_v3.project_name,
            "--project-domain", identity_fakes_v3.domain_name,
            "--availability-zone-hint", "nova",
            self._network.name,
        ]
        verifylist = [
            ('admin_state', False),
            ('shared', True),
            ('project', identity_fakes_v3.project_name),
            ('project_domain', identity_fakes_v3.domain_name),
            ('availability_zone_hints', ["nova"]),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_network.assert_called_with(**{
            'admin_state_up': False,
            'availability_zone_hints': ["nova"],
            'name': self._network.name,
            'shared': True,
            'tenant_id': identity_fakes_v3.project_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_other_options(self):
        arglist = [
            "--enable",
            "--no-share",
            self._network.name,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', False),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_with(**{
            'admin_state_up': True,
            'name': self._network.name,
            'shared': False,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestCreateNetworkIdentityV2(TestNetwork):

    # The new network created.
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={'tenant_id': identity_fakes_v2.project_id}
    )

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'id',
        'name',
        'project_id',
        'router_external',
        'status',
        'subnets',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        utils.format_list(_network.availability_zone_hints),
        utils.format_list(_network.availability_zones),
        _network.id,
        _network.name,
        _network.project_id,
        network._format_router_external(_network.router_external),
        _network.status,
        utils.format_list(_network.subnets),
    )

    def setUp(self):
        super(TestCreateNetworkIdentityV2, self).setUp()

        self.network.create_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, self.namespace)

        # Set identity client v2. And get a shortcut to Identity client.
        identity_client = identity_fakes_v2.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.tenants
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v2.PROJECT),
            loaded=True,
        )

        # There is no DomainManager Mock in fake identity v2.

    def test_create_with_project_identityv2(self):
        arglist = [
            "--project", identity_fakes_v2.project_name,
            self._network.name,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', None),
            ('name', self._network.name),
            ('project', identity_fakes_v2.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_with(**{
            'admin_state_up': True,
            'name': self._network.name,
            'tenant_id': identity_fakes_v2.project_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_domain_identityv2(self):
        arglist = [
            "--project", identity_fakes_v3.project_name,
            "--project-domain", identity_fakes_v3.domain_name,
            self._network.name,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', None),
            ('project', identity_fakes_v3.project_name),
            ('project_domain', identity_fakes_v3.domain_name),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            AttributeError,
            self.cmd.take_action,
            parsed_args,
        )


class TestDeleteNetwork(TestNetwork):

    # The network to delete.
    _network = network_fakes.FakeNetwork.create_one_network()

    def setUp(self):
        super(TestDeleteNetwork, self).setUp()

        self.network.delete_network = mock.Mock(return_value=None)

        self.network.find_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('network', [self._network.name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_network.assert_called_with(self._network)
        self.assertIsNone(result)


class TestListNetwork(TestNetwork):

    # The networks going to be listed up.
    _network = network_fakes.FakeNetwork.create_networks(count=3)

    columns = (
        'ID',
        'Name',
        'Subnets',
    )
    columns_long = (
        'ID',
        'Name',
        'Status',
        'Project',
        'State',
        'Shared',
        'Subnets',
        'Network Type',
        'Router Type',
        'Availability Zones',
    )

    data = []
    for net in _network:
        data.append((
            net.id,
            net.name,
            utils.format_list(net.subnets),
        ))

    data_long = []
    for net in _network:
        data_long.append((
            net.id,
            net.name,
            net.status,
            net.project_id,
            network._format_admin_state(net.admin_state_up),
            net.shared,
            utils.format_list(net.subnets),
            net.provider_network_type,
            network._format_router_external(net.router_external),
            utils.format_list(net.availability_zones),
        ))

    def setUp(self):
        super(TestListNetwork, self).setUp()

        # Get the command object to test
        self.cmd = network.ListNetwork(self.app, self.namespace)

        self.network.networks = mock.Mock(return_value=self._network)

    def test_network_list_no_options(self):
        arglist = []
        verifylist = [
            ('external', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_list_external(self):
        arglist = [
            '--external',
        ]
        verifylist = [
            ('external', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_with(
            **{'router:external': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('external', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestSetNetwork(TestNetwork):

    # The network to set.
    _network = network_fakes.FakeNetwork.create_one_network()

    def setUp(self):
        super(TestSetNetwork, self).setUp()

        self.network.update_network = mock.Mock(return_value=None)

        self.network.find_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.SetNetwork(self.app, self.namespace)

    def test_set_this(self):
        arglist = [
            self._network.name,
            '--enable',
            '--name', 'noob',
            '--share',
        ]
        verifylist = [
            ('network', self._network.name),
            ('admin_state', True),
            ('name', 'noob'),
            ('shared', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': 'noob',
            'admin_state_up': True,
            'shared': True,
        }
        self.network.update_network.assert_called_with(self._network, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            self._network.name,
            '--disable',
            '--no-share',
        ]
        verifylist = [
            ('network', self._network.name),
            ('admin_state', False),
            ('shared', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'shared': False,
        }
        self.network.update_network.assert_called_with(self._network, **attrs)
        self.assertIsNone(result)

    def test_set_nothing(self):
        arglist = [self._network.name, ]
        verifylist = [('network', self._network.name), ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)


class TestShowNetwork(TestNetwork):

    # The network to show.
    _network = network_fakes.FakeNetwork.create_one_network()

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'id',
        'name',
        'project_id',
        'router_external',
        'status',
        'subnets',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        utils.format_list(_network.availability_zone_hints),
        utils.format_list(_network.availability_zones),
        _network.id,
        _network.name,
        _network.project_id,
        network._format_router_external(_network.router_external),
        _network.status,
        utils.format_list(_network.subnets),
    )

    def setUp(self):
        super(TestShowNetwork, self).setUp()

        self.network.find_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.ShowNetwork(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('network', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_network.assert_called_with(self._network.name,
                                                     ignore_missing=False)

        self.assertEqual(tuple(self.columns), columns)
        self.assertEqual(list(self.data), list(data))


# Tests for Nova network
#
class TestNetworkCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestNetworkCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestCreateNetworkCompute(TestNetworkCompute):

    # The network to create.
    _network = compute_fakes.FakeNetwork.create_one_network()

    columns = (
        'bridge',
        'bridge_interface',
        'broadcast',
        'cidr',
        'cidr_v6',
        'created_at',
        'deleted',
        'deleted_at',
        'dhcp_server',
        'dhcp_start',
        'dns1',
        'dns2',
        'enable_dhcp',
        'gateway',
        'gateway_v6',
        'host',
        'id',
        'injected',
        'label',
        'mtu',
        'multi_host',
        'netmask',
        'netmask_v6',
        'priority',
        'project_id',
        'rxtx_base',
        'share_address',
        'updated_at',
        'vlan',
        'vpn_private_address',
        'vpn_public_address',
        'vpn_public_port',
    )

    data = (
        _network.bridge,
        _network.bridge_interface,
        _network.broadcast,
        _network.cidr,
        _network.cidr_v6,
        _network.created_at,
        _network.deleted,
        _network.deleted_at,
        _network.dhcp_server,
        _network.dhcp_start,
        _network.dns1,
        _network.dns2,
        _network.enable_dhcp,
        _network.gateway,
        _network.gateway_v6,
        _network.host,
        _network.id,
        _network.injected,
        _network.label,
        _network.mtu,
        _network.multi_host,
        _network.netmask,
        _network.netmask_v6,
        _network.priority,
        _network.project_id,
        _network.rxtx_base,
        _network.share_address,
        _network.updated_at,
        _network.vlan,
        _network.vpn_private_address,
        _network.vpn_public_address,
        _network.vpn_public_port,
    )

    def setUp(self):
        super(TestCreateNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.networks.create.return_value = self._network

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should raise exception here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            "--subnet", self._network.cidr,
            self._network.label,
        ]
        verifylist = [
            ('subnet', self._network.cidr),
            ('name', self._network.label),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.networks.create.assert_called_with(**{
            'cidr': self._network.cidr,
            'label': self._network.label,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkCompute(TestNetworkCompute):

    # The network to delete.
    _network = compute_fakes.FakeNetwork.create_one_network()

    def setUp(self):
        super(TestDeleteNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.networks.delete.return_value = None

        # Return value of utils.find_resource()
        self.compute.networks.get.return_value = self._network

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, None)

    def test_network_delete(self):
        arglist = [
            self._network.label,
        ]
        verifylist = [
            ('network', [self._network.label]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.networks.delete.assert_called_with(self._network.id)
        self.assertIsNone(result)


class TestListNetworkCompute(TestNetworkCompute):

    # The networks going to be listed up.
    _networks = compute_fakes.FakeNetwork.create_networks(count=3)

    columns = (
        'ID',
        'Name',
        'Subnet',
    )

    data = []
    for net in _networks:
        data.append((
            net.id,
            net.label,
            net.cidr,
        ))

    def setUp(self):
        super(TestListNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.networks.list.return_value = self._networks

        # Get the command object to test
        self.cmd = network.ListNetwork(self.app, None)

    def test_network_list_no_options(self):
        arglist = []
        verifylist = [
            ('external', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.compute.networks.list.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowNetworkCompute(TestNetworkCompute):

    # The network to show.
    _network = compute_fakes.FakeNetwork.create_one_network()

    columns = (
        'bridge',
        'bridge_interface',
        'broadcast',
        'cidr',
        'cidr_v6',
        'created_at',
        'deleted',
        'deleted_at',
        'dhcp_server',
        'dhcp_start',
        'dns1',
        'dns2',
        'enable_dhcp',
        'gateway',
        'gateway_v6',
        'host',
        'id',
        'injected',
        'label',
        'mtu',
        'multi_host',
        'netmask',
        'netmask_v6',
        'priority',
        'project_id',
        'rxtx_base',
        'share_address',
        'updated_at',
        'vlan',
        'vpn_private_address',
        'vpn_public_address',
        'vpn_public_port',
    )

    data = (
        _network.bridge,
        _network.bridge_interface,
        _network.broadcast,
        _network.cidr,
        _network.cidr_v6,
        _network.created_at,
        _network.deleted,
        _network.deleted_at,
        _network.dhcp_server,
        _network.dhcp_start,
        _network.dns1,
        _network.dns2,
        _network.enable_dhcp,
        _network.gateway,
        _network.gateway_v6,
        _network.host,
        _network.id,
        _network.injected,
        _network.label,
        _network.mtu,
        _network.multi_host,
        _network.netmask,
        _network.netmask_v6,
        _network.priority,
        _network.project_id,
        _network.rxtx_base,
        _network.share_address,
        _network.updated_at,
        _network.vlan,
        _network.vpn_private_address,
        _network.vpn_public_address,
        _network.vpn_public_port,
    )

    def setUp(self):
        super(TestShowNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Return value of utils.find_resource()
        self.compute.networks.get.return_value = self._network

        # Get the command object to test
        self.cmd = network.ShowNetwork(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._network.label,
        ]
        verifylist = [
            ('network', self._network.label),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, tuple(columns))
        self.assertEqual(self.data, data)
