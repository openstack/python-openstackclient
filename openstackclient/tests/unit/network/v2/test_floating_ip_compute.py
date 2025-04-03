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
#

from unittest import mock

from osc_lib import exceptions

from openstackclient.api import compute_v2
from openstackclient.network.v2 import floating_ip as fip
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


@mock.patch.object(compute_v2, 'create_floating_ip')
class TestCreateFloatingIPCompute(compute_fakes.TestComputev2):
    _floating_ip = compute_fakes.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        _floating_ip['fixed_ip'],
        _floating_ip['id'],
        _floating_ip['instance_id'],
        _floating_ip['ip'],
        _floating_ip['pool'],
    )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = fip.CreateFloatingIP(self.app, None)

    def test_floating_ip_create_no_arg(self, fip_mock):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_floating_ip_create_default(self, fip_mock):
        fip_mock.return_value = self._floating_ip
        arglist = [
            self._floating_ip['pool'],
        ]
        verifylist = [
            ('network', self._floating_ip['pool']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(
            self.compute_client, self._floating_ip['pool']
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch.object(compute_v2, 'delete_floating_ip')
class TestDeleteFloatingIPCompute(compute_fakes.TestComputev2):
    _floating_ips = compute_fakes.create_floating_ips(count=2)

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = fip.DeleteFloatingIP(self.app, None)

    def test_floating_ip_delete(self, fip_mock):
        fip_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._floating_ips[0]['id'],
        ]
        verifylist = [
            ('floating_ip', [self._floating_ips[0]['id']]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(
            self.compute_client, self._floating_ips[0]['id']
        )
        self.assertIsNone(result)

    def test_floating_ip_delete_multi(self, fip_mock):
        fip_mock.return_value = mock.Mock(return_value=None)
        arglist = [
            self._floating_ips[0]['id'],
            self._floating_ips[1]['id'],
        ]
        verifylist = [
            ('floating_ip', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        fip_mock.assert_has_calls(
            [
                mock.call(self.compute_client, self._floating_ips[0]['id']),
                mock.call(self.compute_client, self._floating_ips[1]['id']),
            ]
        )
        self.assertIsNone(result)

    def test_floating_ip_delete_multi_exception(self, fip_mock):
        fip_mock.return_value = mock.Mock(return_value=None)
        fip_mock.side_effect = [
            mock.Mock(return_value=None),
            exceptions.CommandError,
        ]
        arglist = [
            self._floating_ips[0]['id'],
            'unexist_floating_ip',
        ]
        verifylist = [
            (
                'floating_ip',
                [self._floating_ips[0]['id'], 'unexist_floating_ip'],
            )
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 floating_ips failed to delete.', str(e))

        fip_mock.assert_any_call(
            self.compute_client, self._floating_ips[0]['id']
        )
        fip_mock.assert_any_call(self.compute_client, 'unexist_floating_ip')


@mock.patch.object(compute_v2, 'list_floating_ips')
class TestListFloatingIPCompute(compute_fakes.TestComputev2):
    _floating_ips = compute_fakes.create_floating_ips(count=3)

    columns = (
        'ID',
        'Floating IP Address',
        'Fixed IP Address',
        'Server',
        'Pool',
    )

    data = []
    for ip in _floating_ips:
        data.append(
            (
                ip['id'],
                ip['ip'],
                ip['fixed_ip'],
                ip['instance_id'],
                ip['pool'],
            )
        )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = fip.ListFloatingIP(self.app, None)

    def test_floating_ip_list(self, fip_mock):
        fip_mock.return_value = self._floating_ips
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(self.compute_client)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


@mock.patch.object(compute_v2, 'get_floating_ip')
class TestShowFloatingIPCompute(compute_fakes.TestComputev2):
    _floating_ip = compute_fakes.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        _floating_ip['fixed_ip'],
        _floating_ip['id'],
        _floating_ip['instance_id'],
        _floating_ip['ip'],
        _floating_ip['pool'],
    )

    def setUp(self):
        super().setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.cmd = fip.ShowFloatingIP(self.app, None)

    def test_floating_ip_show(self, fip_mock):
        fip_mock.return_value = self._floating_ip
        arglist = [
            self._floating_ip['id'],
        ]
        verifylist = [
            ('floating_ip', self._floating_ip['id']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        fip_mock.assert_called_once_with(
            self.compute_client, self._floating_ip['id']
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
