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
import random
import re
from unittest import mock
import uuid

from keystoneauth1 import discover
from openstack.compute.v2 import _proxy
from openstack.compute.v2 import availability_zone as _availability_zone
from openstack.compute.v2 import extension as _extension
from openstack.compute.v2 import flavor as _flavor
from openstack.compute.v2 import limits as _limits
from openstack.compute.v2 import migration as _migration
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import server_action as _server_action
from openstack.compute.v2 import server_interface as _server_interface
from openstack.compute.v2 import server_migration as _server_migration
from openstack.compute.v2 import volume_attachment as _volume_attachment

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes


class FakeComputev2Client:
    def __init__(self, **kwargs):
        self.agents = mock.Mock()
        self.agents.resource_class = fakes.FakeResource(None, {})

        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})

        self.servers = mock.Mock()
        self.servers.resource_class = fakes.FakeResource(None, {})

        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})

        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})

        self.flavors = mock.Mock()

        self.flavor_access = mock.Mock()
        self.flavor_access.resource_class = fakes.FakeResource(None, {})

        self.usage = mock.Mock()
        self.usage.resource_class = fakes.FakeResource(None, {})

        self.volumes = mock.Mock()
        self.volumes.resource_class = fakes.FakeResource(None, {})

        self.hypervisors = mock.Mock()
        self.hypervisors.resource_class = fakes.FakeResource(None, {})

        self.hypervisors_stats = mock.Mock()
        self.hypervisors_stats.resource_class = fakes.FakeResource(None, {})

        self.keypairs = mock.Mock()
        self.keypairs.resource_class = fakes.FakeResource(None, {})

        self.server_groups = mock.Mock()
        self.server_groups.resource_class = fakes.FakeResource(None, {})

        self.server_migrations = mock.Mock()
        self.server_migrations.resource_class = fakes.FakeResource(None, {})

        self.instance_action = mock.Mock()
        self.instance_action.resource_class = fakes.FakeResource(None, {})

        self.migrations = mock.Mock()
        self.migrations.resource_class = fakes.FakeResource(None, {})

        self.auth_token = kwargs['token']

        self.management_url = kwargs['endpoint']


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.compute = mock.Mock(_proxy.Proxy)
        self.compute_client = self.app.client_manager.compute
        self.set_compute_api_version()  # default to the lowest

    def set_compute_api_version(self, version: str = '2.1'):
        """Set a fake server version.

        :param version: The fake microversion to "support". This should be a
            string of format '2.xx'.
        :returns: None
        """
        assert re.match(r'2.\d+', version)

        self.compute_client.default_microversion = version
        self.compute_client.get_endpoint_data.return_value = (
            discover.EndpointData(
                min_microversion='2.1',  # nova has not bumped this yet
                max_microversion=version,
            )
        )


class TestComputev2(
    network_fakes.FakeClientMixin,
    image_fakes.FakeClientMixin,
    volume_fakes.FakeClientMixin,
    identity_fakes.FakeClientMixin,
    FakeClientMixin,
    utils.TestCommand,
): ...


def create_one_agent(attrs=None):
    """Create a fake agent.

    :param dict attrs:
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

    agent = fakes.FakeResource(info=copy.deepcopy(agent_info), loaded=True)
    return agent


def create_agents(attrs=None, count=2):
    """Create multiple fake agents.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of agents to fake
    :return:
        A list of FakeResource objects faking the agents
    """
    agents = []
    for i in range(0, count):
        agents.append(create_one_agent(attrs))

    return agents


def create_one_extension(attrs=None):
    """Create a fake extension.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.extension.Extension object
    """
    attrs = attrs or {}

    # Set default attributes.
    extension_info = {
        'alias': 'NMN',
        'description': 'description-' + uuid.uuid4().hex,
        'links': [
            {
                "href": "https://github.com/openstack/compute-api",
                "type": "text/html",
                "rel": "describedby",
            }
        ],
        'name': 'name-' + uuid.uuid4().hex,
        'namespace': (
            'http://docs.openstack.org/compute/ext/multinic/api/v1.1'
        ),
        'updated_at': '2014-01-07T12:00:0-00:00',
    }

    # Overwrite default attributes.
    extension_info.update(attrs)

    extension = _extension.Extension(**extension_info)
    return extension


def create_one_security_group(attrs=None):
    """Create a fake security group.

    :param dict attrs:
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
    return security_group_attrs


def create_security_groups(attrs=None, count=2):
    """Create multiple fake security groups.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of security groups to fake
    :return:
        A list of FakeResource objects faking the security groups
    """
    security_groups = []
    for i in range(0, count):
        security_groups.append(create_one_security_group(attrs))

    return security_groups


