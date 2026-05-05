# Copyright (c) 2016 Juniper Networks Inc.
# All Rights Reserved.
#
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


from openstack.network.v2 import bgpvpn as _bgpvpn
from openstack.network.v2 import bgpvpn_network_association as _net_assoc
from openstack.network.v2 import bgpvpn_port_association as _port_assoc
from openstack.network.v2 import bgpvpn_router_association as _router_assoc
from openstack import resource as sdk_resource

from openstackclient.tests.unit.network.v2 import fakes as test_fakes


_FAKE_PROJECT_ID = 'fake_project_id'


class TestNeutronClientBgpvpn(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()


def create_one_bgpvpn(attrs=None):
    """Create a fake BGP VPN."""

    attrs = attrs or {}

    # Set default attributes.
    bgpvpn_attrs = {
        'id': 'fake_bgpvpn_id',
        'tenant_id': _FAKE_PROJECT_ID,
        'name': '',
        'type': 'l3',
        'route_targets': [],
        'import_targets': [],
        'export_targets': [],
        'route_distinguishers': [],
        'networks': [],
        'routers': [],
        'ports': [],
        'vni': 100,
        'local_pref': 777,
    }

    # Overwrite default attributes.
    bgpvpn_attrs.update(attrs)
    return _bgpvpn.BgpVpn(**bgpvpn_attrs)


def create_bgpvpns(attrs=None, count=1):
    """Create multiple fake BGP VPN."""

    bgpvpns = []
    for i in range(0, count):
        if attrs is None:
            attrs = {'id': 'fake_id{i}'}
        elif getattr(attrs, 'id', None) is None:
            attrs['id'] = 'fake_id{i}'
        bgpvpns.append(create_one_bgpvpn(attrs))

    return bgpvpns


def create_one_resource(attrs=None):
    """Create a fake resource."""
    attrs = attrs or {}

    res_attrs = {
        'id': 'fake_resource_id',
    }

    res_attrs.update(attrs)
    return sdk_resource.Resource(**res_attrs)


def create_resources(attrs=None, count=1):
    """Create multiple fake resources."""

    resources = []
    for i in range(0, count):
        if attrs is None:
            attrs = {'id': 'fake_id{i}'}
        elif getattr(attrs, 'id', None) is None:
            attrs['id'] = 'fake_id{i}'
        resources.append(create_one_resource(attrs))

    return resources


def create_one_network_association(attrs=None):
    """Create a fake network association."""
    attrs = attrs or {}
    assoc_attrs = {
        'id': 'fake_association_id',
        'network_id': 'fake_resource_id',
        'tenant_id': _FAKE_PROJECT_ID,
    }
    assoc_attrs.update(attrs)
    return _net_assoc.BgpVpnNetworkAssociation(**assoc_attrs)


def create_network_associations(count=1):
    """Create multiple fake network associations."""
    assocs = []
    for idx in range(count):
        assocs.append(
            {
                'id': f'fake_association_id{idx}',
                'network_id': f'fake_resource_id{idx}',
                'tenant_id': _FAKE_PROJECT_ID,
            }
        )
    return assocs


def create_one_router_association(attrs=None):
    """Create a fake router association."""
    attrs = attrs or {}
    assoc_attrs = {
        'id': 'fake_association_id',
        'router_id': 'fake_resource_id',
        'tenant_id': _FAKE_PROJECT_ID,
    }
    assoc_attrs.update(attrs)
    return _router_assoc.BgpVpnRouterAssociation(**assoc_attrs)


def create_router_associations(count=1):
    """Create multiple fake router associations."""
    assocs = []
    for idx in range(count):
        assocs.append(
            {
                'id': f'fake_association_id{idx}',
                'router_id': f'fake_resource_id{idx}',
                'tenant_id': _FAKE_PROJECT_ID,
            }
        )
    return assocs


def create_one_port_association(attrs=None):
    """Create a fake port association."""
    attrs = attrs or {}
    assoc_attrs = {
        'id': 'fake_association_id',
        'port_id': 'fake_resource_id',
        'tenant_id': _FAKE_PROJECT_ID,
        'routes': [],
    }
    assoc_attrs.update(attrs)
    return _port_assoc.BgpVpnPortAssociation(**assoc_attrs)


def create_port_associations(count=1):
    """Create multiple fake port associations."""
    assocs = []
    for idx in range(count):
        assocs.append(
            {
                'id': f'fake_association_id{idx}',
                'port_id': f'fake_resource_id{idx}',
                'tenant_id': _FAKE_PROJECT_ID,
                'routes': [],
            }
        )
    return assocs
