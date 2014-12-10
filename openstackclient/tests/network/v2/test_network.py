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

import copy
import mock

from openstackclient.common import exceptions
from openstackclient.network.v2 import network
from openstackclient.tests.network import common

RESOURCE = 'network'
RESOURCES = 'networks'
FAKE_ID = 'iditty'
FAKE_NAME = 'noo'
RECORD = {
    'id': FAKE_ID,
    'name': FAKE_NAME,
    'router:external': True,
    'subnets': ['a', 'b'],
}
COLUMNS = ['id', 'name', 'subnets']
RESPONSE = {RESOURCE: RECORD}
FILTERED = [('id', 'name', 'router:external', 'subnets'),
            (FAKE_ID, FAKE_NAME, True, 'a, b')]


class TestCreateNetwork(common.TestNetworkBase):
    def test_create_no_options(self):
        arglist = [
            FAKE_NAME,
        ]
        verifylist = [
            ('name', FAKE_NAME),
            ('admin_state', True),
            ('shared', None),
        ]
        mocker = mock.Mock(return_value=copy.deepcopy(RESPONSE))
        self.app.client_manager.network.create_network = mocker
        cmd = network.CreateNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = list(cmd.take_action(parsed_args))

        mocker.assert_called_with({
            RESOURCE: {
                'admin_state_up': True,
                'name': FAKE_NAME,
            }
        })
        self.assertEqual(FILTERED, result)

    def test_create_all_options(self):
        arglist = [
            "--disable",
            "--share",
            FAKE_NAME,
        ] + self.given_show_options
        verifylist = [
            ('admin_state', False),
            ('shared', True),
            ('name', FAKE_NAME),
        ] + self.then_show_options
        mocker = mock.Mock(return_value=copy.deepcopy(RESPONSE))
        self.app.client_manager.network.create_network = mocker
        cmd = network.CreateNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = list(cmd.take_action(parsed_args))

        mocker.assert_called_with({
            RESOURCE: {
                'admin_state_up': False,
                'name': FAKE_NAME,
                'shared': True,
            }
        })
        self.assertEqual(FILTERED, result)

    def test_create_other_options(self):
        arglist = [
            "--enable",
            "--no-share",
            FAKE_NAME,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', False),
            ('name', FAKE_NAME),
        ]
        mocker = mock.Mock(return_value=copy.deepcopy(RESPONSE))
        self.app.client_manager.network.create_network = mocker
        cmd = network.CreateNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = list(cmd.take_action(parsed_args))

        mocker.assert_called_with({
            RESOURCE: {
                'admin_state_up': True,
                'name': FAKE_NAME,
                'shared': False,
            }
        })
        self.assertEqual(FILTERED, result)


