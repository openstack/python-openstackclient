# Copyright 2017 FUJITSU LIMITED
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

from unittest import mock

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstack.identity.v3 import project as _project
from openstack.network.v2 import vpn_endpoint_group as _vpn_endpoint_group
from openstack.network.v2 import vpn_ike_policy as _vpn_ike_policy
from openstack.network.v2 import vpn_ipsec_policy as sdk_vpn_ipsecp_p
from openstack.network.v2 import vpn_ipsec_site_connection as sdk_vpn_ipsec_sc
from openstack.network.v2 import vpn_service as sdk_vpn_service
from openstack.test import fakes as sdk_fakes

from openstackclient.network.v2.vpnaas import ipsec_site_connection
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes
from openstackclient.tests.unit import utils as tests_utils


class TestIPsecSiteConn(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self._ipsec_site_conn = fakes.IPsecSiteConnection().create_conn()

        def _mock_ipsec_site_conn(*args, **kwargs):
            return {'id': args[0]}

        self.network_client.find_vpn_ipsec_site_connection.side_effect = (
            mock.Mock(side_effect=_mock_ipsec_site_conn)
        )
        self.headers = (
            'ID',
            'Name',
            'Peer Address',
            'Authentication Algorithm',
            'Status',
            'Project',
            'Peer CIDRs',
            'VPN Service',
            'IPSec Policy',
            'IKE Policy',
            'MTU',
            'Initiator',
            'State',
            'Description',
            'Pre-shared Key',
            'Route Mode',
            'Local ID',
            'Peer ID',
            'Local Endpoint Group ID',
            'Peer Endpoint Group ID',
            'DPD',
        )
        self.ordered_headers = (
            'Authentication Algorithm',
            'DPD',
            'Description',
            'ID',
            'IKE Policy',
            'IPSec Policy',
            'Initiator',
            'Local Endpoint Group ID',
            'Local ID',
            'MTU',
            'Name',
            'Peer Address',
            'Peer CIDRs',
            'Peer Endpoint Group ID',
            'Peer ID',
            'Pre-shared Key',
            'Project',
            'Route Mode',
            'State',
            'Status',
            'VPN Service',
        )
        self.ordered_data = (
            self._ipsec_site_conn['auth_mode'],
            self._ipsec_site_conn['dpd'],
            self._ipsec_site_conn['description'],
            self._ipsec_site_conn['id'],
            self._ipsec_site_conn['ikepolicy_id'],
            self._ipsec_site_conn['ipsecpolicy_id'],
            self._ipsec_site_conn['initiator'],
            self._ipsec_site_conn['local_ep_group_id'],
            self._ipsec_site_conn['local_id'],
            self._ipsec_site_conn['mtu'],
            self._ipsec_site_conn['name'],
            self._ipsec_site_conn['peer_address'],
            format_columns.ListColumn(self._ipsec_site_conn['peer_cidrs']),
            self._ipsec_site_conn['peer_ep_group_id'],
            self._ipsec_site_conn['peer_id'],
            self._ipsec_site_conn['psk'],
            self._ipsec_site_conn['project_id'],
            self._ipsec_site_conn['route_mode'],
            self._ipsec_site_conn['admin_state_up'],
            self._ipsec_site_conn['status'],
            self._ipsec_site_conn['vpnservice_id'],
        )


class TestCreateIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.network_client.create_vpn_ipsec_site_connection.return_value = (
            self._ipsec_site_conn
        )
        self.mocked = self.network_client.create_vpn_ipsec_site_connection
        self.cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            self.app, None
        )

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_all_params(self):
        arglist = [
            '--project',
            self.project.id,
            '--peer-address',
            '192.168.2.10',
            '--peer-id',
            '192.168.2.10',
            '--psk',
            'abcd',
            '--initiator',
            'bi-directional',
            '--vpnservice',
            'vpnservice_id',
            '--ikepolicy',
            'ikepolicy_id',
            '--ipsecpolicy',
            'ipsecpolicy_id',
            '--mtu',
            '1500',
            '--description',
            'my-vpn-connection',
            '--local-endpoint-group',
            'local-epg',
            '--peer-endpoint-group',
            'peer-epg',
            self._ipsec_site_conn.name,
        ]
        verifylist = [
            ('project', self.project.id),
            ('peer_address', '192.168.2.10'),
            ('peer_id', '192.168.2.10'),
            ('psk', 'abcd'),
            ('initiator', 'bi-directional'),
            ('vpnservice', 'vpnservice_id'),
            ('ikepolicy', 'ikepolicy_id'),
            ('ipsecpolicy', 'ipsecpolicy_id'),
            ('mtu', '1500'),
            ('description', 'my-vpn-connection'),
            ('local_endpoint_group', 'local-epg'),
            ('peer_endpoint_group', 'peer-epg'),
            ('name', self._ipsec_site_conn.name),
        ]

        def _mock_endpoint_group(*args, **kwargs):
            return _vpn_endpoint_group.VpnEndpointGroup(**{'id': args[0]})

        def _mock_vpn_service(*args, **kwargs):
            return sdk_vpn_service.VpnService(**{'id': args[0]})

        def _mock_vpn_ike_policy(*args, **kwargs):
            return _vpn_ike_policy.VpnIkePolicy(**{'id': args[0]})

        def _mock_vpn_ipsec_policy(*args, **kwargs):
            return sdk_vpn_ipsecp_p.VpnIpsecPolicy(**{'id': args[0]})

        self.network_client.find_vpn_endpoint_group.side_effect = mock.Mock(
            side_effect=_mock_endpoint_group
        )
        self.network_client.find_vpn_service.side_effect = mock.Mock(
            side_effect=_mock_vpn_service
        )
        self.network_client.find_vpn_ike_policy.side_effect = mock.Mock(
            side_effect=_mock_vpn_ike_policy
        )
        self.network_client.find_vpn_ipsec_policy.side_effect = mock.Mock(
            side_effect=_mock_vpn_ipsec_policy
        )
        self.network_client.create_vpn_ipsec_site_connection.return_value = (
            self._ipsec_site_conn
        )
        self.ordered_data = (
            self._ipsec_site_conn['auth_mode'],
            self._ipsec_site_conn['dpd'],
            self._ipsec_site_conn['description'],
            self._ipsec_site_conn['id'],
            self._ipsec_site_conn['ikepolicy_id'],
            self._ipsec_site_conn['ipsecpolicy_id'],
            self._ipsec_site_conn['initiator'],
            self._ipsec_site_conn['local_ep_group_id'],
            self._ipsec_site_conn['local_id'],
            self._ipsec_site_conn['mtu'],
            self._ipsec_site_conn['name'],
            self._ipsec_site_conn['peer_address'],
            format_columns.ListColumn(self._ipsec_site_conn['peer_cidrs']),
            self._ipsec_site_conn['peer_ep_group_id'],
            self._ipsec_site_conn['peer_id'],
            self._ipsec_site_conn['psk'],
            self._ipsec_site_conn['project_id'],
            self._ipsec_site_conn['route_mode'],
            self._ipsec_site_conn['admin_state_up'],
            self._ipsec_site_conn['status'],
            self._ipsec_site_conn['vpnservice_id'],
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            project_id=self.project.id,
            peer_address='192.168.2.10',
            peer_id='192.168.2.10',
            psk='abcd',
            initiator='bi-directional',
            vpnservice_id='vpnservice_id',
            ikepolicy_id='ikepolicy_id',
            ipsecpolicy_id='ipsecpolicy_id',
            mtu='1500',
            description='my-vpn-connection',
            local_ep_group_id='local-epg',
            peer_ep_group_id='peer-epg',
            name=self._ipsec_site_conn.name,
        )
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertCountEqual(self.ordered_data, data)


class TestDeleteIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()
        self.cmd = ipsec_site_connection.DeleteIPsecSiteConnection(
            self.app, None
        )

    def test_delete_with_one_resource(self):
        def _mock_ips_sc(*args, **kwargs):
            return sdk_vpn_ipsec_sc.VpnIPSecSiteConnection(**{'id': args[0]})

        self.network_client.find_vpn_endpoint_group.side_effect = _mock_ips_sc

        arglist = [self._ipsec_site_conn['id']]
        verifylist = [('ipsec_site_connection', [self._ipsec_site_conn['id']])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_vpn_ipsec_site_connection.assert_called_once_with(
            self._ipsec_site_conn['id']
        )
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_ips_c(*args, **kwargs):
            return sdk_vpn_ipsec_sc.VpnIPSecSiteConnection(**{'id': args[0]})

        self.network_client.find_vpn_ipsec_policy.side_effect = _mock_ips_c

        arglist = ['target1', 'target2']
        verifylist = [('ipsec_site_connection', ['target1', 'target2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(
            2,
            self.network_client.delete_vpn_ipsec_site_connection.call_count,
        )
        for idx, reference in enumerate(['target1', 'target2']):
            actual = ''.join(
                self.network_client.delete_vpn_ipsec_site_connection.call_args_list[
                    idx
                ][0]
            )
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        arglist = ['target']
        verifylist = [('ipsec_site_connection', ['target'])]

        self.network_client.find_vpn_ipsec_site_connection.side_effect = [
            'target',
            exceptions.CommandError,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestListIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()
        self.cmd = ipsec_site_connection.ListIPsecSiteConnection(
            self.app, None
        )

        self.short_header = (
            'ID',
            'Name',
            'Peer Address',
            'Authentication Algorithm',
            'Status',
        )

        self.short_data = (
            self._ipsec_site_conn['id'],
            self._ipsec_site_conn['name'],
            self._ipsec_site_conn['peer_address'],
            self._ipsec_site_conn['auth_mode'],
            self._ipsec_site_conn['status'],
        )

        self.network_client.vpn_ipsec_site_connections.return_value = [
            self._ipsec_site_conn
        ]

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_ipsec_site_connections.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_ipsec_site_connections.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()

        self.network_client.update_vpn_ipsec_site_connection.return_value = (
            self._ipsec_site_conn
        )

        self.cmd = ipsec_site_connection.SetIPsecSiteConnection(self.app, None)

    def test_set_ipsec_site_conn_with_peer_id(self):
        arglist = [
            self._ipsec_site_conn['id'],
            '--peer-id',
            '192.168.3.10',
        ]
        verifylist = [
            ('ipsec_site_connection', self._ipsec_site_conn['id']),
            ('peer_id', '192.168.3.10'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ipsec_site_connection.assert_called_once_with(
            self._ipsec_site_conn['id'], peer_id='192.168.3.10'
        )
        self.assertIsNone(result)

    def test_set_name(self):
        arglist = [
            self._ipsec_site_conn['id'],
            '--name',
            'change',
        ]
        verifylist = [
            ('ipsec_site_connection', self._ipsec_site_conn['id']),
            ('name', 'change'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ipsec_site_connection.assert_called_once_with(
            self._ipsec_site_conn['id'], name='change'
        )
        self.assertIsNone(result)

    def test_set_description(self):
        arglist = [
            self._ipsec_site_conn['id'],
            '--description',
            'change-desc',
        ]
        verifylist = [
            ('ipsec_site_connection', self._ipsec_site_conn['id']),
            ('description', 'change-desc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ipsec_site_connection.assert_called_once_with(
            self._ipsec_site_conn['id'], description='change-desc'
        )
        self.assertIsNone(result)


class TestShowIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()

        self.network_client.find_vpn_ipsec_site_connection.side_effect = None
        self.network_client.find_vpn_ipsec_site_connection.return_value = (
            self._ipsec_site_conn
        )

        self.cmd = ipsec_site_connection.ShowIPsecSiteConnection(
            self.app, None
        )

    def test_show_filtered_by_id_or_name(self):
        arglist = [
            self._ipsec_site_conn['id'],
        ]
        verifylist = [
            ('ipsec_site_connection', self._ipsec_site_conn['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_ipsec_site_connection.assert_called_once_with(
            self._ipsec_site_conn['id'], ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
