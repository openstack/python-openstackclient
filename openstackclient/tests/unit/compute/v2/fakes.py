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
from unittest import mock
import uuid

from novaclient import api_versions
from openstack.compute.v2 import aggregate as _aggregate
from openstack.compute.v2 import availability_zone as _availability_zone
from openstack.compute.v2 import extension as _extension
from openstack.compute.v2 import flavor as _flavor
from openstack.compute.v2 import hypervisor as _hypervisor
from openstack.compute.v2 import keypair as _keypair
from openstack.compute.v2 import migration as _migration
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import server_action as _server_action
from openstack.compute.v2 import server_group as _server_group
from openstack.compute.v2 import server_interface as _server_interface
from openstack.compute.v2 import server_migration as _server_migration
from openstack.compute.v2 import service as _service
from openstack.compute.v2 import usage as _usage
from openstack.compute.v2 import volume_attachment as _volume_attachment

from openstackclient.api import compute_v2
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
    'server-group-members': servgroup_members_num,
}

QUOTA_columns = tuple(sorted(QUOTA))
QUOTA_data = tuple(QUOTA[x] for x in sorted(QUOTA))


class FakeComputev2Client(object):
    def __init__(self, **kwargs):
        self.agents = mock.Mock()
        self.agents.resource_class = fakes.FakeResource(None, {})

        self.images = mock.Mock()
        self.images.resource_class = fakes.FakeResource(None, {})

        self.limits = mock.Mock()
        self.limits.resource_class = fakes.FakeResource(None, {})

        self.servers = mock.Mock()
        self.servers.resource_class = fakes.FakeResource(None, {})

        self.services = mock.Mock()
        self.services.resource_class = fakes.FakeResource(None, {})

        self.extensions = mock.Mock()
        self.extensions.resource_class = fakes.FakeResource(None, {})

        self.flavors = mock.Mock()

        self.flavor_access = mock.Mock()
        self.flavor_access.resource_class = fakes.FakeResource(None, {})

        self.quotas = mock.Mock()
        self.quotas.resource_class = fakes.FakeResource(None, {})

        self.quota_classes = mock.Mock()
        self.quota_classes.resource_class = fakes.FakeResource(None, {})

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

        self.hosts = mock.Mock()
        self.hosts.resource_class = fakes.FakeResource(None, {})

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

        self.api_version = api_versions.APIVersion('2.1')


class TestComputev2(
    network_fakes.FakeClientMixin,
    image_fakes.FakeClientMixin,
    utils.TestCommand,
):
    def setUp(self):
        super().setUp()

        self.app.client_manager.compute = FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.compute.api = compute_v2.APIv2(
            session=self.app.client_manager.session,
            endpoint=fakes.AUTH_URL,
        )

        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.volume = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )


def create_one_aggregate(attrs=None):
    """Create a fake aggregate.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.aggregate.Aggregate object
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
        },
    }

    # Overwrite default attributes.
    aggregate_info.update(attrs)

    aggregate = _aggregate.Aggregate(**aggregate_info)
    return aggregate


def create_aggregates(attrs=None, count=2):
    """Create multiple fake aggregates.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of aggregates to fake
    :return: A list of fake openstack.compute.v2.aggregate.Aggregate objects
    """
    aggregates = []
    for i in range(0, count):
        aggregates.append(create_one_aggregate(attrs))

    return aggregates


def get_aggregates(aggregates=None, count=2):
    """Get an iterable MagicMock object with a list of faked aggregates.

    If aggregates list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :return: A list of fake openstack.compute.v2.aggregate.Aggregate objects
    :param int count: The number of aggregates to fake
    :return: An iterable Mock object with side_effect set to a list of faked
        aggregates
    """
    if aggregates is None:
        aggregates = create_aggregates(count)
    return mock.Mock(side_effect=aggregates)


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


def create_one_service(attrs=None):
    """Create a fake service.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.service.Service object
    """
    attrs = attrs or {}

    # Set default attributes.
    service_info = {
        'id': 'id-' + uuid.uuid4().hex,
        'host': 'host-' + uuid.uuid4().hex,
        'binary': 'binary-' + uuid.uuid4().hex,
        'status': 'enabled',
        'availability_zone': 'zone-' + uuid.uuid4().hex,
        'state': 'state-' + uuid.uuid4().hex,
        'updated_at': 'time-' + uuid.uuid4().hex,
        'disabled_reason': 'earthquake',
        # Introduced in API microversion 2.11
        'is_forced_down': False,
    }

    # Overwrite default attributes.
    service_info.update(attrs)

    return _service.Service(**service_info)


def create_services(attrs=None, count=2):
    """Create multiple fake services.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of services to fake
    :return:
        A list of FakeResource objects faking the services
    """
    services = []
    for i in range(0, count):
        services.append(create_one_service(attrs))

    return services


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


def create_one_keypair(attrs=None):
    """Create a fake keypair

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.keypair.Keypair object
    """
    attrs = attrs or {}

    # Set default attributes.
    keypair_info = {
        'name': 'keypair-name-' + uuid.uuid4().hex,
        'type': 'ssh',
        'fingerprint': 'dummy',
        'public_key': 'dummy',
        'user_id': 'user',
    }

    # Overwrite default attributes.
    keypair_info.update(attrs)

    return _keypair.Keypair(**keypair_info)


def create_keypairs(attrs=None, count=2):
    """Create multiple fake keypairs.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of keypairs to fake
    :return: A list of fake openstack.compute.v2.keypair.Keypair objects
    """

    keypairs = []
    for i in range(0, count):
        keypairs.append(create_one_keypair(attrs))

    return keypairs


def get_keypairs(keypairs=None, count=2):
    """Get an iterable MagicMock object with a list of faked keypairs.

    If keypairs list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param list keypairs: A list of fake openstack.compute.v2.keypair.Keypair
        objects
    :param int count: The number of keypairs to fake
    :return: An iterable Mock object with side_effect set to a list of faked
        keypairs
    """
    if keypairs is None:
        keypairs = create_keypairs(count)
    return mock.Mock(side_effect=keypairs)


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


def create_one_host(attrs=None):
    """Create a fake host.

    :param dict attrs:
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
    return host_info


def create_one_usage(attrs=None):
    """Create a fake usage.

    :param dict attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object, with tenant_id and other attributes
    """
    if attrs is None:
        attrs = {}

    # Set default attributes.
    usage_info = {
        'project_id': 'usage-tenant-id-' + uuid.uuid4().hex,
        'total_memory_mb_usage': 512.0,
        'total_vcpus_usage': 1.0,
        'total_local_gb_usage': 1.0,
        'server_usages': [
            {
                'ended_at': None,
                'flavor': 'usage-flavor-' + uuid.uuid4().hex,
                'hours': 1.0,
                'local_gb': 1,
                'memory_mb': 512,
                'name': 'usage-name-' + uuid.uuid4().hex,
                'instance_id': uuid.uuid4().hex,
                'state': 'active',
                'uptime': 3600,
                'vcpus': 1,
            }
        ],
    }

    # Overwrite default attributes.
    usage_info.update(attrs)

    return _usage.Usage(**usage_info)


def create_usages(attrs=None, count=2):
    """Create multiple fake services.

    :param dict attrs:
        A dictionary with all attributes
    :param int count:
        The number of services to fake
    :return:
        A list of FakeResource objects faking the services
    """
    usages = []
    for i in range(0, count):
        usages.append(create_one_usage(attrs))

    return usages


def create_one_comp_quota(attrs=None):
    """Create one quota"""

    attrs = attrs or {}

    quota_attrs = {
        'id': 'project-id-' + uuid.uuid4().hex,
        'cores': 20,
        'fixed_ips': 30,
        'injected_files': 100,
        'injected_file_content_bytes': 10240,
        'injected_file_path_bytes': 255,
        'instances': 50,
        'key_pairs': 20,
        'metadata_items': 10,
        'ram': 51200,
        'server_groups': 10,
        'server_group_members': 10,
    }

    quota_attrs.update(attrs)
    quota = fakes.FakeResource(info=copy.deepcopy(quota_attrs), loaded=True)

    quota.project_id = quota_attrs['id']

    return quota


def create_one_default_comp_quota(attrs=None):
    """Create one quota"""

    attrs = attrs or {}

    quota_attrs = {
        'id': 'project-id-' + uuid.uuid4().hex,
        'cores': 10,
        'fixed_ips': 10,
        'injected_files': 100,
        'injected_file_content_bytes': 10240,
        'injected_file_path_bytes': 255,
        'instances': 20,
        'key_pairs': 20,
        'metadata_items': 10,
        'ram': 51200,
        'server_groups': 10,
        'server_group_members': 10,
    }

    quota_attrs.update(attrs)
    quota = fakes.FakeResource(info=copy.deepcopy(quota_attrs), loaded=True)

    quota.project_id = quota_attrs['id']

    return quota