class TestDeleteNetwork(common.TestNetworkBase):
    def test_delete(self):
        arglist = [
            FAKE_NAME,
        ]
        verifylist = [
            ('networks', [FAKE_NAME]),
        ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        mocker = mock.Mock(return_value=None)
        self.app.client_manager.network.delete_network = mocker
        cmd = network.DeleteNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        mocker.assert_called_with(FAKE_ID)
        self.assertEqual(None, result)


class TestListNetwork(common.TestNetworkBase):
    def test_list_no_options(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('dhcp', None),
            ('external', False),
        ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        cmd = network.ListNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        lister.assert_called_with()
        self.assertEqual(COLUMNS, result[0])
        self.assertEqual((FAKE_ID, FAKE_NAME, 'a, b'), next(result[1]))
        self.assertRaises(StopIteration, next, result[1])

    def test_list_long(self):
        arglist = ['--long']
        verifylist = [
            ('long', True),
            ('dhcp', None),
            ('external', False),
        ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        cmd = network.ListNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        lister.assert_called_with()
        headings = ['id', 'name', 'router:external', 'subnets']
        self.assertEqual(headings, result[0])
        data = (FAKE_ID, FAKE_NAME, True, 'a, b')
        self.assertEqual(data, next(result[1]))
        self.assertRaises(StopIteration, next, result[1])

    def test_list_dhcp(self):
        arglist = [
            '--dhcp',
            'dhcpid',
        ] + self.given_list_options
        verifylist = [
            ('dhcp', 'dhcpid'),
        ] + self.then_list_options
        fake_dhcp_data = [{'id': '1'}, {'id': '2'}]
        fake_dhcp_response = {'networks_on_dhcp_agent': fake_dhcp_data}
        lister = mock.Mock(return_value=fake_dhcp_response)
        netty = self.app.client_manager.network
        netty.list_networks_on_dhcp_agent = lister
        cmd = network.ListNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        lister.assert_called_with(dhcp_agent='dhcpid')
        self.assertEqual(['id'], result[0])
        self.assertEqual(('1',), next(result[1]))
        self.assertEqual(('2',), next(result[1]))
        self.assertRaises(StopIteration, next, result[1])

    def test_list_external(self):
        arglist = ['--external', '-c', 'id']
        verifylist = [('external', True)]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        cmd = network.ListNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        lister.assert_called_with(**{'router:external': True})
        self.assertEqual(['id'], result[0])
        self.assertEqual((FAKE_ID,), next(result[1]))
        self.assertRaises(StopIteration, next, result[1])


class TestSetNetwork(common.TestNetworkBase):
    def test_set_this(self):
        arglist = [
            FAKE_NAME,
            '--enable',
            '--name', 'noob',
            '--share',
        ]
        verifylist = [
            ('identifier', FAKE_NAME),
            ('admin_state', True),
            ('name', 'noob'),
            ('shared', True),
        ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        mocker = mock.Mock(return_value=None)
        self.app.client_manager.network.update_network = mocker
        cmd = network.SetNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        exp = {'admin_state_up': True, 'name': 'noob', 'shared': True}
        exp_record = {RESOURCE: exp}
        mocker.assert_called_with(FAKE_ID, exp_record)
        self.assertEqual(None, result)

    def test_set_that(self):
        arglist = [
            FAKE_NAME,
            '--disable',
            '--no-share',
        ]
        verifylist = [
            ('identifier', FAKE_NAME),
            ('admin_state', False),
            ('shared', False),
        ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        mocker = mock.Mock(return_value=None)
        self.app.client_manager.network.update_network = mocker
        cmd = network.SetNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = cmd.take_action(parsed_args)

        exp = {'admin_state_up': False, 'shared': False}
        exp_record = {RESOURCE: exp}
        mocker.assert_called_with(FAKE_ID, exp_record)
        self.assertEqual(None, result)

    def test_set_nothing(self):
        arglist = [FAKE_NAME, ]
        verifylist = [('identifier', FAKE_NAME), ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        mocker = mock.Mock(return_value=None)
        self.app.client_manager.network.update_network = mocker
        cmd = network.SetNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, cmd.take_action,
                          parsed_args)


class TestShowNetwork(common.TestNetworkBase):
    def test_show_no_options(self):
        arglist = [
            FAKE_NAME,
        ]
        verifylist = [
            ('identifier', FAKE_NAME),
        ]
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        mocker = mock.Mock(return_value=copy.deepcopy(RESPONSE))
        self.app.client_manager.network.show_network = mocker
        cmd = network.ShowNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = list(cmd.take_action(parsed_args))

        mocker.assert_called_with(FAKE_ID)
        self.assertEqual(FILTERED, result)

    def test_show_all_options(self):
        arglist = [FAKE_NAME] + self.given_show_options
        verifylist = [('identifier', FAKE_NAME)] + self.then_show_options
        lister = mock.Mock(return_value={RESOURCES: [RECORD]})
        self.app.client_manager.network.list_networks = lister
        mocker = mock.Mock(return_value=copy.deepcopy(RESPONSE))
        self.app.client_manager.network.show_network = mocker
        cmd = network.ShowNetwork(self.app, self.namespace)

        parsed_args = self.check_parser(cmd, arglist, verifylist)
        result = list(cmd.take_action(parsed_args))

        mocker.assert_called_with(FAKE_ID)
        self.assertEqual(FILTERED, result)