def get_security_groups(security_groups=None, count=2):
    """Get an iterable MagicMock with a list of faked security groups.

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
        security_groups = create_security_groups(count)
    return mock.Mock(side_effect=security_groups)


def create_one_security_group_rule(attrs=None):
    """Create a fake security group rule.

    :param dict attrs:
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

    return security_group_rule_attrs


def create_security_group_rules(attrs=None, count=2):
    """Create multiple fake security group rules.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of security group rules to fake
    :return:
        A list of FakeResource objects faking the security group rules
    """
    security_group_rules = []
    for i in range(0, count):
        security_group_rules.append(create_one_security_group_rule(attrs))

    return security_group_rules


def create_one_server(attrs=None, methods=None):
    """Create a fake server.

    :param dict attrs:
        A dictionary with all attributes
    :param dict methods:
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

    server = fakes.FakeResource(
        info=copy.deepcopy(server_info), methods=methods, loaded=True
    )
    return server


def create_servers(attrs=None, methods=None, count=2):
    """Create multiple fake servers.

    :param dict attrs:
        A dictionary with all attributes
    :param dict methods:
        A dictionary with all methods
    :param int count:
        The number of servers to fake
    :return:
        A list of FakeResource objects faking the servers
    """
    servers = []
    for i in range(0, count):
        servers.append(create_one_server(attrs, methods))

    return servers


def create_one_sdk_server(attrs=None):
    """Create a fake server for testing migration to sdk

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.server.Server object,
    """
    attrs = attrs or {}

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
    server = _server.Server(**server_info)

    # Override methods
    server.trigger_crash_dump = mock.MagicMock()

    return server


def create_sdk_servers(attrs=None, count=2):
    """Create multiple fake servers for testing migration to sdk

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of servers to fake
    :return: A list of fake openstack.compute.v2.server.Server objects
    """
    servers = []
    for i in range(0, count):
        servers.append(create_one_sdk_server(attrs))

    return servers


def get_servers(servers=None, count=2):
    """Get an iterable MagicMock object with a list of faked servers.

    If servers list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param list servers: A list of fake openstack.compute.v2.server.Server
        objects
    :param int count:
        The number of servers to fake
    :return: An iterable Mock object with side_effect set to a list of faked
        servers
    """
    if servers is None:
        servers = create_servers(count)
    return mock.Mock(side_effect=servers)


def create_one_server_action(attrs=None):
    """Create a fake server action.

    :param attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.server_action.ServerAction object
    """
    attrs = attrs or {}

    # Set default attributes
    server_action_info = {
        "server_id": "server-event-" + uuid.uuid4().hex,
        "user_id": "user-id-" + uuid.uuid4().hex,
        "start_time": "2017-02-27T07:47:13.000000",
        "request_id": "req-" + uuid.uuid4().hex,
        "action": "create",
        "message": None,
        "project_id": "project-id-" + uuid.uuid4().hex,
        "events": [
            {
                "finish_time": "2017-02-27T07:47:25.000000",
                "start_time": "2017-02-27T07:47:15.000000",
                "traceback": None,
                "event": "compute__do_build_and_run_instance",
                "result": "Success",
            }
        ],
    }
    # Overwrite default attributes
    server_action_info.update(attrs)

    # We handle events separately since they're nested resources
    events = [
        _server_action.ServerActionEvent(**event)
        for event in server_action_info.pop('events')
    ]

    server_action = _server_action.ServerAction(
        **server_action_info,
        events=events,
    )
    return server_action


def create_one_flavor(attrs=None):
    """Create a fake flavor.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.flavor.Flavor object
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
        'description': 'description',
        'OS-FLV-EXT-DATA:ephemeral': 0,
        'extra_specs': {'property': 'value'},
    }

    # Overwrite default attributes.
    flavor_info.update(attrs)

    flavor = _flavor.Flavor(**flavor_info)

    return flavor


def create_flavors(attrs=None, count=2):
    """Create multiple fake flavors.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of flavors to fake
    :return: A list of fake openstack.compute.v2.flavor.Flavor objects
    """
    flavors = []
    for i in range(0, count):
        flavors.append(create_one_flavor(attrs))

    return flavors


def get_flavors(flavors=None, count=2):
    """Get an iterable MagicMock object with a list of faked flavors.

    If flavors list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param list flavors: A list of fake openstack.compute.v2.flavor.Flavor
        objects
    :param int count: The number of flavors to fake
    :return: An iterable Mock object with side_effect set to a list of faked
        flavors
    """
    if flavors is None:
        flavors = create_flavors(count)
    return mock.Mock(side_effect=flavors)


