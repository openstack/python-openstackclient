#   Copyright 2013 Nebula Inc.
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

import copy
import mock
import uuid

from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.image.v2 import fakes as image_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils
from openstackclient.tests.volume.v2 import fakes as volume_fakes


extension_name = 'Multinic'
extension_namespace = 'http://docs.openstack.org/compute/ext/'\
    'multinic/api/v1.1'
extension_description = 'Multiple network support'
extension_updated = '2014-01-07T12:00:0-00:00'
extension_alias = 'NMN'
extension_links = '[{"href":'\
    '"https://github.com/openstack/compute-api", "type":'\
    ' "text/html", "rel": "describedby"}]'

EXTENSION = {
    'name': extension_name,
    'namespace': extension_namespace,
    'description': extension_description,
    'updated': extension_updated,
    'alias': extension_alias,
    'links': extension_links,
}

floating_ip_num = 100
fix_ip_num = 100
injected_file_num = 100
injected_file_size_num = 10240
injected_path_size_num = 255
key_pair_num = 100
core_num = 20
ram_num = 51200
instance_num = 10
property_num = 128
secgroup_rule_num = 20
secgroup_num = 10
project_name = 'project_test'
QUOTA = {
    'project': project_name,
    'floating-ips': floating_ip_num,
    'fix-ips': fix_ip_num,
    'injected-files': injected_file_num,
    'injected-file-size': injected_file_size_num,
    'injected-path-size': injected_path_size_num,
    'key-pairs': key_pair_num,
    'cores': core_num,
    'ram': ram_num,
    'instances': instance_num,
    'properties': property_num,
    'secgroup_rules': secgroup_rule_num,
    'secgroups': secgroup_num,
}

QUOTA_columns = tuple(sorted(QUOTA))
QUOTA_data = tuple(QUOTA[x] for x in sorted(QUOTA))

service_host = 'host_test'
service_binary = 'compute_test'
service_status = 'enabled'
SERVICE = {
    'host': service_host,
    'binary': service_binary,
    'status': service_status,
}


class FakeComputev2Client(object):

    def __init__(self, **kwargs):
        self.aggregates = mock.Mock()
        self.aggregates.resource_class = fakes.FakeResource(None, {})

        self.availability_zones = mock.Mock()
        self.availability_zones.resource_class = fakes.FakeResource(None, {})

        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})

        self.servers = mock.Mock()
        self.servers.resource_class = fakes.FakeResource(None, {})

        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})

        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})

        self.flavors = mock.Mock()
        self.flavors.resource_class = fakes.FakeResource(None, {})

        self.quotas = mock.Mock()
        self.quotas.resource_class = fakes.FakeResource(None, {})

        self.quota_classes = mock.Mock()
        self.quota_classes.resource_class = fakes.FakeResource(None, {})

        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})

        self.hypervisors = mock.Mock()
        self.hypervisors.resource_class = fakes.FakeResource(None, {})

        self.hypervisors_stats = mock.Mock()
        self.hypervisors_stats.resource_class = fakes.FakeResource(None, {})

        self.security_groups = mock.Mock()
        self.security_groups.resource_class = fakes.FakeResource(None, {})

        self.security_group_rules = mock.Mock()
        self.security_group_rules.resource_class = fakes.FakeResource(None, {})

        self.floating_ips = mock.Mock()
        self.floating_ips.resource_class = fakes.FakeResource(None, {})

        self.networks = mock.Mock()
        self.networks.resource_class = fakes.FakeResource(None, {})

        self.auth_token = kwargs['token']

        self.management_url = kwargs['endpoint']


class TestComputev2(utils.TestCommand):

    def setUp(self):
        super(TestComputev2, self).setUp()

        self.app.client_manager.compute = FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.image = image_fakes.FakeImagev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.network = network_fakes.FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.volume = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


class FakeHypervisor(object):
    """Fake one or more hypervisor."""

    @staticmethod
    def create_one_hypervisor(attrs={}):
        """Create a fake hypervisor.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, hypervisor_hostname, and so on
        """
        # Set default attributes.
        hypervisor_info = {
            'id': 'hypervisor-id-' + uuid.uuid4().hex,
            'hypervisor_hostname': 'hypervisor-hostname-' + uuid.uuid4().hex,
            'status': 'enabled',
            'host_ip': '192.168.0.10',
            'cpu_info': {
                'aaa': 'aaa',
            },
            'free_disk_gb': 50,
            'hypervisor_version': 2004001,
            'disk_available_least': 50,
            'local_gb': 50,
            'free_ram_mb': 1024,
            'service': {
                'host': 'aaa',
                'disabled_reason': None,
                'id': 1,
            },
            'vcpus_used': 0,
            'hypervisor_type': 'QEMU',
            'local_gb_used': 0,
            'vcpus': 4,
            'memory_mb_used': 512,
            'memory_mb': 1024,
            'current_workload': 0,
            'state': 'up',
            'running_vms': 0,
        }

        # Overwrite default attributes.
        hypervisor_info.update(attrs)

        hypervisor = fakes.FakeResource(info=copy.deepcopy(hypervisor_info),
                                        loaded=True)
        return hypervisor

    @staticmethod
    def create_hypervisors(attrs={}, count=2):
        """Create multiple fake hypervisors.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of hypervisors to fake
        :return:
            A list of FakeResource objects faking the hypervisors
        """
        hypervisors = []
        for i in range(0, count):
            hypervisors.append(FakeHypervisor.create_one_hypervisor(attrs))

        return hypervisors


