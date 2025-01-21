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

import copy
from random import choice
from random import randint
from unittest import mock
import uuid

from openstack.network.v2 import _proxy
from openstack.network.v2 import address_group as _address_group
from openstack.network.v2 import address_scope as _address_scope
from openstack.network.v2 import agent as network_agent
from openstack.network.v2 import auto_allocated_topology as allocated_topology
from openstack.network.v2 import availability_zone as _availability_zone
from openstack.network.v2 import extension as _extension
from openstack.network.v2 import flavor as _flavor
from openstack.network.v2 import local_ip as _local_ip
from openstack.network.v2 import local_ip_association as _local_ip_association
from openstack.network.v2 import ndp_proxy as _ndp_proxy
from openstack.network.v2 import network as _network
from openstack.network.v2 import network_ip_availability as _ip_availability
from openstack.network.v2 import network_segment_range as _segment_range
from openstack.network.v2 import port as _port
from openstack.network.v2 import rbac_policy as network_rbac
from openstack.network.v2 import security_group as _security_group
from openstack.network.v2 import segment as _segment
from openstack.network.v2 import service_profile as _service_profile
from openstack.network.v2 import trunk as _trunk

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils


RULE_TYPE_BANDWIDTH_LIMIT = 'bandwidth-limit'
RULE_TYPE_DSCP_MARKING = 'dscp-marking'
RULE_TYPE_MINIMUM_BANDWIDTH = 'minimum-bandwidth'
RULE_TYPE_MINIMUM_PACKET_RATE = 'minimum-packet-rate'
VALID_QOS_RULES = [
    RULE_TYPE_BANDWIDTH_LIMIT,
    RULE_TYPE_DSCP_MARKING,
    RULE_TYPE_MINIMUM_BANDWIDTH,
    RULE_TYPE_MINIMUM_PACKET_RATE,
]
VALID_DSCP_MARKS = [
    0,
    8,
    10,
    12,
    14,
    16,
    18,
    20,
    22,
    24,
    26,
    28,
    30,
    32,
    34,
    36,
    38,
    40,
    46,
    48,
    56,
]


class FakeClientMixin:
    def setUp(self):
        super().setUp()

        self.app.client_manager.network = mock.Mock(spec=_proxy.Proxy)
        self.network_client = self.app.client_manager.network


class TestNetworkV2(
    identity_fakes.FakeClientMixin,
    FakeClientMixin,
    utils.TestCommand,
): ...


def create_one_extension(attrs=None):
    """Create a fake extension.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An Extension object with name, namespace, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    extension_info = {
        'name': 'name-' + uuid.uuid4().hex,
        'description': 'description-' + uuid.uuid4().hex,
        'alias': 'Dystopian',
        'links': [],
        'updated_at': '2013-07-09T12:00:0-00:00',
    }

    # Overwrite default attributes.
    extension_info.update(attrs)

    extension = _extension.Extension(**extension_info)
    return extension


class FakeNetworkQosPolicy:
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
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'shared': False,
            'description': 'qos-policy-description-' + uuid.uuid4().hex,
            'rules': rules,
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        qos_policy_attrs.update(attrs)

        qos_policy = fakes.FakeResource(
            info=copy.deepcopy(qos_policy_attrs), loaded=True
        )

        # Set attributes with special mapping in OpenStack SDK.
        qos_policy.is_shared = qos_policy_attrs['shared']

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
                FakeNetworkQosPolicy.create_one_qos_policy(attrs)
            )

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


class FakeNetworkSecGroup:
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
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'description': 'security-group-description-' + uuid.uuid4().hex,
            'location': 'MUNCHMUNCHMUNCH',
        }

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs), loaded=True
        )

        return security_group


class FakeNetworkQosRule:
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
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'type': type,
            'location': 'MUNCHMUNCHMUNCH',
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
        elif type == RULE_TYPE_MINIMUM_PACKET_RATE:
            qos_rule_attrs['min_kpps'] = randint(1, 10000)
            qos_rule_attrs['direction'] = 'egress'

        # Overwrite default attributes.
        qos_rule_attrs.update(attrs)

        qos_rule = fakes.FakeResource(
            info=copy.deepcopy(qos_rule_attrs), loaded=True
        )

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
            qos_rules = FakeNetworkQosRule.create_qos_rules(count)
        return mock.Mock(side_effect=qos_rules)


class FakeNetworkQosRuleType:
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
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        qos_rule_type_attrs.update(attrs)

        return fakes.FakeResource(
            info=copy.deepcopy(qos_rule_type_attrs), loaded=True
        )

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
                FakeNetworkQosRuleType.create_one_qos_rule_type(attrs)
            )

        return qos_rule_types


class FakeRouter:
    """Fake one or more routers."""

    @staticmethod
    def create_one_router(attrs=None):
        """Create a fake router.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, admin_state_up,
            status, project_id
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
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'routes': [],
            'external_gateway_info': {},
            'availability_zone_hints': [],
            'availability_zones': [],
            'tags': [],
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        router_attrs.update(attrs)

        router = fakes.FakeResource(
            info=copy.deepcopy(router_attrs), loaded=True
        )

        # Set attributes with special mapping in OpenStack SDK.
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


