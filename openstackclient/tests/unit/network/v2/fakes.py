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

import argparse
import copy
from random import choice
from random import randint
import uuid

import mock

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit import utils


QUOTA = {
    "subnet": 10,
    "network": 10,
    "floatingip": 50,
    "subnetpool": -1,
    "security_group_rule": 100,
    "security_group": 10,
    "router": 10,
    "rbac_policy": -1,
    "port": 50,
    "vip": 10,
    "member": 10,
    "healthmonitor": 10,
    "l7policy": 5,
}

RULE_TYPE_BANDWIDTH_LIMIT = 'bandwidth-limit'
RULE_TYPE_DSCP_MARKING = 'dscp-marking'
RULE_TYPE_MINIMUM_BANDWIDTH = 'minimum-bandwidth'
VALID_QOS_RULES = [RULE_TYPE_BANDWIDTH_LIMIT,
                   RULE_TYPE_DSCP_MARKING,
                   RULE_TYPE_MINIMUM_BANDWIDTH]
VALID_DSCP_MARKS = [0, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32,
                    34, 36, 38, 40, 46, 48, 56]


class FakeNetworkV2Client(object):

    def __init__(self, **kwargs):
        self.session = mock.Mock()
        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})


class TestNetworkV2(utils.TestCommand):

    def setUp(self):
        super(TestNetworkV2, self).setUp()

        self.namespace = argparse.Namespace()

        self.app.client_manager.session = mock.Mock()

        self.app.client_manager.network = FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.sdk_connection = mock.Mock()
        self.app.client_manager.sdk_connection.network = \
            self.app.client_manager.network

        self.app.client_manager.identity = (
            identity_fakes_v3.FakeIdentityv3Client(
                endpoint=fakes.AUTH_URL,
                token=fakes.AUTH_TOKEN,
            )
        )


class FakeAddressScope(object):
    """Fake one or more address scopes."""

    @staticmethod
    def create_one_address_scope(attrs=None):
        """Create a fake address scope.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        address_scope_attrs = {
            'name': 'address-scope-name-' + uuid.uuid4().hex,
            'id': 'address-scope-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'shared': False,
            'ip_version': 4,
        }

        # Overwrite default attributes.
        address_scope_attrs.update(attrs)

        address_scope = fakes.FakeResource(
            info=copy.deepcopy(address_scope_attrs),
            loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        address_scope.is_shared = address_scope_attrs['shared']
        address_scope.project_id = address_scope_attrs['tenant_id']

        return address_scope

    @staticmethod
    def create_address_scopes(attrs=None, count=2):
        """Create multiple fake address scopes.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of address scopes to fake
        :return:
            A list of FakeResource objects faking the address scopes
        """
        address_scopes = []
        for i in range(0, count):
            address_scopes.append(
                FakeAddressScope.create_one_address_scope(attrs))

        return address_scopes

    @staticmethod
    def get_address_scopes(address_scopes=None, count=2):
        """Get an iterable Mock object with a list of faked address scopes.

        If address scopes list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List address_scopes:
            A list of FakeResource objects faking address scopes
        :param int count:
            The number of address scopes to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            address scopes
        """
        if address_scopes is None:
            address_scopes = FakeAddressScope.create_address_scopes(count)
        return mock.Mock(side_effect=address_scopes)


class FakeAutoAllocatedTopology(object):
    """Fake Auto Allocated Topology"""

    @staticmethod
    def create_one_topology(attrs=None):
        attrs = attrs or {}

        auto_allocated_topology_attrs = {
            'id': 'network-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
        }

        auto_allocated_topology_attrs.update(attrs)

        auto_allocated_topology = fakes.FakeResource(
            info=copy.deepcopy(auto_allocated_topology_attrs),
            loaded=True)

        auto_allocated_topology.project_id = auto_allocated_topology_attrs[
            'tenant_id'
        ]

        return auto_allocated_topology


class FakeAvailabilityZone(object):
    """Fake one or more network availability zones (AZs)."""

    @staticmethod
    def create_one_availability_zone(attrs=None):
        """Create a fake AZ.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, state, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        availability_zone = {
            'name': uuid.uuid4().hex,
            'state': 'available',
            'resource': 'network',
        }

        # Overwrite default attributes.
        availability_zone.update(attrs)

        availability_zone = fakes.FakeResource(
            info=copy.deepcopy(availability_zone),
            loaded=True)
        return availability_zone

    @staticmethod
    def create_availability_zones(attrs=None, count=2):
        """Create multiple fake AZs.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of AZs to fake
        :return:
            A list of FakeResource objects faking the AZs
        """
        availability_zones = []
        for i in range(0, count):
            availability_zone = \
                FakeAvailabilityZone.create_one_availability_zone(attrs)
            availability_zones.append(availability_zone)

        return availability_zones


class FakeIPAvailability(object):
    """Fake one or more network ip availabilities."""

    @staticmethod
    def create_one_ip_availability(attrs=None):
        """Create a fake list with ip availability stats of a network.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with network_name, network_id, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        network_ip_attrs = {
            'network_id': 'network-id-' + uuid.uuid4().hex,
            'network_name': 'network-name-' + uuid.uuid4().hex,
            'tenant_id': '',
            'subnet_ip_availability': [],
            'total_ips': 254,
            'used_ips': 6,
        }
        network_ip_attrs.update(attrs)

        network_ip_availability = fakes.FakeResource(
            info=copy.deepcopy(network_ip_attrs),
            loaded=True)
        network_ip_availability.project_id = network_ip_attrs['tenant_id']

        return network_ip_availability

    @staticmethod
    def create_ip_availability(count=2):
        """Create fake list of ip availability stats of multiple networks.

        :param int count:
            The number of networks to fake
        :return:
            A list of FakeResource objects faking network ip availability stats
        """
        network_ip_availabilities = []
        for i in range(0, count):
            network_ip_availability = \
                FakeIPAvailability.create_one_ip_availability()
            network_ip_availabilities.append(network_ip_availability)

        return network_ip_availabilities


class FakeExtension(object):
    """Fake one or more extension."""

    @staticmethod
    def create_one_extension(attrs=None):
        """Create a fake extension.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, namespace, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        extension_info = {
            'name': 'name-' + uuid.uuid4().hex,
            'namespace': 'http://docs.openstack.org/network/',
            'description': 'description-' + uuid.uuid4().hex,
            'updated': '2013-07-09T12:00:0-00:00',
            'alias': 'Dystopian',
            'links': '[{"href":''"https://github.com/os/network", "type"}]',
        }

        # Overwrite default attributes.
        extension_info.update(attrs)

        extension = fakes.FakeResource(
            info=copy.deepcopy(extension_info),
            loaded=True)
        return extension