def create_one_comp_detailed_quota(attrs=None):
    """Create one quota"""

    attrs = attrs or {}

    quota_attrs = {
        'id': 'project-id-' + uuid.uuid4().hex,
        'cores': {'reserved': 0, 'in_use': 0, 'limit': 20},
        'fixed_ips': {'reserved': 0, 'in_use': 0, 'limit': 30},
        'injected_files': {'reserved': 0, 'in_use': 0, 'limit': 100},
        'injected_file_content_bytes': {
            'reserved': 0,
            'in_use': 0,
            'limit': 10240,
        },
        'injected_file_path_bytes': {
            'reserved': 0,
            'in_use': 0,
            'limit': 255,
        },
        'instances': {'reserved': 0, 'in_use': 0, 'limit': 50},
        'key_pairs': {'reserved': 0, 'in_use': 0, 'limit': 20},
        'metadata_items': {'reserved': 0, 'in_use': 0, 'limit': 10},
        'ram': {'reserved': 0, 'in_use': 0, 'limit': 51200},
        'server_groups': {'reserved': 0, 'in_use': 0, 'limit': 10},
        'server_group_members': {'reserved': 0, 'in_use': 0, 'limit': 10},
    }

    quota_attrs.update(attrs)
    quota = fakes.FakeResource(info=copy.deepcopy(quota_attrs), loaded=True)

    quota.project_id = quota_attrs['id']

    return quota


class FakeLimits(object):
    """Fake limits"""

    def __init__(self, absolute_attrs=None, rate_attrs=None):
        self.absolute_limits_attrs = {
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
        }
        absolute_attrs = absolute_attrs or {}
        self.absolute_limits_attrs.update(absolute_attrs)

        self.rate_limits_attrs = [
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
        ]

    @property
    def absolute(self):
        for name, value in self.absolute_limits_attrs.items():
            yield FakeAbsoluteLimit(name, value)

    def absolute_limits(self):
        reference_data = []
        for name, value in self.absolute_limits_attrs.items():
            reference_data.append((name, value))
        return reference_data

    @property
    def rate(self):
        for group in self.rate_limits_attrs:
            uri = group['uri']
            for rate in group['limit']:
                yield FakeRateLimit(
                    rate['verb'],
                    uri,
                    rate['value'],
                    rate['remaining'],
                    rate['unit'],
                    rate['next-available'],
                )

    def rate_limits(self):
        reference_data = []
        for group in self.rate_limits_attrs:
            uri = group['uri']
            for rate in group['limit']:
                reference_data.append(
                    (
                        rate['verb'],
                        uri,
                        rate['value'],
                        rate['remaining'],
                        rate['unit'],
                        rate['next-available'],
                    )
                )
        return reference_data


class FakeAbsoluteLimit(object):
    """Data model that represents an absolute limit"""

    def __init__(self, name, value):
        self.name = name
        self.value = value


class FakeRateLimit(object):
    """Data model that represents a flattened view of a single rate limit"""

    def __init__(self, verb, uri, value, remain, unit, next_available):
        self.verb = verb
        self.uri = uri
        self.value = value
        self.remain = remain
        self.unit = unit
        self.next_available = next_available


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


def create_one_hypervisor(attrs=None):
    """Create a fake hypervisor.

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.hypervisor.Hypervisor object
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

    hypervisor = _hypervisor.Hypervisor(**hypervisor_info, loaded=True)
    return hypervisor


def create_hypervisors(attrs=None, count=2):
    """Create multiple fake hypervisors.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of hypervisors to fake
    :return: A list of fake openstack.compute.v2.hypervisor.Hypervisor objects
    """
    hypervisors = []
    for i in range(0, count):
        hypervisors.append(create_one_hypervisor(attrs))

    return hypervisors


def create_one_server_group(attrs=None):
    """Create a fake server group

    :param dict attrs: A dictionary with all attributes
    :return: A fake openstack.compute.v2.server_group.ServerGroup object
    """
    if attrs is None:
        attrs = {}

    # Set default attributes.
    server_group_info = {
        'id': 'server-group-id-' + uuid.uuid4().hex,
        'member_ids': '',
        'metadata': {},
        'name': 'server-group-name-' + uuid.uuid4().hex,
        'project_id': 'server-group-project-id-' + uuid.uuid4().hex,
        'user_id': 'server-group-user-id-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    server_group_info.update(attrs)

    server_group = _server_group.ServerGroup(**server_group_info)
    return server_group


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
