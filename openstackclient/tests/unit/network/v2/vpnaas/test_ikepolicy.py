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

from openstack.identity.v3 import project as _project
from openstack.network.v2 import vpn_ike_policy as _vpn_ike_policy
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.network.v2.vpnaas import ikepolicy
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes
from openstackclient.tests.unit import utils as tests_utils


class TestIKEPolicy(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self._ikepolicy = fakes.IKEPolicy().create()

        def _mock_ikepolicy(*args, **kwargs):
            self.network_client.find_vpn_ike_policy.assert_called_once_with(
                self._ikepolicy.id, ignore_missing=False
            )
            return {'id': args[0]}

        self.network_client.find_vpn_ike_policy.side_effect = mock.Mock(
            side_effect=_mock_ikepolicy
        )
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
            self._ikepolicy.id,
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

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project
        self.network_client.create_vpn_ike_policy.return_value = (
            self._ikepolicy
        )

        self.cmd = ikepolicy.CreateIKEPolicy(self.app, None)

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
        self.network_client.create_vpn_ike_policy.return_value = (
            self._ikepolicy
        )

        arglist = [
            '--description',
            'my-desc',
            '--auth-algorithm',
            'sha1',
            '--encryption-algorithm',
            'aes-128',
            '--phase1-negotiation-mode',
            'main',
            '--ike-version',
            'v1',
            '--pfs',
            'group5',
            '--project',
            self.project.id,
            self._ikepolicy.name,
        ]
        verifylist = [
            ('description', 'my-desc'),
            ('auth_algorithm', 'sha1'),
            ('encryption_algorithm', 'aes-128'),
            ('phase1_negotiation_mode', 'main'),
            ('ike_version', 'v1'),
            ('pfs', 'group5'),
            ('project', self.project.id),
            ('name', self._ikepolicy.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.ordered_data = tuple(
            self._ikepolicy[column] for column in self.ordered_columns
        )
        self.network_client.create_vpn_ike_policy.assert_called_once_with(
            description='my-desc',
            auth_algorithm='sha1',
            encryption_algorithm='aes-128',
            phase1_negotiation_mode='main',
            ike_version='v1',
            pfs='group5',
            project_id=self.project.id,
            name=self._ikepolicy.name,
        )
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertEqual(self.ordered_data, data)


class TestDeleteIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()

        self.cmd = ikepolicy.DeleteIKEPolicy(self.app, None)

    def test_delete_with_one_resource(self):
        def _mock_ike_p(*args, **kwargs):
            return _vpn_ike_policy.VpnIkePolicy(**{'id': args[0]})

        self.network_client.find_vpn_ike_policy.side_effect = _mock_ike_p

        arglist = [self._ikepolicy.id]
        verifylist = [('ikepolicy', [self._ikepolicy.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_vpn_ike_policy.assert_called_once_with(
            self._ikepolicy.id
        )
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_ike_p(*args, **kwargs):
            return _vpn_ike_policy.VpnIkePolicy(**{'id': args[0]})

        self.network_client.find_vpn_ike_policy.side_effect = _mock_ike_p

        arglist = ['target1', 'target2']
        verifylist = [('ikepolicy', ['target1', 'target2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(
            2, self.network_client.delete_vpn_ike_policy.call_count
        )
        for idx, reference in enumerate(['target1', 'target2']):
            actual = ''.join(
                self.network_client.delete_vpn_ike_policy.call_args_list[idx][
                    0
                ]
            )
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        arglist = ['target1']
        verifylist = [('ikepolicy', ['target1'])]

        self.network_client.find_vpn_ike_policy.side_effect = [
            'target1',
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
            self._ikepolicy.id,
            self._ikepolicy['name'],
            self._ikepolicy['auth_algorithm'],
            self._ikepolicy['encryption_algorithm'],
            self._ikepolicy['ike_version'],
            self._ikepolicy['pfs'],
        )

        self.network_client.vpn_ike_policies.return_value = [self._ikepolicy]

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_ike_policies.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_ike_policies.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()

        self.network_client.update_vpn_ike_policy.return_value = (
            self._ikepolicy
        )

        self.cmd = ikepolicy.SetIKEPolicy(self.app, None)

    def test_set_auth_algorithm_with_sha256(self):
        arglist = [
            self._ikepolicy.id,
            '--auth-algorithm',
            'sha256',
        ]
        verifylist = [
            ('ikepolicy', self._ikepolicy.id),
            ('auth_algorithm', 'sha256'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ike_policy.assert_called_once_with(
            self._ikepolicy.id, **{'auth_algorithm': 'sha256'}
        )
        self.assertIsNone(result)

    def test_set_phase1_negotiation_mode_with_aggressive(self):
        arglist = [
            self._ikepolicy.id,
            '--phase1-negotiation-mode',
            'aggressive',
        ]
        verifylist = [
            ('ikepolicy', self._ikepolicy.id),
            ('phase1_negotiation_mode', 'aggressive'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ike_policy.assert_called_once_with(
            self._ikepolicy.id, **{'phase1_negotiation_mode': 'aggressive'}
        )
        self.assertIsNone(result)

    def test_set_name(self):
        arglist = [
            self._ikepolicy.id,
            '--name',
            'foo',
        ]
        verifylist = [
            ('ikepolicy', self._ikepolicy.id),
            ('name', 'foo'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ike_policy.assert_called_once_with(
            self._ikepolicy.id, name='foo'
        )
        self.assertIsNone(result)

    def test_set_description(self):
        arglist = [
            self._ikepolicy.id,
            '--description',
            'foo',
        ]
        verifylist = [
            ('ikepolicy', self._ikepolicy.id),
            ('description', 'foo'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ike_policy.assert_called_once_with(
            self._ikepolicy.id, description='foo'
        )
        self.assertIsNone(result)


class TestShowIKEPolicy(TestIKEPolicy):
    def setUp(self):
        super().setUp()

        self.network_client.find_vpn_ike_policy.side_effect = None
        self.network_client.find_vpn_ike_policy.return_value = self._ikepolicy

        self.cmd = ikepolicy.ShowIKEPolicy(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        arglist = [self._ikepolicy.id]
        verifylist = [('ikepolicy', self._ikepolicy.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_ike_policy.assert_called_once_with(
            self._ikepolicy.id, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
