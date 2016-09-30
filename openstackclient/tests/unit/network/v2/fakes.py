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
import mock
import uuid

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


class FakeNetworkV2Client(object):

    def __init__(self, **kwargs):
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

        :param List address scopes:
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
    def create_one_ip_availability():
        """Create a fake list with ip availability stats of a network.

        :return:
            A FakeResource object with network_name, network_id, etc.
        """

        # Set default attributes.
        network_ip_availability = {
            'network_id': 'network-id-' + uuid.uuid4().hex,
            'network_name': 'network-name-' + uuid.uuid4().hex,
            'tenant_id': '',
            'subnet_ip_availability': [],
            'total_ips': 254,
            'used_ips': 6,
        }

        network_ip_availability = fakes.FakeResource(
            info=copy.deepcopy(network_ip_availability),
            loaded=True)
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
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'admin_state_up': True,
            'shared': False,
            'subnets': ['a', 'b'],
            'provider_network_type': 'vlan',
            'router:external': True,
            'availability_zones': [],
            'availability_zone_hints': [],
            'is_default': False,
            'port_security_enabled': True,
        }

        # Overwrite default attributes.
        network_attrs.update(attrs)

        network = fakes.FakeResource(info=copy.deepcopy(network_attrs),
                                     loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        network.project_id = network_attrs['tenant_id']
        network.is_router_external = network_attrs['router:external']
        network.is_port_security_enabled = \
            network_attrs['port_security_enabled']

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
            'device_id': 'device-id-' + uuid.uuid4().hex,
            'device_owner': 'compute:nova',
            'dns_assignment': [{}],
            'dns_name': 'dns-name-' + uuid.uuid4().hex,
            'extra_dhcp_opts': [{}],
            'fixed_ips': [{}],
            'id': 'port-id-' + uuid.uuid4().hex,
            'mac_address': 'fa:16:3e:a9:4e:72',
            'name': 'port-name-' + uuid.uuid4().hex,
            'network_id': 'network-id-' + uuid.uuid4().hex,
            'port_security_enabled': True,
            'security_groups': [],
            'status': 'ACTIVE',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        port_attrs.update(attrs)

        port = fakes.FakeResource(info=copy.deepcopy(port_attrs),
                                  loaded=True)

        # Set attributes with special mappings in OpenStack SDK.
        port.project_id = port_attrs['tenant_id']
        port.binding_host_id = port_attrs['binding:host_id']
        port.binding_profile = port_attrs['binding:profile']
        port.binding_vif_details = port_attrs['binding:vif_details']
        port.binding_vif_type = port_attrs['binding:vif_type']
        port.binding_vnic_type = port_attrs['binding:vnic_type']

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
        }

        # Overwrite default attributes.
        router_attrs.update(attrs)

        router = fakes.FakeResource(info=copy.deepcopy(router_attrs),
                                    loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        router.project_id = router_attrs['tenant_id']

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
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'security_group_rules': [],
        }

        # Overwrite default attributes.
        security_group_attrs.update(attrs)

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs),
            loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        security_group.project_id = security_group_attrs['tenant_id']

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

        :param List security groups:
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
            'direction': 'ingress',
            'ethertype': 'IPv4',
            'id': 'security-group-rule-id-' + uuid.uuid4().hex,
            'port_range_max': None,
            'port_range_min': None,
            'protocol': 'tcp',
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
        """Get an iterable Mock object with a list of faked security group rules.

        If security group rules list is provided, then initialize the Mock
        object with the list. Otherwise create one.

        :param List security group rules:
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
        }

        # Overwrite default attributes.
        subnet_attrs.update(attrs)

        subnet = fakes.FakeResource(info=copy.deepcopy(subnet_attrs),
                                    loaded=True)

        # Set attributes with special mappings in OpenStack SDK.
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

        :param List floating ips:
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
        }

        # Overwrite default attributes.
        subnet_pool_attrs.update(attrs)

        subnet_pool = fakes.FakeResource(
            info=copy.deepcopy(subnet_pool_attrs),
            loaded=True
        )

        # Set attributes with special mapping in OpenStack SDK.
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

        :param List subnet pools:
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
