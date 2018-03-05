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

"""Compute v2 API Library Tests"""

from keystoneauth1 import session
from osc_lib import exceptions as osc_lib_exceptions
from requests_mock.contrib import fixture

from openstackclient.api import compute_v2 as compute
from openstackclient.tests.unit import utils


FAKE_PROJECT = 'xyzpdq'
FAKE_URL = 'http://gopher.com/v2'


class TestComputeAPIv2(utils.TestCase):

    def setUp(self):
        super(TestComputeAPIv2, self).setUp()
        sess = session.Session()
        self.api = compute.APIv2(session=sess, endpoint=FAKE_URL)
        self.requests_mock = self.useFixture(fixture.Fixture())


class TestFloatingIP(TestComputeAPIv2):

    FAKE_FLOATING_IP_RESP = {
        'id': 1,
        'ip': '203.0.113.11',                   # TEST-NET-3
        'fixed_ip': '198.51.100.11',            # TEST-NET-2
        'pool': 'nova',
        'instance_id': None,
    }
    FAKE_FLOATING_IP_RESP_2 = {
        'id': 2,
        'ip': '203.0.113.12',                   # TEST-NET-3
        'fixed_ip': '198.51.100.12',            # TEST-NET-2
        'pool': 'nova',
        'instance_id': None,
    }
    LIST_FLOATING_IP_RESP = [
        FAKE_FLOATING_IP_RESP,
        FAKE_FLOATING_IP_RESP_2,
    ]

    FAKE_SERVER_RESP_1 = {
        'id': 1,
        'name': 'server1',
    }

    def test_floating_ip_add_id(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/servers/1/action',
            json={'server': {}},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/servers/1',
            json={'server': self.FAKE_SERVER_RESP_1},
            status_code=200,
        )
        ret = self.api.floating_ip_add('1', '1.0.1.0')
        self.assertEqual(200, ret.status_code)

    def test_floating_ip_add_name(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/servers/1/action',
            json={'server': {}},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/servers/server1',
            json={'server': self.FAKE_SERVER_RESP_1},
            status_code=200,
        )
        ret = self.api.floating_ip_add('server1', '1.0.1.0')
        self.assertEqual(200, ret.status_code)

    def test_floating_ip_create(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-floating-ips',
            json={'floating_ip': self.FAKE_FLOATING_IP_RESP},
            status_code=200,
        )
        ret = self.api.floating_ip_create('nova')
        self.assertEqual(self.FAKE_FLOATING_IP_RESP, ret)

    def test_floating_ip_create_not_found(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-floating-ips',
            status_code=404,
        )
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            self.api.floating_ip_create,
            'not-nova',
        )

    def test_floating_ip_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/os-floating-ips/1',
            status_code=202,
        )
        ret = self.api.floating_ip_delete('1')
        self.assertEqual(202, ret.status_code)
        self.assertEqual("", ret.text)

    def test_floating_ip_delete_none(self):
        ret = self.api.floating_ip_delete()
        self.assertIsNone(ret)

    def test_floating_ip_find_id(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ips/1',
            json={'floating_ip': self.FAKE_FLOATING_IP_RESP},
            status_code=200,
        )
        ret = self.api.floating_ip_find('1')
        self.assertEqual(self.FAKE_FLOATING_IP_RESP, ret)

    def test_floating_ip_find_ip(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ips/' + self.FAKE_FLOATING_IP_RESP['ip'],
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ips',
            json={'floating_ips': self.LIST_FLOATING_IP_RESP},
            status_code=200,
        )
        ret = self.api.floating_ip_find(self.FAKE_FLOATING_IP_RESP['ip'])
        self.assertEqual(self.FAKE_FLOATING_IP_RESP, ret)

    def test_floating_ip_find_not_found(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ips/1.2.3.4',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ips',
            json={'floating_ips': self.LIST_FLOATING_IP_RESP},
            status_code=200,
        )
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            self.api.floating_ip_find,
            '1.2.3.4',
        )

    def test_floating_ip_list(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ips',
            json={'floating_ips': self.LIST_FLOATING_IP_RESP},
            status_code=200,
        )
        ret = self.api.floating_ip_list()
        self.assertEqual(self.LIST_FLOATING_IP_RESP, ret)

    def test_floating_ip_remove_id(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/servers/1/action',
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/servers/1',
            json={'server': self.FAKE_SERVER_RESP_1},
            status_code=200,
        )
        ret = self.api.floating_ip_remove('1', '1.0.1.0')
        self.assertEqual(200, ret.status_code)

    def test_floating_ip_remove_name(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/servers/1/action',
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/servers/server1',
            json={'server': self.FAKE_SERVER_RESP_1},
            status_code=200,
        )
        ret = self.api.floating_ip_remove('server1', '1.0.1.0')
        self.assertEqual(200, ret.status_code)


