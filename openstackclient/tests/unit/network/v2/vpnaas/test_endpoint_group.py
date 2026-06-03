#   Copyright 2017 FUJITSU LIMITED
#   All Rights Reserved
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

from openstack.network.v2 import vpn_endpoint_group as sdk_vpn_epg
from openstackclient.tests.unit import utils as tests_utils
from osc_lib import exceptions

from openstackclient.identity import common as identity_common
from openstackclient.network.v2.vpnaas import endpoint_group
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes


class TestEndpointGroup(test_fakes.TestNetworkV2):
    def _generate_data(self, ordered_dict=None, data=None):
        source = ordered_dict if ordered_dict else self._endpoint_group
        if data:
            source.update(data)
        return source

    def _generate_req_and_res(self, verifylist):
        request = dict(verifylist)
        response = self._endpoint_group
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
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super().setUp()

        self._endpoint_group = fakes.EndpointGroup().create()
        self.CONVERT_MAP = {
            'project': 'project_id',
        }

        def _mock_endpoint_group(*args, **kwargs):
            self.network_client.find_vpn_endpoint_group.assert_called_once_with(
                self.resource['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.network_client.find_vpn_endpoint_group.side_effect = mock.Mock(
            side_effect=_mock_endpoint_group
        )
        identity_common.find_project = mock.Mock()
        identity_common.find_project.return_value.id = self._endpoint_group[
            'project_id'
        ]
        self.res = 'endpoint_group'
        self.res_plural = 'endpoint_groups'
        self.resource = self._endpoint_group
        self.headers = (
            'ID',
            'Name',
            'Type',
            'Endpoints',
            'Description',
            'Project',
        )
        self.data = self._generate_data()
        self.ordered_headers = (
            'Description',
            'Endpoints',
            'ID',
            'Name',
            'Project',
            'Type',
        )
        self.ordered_data = (
            self._endpoint_group['description'],
            self._endpoint_group['endpoints'],
            self._endpoint_group['id'],
            self._endpoint_group['name'],
            self._endpoint_group['project_id'],
            self._endpoint_group['type'],
        )
        self.ordered_columns = (
            'description',
            'endpoints',
            'id',
            'name',
            'project_id',
            'type',
        )


class TestCreateEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.network_client.create_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )
        self.mocked = self.network_client.create_vpn_endpoint_group
        self.cmd = endpoint_group.CreateEndpointGroup(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_vpn_endpoint_group.return_value = response
        identity_common.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = self._generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params_cidr(self, args={}):
        name = args.get('name') or 'my-name'
        description = args.get('description') or 'my-desc'
        endpoint_type = args.get('type') or 'cidr'
        endpoints = args.get('endpoints') or ['10.0.0.0/24', '20.0.0.0/24']
        project_id = args.get('project_id') or 'my-project'
        arglist = [
            '--description',
            description,
            '--type',
            endpoint_type,
            '--value',
            '10.0.0.0/24',
            '--value',
            '20.0.0.0/24',
            '--project',
            project_id,
            name,
        ]
        verifylist = [
            ('description', description),
            ('type', endpoint_type),
            ('endpoints', endpoints),
            ('project', project_id),
            ('name', name),
        ]
        return arglist, verifylist

    def _test_create_with_all_params_cidr(self, args={}):
        arglist, verifylist = self._set_all_params_cidr(args)
        request, response = self._generate_req_and_res(verifylist)
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

    def test_create_with_all_params_cidr(self):
        self._test_create_with_all_params_cidr()


class TestDeleteEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.delete_vpn_endpoint_group
        self.cmd = endpoint_group.DeleteEndpointGroup(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_e_g(*args, **kwargs):
            return sdk_vpn_epg.VpnEndpointGroup(**{'id': args[0]})

        self.network_client.find_vpn_endpoint_group.side_effect = _mock_e_g

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_e_g(*args, **kwargs):
            return sdk_vpn_epg.VpnEndpointGroup(**{'id': args[0]})

        self.network_client.find_vpn_endpoint_group.side_effect = _mock_e_g

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
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestListEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.cmd = endpoint_group.ListEndpointGroup(self.app, None)

        self.short_header = (
            'ID',
            'Name',
            'Type',
            'Endpoints',
        )

        self.short_data = (
            self._endpoint_group['id'],
            self._endpoint_group['name'],
            self._endpoint_group['type'],
            self._endpoint_group['endpoints'],
        )

        self.network_client.vpn_endpoint_groups.return_value = [
            self._endpoint_group
        ]
        self.mocked = self.network_client.vpn_endpoint_groups

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


class TestSetEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )
        self.mocked = self.network_client.update_vpn_endpoint_group
        self.cmd = endpoint_group.SetEndpointGroup(self.app, None)

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


class TestShowEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.network_client.find_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )
        self.network_client.find_vpn_endpoint_group.side_effect = None
        self.cmd = endpoint_group.ShowEndpointGroup(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_endpoint_group.assert_called_once_with(
            target, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
