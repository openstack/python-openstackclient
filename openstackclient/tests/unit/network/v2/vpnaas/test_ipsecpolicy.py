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

from openstack.network.v2 import vpn_ipsec_policy as sdk_vpn_ipsecp_p
from openstackclient.tests.unit import utils as tests_utils
from osc_lib import exceptions

from openstackclient.identity import common as identity_common
from openstackclient.network.v2.vpnaas import ipsecpolicy
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes


class TestIPSecPolicy(test_fakes.TestNetworkV2):
    def _generate_data(self, ordered_dict=None, data=None):
        source = ordered_dict if ordered_dict else self._ipsecpolicy
        if data:
            source.update(data)
        return source

    def _generate_req_and_res(self, verifylist):
        request = dict(verifylist)
        response = self._ipsecpolicy
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
        self.assertEqual(self.ordered_headers, headers)
        self.assertEqual(self.ordered_data, data)

    def setUp(self):
        super().setUp()

        self._ipsecpolicy = fakes.IPSecPolicy().create()
        self.CONVERT_MAP = {
            'project': 'project_id',
        }

        def _mock_ipsecpolicy(*args, **kwargs):
            self.network_client.find_vpn_ipsec_policy.assert_called_once_with(
                self.resource['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.network_client.find_vpn_ipsec_policy.side_effect = mock.Mock(
            side_effect=_mock_ipsecpolicy
        )
        identity_common.find_project = mock.Mock()
        identity_common.find_project.id = self._ipsecpolicy['project_id']
        self.res = 'ipsecpolicy'
        self.res_plural = 'ipsecpolicies'
        self.resource = self._ipsecpolicy
        self.headers = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encapsulation Mode',
            'Transform Protocol',
            'Encryption Algorithm',
            'Perfect Forward Secrecy (PFS)',
            'Description',
            'Project',
            'Lifetime',
        )
        self.data = self._generate_data()
        self.ordered_headers = (
            'Authentication Algorithm',
            'Description',
            'Encapsulation Mode',
            'Encryption Algorithm',
            'ID',
            'Lifetime',
            'Name',
            'Perfect Forward Secrecy (PFS)',
            'Project',
            'Transform Protocol',
        )
        self.ordered_data = (
            self._ipsecpolicy['auth_algorithm'],
            self._ipsecpolicy['description'],
            self._ipsecpolicy['encapsulation_mode'],
            self._ipsecpolicy['encryption_algorithm'],
            self._ipsecpolicy['id'],
            self._ipsecpolicy['lifetime'],
            self._ipsecpolicy['name'],
            self._ipsecpolicy['pfs'],
            self._ipsecpolicy['project_id'],
            self._ipsecpolicy['transform_protocol'],
        )
        self.ordered_columns = (
            'auth_algorithm',
            'description',
            'encapsulation_mode',
            'encryption_algorithm',
            'id',
            'lifetime',
            'name',
            'pfs',
            'project_id',
            'transform_protocol',
        )


class TestCreateIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.create_vpn_ipsec_policy.return_value = (
            self._ipsecpolicy
        )
        self.mocked = self.network_client.create_vpn_ipsec_policy
        self.cmd = ipsecpolicy.CreateIPsecPolicy(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_vpn_ipsec_policy.return_value = response
        identity_common.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = self._generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name') or 'my-name'
        auth_algorithm = args.get('auth_algorithm') or 'sha1'
        encapsulation_mode = args.get('encapsulation_mode') or 'tunnel'
        transform_protocol = args.get('transform_protocol') or 'esp'
        encryption_algorithm = args.get('encryption_algorithm') or 'aes-128'
        pfs = args.get('pfs') or 'group5'
        description = args.get('description') or 'my-desc'
        project_id = args.get('project_id') or 'my-project'
        arglist = [
            name,
            '--auth-algorithm',
            auth_algorithm,
            '--encapsulation-mode',
            encapsulation_mode,
            '--transform-protocol',
            transform_protocol,
            '--encryption-algorithm',
            encryption_algorithm,
            '--pfs',
            pfs,
            '--description',
            description,
            '--project',
            project_id,
        ]
        verifylist = [
            ('name', name),
            ('auth_algorithm', auth_algorithm),
            ('encapsulation_mode', encapsulation_mode),
            ('transform_protocol', transform_protocol),
            ('encryption_algorithm', encryption_algorithm),
            ('pfs', pfs),
            ('description', description),
            ('project', project_id),
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self, args={}):
        arglist, verifylist = self._set_all_params(args)
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

    def test_create_with_all_params(self):
        self._test_create_with_all_params()

    def test_create_with_all_params_name(self):
        self._test_create_with_all_params({'name': 'new_ipsecpolicy'})


class TestDeleteIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.delete_vpn_ipsec_policy
        self.cmd = ipsecpolicy.DeleteIPsecPolicy(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_ipsec_p(*args, **kwargs):
            return sdk_vpn_ipsecp_p.VpnIpsecPolicy(**{'id': args[0]})

        self.network_client.find_vpn_ipsec_policy.side_effect = _mock_ipsec_p

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_ipsec_p(*args, **kwargs):
            return sdk_vpn_ipsecp_p.VpnIpsecPolicy(**{'id': args[0]})

        self.network_client.find_vpn_ipsec_policy.side_effect = _mock_ipsec_p

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


class TestListIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()
        self.cmd = ipsecpolicy.ListIPsecPolicy(self.app, None)

        self.short_header = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encapsulation Mode',
            'Transform Protocol',
            'Encryption Algorithm',
        )

        self.short_data = (
            self._ipsecpolicy['id'],
            self._ipsecpolicy['name'],
            self._ipsecpolicy['auth_algorithm'],
            self._ipsecpolicy['encapsulation_mode'],
            self._ipsecpolicy['transform_protocol'],
            self._ipsecpolicy['encryption_algorithm'],
        )

        self.network_client.vpn_ipsec_policies.return_value = [
            self._ipsecpolicy
        ]
        self.mocked = self.network_client.vpn_ipsec_policies

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


class TestSetIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_ipsec_policy.return_value = (
            self._ipsecpolicy
        )
        self.mocked = self.network_client.update_vpn_ipsec_policy
        self.cmd = ipsecpolicy.SetIPsecPolicy(self.app, None)

    def test_set_auth_algorithm_with_sha256(self):
        target = self.resource['id']
        auth_algorithm = 'sha256'
        arglist = [target, '--auth-algorithm', auth_algorithm]
        verifylist = [
            (self.res, target),
            ('auth_algorithm', auth_algorithm),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'auth_algorithm': 'sha256'}
        )
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


class TestShowIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()

        self.network_client.find_vpn_ipsec_policy.side_effect = None
        self.network_client.find_vpn_ipsec_policy.return_value = (
            self._ipsecpolicy
        )
        self.cmd = ipsecpolicy.ShowIPsecPolicy(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        def _mock_ipsec_p(*args, **kwargs):
            return sdk_vpn_ipsecp_p.VpnIpsecPolicy(**{'id': args[0]})

        self.network_client.find_vpn_service.side_effect = _mock_ipsec_p

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_ipsec_policy.assert_called_once_with(
            target, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