def create_one_flavor_access(attrs=None):
    """Create a fake flavor access.

    :param dict attrs:
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
        info=copy.deepcopy(flavor_access_info), loaded=True
    )

    return flavor_access


def create_one_availability_zone(attrs=None):
    """Create a fake AZ.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.availability_zone.AvailabilityZone
        object
    """
    attrs = attrs or {}

    # Set default attributes.
    host_name = uuid.uuid4().hex
    service_name = uuid.uuid4().hex
    availability_zone_info = {
        'name': uuid.uuid4().hex,
        'state': {'available': True},
        'hosts': {
            host_name: {
                service_name: {
                    'available': True,
                    'active': True,
                    'updated_at': '2023-01-01T00:00:00.000000',
                }
            }
        },
    }

    # Overwrite default attributes.
    availability_zone_info.update(attrs)

    availability_zone = _availability_zone.AvailabilityZone(
        **availability_zone_info
    )
    return availability_zone


def create_availability_zones(attrs=None, count=2):
    """Create multiple fake AZs.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of availability zones to fake
    :return: A list of fake
        openstack.compute.v2.availability_zone.AvailabilityZone objects
    """
    availability_zones = []
    for i in range(0, count):
        availability_zone = create_one_availability_zone(attrs)
        availability_zones.append(availability_zone)

    return availability_zones


def create_one_floating_ip(attrs=None):
    """Create a fake floating ip.

    :param dict attrs:
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

    return floating_ip_attrs


def create_floating_ips(attrs=None, count=2):
    """Create multiple fake floating ips.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of floating ips to fake
    :return:
        A list of FakeResource objects faking the floating ips
    """
    floating_ips = []
    for i in range(0, count):
        floating_ips.append(create_one_floating_ip(attrs))
    return floating_ips


def get_floating_ips(floating_ips=None, count=2):
    """Get an iterable MagicMock object with a list of faked floating ips.

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
        floating_ips = create_floating_ips(count)
    return mock.Mock(side_effect=floating_ips)


def create_one_floating_ip_pool(attrs=None):
    """Create a fake floating ip pool.

    :param dict attrs:
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

    return floating_ip_pool_attrs


def create_floating_ip_pools(attrs=None, count=2):
    """Create multiple fake floating ip pools.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of floating ip pools to fake
    :return:
        A list of FakeResource objects faking the floating ip pools
    """
    floating_ip_pools = []
    for i in range(0, count):
        floating_ip_pools.append(create_one_floating_ip_pool(attrs))
    return floating_ip_pools