class TestFloatingIPPool(TestComputeAPIv2):

    LIST_FLOATING_IP_POOL_RESP = [
        {"name": "tide"},
        {"name": "press"},
    ]

    def test_floating_ip_pool_list(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-floating-ip-pools',
            json={'floating_ip_pools': self.LIST_FLOATING_IP_POOL_RESP},
            status_code=200,
        )
        ret = self.api.floating_ip_pool_list()
        self.assertEqual(self.LIST_FLOATING_IP_POOL_RESP, ret)


class TestHost(TestComputeAPIv2):

    FAKE_HOST_RESP_1 = {
        "zone": "internal",
        "host_name": "myhost",
        "service": "conductor",
    }

    FAKE_HOST_RESP_2 = {
        "zone": "internal",
        "host_name": "myhost",
        "service": "scheduler",
    }

    FAKE_HOST_RESP_3 = {
        "zone": "nova",
        "host_name": "myhost",
        "service": "compute",
    }

    LIST_HOST_RESP = [
        FAKE_HOST_RESP_1,
        FAKE_HOST_RESP_2,
        FAKE_HOST_RESP_3,
    ]

    def test_host_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-hosts',
            json={'hosts': self.LIST_HOST_RESP},
            status_code=200,
        )
        ret = self.api.host_list()
        self.assertEqual(self.LIST_HOST_RESP, ret)

    def test_host_list_zone(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-hosts?zone=nova',
            json={'hosts': [self.FAKE_HOST_RESP_3]},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-hosts',
            json={'hosts': [self.FAKE_HOST_RESP_3]},
            status_code=200,
        )
        ret = self.api.host_list(zone='nova')
        self.assertEqual([self.FAKE_HOST_RESP_3], ret)

    def test_host_set_none(self):
        ret = self.api.host_set(host='myhost')
        self.assertIsNone(ret)

    def test_host_set(self):
        self.requests_mock.register_uri(
            'PUT',
            FAKE_URL + '/os-hosts/myhost',
            json={},
            status_code=200,
        )
        ret = self.api.host_set(host='myhost', status='enabled')
        self.assertEqual({}, ret)

    def test_host_show(self):
        FAKE_RESOURCE_1 = {
            "cpu": 2,
            "disk_gb": 1028,
            "host": "c1a7de0ac9d94e4baceae031d05caae3",
            "memory_mb": 8192,
            "project": "(total)",
        }
        FAKE_RESOURCE_2 = {
            "cpu": 0,
            "disk_gb": 0,
            "host": "c1a7de0ac9d94e4baceae031d05caae3",
            "memory_mb": 512,
            "project": "(used_now)",
        }
        FAKE_RESOURCE_3 = {
            "cpu": 0,
            "disk_gb": 0,
            "host": "c1a7de0ac9d94e4baceae031d05caae3",
            "memory_mb": 0,
            "project": "(used_max)",
        }
        FAKE_HOST_RESP = [
            {'resource': FAKE_RESOURCE_1},
            {'resource': FAKE_RESOURCE_2},
            {'resource': FAKE_RESOURCE_3},
        ]
        FAKE_HOST_LIST = [
            FAKE_RESOURCE_1,
            FAKE_RESOURCE_2,
            FAKE_RESOURCE_3,
        ]

        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-hosts/myhost',
            json={'host': FAKE_HOST_RESP},
            status_code=200,
        )
        ret = self.api.host_show(host='myhost')
        self.assertEqual(FAKE_HOST_LIST, ret)


