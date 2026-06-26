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

from openstack.network.v2 import vpn_ike_policy as sdk_vpn_ike_p
from osc_lib import exceptions

from openstackclient.identity import common as identity_common
from openstackclient.network.v2.vpnaas import ikepolicy
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes
from openstackclient.tests.unit import utils as tests_utils


class TestIKEPolicy(test_fakes.TestNetworkV2):
    def _generate_data(self, ordered_dict=None, data=None):
        source = ordered_dict if ordered_dict else self._ikepolicy
        if data:
            source.update(data)
        return source

    def _generate_req_and_res(self, verifylist):
        request = dict(verifylist)
        response = self._ikepolicy
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

        self._ikepolicy = fakes.IKEPolicy().create()
        self.CONVERT_MAP = {
            'project': 'project_id',
        }

        def _mock_ikepolicy(*args, **kwargs):
            self.network_client.find_vpn_ike_policy.assert_called_once_with(
                self.resource['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.network_client.find_vpn_ike_policy.side_effect = mock.Mock(
            side_effect=_mock_ikepolicy
        )
        identity_common.find_project = mock.Mock()
        identity_common.find_project.id = self._ikepolicy['project_id']
        self.res = 'ikepolicy'
        self.res_plural = 'ikepolicies'
        self.resource = self._ikepolicy
        self.headers = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encryption Algorithm',
            'IKE Version',
            'Perfect Forward Secrecy (PFS)',
            'Description',
            'Phase1 Negotiation Mode',
            'Project',
            'Lifetime',
        )
        self.data = self._generate_data()
        self.ordered_headers = (
            'Authentication Algorithm',
            'Description',
            'Encryption Algorithm',
            'ID',
            'IKE Version',
            'Lifetime',
            'Name',
            'Perfect Forward Secrecy (PFS)',
            'Phase1 Negotiation Mode',
            'Project',
        )
        self.ordered_data = (
            self._ikepolicy['auth_algorithm'],
            self._ikepolicy['description'],
            self._ikepolicy['encryption_algorithm'],
            self._ikepolicy['id'],
            self._ikepolicy['ike_version'],
            self._ikepolicy['lifetime'],
            self._ikepolicy['name'],
            self._ikepolicy['pfs'],
            self._ikepolicy['phase1_negotiation_mode'],
            self._ikepolicy['project_id'],
        )
        self.ordered_columns = (
            'auth_algorithm',
            'description',
            'encryption_algorithm',
            'id',
            'ike_version',
            'lifetime',
            'name',
            'pfs',
            'phase1_negotiation_mode',
            'project_id',
        )


class TestCreateIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.create_vpn_ike_policy.return_value = (
            self._ikepolicy
        )
        self.mocked = self.network_client.create_vpn_ike_policy
        self.cmd = ikepolicy.CreateIKEPolicy(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_vpn_ike_policy.return_value = response
        identity_common.find_project.return_value.id = response['project_id']
        # Update response(finally returns 'data')
        self.data = self._generate_data(ordered_dict=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name') or 'my-name'
        description = args.get('description') or 'my-desc'
        auth_algorithm = args.get('auth_algorithm') or 'sha1'
        encryption_algorithm = args.get('encryption_algorithm') or 'aes-128'
        phase1_negotiation_mode = args.get('phase1_negotiation_mode') or 'main'
        ike_version = args.get('ike_version') or 'v1'
        pfs = args.get('pfs') or 'group5'
        project_id = args.get('project_id') or 'my-tenant'
        arglist = [
            '--description',
            description,
            '--auth-algorithm',
            auth_algorithm,
            '--encryption-algorithm',
            encryption_algorithm,
            '--phase1-negotiation-mode',
            phase1_negotiation_mode,
            '--ike-version',
            ike_version,
            '--pfs',
            pfs,
            '--project',
            project_id,
            name,
        ]
        verifylist = [
            ('description', description),
            ('auth_algorithm', auth_algorithm),
            ('encryption_algorithm', encryption_algorithm),
            ('phase1_negotiation_mode', phase1_negotiation_mode),
            ('ike_version', ike_version),
            ('pfs', pfs),
            ('project', project_id),
            ('name', name),
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
        self._test_create_with_all_params({'name': 'new_ikepolicy'})

    def test_create_with_all_params_aggressive_mode(self):
        self._test_create_with_all_params(
            {'phase1_negotiation_mode': 'aggressive'}
        )


class TestDeleteIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.delete_vpn_ike_policy
        self.cmd = ikepolicy.DeleteIKEPolicy(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_ike_p(*args, **kwargs):
            return sdk_vpn_ike_p.VpnIkePolicy(**{'id': args[0]})

        self.network_client.find_vpn_ike_policy.side_effect = _mock_ike_p

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_ike_p(*args, **kwargs):
            return sdk_vpn_ike_p.VpnIkePolicy(**{'id': args[0]})

        self.network_client.find_vpn_ike_policy.side_effect = _mock_ike_p

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

        self.network_client.find_vpn_ike_policy.side_effect = [
            target1,
            exceptions.CommandError,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestListIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()
        self.cmd = ikepolicy.ListIKEPolicy(self.app, None)

        self.short_header = (
            'ID',
            'Name',
            'Authentication Algorithm',
            'Encryption Algorithm',
            'IKE Version',
            'Perfect Forward Secrecy (PFS)',
        )

        self.short_data = (
            self._ikepolicy['id'],
            self._ikepolicy['name'],
            self._ikepolicy['auth_algorithm'],
            self._ikepolicy['encryption_algorithm'],
            self._ikepolicy['ike_version'],
            self._ikepolicy['pfs'],
        )

        self.network_client.vpn_ike_policies.return_value = [self._ikepolicy]
        self.mocked = self.network_client.vpn_ike_policies

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


class TestSetIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_ike_policy.return_value = (
            self._ikepolicy
        )
        self.mocked = self.network_client.update_vpn_ike_policy
        self.cmd = ikepolicy.SetIKEPolicy(self.app, None)

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

    def test_set_phase1_negotiation_mode_with_aggressive(self):
        target = self.resource['id']
        phase1_negotiation_mode = 'aggressive'
        arglist = [
            target,
            '--phase1-negotiation-mode',
            phase1_negotiation_mode,
        ]
        verifylist = [
            (self.res, target),
            ('phase1_negotiation_mode', phase1_negotiation_mode),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'phase1_negotiation_mode': 'aggressive'}
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


class TestShowIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.find_vpn_ike_policy.side_effect = None
        self.network_client.find_vpn_ike_policy.return_value = self._ikepolicy
        self.cmd = ikepolicy.ShowIKEPolicy(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_ike_policy.assert_called_once_with(
            target, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
