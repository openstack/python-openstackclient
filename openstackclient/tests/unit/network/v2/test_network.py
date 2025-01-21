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

import random
from unittest import mock
from unittest.mock import call

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.network.v2 import network
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes_v2
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


# Tests for Neutron network
#
class TestNetwork(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains


class TestCreateNetworkIdentityV3(TestNetwork):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # The new network created.
    _network = network_fakes.create_one_network(
        attrs={
            'project_id': project.id,
            'availability_zone_hints': ["nova"],
        }
    )
    qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy(
        attrs={'id': _network.qos_policy_id}
    )

    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'created_at',
        'description',
        'dns_domain',
        'id',
        'ipv4_address_scope',
        'ipv6_address_scope',
        'is_default',
        'is_vlan_transparent',
        'is_vlan_qinq',
        'mtu',
        'name',
        'port_security_enabled',
        'project_id',
        'provider:network_type',
        'provider:physical_network',
        'provider:segmentation_id',
        'qos_policy_id',
        'router:external',
        'shared',
        'status',
        'segments',
        'subnets',
        'tags',
        'revision_number',
        'updated_at',
    )

    data = (
        network.AdminStateColumn(_network.is_admin_state_up),
        format_columns.ListColumn(_network.availability_zone_hints),
        format_columns.ListColumn(_network.availability_zones),
        _network.created_at,
        _network.description,
        _network.dns_domain,
        _network.id,
        _network.ipv4_address_scope_id,
        _network.ipv6_address_scope_id,
        _network.is_default,
        _network.mtu,
        _network.name,
        _network.is_port_security_enabled,
        _network.project_id,
        _network.provider_network_type,
        _network.provider_physical_network,
        _network.provider_segmentation_id,
        _network.qos_policy_id,
        network.RouterExternalColumn(_network.is_router_external),
        _network.is_shared,
        _network.is_vlan_transparent,
        _network.is_vlan_qinq,
        _network.status,
        _network.segments,
        format_columns.ListColumn(_network.subnet_ids),
        format_columns.ListColumn(_network.tags),
        _network.revision_number,
        _network.updated_at,
    )

    def setUp(self):
        super().setUp()

        self.network_client.create_network = mock.Mock(
            return_value=self._network
        )
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, None)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )

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

        self.network_client.create_network.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self._network.name,
            }
        )
        self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            "--disable",
            "--share",
            "--description",
            self._network.description,
            "--mtu",
            str(self._network.mtu),
            "--project",
            self.project.name,
            "--project-domain",
            self.domain.name,
            "--availability-zone-hint",
            "nova",
            "--external",
            "--default",
            "--provider-network-type",
            "vlan",
            "--provider-physical-network",
            "physnet1",
            "--provider-segment",
            "400",
            "--qos-policy",
            self.qos_policy.id,
            "--transparent-vlan",
            "--no-qinq-vlan",
            "--enable-port-security",
            "--dns-domain",
            "example.org.",
            self._network.name,
        ]
        verifylist = [
            ('disable', True),
            ('share', True),
            ('description', self._network.description),
            ('mtu', str(self._network.mtu)),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('availability_zone_hints', ["nova"]),
            ('external', True),
            ('default', True),
            ('provider_network_type', 'vlan'),
            ('physical_network', 'physnet1'),
            ('segmentation_id', '400'),
            ('qos_policy', self.qos_policy.id),
            ('transparent_vlan', True),
            ('qinq_vlan', False),
            ('enable_port_security', True),
            ('name', self._network.name),
            ('dns_domain', 'example.org.'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_network.assert_called_once_with(
            **{
                'admin_state_up': False,
                'availability_zone_hints': ["nova"],
                'name': self._network.name,
                'shared': True,
                'description': self._network.description,
                'mtu': str(self._network.mtu),
                'project_id': self.project.id,
                'is_default': True,
                'router:external': True,
                'provider:network_type': 'vlan',
                'provider:physical_network': 'physnet1',
                'provider:segmentation_id': '400',
                'qos_policy_id': self.qos_policy.id,
                'vlan_transparent': True,
                'vlan_qinq': False,
                'port_security_enabled': True,
                'dns_domain': 'example.org.',
            }
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_other_options(self):
        arglist = [
            "--enable",
            "--no-share",
            "--disable-port-security",
            "--qinq-vlan",
            self._network.name,
        ]
        verifylist = [
            ('enable', True),
            ('no_share', True),
            ('name', self._network.name),
            ('external', False),
            ('qinq_vlan', True),
            ('disable_port_security', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_network.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self._network.name,
                'shared': False,
                'vlan_qinq': True,
                'port_security_enabled': False,
            }
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def _test_create_with_tag(self, add_tags=True):
        arglist = [self._network.name]
        if add_tags:
            arglist += ['--tag', 'red', '--tag', 'blue']
        else:
            arglist += ['--no-tag']
        verifylist = [
            ('name', self._network.name),
            ('enable', True),
            ('share', None),
            ('project', None),
            ('external', False),
        ]
        if add_tags:
            verifylist.append(('tags', ['red', 'blue']))
        else:
            verifylist.append(('no_tag', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_network.assert_called_once_with(
            name=self._network.name, admin_state_up=True
        )
        if add_tags:
            self.network_client.set_tags.assert_called_once_with(
                self._network, tests_utils.CompareBySet(['red', 'blue'])
            )
        else:
            self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_with_tags(self):
        self._test_create_with_tag(add_tags=True)

    def test_create_with_no_tag(self):
        self._test_create_with_tag(add_tags=False)

    def test_create_with_vlan_qinq_and_transparency_enabled(self):
        arglist = [
            "--transparent-vlan",
            "--qinq-vlan",
            self._network.name,
        ]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestCreateNetworkIdentityV2(
    identity_fakes_v2.FakeClientMixin,
    network_fakes.FakeClientMixin,
    tests_utils.TestCommand,
):
    project = identity_fakes_v2.FakeProject.create_one_project()
    # The new network created.
    _network = network_fakes.create_one_network(
        attrs={'project_id': project.id}
    )
    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'created_at',
        'description',
        'dns_domain',
        'id',
        'ipv4_address_scope',
        'ipv6_address_scope',
        'is_default',
        'is_vlan_transparent',
        'is_vlan_qinq',
        'mtu',
        'name',
        'port_security_enabled',
        'project_id',
        'provider:network_type',
        'provider:physical_network',
        'provider:segmentation_id',
        'qos_policy_id',
        'router:external',
        'shared',
        'status',
        'segments',
        'subnets',
        'tags',
        'revision_number',
        'updated_at',
    )

    data = (
        network.AdminStateColumn(_network.is_admin_state_up),
        format_columns.ListColumn(_network.availability_zone_hints),
        format_columns.ListColumn(_network.availability_zones),
        _network.created_at,
        _network.description,
        _network.dns_domain,
        _network.id,
        _network.ipv4_address_scope_id,
        _network.ipv6_address_scope_id,
        _network.is_default,
        _network.mtu,
        _network.name,
        _network.is_port_security_enabled,
        _network.project_id,
        _network.provider_network_type,
        _network.provider_physical_network,
        _network.provider_segmentation_id,
        _network.qos_policy_id,
        network.RouterExternalColumn(_network.is_router_external),
        _network.is_shared,
        _network.is_vlan_transparent,
        _network.is_vlan_qinq,
        _network.status,
        _network.segments,
        format_columns.ListColumn(_network.subnet_ids),
        format_columns.ListColumn(_network.tags),
        _network.revision_number,
        _network.updated_at,
    )

    def setUp(self):
        super().setUp()

        self.network_client.create_network = mock.Mock(
            return_value=self._network
        )
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, None)

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.tenants
        self.projects_mock.get.return_value = self.project

        # There is no DomainManager Mock in fake identity v2.

    def test_create_with_project_identityv2(self):
        arglist = [
            "--project",
            self.project.name,
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

        self.network_client.create_network.assert_called_once_with(
            **{
                'admin_state_up': True,
                'name': self._network.name,
                'project_id': self.project.id,
            }
        )
        self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_with_domain_identityv2(self):
        arglist = [
            "--project",
            self.project.name,
            "--project-domain",
            "domain-name",
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
        super().setUp()

        # The networks to delete
        self._networks = network_fakes.create_networks(count=3)

        self.network_client.delete_network = mock.Mock(return_value=None)

        self.network_client.find_network = network_fakes.get_networks(
            networks=self._networks
        )

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, None)

    def test_delete_one_network(self):
        arglist = [
            self._networks[0].name,
        ]
        verifylist = [
            ('network', [self._networks[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_network.assert_called_once_with(
            self._networks[0]
        )
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
        self.network_client.delete_network.assert_has_calls(calls)
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
        self.network_client.find_network = mock.Mock(side_effect=ret_find)

        # Fake exception in delete_network()
        ret_delete = [
            None,
            exceptions.NotFound('404'),
        ]
        self.network_client.delete_network = mock.Mock(side_effect=ret_delete)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        # The second call of find_network() should fail. So delete_network()
        # was only called twice.
        calls = [
            call(self._networks[0]),
            call(self._networks[1]),
        ]
        self.network_client.delete_network.assert_has_calls(calls)


class TestListNetwork(TestNetwork):
    # The networks going to be listed up.
    _network = network_fakes.create_networks(count=3)

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
        'Tags',
    )

    data = []
    for net in _network:
        data.append(
            (
                net.id,
                net.name,
                format_columns.ListColumn(net.subnet_ids),
            )
        )

    data_long = []
    for net in _network:
        data_long.append(
            (
                net.id,
                net.name,
                net.status,
                net.project_id,
                network.AdminStateColumn(net.is_admin_state_up),
                net.is_shared,
                format_columns.ListColumn(net.subnet_ids),
                net.provider_network_type,
                network.RouterExternalColumn(net.is_router_external),
                format_columns.ListColumn(net.availability_zones),
                format_columns.ListColumn(net.tags),
            )
        )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = network.ListNetwork(self.app, None)

        self.network_client.networks = mock.Mock(return_value=self._network)

        self._agent = network_fakes.create_one_network_agent()
        self.network_client.get_agent = mock.Mock(return_value=self._agent)

        self.network_client.dhcp_agent_hosting_networks = mock.Mock(
            return_value=self._network
        )

        # TestListTagMixin
        self._tag_list_resource_mock = self.network_client.networks

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

        self.network_client.networks.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.networks.assert_called_once_with(
            **{'router:external': True, 'is_router_external': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.networks.assert_called_once_with(
            **{'router:external': False, 'is_router_external': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.networks.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, list(data))

    def test_list_name(self):
        test_name = "fakename"
        arglist = [
            '--name',
            test_name,
        ]
        verifylist = [
            ('external', False),
            ('long', False),
            ('name', test_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.networks.assert_called_once_with(
            **{'name': test_name}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.networks.assert_called_once_with(
            **{'admin_state_up': True, 'is_admin_state_up': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_disable(self):
        arglist = [
            '--disable',
        ]
        verifylist = [('long', False), ('external', False), ('disable', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.networks.assert_called_once_with(
            **{'admin_state_up': False, 'is_admin_state_up': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_project(self):
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
        self.network_client.networks.assert_called_once_with(
            **{'project_id': project.id}
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_project_domain(self):
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
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'project_id': project.id}

        self.network_client.networks.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.networks.assert_called_once_with(
            **{'shared': True, 'is_shared': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.networks.assert_called_once_with(
            **{'shared': False, 'is_shared': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_status(self):
        choices = ['ACTIVE', 'BUILD', 'DOWN', 'ERROR']
        test_status = random.choice(choices)
        arglist = [
            '--status',
            test_status,
        ]
        verifylist = [
            ('long', False),
            ('status', test_status),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.networks.assert_called_once_with(
            **{'status': test_status}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_provider_network_type(self):
        network_type = self._network[0].provider_network_type
        arglist = [
            '--provider-network-type',
            network_type,
        ]
        verifylist = [
            ('provider_network_type', network_type),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.networks.assert_called_once_with(
            **{
                'provider:network_type': network_type,
                'provider_network_type': network_type,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_provider_physical_network(self):
        physical_network = self._network[0].provider_physical_network
        arglist = [
            '--provider-physical-network',
            physical_network,
        ]
        verifylist = [
            ('physical_network', physical_network),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.networks.assert_called_once_with(
            **{
                'provider:physical_network': physical_network,
                'provider_physical_network': physical_network,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_provider_segment(self):
        segmentation_id = self._network[0].provider_segmentation_id
        arglist = [
            '--provider-segment',
            segmentation_id,
        ]
        verifylist = [
            ('segmentation_id', segmentation_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.networks.assert_called_once_with(
            **{
                'provider:segmentation_id': segmentation_id,
                'provider_segmentation_id': segmentation_id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_network_list_dhcp_agent(self):
        arglist = ['--agent', self._agent.id]
        verifylist = [
            ('agent_id', self._agent.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.dhcp_agent_hosting_networks.assert_called_once_with(
            self._agent
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(list(data), list(self.data))

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

        self.network_client.networks.assert_called_once_with(
            **{
                'tags': 'red,blue',
                'any_tags': 'red,green',
                'not_tags': 'orange,yellow',
                'not_any_tags': 'black,white',
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))


class TestSetNetwork(TestNetwork):
    # The network to set.
    _network = network_fakes.create_one_network({'tags': ['green', 'red']})
    qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy(
        attrs={'id': _network.qos_policy_id}
    )

    def setUp(self):
        super().setUp()

        self.network_client.update_network = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)

        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )

        # Get the command object to test
        self.cmd = network.SetNetwork(self.app, None)

    def test_set_this(self):
        arglist = [
            self._network.name,
            '--enable',
            '--name',
            'noob',
            '--share',
            '--description',
            self._network.description,
            '--dns-domain',
            'example.org.',
            '--external',
            '--default',
            '--provider-network-type',
            'vlan',
            '--provider-physical-network',
            'physnet1',
            '--provider-segment',
            '400',
            '--enable-port-security',
            '--qos-policy',
            self.qos_policy.name,
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
            ('enable_port_security', True),
            ('qos_policy', self.qos_policy.name),
            ('dns_domain', 'example.org.'),
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
            'port_security_enabled': True,
            'qos_policy_id': self.qos_policy.id,
            'dns_domain': 'example.org.',
        }
        self.network_client.update_network.assert_called_once_with(
            self._network, **attrs
        )
        self.assertIsNone(result)

    def test_set_that(self):
        arglist = [
            self._network.name,
            '--disable',
            '--no-share',
            '--internal',
            '--disable-port-security',
            '--no-qos-policy',
        ]
        verifylist = [
            ('network', self._network.name),
            ('disable', True),
            ('no_share', True),
            ('internal', True),
            ('disable_port_security', True),
            ('no_qos_policy', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'shared': False,
            'router:external': False,
            'port_security_enabled': False,
            'qos_policy_id': None,
        }
        self.network_client.update_network.assert_called_once_with(
            self._network, **attrs
        )
        self.assertIsNone(result)

    def test_set_to_empty(self):
        # Test if empty strings are accepted to clear any of the fields,
        # so once they are set to a value its possible to clear them again.

        arglist = [
            self._network.name,
            '--name',
            '',
            '--description',
            '',
            '--dns-domain',
            '',
        ]
        verifylist = [
            ('network', self._network.name),
            ('description', ''),
            ('name', ''),
            ('dns_domain', ''),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': '',
            'description': '',
            'dns_domain': '',
        }
        self.network_client.update_network.assert_called_once_with(
            self._network, **attrs
        )
        self.assertIsNone(result)

    def test_set_nothing(self):
        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('network', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_network.called)
        self.assertFalse(self.network_client.set_tags.called)
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
        arglist.append(self._network.name)
        verifylist.append(('network', self._network.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_network.called)
        self.network_client.set_tags.assert_called_once_with(
            self._network, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_set_with_tags(self):
        self._test_set_tags(with_tags=True)

    def test_set_with_no_tag(self):
        self._test_set_tags(with_tags=False)


class TestShowNetwork(TestNetwork):
    # The network to show.
    _network = network_fakes.create_one_network()
    columns = (
        'admin_state_up',
        'availability_zone_hints',
        'availability_zones',
        'created_at',
        'description',
        'dns_domain',
        'id',
        'ipv4_address_scope',
        'ipv6_address_scope',
        'is_default',
        'is_vlan_transparent',
        'is_vlan_qinq',
        'mtu',
        'name',
        'port_security_enabled',
        'project_id',
        'provider:network_type',
        'provider:physical_network',
        'provider:segmentation_id',
        'qos_policy_id',
        'router:external',
        'shared',
        'status',
        'segments',
        'subnets',
        'tags',
        'revision_number',
        'updated_at',
    )

    data = (
        network.AdminStateColumn(_network.is_admin_state_up),
        format_columns.ListColumn(_network.availability_zone_hints),
        format_columns.ListColumn(_network.availability_zones),
        _network.created_at,
        _network.description,
        _network.dns_domain,
        _network.id,
        _network.ipv4_address_scope_id,
        _network.ipv6_address_scope_id,
        _network.is_default,
        _network.mtu,
        _network.name,
        _network.is_port_security_enabled,
        _network.project_id,
        _network.provider_network_type,
        _network.provider_physical_network,
        _network.provider_segmentation_id,
        _network.qos_policy_id,
        network.RouterExternalColumn(_network.is_router_external),
        _network.is_shared,
        _network.is_vlan_transparent,
        _network.is_vlan_qinq,
        _network.status,
        _network.segments,
        format_columns.ListColumn(_network.subnet_ids),
        format_columns.ListColumn(_network.tags),
        _network.revision_number,
        _network.updated_at,
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )

        # Get the command object to test
        self.cmd = network.ShowNetwork(self.app, None)

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
            self._network.name,
        ]
        verifylist = [
            ('network', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_called_once_with(
            self._network.name, ignore_missing=False
        )

        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)


class TestUnsetNetwork(TestNetwork):
    # The network to set.
    _network = network_fakes.create_one_network({'tags': ['green', 'red']})
    qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy(
        attrs={'id': _network.qos_policy_id}
    )

    def setUp(self):
        super().setUp()

        self.network_client.update_network = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)

        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self.qos_policy
        )

        # Get the command object to test
        self.cmd = network.UnsetNetwork(self.app, None)

    def test_unset_nothing(self):
        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('network', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_network.called)
        self.assertFalse(self.network_client.set_tags.called)
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
        arglist.append(self._network.name)
        verifylist.append(('network', self._network.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_network.called)
        self.network_client.set_tags.assert_called_once_with(
            self._network, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_unset_with_tags(self):
        self._test_unset_tags(with_tags=True)

    def test_unset_with_all_tag(self):
        self._test_unset_tags(with_tags=False)