class FakeNetwork(object):
    """Fake one or more networks."""

    @staticmethod
    def create_one_network(attrs=None):
        """Create a fake network.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        network_attrs = {
            'id': 'network-id-' + uuid.uuid4().hex,
            'name': 'network-name-' + uuid.uuid4().hex,
            'status': 'ACTIVE',
            'description': 'network-description-' + uuid.uuid4().hex,
            'dns_domain': 'example.org.',
            'mtu': '1350',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'admin_state_up': True,
            'shared': False,
            'subnets': ['a', 'b'],
            'provider:network_type': 'vlan',
            'provider:physical_network': 'physnet1',
            'provider:segmentation_id': "400",
            'router:external': True,
            'availability_zones': [],
            'availability_zone_hints': [],
            'is_default': False,
            'port_security_enabled': True,
            'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
            'ipv4_address_scope': 'ipv4' + uuid.uuid4().hex,
            'ipv6_address_scope': 'ipv6' + uuid.uuid4().hex,
            'tags': [],
        }

        # Overwrite default attributes.
        network_attrs.update(attrs)

        network = fakes.FakeResource(info=copy.deepcopy(network_attrs),
                                     loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        network.project_id = network_attrs['tenant_id']
        network.is_router_external = network_attrs['router:external']
        network.is_admin_state_up = network_attrs['admin_state_up']
        network.is_port_security_enabled = \
            network_attrs['port_security_enabled']
        network.subnet_ids = network_attrs['subnets']
        network.is_shared = network_attrs['shared']
        network.is_tags = network_attrs['tags']
        network.provider_network_type = \
            network_attrs['provider:network_type']
        network.provider_physical_network = \
            network_attrs['provider:physical_network']
        network.provider_segmentation_id = \
            network_attrs['provider:segmentation_id']
        network.ipv4_address_scope_id = \
            network_attrs['ipv4_address_scope']
        network.ipv6_address_scope_id = \
            network_attrs['ipv6_address_scope']

        return network

    @staticmethod
    def create_networks(attrs=None, count=2):
        """Create multiple fake networks.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of networks to fake
        :return:
            A list of FakeResource objects faking the networks
        """
        networks = []
        for i in range(0, count):
            networks.append(FakeNetwork.create_one_network(attrs))

        return networks

    @staticmethod
    def get_networks(networks=None, count=2):
        """Get an iterable Mock object with a list of faked networks.

        If networks list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List networks:
            A list of FakeResource objects faking networks
        :param int count:
            The number of networks to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            networks
        """
        if networks is None:
            networks = FakeNetwork.create_networks(count)
        return mock.Mock(side_effect=networks)


class FakeNetworkFlavor(object):
    """Fake Network Flavor."""

    @staticmethod
    def create_one_network_flavor(attrs=None):
        """Create a fake network flavor.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object faking the network flavor
        """
        attrs = attrs or {}

        fake_uuid = uuid.uuid4().hex
        network_flavor_attrs = {
            'description': 'network-flavor-description-' + fake_uuid,
            'enabled': True,
            'id': 'network-flavor-id-' + fake_uuid,
            'name': 'network-flavor-name-' + fake_uuid,
            'service_type': 'vpn',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        network_flavor_attrs.update(attrs)

        network_flavor = fakes.FakeResource(
            info=copy.deepcopy(network_flavor_attrs),
            loaded=True
        )

        network_flavor.project_id = network_flavor_attrs['tenant_id']
        network_flavor.is_enabled = network_flavor_attrs['enabled']

        return network_flavor

    @staticmethod
    def create_flavor(attrs=None, count=2):
        """Create multiple fake network flavors.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of network flavors to fake
        :return:
            A list of FakeResource objects faking the network falvors
        """
        network_flavors = []
        for i in range(0, count):
            network_flavors.append(
                FakeNetworkFlavor.create_one_network_flavor(attrs)
            )
        return network_flavors

    @staticmethod
    def get_flavor(network_flavors=None, count=2):
        """Get a list of flavors."""
        if network_flavors is None:
            network_flavors = (FakeNetworkFlavor.create_flavor(count))
        return mock.Mock(side_effect=network_flavors)


class FakeNetworkSegment(object):
    """Fake one or more network segments."""

    @staticmethod
    def create_one_network_segment(attrs=None):
        """Create a fake network segment.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object faking the network segment
        """
        attrs = attrs or {}

        # Set default attributes.
        fake_uuid = uuid.uuid4().hex
        network_segment_attrs = {
            'description': 'network-segment-description-' + fake_uuid,
            'id': 'network-segment-id-' + fake_uuid,
            'name': 'network-segment-name-' + fake_uuid,
            'network_id': 'network-id-' + fake_uuid,
            'network_type': 'vlan',
            'physical_network': 'physical-network-name-' + fake_uuid,
            'segmentation_id': 1024,
        }

        # Overwrite default attributes.
        network_segment_attrs.update(attrs)

        network_segment = fakes.FakeResource(
            info=copy.deepcopy(network_segment_attrs),
            loaded=True
        )

        return network_segment

    @staticmethod
    def create_network_segments(attrs=None, count=2):
        """Create multiple fake network segments.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of network segments to fake
        :return:
            A list of FakeResource objects faking the network segments
        """
        network_segments = []
        for i in range(0, count):
            network_segments.append(
                FakeNetworkSegment.create_one_network_segment(attrs)
            )
        return network_segments


class FakeNetworkSegmentRange(object):
    """Fake one or more network segment ranges."""

    @staticmethod
    def create_one_network_segment_range(attrs=None):
        """Create a fake network segment range.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object faking the network segment range
        """
        attrs = attrs or {}

        # Set default attributes.
        fake_uuid = uuid.uuid4().hex
        network_segment_range_attrs = {
            'id': 'network-segment-range-id-' + fake_uuid,
            'name': 'network-segment-name-' + fake_uuid,
            'default': False,
            'shared': False,
            'project_id': 'project-id-' + fake_uuid,
            'network_type': 'vlan',
            'physical_network': 'physical-network-name-' + fake_uuid,
            'minimum': 100,
            'maximum': 106,
            'used': {104: '3312e4ba67864b2eb53f3f41432f8efc',
                     106: '3312e4ba67864b2eb53f3f41432f8efc'},
            'available': [100, 101, 102, 103, 105],
        }

        # Overwrite default attributes.
        network_segment_range_attrs.update(attrs)

        network_segment_range = fakes.FakeResource(
            info=copy.deepcopy(network_segment_range_attrs),
            loaded=True
        )

        return network_segment_range

    @staticmethod
    def create_network_segment_ranges(attrs=None, count=2):
        """Create multiple fake network segment ranges.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of network segment ranges to fake
        :return:
            A list of FakeResource objects faking the network segment ranges
        """
        network_segment_ranges = []
        for i in range(0, count):
            network_segment_ranges.append(
                FakeNetworkSegmentRange.create_one_network_segment_range(attrs)
            )
        return network_segment_ranges


class FakePort(object):
    """Fake one or more ports."""

    @staticmethod
    def create_one_port(attrs=None):
        """Create a fake port.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        port_attrs = {
            'admin_state_up': True,
            'allowed_address_pairs': [{}],
            'binding:host_id': 'binding-host-id-' + uuid.uuid4().hex,
            'binding:profile': {},
            'binding:vif_details': {},
            'binding:vif_type': 'ovs',
            'binding:vnic_type': 'normal',
            'data_plane_status': None,
            'description': 'description-' + uuid.uuid4().hex,
            'device_id': 'device-id-' + uuid.uuid4().hex,
            'device_owner': 'compute:nova',
            'dns_assignment': [{}],
            'dns_domain': 'dns-domain-' + uuid.uuid4().hex,
            'dns_name': 'dns-name-' + uuid.uuid4().hex,
            'extra_dhcp_opts': [{}],
            'fixed_ips': [{'ip_address': '10.0.0.3',
                           'subnet_id': 'subnet-id-' + uuid.uuid4().hex}],
            'id': 'port-id-' + uuid.uuid4().hex,
            'mac_address': 'fa:16:3e:a9:4e:72',
            'name': 'port-name-' + uuid.uuid4().hex,
            'network_id': 'network-id-' + uuid.uuid4().hex,
            'port_security_enabled': True,
            'security_group_ids': [],
            'status': 'ACTIVE',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
            'tags': [],
            'uplink_status_propagation': False,
        }

        # Overwrite default attributes.
        port_attrs.update(attrs)

        port = fakes.FakeResource(info=copy.deepcopy(port_attrs),
                                  loaded=True)

        # Set attributes with special mappings in OpenStack SDK.
        port.binding_host_id = port_attrs['binding:host_id']
        port.binding_profile = port_attrs['binding:profile']
        port.binding_vif_details = port_attrs['binding:vif_details']
        port.binding_vif_type = port_attrs['binding:vif_type']
        port.binding_vnic_type = port_attrs['binding:vnic_type']
        port.is_admin_state_up = port_attrs['admin_state_up']
        port.is_port_security_enabled = port_attrs['port_security_enabled']
        port.project_id = port_attrs['tenant_id']
        port.security_group_ids = port_attrs['security_group_ids']
        port.qos_policy_id = port_attrs['qos_policy_id']
        port.uplink_status_propagation = port_attrs[
            'uplink_status_propagation']

        return port

    @staticmethod
    def create_ports(attrs=None, count=2):
        """Create multiple fake ports.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of ports to fake
        :return:
            A list of FakeResource objects faking the ports
        """
        ports = []
        for i in range(0, count):
            ports.append(FakePort.create_one_port(attrs))

        return ports

    @staticmethod
    def get_ports(ports=None, count=2):
        """Get an iterable Mock object with a list of faked ports.

        If ports list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List ports:
            A list of FakeResource objects faking ports
        :param int count:
            The number of ports to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            ports
        """
        if ports is None:
            ports = FakePort.create_ports(count)
        return mock.Mock(side_effect=ports)


