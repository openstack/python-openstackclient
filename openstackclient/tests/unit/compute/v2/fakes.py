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

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes

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
servgroup_num = 10
servgroup_members_num = 10
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
    'server-groups': servgroup_num,
    'server-group-members': servgroup_members_num
}

QUOTA_columns = tuple(sorted(QUOTA))
QUOTA_data = tuple(QUOTA[x] for x in sorted(QUOTA))


class FakeAggregate(object):
    """Fake one aggregate."""

    @staticmethod
    def create_one_aggregate(attrs=None):
        """Create a fake aggregate.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id and other attributes
        """
        attrs = attrs or {}

        # Set default attribute
        aggregate_info = {
            "name": "aggregate-name-" + uuid.uuid4().hex,
            "availability_zone": "ag_zone",
            "hosts": [],
            "id": "aggregate-id-" + uuid.uuid4().hex,
            "metadata": {
                "availability_zone": "ag_zone",
                "key1": "value1",
            }
        }

        # Overwrite default attributes.
        aggregate_info.update(attrs)

        aggregate = fakes.FakeResource(
            info=copy.deepcopy(aggregate_info),
            loaded=True)
        return aggregate

    @staticmethod
    def create_aggregates(attrs=None, count=2):
        """Create multiple fake aggregates.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of aggregates to fake
        :return:
            A list of FakeResource objects faking the aggregates
        """
        aggregates = []
        for i in range(0, count):
            aggregates.append(FakeAggregate.create_one_aggregate(attrs))

        return aggregates

    @staticmethod
    def get_aggregates(aggregates=None, count=2):
        """Get an iterable MagicMock object with a list of faked aggregates.

        If aggregates list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List aggregates:
            A list of FakeResource objects faking aggregates
        :param int count:
            The number of aggregates to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            aggregates
        """
        if aggregates is None:
            aggregates = FakeAggregate.create_aggregates(count)
        return mock.Mock(side_effect=aggregates)


class FakeComputev2Client(object):

    def __init__(self, **kwargs):
        self.agents = mock.Mock()
        self.agents.resource_class = fakes.FakeResource(None, {})

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

        self.flavor_access = mock.Mock()
        self.flavor_access.resource_class = fakes.FakeResource(None, {})

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

        self.floating_ip_pools = mock.Mock()
        self.floating_ip_pools.resource_class = fakes.FakeResource(None, {})

        self.networks = mock.Mock()
        self.networks.resource_class = fakes.FakeResource(None, {})

        self.keypairs = mock.Mock()
        self.keypairs.resource_class = fakes.FakeResource(None, {})

        self.hosts = mock.Mock()
        self.hosts.resource_class = fakes.FakeResource(None, {})

        self.server_groups = mock.Mock()
        self.server_groups.resource_class = fakes.FakeResource(None, {})

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


class FakeAgent(object):
    """Fake one or more agent."""

    @staticmethod
    def create_one_agent(attrs=None):
        """Create a fake agent.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with agent_id, os, and so on
        """

        attrs = attrs or {}

        # set default attributes.
        agent_info = {
            'agent_id': 'agent-id-' + uuid.uuid4().hex,
            'os': 'agent-os-' + uuid.uuid4().hex,
            'architecture': 'agent-architecture',
            'version': '8.0',
            'url': 'http://127.0.0.1',
            'md5hash': 'agent-md5hash',
            'hypervisor': 'hypervisor',
        }

        # Overwrite default attributes.
        agent_info.update(attrs)

        agent = fakes.FakeResource(info=copy.deepcopy(agent_info),
                                   loaded=True)
        return agent

    @staticmethod
    def create_agents(attrs=None, count=2):
        """Create multiple fake agents.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of agents to fake
        :return:
            A list of FakeResource objects faking the agents
        """
        agents = []
        for i in range(0, count):
            agents.append(FakeAgent.create_one_agent(attrs))

        return agents


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
            'namespace': (
                'http://docs.openstack.org/compute/ext/multinic/api/v1.1'),
            'description': 'description-' + uuid.uuid4().hex,
            'updated': '2014-01-07T12:00:0-00:00',
            'alias': 'NMN',
            'links': ('[{"href":'
                      '"https://github.com/openstack/compute-api", "type":'
                      ' "text/html", "rel": "describedby"}]')
        }

        # Overwrite default attributes.
        extension_info.update(attrs)

        extension = fakes.FakeResource(
            info=copy.deepcopy(extension_info),
            loaded=True)
        return extension


