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
#

import collections
from unittest import mock
import uuid

from openstack.network.v2 import vpn_endpoint_group as vpn_epg
from openstack.network.v2 import vpn_ike_policy as vpn_ikep
from openstack.network.v2 import vpn_ipsec_policy as vpn_ipsecp
from openstack.network.v2 import vpn_ipsec_site_connection as vpn_sitec
from openstack.network.v2 import vpn_service


class FakeVPNaaS:
    def create(self, attrs={}):
        """Create a fake vpnaas resources

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A OrderedDict faking the vpnaas resource
        """
        self.ordered.update(attrs)
        if 'IKEPolicy' == self.__class__.__name__:
            return vpn_ikep.VpnIkePolicy(**self.ordered)
        if 'IPSecPolicy' == self.__class__.__name__:
            return vpn_ipsecp.VpnIpsecPolicy(**self.ordered)
        if 'VPNService' == self.__class__.__name__:
            return vpn_service.VpnService(**self.ordered)
        if 'EndpointGroup' == self.__class__.__name__:
            return vpn_epg.VpnEndpointGroup(**self.ordered)

    def bulk_create(self, attrs=None, count=2):
        """Create multiple fake vpnaas resources

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of vpnaas resources to fake
        :return:
            A list of dictionaries faking the vpnaas resources
        """
        return [self.create(attrs=attrs) for i in range(0, count)]

    def get(self, attrs=None, count=2):
        """Get multiple fake vpnaas resources

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of vpnaas resources to fake
        :return:
            A list of dictionaries faking the vpnaas resource
        """
        if attrs is None:
            self.attrs = self.bulk_create(count=count)
        return mock.Mock(side_effect=attrs)


class IKEPolicy(FakeVPNaaS):
    """Fake one or more IKE policies"""

    def __init__(self):
        super().__init__()
        self.ordered = collections.OrderedDict(
            (
                ('id', 'ikepolicy-id-' + uuid.uuid4().hex),
                ('name', 'my-ikepolicy-' + uuid.uuid4().hex),
                ('auth_algorithm', 'sha1'),
                ('encryption_algorithm', 'aes-128'),
                ('ike_version', 'v1'),
                ('pfs', 'group5'),
                ('description', 'my-desc-' + uuid.uuid4().hex),
                ('phase1_negotiation_mode', 'main'),
                ('project_id', 'project-id-' + uuid.uuid4().hex),
                ('lifetime', {'units': 'seconds', 'value': 3600}),
            )
        )


class IPSecPolicy(FakeVPNaaS):
    """Fake one or more IPsec policies"""

    def __init__(self):
        super().__init__()
        self.ordered = collections.OrderedDict(
            (
                ('id', 'ikepolicy-id-' + uuid.uuid4().hex),
                ('name', 'my-ikepolicy-' + uuid.uuid4().hex),
                ('auth_algorithm', 'sha1'),
                ('encapsulation_mode', 'tunnel'),
                ('transform_protocol', 'esp'),
                ('encryption_algorithm', 'aes-128'),
                ('pfs', 'group5'),
                ('description', 'my-desc-' + uuid.uuid4().hex),
                ('project_id', 'project-id-' + uuid.uuid4().hex),
                ('lifetime', {'units': 'seconds', 'value': 3600}),
            )
        )


class VPNService(FakeVPNaaS):
    """Fake one or more VPN services"""

    def __init__(self):
        super().__init__()
        self.ordered = collections.OrderedDict(
            (
                ('id', 'vpnservice-id-' + uuid.uuid4().hex),
                ('name', 'my-vpnservice-' + uuid.uuid4().hex),
                ('router_id', 'router-id-' + uuid.uuid4().hex),
                ('subnet_id', 'subnet-id-' + uuid.uuid4().hex),
                ('flavor_id', 'flavor-id-' + uuid.uuid4().hex),
                ('admin_state_up', True),
                ('status', 'ACTIVE'),
                ('description', 'my-desc-' + uuid.uuid4().hex),
                ('project_id', 'project-id-' + uuid.uuid4().hex),
                ('external_v4_ip', '192.0.2.42'),
                ('external_v6_ip', '2001:0db8:207a:4a3a:053b:6fab:7df9:1afd'),
            )
        )


class EndpointGroup(FakeVPNaaS):
    """Fake one or more Endpoint Groups"""

    def __init__(self):
        super().__init__()
        self.ordered = collections.OrderedDict(
            (
                ('id', 'ep-group-id-' + uuid.uuid4().hex),
                ('name', 'my-ep-group-' + uuid.uuid4().hex),
                ('type', 'cidr'),
                ('endpoints', ['10.0.0.0/24', '20.0.0.0/24']),
                ('description', 'my-desc-' + uuid.uuid4().hex),
                ('project_id', 'project-id-' + uuid.uuid4().hex),
            )
        )


class IPsecSiteConnection:
    """Fake one or more IPsec site connections"""

    @staticmethod
    def create_conn(attrs=None):
        """Create a fake IPsec conn.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A Dictionary with id, name, peer_address, auth_mode, status,
            project_id, peer_cidrs, vpnservice_id, ipsecpolicy_id,
            ikepolicy_id, mtu, initiator, admin_state_up, description,
            psk, route_mode, local_id, peer_id, local_ep_group_id,
            peer_ep_group_id
        """
        attrs = attrs or {}

        # Set default attributes.
        conn_attrs = {
            'id': 'ipsec-site-conn-id-' + uuid.uuid4().hex,
            'name': 'my-ipsec-site-conn-' + uuid.uuid4().hex,
            'peer_address': '192.168.2.10',
            'auth_mode': '',
            'status': '',
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'peer_cidrs': [],
            'vpnservice_id': 'vpnservice-id-' + uuid.uuid4().hex,
            'ipsecpolicy_id': 'ipsecpolicy-id-' + uuid.uuid4().hex,
            'ikepolicy_id': 'ikepolicy-id-' + uuid.uuid4().hex,
            'mtu': 1500,
            'initiator': 'bi-directional',
            'admin_state_up': True,
            'description': 'my-vpn-connection',
            'psk': 'abcd',
            'route_mode': '',
            'local_id': '',
            'peer_id': '192.168.2.10',
            'local_ep_group_id': 'local-ep-group-id-' + uuid.uuid4().hex,
            'peer_ep_group_id': 'peer-ep-group-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        conn_attrs.update(attrs)
        return vpn_sitec.VpnIPSecSiteConnection(**conn_attrs)