class FakeSecurityGroup:
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
            'stateful': True,
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'security_group_rules': [],
            'tags': [],
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        security_group_attrs.update(attrs)

        security_group = fakes.FakeResource(
            info=copy.deepcopy(security_group_attrs), loaded=True
        )

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
                FakeSecurityGroup.create_one_security_group(attrs)
            )

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


class FakeSecurityGroupRule:
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
            'description': 'security-group-rule-description-'
            + uuid.uuid4().hex,
            'direction': 'ingress',
            'ether_type': 'IPv4',
            'id': 'security-group-rule-id-' + uuid.uuid4().hex,
            'port_range_max': None,
            'port_range_min': None,
            'protocol': None,
            'remote_group_id': None,
            'remote_address_group_id': None,
            'remote_ip_prefix': '0.0.0.0/0',
            'security_group_id': 'security-group-id-' + uuid.uuid4().hex,
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        security_group_rule_attrs.update(attrs)

        security_group_rule = fakes.FakeResource(
            info=copy.deepcopy(security_group_rule_attrs), loaded=True
        )

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
                FakeSecurityGroupRule.create_one_security_group_rule(attrs)
            )

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
                FakeSecurityGroupRule.create_security_group_rules(count)
            )
        return mock.Mock(side_effect=security_group_rules)


class FakeSubnet:
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
            'project_id': project_id,
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
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        subnet_attrs.update(attrs)

        subnet = fakes.FakeResource(
            info=copy.deepcopy(subnet_attrs), loaded=True
        )

        # Set attributes with special mappings in OpenStack SDK.
        subnet.is_dhcp_enabled = subnet_attrs['enable_dhcp']
        subnet.subnet_pool_id = subnet_attrs['subnetpool_id']

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


class FakeFloatingIP:
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
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'description': 'floating-ip-description-' + uuid.uuid4().hex,
            'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
            'tags': [],
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        floating_ip_attrs.update(attrs)

        floating_ip = fakes.FakeResource(
            info=copy.deepcopy(floating_ip_attrs), loaded=True
        )

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


class FakeNetworkMeter:
    """Fake network meter"""

    @staticmethod
    def create_one_meter(attrs=None):
        """Create metering pool"""
        attrs = attrs or {}

        meter_attrs = {
            'id': 'meter-id-' + uuid.uuid4().hex,
            'name': 'meter-name-' + uuid.uuid4().hex,
            'description': 'meter-description-' + uuid.uuid4().hex,
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'shared': False,
            'location': 'MUNCHMUNCHMUNCH',
        }

        meter_attrs.update(attrs)

        meter = fakes.FakeResource(
            info=copy.deepcopy(meter_attrs), loaded=True
        )

        return meter

    @staticmethod
    def create_meter(attrs=None, count=2):
        """Create multiple meters"""

        meters = []
        for i in range(0, count):
            meters.append(FakeNetworkMeter.create_one_meter(attrs))
        return meters

    @staticmethod
    def get_meter(meter=None, count=2):
        """Get a list of meters"""
        if meter is None:
            meter = FakeNetworkMeter.create_meter(count)
        return mock.Mock(side_effect=meter)


class FakeNetworkMeterRule:
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
            'source_ip_prefix': '8.8.8.8/32',
            'destination_ip_prefix': '10.0.0.0/24',
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'location': 'MUNCHMUNCHMUNCH',
        }

        meter_rule_attrs.update(attrs)

        meter_rule = fakes.FakeResource(
            info=copy.deepcopy(meter_rule_attrs), loaded=True
        )

        return meter_rule

    @staticmethod
    def create_meter_rule(attrs=None, count=2):
        """Create multiple meter rules"""

        meter_rules = []
        for i in range(0, count):
            meter_rules.append(FakeNetworkMeterRule.create_one_rule(attrs))
        return meter_rules

    @staticmethod
    def get_meter_rule(meter_rule=None, count=2):
        """Get a list of meter rules"""
        if meter_rule is None:
            meter_rule = FakeNetworkMeterRule.create_meter_rule(count)
        return mock.Mock(side_effect=meter_rule)


