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
from mock import call
import random

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.network.v2 import network
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes_v2
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


# Tests for Neutron network
#
class TestNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateNetworkIdentityV3(TestNetwork):

    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # The new network created.
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={
            'tenant_id': project.id,
            'availability_zone_hints': ["nova"],
        }
    )

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'description',
        'id',
        'is_default',
        'name',
        'port_security_enabled',
        'project_id',
        'provider_network_type',
        'router:external',
        'shared',
        'status',
        'subnets',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        utils.format_list(_network.availability_zone_hints),
        utils.format_list(_network.availability_zones),
        _network.description,
        _network.id,
        _network.is_default,
        _network.name,
        _network.is_port_security_enabled,
        _network.project_id,
        _network.provider_network_type,
        network._format_router_external(_network.is_router_external),
        _network.shared,
        _network.status,
        utils.format_list(_network.subnets),
    )

    def setUp(self):
        super(TestCreateNetworkIdentityV3, self).setUp()

        self.network.create_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, self.namespace)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('name', self._network.name),
            ('enable', True),
            ('share', None),
            ('project', None),
            ('external', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_once_with(**{
            'admin_state_up': True,
            'name': self._network.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            "--disable",
            "--share",
            "--description", self._network.description,
            "--project", self.project.name,
            "--project-domain", self.domain.name,
            "--availability-zone-hint", "nova",
            "--external", "--default",
            "--provider-network-type", "vlan",
            "--provider-physical-network", "physnet1",
            "--provider-segment", "400",
            "--transparent-vlan",
            "--enable-port-security",
            self._network.name,
        ]
        verifylist = [
            ('disable', True),
            ('share', True),
            ('description', self._network.description),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('availability_zone_hints', ["nova"]),
            ('external', True),
            ('default', True),
            ('provider_network_type', 'vlan'),
            ('physical_network', 'physnet1'),
            ('segmentation_id', '400'),
            ('transparent_vlan', True),
            ('enable_port_security', True),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_network.assert_called_once_with(**{
            'admin_state_up': False,
            'availability_zone_hints': ["nova"],
            'name': self._network.name,
            'shared': True,
            'description': self._network.description,
            'tenant_id': self.project.id,
            'is_default': True,
            'router:external': True,
            'provider:network_type': 'vlan',
            'provider:physical_network': 'physnet1',
            'provider:segmentation_id': '400',
            'vlan_transparent': True,
            'port_security_enabled': True,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_other_options(self):
        arglist = [
            "--enable",
            "--no-share",
            "--disable-port-security",
            self._network.name,
        ]
        verifylist = [
            ('enable', True),
            ('no_share', True),
            ('name', self._network.name),
            ('external', False),
            ('disable_port_security', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_once_with(**{
            'admin_state_up': True,
            'name': self._network.name,
            'shared': False,
            'port_security_enabled': False,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestCreateNetworkIdentityV2(TestNetwork):

    project = identity_fakes_v2.FakeProject.create_one_project()
    # The new network created.
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={'tenant_id': project.id}
    )

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'description',
        'id',
        'is_default',
        'name',
        'port_security_enabled',
        'project_id',
        'provider_network_type',
        'router:external',
        'shared',
        'status',
        'subnets',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        utils.format_list(_network.availability_zone_hints),
        utils.format_list(_network.availability_zones),
        _network.description,
        _network.id,
        _network.is_default,
        _network.name,
        _network.is_port_security_enabled,
        _network.project_id,
        _network.provider_network_type,
        network._format_router_external(_network.is_router_external),
        _network.shared,
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
        self.projects_mock.get.return_value = self.project

        # There is no DomainManager Mock in fake identity v2.

    def test_create_with_project_identityv2(self):
        arglist = [
            "--project", self.project.name,
            self._network.name,
        ]
        verifylist = [
            ('enable', True),
            ('share', None),
            ('name', self._network.name),
            ('project', self.project.name),
            ('external', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_once_with(**{
            'admin_state_up': True,
            'name': self._network.name,
            'tenant_id': self.project.id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_domain_identityv2(self):
        arglist = [
            "--project", self.project.name,
            "--project-domain", "domain-name",
            self._network.name,
        ]
        verifylist = [
            ('enable', True),
            ('share', None),
            ('project', self.project.name),
            ('project_domain', "domain-name"),
            ('name', self._network.name),
            ('external', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            AttributeError,
            self.cmd.take_action,
            parsed_args,
        )


class TestDeleteNetwork(TestNetwork):

    def setUp(self):
        super(TestDeleteNetwork, self).setUp()

        # The networks to delete
        self._networks = network_fakes.FakeNetwork.create_networks(count=3)

        self.network.delete_network = mock.Mock(return_value=None)

        self.network.find_network = network_fakes.FakeNetwork.get_networks(
            networks=self._networks)

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, self.namespace)

    def test_delete_one_network(self):
        arglist = [
            self._networks[0].name,
        ]
        verifylist = [
            ('network', [self._networks[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_network.assert_called_once_with(self._networks[0])
        self.assertIsNone(result)

    def test_delete_multiple_networks(self):
        arglist = []
        for n in self._networks:
            arglist.append(n.id)
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self._networks:
            calls.append(call(n))
        self.network.delete_network.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_networks_exception(self):
        arglist = [
            self._networks[0].id,
            'xxxx-yyyy-zzzz',
            self._networks[1].id,
        ]
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception in find_network()
        ret_find = [
            self._networks[0],
            exceptions.NotFound('404'),
            self._networks[1],
        ]
        self.network.find_network = mock.Mock(side_effect=ret_find)

        # Fake exception in delete_network()
        ret_delete = [
            None,
            exceptions.NotFound('404'),
        ]
        self.network.delete_network = mock.Mock(side_effect=ret_delete)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        # The second call of find_network() should fail. So delete_network()
        # was only called twice.
        calls = [
            call(self._networks[0]),
            call(self._networks[1]),
        ]
        self.network.delete_network.assert_has_calls(calls)


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
            network._format_router_external(net.is_router_external),
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

        self.network.networks.assert_called_once_with()
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

        self.network.networks.assert_called_once_with(
            **{'router:external': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_list_internal(self):
        arglist = [
            '--internal',
        ]
        verifylist = [
            ('internal', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'router:external': False}
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

        self.network.networks.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_list_name(self):
        test_name = "fakename"
        arglist = [
            '--name', test_name,
        ]
        verifylist = [
            ('external', False),
            ('long', False),
            ('name', test_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'name': test_name}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_enable(self):
        arglist = [
            '--enable',
        ]
        verifylist = [
            ('long', False),
            ('external', False),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'admin_state_up': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_disable(self):
        arglist = [
            '--disable',
        ]
        verifylist = [
            ('long', False),
            ('external', False),
            ('disable', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'admin_state_up': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network.networks.assert_called_once_with(
            **{'tenant_id': project.id}
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_networ_list_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
            '--project-domain', project.domain_id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'tenant_id': project.id}

        self.network.networks.assert_called_once_with(**filters)

    def test_network_list_share(self):
        arglist = [
            '--share',
        ]
        verifylist = [
            ('long', False),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'shared': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_no_share(self):
        arglist = [
            '--no-share',
        ]
        verifylist = [
            ('long', False),
            ('no_share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'shared': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_status(self):
        choices = ['ACTIVE', 'BUILD', 'DOWN', 'ERROR']
        test_status = random.choice(choices)
        arglist = [
            '--status', test_status,
        ]
        verifylist = [
            ('long', False),
            ('status', test_status),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_once_with(
            **{'status': test_status}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


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
            '--description', self._network.description,
            '--external',
            '--default',
            '--provider-network-type', 'vlan',
            '--provider-physical-network', 'physnet1',
            '--provider-segment', '400',
            '--no-transparent-vlan',
            '--enable-port-security',
        ]
        verifylist = [
            ('network', self._network.name),
            ('enable', True),
            ('description', self._network.description),
            ('name', 'noob'),
            ('share', True),
            ('external', True),
            ('default', True),
            ('provider_network_type', 'vlan'),
            ('physical_network', 'physnet1'),
            ('segmentation_id', '400'),
            ('no_transparent_vlan', True),
            ('enable_port_security', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': 'noob',
            'admin_state_up': True,
            'description': self._network.description,
            'shared': True,
            'router:external': True,
            'is_default': True,
            'provider:network_type': 'vlan',
            'provider:physical_network': 'physnet1',
            'provider:segmentation_id': '400',
            'vlan_transparent': False,
            'port_security_enabled': True,
        }
        self.network.update_network.assert_called_once_with(
            self._network, **attrs)
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            self._network.name,
            '--disable',
            '--no-share',
            '--internal',
            '--disable-port-security',
        ]
        verifylist = [
            ('network', self._network.name),
            ('disable', True),
            ('no_share', True),
            ('internal', True),
            ('disable_port_security', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'shared': False,
            'router:external': False,
            'port_security_enabled': False,
        }
        self.network.update_network.assert_called_once_with(
            self._network, **attrs)
        self.assertIsNone(result)

    def test_set_nothing(self):
        arglist = [self._network.name, ]
        verifylist = [('network', self._network.name), ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_network.assert_called_once_with(
            self._network, **attrs)
        self.assertIsNone(result)


class TestShowNetwork(TestNetwork):

    # The network to show.
    _network = network_fakes.FakeNetwork.create_one_network()

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'description',
        'id',
        'is_default',
        'name',
        'port_security_enabled',
        'project_id',
        'provider_network_type',
        'router:external',
        'shared',
        'status',
        'subnets',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        utils.format_list(_network.availability_zone_hints),
        utils.format_list(_network.availability_zones),
        _network.description,
        _network.id,
        _network.is_default,
        _network.name,
        _network.is_port_security_enabled,
        _network.project_id,
        _network.provider_network_type,
        network._format_router_external(_network.is_router_external),
        _network.shared,
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

        self.network.find_network.assert_called_once_with(
            self._network.name, ignore_missing=False)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


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

        self.compute.networks.create.assert_called_once_with(**{
            'cidr': self._network.cidr,
            'label': self._network.label,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkCompute(TestNetworkCompute):

    def setUp(self):
        super(TestDeleteNetworkCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # The networks to delete
        self._networks = compute_fakes.FakeNetwork.create_networks(count=3)

        self.compute.networks.delete.return_value = None

        # Return value of utils.find_resource()
        self.compute.networks.get = \
            compute_fakes.FakeNetwork.get_networks(networks=self._networks)

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, None)

    def test_delete_one_network(self):
        arglist = [
            self._networks[0].label,
        ]
        verifylist = [
            ('network', [self._networks[0].label]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.networks.delete.assert_called_once_with(
            self._networks[0].id)
        self.assertIsNone(result)

    def test_delete_multiple_networks(self):
        arglist = []
        for n in self._networks:
            arglist.append(n.label)
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self._networks:
            calls.append(call(n.id))
        self.compute.networks.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_networks_exception(self):
        arglist = [
            self._networks[0].id,
            'xxxx-yyyy-zzzz',
            self._networks[1].id,
        ]
        verifylist = [
            ('network', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception in utils.find_resource()
        # In compute v2, we use utils.find_resource() to find a network.
        # It calls get() several times, but find() only one time. So we
        # choose to fake get() always raise exception, then pass through.
        # And fake find() to find the real network or not.
        self.compute.networks.get.side_effect = Exception()
        ret_find = [
            self._networks[0],
            Exception(),
            self._networks[1],
        ]
        self.compute.networks.find.side_effect = ret_find

        # Fake exception in delete()
        ret_delete = [
            None,
            Exception(),
        ]
        self.compute.networks.delete = mock.Mock(side_effect=ret_delete)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        # The second call of utils.find_resource() should fail. So delete()
        # was only called twice.
        calls = [
            call(self._networks[0].id),
            call(self._networks[1].id),
        ]
        self.compute.networks.delete.assert_has_calls(calls)


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

        self.compute.networks.list.assert_called_once_with()
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

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
