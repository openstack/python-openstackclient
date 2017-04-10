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

import mock
from mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import floating_ip as fip
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import utils as tests_utils


# Tests for Nova network

class TestFloatingIPCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFloatingIPCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestCreateFloatingIPCompute(TestFloatingIPCompute):

    # The floating ip to be deleted.
    floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        floating_ip.fixed_ip,
        floating_ip.id,
        floating_ip.instance_id,
        floating_ip.ip,
        floating_ip.pool,
    )

    def setUp(self):
        super(TestCreateFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.create.return_value = self.floating_ip

        # Get the command object to test
        self.cmd = fip.CreateFloatingIP(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.floating_ip.pool,
        ]
        verifylist = [
            ('network', self.floating_ip.pool),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.create.assert_called_once_with(
            self.floating_ip.pool)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteFloatingIPCompute(TestFloatingIPCompute):

    # The floating ips to be deleted.
    floating_ips = compute_fakes.FakeFloatingIP.create_floating_ips(count=2)

    def setUp(self):
        super(TestDeleteFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.delete.return_value = None

        # Return value of utils.find_resource()
        self.compute.floating_ips.get = (
            compute_fakes.FakeFloatingIP.get_floating_ips(self.floating_ips))

        # Get the command object to test
        self.cmd = fip.DeleteFloatingIP(self.app, None)

    def test_floating_ip_delete(self):
        arglist = [
            self.floating_ips[0].id,
        ]
        verifylist = [
            ('floating_ip', [self.floating_ips[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.delete.assert_called_once_with(
            self.floating_ips[0].id
        )
        self.assertIsNone(result)

    def test_multi_floating_ips_delete(self):
        arglist = []
        verifylist = []

        for f in self.floating_ips:
            arglist.append(f.id)
        verifylist = [
            ('floating_ip', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for f in self.floating_ips:
            calls.append(call(f.id))
        self.compute.floating_ips.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_floating_ips_delete_with_exception(self):
        arglist = [
            self.floating_ips[0].id,
            'unexist_floating_ip',
        ]
        verifylist = [
            ('floating_ip',
             [self.floating_ips[0].id, 'unexist_floating_ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.floating_ips[0], exceptions.CommandError]
        self.compute.floating_ips.get = (
            mock.Mock(side_effect=find_mock_result)
        )
        self.compute.floating_ips.find.side_effect = exceptions.NotFound(None)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 floating_ips failed to delete.', str(e))

        self.compute.floating_ips.get.assert_any_call(
            self.floating_ips[0].id)
        self.compute.floating_ips.get.assert_any_call(
            'unexist_floating_ip')
        self.compute.floating_ips.delete.assert_called_once_with(
            self.floating_ips[0].id
        )


class TestListFloatingIPCompute(TestFloatingIPCompute):

    # The floating ips to be list up
    floating_ips = compute_fakes.FakeFloatingIP.create_floating_ips(count=3)

    columns = (
        'ID',
        'Floating IP Address',
        'Fixed IP Address',
        'Server',
        'Pool',
    )

    data = []
    for ip in floating_ips:
        data.append((
            ip.id,
            ip.ip,
            ip.fixed_ip,
            ip.instance_id,
            ip.pool,
        ))

    def setUp(self):
        super(TestListFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.list.return_value = self.floating_ips

        # Get the command object to test
        self.cmd = fip.ListFloatingIP(self.app, None)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFloatingIPCompute(TestFloatingIPCompute):

    # The floating ip to display.
    floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        floating_ip.fixed_ip,
        floating_ip.id,
        floating_ip.instance_id,
        floating_ip.ip,
        floating_ip.pool,
    )

    def setUp(self):
        super(TestShowFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Return value of utils.find_resource()
        self.compute.floating_ips.get.return_value = self.floating_ip

        # Get the command object to test
        self.cmd = fip.ShowFloatingIP(self.app, None)

    def test_floating_ip_show(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