class FakeSubnetPool:
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
            'project_id': 'project-id-' + uuid.uuid4().hex,
            'is_default': False,
            'shared': False,
            'max_prefixlen': '32',
            'min_prefixlen': '8',
            'default_quota': None,
            'ip_version': '4',
            'description': 'subnet-pool-description-' + uuid.uuid4().hex,
            'tags': [],
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        subnet_pool_attrs.update(attrs)

        subnet_pool = fakes.FakeResource(
            info=copy.deepcopy(subnet_pool_attrs), loaded=True
        )

        # Set attributes with special mapping in OpenStack SDK.
        subnet_pool.default_prefix_length = subnet_pool_attrs[
            'default_prefixlen'
        ]
        subnet_pool.is_shared = subnet_pool_attrs['shared']
        subnet_pool.maximum_prefix_length = subnet_pool_attrs['max_prefixlen']
        subnet_pool.minimum_prefix_length = subnet_pool_attrs['min_prefixlen']

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
            subnet_pools.append(FakeSubnetPool.create_one_subnet_pool(attrs))

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


class FakeNetworkServiceProvider:
    """Fake Network Service Providers"""

    @staticmethod
    def create_one_network_service_provider(attrs=None):
        """Create service provider"""
        attrs = attrs or {}

        service_provider = {
            'name': 'provider-name-' + uuid.uuid4().hex,
            'service_type': 'service-type-' + uuid.uuid4().hex,
            'default': False,
            'location': 'MUNCHMUNCHMUNCH',
        }

        service_provider.update(attrs)

        provider = fakes.FakeResource(
            info=copy.deepcopy(service_provider), loaded=True
        )
        provider.is_default = service_provider['default']

        return provider

    @staticmethod
    def create_network_service_providers(attrs=None, count=2):
        """Create multiple service providers"""

        service_providers = []
        for i in range(0, count):
            service_providers.append(
                FakeNetworkServiceProvider.create_one_network_service_provider(
                    attrs
                )
            )
        return service_providers


class FakeFloatingIPPortForwarding:
    """Fake one or more Port forwarding"""

    @staticmethod
    def create_one_port_forwarding(attrs=None, use_range=False):
        """Create a fake Port Forwarding.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param Boolean use_range:
            A boolean which defines if we will use ranges or not
        :return:
            A FakeResource object with name, id, etc.
        """
        attrs = attrs or {}
        floatingip_id = (
            attrs.get('floatingip_id') or 'floating-ip-id-' + uuid.uuid4().hex
        )
        # Set default attributes.
        port_forwarding_attrs = {
            'id': uuid.uuid4().hex,
            'floatingip_id': floatingip_id,
            'internal_port_id': 'internal-port-id-' + uuid.uuid4().hex,
            'internal_ip_address': '192.168.1.2',
            'protocol': 'tcp',
            'description': 'some description',
            'location': 'MUNCHMUNCHMUNCH',
        }

        if use_range:
            port_range = randint(0, 100)
            internal_start = randint(1, 65535 - port_range)
            internal_end = internal_start + port_range
            internal_range = ':'.join(map(str, [internal_start, internal_end]))
            external_start = randint(1, 65535 - port_range)
            external_end = external_start + port_range
            external_range = ':'.join(map(str, [external_start, external_end]))
            port_forwarding_attrs['internal_port_range'] = internal_range
            port_forwarding_attrs['external_port_range'] = external_range
            port_forwarding_attrs['internal_port'] = None
            port_forwarding_attrs['external_port'] = None
        else:
            port_forwarding_attrs['internal_port'] = randint(1, 65535)
            port_forwarding_attrs['external_port'] = randint(1, 65535)
            port_forwarding_attrs['internal_port_range'] = ''
            port_forwarding_attrs['external_port_range'] = ''

        # Overwrite default attributes.
        port_forwarding_attrs.update(attrs)

        port_forwarding = fakes.FakeResource(
            info=copy.deepcopy(port_forwarding_attrs), loaded=True
        )
        return port_forwarding

    @staticmethod
    def create_port_forwardings(attrs=None, count=2, use_range=False):
        """Create multiple fake Port Forwarding.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of Port Forwarding rule to fake
        :param Boolean use_range:
            A boolean which defines if we will use ranges or not
        :return:
            A list of FakeResource objects faking the Port Forwardings
        """
        port_forwardings = []
        for i in range(0, count):
            port_forwardings.append(
                FakeFloatingIPPortForwarding.create_one_port_forwarding(
                    attrs, use_range=use_range
                )
            )
        return port_forwardings

    @staticmethod
    def get_port_forwardings(port_forwardings=None, count=2, use_range=False):
        """Get a list of faked Port Forwardings.

        If port forwardings list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List port forwardings:
            A list of FakeResource objects faking port forwardings
        :param int count:
            The number of Port Forwardings to fake
        :param Boolean use_range:
            A boolean which defines if we will use ranges or not
        :return:
            An iterable Mock object with side_effect set to a list of faked
            Port Forwardings
        """
        if port_forwardings is None:
            port_forwardings = (
                FakeFloatingIPPortForwarding.create_port_forwardings(
                    count, use_range=use_range
                )
            )

        return mock.Mock(side_effect=port_forwardings)