class FakehypervisorStats(object):
    """Fake one or more hypervisor stats."""

    @staticmethod
    def create_one_hypervisor_stats(attrs={}, methods={}):
        """Create a fake hypervisor stats.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, hypervisor_hostname, and so on
        """
        # Set default attributes.
        stats_info = {
            'count': 2,
            'current_workload': 0,
            'disk_available_least': 50,
            'free_disk_gb': 100,
            'free_ram_mb': 23000,
            'local_gb': 100,
            'local_gb_used': 0,
            'memory_mb': 23800,
            'memory_mb_used': 1400,
            'running_vms': 3,
            'vcpus': 8,
            'vcpus_used': 3,
        }
        stats_info.update(attrs)

        # Set default method.
        hypervisor_stats_method = {'to_dict': stats_info}
        hypervisor_stats_method.update(methods)

        hypervisor_stats = fakes.FakeResource(
            info=copy.deepcopy(stats_info),
            methods=copy.deepcopy(hypervisor_stats_method),
            loaded=True)
        return hypervisor_stats

    @staticmethod
    def create_hypervisors_stats(attrs={}, count=2):
        """Create multiple fake hypervisors stats.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of hypervisors to fake
        :return:
            A list of FakeResource objects faking the hypervisors
        """
        hypervisors = []
        for i in range(0, count):
            hypervisors.append(
                FakehypervisorStats.create_one_hypervisor_stats(attrs))

        return hypervisors


class FakeSecurityGroup(object):
    """Fake one or more security groups."""

    @staticmethod
    def create_one_security_group(attrs=None, methods=None):
        """Create a fake security group.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, etc.
        """
        if attrs is None:
            attrs = {}
        if methods is None:
            methods = {}

        # Set default attributes.
        security_group_attrs = {
            'id': 'security-group-id-' + uuid.uuid4().hex,
            'name': 'security-group-name-' + uuid.uuid4().hex,
            'description': 'security-group-description-' + uuid.uuid4().hex,
            'tenant_id': 'project-id-' + uuid.uuid4().hex,
            'rules': [],
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
    def create_security_groups(attrs=None, methods=None, count=2):
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
            'from_port': -1,
            'group': {},
            'id': 'security-group-rule-id-' + uuid.uuid4().hex,
            'ip_protocol': 'icmp',
            'ip_range': {'cidr': '0.0.0.0/0'},
            'parent_group_id': 'security-group-id-' + uuid.uuid4().hex,
            'to_port': -1,
        }

        # Overwrite default attributes.
        security_group_rule_attrs.update(attrs)

        # Set default methods.
        security_group_rule_methods = {}

        # Overwrite default methods.
        security_group_rule_methods.update(methods)

        security_group_rule = fakes.FakeResource(
            info=copy.deepcopy(security_group_rule_attrs),
            methods=copy.deepcopy(security_group_rule_methods),
            loaded=True)
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


class FakeServer(object):
    """Fake one or more compute servers."""

    @staticmethod
    def create_one_server(attrs={}, methods={}):
        """Create a fake server.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, metadata
        """
        # Set default attributes.
        server_info = {
            'id': 'server-id-' + uuid.uuid4().hex,
            'name': 'server-name-' + uuid.uuid4().hex,
            'metadata': {},
            'image': {
                'id': 'image-id-' + uuid.uuid4().hex,
            },
            'flavor': {
                'id': 'flavor-id-' + uuid.uuid4().hex,
            }
        }

        # Overwrite default attributes.
        server_info.update(attrs)

        server = fakes.FakeResource(info=copy.deepcopy(server_info),
                                    methods=methods,
                                    loaded=True)
        return server

    @staticmethod
    def create_servers(attrs={}, methods={}, count=2):
        """Create multiple fake servers.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :param int count:
            The number of servers to fake
        :return:
            A list of FakeResource objects faking the servers
        """
        servers = []
        for i in range(0, count):
            servers.append(FakeServer.create_one_server(attrs, methods))

        return servers

    @staticmethod
    def get_servers(servers=None, count=2):
        """Get an iterable MagicMock object with a list of faked servers.

        If servers list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List servers:
            A list of FakeResource objects faking servers
        :param int count:
            The number of servers to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            servers
        """
        if servers is None:
            servers = FakeServer.create_servers(count)
        return mock.MagicMock(side_effect=servers)