class TestNetwork(TestComputeAPIv2):

    FAKE_NETWORK_RESP = {
        'id': '1',
        'label': 'label1',
        'cidr': '1.2.3.0/24',
    }

    FAKE_NETWORK_RESP_2 = {
        'id': '2',
        'label': 'label2',
        'cidr': '4.5.6.0/24',
    }

    LIST_NETWORK_RESP = [
        FAKE_NETWORK_RESP,
        FAKE_NETWORK_RESP_2,
    ]

    def test_network_create_default(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-networks',
            json={'network': self.FAKE_NETWORK_RESP},
            status_code=200,
        )
        ret = self.api.network_create('label1')
        self.assertEqual(self.FAKE_NETWORK_RESP, ret)

    def test_network_create_options(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-networks',
            json={'network': self.FAKE_NETWORK_RESP},
            status_code=200,
        )
        ret = self.api.network_create(
            name='label1',
            subnet='1.2.3.0/24',
        )
        self.assertEqual(self.FAKE_NETWORK_RESP, ret)

    def test_network_delete_id(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks/1',
            json={'network': self.FAKE_NETWORK_RESP},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/os-networks/1',
            status_code=202,
        )
        ret = self.api.network_delete('1')
        self.assertEqual(202, ret.status_code)
        self.assertEqual("", ret.text)

    def test_network_delete_name(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks/label1',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks',
            json={'networks': self.LIST_NETWORK_RESP},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/os-networks/1',
            status_code=202,
        )
        ret = self.api.network_delete('label1')
        self.assertEqual(202, ret.status_code)
        self.assertEqual("", ret.text)

    def test_network_delete_not_found(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks/label3',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks',
            json={'networks': self.LIST_NETWORK_RESP},
            status_code=200,
        )
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            self.api.network_delete,
            'label3',
        )

    def test_network_find_id(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks/1',
            json={'network': self.FAKE_NETWORK_RESP},
            status_code=200,
        )
        ret = self.api.network_find('1')
        self.assertEqual(self.FAKE_NETWORK_RESP, ret)

    def test_network_find_name(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks/label2',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks',
            json={'networks': self.LIST_NETWORK_RESP},
            status_code=200,
        )
        ret = self.api.network_find('label2')
        self.assertEqual(self.FAKE_NETWORK_RESP_2, ret)

    def test_network_find_not_found(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks/label3',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks',
            json={'networks': self.LIST_NETWORK_RESP},
            status_code=200,
        )
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            self.api.network_find,
            'label3',
        )

    def test_network_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-networks',
            json={'networks': self.LIST_NETWORK_RESP},
            status_code=200,
        )
        ret = self.api.network_list()
        self.assertEqual(self.LIST_NETWORK_RESP, ret)