class FakeL3ConntrackHelper:
    """Fake one or more L3 conntrack helper"""

    @staticmethod
    def create_one_l3_conntrack_helper(attrs=None):
        """Create a fake L3 conntrack helper.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object with protocol, port, etc.
        """
        attrs = attrs or {}
        router_id = attrs.get('router_id') or 'router-id-' + uuid.uuid4().hex
        # Set default attributes.
        ct_attrs = {
            'id': uuid.uuid4().hex,
            'router_id': router_id,
            'helper': 'tftp',
            'protocol': 'tcp',
            'port': randint(1, 65535),
            'location': 'MUNCHMUNCHMUNCH',
        }

        # Overwrite default attributes.
        ct_attrs.update(attrs)

        ct = fakes.FakeResource(info=copy.deepcopy(ct_attrs), loaded=True)
        return ct

    @staticmethod
    def create_l3_conntrack_helpers(attrs=None, count=2):
        """Create multiple fake L3 Conntrack helpers.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of L3 Conntrack helper rule to fake
        :return:
            A list of FakeResource objects faking the Conntrack helpers
        """
        ct_helpers = []
        for i in range(0, count):
            ct_helpers.append(
                FakeL3ConntrackHelper.create_one_l3_conntrack_helper(attrs)
            )
        return ct_helpers

    @staticmethod
    def get_l3_conntrack_helpers(ct_helpers=None, count=2):
        """Get a list of faked L3 Conntrack helpers.

        If ct_helpers list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List ct_helpers:
            A list of FakeResource objects faking conntrack helpers
        :param int count:
            The number of L3 conntrack helpers to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            L3 conntrack helpers
        """
        if ct_helpers is None:
            ct_helpers = FakeL3ConntrackHelper.create_l3_conntrack_helpers(
                count
            )

        return mock.Mock(side_effect=ct_helpers)


def create_one_address_group(attrs=None):
    """Create a fake address group.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An AddressGroup object with name, id, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    address_group_attrs = {
        'name': 'address-group-name-' + uuid.uuid4().hex,
        'description': 'address-group-description-' + uuid.uuid4().hex,
        'id': 'address-group-id-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'addresses': ['10.0.0.1/32'],
        'location': 'MUNCHMUNCHMUNCH',
    }

    # Overwrite default attributes.
    address_group_attrs.update(attrs)

    address_group = _address_group.AddressGroup(**address_group_attrs)

    return address_group


def create_address_groups(attrs=None, count=2):
    """Create multiple fake address groups.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of address groups to fake
    :return:
        A list of AddressGroup objects faking the address groups
    """
    address_groups = []
    for i in range(0, count):
        address_groups.append(create_one_address_group(attrs))

    return address_groups


def get_address_groups(address_groups=None, count=2):
    """Get an iterable Mock object with a list of faked address groups.

    If address groups list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :param List address_groups:
        A list of FakeResource objects faking address groups
    :param int count:
        The number of address groups to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        AddressGroup objects
    """
    if address_groups is None:
        address_groups = create_address_groups(count)
    return mock.Mock(side_effect=address_groups)


def create_one_address_scope(attrs=None):
    """Create a fake address scope.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An AddressScope object with name, id, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    address_scope_attrs = {
        'name': 'address-scope-name-' + uuid.uuid4().hex,
        'id': 'address-scope-id-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'shared': False,
        'ip_version': 4,
        'location': 'MUNCHMUNCHMUNCH',
    }

    # Overwrite default attributes.
    address_scope_attrs.update(attrs)

    address_scope = _address_scope.AddressScope(**address_scope_attrs)

    # Set attributes with special mapping in OpenStack SDK.
    address_scope.is_shared = address_scope_attrs['shared']

    return address_scope


def create_address_scopes(attrs=None, count=2):
    """Create multiple fake address scopes.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of address scopes to fake
    :return:
        A list of AddressScope objects faking the address scopes
    """
    address_scopes = []
    for i in range(0, count):
        address_scopes.append(create_one_address_scope(attrs))

    return address_scopes


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
        AddressScope objects
    """
    if address_scopes is None:
        address_scopes = create_address_scopes(count)
    return mock.Mock(side_effect=address_scopes)


def create_one_topology(attrs=None):
    attrs = attrs or {}

    auto_allocated_topology_attrs = {
        'id': 'network-id-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
    }

    auto_allocated_topology_attrs.update(attrs)

    auto_allocated_topology = allocated_topology.AutoAllocatedTopology(
        **auto_allocated_topology_attrs
    )

    return auto_allocated_topology


def create_one_availability_zone(attrs=None):
    """Create a fake AZ.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An AvailabilityZone object with name, state, etc.
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

    availability_zone = _availability_zone.AvailabilityZone(
        **availability_zone
    )
    return availability_zone