class FakeNetworkAgent(object):
    """Fake one or more network agents."""

    @staticmethod
    def create_one_network_agent(attrs=None):
        """Create a fake network agent

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, agent_type, and so on.
        """
        attrs = attrs or {}

        # Set default attributes
        agent_attrs = {
            'id': 'agent-id-' + uuid.uuid4().hex,
            'agent_type': 'agent-type-' + uuid.uuid4().hex,
            'host': 'host-' + uuid.uuid4().hex,
            'availability_zone': 'zone-' + uuid.uuid4().hex,
            'alive': True,
            'admin_state_up': True,
            'binary': 'binary-' + uuid.uuid4().hex,
            'configurations': {'subnet': 2, 'networks': 1},
        }
        agent_attrs.update(attrs)
        agent = fakes.FakeResource(info=copy.deepcopy(agent_attrs),
                                   loaded=True)
        agent.is_admin_state_up = agent_attrs['admin_state_up']
        agent.is_alive = agent_attrs['alive']
        return agent

    @staticmethod
    def create_network_agents(attrs=None, count=2):
        """Create multiple fake network agents.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of network agents to fake
        :return:
            A list of FakeResource objects faking the network agents
        """
        agents = []
        for i in range(0, count):
            agents.append(FakeNetworkAgent.create_one_network_agent(attrs))

        return agents

    @staticmethod
    def get_network_agents(agents=None, count=2):
        """Get an iterable Mock object with a list of faked network agents.

        If network agents list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List agents:
            A list of FakeResource objects faking network agents
        :param int count:
            The number of network agents to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            network agents
        """
        if agents is None:
            agents = FakeNetworkAgent.create_network_agents(count)
        return mock.Mock(side_effect=agents)


