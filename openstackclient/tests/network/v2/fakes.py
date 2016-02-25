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

from openstackclient.tests import fakes
from openstackclient.tests import utils

extension_name = 'Matrix'
extension_namespace = 'http://docs.openstack.org/network/'
extension_description = 'Simulated reality'
extension_updated = '2013-07-09T12:00:0-00:00'
extension_alias = 'Dystopian'
extension_links = '[{"href":''"https://github.com/os/network", "type"}]'

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
}


def create_extension():
    extension = mock.Mock()
    extension.name = extension_name
    extension.namespace = extension_namespace
    extension.description = extension_description
    extension.updated = extension_updated
    extension.alias = extension_alias
    extension.links = extension_links
    return extension


class FakeNetworkV2Client(object):

    def __init__(self, **kwargs):
        self.extensions = mock.Mock(return_value=[create_extension()])


class TestNetworkV2(utils.TestCommand):

    def setUp(self):
        super(TestNetworkV2, self).setUp()

        self.namespace = argparse.Namespace()

        self.app.client_manager.session = mock.Mock()

        self.app.client_manager.network = FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class FakeAvailabilityZone(object):
    """Fake one or more network availability zones (AZs)."""

    @staticmethod
    def create_one_availability_zone(attrs={}, methods={}):
        """Create a fake AZ.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object with name, state, etc.
        """
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
            methods=methods,
            loaded=True)
        return availability_zone

    @staticmethod
    def create_availability_zones(attrs={}, methods={}, count=2):
        """Create multiple fake AZs.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of AZs to fake
        :return:
            A list of FakeResource objects faking the AZs
        """
        availability_zones = []
        for i in range(0, count):
            availability_zone = \
                FakeAvailabilityZone.create_one_availability_zone(
                    attrs, methods)
            availability_zones.append(availability_zone)

        return availability_zones


class FakeNetwork(object):
    """Fake one or more networks."""

    @staticmethod
    def create_one_network(attrs={}, methods={}):
        """Create a fake network.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, admin_state_up,
            router_external, status, subnets, tenant_id
        """
        # Set default attributes.
        network_attrs = {
            'id': 'network-id-' + uuid.uuid4().hex,
            'name': 'network-name-' + uuid.uuid4().hex,
            'status': 'ACTIVE',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'admin_state_up': True,
            'shared': False,
            'subnets': ['a', 'b'],
            'provider_network_type': 'vlan',
            'router_external': True,
            'availability_zones': [],
            'availability_zone_hints': [],
        }

        # Overwrite default attributes.
        network_attrs.update(attrs)

        # Set default methods.
        network_methods = {
            'keys': ['id', 'name', 'admin_state_up', 'router_external',
                     'status', 'subnets', 'tenant_id', 'availability_zones',
                     'availability_zone_hints'],
        }

        # Overwrite default methods.
        network_methods.update(methods)

        network = fakes.FakeResource(info=copy.deepcopy(network_attrs),
                                     methods=copy.deepcopy(network_methods),
                                     loaded=True)

        # Set attributes with special mapping in OpenStack SDK.
        network.project_id = network_attrs['tenant_id']

        return network

    @staticmethod
    def create_networks(attrs={}, methods={}, count=2):
        """Create multiple fake networks.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of networks to fake
        :return:
            A list of FakeResource objects faking the networks
        """
        networks = []
        for i in range(0, count):
            networks.append(FakeNetwork.create_one_network(attrs, methods))

        return networks

    @staticmethod
    def get_networks(networks=None, count=2):
        """Get an iterable MagicMock object with a list of faked networks.

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
        return mock.MagicMock(side_effect=networks)


class FakePort(object):
    """Fake one or more ports."""

    @staticmethod
    def create_one_port(attrs={}, methods={}):
        """Create a fake port.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, etc.
        """
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

        # Set default methods.
        port_methods = {
            'keys': ['admin_state_up', 'allowed_address_pairs',
                     'binding:host_id', 'binding:profile',
                     'binding:vif_details', 'binding:vif_type',
                     'binding:vnic_type', 'device_id', 'device_owner',
                     'dns_assignment', 'dns_name', 'extra_dhcp_opts',
                     'fixed_ips', 'id', 'mac_address', 'name',
                     'network_id', 'port_security_enabled',
                     'security_groups', 'status', 'tenant_id'],
        }

        # Overwrite default methods.
        port_methods.update(methods)

        port = fakes.FakeResource(info=copy.deepcopy(port_attrs),
                                  methods=copy.deepcopy(port_methods),
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
    def create_ports(attrs={}, methods={}, count=2):
        """Create multiple fake ports.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of ports to fake
        :return:
            A list of FakeResource objects faking the ports
        """
        ports = []
        for i in range(0, count):
            ports.append(FakePort.create_one_port(attrs, methods))

        return ports

    @staticmethod
    def get_ports(ports=None, count=2):
        """Get an iterable MagicMock object with a list of faked ports.

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
        return mock.MagicMock(side_effect=ports)


