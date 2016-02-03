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
        project_id = 'project-id-' + uuid.uuid4().hex
        network_attrs = {
            'id': 'network-id-' + uuid.uuid4().hex,
            'name': 'network-name-' + uuid.uuid4().hex,
            'status': 'ACTIVE',
            'tenant_id': project_id,
            'admin_state_up': True,
            'shared': False,
            'subnets': ['a', 'b'],
            'provider_network_type': 'vlan',
            'router_external': True,
            'is_dirty': True,
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
        network.project_id = project_id

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

        # Set attributes with special mappings.
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
        subnet_attrs = {
            'id': 'subnet-id-' + uuid.uuid4().hex,
            'name': 'subnet-name-' + uuid.uuid4().hex,
            'network_id': 'network-id-' + uuid.uuid4().hex,
            'cidr': '10.10.10.0/24',
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'enable_dhcp': True,
            'dns_nameservers': [],
            'allocation_pools': [],
            'host_routes': [],
            'ip_version': '4',
            'gateway_ip': '10.10.10.1',
        }

        # Overwrite default attributes.
        subnet_attrs.update(attrs)

        # Set default methods.
        subnet_methods = {
            'keys': ['id', 'name', 'network_id', 'cidr', 'enable_dhcp',
                     'allocation_pools', 'dns_nameservers', 'gateway_ip',
                     'host_routes', 'ip_version', 'tenant_id']
        }

        # Overwrite default methods.
        subnet_methods.update(methods)

        subnet = fakes.FakeResource(info=copy.deepcopy(subnet_attrs),
                                    methods=copy.deepcopy(subnet_methods),
                                    loaded=True)

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
