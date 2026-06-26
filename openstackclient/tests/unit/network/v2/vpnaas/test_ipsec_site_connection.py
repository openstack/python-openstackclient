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
#

from unittest import mock

from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstack.network.v2 import vpn_endpoint_group as sdk_vpn_epg
from openstack.network.v2 import vpn_ike_policy as sdk_vpn_ike_p
from openstack.network.v2 import vpn_ipsec_policy as sdk_vpn_ipsecp_p
from openstack.network.v2 import vpn_ipsec_site_connection as sdk_vpn_ipsec_sc
from openstack.network.v2 import vpn_service as sdk_vpn_service

from openstackclient.identity import common as identity_common
from openstackclient.network.v2.vpnaas import ipsec_site_connection
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes
from openstackclient.tests.unit import utils as tests_utils


class TestIPsecSiteConn(test_fakes.TestNetworkV2):
    def _generate_data(self, ordered_dict=None, data=None):
        source = ordered_dict if ordered_dict else self._ipsec_site_conn
        if data:
            source.update(data)
        return source

    def _generate_req_and_res(self, verifylist):
        request = dict(verifylist)
        response = self._ipsec_site_conn
        for key, val in verifylist:
            converted = self.CONVERT_MAP.get(key, key)
            del request[key]
            new_value = val
            request[converted] = new_value
            response[converted] = new_value
        return request, response

    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: list(exp_req)}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertCountEqual(self.ordered_data, data)

    def setUp(self):
        super().setUp()

        self._ipsec_site_conn = fakes.IPsecSiteConnection().create_conn()
        self.CONVERT_MAP = {
            'project': 'project_id',
            'ikepolicy': 'ikepolicy_id',
            'ipsecpolicy': 'ipsecpolicy_id',
            'vpnservice': 'vpnservice_id',
            'peer_endpoint_group': 'peer_ep_group_id',
            'local_endpoint_group': 'local_ep_group_id',
        }

        def _mock_ipsec_site_conn(*args, **kwargs):
            return {'id': args[0]}

        self.network_client.find_vpn_ipsec_site_connection.side_effect = (
            mock.Mock(side_effect=_mock_ipsec_site_conn)
        )
        identity_common.find_project = mock.Mock()
        identity_common.find_project.id = self._ipsec_site_conn['project_id']
        self.res = 'ipsec_site_connection'
        self.res_plural = 'ipsec_site_connections'
        self.resource = self._ipsec_site_conn
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
        self.data = self._generate_data()
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
        self.network_client.create_vpn_ipsec_site_connection.return_value = (
            self._ipsec_site_conn
        )
        self.mocked = self.network_client.create_vpn_ipsec_site_connection
        self.cmd = ipsec_site_connection.CreateIPsecSiteConnection(
            self.app, None
        )

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_vpn_ipsec_site_connection.return_value = (
            response
        )
        identity_common.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = self._generate_data(ordered_dict=response)
        self.ordered_data = (
            response['auth_mode'],
            response['dpd'],
            response['description'],
            response['id'],
            response['ikepolicy_id'],
            response['ipsecpolicy_id'],
            response['initiator'],
            response['local_ep_group_id'],
            response['local_id'],
            response['mtu'],
            response['name'],
            response['peer_address'],
            format_columns.ListColumn(response['peer_cidrs']),
            response['peer_ep_group_id'],
            response['peer_id'],
            response['psk'],
            response['project_id'],
            response['route_mode'],
            response['admin_state_up'],
            response['status'],
            response['vpnservice_id'],
        )

    def _set_all_params(self, args={}):
        project_id = args.get('project_id') or 'my-tenant'
        name = args.get('name') or 'connection1'
        peer_address = args.get('peer_address') or '192.168.2.10'
        peer_id = args.get('peer_id') or '192.168.2.10'
        psk = args.get('psk') or 'abcd'
        mtu = args.get('mtu') or '1500'
        initiator = args.get('initiator') or 'bi-directional'
        vpnservice_id = args.get('vpnservice') or 'vpnservice_id'
        ikepolicy_id = args.get('ikepolicy') or 'ikepolicy_id'
        ipsecpolicy_id = args.get('ipsecpolicy') or 'ipsecpolicy_id'
        local_ep_group = args.get('local_ep_group_id') or 'local-epg'
        peer_ep_group = args.get('peer_ep_group_id') or 'peer-epg'
        description = args.get('description') or 'my-vpn-connection'

        arglist = [
            '--project',
            project_id,
            '--peer-address',
            peer_address,
            '--peer-id',
            peer_id,
            '--psk',
            psk,
            '--initiator',
            initiator,
            '--vpnservice',
            vpnservice_id,
            '--ikepolicy',
            ikepolicy_id,
            '--ipsecpolicy',
            ipsecpolicy_id,
            '--mtu',
            mtu,
            '--description',
            description,
            '--local-endpoint-group',
            local_ep_group,
            '--peer-endpoint-group',
            peer_ep_group,
            name,
        ]
        verifylist = [
            ('project', project_id),
            ('peer_address', peer_address),
            ('peer_id', peer_id),
            ('psk', psk),
            ('initiator', initiator),
            ('vpnservice', vpnservice_id),
            ('ikepolicy', ikepolicy_id),
            ('ipsecpolicy', ipsecpolicy_id),
            ('mtu', mtu),
            ('description', description),
            ('local_endpoint_group', local_ep_group),
            ('peer_endpoint_group', peer_ep_group),
            ('name', name),
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self, args={}):
        arglist, verifylist = self._set_all_params(args)
        request, response = self._generate_req_and_res(verifylist)

        def _mock_endpoint_group(*args, **kwargs):
            return sdk_vpn_epg.VpnEndpointGroup(**{'id': args[0]})

        def _mock_vpn_service(*args, **kwargs):
            return sdk_vpn_service.VpnService(**{'id': args[0]})

        def _mock_vpn_ike_policy(*args, **kwargs):
            return sdk_vpn_ike_p.VpnIkePolicy(**{'id': args[0]})

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
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

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
        self._test_create_with_all_params()


class TestDeleteIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.delete_vpn_ipsec_site_connection
        self.cmd = ipsec_site_connection.DeleteIPsecSiteConnection(
            self.app, None
        )

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_ips_sc(*args, **kwargs):
            return sdk_vpn_ipsec_sc.VpnIPSecSiteConnection(**{'id': args[0]})

        self.network_client.find_vpn_endpoint_group.side_effect = _mock_ips_sc

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_ips_c(*args, **kwargs):
            return sdk_vpn_ipsec_sc.VpnIPSecSiteConnection(**{'id': args[0]})

        self.network_client.find_vpn_ipsec_policy.side_effect = _mock_ips_c

        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0])
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        target1 = 'target'
        arglist = [target1]
        verifylist = [(self.res, [target1])]

        self.network_client.find_vpn_ipsec_site_connection.side_effect = [
            target1,
            exceptions.CommandError,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.res.replace('_', ' ')
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
        self.mocked = self.network_client.vpn_ipsec_site_connections

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetIPsecSiteConn(TestIPsecSiteConn):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_ipsec_site_connection.return_value = (
            self._ipsec_site_conn
        )
        self.mocked = self.network_client.update_vpn_ipsec_site_connection
        self.cmd = ipsec_site_connection.SetIPsecSiteConnection(self.app, None)

    def test_set_ipsec_site_conn_with_peer_id(self):
        target = self.resource['id']
        peer_id = '192.168.3.10'
        arglist = [target, '--peer-id', peer_id]
        verifylist = [
            (self.res, target),
            ('peer_id', peer_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'peer_id': peer_id})
        self.assertIsNone(result)

    def test_set_name(self):
        target = self.resource['id']
        update = 'change'
        arglist = [target, '--name', update]
        verifylist = [
            (self.res, target),
            ('name', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'name': update})
        self.assertIsNone(result)

    def test_set_description(self):
        target = self.resource['id']
        update = 'change-desc'
        arglist = [target, '--description', update]
        verifylist = [
            (self.res, target),
            ('description', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'description': update})
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
        target = self.resource['id']

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_ipsec_site_connection.assert_called_once_with(
            target, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