class FakeNetworkRBAC(object):
    """Fake one or more network rbac policies."""

    @staticmethod
    def create_one_network_rbac(attrs=None):
        """Create a fake network rbac

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, action, target_tenant,
            tenant_id, type
        """
        attrs = attrs or {}

        # Set default attributes
        rbac_attrs = {
            'id': 'rbac-id-' + uuid.uuid4().hex,
            'object_type': 'network',
            'object_id': 'object-id-' + uuid.uuid4().hex,
            'action': 'access_as_shared',
            'target_tenant': 'target-tenant-' + uuid.uuid4().hex,
            'tenant_id': 'tenant-id-' + uuid.uuid4().hex,
        }
        rbac_attrs.update(attrs)
        rbac = fakes.FakeResource(info=copy.deepcopy(rbac_attrs),
                                  loaded=True)
        # Set attributes with special mapping in OpenStack SDK.
        rbac.project_id = rbac_attrs['tenant_id']
        rbac.target_project_id = rbac_attrs['target_tenant']
        return rbac

    @staticmethod
    def create_network_rbacs(attrs=None, count=2):
        """Create multiple fake network rbac policies.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of rbac policies to fake
        :return:
            A list of FakeResource objects faking the rbac policies
        """
        rbac_policies = []
        for i in range(0, count):
            rbac_policies.append(FakeNetworkRBAC.
                                 create_one_network_rbac(attrs))

        return rbac_policies

    @staticmethod
    def get_network_rbacs(rbac_policies=None, count=2):
        """Get an iterable Mock object with a list of faked rbac policies.

        If rbac policies list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List rbac_policies:
            A list of FakeResource objects faking rbac policies
        :param int count:
            The number of rbac policies to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            rbac policies
        """
        if rbac_policies is None:
            rbac_policies = FakeNetworkRBAC.create_network_rbacs(count)
        return mock.Mock(side_effect=rbac_policies)


class FakeNetworkFlavorProfile(object):
    """Fake network flavor profile."""

    @staticmethod
    def create_one_service_profile(attrs=None):
        """Create flavor profile."""
        attrs = attrs or {}

        flavor_profile_attrs = {
            'id': 'flavor-profile-id' + uuid.uuid4().hex,
            'description': 'flavor-profile-description-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'driver': 'driver-' + uuid.uuid4().hex,
            'metainfo': 'metainfo-' + uuid.uuid4().hex,
            'enabled': True
        }

        flavor_profile_attrs.update(attrs)

        flavor_profile = fakes.FakeResource(
            info=copy.deepcopy(flavor_profile_attrs),
            loaded=True)

        flavor_profile.project_id = flavor_profile_attrs['tenant_id']
        flavor_profile.is_enabled = flavor_profile_attrs['enabled']

        return flavor_profile

    @staticmethod
    def create_service_profile(attrs=None, count=2):
        """Create multiple flavor profiles."""

        flavor_profiles = []
        for i in range(0, count):
            flavor_profiles.append(FakeNetworkFlavorProfile.
                                   create_one_service_profile(attrs))
        return flavor_profiles

    @staticmethod
    def get_service_profile(flavor_profile=None, count=2):
        """Get a list of flavor profiles."""
        if flavor_profile is None:
            flavor_profile = (FakeNetworkFlavorProfile.
                              create_service_profile(count))
        return mock.Mock(side_effect=flavor_profile)


class FakeNetworkQosPolicy(object):
    """Fake one or more QoS policies."""

    @staticmethod
    def create_one_qos_policy(attrs=None):
        """Create a fake QoS policy.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}
        qos_id = attrs.get('id') or 'qos-policy-id-' + uuid.uuid4().hex
        rule_attrs = {'qos_policy_id': qos_id}
        rules = [FakeNetworkQosRule.create_one_qos_rule(rule_attrs)]

        # Set default attributes.
        qos_policy_attrs = {
            'name': 'qos-policy-name-' + uuid.uuid4().hex,
            'id': qos_id,
            'is_default': False,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'shared': False,
            'description': 'qos-policy-description-' + uuid.uuid4().hex,
            'rules': rules,
        }

        # Overwrite default attributes.
        qos_policy_attrs.update(attrs)

        qos_policy = fakes.FakeResource(
            info=copy.deepcopy(qos_policy_attrs),
            loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        qos_policy.is_shared = qos_policy_attrs['shared']
        qos_policy.project_id = qos_policy_attrs['tenant_id']

        return qos_policy

    @staticmethod
    def create_qos_policies(attrs=None, count=2):
        """Create multiple fake QoS policies.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of QoS policies to fake
        :return:
            A list of FakeResource objects faking the QoS policies
        """
        qos_policies = []
        for i in range(0, count):
            qos_policies.append(
                FakeNetworkQosPolicy.create_one_qos_policy(attrs))

        return qos_policies

    @staticmethod
    def get_qos_policies(qos_policies=None, count=2):
        """Get an iterable MagicMock object with a list of faked QoS policies.

        If qos policies list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List qos_policies:
            A list of FakeResource objects faking qos policies
        :param int count:
            The number of QoS policies to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            QoS policies
        """
        if qos_policies is None:
            qos_policies = FakeNetworkQosPolicy.create_qos_policies(count)
        return mock.Mock(side_effect=qos_policies)


class FakeNetworkSecGroup(object):
    """Fake one security group."""

    @staticmethod
    def create_one_security_group(attrs=None):
        """Create a fake security group.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}
        sg_id = attrs.get('id') or 'security-group-id-' + uuid.uuid4().hex

        # Set default attributes.
        security_group_attrs = {
            'name': 'security-group-name-' + uuid.uuid4().hex,
            'id': sg_id,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'description': 'security-group-description-' + uuid.uuid4().hex
        }

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs),
            loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        security_group.project_id = security_group_attrs['tenant_id']

        return security_group


