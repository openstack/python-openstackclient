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

from openstackclient.network.v2 import l3_conntrack_helper
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestConntrackHelper(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.router = network_fakes.FakeRouter.create_one_router()
        self.network_client.find_router = mock.Mock(return_value=self.router)


class TestCreateL3ConntrackHelper(TestConntrackHelper):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id}
        self.ct_helper = (
            network_fakes.FakeL3ConntrackHelper.create_one_l3_conntrack_helper(
                attrs
            )
        )
        self.columns = ('helper', 'id', 'port', 'protocol', 'router_id')

        self.data = (
            self.ct_helper.helper,
            self.ct_helper.id,
            self.ct_helper.port,
            self.ct_helper.protocol,
            self.ct_helper.router_id,
        )
        self.network_client.create_conntrack_helper = mock.Mock(
            return_value=self.ct_helper
        )

        # Get the command object to test
        self.cmd = l3_conntrack_helper.CreateConntrackHelper(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            '--helper',
            'tftp',
            '--protocol',
            'udp',
            '--port',
            '69',
            self.router.id,
        ]

        verifylist = [
            ('helper', 'tftp'),
            ('protocol', 'udp'),
            ('port', 69),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_conntrack_helper.assert_called_once_with(
            self.router.id, **{'helper': 'tftp', 'protocol': 'udp', 'port': 69}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_wrong_options(self):
        arglist = [
            '--protocol',
            'udp',
            '--port',
            '69',
            self.router.id,
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            None,
        )


class TestDeleteL3ConntrackHelper(TestConntrackHelper):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id}
        self.ct_helper = (
            network_fakes.FakeL3ConntrackHelper.create_one_l3_conntrack_helper(
                attrs
            )
        )
        self.network_client.delete_conntrack_helper = mock.Mock(
            return_value=None
        )

        # Get the command object to test
        self.cmd = l3_conntrack_helper.DeleteConntrackHelper(self.app, None)

    def test_delete(self):
        arglist = [self.ct_helper.router_id, self.ct_helper.id]
        verifylist = [
            ('conntrack_helper_id', [self.ct_helper.id]),
            ('router', self.ct_helper.router_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.delete_conntrack_helper.assert_called_once_with(
            self.ct_helper.id, self.router.id, ignore_missing=False
        )
        self.assertIsNone(result)

    def test_delete_error(self):
        arglist = [self.router.id, self.ct_helper.id]
        verifylist = [
            ('conntrack_helper_id', [self.ct_helper.id]),
            ('router', self.router.id),
        ]
        self.network_client.delete_conntrack_helper.side_effect = Exception(
            'Error message'
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestListL3ConntrackHelper(TestConntrackHelper):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id}
        ct_helpers = (
            network_fakes.FakeL3ConntrackHelper.create_l3_conntrack_helpers(
                attrs, count=3
            )
        )
        self.columns = (
            'ID',
            'Router ID',
            'Helper',
            'Protocol',
            'Port',
        )
        self.data = []
        for ct_helper in ct_helpers:
            self.data.append(
                (
                    ct_helper.id,
                    ct_helper.router_id,
                    ct_helper.helper,
                    ct_helper.protocol,
                    ct_helper.port,
                )
            )
        self.network_client.conntrack_helpers = mock.Mock(
            return_value=ct_helpers
        )

        # Get the command object to test
        self.cmd = l3_conntrack_helper.ListConntrackHelper(self.app, None)

    def test_conntrack_helpers_list(self):
        arglist = [self.router.id]
        verifylist = [
            ('router', self.router.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.conntrack_helpers.assert_called_once_with(
            self.router.id
        )
        self.assertEqual(self.columns, columns)
        list_data = list(data)
        self.assertEqual(len(self.data), len(list_data))
        for index in range(len(list_data)):
            self.assertEqual(self.data[index], list_data[index])


class TestSetL3ConntrackHelper(TestConntrackHelper):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id}
        self.ct_helper = (
            network_fakes.FakeL3ConntrackHelper.create_one_l3_conntrack_helper(
                attrs
            )
        )
        self.network_client.update_conntrack_helper = mock.Mock(
            return_value=None
        )

        # Get the command object to test
        self.cmd = l3_conntrack_helper.SetConntrackHelper(self.app, None)

    def test_set_nothing(self):
        arglist = [
            self.router.id,
            self.ct_helper.id,
        ]
        verifylist = [
            ('router', self.router.id),
            ('conntrack_helper_id', self.ct_helper.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_conntrack_helper.assert_called_once_with(
            self.ct_helper.id, self.router.id
        )
        self.assertIsNone(result)

    def test_set_port(self):
        arglist = [
            self.router.id,
            self.ct_helper.id,
            '--port',
            '124',
        ]
        verifylist = [
            ('router', self.router.id),
            ('conntrack_helper_id', self.ct_helper.id),
            ('port', 124),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_conntrack_helper.assert_called_once_with(
            self.ct_helper.id, self.router.id, port=124
        )
        self.assertIsNone(result)


class TestShowL3ConntrackHelper(TestConntrackHelper):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id}
        self.ct_helper = (
            network_fakes.FakeL3ConntrackHelper.create_one_l3_conntrack_helper(
                attrs
            )
        )
        self.columns = ('helper', 'id', 'port', 'protocol', 'router_id')

        self.data = (
            self.ct_helper.helper,
            self.ct_helper.id,
            self.ct_helper.port,
            self.ct_helper.protocol,
            self.ct_helper.router_id,
        )
        self.network_client.get_conntrack_helper = mock.Mock(
            return_value=self.ct_helper
        )

        # Get the command object to test
        self.cmd = l3_conntrack_helper.ShowConntrackHelper(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_default_options(self):
        arglist = [
            self.router.id,
            self.ct_helper.id,
        ]
        verifylist = [
            ('router', self.router.id),
            ('conntrack_helper_id', self.ct_helper.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.get_conntrack_helper.assert_called_once_with(
            self.ct_helper.id, self.router.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
