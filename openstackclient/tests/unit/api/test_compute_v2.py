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

from requests_mock.contrib import fixture

from keystoneclient import session
from openstackclient.api import compute_v2 as compute
from openstackclient.tests.unit import utils
from osc_lib import exceptions as osc_lib_exceptions


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