class FakeFlavorResource(fakes.FakeResource):
    """Fake flavor object's methods to help test.

    The flavor object has three methods to get, set, unset its properties.
    Need to fake them, otherwise the functions to be tested won't run properly.
    """

    def __init__(self, manager=None, info={}, loaded=False, methods={}):
        super(FakeFlavorResource, self).__init__(manager, info,
                                                 loaded, methods)
        # Fake properties.
        self._keys = {'property': 'value'}

    def set_keys(self, args):
        self._keys.update(args)

    def unset_keys(self, keys):
        for key in keys:
            self._keys.pop(key, None)

    def get_keys(self):
        return self._keys


class FakeFlavor(object):
    """Fake one or more flavors."""

    @staticmethod
    def create_one_flavor(attrs={}):
        """Create a fake flavor.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeFlavorResource object, with id, name, ram, vcpus, properties
        """
        # Set default attributes.
        flavor_info = {
            'id': 'flavor-id-' + uuid.uuid4().hex,
            'name': 'flavor-name-' + uuid.uuid4().hex,
            'ram': 8192,
            'vcpus': 4,
            'disk': 128,
            'swap': '',
            'rxtx_factor': '1.0',
            'OS-FLV-DISABLED:disabled': False,
            'os-flavor-access:is_public': True,
            'OS-FLV-EXT-DATA:ephemeral': 0,
        }

        # Overwrite default attributes.
        flavor_info.update(attrs)

        flavor = FakeFlavorResource(info=copy.deepcopy(flavor_info),
                                    loaded=True)

        # Set attributes with special mappings in nova client.
        flavor.disabled = flavor_info['OS-FLV-DISABLED:disabled']
        flavor.is_public = flavor_info['os-flavor-access:is_public']
        flavor.ephemeral = flavor_info['OS-FLV-EXT-DATA:ephemeral']

        return flavor

    @staticmethod
    def create_flavors(attrs={}, count=2):
        """Create multiple fake flavors.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of flavors to fake
        :return:
            A list of FakeFlavorResource objects faking the flavors
        """
        flavors = []
        for i in range(0, count):
            flavors.append(FakeFlavor.create_one_flavor(attrs))

        return flavors

    @staticmethod
    def get_flavors(flavors=None, count=2):
        """Get an iterable MagicMock object with a list of faked flavors.

        If flavors list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List flavors:
            A list of FakeFlavorResource objects faking flavors
        :param int count:
            The number of flavors to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            flavors
        """
        if flavors is None:
            flavors = FakeServer.create_flavors(count)
        return mock.MagicMock(side_effect=flavors)


class FakeAvailabilityZone(object):
    """Fake one or more compute availability zones (AZs)."""

    @staticmethod
    def create_one_availability_zone(attrs={}, methods={}):
        """Create a fake AZ.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object with zoneName, zoneState, etc.
        """
        # Set default attributes.
        host_name = uuid.uuid4().hex
        service_name = uuid.uuid4().hex
        service_updated_at = uuid.uuid4().hex
        availability_zone = {
            'zoneName': uuid.uuid4().hex,
            'zoneState': {'available': True},
            'hosts': {host_name: {service_name: {
                'available': True,
                'active': True,
                'updated_at': service_updated_at,
            }}},
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
            'ip': '1.0.9.0',
            'fixed_ip': '2.0.9.0',
            'instance_id': 'server-id-' + uuid.uuid4().hex,
            'pool': 'public',
        }

        # Overwrite default attributes.
        floating_ip_attrs.update(attrs)

        # Set default methods.
        floating_ip_methods = {}

        # Overwrite default methods.
        floating_ip_methods.update(methods)

        floating_ip = fakes.FakeResource(
            info=copy.deepcopy(floating_ip_attrs),
            methods=copy.deepcopy(floating_ip_methods),
            loaded=True)

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
            A FakeResource object, with id, label, cidr and so on
        """
        # Set default attributes.
        network_attrs = {
            'bridge': 'br100',
            'bridge_interface': None,
            'broadcast': '10.0.0.255',
            'cidr': '10.0.0.0/24',
            'cidr_v6': None,
            'created_at': '2016-02-11T11:17:37.000000',
            'deleted': False,
            'deleted_at': None,
            'dhcp_server': '10.0.0.1',
            'dhcp_start': '10.0.0.2',
            'dns1': '8.8.4.4',
            'dns2': None,
            'enable_dhcp': True,
            'gateway': '10.0.0.1',
            'gateway_v6': None,
            'host': None,
            'id': 'network-id-' + uuid.uuid4().hex,
            'injected': False,
            'label': 'network-label-' + uuid.uuid4().hex,
            'mtu': None,
            'multi_host': False,
            'netmask': '255.255.255.0',
            'netmask_v6': None,
            'priority': None,
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'rxtx_base': None,
            'share_address': False,
            'updated_at': None,
            'vlan': None,
            'vpn_private_address': None,
            'vpn_public_address': None,
            'vpn_public_port': None,
        }

        # Overwrite default attributes.
        network_attrs.update(attrs)

        # Set default methods.
        network_methods = {
            'keys': ['id', 'label', 'cidr'],
        }

        # Overwrite default methods.
        network_methods.update(methods)

        network = fakes.FakeResource(info=copy.deepcopy(network_attrs),
                                     methods=copy.deepcopy(network_methods),
                                     loaded=True)

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
