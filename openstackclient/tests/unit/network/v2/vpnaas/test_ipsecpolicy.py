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
from openstack.network.v2 import vpn_ipsec_policy as sdk_vpn_ipsecp_p
from openstack.test import fakes as sdk_fakes
from openstackclient.tests.unit import utils as tests_utils
from osc_lib import exceptions

from openstackclient.network.v2.vpnaas import ipsecpolicy
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes


class TestIPSecPolicy(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self._ipsecpolicy = fakes.IPSecPolicy().create()

        def _mock_ipsecpolicy(*args, **kwargs):
            self.network_client.find_vpn_ipsec_policy.assert_called_once_with(
                self._ipsecpolicy['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.network_client.find_vpn_ipsec_policy.side_effect = mock.Mock(
            side_effect=_mock_ipsecpolicy
        )
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

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.network_client.create_vpn_ipsec_policy.return_value = (
            self._ipsecpolicy
        )
        self.mocked = self.network_client.create_vpn_ipsec_policy
        self.cmd = ipsecpolicy.CreateIPsecPolicy(self.app, None)

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
            'my-name',
            '--auth-algorithm',
            'sha1',
            '--encapsulation-mode',
            'tunnel',
            '--transform-protocol',
            'esp',
            '--encryption-algorithm',
            'aes-128',
            '--pfs',
            'group5',
            '--description',
            'my-desc',
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('name', 'my-name'),
            ('auth_algorithm', 'sha1'),
            ('encapsulation_mode', 'tunnel'),
            ('transform_protocol', 'esp'),
            ('encryption_algorithm', 'aes-128'),
            ('pfs', 'group5'),
            ('description', 'my-desc'),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.network_client.create_vpn_ipsec_policy.assert_called_once_with(
            name='my-name',
            auth_algorithm='sha1',
            encapsulation_mode='tunnel',
            transform_protocol='esp',
            encryption_algorithm='aes-128',
            pfs='group5',
            description='my-desc',
            project_id=self.project.id,
        )
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertCountEqual(self.ordered_data, data)

    def test_create_with_all_params_name(self):
        arglist = [
            'new_ipsecpolicy',
            '--auth-algorithm',
            'sha1',
            '--encapsulation-mode',
            'tunnel',
            '--transform-protocol',
            'esp',
            '--encryption-algorithm',
            'aes-128',
            '--pfs',
            'group5',
            '--description',
            'my-desc',
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('name', 'new_ipsecpolicy'),
            ('auth_algorithm', 'sha1'),
            ('encapsulation_mode', 'tunnel'),
            ('transform_protocol', 'esp'),
            ('encryption_algorithm', 'aes-128'),
            ('pfs', 'group5'),
            ('description', 'my-desc'),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.network_client.create_vpn_ipsec_policy.assert_called_once_with(
            name='new_ipsecpolicy',
            auth_algorithm='sha1',
            encapsulation_mode='tunnel',
            transform_protocol='esp',
            encryption_algorithm='aes-128',
            pfs='group5',
            description='my-desc',
            project_id=self.project.id,
        )
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertCountEqual(self.ordered_data, data)


class TestDeleteIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()
        self.cmd = ipsecpolicy.DeleteIPsecPolicy(self.app, None)

    def test_delete_with_one_resource(self):
        def _mock_ipsec_p(*args, **kwargs):
            return sdk_vpn_ipsecp_p.VpnIpsecPolicy(**{'id': args[0]})

        self.network_client.find_vpn_ipsec_policy.side_effect = _mock_ipsec_p

        arglist = [self._ipsecpolicy['id']]
        verifylist = [('ipsecpolicy', [self._ipsecpolicy['id']])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_vpn_ipsec_policy.assert_called_once_with(
            self._ipsecpolicy['id']
        )
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_ipsec_p(*args, **kwargs):
            return sdk_vpn_ipsecp_p.VpnIpsecPolicy(**{'id': args[0]})

        self.network_client.find_vpn_ipsec_policy.side_effect = _mock_ipsec_p

        arglist = ['target1', 'target2']
        verifylist = [('ipsecpolicy', ['target1', 'target2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(
            2, self.network_client.delete_vpn_ipsec_policy.call_count
        )
        for idx, reference in enumerate(['target1', 'target2']):
            actual = ''.join(
                self.network_client.delete_vpn_ipsec_policy.call_args_list[
                    idx
                ][0]
            )
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        arglist = ['target']
        verifylist = [('ipsecpolicy', ['target'])]

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

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_ipsec_policies.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_ipsec_policies.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetIPSecPolicy(TestIPSecPolicy):
    def setUp(self):
        super().setUp()
        self.network_client.update_vpn_ipsec_policy.return_value = (
            self._ipsecpolicy
        )
        self.cmd = ipsecpolicy.SetIPsecPolicy(self.app, None)

    def test_set_auth_algorithm_with_sha256(self):
        arglist = [self._ipsecpolicy['id'], '--auth-algorithm', 'sha256']
        verifylist = [
            ('ipsecpolicy', self._ipsecpolicy['id']),
            ('auth_algorithm', 'sha256'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ipsec_policy.assert_called_once_with(
            self._ipsecpolicy['id'], auth_algorithm='sha256'
        )
        self.assertIsNone(result)

    def test_set_name(self):
        arglist = [self._ipsecpolicy['id'], '--name', 'change']
        verifylist = [
            ('ipsecpolicy', self._ipsecpolicy['id']),
            ('name', 'change'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ipsec_policy.assert_called_once_with(
            self._ipsecpolicy['id'], name='change'
        )
        self.assertIsNone(result)

    def test_set_description(self):
        arglist = [self._ipsecpolicy['id'], '--description', 'change-desc']
        verifylist = [
            ('ipsecpolicy', self._ipsecpolicy['id']),
            ('description', 'change-desc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_ipsec_policy.assert_called_once_with(
            self._ipsecpolicy['id'], description='change-desc'
        )
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
        arglist = [self._ipsecpolicy['id']]
        verifylist = [('ipsecpolicy', self._ipsecpolicy['id'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_ipsec_policy.assert_called_once_with(
            self._ipsecpolicy['id'], ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