def create_one_network(attrs=None):
    """Create a fake network.

    :param dict attrs:
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

    return network_attrs


def create_networks(attrs=None, count=2):
    """Create multiple fake networks.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of networks to fake
    :return:
        A list of FakeResource objects faking the networks
    """
    networks = []
    for i in range(0, count):
        networks.append(create_one_network(attrs))

    return networks


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
        networks = create_networks(count=count)
    return mock.Mock(side_effect=networks)


def create_limits(attrs=None):
    """Create a fake limits object."""
    attrs = attrs or {}

    limits_attrs = {
        'absolute': {
            'maxServerMeta': 128,
            'maxTotalInstances': 10,
            'maxPersonality': 5,
            'totalServerGroupsUsed': 0,
            'maxImageMeta': 128,
            'maxPersonalitySize': 10240,
            'maxTotalRAMSize': 51200,
            'maxServerGroups': 10,
            'maxSecurityGroupRules': 20,
            'maxTotalKeypairs': 100,
            'totalCoresUsed': 0,
            'totalRAMUsed': 0,
            'maxSecurityGroups': 10,
            'totalFloatingIpsUsed': 0,
            'totalInstancesUsed': 0,
            'maxServerGroupMembers': 10,
            'maxTotalFloatingIps': 10,
            'totalSecurityGroupsUsed': 0,
            'maxTotalCores': 20,
        },
        'rate': [
            {
                "uri": "*",
                "limit": [
                    {
                        "value": 10,
                        "verb": "POST",
                        "remaining": 2,
                        "unit": "MINUTE",
                        "next-available": "2011-12-15T22:42:45Z",
                    },
                    {
                        "value": 10,
                        "verb": "PUT",
                        "remaining": 2,
                        "unit": "MINUTE",
                        "next-available": "2011-12-15T22:42:45Z",
                    },
                    {
                        "value": 100,
                        "verb": "DELETE",
                        "remaining": 100,
                        "unit": "MINUTE",
                        "next-available": "2011-12-15T22:42:45Z",
                    },
                ],
            }
        ],
    }
    limits_attrs.update(attrs)

    limits = _limits.Limits(**limits_attrs)
    return limits


def create_one_migration(attrs=None):
    """Create a fake migration.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.migration.Migration object
    """
    attrs = attrs or {}

    # Set default attributes.
    migration_info = {
        "created_at": "2017-01-31T08:03:21.000000",
        "dest_compute": "compute-" + uuid.uuid4().hex,
        "dest_host": "10.0.2.15",
        "dest_node": "node-" + uuid.uuid4().hex,
        "id": random.randint(1, 999),
        "migration_type": "migration",
        "new_flavor_id": uuid.uuid4().hex,
        "old_flavor_id": uuid.uuid4().hex,
        "project_id": uuid.uuid4().hex,
        "server_id": uuid.uuid4().hex,
        "source_compute": "compute-" + uuid.uuid4().hex,
        "source_node": "node-" + uuid.uuid4().hex,
        "status": "migrating",
        "updated_at": "2017-01-31T08:03:25.000000",
        "user_id": uuid.uuid4().hex,
        "uuid": uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    migration_info.update(attrs)

    migration = _migration.Migration(**migration_info)
    return migration


def create_migrations(attrs=None, count=2):
    """Create multiple fake migrations.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of migrations to fake
    :return: A list of fake openstack.compute.v2.migration.Migration objects
    """
    migrations = []
    for i in range(0, count):
        migrations.append(create_one_migration(attrs))

    return migrations


def create_one_server_migration(attrs=None):
    """Create a fake server migration.

    :param dict attrs: A dictionary with all attributes
    :return A fake openstack.compute.v2.server_migration.ServerMigration object
    """
    attrs = attrs or {}

    # Set default attributes.

    migration_info = {
        "created_at": "2016-01-29T13:42:02.000000",
        "dest_compute": "compute2",
        "dest_host": "1.2.3.4",
        "dest_node": "node2",
        "id": random.randint(1, 999),
        "server_uuid": uuid.uuid4().hex,
        "source_compute": "compute1",
        "source_node": "node1",
        "status": "running",
        "memory_total_bytes": random.randint(1, 99999),
        "memory_processed_bytes": random.randint(1, 99999),
        "memory_remaining_bytes": random.randint(1, 99999),
        "disk_total_bytes": random.randint(1, 99999),
        "disk_processed_bytes": random.randint(1, 99999),
        "disk_remaining_bytes": random.randint(1, 99999),
        "updated_at": "2016-01-29T13:42:02.000000",
        # added in 2.59
        "uuid": uuid.uuid4().hex,
        # added in 2.80
        "user_id": uuid.uuid4().hex,
        "project_id": uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    migration_info.update(attrs)

    migration = _server_migration.ServerMigration(**migration_info)
    return migration


def create_server_migrations(attrs=None, methods=None, count=2):
    """Create multiple server migrations.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of server migrations to fake
    :return A list of fake
        openstack.compute.v2.server_migration.ServerMigration objects
    """
    migrations = []
    for i in range(0, count):
        migrations.append(create_one_server_migration(attrs, methods))

    return migrations


def create_one_volume_attachment(attrs=None):
    """Create a fake volume attachment.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.volume_attachment.VolumeAttachment
        object
    """
    attrs = attrs or {}

    # Set default attributes.
    volume_attachment_info = {
        "id": uuid.uuid4().hex,
        "device": "/dev/sdb",
        "server_id": uuid.uuid4().hex,
        "volume_id": uuid.uuid4().hex,
        # introduced in API microversion 2.70
        "tag": "foo",
        # introduced in API microversion 2.79
        "delete_on_termination": True,
        # introduced in API microversion 2.89
        "attachment_id": uuid.uuid4().hex,
        "bdm_id": uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    volume_attachment_info.update(attrs)

    return _volume_attachment.VolumeAttachment(**volume_attachment_info)


def create_volume_attachments(attrs=None, count=2):
    """Create multiple fake volume attachments.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of volume attachments to fake
    :return: A list of fake
        openstack.compute.v2.volume_attachment.VolumeAttachment objects
    """
    volume_attachments = []
    for i in range(0, count):
        volume_attachments.append(create_one_volume_attachment(attrs))

    return volume_attachments


def create_one_server_interface(attrs=None):
    """Create a fake SDK ServerInterface.

    :param dict attrs: A dictionary with all attributes
    :param dict methods: A dictionary with all methods
    :return: A fake openstack.compute.v2.server_interface.ServerInterface
        object
    """
    attrs = attrs or {}

    # Set default attributes.
    server_interface_info = {
        "fixed_ips": uuid.uuid4().hex,
        "mac_addr": "aa:aa:aa:aa:aa:aa",
        "net_id": uuid.uuid4().hex,
        "port_id": uuid.uuid4().hex,
        "port_state": "ACTIVE",
        "server_id": uuid.uuid4().hex,
        # introduced in API microversion 2.70
        "tag": "foo",
    }

    # Overwrite default attributes.
    server_interface_info.update(attrs)

    return _server_interface.ServerInterface(**server_interface_info)
