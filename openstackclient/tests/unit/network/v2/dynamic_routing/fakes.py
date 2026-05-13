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

import uuid

from openstack.network.v2 import agent as _agent
from openstack.network.v2 import bgp_peer as _bgp_peer
from openstack.network.v2 import bgp_speaker as _bgp_speaker


class FakeBgpSpeaker:
    """Fake one or more bgp speakers."""

    @staticmethod
    def create_one_bgp_speaker(attrs=None):
        attrs = attrs or {}
        # Set default attributes.
        bgp_speaker_attrs = {
            'peers': [],
            'local_as': 200,
            'advertise_tenant_networks': True,
            'networks': [],
            'ip_version': 4,
            'advertise_floating_ip_host_routes': True,
            'id': uuid.uuid4().hex,
            'name': 'bgp-speaker-' + uuid.uuid4().hex,
            'tenant_id': uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        bgp_speaker_attrs.update(attrs)
        ret_bgp_speaker = _bgp_speaker.BgpSpeaker(**bgp_speaker_attrs)

        return ret_bgp_speaker

    @staticmethod
    def create_bgp_speakers(attrs=None, count=1):
        """Create multiple fake bgp speakers."""
        bgp_speakers = []
        for i in range(count):
            bgp_speaker = FakeBgpSpeaker.create_one_bgp_speaker(attrs)
            bgp_speakers.append(bgp_speaker)

        return bgp_speakers


class FakeBgpPeer:
    """Fake one or more bgp peers."""

    @staticmethod
    def create_one_bgp_peer(attrs=None):
        attrs = attrs or {}
        # Set default attributes.
        bgp_peer_attrs = {
            'auth_type': None,
            'peer_ip': '1.1.1.1',
            'remote_as': 100,
            'id': uuid.uuid4().hex,
            'name': 'bgp-peer-' + uuid.uuid4().hex,
            'tenant_id': uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        bgp_peer_attrs.update(attrs)
        ret_bgp_peer = _bgp_peer.BgpPeer(**bgp_peer_attrs)

        return ret_bgp_peer

    @staticmethod
    def create_bgp_peers(attrs=None, count=1):
        """Create one or multiple fake bgp peers."""
        bgp_peers = []
        for i in range(count):
            bgp_peer = FakeBgpPeer.create_one_bgp_peer(attrs)
            bgp_peers.append(bgp_peer)

        return bgp_peers


class FakeDRAgent:
    """Fake one or more dynamic routing agents."""

    @staticmethod
    def create_one_dragent(attrs=None):
        attrs = attrs or {}
        # Set default attributes.
        dragent_attrs = {
            'binary': 'neutron-bgp-dragent',
            'admin_state_up': True,
            'availability_zone': None,
            'alive': True,
            'topic': 'bgp_dragent',
            'host': 'network-' + uuid.uuid4().hex,
            'name': 'bgp-dragent-' + uuid.uuid4().hex,
            'agent_type': 'BGP dynamic routing agent',
            'id': uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        dragent_attrs.update(attrs)
        return _agent.Agent(**dragent_attrs)

    @staticmethod
    def create_dragents(attrs=None, count=1):
        """Create one or multiple fake dynamic routing agents."""
        agents = []
        for i in range(count):
            agent = FakeDRAgent.create_one_dragent(attrs)
            agents.append(agent)

        return agents
