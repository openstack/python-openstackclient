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

from openstackclient.network.v2.dynamic_routing import bgp_peer
from openstackclient.tests.unit.network.v2.dynamic_routing import fakes
from openstackclient.tests.unit.network.v2 import fakes as test_fakes


class TestListBgpPeer(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._bgp_peers = fakes.FakeBgpPeer.create_bgp_peers(count=1)
        self.columns = ('ID', 'Name', 'Peer IP', 'Remote AS')
        self.data = []
        for _bgp_peer in self._bgp_peers:
            self.data.append(
                (
                    _bgp_peer['id'],
                    _bgp_peer['name'],
                    _bgp_peer['peer_ip'],
                    _bgp_peer['remote_as'],
                )
            )

        self.network_client.bgp_peers.return_value = self._bgp_peers

        # Get the command object to test
        self.cmd = bgp_peer.ListBgpPeer(self.app, None)

    def test_bgp_peer_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.bgp_peers.assert_called_once_with(
            retrieve_all=True
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestDeleteBgpPeer(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._bgp_peer = fakes.FakeBgpPeer.create_one_bgp_peer()

        self.network_client.delete_bgp_peer.return_value = None
        self.network_client.find_bgp_peer.return_value = mock.Mock(
            id=self._bgp_peer.id
        )
        self.cmd = bgp_peer.DeleteBgpPeer(self.app, None)

    def test_delete_bgp_peer(self):
        arglist = [
            self._bgp_peer['name'],
        ]
        verifylist = [
            ('bgp_peer', self._bgp_peer['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgp_peer.assert_called_once_with(
            self._bgp_peer.id
        )
        self.assertIsNone(result)


class TestShowBgpPeer(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._one_bgp_peer = fakes.FakeBgpPeer.create_one_bgp_peer()
        self.data = (
            self._one_bgp_peer['auth_type'],
            self._one_bgp_peer['id'],
            self._one_bgp_peer['name'],
            self._one_bgp_peer['peer_ip'],
            self._one_bgp_peer['tenant_id'],
            self._one_bgp_peer['remote_as'],
        )
        self._bgp_peer = self._one_bgp_peer
        self._bgp_peer_name = self._one_bgp_peer['name']
        self.columns = (
            'auth_type',
            'id',
            'name',
            'peer_ip',
            'project_id',
            'remote_as',
        )

        self.network_client.find_bgp_peer.return_value = self._bgp_peer
        # Get the command object to test
        self.cmd = bgp_peer.ShowBgpPeer(self.app, None)

    def test_bgp_peer_show(self):
        arglist = [
            self._bgp_peer_name,
        ]
        verifylist = [
            ('bgp_peer', self._bgp_peer_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        data = self.cmd.take_action(parsed_args)
        self.network_client.find_bgp_peer.assert_called_once_with(
            self._bgp_peer.name, ignore_missing=False
        )
        self.assertEqual(self.columns, data[0])
        self.assertEqual(self.data, data[1])


class TestSetBgpPeer(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._one_bgp_peer = fakes.FakeBgpPeer.create_one_bgp_peer()
        self._bgp_peer_name = self._one_bgp_peer['name']

        self.network_client.update_bgp_peer.return_value = None
        self.network_client.find_bgp_peer.return_value = mock.Mock(
            id=self._one_bgp_peer.id
        )

        self.cmd = bgp_peer.SetBgpPeer(self.app, None)

    def test_set_bgp_peer(self):
        arglist = [
            self._bgp_peer_name,
            '--name',
            'noob',
        ]
        verifylist = [
            ('bgp_peer', self._bgp_peer_name),
            ('name', 'noob'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'name': 'noob', 'password': None}
        self.network_client.update_bgp_peer.assert_called_once_with(
            self._one_bgp_peer.id, **attrs
        )
        self.assertIsNone(result)