def create_availability_zones(attrs=None, count=2):
    """Create multiple fake AZs.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of AZs to fake
    :return:
        A list of AvailabilityZone objects faking the AZs
    """
    availability_zones = []
    for i in range(0, count):
        availability_zone = create_one_availability_zone(attrs)
        availability_zones.append(availability_zone)

    return availability_zones


def create_one_ip_availability(attrs=None):
    """Create a fake list with ip availability stats of a network.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A NetworkIPAvailability object with network_name, network_id, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    network_ip_attrs = {
        'network_id': 'network-id-' + uuid.uuid4().hex,
        'network_name': 'network-name-' + uuid.uuid4().hex,
        'project_id': '',
        'subnet_ip_availability': [],
        'total_ips': 254,
        'used_ips': 6,
        'location': 'MUNCHMUNCHMUNCH',
    }
    network_ip_attrs.update(attrs)

    network_ip_availability = _ip_availability.NetworkIPAvailability(
        **network_ip_attrs
    )

    return network_ip_availability


def create_ip_availability(count=2):
    """Create fake list of ip availability stats of multiple networks.

    :param int count:
        The number of networks to fake
    :return:
        A list of NetworkIPAvailability objects faking
        network ip availability stats
    """
    network_ip_availabilities = []
    for i in range(0, count):
        network_ip_availability = create_one_ip_availability()
        network_ip_availabilities.append(network_ip_availability)

    return network_ip_availabilities


def create_one_network(attrs=None):
    """Create a fake network.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An Network object, with id, name, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    network_attrs = {
        'created_at': '2021-11-29T10:10:23.000000',
        'id': 'network-id-' + uuid.uuid4().hex,
        'name': 'network-name-' + uuid.uuid4().hex,
        'status': 'ACTIVE',
        'description': 'network-description-' + uuid.uuid4().hex,
        'dns_domain': 'example.org.',
        'mtu': '1350',
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'admin_state_up': True,
        'shared': False,
        'subnets': ['a', 'b'],
        'segments': 'network-segment-' + uuid.uuid4().hex,
        'provider:network_type': 'vlan',
        'provider:physical_network': 'physnet1',
        'provider:segmentation_id': "400",
        'router:external': True,
        'availability_zones': [],
        'availability_zone_hints': [],
        'is_default': False,
        'is_vlan_transparent': True,
        'is_vlan_qinq': False,
        'port_security_enabled': True,
        'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
        'ipv4_address_scope': 'ipv4' + uuid.uuid4().hex,
        'ipv6_address_scope': 'ipv6' + uuid.uuid4().hex,
        'tags': [],
        'location': 'MUNCHMUNCHMUNCH',
        'updated_at': '2021-11-29T10:10:25.000000',
    }

    # Overwrite default attributes.
    network_attrs.update(attrs)

    network = _network.Network(**network_attrs)

    return network


def create_networks(attrs=None, count=2):
    """Create multiple fake networks.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of networks to fake
    :return:
        A list of Network objects faking the networks
    """
    networks = []
    for i in range(0, count):
        networks.append(create_one_network(attrs))

    return networks


def get_networks(networks=None, count=2):
    """Get an iterable Mock object with a list of faked networks.

    If networks list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List networks:
        A list of Network objects faking networks
    :param int count:
        The number of networks to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        networks
    """
    if networks is None:
        networks = create_networks(count)
    return mock.Mock(side_effect=networks)


def create_one_network_flavor(attrs=None):
    """Create a fake network flavor.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A Flavor object faking the network flavor
    """
    attrs = attrs or {}

    fake_uuid = uuid.uuid4().hex
    network_flavor_attrs = {
        'description': 'network-flavor-description-' + fake_uuid,
        'is_enabled': True,
        'id': 'network-flavor-id-' + fake_uuid,
        'name': 'network-flavor-name-' + fake_uuid,
        'service_type': 'vpn',
        'location': 'MUNCHMUNCHMUNCH',
    }

    # Overwrite default attributes.
    network_flavor_attrs.update(attrs)

    network_flavor = _flavor.Flavor(**network_flavor_attrs)

    return network_flavor


def create_flavor(attrs=None, count=2):
    """Create multiple fake network flavors.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of network flavors to fake
    :return:
        A list of Flavor objects faking the network falvors
    """
    network_flavors = []
    for i in range(0, count):
        network_flavors.append(create_one_network_flavor(attrs))

    return network_flavors


def get_flavor(network_flavors=None, count=2):
    """Get a list of flavors."""
    if network_flavors is None:
        network_flavors = create_flavor(count)
    return mock.Mock(side_effect=network_flavors)


