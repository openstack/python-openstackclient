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

from openstackclient.network.v2.dynamic_routing import bgp_speaker
from openstackclient.tests.unit.network.v2.dynamic_routing import fakes
from openstackclient.tests.unit.network.v2 import fakes as test_fakes


class TestListBgpSpeaker(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._bgp_speakers = fakes.FakeBgpSpeaker.create_bgp_speakers()
        self.columns = ('ID', 'Name', 'Local AS', 'IP Version')
        self.data = []
        for _bgp_speaker in self._bgp_speakers:
            self.data.append(
                (
                    _bgp_speaker['id'],
                    _bgp_speaker['name'],
                    _bgp_speaker['local_as'],
                    _bgp_speaker['ip_version'],
                )
            )

        self.network_client.bgp_speakers.return_value = self._bgp_speakers

        # Get the command object to test
        self.cmd = bgp_speaker.ListBgpSpeaker(self.app, None)

    def test_bgp_speaker_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)
        self.network_client.bgp_speakers.assert_called_once_with(
            retrieve_all=True
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestDeleteBgpSpeaker(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self.network_client.delete_bgp_speaker.return_value = None
        self.network_client.find_bgp_speaker.return_value = mock.Mock(
            id=self._bgp_speaker.id
        )

        self.cmd = bgp_speaker.DeleteBgpSpeaker(self.app, None)

    def test_delete_bgp_speaker(self):
        arglist = [
            self._bgp_speaker['name'],
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgp_speaker.assert_called_once_with(
            self._bgp_speaker.id
        )
        self.assertIsNone(result)


class TestShowBgpSpeaker(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._one_bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self.data = (
            self._one_bgp_speaker['advertise_floating_ip_host_routes'],
            self._one_bgp_speaker['advertise_tenant_networks'],
            self._one_bgp_speaker['id'],
            self._one_bgp_speaker['ip_version'],
            self._one_bgp_speaker['local_as'],
            self._one_bgp_speaker['name'],
            self._one_bgp_speaker['networks'],
            self._one_bgp_speaker['peers'],
            self._one_bgp_speaker['tenant_id'],
        )
        self._bgp_speaker = self._one_bgp_speaker
        self._bgp_speaker_name = self._one_bgp_speaker['name']
        self.columns = (
            'advertise_floating_ip_host_routes',
            'advertise_tenant_networks',
            'id',
            'ip_version',
            'local_as',
            'name',
            'networks',
            'peers',
            'project_id',
        )

        self.network_client.find_bgp_speaker.return_value = self._bgp_speaker
        # Get the command object to test
        self.cmd = bgp_speaker.ShowBgpSpeaker(self.app, None)

    def test_bgp_speaker_show(self):
        arglist = [
            self._bgp_speaker_name,
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        data = self.cmd.take_action(parsed_args)
        self.network_client.find_bgp_speaker.assert_called_once_with(
            self._bgp_speaker.name, ignore_missing=False
        )
        self.assertEqual(self.columns, data[0])
        self.assertEqual(self.data, data[1])


class TestSetBgpSpeaker(test_fakes.TestNetworkV2):
    _one_bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    _bgp_speaker_name = _one_bgp_speaker['name']

    def setUp(self):
        super().setUp()
        self.network_client.update_bgp_speaker.return_value = None
        self.network_client.find_bgp_speaker.return_value = mock.Mock(
            id=self._one_bgp_speaker.id
        )

        self.cmd = bgp_speaker.SetBgpSpeaker(self.app, None)

    def test_set_bgp_speaker(self):
        arglist = [
            self._bgp_speaker_name,
            '--name',
            'noob',
        ]
        verifylist = [
            ('bgp_speaker', self._bgp_speaker_name),
            ('name', 'noob'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {'name': 'noob'}
        self.network_client.update_bgp_speaker.assert_called_once_with(
            self._one_bgp_speaker.id, **attrs
        )
        self.assertIsNone(result)