class FakeRouter(object):
    """Fake one or more routers."""

    @staticmethod
    def create_one_router(attrs={}, methods={}):
        """Create a fake router.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, admin_state_up,
            status, tenant_id
        """
        # Set default attributes.
        router_attrs = {
            'id': 'router-id-' + uuid.uuid4().hex,
            'name': 'router-name-' + uuid.uuid4().hex,
            'status': 'ACTIVE',
            'admin_state_up': True,
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

        # Set default methods.
        router_methods = {
            'keys': ['id', 'name', 'admin_state_up', 'distributed', 'ha',
                     'tenant_id'],
        }

        # Overwrite default methods.
        router_methods.update(methods)

        router = fakes.FakeResource(info=copy.deepcopy(router_attrs),
                                    methods=copy.deepcopy(router_methods),
                                    loaded=True)
        return router

    @staticmethod
    def create_routers(attrs={}, methods={}, count=2):
        """Create multiple fake routers.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of routers to fake
        :return:
            A list of FakeResource objects faking the routers
        """
        routers = []
        for i in range(0, count):
            routers.append(FakeRouter.create_one_router(attrs, methods))

        return routers

    @staticmethod
    def get_routers(routers=None, count=2):
        """Get an iterable MagicMock object with a list of faked routers.

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
        return mock.MagicMock(side_effect=routers)


class FakeSecurityGroup(object):
    """Fake one or more security groups."""

    @staticmethod
    def create_one_security_group(attrs={}, methods={}):
        """Create a fake security group.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, etc.
        """
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

        # Set default methods.
        security_group_methods = {}

        # Overwrite default methods.
        security_group_methods.update(methods)

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs),
            methods=copy.deepcopy(security_group_methods),
            loaded=True)
        return security_group

    @staticmethod
    def create_security_groups(attrs={}, methods={}, count=2):
        """Create multiple fake security groups.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of security groups to fake
        :return:
            A list of FakeResource objects faking the security groups
        """
        security_groups = []
        for i in range(0, count):
            security_groups.append(
                FakeSecurityGroup.create_one_security_group(attrs, methods))

        return security_groups


class FakeSecurityGroupRule(object):
    """Fake one or more security group rules."""

    @staticmethod
    def create_one_security_group_rule(attrs={}, methods={}):
        """Create a fake security group rule.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, etc.
        """
        # Set default attributes.
        security_group_rule_attrs = {
            'direction': 'ingress',
            'ethertype': 'IPv4',
            'id': 'security-group-rule-id-' + uuid.uuid4().hex,
            'port_range_max': None,
            'port_range_min': None,
            'protocol': None,
            'remote_group_id': 'remote-security-group-id-' + uuid.uuid4().hex,
            'remote_ip_prefix': None,
            'security_group_id': 'security-group-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        security_group_rule_attrs.update(attrs)

        # Set default methods.
        security_group_rule_methods = {
            'keys': ['direction', 'ethertype', 'id', 'port_range_max',
                     'port_range_min', 'protocol', 'remote_group_id',
                     'remote_ip_prefix', 'security_group_id', 'tenant_id'],
        }

        # Overwrite default methods.
        security_group_rule_methods.update(methods)

        security_group_rule = fakes.FakeResource(
            info=copy.deepcopy(security_group_rule_attrs),
            methods=copy.deepcopy(security_group_rule_methods),
            loaded=True)

        # Set attributes with special mappings.
        security_group_rule.project_id = security_group_rule_attrs['tenant_id']

        return security_group_rule

    @staticmethod
    def create_security_group_rules(attrs={}, methods={}, count=2):
        """Create multiple fake security group rules.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of security group rules to fake
        :return:
            A list of FakeResource objects faking the security group rules
        """
        security_group_rules = []
        for i in range(0, count):
            security_group_rules.append(
                FakeSecurityGroupRule.create_one_security_group_rule(
                    attrs, methods))

        return security_group_rules


class FakeSubnet(object):
    """Fake one or more subnets."""

    @staticmethod
    def create_one_subnet(attrs={}, methods={}):
        """Create a fake subnet.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object faking the subnet
        """
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
            'ip_version': '4',
            'gateway_ip': '10.10.10.1',
            'ipv6_address_mode': 'None',
            'ipv6_ra_mode': 'None',
            'subnetpool_id': 'None',
        }

        # Overwrite default attributes.
        subnet_attrs.update(attrs)

        # Set default methods.
        subnet_methods = {
            'keys': ['id', 'name', 'network_id', 'cidr', 'enable_dhcp',
                     'allocation_pools', 'dns_nameservers', 'gateway_ip',
                     'host_routes', 'ip_version', 'tenant_id',
                     'ipv6_address_mode', 'ipv6_ra_mode', 'subnetpool_id']
        }

        # Overwrite default methods.
        subnet_methods.update(methods)

        subnet = fakes.FakeResource(info=copy.deepcopy(subnet_attrs),
                                    methods=copy.deepcopy(subnet_methods),
                                    loaded=True)
        # Set attributes with special mappings in OpenStack SDK.
        subnet.project_id = subnet_attrs['tenant_id']

        return subnet

    @staticmethod
    def create_subnets(attrs={}, methods={}, count=2):
        """Create multiple fake subnets.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of subnets to fake
        :return:
            A list of FakeResource objects faking the subnets
        """
        subnets = []
        for i in range(0, count):
            subnets.append(FakeSubnet.create_one_subnet(attrs, methods))

        return subnets


class FakeFloatingIP(object):
    """Fake one or more floating ip."""

    @staticmethod
    def create_one_floating_ip(attrs={}, methods={}):
        """Create a fake floating ip.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, ip, and so on
        """
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
        }

        # Overwrite default attributes.
        floating_ip_attrs.update(attrs)

        # Set default methods.
        floating_ip_methods = {
            'keys': ['id', 'floating_ip_address', 'fixed_ip_address',
                     'dns_domain', 'dns_name', 'status', 'router_id',
                     'floating_network_id', 'port_id', 'tenant_id']
        }

        # Overwrite default methods.
        floating_ip_methods.update(methods)

        floating_ip = fakes.FakeResource(
            info=copy.deepcopy(floating_ip_attrs),
            methods=copy.deepcopy(floating_ip_methods),
            loaded=True
        )

        # Set attributes with special mappings in OpenStack SDK.
        floating_ip.project_id = floating_ip_attrs['tenant_id']

        return floating_ip

    @staticmethod
    def create_floating_ips(attrs={}, methods={}, count=2):
        """Create multiple fake floating ips.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of floating ips to fake
        :return:
            A list of FakeResource objects faking the floating ips
        """
        floating_ips = []
        for i in range(0, count):
            floating_ips.append(FakeFloatingIP.create_one_floating_ip(
                attrs,
                methods
            ))
        return floating_ips

    @staticmethod
    def get_floating_ips(floating_ips=None, count=2):
        """Get an iterable MagicMock object with a list of faked floating ips.

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
        return mock.MagicMock(side_effect=floating_ips)


class FakeSubnetPool(object):
    """Fake one or more subnet pools."""

    @staticmethod
    def create_one_subnet_pool(attrs={}, methods={}):
        """Create a fake subnet pool.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object faking the subnet pool
        """
        # Set default attributes.
        subnet_pool_attrs = {
            'id': 'subnet-pool-id-' + uuid.uuid4().hex,
            'name': 'subnet-pool-name-' + uuid.uuid4().hex,
            'prefixes': ['10.0.0.0/24', '10.1.0.0/24'],
            'default_prefixlen': 8,
            'address_scope_id': 'address-scope-id-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'is_default': False,
            'shared': False,
            'max_prefixlen': 32,
            'min_prefixlen': 8,
            'default_quota': None,
            'ip_version': 4,
        }

        # Overwrite default attributes.
        subnet_pool_attrs.update(attrs)

        # Set default methods.
        subnet_pool_methods = {
            'keys': ['id', 'name', 'prefixes', 'default_prefixlen',
                     'address_scope_id', 'tenant_id', 'is_default',
                     'shared', 'max_prefixlen', 'min_prefixlen',
                     'default_quota', 'ip_version']
        }

        # Overwrite default methods.
        subnet_pool_methods.update(methods)

        subnet_pool = fakes.FakeResource(
            info=copy.deepcopy(subnet_pool_attrs),
            methods=copy.deepcopy(subnet_pool_methods),
            loaded=True
        )

        # Set attributes with special mapping in OpenStack SDK.
        subnet_pool.project_id = subnet_pool_attrs['tenant_id']

        return subnet_pool

    @staticmethod
    def create_subnet_pools(attrs={}, methods={}, count=2):
        """Create multiple fake subnet pools.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of subnet pools to fake
        :return:
            A list of FakeResource objects faking the subnet pools
        """
        subnet_pools = []
        for i in range(0, count):
            subnet_pools.append(
                FakeSubnetPool.create_one_subnet_pool(attrs, methods)
            )

        return subnet_pools