def create_one_network_segment(attrs=None):
    """Create a fake network segment.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An Segment object faking the network segment
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
        'location': 'MUNCHMUNCHMUNCH',
    }

    # Overwrite default attributes.
    network_segment_attrs.update(attrs)

    network_segment = _segment.Segment(**network_segment_attrs)

    return network_segment


def create_network_segments(attrs=None, count=2):
    """Create multiple fake network segments.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of network segments to fake
    :return:
        A list of Segment objects faking the network segments
    """
    network_segments = []
    for i in range(0, count):
        network_segments.append(create_one_network_segment(attrs))
    return network_segments


def create_one_network_segment_range(attrs=None):
    """Create a fake network segment range.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A NetworkSegmentRange object faking the network segment range
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
        'used': {
            104: '3312e4ba67864b2eb53f3f41432f8efc',
            106: '3312e4ba67864b2eb53f3f41432f8efc',
        },
        'available': [100, 101, 102, 103, 105],
        'location': 'MUNCHMUNCHMUNCH',
    }

    # Overwrite default attributes.
    network_segment_range_attrs.update(attrs)

    network_segment_range = _segment_range.NetworkSegmentRange(
        **network_segment_range_attrs
    )

    return network_segment_range


def create_network_segment_ranges(attrs=None, count=2):
    """Create multiple fake network segment ranges.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of network segment ranges to fake
    :return:
        A list of NetworkSegmentRange objects faking
        the network segment ranges
    """
    network_segment_ranges = []
    for i in range(0, count):
        network_segment_ranges.append(create_one_network_segment_range(attrs))
    return network_segment_ranges


def create_one_port(attrs=None):
    """Create a fake port.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A Port object, with id, name, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    port_attrs = {
        'is_admin_state_up': True,
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
        'device_profile': 'cyborg_device_profile_1',
        'dns_assignment': [{}],
        'dns_domain': 'dns-domain-' + uuid.uuid4().hex,
        'dns_name': 'dns-name-' + uuid.uuid4().hex,
        'extra_dhcp_opts': [{}],
        'fixed_ips': [
            {
                'ip_address': '10.0.0.3',
                'subnet_id': 'subnet-id-' + uuid.uuid4().hex,
            }
        ],
        'hardware_offload_type': None,
        'hints': {},
        'id': 'port-id-' + uuid.uuid4().hex,
        'mac_address': 'fa:16:3e:a9:4e:72',
        'name': 'port-name-' + uuid.uuid4().hex,
        'network_id': 'network-id-' + uuid.uuid4().hex,
        'numa_affinity_policy': 'required',
        'is_port_security_enabled': True,
        'security_group_ids': [],
        'status': 'ACTIVE',
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'qos_network_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
        'qos_policy_id': 'qos-policy-id-' + uuid.uuid4().hex,
        'tags': [],
        'trusted': None,
        'propagate_uplink_status': False,
        'location': 'MUNCHMUNCHMUNCH',
        'trunk_details': {},
    }

    # Overwrite default attributes.
    port_attrs.update(attrs)

    port = _port.Port(**port_attrs)

    return port


def create_ports(attrs=None, count=2):
    """Create multiple fake ports.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of ports to fake
    :return:
        A list of Port objects faking the ports
    """
    ports = []
    for i in range(0, count):
        ports.append(create_one_port(attrs))

    return ports


def get_ports(ports=None, count=2):
    """Get an iterable Mock object with a list of faked ports.

    If ports list is provided, then initialize the Mock object with the
    list. Otherwise create one.

    :param List ports:
        A list of Port objects faking ports
    :param int count:
        The number of ports to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        ports
    """
    if ports is None:
        ports = create_ports(count)
    return mock.Mock(side_effect=ports)


def create_one_network_agent(attrs=None):
    """Create a fake network agent

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        An Agent object, with id, agent_type, and so on.
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
        'location': 'MUNCHMUNCHMUNCH',
    }
    agent_attrs.update(attrs)
    agent = network_agent.Agent(**agent_attrs)

    return agent


def create_network_agents(attrs=None, count=2):
    """Create multiple fake network agents.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of network agents to fake
    :return:
        A list of Agent objects faking the network agents
    """
    agents = []
    for i in range(0, count):
        agents.append(create_one_network_agent(attrs))

    return agents


def get_network_agents(agents=None, count=2):
    """Get an iterable Mock object with a list of faked network agents.

    If network agents list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :param List agents:
        A list of Agent objects faking network agents
    :param int count:
        The number of network agents to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        network agents
    """
    if agents is None:
        agents = create_network_agents(count)
    return mock.Mock(side_effect=agents)


