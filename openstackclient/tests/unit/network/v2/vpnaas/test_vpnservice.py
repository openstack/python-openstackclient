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
import uuid

from openstack.network.v2 import vpn_service as sdk_vpn_service
from osc_lib import exceptions

from openstackclient.identity import common as identity_common
from openstackclient.network.v2.vpnaas import vpnservice
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes


class TestVPNService(test_fakes.TestNetworkV2):
    def _generate_data(self, ordered_dict=None, data=None):
        source = ordered_dict if ordered_dict else self._vpnservice
        if data:
            source.update(data)
        return source

    def _generate_req_and_res(self, verifylist):
        request = dict(verifylist)
        response = self._vpnservice
        for key, val in verifylist:
            converted = self.CONVERT_MAP.get(key, key)
            del request[key]
            new_value = val
            request[converted] = new_value
            response[converted] = new_value
        return request, response

    def _check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: list(exp_req)}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super().setUp()

        self._vpnservice = fakes.VPNService().create()
        self.CONVERT_MAP = {
            'project': 'project_id',
            'router': 'router_id',
            'subnet': 'subnet_id',
        }

        def _mock_vpnservice(*args, **kwargs):
            self.network_client.find_vpn_service.assert_called_once_with(
                self.resource['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.fake_router = mock.Mock()
        self.fake_subnet = mock.Mock()
        self.network_client.find_router.return_value = self.fake_router
        self.network_client.find_subnet.return_value = self.fake_subnet
        self.args = {
            'name': 'my-name',
            'description': 'my-desc',
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'router_id': 'router-id-' + uuid.uuid4().hex,
            'subnet_id': 'subnet-id-' + uuid.uuid4().hex,
        }
        self.fake_subnet.id = self.args['subnet_id']
        self.fake_router.id = self.args['router_id']

        self.network_client.find_vpn_service.side_effect = mock.Mock(
            side_effect=_mock_vpnservice
        )
        identity_common.find_project = mock.Mock()
        identity_common.find_project.id = self._vpnservice['project_id']

        self.res = 'vpnservice'
        self.res_plural = 'vpnservices'
        self.resource = self._vpnservice
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
        self.data = self._generate_data()
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
        self.network_client.create_vpn_service.return_value = self._vpnservice
        self.mocked = self.network_client.create_vpn_service
        self.cmd = vpnservice.CreateVPNService(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_vpn_service.return_value = response
        identity_common.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = self._generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self):
        name = self.args.get('name')
        description = self.args.get('description')
        router_id = self.args.get('router_id')
        subnet_id = self.args.get('subnet_id')
        project_id = self.args.get('project_id')
        arglist = [
            '--description',
            description,
            '--project',
            project_id,
            '--subnet',
            subnet_id,
            '--router',
            router_id,
            name,
        ]
        verifylist = [
            ('description', description),
            ('project', project_id),
            ('subnet', subnet_id),
            ('router', router_id),
            ('name', name),
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self):
        arglist, verifylist = self._set_all_params()
        request, response = self._generate_req_and_res(verifylist)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self._check_results(headers, data, request)

    def test_create_with_all_params(self):
        self._test_create_with_all_params()


class TestDeleteVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.delete_vpn_service
        self.cmd = vpnservice.DeleteVPNService(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_vpn_s(*args, **kwargs):
            return sdk_vpn_service.VpnService(**{'id': args[0]})

        self.network_client.find_vpn_service.side_effect = _mock_vpn_s

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_vpn_s(*args, **kwargs):
            return sdk_vpn_service.VpnService(**{'id': args[0]})

        self.network_client.find_vpn_service.side_effect = _mock_vpn_s

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

        self.network_client.find_vpn_ipsec_policy.side_effect = [
            target1,
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
        self.mocked = self.network_client.vpn_services

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


class TestSetVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_service.return_value = self._vpnservice
        self.mocked = self.network_client.update_vpn_service
        self.cmd = vpnservice.SetVPNSercice(self.app, None)

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


class TestShowVPNService(TestVPNService):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.get_vpn_service
        self.network_client.find_vpn_service.side_effect = None
        self.network_client.find_vpn_service.return_value = self._vpnservice
        self.cmd = vpnservice.ShowVPNService(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_service.assert_called_once_with(
            target, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
