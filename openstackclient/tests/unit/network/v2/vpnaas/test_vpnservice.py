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
import uuid

from openstack.identity.v3 import project as _project
from openstack.network.v2 import vpn_service as sdk_vpn_service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.network.v2.vpnaas import vpnservice
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes


class TestVPNService(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self._vpnservice = fakes.VPNService().create()

        def _mock_vpnservice(*args, **kwargs):
            self.network_client.find_vpn_service.assert_called_once_with(
                self._vpnservice['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.fake_router = mock.Mock()
        self.fake_subnet = mock.Mock()
        self.network_client.find_router.return_value = self.fake_router
        self.network_client.find_subnet.return_value = self.fake_subnet
        self.fake_router.id = 'router-id-' + uuid.uuid4().hex
        self.fake_subnet.id = 'subnet-id-' + uuid.uuid4().hex

        self.network_client.find_vpn_service.side_effect = mock.Mock(
            side_effect=_mock_vpnservice
        )

        self.headers = (
            'ID',
            'Name',
            'Router',
            'Subnet',
            'Flavor',
            'State',
            'Status',
            'Description',
            'Project',
            'Ext v4 IP',
            'Ext v6 IP',
        )
        self.ordered_headers = (
            'Description',
            'Ext v4 IP',
            'Ext v6 IP',
            'Flavor',
            'ID',
            'Name',
            'Project',
            'Router',
            'State',
            'Status',
            'Subnet',
        )
        self.ordered_data = (
            self._vpnservice['description'],
            self._vpnservice['external_v4_ip'],
            self._vpnservice['external_v6_ip'],
            self._vpnservice['flavor_id'],
            self._vpnservice['id'],
            self._vpnservice['name'],
            self._vpnservice['project_id'],
            self._vpnservice['router_id'],
            self._vpnservice['admin_state_up'],
            self._vpnservice['status'],
            self._vpnservice['subnet_id'],
        )
        self.ordered_columns = (
            'description',
            'external_v4_ip',
            'external_v6_ip',
            'flavor_id',
            'id',
            'name',
            'project_id',
            'router_id',
            'admin_state_up',
            'status',
            'subnet_id',
        )


class TestCreateVPNService(TestVPNService):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.network_client.create_vpn_service.return_value = self._vpnservice
        self.mocked = self.network_client.create_vpn_service
        self.cmd = vpnservice.CreateVPNService(self.app, None)

    def test_create_with_all_params(self):
        arglist = [
            '--description',
            'my-desc',
            '--project',
            self.project.id,
            '--subnet',
            self.fake_subnet.id,
            '--router',
            self.fake_router.id,
            'my-name',
        ]
        verifylist = [
            ('description', 'my-desc'),
            ('project', self.project.id),
            ('subnet', self.fake_subnet.id),
            ('router', self.fake_router.id),
            ('name', 'my-name'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.network_client.create_vpn_service.assert_called_once_with(
            description='my-desc',
            project_id=self.project.id,
            subnet_id=self.fake_subnet.id,
            router_id=self.fake_router.id,
            name='my-name',
        )
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertCountEqual(self.ordered_data, data)


class TestDeleteVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.cmd = vpnservice.DeleteVPNService(self.app, None)

    def test_delete_with_one_resource(self):
        def _mock_vpn_s(*args, **kwargs):
            return sdk_vpn_service.VpnService(**{'id': args[0]})

        self.network_client.find_vpn_service.side_effect = _mock_vpn_s

        arglist = [self._vpnservice['id']]
        verifylist = [('vpnservice', [self._vpnservice['id']])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_vpn_service.assert_called_once_with(
            self._vpnservice['id']
        )
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_vpn_s(*args, **kwargs):
            return sdk_vpn_service.VpnService(**{'id': args[0]})

        self.network_client.find_vpn_service.side_effect = _mock_vpn_s

        arglist = ['target1', 'target2']
        verifylist = [('vpnservice', ['target1', 'target2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.network_client.delete_vpn_service.call_count)
        for idx, reference in enumerate(['target1', 'target2']):
            actual = ''.join(
                self.network_client.delete_vpn_service.call_args_list[idx][0]
            )
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        arglist = ['target']
        verifylist = [('vpnservice', ['target'])]

        self.network_client.find_vpn_ipsec_policy.side_effect = [
            'target',
            exceptions.CommandError,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestListVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.cmd = vpnservice.ListVPNService(self.app, None)

        self.short_header = (
            'ID',
            'Name',
            'Router',
            'Subnet',
            'Flavor',
            'State',
            'Status',
        )

        self.short_data = (
            self._vpnservice['id'],
            self._vpnservice['name'],
            self._vpnservice['router_id'],
            self._vpnservice['subnet_id'],
            self._vpnservice['flavor_id'],
            self._vpnservice['admin_state_up'],
            self._vpnservice['status'],
        )

        self.network_client.vpn_services.return_value = [self._vpnservice]

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_services.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_services.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_service.return_value = self._vpnservice
        self.cmd = vpnservice.SetVPNSercice(self.app, None)

    def test_set_name(self):
        arglist = [self._vpnservice['id'], '--name', 'change']
        verifylist = [
            ('vpnservice', self._vpnservice['id']),
            ('name', 'change'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_service.assert_called_once_with(
            self._vpnservice['id'], name='change'
        )
        self.assertIsNone(result)

    def test_set_description(self):
        arglist = [self._vpnservice['id'], '--description', 'change-desc']
        verifylist = [
            ('vpnservice', self._vpnservice['id']),
            ('description', 'change-desc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_service.assert_called_once_with(
            self._vpnservice['id'], description='change-desc'
        )
        self.assertIsNone(result)


class TestShowVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.network_client.find_vpn_service.side_effect = None
        self.network_client.find_vpn_service.return_value = self._vpnservice
        self.cmd = vpnservice.ShowVPNService(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        arglist = [self._vpnservice['id']]
        verifylist = [('vpnservice', self._vpnservice['id'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_service.assert_called_once_with(
            self._vpnservice['id'], ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