def create_one_network_rbac(attrs=None):
    """Create a fake network rbac

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A RBACPolicy object, with id, action, target_tenant,
        project_id, type
    """
    attrs = attrs or {}

    # Set default attributes
    rbac_attrs = {
        'id': 'rbac-id-' + uuid.uuid4().hex,
        'object_type': 'network',
        'object_id': 'object-id-' + uuid.uuid4().hex,
        'action': 'access_as_shared',
        'target_tenant': 'target-tenant-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'location': 'MUNCHMUNCHMUNCH',
    }

    rbac_attrs.update(attrs)
    rbac = network_rbac.RBACPolicy(**rbac_attrs)

    return rbac


def create_network_rbacs(attrs=None, count=2):
    """Create multiple fake network rbac policies.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of rbac policies to fake
    :return:
        A list of RBACPolicy objects faking the rbac policies
    """
    rbac_policies = []
    for i in range(0, count):
        rbac_policies.append(create_one_network_rbac(attrs))

    return rbac_policies


def get_network_rbacs(rbac_policies=None, count=2):
    """Get an iterable Mock object with a list of faked rbac policies.

    If rbac policies list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :param List rbac_policies:
        A list of RBACPolicy objects faking rbac policies
    :param int count:
        The number of rbac policies to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        rbac policies
    """
    if rbac_policies is None:
        rbac_policies = create_network_rbacs(count)
    return mock.Mock(side_effect=rbac_policies)


def create_one_security_group(attrs=None):
    """Create a security group."""
    attrs = attrs or {}

    security_group_attrs = {
        'name': 'security-group-name-' + uuid.uuid4().hex,
        'id': 'security-group-id-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'description': 'security-group-description-' + uuid.uuid4().hex,
        'location': 'MUNCHMUNCHMUNCH',
    }

    security_group_attrs.update(attrs)

    security_group = _security_group.SecurityGroup(**security_group_attrs)

    return security_group


def create_security_groups(attrs=None, count=2):
    """Create multiple fake security groups.

    :param dict attrs: A dictionary with all attributes
    :param int count: The number of security groups to fake
    :return: A list of fake SecurityGroup objects
    """
    security_groups = []
    for i in range(0, count):
        security_groups.append(create_one_security_group(attrs))

    return security_groups


def create_one_service_profile(attrs=None):
    """Create service profile."""
    attrs = attrs or {}

    service_profile_attrs = {
        'id': 'flavor-profile-id' + uuid.uuid4().hex,
        'description': 'flavor-profile-description-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'driver': 'driver-' + uuid.uuid4().hex,
        'metainfo': 'metainfo-' + uuid.uuid4().hex,
        'enabled': True,
        'location': 'MUNCHMUNCHMUNCH',
    }

    service_profile_attrs.update(attrs)

    flavor_profile = _service_profile.ServiceProfile(**service_profile_attrs)

    return flavor_profile


def create_service_profile(attrs=None, count=2):
    """Create multiple service profiles."""

    service_profiles = []
    for i in range(0, count):
        service_profiles.append(create_one_service_profile(attrs))
    return service_profiles


def get_service_profile(flavor_profile=None, count=2):
    """Get a list of flavor profiles."""
    if flavor_profile is None:
        flavor_profile = create_service_profile(count)

    return mock.Mock(side_effect=flavor_profile)


def create_one_local_ip(attrs=None):
    """Create a fake local ip.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with name, id, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    local_ip_attrs = {
        'created_at': '2021-11-29T10:10:23.000000',
        'name': 'local-ip-name-' + uuid.uuid4().hex,
        'description': 'local-ip-description-' + uuid.uuid4().hex,
        'id': 'local-ip-id-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'local_port_id': 'local_port_id-' + uuid.uuid4().hex,
        'network_id': 'network_id-' + uuid.uuid4().hex,
        'local_ip_address': '10.0.0.1',
        'ip_mode': 'translate',
        'revision_number': 'local-ip-revision-number-' + uuid.uuid4().hex,
        'updated_at': '2021-11-29T10:10:25.000000',
    }

    # Overwrite default attributes.
    local_ip_attrs.update(attrs)

    local_ip = _local_ip.LocalIP(**local_ip_attrs)

    return local_ip


def create_local_ips(attrs=None, count=2):
    """Create multiple fake local ips.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of local ips to fake
    :return:
        A list of FakeResource objects faking the local ips
    """
    local_ips = []
    for i in range(0, count):
        local_ips.append(create_one_local_ip(attrs))

    return local_ips


def get_local_ips(local_ips=None, count=2):
    """Get an iterable Mock object with a list of faked local ips.

    If local ip list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :param List local_ips:
        A list of FakeResource objects faking local ips
    :param int count:
        The number of local ips to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        local ips
    """
    if local_ips is None:
        local_ips = create_local_ips(count)
    return mock.Mock(side_effect=local_ips)


def create_one_local_ip_association(attrs=None):
    """Create a fake local ip association.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with local_ip_id, local_ip_address, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    local_ip_association_attrs = {
        'local_ip_id': 'local-ip-id-' + uuid.uuid4().hex,
        'local_ip_address': '172.24.4.228',
        'fixed_port_id': 'fixed-port-id-' + uuid.uuid4().hex,
        'fixed_ip': '10.0.0.5',
        'host': 'host-' + uuid.uuid4().hex,
    }

    # Overwrite default attributes.
    local_ip_association_attrs.update(attrs)

    local_ip_association = _local_ip_association.LocalIPAssociation(
        **local_ip_association_attrs
    )

    return local_ip_association


