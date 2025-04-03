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

from unittest import mock
from unittest.mock import call
import uuid

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.network.v2 import port
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as test_utils


LIST_FIELDS_TO_RETRIEVE = ['id', 'name', 'mac_address', 'fixed_ips', 'status']
LIST_FIELDS_TO_RETRIEVE_LONG = [
    'security_groups',
    'device_owner',
    'tags',
    'trunk_details',
]


class TestPort(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects

    @staticmethod
    def _get_common_cols_data(fake_port):
        columns = (
            'admin_state_up',
            'allowed_address_pairs',
            'binding_host_id',
            'binding_profile',
            'binding_vif_details',
            'binding_vif_type',
            'binding_vnic_type',
            'created_at',
            'data_plane_status',
            'description',
            'device_id',
            'device_owner',
            'device_profile',
            'dns_assignment',
            'dns_domain',
            'dns_name',
            'extra_dhcp_opts',
            'fixed_ips',
            'hardware_offload_type',
            'hints',
            'id',
            'ip_allocation',
            'mac_address',
            'name',
            'network_id',
            'numa_affinity_policy',
            'port_security_enabled',
            'project_id',
            'propagate_uplink_status',
            'resource_request',
            'revision_number',
            'qos_network_policy_id',
            'qos_policy_id',
            'security_group_ids',
            'status',
            'tags',
            'trusted',
            'trunk_details',
            'updated_at',
        )

        data = (
            port.AdminStateColumn(fake_port.is_admin_state_up),
            format_columns.ListDictColumn(fake_port.allowed_address_pairs),
            fake_port.binding_host_id,
            format_columns.DictColumn(fake_port.binding_profile),
            format_columns.DictColumn(fake_port.binding_vif_details),
            fake_port.binding_vif_type,
            fake_port.binding_vnic_type,
            fake_port.created_at,
            fake_port.data_plane_status,
            fake_port.description,
            fake_port.device_id,
            fake_port.device_owner,
            fake_port.device_profile,
            format_columns.ListDictColumn(fake_port.dns_assignment),
            fake_port.dns_domain,
            fake_port.dns_name,
            format_columns.ListDictColumn(fake_port.extra_dhcp_opts),
            format_columns.ListDictColumn(fake_port.fixed_ips),
            fake_port.hardware_offload_type,
            fake_port.hints,
            fake_port.id,
            fake_port.ip_allocation,
            fake_port.mac_address,
            fake_port.name,
            fake_port.network_id,
            fake_port.numa_affinity_policy,
            fake_port.is_port_security_enabled,
            fake_port.project_id,
            fake_port.propagate_uplink_status,
            fake_port.resource_request,
            fake_port.revision_number,
            fake_port.qos_network_policy_id,
            fake_port.qos_policy_id,
            format_columns.ListColumn(fake_port.security_group_ids),
            fake_port.status,
            format_columns.ListColumn(fake_port.tags),
            fake_port.trusted,
            fake_port.trunk_details,
            fake_port.updated_at,
        )

        return columns, data


class TestCreatePort(TestPort):
    _port = network_fakes.create_one_port()
    columns, data = TestPort._get_common_cols_data(_port)

    def setUp(self):
        super().setUp()

        self.network_client.create_port = mock.Mock(return_value=self._port)
        self.network_client.set_tags = mock.Mock(return_value=None)
        fake_net = network_fakes.create_one_network(
            {
                'id': self._port.network_id,
            }
        )
        self.network_client.find_network = mock.Mock(return_value=fake_net)
        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network_client.find_subnet = mock.Mock(
            return_value=self.fake_subnet
        )
        self.network_client.find_extension = mock.Mock(return_value=[])
        # Get the command object to test
        self.cmd = port.CreatePort(self.app, None)

    def test_create_default_options(self):
        arglist = [
            '--network',
            self._port.network_id,
            'test-port',
        ]
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'name': 'test-port',
            }
        )
        self.assertFalse(self.network_client.set_tags.called)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_full_options(self):
        arglist = [
            '--mac-address',
            'aa:aa:aa:aa:aa:aa',
            '--fixed-ip',
            f'subnet={self.fake_subnet.id},ip-address=10.0.0.2',
            '--description',
            self._port.description,
            '--device',
            'deviceid',
            '--device-owner',
            'fakeowner',
            '--disable',
            '--vnic-type',
            'macvtap',
            '--binding-profile',
            'foo=bar',
            '--binding-profile',
            'foo2=bar2',
            '--network',
            self._port.network_id,
            '--dns-domain',
            'example.org',
            '--dns-name',
            '8.8.8.8',
            'test-port',
        ]
        verifylist = [
            ('mac_address', 'aa:aa:aa:aa:aa:aa'),
            (
                'fixed_ip',
                [{'subnet': self.fake_subnet.id, 'ip-address': '10.0.0.2'}],
            ),
            ('description', self._port.description),
            ('device', 'deviceid'),
            ('device_owner', 'fakeowner'),
            ('disable', True),
            ('vnic_type', 'macvtap'),
            ('binding_profile', {'foo': 'bar', 'foo2': 'bar2'}),
            ('network', self._port.network_id),
            ('dns_domain', 'example.org'),
            ('dns_name', '8.8.8.8'),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'mac_address': 'aa:aa:aa:aa:aa:aa',
                'fixed_ips': [
                    {
                        'subnet_id': self.fake_subnet.id,
                        'ip_address': '10.0.0.2',
                    }
                ],
                'description': self._port.description,
                'device_id': 'deviceid',
                'device_owner': 'fakeowner',
                'admin_state_up': False,
                'binding:vnic_type': 'macvtap',
                'binding:profile': {'foo': 'bar', 'foo2': 'bar2'},
                'network_id': self._port.network_id,
                'dns_domain': 'example.org',
                'dns_name': '8.8.8.8',
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_invalid_json_binding_profile(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--binding-profile',
            '{"parent_name":"fake_parent"',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_create_invalid_key_value_binding_profile(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--binding-profile',
            'key',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_create_json_binding_profile(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--binding-profile',
            '{"parent_name":"fake_parent"}',
            '--binding-profile',
            '{"tag":42}',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            ('binding_profile', {'parent_name': 'fake_parent', 'tag': 42}),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'binding:profile': {'parent_name': 'fake_parent', 'tag': 42},
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_security_group(self):
        secgroup = network_fakes.FakeSecurityGroup.create_one_security_group()
        self.network_client.find_security_group = mock.Mock(
            return_value=secgroup
        )
        arglist = [
            '--network',
            self._port.network_id,
            '--security-group',
            secgroup.id,
            'test-port',
        ]

        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('security_groups', [secgroup.id]),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'security_group_ids': [secgroup.id],
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_port_with_dns_name(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--dns-name',
            '8.8.8.8',
            'test-port',
        ]
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('dns_name', '8.8.8.8'),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'dns_name': '8.8.8.8',
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_security_groups(self):
        sg_1 = network_fakes.FakeSecurityGroup.create_one_security_group()
        sg_2 = network_fakes.FakeSecurityGroup.create_one_security_group()
        self.network_client.find_security_group = mock.Mock(
            side_effect=[sg_1, sg_2]
        )
        arglist = [
            '--network',
            self._port.network_id,
            '--security-group',
            sg_1.id,
            '--security-group',
            sg_2.id,
            'test-port',
        ]
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('security_groups', [sg_1.id, sg_2.id]),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'security_group_ids': [sg_1.id, sg_2.id],
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_no_security_groups(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--no-security-group',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            ('security_groups', []),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'security_group_ids': [],
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_no_fixed_ips(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--no-fixed-ip',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            ('no_fixed_ip', True),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'fixed_ips': [],
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_port_with_allowed_address_pair_ipaddr(self):
        pairs = [
            {'ip_address': '192.168.1.123'},
            {'ip_address': '192.168.1.45'},
        ]
        arglist = [
            '--network',
            self._port.network_id,
            '--allowed-address',
            'ip-address=192.168.1.123',
            '--allowed-address',
            'ip-address=192.168.1.45',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            (
                'allowed_address_pairs',
                [
                    {'ip-address': '192.168.1.123'},
                    {'ip-address': '192.168.1.45'},
                ],
            ),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'allowed_address_pairs': pairs,
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_port_with_allowed_address_pair(self):
        pairs = [
            {
                'ip_address': '192.168.1.123',
                'mac_address': 'aa:aa:aa:aa:aa:aa',
            },
            {'ip_address': '192.168.1.45', 'mac_address': 'aa:aa:aa:aa:aa:b1'},
        ]
        arglist = [
            '--network',
            self._port.network_id,
            '--allowed-address',
            'ip-address=192.168.1.123,mac-address=aa:aa:aa:aa:aa:aa',
            '--allowed-address',
            'ip-address=192.168.1.45,mac-address=aa:aa:aa:aa:aa:b1',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            (
                'allowed_address_pairs',
                [
                    {
                        'ip-address': '192.168.1.123',
                        'mac-address': 'aa:aa:aa:aa:aa:aa',
                    },
                    {
                        'ip-address': '192.168.1.45',
                        'mac-address': 'aa:aa:aa:aa:aa:b1',
                    },
                ],
            ),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'allowed_address_pairs': pairs,
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_port_with_qos(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        arglist = [
            '--network',
            self._port.network_id,
            '--qos-policy',
            qos_policy.id,
            'test-port',
        ]
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('qos_policy', qos_policy.id),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'qos_policy_id': qos_policy.id,
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_port_security_enabled(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--enable-port-security',
            'test-port',
        ]
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('enable_port_security', True),
            ('name', 'test-port'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'port_security_enabled': True,
                'name': 'test-port',
            }
        )

    def test_create_port_security_disabled(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--disable-port-security',
            'test-port',
        ]
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('disable_port_security', True),
            ('name', 'test-port'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'port_security_enabled': False,
                'name': 'test-port',
            }
        )

    def _test_create_with_tag(self, add_tags=True, add_tags_in_post=True):
        arglist = [
            '--network',
            self._port.network_id,
            'test-port',
        ]
        if add_tags:
            arglist += ['--tag', 'red', '--tag', 'blue']
        else:
            arglist += ['--no-tag']
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('enable', True),
            ('name', 'test-port'),
        ]
        if add_tags:
            verifylist.append(('tags', ['red', 'blue']))
        else:
            verifylist.append(('no_tag', True))

        self.network_client.find_extension = mock.Mock(
            return_value=add_tags_in_post
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = {
            'admin_state_up': True,
            'network_id': self._port.network_id,
            'name': 'test-port',
        }
        if add_tags_in_post:
            if add_tags:
                args['tags'] = sorted(['red', 'blue'])
            else:
                args['tags'] = []
            self.network_client.create_port.assert_called_once()
            # Now we need to verify if arguments to call create_port are as
            # expected,
            # But we can't simply use assert_called_once_with() method because
            # duplicates from 'tags' are removed with
            # list(set(parsed_args.tags)) and that don't quarantee order of
            # tags list which is used to call create_port().
            create_port_call_kwargs = (
                self.network_client.create_port.call_args[1]
            )
            create_port_call_kwargs['tags'] = sorted(
                create_port_call_kwargs['tags']
            )
            self.assertDictEqual(args, create_port_call_kwargs)
        else:
            self.network_client.create_port.assert_called_once_with(
                admin_state_up=True,
                network_id=self._port.network_id,
                name='test-port',
            )
            if add_tags:
                self.network_client.set_tags.assert_called_once_with(
                    self._port, test_utils.CompareBySet(['red', 'blue'])
                )
            else:
                self.assertFalse(self.network_client.set_tags.called)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_tags(self):
        self._test_create_with_tag(add_tags=True, add_tags_in_post=True)

    def test_create_with_no_tag(self):
        self._test_create_with_tag(add_tags=False, add_tags_in_post=True)

    def test_create_with_tags_using_put(self):
        self._test_create_with_tag(add_tags=True, add_tags_in_post=False)

    def test_create_with_no_tag_using_put(self):
        self._test_create_with_tag(add_tags=False, add_tags_in_post=False)

    def _test_create_with_uplink_status_propagation(self, enable=True):
        arglist = [
            '--network',
            self._port.network_id,
            'test-port',
        ]
        if enable:
            arglist += ['--enable-uplink-status-propagation']
        else:
            arglist += ['--disable-uplink-status-propagation']
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('name', 'test-port'),
        ]
        if enable:
            verifylist.append(('enable_uplink_status_propagation', True))
        else:
            verifylist.append(('disable_uplink_status_propagation', True))
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'propagate_uplink_status': enable,
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_uplink_status_propagation_enabled(self):
        self._test_create_with_uplink_status_propagation(enable=True)

    def test_create_with_uplink_status_propagation_disabled(self):
        self._test_create_with_uplink_status_propagation(enable=False)

    def test_create_port_with_extra_dhcp_option(self):
        extra_dhcp_options = [
            {
                'opt_name': 'classless-static-route',
                'opt_value': '169.254.169.254/32,22.2.0.2,0.0.0.0/0,22.2.0.1',
                'ip_version': '4',
            },
            {
                'opt_name': 'dns-server',
                'opt_value': '240C::6666',
                'ip_version': '6',
            },
        ]
        arglist = [
            '--network',
            self._port.network_id,
            '--extra-dhcp-option',
            'name=classless-static-route,'
            'value=169.254.169.254/32,22.2.0.2,'
            '0.0.0.0/0,22.2.0.1,'
            'ip-version=4',
            '--extra-dhcp-option',
            'name=dns-server,value=240C::6666,ip-version=6',
            'test-port',
        ]

        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            (
                'extra_dhcp_options',
                [
                    {
                        'name': 'classless-static-route',
                        'value': '169.254.169.254/32,22.2.0.2,'
                        '0.0.0.0/0,22.2.0.1',
                        'ip-version': '4',
                    },
                    {
                        'name': 'dns-server',
                        'value': '240C::6666',
                        'ip-version': '6',
                    },
                ],
            ),
            ('name', 'test-port'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'extra_dhcp_opts': extra_dhcp_options,
                'name': 'test-port',
            }
        )

    def _test_create_with_numa_affinity_policy(self, policy=None):
        arglist = [
            '--network',
            self._port.network_id,
            'test-port',
        ]
        if policy:
            arglist += [f'--numa-policy-{policy}']

        numa_affinity_policy = None if not policy else policy
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('name', 'test-port'),
        ]
        if policy:
            verifylist.append((f'numa_policy_{policy}', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        create_args = {
            'admin_state_up': True,
            'network_id': self._port.network_id,
            'name': 'test-port',
        }
        if numa_affinity_policy:
            create_args['numa_affinity_policy'] = numa_affinity_policy
        self.network_client.create_port.assert_called_once_with(**create_args)

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_numa_affinity_policy_required(self):
        self._test_create_with_numa_affinity_policy(policy='required')

    def test_create_with_numa_affinity_policy_preferred(self):
        self._test_create_with_numa_affinity_policy(policy='preferred')

    def test_create_with_numa_affinity_policy_legacy(self):
        self._test_create_with_numa_affinity_policy(policy='legacy')

    def test_create_with_numa_affinity_policy_null(self):
        self._test_create_with_numa_affinity_policy()

    def test_create_with_device_profile(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--device-profile',
            'cyborg_device_profile_1',
            'test-port',
        ]

        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            (
                'device_profile',
                self._port.device_profile,
            ),
            ('name', 'test-port'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        create_args = {
            'admin_state_up': True,
            'network_id': self._port.network_id,
            'name': 'test-port',
            'device_profile': 'cyborg_device_profile_1',
        }
        self.network_client.create_port.assert_called_once_with(**create_args)
        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_hints_invalid_json(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--hint',
            'invalid json',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_create_hints_invalid_alias(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--hint',
            'invalid-alias=value',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            ('hint', {'invalid-alias': 'value'}),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_create_hints_invalid_value(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--hint',
            'ovs-tx-steering=invalid-value',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            ('hint', {'ovs-tx-steering': 'invalid-value'}),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_create_hints_valid_alias_value(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--hint',
            'ovs-tx-steering=hash',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            ('hint', {'ovs-tx-steering': 'hash'}),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'hints': {
                    'openvswitch': {'other_config': {'tx-steering': 'hash'}}
                },
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_hints_valid_json(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--hint',
            '{"openvswitch": {"other_config": {"tx-steering": "hash"}}}',
            'test-port',
        ]
        verifylist = [
            ('network', self._port.network_id),
            ('enable', True),
            (
                'hint',
                {"openvswitch": {"other_config": {"tx-steering": "hash"}}},
            ),
            ('name', 'test-port'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_port.assert_called_once_with(
            **{
                'admin_state_up': True,
                'network_id': self._port.network_id,
                'hints': {
                    'openvswitch': {'other_config': {'tx-steering': 'hash'}}
                },
                'name': 'test-port',
            }
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def _test_create_with_hardware_offload_type(self, hwol_type=None):
        arglist = [
            '--network',
            self._port.network_id,
            'test-port',
        ]
        if hwol_type:
            arglist += ['--hardware-offload-type', hwol_type]

        hardware_offload_type = None if not hwol_type else hwol_type
        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('name', 'test-port'),
        ]
        if hwol_type:
            verifylist.append(('hardware_offload_type', hwol_type))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        create_args = {
            'admin_state_up': True,
            'network_id': self._port.network_id,
            'name': 'test-port',
        }
        if hwol_type:
            create_args['hardware_offload_type'] = hardware_offload_type
        self.network_client.create_port.assert_called_once_with(**create_args)

        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_with_hardware_offload_type_switchdev(self):
        self._test_create_with_hardware_offload_type(hwol_type='switchdev')

    def test_create_with_hardware_offload_type_null(self):
        self._test_create_with_hardware_offload_type()

    def _test_create_with_trusted_field(self, trusted):
        arglist = [
            '--network',
            self._port.network_id,
            'test-port',
        ]
        if trusted:
            arglist += ['--trusted']
        else:
            arglist += ['--not-trusted']

        verifylist = [
            (
                'network',
                self._port.network_id,
            ),
            ('name', 'test-port'),
        ]
        if trusted:
            verifylist.append(('trusted', True))
        else:
            verifylist.append(('trusted', False))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        create_args = {
            'admin_state_up': True,
            'network_id': self._port.network_id,
            'name': 'test-port',
        }
        create_args['trusted'] = trusted
        self.network_client.create_port.assert_called_once_with(**create_args)

        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_with_trusted_true(self):
        self._test_create_with_trusted_field(True)

    def test_create_with_trusted_false(self):
        self._test_create_with_trusted_field(False)


class TestDeletePort(TestPort):
    # Ports to delete.
    _ports = network_fakes.create_ports(count=2)

    def setUp(self):
        super().setUp()

        self.network_client.delete_port = mock.Mock(return_value=None)
        self.network_client.find_port = network_fakes.get_ports(
            ports=self._ports
        )
        # Get the command object to test
        self.cmd = port.DeletePort(self.app, None)

    def test_port_delete(self):
        arglist = [
            self._ports[0].name,
        ]
        verifylist = [
            ('port', [self._ports[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.find_port.assert_called_once_with(
            self._ports[0].name, ignore_missing=False
        )
        self.network_client.delete_port.assert_called_once_with(self._ports[0])
        self.assertIsNone(result)

    def test_multi_ports_delete(self):
        arglist = []
        verifylist = []

        for p in self._ports:
            arglist.append(p.name)
        verifylist = [
            ('port', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for p in self._ports:
            calls.append(call(p))
        self.network_client.delete_port.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_ports_delete_with_exception(self):
        arglist = [
            self._ports[0].name,
            'unexist_port',
        ]
        verifylist = [
            ('port', [self._ports[0].name, 'unexist_port']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._ports[0], exceptions.CommandError]
        self.network_client.find_port = mock.Mock(side_effect=find_mock_result)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 ports failed to delete.', str(e))

        self.network_client.find_port.assert_any_call(
            self._ports[0].name, ignore_missing=False
        )
        self.network_client.find_port.assert_any_call(
            'unexist_port', ignore_missing=False
        )
        self.network_client.delete_port.assert_called_once_with(self._ports[0])


class TestListPort(compute_fakes.FakeClientMixin, TestPort):
    _project = identity_fakes.FakeProject.create_one_project()
    _networks = network_fakes.create_networks(count=3)
    _sport1 = network_fakes.create_one_port(
        attrs={'project_id': _project.id, 'network_id': _networks[1]['id']}
    )
    _sport2 = network_fakes.create_one_port(
        attrs={'project_id': _project.id, 'network_id': _networks[2]['id']}
    )
    _trunk_details = {
        'trunk_id': str(uuid.uuid4()),
        'sub_ports': [
            {
                'segmentation_id': 100,
                'segmentation_type': 'vlan',
                'port_id': _sport1.id,
            },
            {
                'segmentation_id': 102,
                'segmentation_type': 'vlan',
                'port_id': _sport2.id,
            },
        ],
    }
    _pport = network_fakes.create_one_port(
        attrs={
            'project_id': _project.id,
            'network_id': _networks[0]['id'],
            'trunk_details': _trunk_details,
        }
    )
    _ports = (_pport, _sport1, _sport2)

    columns = [
        'ID',
        'Name',
        'MAC Address',
        'Fixed IP Addresses',
        'Status',
    ]

    columns_long = [
        'ID',
        'Name',
        'MAC Address',
        'Fixed IP Addresses',
        'Status',
        'Security Groups',
        'Device Owner',
        'Tags',
        'Trunk subports',
    ]

    data = []
    for prt in _ports:
        data.append(
            (
                prt.id,
                prt.name,
                prt.mac_address,
                format_columns.ListDictColumn(prt.fixed_ips),
                prt.status,
            )
        )

    data_long = []
    for prt in _ports:
        data_long.append(
            (
                prt.id,
                prt.name,
                prt.mac_address,
                format_columns.ListDictColumn(prt.fixed_ips),
                prt.status,
                format_columns.ListColumn(prt.security_group_ids),
                prt.device_owner,
                format_columns.ListColumn(prt.tags),
                port.SubPortColumn(prt.trunk_details),
            )
        )

    def setUp(self):
        super().setUp()

        self.network_client.ports = mock.Mock(return_value=self._ports)
        fake_router = network_fakes.FakeRouter.create_one_router(
            {
                'id': 'fake-router-id',
            }
        )
        fake_network = network_fakes.create_one_network(
            {
                'id': 'fake-network-id',
            }
        )
        self.network_client.find_router = mock.Mock(return_value=fake_router)
        self.network_client.find_network = mock.Mock(return_value=fake_network)

        # Get the command object to test
        self.cmd = port.ListPort(self.app, None)

    def test_port_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            fields=LIST_FIELDS_TO_RETRIEVE
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_router_opt(self):
        arglist = [
            '--router',
            'fake-router-name',
        ]

        verifylist = [('router', 'fake-router-name')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'device_id': 'fake-router-id',
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_with_server_option(self):
        fake_server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = fake_server

        arglist = [
            '--server',
            'fake-server-name',
        ]
        verifylist = [
            ('server', 'fake-server-name'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.ports.assert_called_once_with(
            device_id=fake_server.id, fields=LIST_FIELDS_TO_RETRIEVE
        )
        self.compute_client.find_server.aassert_called_once_with(
            mock.ANY, 'fake-server-name'
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_device_id_opt(self):
        arglist = [
            '--device-id',
            self._ports[0].device_id,
        ]

        verifylist = [('device_id', self._ports[0].device_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'device_id': self._ports[0].device_id,
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_device_owner_opt(self):
        arglist = [
            '--device-owner',
            self._ports[0].device_owner,
        ]

        verifylist = [('device_owner', self._ports[0].device_owner)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'device_owner': self._ports[0].device_owner,
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_all_opt(self):
        arglist = [
            '--device-owner',
            self._ports[0].device_owner,
            '--router',
            'fake-router-name',
            '--network',
            'fake-network-name',
            '--mac-address',
            self._ports[0].mac_address,
        ]

        verifylist = [
            ('device_owner', self._ports[0].device_owner),
            ('router', 'fake-router-name'),
            ('network', 'fake-network-name'),
            ('mac_address', self._ports[0].mac_address),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'device_owner': self._ports[0].device_owner,
                'device_id': 'fake-router-id',
                'network_id': 'fake-network-id',
                'mac_address': self._ports[0].mac_address,
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_mac_address_opt(self):
        arglist = [
            '--mac-address',
            self._ports[0].mac_address,
        ]

        verifylist = [('mac_address', self._ports[0].mac_address)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'mac_address': self._ports[0].mac_address,
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_fixed_ip_opt_ip_address(self):
        ip_address = self._ports[0].fixed_ips[0]['ip_address']
        arglist = [
            '--fixed-ip',
            f"ip-address={ip_address}",
        ]
        verifylist = [('fixed_ip', [{'ip-address': ip_address}])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'fixed_ips': [f'ip_address={ip_address}'],
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_fixed_ip_opt_ip_address_substr(self):
        ip_address_ss = self._ports[0].fixed_ips[0]['ip_address'][:-1]
        arglist = [
            '--fixed-ip',
            f"ip-substring={ip_address_ss}",
        ]
        verifylist = [('fixed_ip', [{'ip-substring': ip_address_ss}])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'fixed_ips': [f'ip_address_substr={ip_address_ss}'],
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_fixed_ip_opt_subnet_id(self):
        subnet_id = self._ports[0].fixed_ips[0]['subnet_id']
        arglist = [
            '--fixed-ip',
            f"subnet={subnet_id}",
        ]
        verifylist = [('fixed_ip', [{'subnet': subnet_id}])]

        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet(
            {'id': subnet_id}
        )
        self.network_client.find_subnet = mock.Mock(
            return_value=self.fake_subnet
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'fixed_ips': [f'subnet_id={subnet_id}'],
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_fixed_ip_opts(self):
        subnet_id = self._ports[0].fixed_ips[0]['subnet_id']
        ip_address = self._ports[0].fixed_ips[0]['ip_address']
        arglist = [
            '--fixed-ip',
            f"subnet={subnet_id},ip-address={ip_address}",
        ]
        verifylist = [
            ('fixed_ip', [{'subnet': subnet_id, 'ip-address': ip_address}])
        ]

        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet(
            {'id': subnet_id}
        )
        self.network_client.find_subnet = mock.Mock(
            return_value=self.fake_subnet
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'fixed_ips': [
                    f'subnet_id={subnet_id}',
                    f'ip_address={ip_address}',
                ],
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_fixed_ips(self):
        subnet_id = self._ports[0].fixed_ips[0]['subnet_id']
        ip_address = self._ports[0].fixed_ips[0]['ip_address']
        arglist = [
            '--fixed-ip',
            f"subnet={subnet_id}",
            '--fixed-ip',
            f"ip-address={ip_address}",
        ]
        verifylist = [
            ('fixed_ip', [{'subnet': subnet_id}, {'ip-address': ip_address}])
        ]

        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet(
            {
                'id': subnet_id,
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.network_client.find_subnet = mock.Mock(
            return_value=self.fake_subnet
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            **{
                'fixed_ips': [
                    f'subnet_id={subnet_id}',
                    f'ip_address={ip_address}',
                ],
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_list_port_with_long(self):
        arglist = [
            '--long',
        ]

        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ports.assert_called_once_with(
            fields=LIST_FIELDS_TO_RETRIEVE + LIST_FIELDS_TO_RETRIEVE_LONG
        )
        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, list(data))

    def test_port_list_host(self):
        arglist = [
            '--host',
            'foobar',
        ]
        verifylist = [
            ('host', 'foobar'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {
            'binding:host_id': 'foobar',
            'fields': LIST_FIELDS_TO_RETRIEVE,
        }

        self.network_client.ports.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_project(self):
        project = identity_fakes.FakeProject.create_one_project()
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
        filters = {
            'project_id': project.id,
            'fields': LIST_FIELDS_TO_RETRIEVE,
        }

        self.network_client.ports.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_project_domain(self):
        project = identity_fakes.FakeProject.create_one_project()
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
        filters = {
            'project_id': project.id,
            'fields': LIST_FIELDS_TO_RETRIEVE,
        }

        self.network_client.ports.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_name(self):
        test_name = "fakename"
        arglist = [
            '--name',
            test_name,
        ]
        verifylist = [
            ('name', test_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {
            'name': test_name,
            'fields': LIST_FIELDS_TO_RETRIEVE,
        }

        self.network_client.ports.assert_called_once_with(**filters)
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

        self.network_client.ports.assert_called_once_with(
            **{
                'tags': 'red,blue',
                'any_tags': 'red,green',
                'not_tags': 'orange,yellow',
                'not_any_tags': 'black,white',
                'fields': LIST_FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_security_group(self):
        arglist = [
            '--security-group',
            'sg-id1',
            '--security-group',
            'sg-id2',
        ]
        verifylist = [
            ('security_groups', ['sg-id1', 'sg-id2']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {
            'security_group_ids': ['sg-id1', 'sg-id2'],
            'fields': LIST_FIELDS_TO_RETRIEVE,
        }

        self.network_client.ports.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_port_list_status(self):
        arglist = [
            '--status',
            'ACTIVE',
        ]
        verifylist = [
            ('status', 'ACTIVE'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {
            'status': 'ACTIVE',
            'fields': LIST_FIELDS_TO_RETRIEVE,
        }

        self.network_client.ports.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(
            self.data,
            list(data),
        )


class TestSetPort(TestPort):
    _port = network_fakes.create_one_port({'tags': ['green', 'red']})

    def setUp(self):
        super().setUp()
        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet()
        self.network_client.find_subnet = mock.Mock(
            return_value=self.fake_subnet
        )
        self.network_client.find_port = mock.Mock(return_value=self._port)
        self.network_client.update_port = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = port.SetPort(self.app, None)

    def test_set_port_defaults(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', self._port.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertFalse(self.network_client.update_port.called)
        self.assertFalse(self.network_client.set_tags.called)
        self.assertIsNone(result)

    def test_set_port_fixed_ip(self):
        _testport = network_fakes.create_one_port(
            {'fixed_ips': [{'ip_address': '0.0.0.1'}]}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--fixed-ip',
            'ip-address=10.0.0.12',
            _testport.name,
        ]
        verifylist = [
            ('fixed_ip', [{'ip-address': '10.0.0.12'}]),
            ('port', _testport.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'fixed_ips': [
                {'ip_address': '0.0.0.1'},
                {'ip_address': '10.0.0.12'},
            ],
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_fixed_ip_clear(self):
        _testport = network_fakes.create_one_port(
            {'fixed_ips': [{'ip_address': '0.0.0.1'}]}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--fixed-ip',
            'ip-address=10.0.0.12',
            '--no-fixed-ip',
            _testport.name,
        ]
        verifylist = [
            ('fixed_ip', [{'ip-address': '10.0.0.12'}]),
            ('no_fixed_ip', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'fixed_ips': [
                {'ip_address': '10.0.0.12'},
            ],
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_dns_name(self):
        arglist = [
            '--dns-name',
            '8.8.8.8',
            self._port.name,
        ]
        verifylist = [
            ('dns_name', '8.8.8.8'),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'dns_name': '8.8.8.8',
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_overwrite_binding_profile(self):
        _testport = network_fakes.create_one_port(
            {'binding_profile': {'lok_i': 'visi_on'}}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--binding-profile',
            'lok_i=than_os',
            '--no-binding-profile',
            _testport.name,
        ]
        verifylist = [
            ('binding_profile', {'lok_i': 'than_os'}),
            ('no_binding_profile', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'binding:profile': {'lok_i': 'than_os'},
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_overwrite_mac_address(self):
        _testport = network_fakes.create_one_port(
            {'mac_address': '11:22:33:44:55:66'}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--mac-address',
            '66:55:44:33:22:11',
            _testport.name,
        ]
        verifylist = [
            ('mac_address', '66:55:44:33:22:11'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'mac_address': '66:55:44:33:22:11',
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_this(self):
        arglist = [
            '--disable',
            '--no-fixed-ip',
            '--no-binding-profile',
            self._port.name,
        ]
        verifylist = [
            ('disable', True),
            ('no_binding_profile', True),
            ('no_fixed_ip', True),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
            'binding:profile': {},
            'fixed_ips': [],
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_that(self):
        arglist = [
            '--description',
            'newDescription',
            '--enable',
            '--vnic-type',
            'macvtap',
            '--binding-profile',
            'foo=bar',
            '--host',
            'binding-host-id-xxxx',
            '--name',
            'newName',
            self._port.name,
        ]
        verifylist = [
            ('description', 'newDescription'),
            ('enable', True),
            ('vnic_type', 'macvtap'),
            ('binding_profile', {'foo': 'bar'}),
            ('host', 'binding-host-id-xxxx'),
            ('name', 'newName'),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': True,
            'binding:vnic_type': 'macvtap',
            'binding:profile': {'foo': 'bar'},
            'binding:host_id': 'binding-host-id-xxxx',
            'description': 'newDescription',
            'name': 'newName',
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_invalid_json_binding_profile(self):
        arglist = [
            '--binding-profile',
            '{"parent_name"}',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_set_port_invalid_key_value_binding_profile(self):
        arglist = [
            '--binding-profile',
            'key',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_set_port_mixed_binding_profile(self):
        arglist = [
            '--binding-profile',
            'foo=bar',
            '--binding-profile',
            '{"foo2": "bar2"}',
            self._port.name,
        ]
        verifylist = [
            ('binding_profile', {'foo': 'bar', 'foo2': 'bar2'}),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'binding:profile': {'foo': 'bar', 'foo2': 'bar2'},
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_security_group(self):
        sg = network_fakes.FakeSecurityGroup.create_one_security_group()
        self.network_client.find_security_group = mock.Mock(return_value=sg)
        arglist = [
            '--security-group',
            sg.id,
            self._port.name,
        ]
        verifylist = [
            ('security_groups', [sg.id]),
            ('port', self._port.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'security_group_ids': [sg.id],
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_security_group_append(self):
        sg_1 = network_fakes.FakeSecurityGroup.create_one_security_group()
        sg_2 = network_fakes.FakeSecurityGroup.create_one_security_group()
        sg_3 = network_fakes.FakeSecurityGroup.create_one_security_group()
        self.network_client.find_security_group = mock.Mock(
            side_effect=[sg_2, sg_3]
        )
        _testport = network_fakes.create_one_port(
            {'security_group_ids': [sg_1.id]}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--security-group',
            sg_2.id,
            '--security-group',
            sg_3.id,
            _testport.name,
        ]
        verifylist = [
            ('security_groups', [sg_2.id, sg_3.id]),
            ('port', _testport.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'security_group_ids': [sg_1.id, sg_2.id, sg_3.id],
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_security_group_clear(self):
        arglist = [
            '--no-security-group',
            self._port.name,
        ]
        verifylist = [
            ('no_security_group', True),
            ('port', self._port.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'security_group_ids': [],
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_security_group_replace(self):
        sg1 = network_fakes.FakeSecurityGroup.create_one_security_group()
        sg2 = network_fakes.FakeSecurityGroup.create_one_security_group()
        _testport = network_fakes.create_one_port(
            {'security_group_ids': [sg1.id]}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        self.network_client.find_security_group = mock.Mock(return_value=sg2)
        arglist = [
            '--security-group',
            sg2.id,
            '--no-security-group',
            _testport.name,
        ]
        verifylist = [
            ('security_groups', [sg2.id]),
            ('no_security_group', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        attrs = {
            'security_group_ids': [sg2.id],
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_allowed_address_pair(self):
        arglist = [
            '--allowed-address',
            'ip-address=192.168.1.123',
            self._port.name,
        ]
        verifylist = [
            ('allowed_address_pairs', [{'ip-address': '192.168.1.123'}]),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'allowed_address_pairs': [{'ip_address': '192.168.1.123'}],
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_append_allowed_address_pair(self):
        _testport = network_fakes.create_one_port(
            {'allowed_address_pairs': [{'ip_address': '192.168.1.123'}]}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--allowed-address',
            'ip-address=192.168.1.45',
            _testport.name,
        ]
        verifylist = [
            ('allowed_address_pairs', [{'ip-address': '192.168.1.45'}]),
            ('port', _testport.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'allowed_address_pairs': [
                {'ip_address': '192.168.1.123'},
                {'ip_address': '192.168.1.45'},
            ],
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_overwrite_allowed_address_pair(self):
        _testport = network_fakes.create_one_port(
            {'allowed_address_pairs': [{'ip_address': '192.168.1.123'}]}
        )
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--allowed-address',
            'ip-address=192.168.1.45',
            '--no-allowed-address',
            _testport.name,
        ]
        verifylist = [
            ('allowed_address_pairs', [{'ip-address': '192.168.1.45'}]),
            ('no_allowed_address_pair', True),
            ('port', _testport.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'allowed_address_pairs': [{'ip_address': '192.168.1.45'}],
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_no_allowed_address_pairs(self):
        arglist = [
            '--no-allowed-address',
            self._port.name,
        ]
        verifylist = [
            ('no_allowed_address_pair', True),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'allowed_address_pairs': [],
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_extra_dhcp_option(self):
        arglist = [
            '--extra-dhcp-option',
            'name=foo,value=bar',
            self._port.name,
        ]
        verifylist = [
            ('extra_dhcp_options', [{'name': 'foo', 'value': 'bar'}]),
            ('port', self._port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'extra_dhcp_opts': [{'opt_name': 'foo', 'opt_value': 'bar'}],
        }
        self.network_client.update_port.assert_called_once_with(
            self._port, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_security_enabled(self):
        arglist = [
            '--enable-port-security',
            self._port.id,
        ]
        verifylist = [
            ('enable_port_security', True),
            (
                'port',
                self._port.id,
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.network_client.update_port.assert_called_once_with(
            self._port,
            **{
                'port_security_enabled': True,
            },
        )

    def test_set_port_security_disabled(self):
        arglist = [
            '--disable-port-security',
            self._port.id,
        ]
        verifylist = [
            ('disable_port_security', True),
            (
                'port',
                self._port.id,
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.network_client.update_port.assert_called_once_with(
            self._port,
            **{
                'port_security_enabled': False,
            },
        )

    def test_set_port_with_qos(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        _testport = network_fakes.create_one_port({'qos_policy_id': None})
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--qos-policy',
            qos_policy.id,
            _testport.name,
        ]
        verifylist = [
            ('qos_policy', qos_policy.id),
            ('port', _testport.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'qos_policy_id': qos_policy.id,
        }
        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_data_plane_status(self):
        _testport = network_fakes.create_one_port({'data_plane_status': None})
        self.network_client.find_port = mock.Mock(return_value=_testport)
        arglist = [
            '--data-plane-status',
            'ACTIVE',
            _testport.name,
        ]
        verifylist = [
            ('data_plane_status', 'ACTIVE'),
            ('port', _testport.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'data_plane_status': 'ACTIVE',
        }

        self.network_client.update_port.assert_called_once_with(
            _testport, **attrs
        )
        self.assertIsNone(result)

    def test_set_port_invalid_data_plane_status_value(self):
        arglist = [
            '--data-plane-status',
            'Spider-Man',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def _test_set_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['red', 'blue', 'green']
        else:
            arglist = ['--no-tag']
            verifylist = [('no_tag', True)]
            expected_args = []
        arglist.append(self._port.name)
        verifylist.append(('port', self._port.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_port.called)
        self.network_client.set_tags.assert_called_once_with(
            self._port, test_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_set_with_tags(self):
        self._test_set_tags(with_tags=True)

    def test_set_with_no_tag(self):
        self._test_set_tags(with_tags=False)

    def _test_create_with_numa_affinity_policy(self, policy):
        arglist = [
            f'--numa-policy-{policy}',
            self._port.id,
        ]
        verifylist = [
            (f'numa_policy_{policy}', True),
            (
                'port',
                self._port.id,
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.network_client.update_port.assert_called_once_with(
            self._port, **{'numa_affinity_policy': policy}
        )

    def test_create_with_numa_affinity_policy_required(self):
        self._test_create_with_numa_affinity_policy('required')

    def test_create_with_numa_affinity_policy_preferred(self):
        self._test_create_with_numa_affinity_policy('preferred')

    def test_create_with_numa_affinity_policy_legacy(self):
        self._test_create_with_numa_affinity_policy('legacy')

    def test_set_hints_invalid_json(self):
        arglist = [
            '--network',
            self._port.network_id,
            '--hint',
            'invalid json',
            'test-port',
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )

    def test_set_hints_invalid_alias(self):
        arglist = [
            '--hint',
            'invalid-alias=value',
            'test-port',
        ]
        verifylist = [
            ('hint', {'invalid-alias': 'value'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_set_hints_invalid_value(self):
        arglist = [
            '--hint',
            'ovs-tx-steering=invalid-value',
            'test-port',
        ]
        verifylist = [
            ('hint', {'ovs-tx-steering': 'invalid-value'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_set_hints_valid_alias_value(self):
        testport = network_fakes.create_one_port()
        self.network_client.find_port = mock.Mock(return_value=testport)
        self.network_client.find_extension = mock.Mock(
            return_value=['port-hints', 'port-hint-ovs-tx-steering']
        )
        arglist = [
            '--hint',
            'ovs-tx-steering=hash',
            testport.name,
        ]
        verifylist = [
            ('hint', {'ovs-tx-steering': 'hash'}),
            ('port', testport.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_port.assert_called_once_with(
            testport,
            **{
                'hints': {
                    'openvswitch': {'other_config': {'tx-steering': 'hash'}}
                }
            },
        )
        self.assertIsNone(result)

    def test_set_hints_valid_json(self):
        testport = network_fakes.create_one_port()
        self.network_client.find_port = mock.Mock(return_value=testport)
        self.network_client.find_extension = mock.Mock(
            return_value=['port-hints', 'port-hint-ovs-tx-steering']
        )
        arglist = [
            '--hint',
            '{"openvswitch": {"other_config": {"tx-steering": "hash"}}}',
            testport.name,
        ]
        verifylist = [
            (
                'hint',
                {"openvswitch": {"other_config": {"tx-steering": "hash"}}},
            ),
            ('port', testport.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_port.assert_called_once_with(
            testport,
            **{
                'hints': {
                    'openvswitch': {'other_config': {'tx-steering': 'hash'}}
                }
            },
        )
        self.assertIsNone(result)

    def _test_set_trusted_field(self, trusted):
        arglist = [self._port.id]
        if trusted:
            arglist += ['--trusted']
        else:
            arglist += ['--not-trusted']

        verifylist = [
            ('port', self._port.id),
        ]
        if trusted:
            verifylist.append(('trusted', True))
        else:
            verifylist.append(('trusted', False))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_port.assert_called_once_with(
            self._port, **{'trusted': trusted}
        )
        self.assertIsNone(result)

    def test_set_trusted_true(self):
        self._test_set_trusted_field(True)

    def test_set_trusted_false(self):
        self._test_set_trusted_field(False)

    def _test_set_uplink_status_propagation(self, uspropagation):
        arglist = [self._port.id]
        if uspropagation:
            arglist += ['--enable-uplink-status-propagation']
        else:
            arglist += ['--disable-uplink-status-propagation']

        verifylist = [
            ('port', self._port.id),
        ]
        if uspropagation:
            verifylist.append(('enable_uplink_status_propagation', True))
        else:
            verifylist.append(('enable_uplink_status_propagation', False))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.update_port.assert_called_once_with(
            self._port, **{'propagate_uplink_status': uspropagation}
        )
        self.assertIsNone(result)

    def test_set_uplink_status_propagation_true(self):
        self._test_set_uplink_status_propagation(True)

    def test_set_uplink_status_propagation_false(self):
        self._test_set_uplink_status_propagation(False)


class TestShowPort(TestPort):
    # The port to show.
    _port = network_fakes.create_one_port()
    columns, data = TestPort._get_common_cols_data(_port)

    def setUp(self):
        super().setUp()

        self.network_client.find_port = mock.Mock(return_value=self._port)

        # Get the command object to test
        self.cmd = port.ShowPort(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_all_options(self):
        arglist = [
            self._port.name,
        ]
        verifylist = [
            ('port', self._port.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_port.assert_called_once_with(
            self._port.name, ignore_missing=False
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestUnsetPort(TestPort):
    def setUp(self):
        super().setUp()
        self._testport = network_fakes.create_one_port(
            {
                'fixed_ips': [
                    {
                        'subnet_id': '042eb10a-3a18-4658-ab-cf47c8d03152',
                        'ip_address': '0.0.0.1',
                    },
                    {
                        'subnet_id': '042eb10a-3a18-4658-ab-cf47c8d03152',
                        'ip_address': '1.0.0.0',
                    },
                ],
                'binding:profile': {
                    'batman': 'Joker',
                    'Superman': 'LexLuthor',
                },
                'tags': ['green', 'red'],
            }
        )
        self.fake_subnet = network_fakes.FakeSubnet.create_one_subnet(
            {'id': '042eb10a-3a18-4658-ab-cf47c8d03152'}
        )
        self.network_client.find_subnet = mock.Mock(
            return_value=self.fake_subnet
        )
        self.network_client.find_port = mock.Mock(return_value=self._testport)
        self.network_client.update_port = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)
        # Get the command object to test
        self.cmd = port.UnsetPort(self.app, None)

    def test_unset_port_parameters(self):
        arglist = [
            '--fixed-ip',
            'subnet=042eb10a-3a18-4658-ab-cf47c8d03152,ip-address=1.0.0.0',
            '--binding-profile',
            'Superman',
            '--qos-policy',
            '--host',
            self._testport.name,
        ]
        verifylist = [
            (
                'fixed_ip',
                [
                    {
                        'subnet': '042eb10a-3a18-4658-ab-cf47c8d03152',
                        'ip-address': '1.0.0.0',
                    }
                ],
            ),
            ('binding_profile', ['Superman']),
            ('qos_policy', True),
            ('host', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'fixed_ips': [
                {
                    'subnet_id': '042eb10a-3a18-4658-ab-cf47c8d03152',
                    'ip_address': '0.0.0.1',
                }
            ],
            'binding:profile': {'batman': 'Joker'},
            'qos_policy_id': None,
            'binding:host_id': None,
        }
        self.network_client.update_port.assert_called_once_with(
            self._testport, **attrs
        )
        self.assertIsNone(result)

    def test_unset_port_fixed_ip_not_existent(self):
        arglist = [
            '--fixed-ip',
            'ip-address=1.0.0.1',
            '--binding-profile',
            'Superman',
            self._testport.name,
        ]
        verifylist = [
            ('fixed_ip', [{'ip-address': '1.0.0.1'}]),
            ('binding_profile', ['Superman']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_port_binding_profile_not_existent(self):
        arglist = [
            '--fixed-ip',
            'ip-address=1.0.0.0',
            '--binding-profile',
            'Neo',
            self._testport.name,
        ]
        verifylist = [
            ('fixed_ip', [{'ip-address': '1.0.0.0'}]),
            ('binding_profile', ['Neo']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_security_group(self):
        _fake_sg1 = network_fakes.FakeSecurityGroup.create_one_security_group()
        _fake_sg2 = network_fakes.FakeSecurityGroup.create_one_security_group()
        _fake_port = network_fakes.create_one_port(
            {'security_group_ids': [_fake_sg1.id, _fake_sg2.id]}
        )
        self.network_client.find_port = mock.Mock(return_value=_fake_port)
        self.network_client.find_security_group = mock.Mock(
            return_value=_fake_sg2
        )
        arglist = [
            '--security-group',
            _fake_sg2.id,
            _fake_port.name,
        ]
        verifylist = [
            ('security_groups', [_fake_sg2.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'security_group_ids': [_fake_sg1.id]}
        self.network_client.update_port.assert_called_once_with(
            _fake_port, **attrs
        )
        self.assertIsNone(result)

    def test_unset_port_security_group_not_existent(self):
        _fake_sg1 = network_fakes.FakeSecurityGroup.create_one_security_group()
        _fake_sg2 = network_fakes.FakeSecurityGroup.create_one_security_group()
        _fake_port = network_fakes.create_one_port(
            {'security_group_ids': [_fake_sg1.id]}
        )
        self.network_client.find_security_group = mock.Mock(
            return_value=_fake_sg2
        )
        arglist = [
            '--security-group',
            _fake_sg2.id,
            _fake_port.name,
        ]
        verifylist = [
            ('security_groups', [_fake_sg2.id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_port_allowed_address_pair(self):
        _fake_port = network_fakes.create_one_port(
            {'allowed_address_pairs': [{'ip_address': '192.168.1.123'}]}
        )
        self.network_client.find_port = mock.Mock(return_value=_fake_port)
        arglist = [
            '--allowed-address',
            'ip-address=192.168.1.123',
            _fake_port.name,
        ]
        verifylist = [
            ('allowed_address_pairs', [{'ip-address': '192.168.1.123'}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'allowed_address_pairs': [],
        }

        self.network_client.update_port.assert_called_once_with(
            _fake_port, **attrs
        )
        self.assertIsNone(result)

    def test_unset_port_allowed_address_pair_not_existent(self):
        _fake_port = network_fakes.create_one_port(
            {'allowed_address_pairs': [{'ip_address': '192.168.1.123'}]}
        )
        self.network_client.find_port = mock.Mock(return_value=_fake_port)
        arglist = [
            '--allowed-address',
            'ip-address=192.168.1.45',
            _fake_port.name,
        ]
        verifylist = [
            ('allowed_address_pairs', [{'ip-address': '192.168.1.45'}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_unset_port_data_plane_status(self):
        _fake_port = network_fakes.create_one_port(
            {'data_plane_status': 'ACTIVE'}
        )
        self.network_client.find_port = mock.Mock(return_value=_fake_port)
        arglist = [
            '--data-plane-status',
            _fake_port.name,
        ]
        verifylist = [
            ('data_plane_status', True),
            ('port', _fake_port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'data_plane_status': None,
        }

        self.network_client.update_port.assert_called_once_with(
            _fake_port, **attrs
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
        arglist.append(self._testport.name)
        verifylist.append(('port', self._testport.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_port.called)
        self.network_client.set_tags.assert_called_once_with(
            self._testport, test_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_unset_with_tags(self):
        self._test_unset_tags(with_tags=True)

    def test_unset_with_all_tag(self):
        self._test_unset_tags(with_tags=False)

    def test_unset_numa_affinity_policy(self):
        _fake_port = network_fakes.create_one_port(
            {'numa_affinity_policy': 'required'}
        )
        self.network_client.find_port = mock.Mock(return_value=_fake_port)
        arglist = [
            '--numa-policy',
            _fake_port.name,
        ]
        verifylist = [
            ('numa_policy', True),
            ('port', _fake_port.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'numa_affinity_policy': None,
        }

        self.network_client.update_port.assert_called_once_with(
            _fake_port, **attrs
        )
        self.assertIsNone(result)

    def test_unset_hints(self):
        testport = network_fakes.create_one_port()
        self.network_client.find_port = mock.Mock(return_value=testport)
        arglist = [
            '--hints',
            testport.name,
        ]
        verifylist = [
            ('hints', True),
            ('port', testport.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_port.assert_called_once_with(
            testport,
            **{'hints': None},
        )
        self.assertIsNone(result)