class FakeNetworkQosRule(object):
    """Fake one or more Network QoS rules."""

    @staticmethod
    def create_one_qos_rule(attrs=None):
        """Create a fake Network QoS rule.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        type = attrs.get('type') or choice(VALID_QOS_RULES)
        qos_rule_attrs = {
            'id': 'qos-rule-id-' + uuid.uuid4().hex,
            'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'type': type,
        }
        if type == RULE_TYPE_BANDWIDTH_LIMIT:
            qos_rule_attrs['max_kbps'] = randint(1, 10000)
            qos_rule_attrs['max_burst_kbits'] = randint(1, 10000)
            qos_rule_attrs['direction'] = 'egress'
        elif type == RULE_TYPE_DSCP_MARKING:
            qos_rule_attrs['dscp_mark'] = choice(VALID_DSCP_MARKS)
        elif type == RULE_TYPE_MINIMUM_BANDWIDTH:
            qos_rule_attrs['min_kbps'] = randint(1, 10000)
            qos_rule_attrs['direction'] = 'egress'

        # Overwrite default attributes.
        qos_rule_attrs.update(attrs)

        qos_rule = fakes.FakeResource(info=copy.deepcopy(qos_rule_attrs),
                                      loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        qos_rule.project_id = qos_rule['tenant_id']

        return qos_rule

    @staticmethod
    def create_qos_rules(attrs=None, count=2):
        """Create multiple fake Network QoS rules.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of Network QoS rule to fake
        :return:
            A list of FakeResource objects faking the Network QoS rules
        """
        qos_rules = []
        for i in range(0, count):
            qos_rules.append(FakeNetworkQosRule.create_one_qos_rule(attrs))
        return qos_rules

    @staticmethod
    def get_qos_rules(qos_rules=None, count=2):
        """Get a list of faked Network QoS rules.

        If Network QoS rules list is provided, then initialize the Mock
        object with the list. Otherwise create one.

        :param List qos_rules:
            A list of FakeResource objects faking Network QoS rules
        :param int count:
            The number of QoS minimum bandwidth rules to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            qos minimum bandwidth rules
        """
        if qos_rules is None:
            qos_rules = (FakeNetworkQosRule.create_qos_rules(count))
        return mock.Mock(side_effect=qos_rules)


class FakeNetworkQosRuleType(object):
    """Fake one or more Network QoS rule types."""

    @staticmethod
    def create_one_qos_rule_type(attrs=None):
        """Create a fake Network QoS rule type.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        qos_rule_type_attrs = {
            'type': 'rule-type-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        qos_rule_type_attrs.update(attrs)

        return fakes.FakeResource(
            info=copy.deepcopy(qos_rule_type_attrs),
            loaded=True)

    @staticmethod
    def create_qos_rule_types(attrs=None, count=2):
        """Create multiple fake Network QoS rule types.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of QoS rule types to fake
        :return:
            A list of FakeResource objects faking the QoS rule types
        """
        qos_rule_types = []
        for i in range(0, count):
            qos_rule_types.append(
                FakeNetworkQosRuleType.create_one_qos_rule_type(attrs))

        return qos_rule_types


class FakeRouter(object):
    """Fake one or more routers."""

    @staticmethod
    def create_one_router(attrs=None):
        """Create a fake router.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, admin_state_up,
            status, tenant_id
        """
        attrs = attrs or {}

        # Set default attributes.
        router_attrs = {
            'id': 'router-id-' + uuid.uuid4().hex,
            'name': 'router-name-' + uuid.uuid4().hex,
            'status': 'ACTIVE',
            'admin_state_up': True,
            'description': 'router-description-' + uuid.uuid4().hex,
            'distributed': False,
            'ha': False,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'routes': [],
            'external_gateway_info': {},
            'availability_zone_hints': [],
            'availability_zones': [],
            'tags': [],
        }

        # Overwrite default attributes.
        router_attrs.update(attrs)

        router = fakes.FakeResource(info=copy.deepcopy(router_attrs),
                                    loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        router.project_id = router_attrs['tenant_id']
        router.is_admin_state_up = router_attrs['admin_state_up']
        router.is_distributed = router_attrs['distributed']
        router.is_ha = router_attrs['ha']

        return router

    @staticmethod
    def create_routers(attrs=None, count=2):
        """Create multiple fake routers.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of routers to fake
        :return:
            A list of FakeResource objects faking the routers
        """
        routers = []
        for i in range(0, count):
            routers.append(FakeRouter.create_one_router(attrs))

        return routers

    @staticmethod
    def get_routers(routers=None, count=2):
        """Get an iterable Mock object with a list of faked routers.

        If routers list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List routers:
            A list of FakeResource objects faking routers
        :param int count:
            The number of routers to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            routers
        """
        if routers is None:
            routers = FakeRouter.create_routers(count)
        return mock.Mock(side_effect=routers)


class FakeSecurityGroup(object):
    """Fake one or more security groups."""

    @staticmethod
    def create_one_security_group(attrs=None):
        """Create a fake security group.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        security_group_attrs = {
            'id': 'security-group-id-' + uuid.uuid4().hex,
            'name': 'security-group-name-' + uuid.uuid4().hex,
            'description': 'security-group-description-' + uuid.uuid4().hex,
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'security_group_rules': [],
            'tags': []
        }

        # Overwrite default attributes.
        security_group_attrs.update(attrs)

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs),
            loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        security_group.project_id = security_group_attrs['project_id']

        return security_group

    @staticmethod
    def create_security_groups(attrs=None, count=2):
        """Create multiple fake security groups.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of security groups to fake
        :return:
            A list of FakeResource objects faking the security groups
        """
        security_groups = []
        for i in range(0, count):
            security_groups.append(
                FakeSecurityGroup.create_one_security_group(attrs))

        return security_groups

    @staticmethod
    def get_security_groups(security_groups=None, count=2):
        """Get an iterable Mock object with a list of faked security groups.

        If security groups list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List security_groups:
            A list of FakeResource objects faking security groups
        :param int count:
            The number of security groups to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            security groups
        """
        if security_groups is None:
            security_groups = FakeSecurityGroup.create_security_groups(count)
        return mock.Mock(side_effect=security_groups)


class FakeSecurityGroupRule(object):
    """Fake one or more security group rules."""

    @staticmethod
    def create_one_security_group_rule(attrs=None):
        """Create a fake security group rule.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, etc.
        """
        attrs = attrs or {}

        # Set default attributes.
        security_group_rule_attrs = {
            'description': 'security-group-rule-description-' +
                           uuid.uuid4().hex,
            'direction': 'ingress',
            'ether_type': 'IPv4',
            'id': 'security-group-rule-id-' + uuid.uuid4().hex,
            'port_range_max': None,
            'port_range_min': None,
            'protocol': None,
            'remote_group_id': None,
            'remote_ip_prefix': '0.0.0.0/0',
            'security_group_id': 'security-group-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        security_group_rule_attrs.update(attrs)

        security_group_rule = fakes.FakeResource(
            info=copy.deepcopy(security_group_rule_attrs),
            loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        security_group_rule.project_id = security_group_rule_attrs['tenant_id']

        return security_group_rule

    @staticmethod
    def create_security_group_rules(attrs=None, count=2):
        """Create multiple fake security group rules.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of security group rules to fake
        :return:
            A list of FakeResource objects faking the security group rules
        """
        security_group_rules = []
        for i in range(0, count):
            security_group_rules.append(
                FakeSecurityGroupRule.create_one_security_group_rule(attrs))

        return security_group_rules

    @staticmethod
    def get_security_group_rules(security_group_rules=None, count=2):
        """Get an iterable Mock with a list of faked security group rules.

        If security group rules list is provided, then initialize the Mock
        object with the list. Otherwise create one.

        :param List security_group_rules:
            A list of FakeResource objects faking security group rules
        :param int count:
            The number of security group rules to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            security group rules
        """
        if security_group_rules is None:
            security_group_rules = (
                FakeSecurityGroupRule.create_security_group_rules(count))
        return mock.Mock(side_effect=security_group_rules)


class FakeSubnet(object):
    """Fake one or more subnets."""

    @staticmethod
    def create_one_subnet(attrs=None):
        """Create a fake subnet.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object faking the subnet
        """
        attrs = attrs or {}

        # Set default attributes.
        project_id = 'project-id-' + uuid.uuid4().hex
        subnet_attrs = {
            'id': 'subnet-id-' + uuid.uuid4().hex,
            'name': 'subnet-name-' + uuid.uuid4().hex,
            'network_id': 'network-id-' + uuid.uuid4().hex,
            'cidr': '10.10.10.0/24',
            'tenant_id': project_id,
            'enable_dhcp': True,
            'dns_nameservers': [],
            'allocation_pools': [],
            'host_routes': [],
            'ip_version': 4,
            'gateway_ip': '10.10.10.1',
            'ipv6_address_mode': None,
            'ipv6_ra_mode': None,
            'segment_id': None,
            'service_types': [],
            'subnetpool_id': None,
            'description': 'subnet-description-' + uuid.uuid4().hex,
            'tags': [],
        }

        # Overwrite default attributes.
        subnet_attrs.update(attrs)

        subnet = fakes.FakeResource(info=copy.deepcopy(subnet_attrs),
                                    loaded=True)

        # Set attributes with special mappings in OpenStack SDK.
        subnet.is_dhcp_enabled = subnet_attrs['enable_dhcp']
        subnet.subnet_pool_id = subnet_attrs['subnetpool_id']
        subnet.project_id = subnet_attrs['tenant_id']

        return subnet

    @staticmethod
    def create_subnets(attrs=None, count=2):
        """Create multiple fake subnets.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of subnets to fake
        :return:
            A list of FakeResource objects faking the subnets
        """
        subnets = []
        for i in range(0, count):
            subnets.append(FakeSubnet.create_one_subnet(attrs))

        return subnets

    @staticmethod
    def get_subnets(subnets=None, count=2):
        """Get an iterable Mock object with a list of faked subnets.

        If subnets list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List subnets:
            A list of FakeResource objects faking subnets
        :param int count:
            The number of subnets to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            subnets
        """
        if subnets is None:
            subnets = FakeSubnet.create_subnets(count)
        return mock.Mock(side_effect=subnets)


class FakeFloatingIP(object):
    """Fake one or more floating ip."""

    @staticmethod
    def create_one_floating_ip(attrs=None):
        """Create a fake floating ip.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, ip, and so on
        """
        attrs = attrs or {}

        # Set default attributes.
        floating_ip_attrs = {
            'id': 'floating-ip-id-' + uuid.uuid4().hex,
            'floating_ip_address': '1.0.9.0',
            'fixed_ip_address': '2.0.9.0',
            'dns_domain': None,
            'dns_name': None,
            'status': 'DOWN',
            'floating_network_id': 'network-id-' + uuid.uuid4().hex,
            'router_id': 'router-id-' + uuid.uuid4().hex,
            'port_id': 'port-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'description': 'floating-ip-description-' + uuid.uuid4().hex,
            'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
            'tags': [],
        }

        # Overwrite default attributes.
        floating_ip_attrs.update(attrs)

        floating_ip = fakes.FakeResource(
            info=copy.deepcopy(floating_ip_attrs),
            loaded=True
        )

        # Set attributes with special mappings in OpenStack SDK.
        floating_ip.project_id = floating_ip_attrs['tenant_id']

        return floating_ip

    @staticmethod
    def create_floating_ips(attrs=None, count=2):
        """Create multiple fake floating ips.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of floating ips to fake
        :return:
            A list of FakeResource objects faking the floating ips
        """
        floating_ips = []
        for i in range(0, count):
            floating_ips.append(FakeFloatingIP.create_one_floating_ip(attrs))
        return floating_ips

    @staticmethod
    def get_floating_ips(floating_ips=None, count=2):
        """Get an iterable Mock object with a list of faked floating ips.

        If floating_ips list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List floating_ips:
            A list of FakeResource objects faking floating ips
        :param int count:
            The number of floating ips to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            floating ips
        """
        if floating_ips is None:
            floating_ips = FakeFloatingIP.create_floating_ips(count)
        return mock.Mock(side_effect=floating_ips)


class FakeNetworkMeter(object):
    """Fake network meter"""

    @staticmethod
    def create_one_meter(attrs=None):
        """Create metering pool"""
        attrs = attrs or {}

        meter_attrs = {
            'id': 'meter-id-' + uuid.uuid4().hex,
            'name': 'meter-name-' + uuid.uuid4().hex,
            'description': 'meter-description-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'shared': False
        }

        meter_attrs.update(attrs)

        meter = fakes.FakeResource(
            info=copy.deepcopy(meter_attrs),
            loaded=True)

        meter.project_id = meter_attrs['tenant_id']

        return meter

    @staticmethod
    def create_meter(attrs=None, count=2):
        """Create multiple meters"""

        meters = []
        for i in range(0, count):
            meters.append(FakeNetworkMeter.
                          create_one_meter(attrs))
        return meters

    @staticmethod
    def get_meter(meter=None, count=2):
        """Get a list of meters"""
        if meter is None:
            meter = (FakeNetworkMeter.
                     create_meter(count))
        return mock.Mock(side_effect=meter)


class FakeNetworkMeterRule(object):
    """Fake metering rule"""

    @staticmethod
    def create_one_rule(attrs=None):
        """Create one meter rule"""
        attrs = attrs or {}

        meter_rule_attrs = {
            'id': 'meter-label-rule-id-' + uuid.uuid4().hex,
            'direction': 'ingress',
            'excluded': False,
            'metering_label_id': 'meter-label-id-' + uuid.uuid4().hex,
            'remote_ip_prefix': '10.0.0.0/24',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
        }

        meter_rule_attrs.update(attrs)

        meter_rule = fakes.FakeResource(
            info=copy.deepcopy(meter_rule_attrs),
            loaded=True)

        meter_rule.project_id = meter_rule_attrs['tenant_id']

        return meter_rule

    @staticmethod
    def create_meter_rule(attrs=None, count=2):
        """Create multiple meter rules"""

        meter_rules = []
        for i in range(0, count):
            meter_rules.append(FakeNetworkMeterRule.
                               create_one_rule(attrs))
        return meter_rules

    @staticmethod
    def get_meter_rule(meter_rule=None, count=2):
        """Get a list of meter rules"""
        if meter_rule is None:
            meter_rule = (FakeNetworkMeterRule.
                          create_meter_rule(count))
        return mock.Mock(side_effect=meter_rule)


class FakeSubnetPool(object):
    """Fake one or more subnet pools."""

    @staticmethod
    def create_one_subnet_pool(attrs=None):
        """Create a fake subnet pool.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object faking the subnet pool
        """
        attrs = attrs or {}

        # Set default attributes.
        subnet_pool_attrs = {
            'id': 'subnet-pool-id-' + uuid.uuid4().hex,
            'name': 'subnet-pool-name-' + uuid.uuid4().hex,
            'prefixes': ['10.0.0.0/24', '10.1.0.0/24'],
            'default_prefixlen': '8',
            'address_scope_id': 'address-scope-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'is_default': False,
            'shared': False,
            'max_prefixlen': '32',
            'min_prefixlen': '8',
            'default_quota': None,
            'ip_version': '4',
            'description': 'subnet-pool-description-' + uuid.uuid4().hex,
            'tags': [],
        }

        # Overwrite default attributes.
        subnet_pool_attrs.update(attrs)

        subnet_pool = fakes.FakeResource(
            info=copy.deepcopy(subnet_pool_attrs),
            loaded=True
        )

        # Set attributes with special mapping in OpenStack SDK.
        subnet_pool.default_prefix_length = \
            subnet_pool_attrs['default_prefixlen']
        subnet_pool.is_shared = subnet_pool_attrs['shared']
        subnet_pool.maximum_prefix_length = subnet_pool_attrs['max_prefixlen']
        subnet_pool.minimum_prefix_length = subnet_pool_attrs['min_prefixlen']
        subnet_pool.project_id = subnet_pool_attrs['tenant_id']

        return subnet_pool

    @staticmethod
    def create_subnet_pools(attrs=None, count=2):
        """Create multiple fake subnet pools.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of subnet pools to fake
        :return:
            A list of FakeResource objects faking the subnet pools
        """
        subnet_pools = []
        for i in range(0, count):
            subnet_pools.append(
                FakeSubnetPool.create_one_subnet_pool(attrs)
            )

        return subnet_pools

    @staticmethod
    def get_subnet_pools(subnet_pools=None, count=2):
        """Get an iterable Mock object with a list of faked subnet pools.

        If subnet_pools list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List subnet_pools:
            A list of FakeResource objects faking subnet pools
        :param int count:
            The number of subnet pools to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            subnet pools
        """
        if subnet_pools is None:
            subnet_pools = FakeSubnetPool.create_subnet_pools(count)
        return mock.Mock(side_effect=subnet_pools)


class FakeNetworkServiceProvider(object):
    """Fake Network Service Providers"""

    @staticmethod
    def create_one_network_service_provider(attrs=None):
        """Create service provider"""
        attrs = attrs or {}

        service_provider = {
            'name': 'provider-name-' + uuid.uuid4().hex,
            'service_type': 'service-type-' + uuid.uuid4().hex,
            'default': False,
        }

        service_provider.update(attrs)

        provider = fakes.FakeResource(
            info=copy.deepcopy(service_provider),
            loaded=True)
        provider.is_default = service_provider['default']

        return provider

    @staticmethod
    def create_network_service_providers(attrs=None, count=2):
        """Create multiple service providers"""

        service_providers = []
        for i in range(0, count):
            service_providers.append(FakeNetworkServiceProvider.
                                     create_one_network_service_provider(
                                         attrs))
        return service_providers


class FakeQuota(object):
    """Fake quota"""

    @staticmethod
    def create_one_net_quota(attrs=None):
        """Create one quota"""
        attrs = attrs or {}

        quota_attrs = {
            'floating_ips': 20,
            'networks': 25,
            'ports': 11,
            'rbac_policies': 15,
            'routers': 40,
            'security_groups': 10,
            'security_group_rules': 100,
            'subnets': 20,
            'subnet_pools': 30}

        quota_attrs.update(attrs)

        quota = fakes.FakeResource(
            info=copy.deepcopy(quota_attrs),
            loaded=True)
        return quota

    @staticmethod
    def create_one_default_net_quota(attrs=None):
        """Create one quota"""
        attrs = attrs or {}

        quota_attrs = {
            'floatingip': 30,
            'network': 20,
            'port': 10,
            'rbac_policy': 25,
            'router': 30,
            'security_group': 30,
            'security_group_rule': 200,
            'subnet': 10,
            'subnetpool': 20}

        quota_attrs.update(attrs)

        quota = fakes.FakeResource(
            info=copy.deepcopy(quota_attrs),
            loaded=True)
        return quota

    @staticmethod
    def create_one_net_detailed_quota(attrs=None):
        """Create one quota"""
        attrs = attrs or {}

        quota_attrs = {
            'floating_ips': {'used': 0, 'reserved': 0, 'limit': 20},
            'networks': {'used': 0, 'reserved': 0, 'limit': 25},
            'ports': {'used': 0, 'reserved': 0, 'limit': 11},
            'rbac_policies': {'used': 0, 'reserved': 0, 'limit': 15},
            'routers': {'used': 0, 'reserved': 0, 'limit': 40},
            'security_groups': {'used': 0, 'reserved': 0, 'limit': 10},
            'security_group_rules': {'used': 0, 'reserved': 0, 'limit': 100},
            'subnets': {'used': 0, 'reserved': 0, 'limit': 20},
            'subnet_pools': {'used': 0, 'reserved': 0, 'limit': 30}}

        quota_attrs.update(attrs)

        quota = fakes.FakeResource(
            info=copy.deepcopy(quota_attrs),
            loaded=True)
        return quota


class FakeFloatingIPPortForwarding(object):
    """"Fake one or more Port forwarding"""

    @staticmethod
    def create_one_port_forwarding(attrs=None):
        """Create a fake Port Forwarding.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}
        floatingip_id = (
            attrs.get('floatingip_id') or'floating-ip-id-' + uuid.uuid4().hex
        )
        # Set default attributes.
        port_forwarding_attrs = {
            'id': uuid.uuid4().hex,
            'floatingip_id': floatingip_id,
            'internal_port_id': 'internal-port-id-' + uuid.uuid4().hex,
            'internal_ip_address': '192.168.1.2',
            'internal_port': randint(1, 65535),
            'external_port': randint(1, 65535),
            'protocol': 'tcp',
        }

        # Overwrite default attributes.
        port_forwarding_attrs.update(attrs)

        port_forwarding = fakes.FakeResource(
            info=copy.deepcopy(port_forwarding_attrs),
            loaded=True
        )
        return port_forwarding

    @staticmethod
    def create_port_forwardings(attrs=None, count=2):
        """Create multiple fake Port Forwarding.

          :param Dictionary attrs:
              A dictionary with all attributes
          :param int count:
              The number of Port Forwarding rule to fake
          :return:
              A list of FakeResource objects faking the Port Forwardings
          """
        port_forwardings = []
        for i in range(0, count):
            port_forwardings.append(
                FakeFloatingIPPortForwarding.create_one_port_forwarding(attrs)
            )
        return port_forwardings

    @staticmethod
    def get_port_forwardings(port_forwardings=None, count=2):
        """Get a list of faked Port Forwardings.

        If port forwardings list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List port forwardings:
            A list of FakeResource objects faking port forwardings
        :param int count:
            The number of Port Forwardings to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            Port Forwardings
        """
        if port_forwardings is None:
            port_forwardings = (
                FakeFloatingIPPortForwarding.create_port_forwardings(count)
            )

        return mock.Mock(side_effect=port_forwardings)