def create_local_ip_associations(attrs=None, count=2):
    """Create multiple fake local ip associations.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of local ip associations to fake
    :return:
        A list of FakeResource objects faking the local ip associations
    """
    local_ip_associations = []
    for i in range(0, count):
        local_ip_associations.append(create_one_local_ip_association(attrs))

    return local_ip_associations


def get_local_ip_associations(local_ip_associations=None, count=2):
    """Get a list of faked local ip associations

    If local ip association list is provided, then initialize
    the Mock object with the list. Otherwise create one.

    :param List local_ip_associations:
        A list of FakeResource objects faking local ip associations
    :param int count:
        The number of local ip associations to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        local ip associations
    """
    if local_ip_associations is None:
        local_ip_associations = create_local_ip_associations(count)

    return mock.Mock(side_effect=local_ip_associations)


def create_one_ndp_proxy(attrs=None):
    """Create a fake NDP proxy.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with router_id, port_id, etc.
    """
    attrs = attrs or {}
    router_id = attrs.get('router_id') or 'router-id-' + uuid.uuid4().hex
    port_id = attrs.get('port_id') or 'port-id-' + uuid.uuid4().hex
    # Set default attributes.
    np_attrs = {
        'id': uuid.uuid4().hex,
        'name': 'ndp-proxy-name-' + uuid.uuid4().hex,
        'router_id': router_id,
        'port_id': port_id,
        'ip_address': '2001::1:2',
        'description': 'ndp-proxy-description-' + uuid.uuid4().hex,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'location': 'MUNCHMUNCHMUNCH',
    }

    # Overwrite default attributes.
    np_attrs.update(attrs)

    return _ndp_proxy.NDPProxy(**np_attrs)


def create_ndp_proxies(attrs=None, count=2):
    """Create multiple fake NDP proxies.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of NDP proxxy to fake
    :return:
        A list of FakeResource objects faking the NDP proxies
    """
    ndp_proxies = []
    for i in range(0, count):
        ndp_proxies.append(create_one_ndp_proxy(attrs))
    return ndp_proxies


def get_ndp_proxies(ndp_proxies=None, count=2):
    """Get a list of faked NDP proxies.

    If ndp_proxy list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :param List ndp_proxies:
        A list of FakeResource objects faking ndp proxy
    :param int count:
        The number of ndp proxy to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        ndp proxy
    """
    if ndp_proxies is None:
        ndp_proxies = create_ndp_proxies(count)
    return mock.Mock(side_effect=ndp_proxies)


def create_one_trunk(attrs=None):
    """Create a fake trunk.

    :param Dictionary attrs:
        A dictionary with all attributes
    :return:
        A FakeResource object with name, id, etc.
    """
    attrs = attrs or {}

    # Set default attributes.
    trunk_attrs = {
        'id': 'trunk-id-' + uuid.uuid4().hex,
        'name': 'trunk-name-' + uuid.uuid4().hex,
        'description': '',
        'port_id': 'port-' + uuid.uuid4().hex,
        'admin_state_up': True,
        'project_id': 'project-id-' + uuid.uuid4().hex,
        'status': 'ACTIVE',
        'sub_ports': [
            {
                'port_id': 'subport-' + uuid.uuid4().hex,
                'segmentation_type': 'vlan',
                'segmentation_id': 100,
            }
        ],
    }
    # Overwrite default attributes.
    trunk_attrs.update(attrs)

    trunk = _trunk.Trunk(**trunk_attrs)

    return trunk


def create_trunks(attrs=None, count=2):
    """Create multiple fake trunks.

    :param Dictionary attrs:
        A dictionary with all attributes
    :param int count:
        The number of trunks to fake
    :return:
        A list of FakeResource objects faking the trunks
    """
    trunks = []
    for i in range(0, count):
        trunks.append(create_one_trunk(attrs))

    return trunks


def get_trunks(trunks=None, count=2):
    """Get an iterable Mock object with a list of faked trunks.

    If trunk list is provided, then initialize the Mock object
    with the list. Otherwise create one.

    :param List trunks:
        A list of FakeResource objects faking trunks
    :param int count:
        The number of trunks to fake
    :return:
        An iterable Mock object with side_effect set to a list of faked
        trunks
    """
    if trunks is None:
        trunks = create_trunks(count)
    return mock.Mock(side_effect=trunks)