class TestSecurityGroup(TestComputeAPIv2):

    FAKE_SECURITY_GROUP_RESP = {
        'id': '1',
        'name': 'sg1',
        'description': 'test security group',
        'tenant_id': '0123456789',
        'rules': []
    }
    FAKE_SECURITY_GROUP_RESP_2 = {
        'id': '2',
        'name': 'sg2',
        'description': 'another test security group',
        'tenant_id': '0123456789',
        'rules': []
    }
    LIST_SECURITY_GROUP_RESP = [
        FAKE_SECURITY_GROUP_RESP_2,
        FAKE_SECURITY_GROUP_RESP,
    ]

    def test_security_group_create_default(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-security-groups',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP},
            status_code=200,
        )
        ret = self.api.security_group_create('sg1')
        self.assertEqual(self.FAKE_SECURITY_GROUP_RESP, ret)

    def test_security_group_create_options(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-security-groups',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP},
            status_code=200,
        )
        ret = self.api.security_group_create(
            name='sg1',
            description='desc',
        )
        self.assertEqual(self.FAKE_SECURITY_GROUP_RESP, ret)

    def test_security_group_delete_id(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/1',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/os-security-groups/1',
            status_code=202,
        )
        ret = self.api.security_group_delete('1')
        self.assertEqual(202, ret.status_code)
        self.assertEqual("", ret.text)

    def test_security_group_delete_name(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/sg1',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups',
            json={'security_groups': self.LIST_SECURITY_GROUP_RESP},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/os-security-groups/1',
            status_code=202,
        )
        ret = self.api.security_group_delete('sg1')
        self.assertEqual(202, ret.status_code)
        self.assertEqual("", ret.text)

    def test_security_group_delete_not_found(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/sg3',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups',
            json={'security_groups': self.LIST_SECURITY_GROUP_RESP},
            status_code=200,
        )
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            self.api.security_group_delete,
            'sg3',
        )

    def test_security_group_find_id(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/1',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP},
            status_code=200,
        )
        ret = self.api.security_group_find('1')
        self.assertEqual(self.FAKE_SECURITY_GROUP_RESP, ret)

    def test_security_group_find_name(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/sg2',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups',
            json={'security_groups': self.LIST_SECURITY_GROUP_RESP},
            status_code=200,
        )
        ret = self.api.security_group_find('sg2')
        self.assertEqual(self.FAKE_SECURITY_GROUP_RESP_2, ret)

    def test_security_group_find_not_found(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/sg3',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups',
            json={'security_groups': self.LIST_SECURITY_GROUP_RESP},
            status_code=200,
        )
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            self.api.security_group_find,
            'sg3',
        )

    def test_security_group_list_no_options(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups',
            json={'security_groups': self.LIST_SECURITY_GROUP_RESP},
            status_code=200,
        )
        ret = self.api.security_group_list()
        self.assertEqual(self.LIST_SECURITY_GROUP_RESP, ret)

    def test_security_group_set_options_id(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/1',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'PUT',
            FAKE_URL + '/os-security-groups/1',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP},
            status_code=200,
        )
        ret = self.api.security_group_set(
            security_group='1',
            description='desc2')
        self.assertEqual(self.FAKE_SECURITY_GROUP_RESP, ret)

    def test_security_group_set_options_name(self):
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups/sg2',
            status_code=404,
        )
        self.requests_mock.register_uri(
            'GET',
            FAKE_URL + '/os-security-groups',
            json={'security_groups': self.LIST_SECURITY_GROUP_RESP},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'PUT',
            FAKE_URL + '/os-security-groups/2',
            json={'security_group': self.FAKE_SECURITY_GROUP_RESP_2},
            status_code=200,
        )
        ret = self.api.security_group_set(
            security_group='sg2',
            description='desc2')
        self.assertEqual(self.FAKE_SECURITY_GROUP_RESP_2, ret)


class TestSecurityGroupRule(TestComputeAPIv2):

    FAKE_SECURITY_GROUP_RULE_RESP = {
        'id': '1',
        'name': 'sgr1',
        'tenant_id': 'proj-1',
        'ip_protocol': 'TCP',
        'from_port': 1,
        'to_port': 22,
        'group': {},
        # 'ip_range': ,
        # 'cidr': ,
        # 'parent_group_id': ,
    }

    def test_security_group_create_no_options(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-security-group-rules',
            json={'security_group_rule': self.FAKE_SECURITY_GROUP_RULE_RESP},
            status_code=200,
        )
        ret = self.api.security_group_rule_create(
            security_group_id='1',
            ip_protocol='tcp',
        )
        self.assertEqual(self.FAKE_SECURITY_GROUP_RULE_RESP, ret)

    def test_security_group_create_options(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-security-group-rules',
            json={'security_group_rule': self.FAKE_SECURITY_GROUP_RULE_RESP},
            status_code=200,
        )
        ret = self.api.security_group_rule_create(
            security_group_id='1',
            ip_protocol='tcp',
            from_port=22,
            to_port=22,
            remote_ip='1.2.3.4/24',
        )
        self.assertEqual(self.FAKE_SECURITY_GROUP_RULE_RESP, ret)

    def test_security_group_create_port_errors(self):
        self.requests_mock.register_uri(
            'POST',
            FAKE_URL + '/os-security-group-rules',
            json={'security_group_rule': self.FAKE_SECURITY_GROUP_RULE_RESP},
            status_code=200,
        )
        self.assertRaises(
            compute.InvalidValue,
            self.api.security_group_rule_create,
            security_group_id='1',
            ip_protocol='tcp',
            from_port='',
            to_port=22,
            remote_ip='1.2.3.4/24',
        )
        self.assertRaises(
            compute.InvalidValue,
            self.api.security_group_rule_create,
            security_group_id='1',
            ip_protocol='tcp',
            from_port=0,
            to_port=[],
            remote_ip='1.2.3.4/24',
        )

    def test_security_group_rule_delete(self):
        self.requests_mock.register_uri(
            'DELETE',
            FAKE_URL + '/os-security-group-rules/1',
            status_code=202,
        )
        ret = self.api.security_group_rule_delete('1')
        self.assertEqual(202, ret.status_code)
        self.assertEqual("", ret.text)
