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

from openstackclient.network.v2.dynamic_routing import bgp_dragent
from openstackclient.tests.unit.network.v2.dynamic_routing import fakes
from openstackclient.tests.unit.network.v2 import fakes as test_fakes


class TestAddBgpSpeakerToDRAgent(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self._bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
        self._bgp_dragent = fakes.FakeDRAgent.create_one_dragent()
        self._bgp_speaker_id = self._bgp_speaker['id']
        self._bgp_dragent_id = self._bgp_dragent['id']

        # Get the command object to test
        self.cmd = bgp_dragent.AddBgpSpeakerToDRAgent(self.app, None)

    def test_add_bgp_speaker_to_dragent(self):
        arglist = [
            self._bgp_dragent_id,
            self._bgp_speaker_id,
        ]
        verifylist = [
            ('dragent_id', self._bgp_dragent_id),
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.network_client.find_bgp_speaker.return_value = mock.Mock(
            id=self._bgp_speaker_id
        )
        self.network_client.add_bgp_speaker_to_dragent.return_value = None

        result = self.cmd.take_action(parsed_args)
        self.network_client.add_bgp_speaker_to_dragent.assert_called_once_with(
            self._bgp_dragent_id, self._bgp_speaker_id
        )
        self.assertIsNone(result)


class TestRemoveBgpSpeakerFromDRAgent(test_fakes.TestNetworkV2):
    _bgp_speaker = fakes.FakeBgpSpeaker.create_one_bgp_speaker()
    _bgp_dragent = fakes.FakeDRAgent.create_one_dragent()
    _bgp_speaker_id = _bgp_speaker['id']
    _bgp_dragent_id = _bgp_dragent['id']

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = bgp_dragent.RemoveBgpSpeakerFromDRAgent(self.app, None)

    def test_remove_bgp_speaker_from_dragent(self):
        arglist = [
            self._bgp_dragent_id,
            self._bgp_speaker_id,
        ]
        verifylist = [
            ('dragent_id', self._bgp_dragent_id),
            ('bgp_speaker', self._bgp_speaker_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.network_client.find_bgp_speaker.return_value = mock.Mock(
            id=self._bgp_speaker_id
        )
        self.network_client.remove_bgp_speaker_from_dragent.return_value = None

        result = self.cmd.take_action(parsed_args)
        self.network_client.remove_bgp_speaker_from_dragent.assert_called_once_with(
            self._bgp_dragent_id, self._bgp_speaker_id
        )
        self.assertIsNone(result)