class FakeHypervisor(object):
    """Fake one or more hypervisor."""

    @staticmethod
    def create_one_hypervisor(attrs=None):
        """Create a fake hypervisor.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, hypervisor_hostname, and so on
        """
        attrs = attrs or {}

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
    def create_hypervisors(attrs=None, count=2):
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


class FakeHypervisorStats(object):
    """Fake one or more hypervisor stats."""

    @staticmethod
    def create_one_hypervisor_stats(attrs=None):
        """Create a fake hypervisor stats.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with count, current_workload, and so on
        """
        attrs = attrs or {}

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

        # Overwrite default attributes.
        stats_info.update(attrs)

        # Set default method.
        hypervisor_stats_method = {'to_dict': stats_info}

        hypervisor_stats = fakes.FakeResource(
            info=copy.deepcopy(stats_info),
            methods=copy.deepcopy(hypervisor_stats_method),
            loaded=True)
        return hypervisor_stats

    @staticmethod
    def create_hypervisors_stats(attrs=None, count=2):
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
                FakeHypervisorStats.create_one_hypervisor_stats(attrs))

        return hypervisors


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
            'rules': [],
        }

        # Overwrite default attributes.
        security_group_attrs.update(attrs)

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs),
            loaded=True)
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
        """Get an iterable MagicMock object with a list of faked security groups.

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
            'from_port': 0,
            'group': {},
            'id': 'security-group-rule-id-' + uuid.uuid4().hex,
            'ip_protocol': 'tcp',
            'ip_range': {'cidr': '0.0.0.0/0'},
            'parent_group_id': 'security-group-id-' + uuid.uuid4().hex,
            'to_port': 0,
        }

        # Overwrite default attributes.
        security_group_rule_attrs.update(attrs)

        security_group_rule = fakes.FakeResource(
            info=copy.deepcopy(security_group_rule_attrs),
            loaded=True)
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


class FakeServer(object):
    """Fake one or more compute servers."""

    @staticmethod
    def create_one_server(attrs=None, methods=None):
        """Create a fake server.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Dictionary methods:
            A dictionary with all methods
        :return:
            A FakeResource object, with id, name, metadata, and so on
        """
        attrs = attrs or {}
        methods = methods or {}

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
            },
            'OS-EXT-STS:power_state': 1,
        }

        # Overwrite default attributes.
        server_info.update(attrs)

        server = fakes.FakeResource(info=copy.deepcopy(server_info),
                                    methods=methods,
                                    loaded=True)
        return server

    @staticmethod
    def create_servers(attrs=None, methods=None, count=2):
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
        return mock.Mock(side_effect=servers)


class FakeService(object):
    """Fake one or more services."""

    @staticmethod
    def create_one_service(attrs=None):
        """Create a fake service.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, host, binary, and so on
        """
        attrs = attrs or {}

        # Set default attributes.
        service_info = {
            'id': 'id-' + uuid.uuid4().hex,
            'host': 'host-' + uuid.uuid4().hex,
            'binary': 'binary-' + uuid.uuid4().hex,
            'status': 'enabled',
            'zone': 'zone-' + uuid.uuid4().hex,
            'state': 'state-' + uuid.uuid4().hex,
            'updated_at': 'time-' + uuid.uuid4().hex,
            'disabled_reason': 'earthquake',
        }

        # Overwrite default attributes.
        service_info.update(attrs)

        service = fakes.FakeResource(info=copy.deepcopy(service_info),
                                     loaded=True)

        return service

    @staticmethod
    def create_services(attrs=None, count=2):
        """Create multiple fake services.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of services to fake
        :return:
            A list of FakeResource objects faking the services
        """
        services = []
        for i in range(0, count):
            services.append(FakeService.create_one_service(attrs))

        return services


class FakeFlavor(object):
    """Fake one or more flavors."""

    @staticmethod
    def create_one_flavor(attrs=None):
        """Create a fake flavor.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, ram, vcpus, and so on
        """
        attrs = attrs or {}

        # Set default attributes.
        flavor_info = {
            'id': 'flavor-id-' + uuid.uuid4().hex,
            'name': 'flavor-name-' + uuid.uuid4().hex,
            'ram': 8192,
            'vcpus': 4,
            'disk': 128,
            'swap': 0,
            'rxtx_factor': 1.0,
            'OS-FLV-DISABLED:disabled': False,
            'os-flavor-access:is_public': True,
            'OS-FLV-EXT-DATA:ephemeral': 0,
            'properties': {'property': 'value'},
        }

        # Overwrite default attributes.
        flavor_info.update(attrs)

        # Set default methods.
        flavor_methods = {
            'set_keys': None,
            'unset_keys': None,
            'get_keys': {'property': 'value'},
        }

        flavor = fakes.FakeResource(info=copy.deepcopy(flavor_info),
                                    methods=flavor_methods,
                                    loaded=True)

        # Set attributes with special mappings in nova client.
        flavor.disabled = flavor_info['OS-FLV-DISABLED:disabled']
        flavor.is_public = flavor_info['os-flavor-access:is_public']
        flavor.ephemeral = flavor_info['OS-FLV-EXT-DATA:ephemeral']

        return flavor

    @staticmethod
    def create_flavors(attrs=None, count=2):
        """Create multiple fake flavors.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of flavors to fake
        :return:
            A list of FakeResource objects faking the flavors
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
            A list of FakeResource objects faking flavors
        :param int count:
            The number of flavors to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            flavors
        """
        if flavors is None:
            flavors = FakeFlavor.create_flavors(count)
        return mock.Mock(side_effect=flavors)


class FakeFlavorAccess(object):
    """Fake one or more flavor accesses."""

    @staticmethod
    def create_one_flavor_access(attrs=None):
        """Create a fake flavor access.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with flavor_id, tenat_id
        """
        attrs = attrs or {}

        # Set default attributes.
        flavor_access_info = {
            'flavor_id': 'flavor-id-' + uuid.uuid4().hex,
            'tenant_id': 'tenant-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        flavor_access_info.update(attrs)

        flavor_access = fakes.FakeResource(
            info=copy.deepcopy(flavor_access_info), loaded=True)

        return flavor_access


class FakeKeypair(object):
    """Fake one or more keypairs."""

    @staticmethod
    def create_one_keypair(attrs=None, no_pri=False):
        """Create a fake keypair

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, name, fingerprint, and so on
        """
        attrs = attrs or {}

        # Set default attributes.
        keypair_info = {
            'name': 'keypair-name-' + uuid.uuid4().hex,
            'fingerprint': 'dummy',
            'public_key': 'dummy',
            'user_id': 'user'
        }
        if not no_pri:
            keypair_info['private_key'] = 'private_key'

        # Overwrite default attributes.
        keypair_info.update(attrs)

        keypair = fakes.FakeResource(info=copy.deepcopy(keypair_info),
                                     loaded=True)

        return keypair

    @staticmethod
    def create_keypairs(attrs=None, count=2):
        """Create multiple fake keypairs.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of keypairs to fake
        :return:
            A list of FakeResource objects faking the keypairs
        """

        keypairs = []
        for i in range(0, count):
            keypairs.append(FakeKeypair.create_one_keypair(attrs))

        return keypairs

    @staticmethod
    def get_keypairs(keypairs=None, count=2):
        """Get an iterable MagicMock object with a list of faked keypairs.

        If keypairs list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List keypairs:
            A list of FakeResource objects faking keypairs
        :param int count:
            The number of keypairs to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            keypairs
        """
        if keypairs is None:
            keypairs = FakeKeypair.create_keypairs(count)
        return mock.Mock(side_effect=keypairs)


class FakeAvailabilityZone(object):
    """Fake one or more compute availability zones (AZs)."""

    @staticmethod
    def create_one_availability_zone(attrs=None):
        """Create a fake AZ.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with zoneName, zoneState, etc.
        """
        attrs = attrs or {}

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
            'ip': '1.0.9.0',
            'fixed_ip': '2.0.9.0',
            'instance_id': 'server-id-' + uuid.uuid4().hex,
            'pool': 'public',
        }

        # Overwrite default attributes.
        floating_ip_attrs.update(attrs)

        floating_ip = fakes.FakeResource(
            info=copy.deepcopy(floating_ip_attrs),
            loaded=True)

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
        return mock.Mock(side_effect=floating_ips)


class FakeFloatingIPPool(object):
    """Fake one or more floating ip pools."""

    @staticmethod
    def create_one_floating_ip_pool(attrs=None):
        """Create a fake floating ip pool.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with name, etc
        """
        if attrs is None:
            attrs = {}

        # Set default attributes.
        floating_ip_pool_attrs = {
            'name': 'floating-ip-pool-name-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        floating_ip_pool_attrs.update(attrs)

        floating_ip_pool = fakes.FakeResource(
            info=copy.deepcopy(floating_ip_pool_attrs),
            loaded=True)

        return floating_ip_pool

    @staticmethod
    def create_floating_ip_pools(attrs=None, count=2):
        """Create multiple fake floating ip pools.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of floating ip pools to fake
        :return:
            A list of FakeResource objects faking the floating ip pools
        """
        floating_ip_pools = []
        for i in range(0, count):
            floating_ip_pools.append(
                FakeFloatingIPPool.create_one_floating_ip_pool(attrs)
            )
        return floating_ip_pools


class FakeNetwork(object):
    """Fake one or more networks."""

    @staticmethod
    def create_one_network(attrs=None):
        """Create a fake network.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, label, cidr and so on
        """
        attrs = attrs or {}

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

        network = fakes.FakeResource(info=copy.deepcopy(network_attrs),
                                     loaded=True)

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
            networks = FakeNetwork.create_networks(count=count)
        return mock.Mock(side_effect=networks)


class FakeHost(object):
    """Fake one host."""

    @staticmethod
    def create_one_host(attrs=None):
        """Create a fake host.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with uuid and other attributes
        """
        attrs = attrs or {}

        # Set default attributes.
        host_info = {
            "service_id": 1,
            "host": "host1",
            "uuid": 'host-id-' + uuid.uuid4().hex,
            "vcpus": 10,
            "memory_mb": 100,
            "local_gb": 100,
            "vcpus_used": 5,
            "memory_mb_used": 50,
            "local_gb_used": 10,
            "hypervisor_type": "xen",
            "hypervisor_version": 1,
            "hypervisor_hostname": "devstack1",
            "free_ram_mb": 50,
            "free_disk_gb": 50,
            "current_workload": 10,
            "running_vms": 1,
            "cpu_info": "",
            "disk_available_least": 1,
            "host_ip": "10.10.10.10",
            "supported_instances": "",
            "metrics": "",
            "pci_stats": "",
            "extra_resources": "",
            "stats": "",
            "numa_topology": "",
            "ram_allocation_ratio": 1.0,
            "cpu_allocation_ratio": 1.0,
            "zone": 'zone-' + uuid.uuid4().hex,
            "host_name": 'name-' + uuid.uuid4().hex,
            "service": 'service-' + uuid.uuid4().hex,
            "cpu": 4,
            "disk_gb": 100,
            'project': 'project-' + uuid.uuid4().hex,
        }
        host_info.update(attrs)
        host = fakes.FakeResource(
            info=copy.deepcopy(host_info),
            loaded=True)
        return host


class FakeServerGroup(object):
    """Fake one server group"""

    @staticmethod
    def create_one_server_group(attrs=None):
        """Create a fake server group

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id and other attributes
        """
        if attrs is None:
            attrs = {}

        # Set default attributes.
        server_group_info = {
            'id': 'server-group-id-' + uuid.uuid4().hex,
            'members': [],
            'metadata': {},
            'name': 'server-group-name-' + uuid.uuid4().hex,
            'policies': [],
            'project_id': 'server-group-project-id-' + uuid.uuid4().hex,
            'user_id': 'server-group-user-id-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        server_group_info.update(attrs)

        server_group = fakes.FakeResource(
            info=copy.deepcopy(server_group_info),
            loaded=True)
        return server_group
