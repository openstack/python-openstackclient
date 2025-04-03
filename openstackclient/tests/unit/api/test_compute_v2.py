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

import http
from unittest import mock
import uuid

from openstack.compute.v2 import _proxy
from osc_lib import exceptions as osc_lib_exceptions

from openstackclient.api import compute_v2 as compute
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils


class TestSecurityGroup(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.compute_client = mock.Mock(_proxy.Proxy)

    def test_create_security_group(self):
        sg_name = 'name-' + uuid.uuid4().hex
        sg_description = 'description-' + uuid.uuid4().hex
        data = {
            'security_group': {
                'id': uuid.uuid4().hex,
                'name': sg_name,
                'description': sg_description,
                'tenant_id': 'project-id-' + uuid.uuid4().hex,
                'rules': [],
            }
        }
        self.compute_client.post.return_value = fakes.FakeResponse(data=data)

        result = compute.create_security_group(
            self.compute_client, sg_name, sg_description
        )

        self.compute_client.post.assert_called_once_with(
            '/os-security-groups',
            data={'name': sg_name, 'description': sg_description},
            microversion='2.1',
        )
        self.assertEqual(data['security_group'], result)

    def test_list_security_groups(self):
        data = {
            'security_groups': [
                {
                    'id': uuid.uuid4().hex,
                    'name': uuid.uuid4().hex,
                    'description': 'description-' + uuid.uuid4().hex,
                    'tenant_id': 'project-id-' + uuid.uuid4().hex,
                    'rules': [],
                }
            ],
        }
        self.compute_client.get.return_value = fakes.FakeResponse(data=data)

        result = compute.list_security_groups(self.compute_client)

        self.compute_client.get.assert_called_once_with(
            '/os-security-groups', microversion='2.1'
        )
        self.assertEqual(data['security_groups'], result)

    def test_find_security_group_by_id(self):
        sg_id = uuid.uuid4().hex
        sg_name = 'name-' + uuid.uuid4().hex
        data = {
            'security_group': {
                'id': sg_id,
                'name': sg_name,
                'description': 'description-' + uuid.uuid4().hex,
                'tenant_id': 'project-id-' + uuid.uuid4().hex,
                'rules': [],
            }
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(data=data),
        ]

        result = compute.find_security_group(self.compute_client, sg_id)

        self.compute_client.get.assert_has_calls(
            [
                mock.call(f'/os-security-groups/{sg_id}', microversion='2.1'),
            ]
        )
        self.assertEqual(data['security_group'], result)

    def test_find_security_group_by_name(self):
        sg_id = uuid.uuid4().hex
        sg_name = 'name-' + uuid.uuid4().hex
        data = {
            'security_groups': [
                {
                    'id': sg_id,
                    'name': sg_name,
                    'description': 'description-' + uuid.uuid4().hex,
                    'tenant_id': 'project-id-' + uuid.uuid4().hex,
                    'rules': [],
                }
            ],
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]

        result = compute.find_security_group(self.compute_client, sg_name)

        self.compute_client.get.assert_has_calls(
            [
                mock.call(
                    f'/os-security-groups/{sg_name}', microversion='2.1'
                ),
                mock.call('/os-security-groups', microversion='2.1'),
            ]
        )
        self.assertEqual(data['security_groups'][0], result)

    def test_find_security_group_not_found(self):
        data = {'security_groups': []}
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            compute.find_security_group,
            self.compute_client,
            'invalid-sg',
        )

    def test_find_security_group_by_name_duplicate(self):
        sg_name = 'name-' + uuid.uuid4().hex
        data = {
            'security_groups': [
                {
                    'id': uuid.uuid4().hex,
                    'name': sg_name,
                    'description': 'description-' + uuid.uuid4().hex,
                    'tenant_id': 'project-id-' + uuid.uuid4().hex,
                    'rules': [],
                },
                {
                    'id': uuid.uuid4().hex,
                    'name': sg_name,
                    'description': 'description-' + uuid.uuid4().hex,
                    'tenant_id': 'project-id-' + uuid.uuid4().hex,
                    'rules': [],
                },
            ],
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]

        self.assertRaises(
            osc_lib_exceptions.NotFound,
            compute.find_security_group,
            self.compute_client,
            sg_name,
        )

    def test_update_security_group(self):
        sg_id = uuid.uuid4().hex
        sg_name = 'name-' + uuid.uuid4().hex
        sg_description = 'description-' + uuid.uuid4().hex
        data = {
            'security_group': {
                'id': sg_id,
                'name': sg_name,
                'description': sg_description,
                'tenant_id': 'project-id-' + uuid.uuid4().hex,
                'rules': [],
            }
        }
        self.compute_client.put.return_value = fakes.FakeResponse(data=data)

        result = compute.update_security_group(
            self.compute_client, sg_id, sg_name, sg_description
        )

        self.compute_client.put.assert_called_once_with(
            f'/os-security-groups/{sg_id}',
            data={'name': sg_name, 'description': sg_description},
            microversion='2.1',
        )
        self.assertEqual(data['security_group'], result)

    def test_delete_security_group(self):
        sg_id = uuid.uuid4().hex
        self.compute_client.delete.return_value = fakes.FakeResponse(
            status_code=http.HTTPStatus.NO_CONTENT
        )

        result = compute.delete_security_group(self.compute_client, sg_id)

        self.compute_client.delete.assert_called_once_with(
            f'/os-security-groups/{sg_id}',
            microversion='2.1',
        )
        self.assertIsNone(result)


class TestSecurityGroupRule(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.compute_client = mock.Mock(_proxy.Proxy)

    def test_create_security_group_rule(self):
        sg_id = uuid.uuid4().hex
        data = {
            'security_group_rule': {
                'parent_group_id': sg_id,
                'ip_protocol': 'tcp',
                'from_port': 22,
                'to_port': 22,
                'cidr': '10.0.0.0/24',
            }
        }
        self.compute_client.post.return_value = fakes.FakeResponse(data=data)

        result = compute.create_security_group_rule(
            self.compute_client,
            security_group_id=sg_id,
            ip_protocol='tcp',
            from_port=22,
            to_port=22,
            remote_ip='10.0.0.0/24',
            remote_group=None,
        )

        self.compute_client.post.assert_called_once_with(
            '/os-security-group-rules',
            data={
                'parent_group_id': sg_id,
                'ip_protocol': 'tcp',
                'from_port': 22,
                'to_port': 22,
                'cidr': '10.0.0.0/24',
                'group_id': None,
            },
            microversion='2.1',
        )
        self.assertEqual(data['security_group_rule'], result)

    def test_delete_security_group_rule(self):
        sg_id = uuid.uuid4().hex
        self.compute_client.delete.return_value = fakes.FakeResponse(
            status_code=http.HTTPStatus.NO_CONTENT
        )

        result = compute.delete_security_group_rule(self.compute_client, sg_id)

        self.compute_client.delete.assert_called_once_with(
            f'/os-security-group-rules/{sg_id}',
            microversion='2.1',
        )
        self.assertIsNone(result)


class TestNetwork(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.compute_client = mock.Mock(_proxy.Proxy)

    def test_create_network(self):
        net_name = 'name-' + uuid.uuid4().hex
        net_subnet = '10.0.0.0/24'
        data = {
            'network': {
                'id': uuid.uuid4().hex,
                'label': net_name,
                'cidr': net_subnet,
                'share_address': True,
                # other fields omitted for brevity
            }
        }
        self.compute_client.post.return_value = fakes.FakeResponse(data=data)

        result = compute.create_network(
            self.compute_client,
            name=net_name,
            subnet=net_subnet,
            share_subnet=True,
        )

        self.compute_client.post.assert_called_once_with(
            '/os-networks',
            data={
                'label': net_name,
                'cidr': net_subnet,
                'share_address': True,
            },
            microversion='2.1',
        )
        self.assertEqual(data['network'], result)

    def test_list_networks(self):
        data = {
            'networks': [
                {
                    'id': uuid.uuid4().hex,
                    'label': f'name-{uuid.uuid4().hex}',
                    # other fields omitted for brevity
                }
            ],
        }
        self.compute_client.get.return_value = fakes.FakeResponse(data=data)

        result = compute.list_networks(self.compute_client)

        self.compute_client.get.assert_called_once_with(
            '/os-networks', microversion='2.1'
        )
        self.assertEqual(data['networks'], result)

    def test_find_network_by_id(self):
        net_id = uuid.uuid4().hex
        net_name = 'name-' + uuid.uuid4().hex
        data = {
            'network': {
                'id': net_id,
                'label': net_name,
                # other fields omitted for brevity
            }
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(data=data),
        ]

        result = compute.find_network(self.compute_client, net_id)

        self.compute_client.get.assert_has_calls(
            [
                mock.call(f'/os-networks/{net_id}', microversion='2.1'),
            ]
        )
        self.assertEqual(data['network'], result)

    def test_find_network_by_name(self):
        net_id = uuid.uuid4().hex
        net_name = 'name-' + uuid.uuid4().hex
        data = {
            'networks': [
                {
                    'id': net_id,
                    'label': net_name,
                    # other fields omitted for brevity
                }
            ],
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]

        result = compute.find_network(self.compute_client, net_name)

        self.compute_client.get.assert_has_calls(
            [
                mock.call(f'/os-networks/{net_name}', microversion='2.1'),
                mock.call('/os-networks', microversion='2.1'),
            ]
        )
        self.assertEqual(data['networks'][0], result)

    def test_find_network_not_found(self):
        data = {'networks': []}
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]
        self.assertRaises(
            osc_lib_exceptions.NotFound,
            compute.find_network,
            self.compute_client,
            'invalid-net',
        )

    def test_find_network_by_name_duplicate(self):
        net_name = 'name-' + uuid.uuid4().hex
        data = {
            'networks': [
                {
                    'id': uuid.uuid4().hex,
                    'label': net_name,
                    # other fields omitted for brevity
                },
                {
                    'id': uuid.uuid4().hex,
                    'label': net_name,
                    # other fields omitted for brevity
                },
            ],
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(status_code=http.HTTPStatus.NOT_FOUND),
            fakes.FakeResponse(data=data),
        ]

        self.assertRaises(
            osc_lib_exceptions.NotFound,
            compute.find_network,
            self.compute_client,
            net_name,
        )

    def test_delete_network(self):
        net_id = uuid.uuid4().hex
        self.compute_client.delete.return_value = fakes.FakeResponse(
            status_code=http.HTTPStatus.NO_CONTENT
        )

        result = compute.delete_network(self.compute_client, net_id)

        self.compute_client.delete.assert_called_once_with(
            f'/os-networks/{net_id}', microversion='2.1'
        )
        self.assertIsNone(result)


class TestFloatingIP(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.compute_client = mock.Mock(_proxy.Proxy)

    def test_create_floating_ip(self):
        network = 'network-' + uuid.uuid4().hex
        data = {
            'floating_ip': {
                'fixed_ip': None,
                'id': uuid.uuid4().hex,
                'instance_id': None,
                'ip': '172.24.4.17',
                'pool': network,
            }
        }
        self.compute_client.post.return_value = fakes.FakeResponse(data=data)

        result = compute.create_floating_ip(
            self.compute_client, network=network
        )

        self.compute_client.post.assert_called_once_with(
            '/os-floating-ips', data={'pool': network}, microversion='2.1'
        )
        self.assertEqual(data['floating_ip'], result)

    def test_list_floating_ips(self):
        data = {
            'floating_ips': [
                {
                    'fixed_ip': None,
                    'id': uuid.uuid4().hex,
                    'instance_id': None,
                    'ip': '172.24.4.17',
                    'pool': f'network-{uuid.uuid4().hex}',
                }
            ],
        }
        self.compute_client.get.return_value = fakes.FakeResponse(data=data)

        result = compute.list_floating_ips(self.compute_client)

        self.compute_client.get.assert_called_once_with(
            '/os-floating-ips', microversion='2.1'
        )
        self.assertEqual(data['floating_ips'], result)

    def test_get_floating_ip(self):
        fip_id = uuid.uuid4().hex
        data = {
            'floating_ip': {
                'fixed_ip': None,
                'id': fip_id,
                'instance_id': None,
                'ip': '172.24.4.17',
                'pool': f'network-{uuid.uuid4().hex}',
            }
        }
        self.compute_client.get.side_effect = [
            fakes.FakeResponse(data=data),
        ]

        result = compute.get_floating_ip(self.compute_client, fip_id)

        self.compute_client.get.assert_called_once_with(
            f'/os-floating-ips/{fip_id}', microversion='2.1'
        )
        self.assertEqual(data['floating_ip'], result)

    def test_delete_floating_ip(self):
        fip_id = uuid.uuid4().hex
        self.compute_client.delete.return_value = fakes.FakeResponse(
            status_code=http.HTTPStatus.NO_CONTENT
        )

        result = compute.delete_floating_ip(self.compute_client, fip_id)

        self.compute_client.delete.assert_called_once_with(
            f'/os-floating-ips/{fip_id}', microversion='2.1'
        )
        self.assertIsNone(result)


class TestFloatingIPPool(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.compute_client = mock.Mock(_proxy.Proxy)

    def test_list_floating_ip_pools(self):
        data = {
            'floating_ip_pools': [
                {
                    'name': f'pool-{uuid.uuid4().hex}',
                }
            ],
        }
        self.compute_client.get.return_value = fakes.FakeResponse(data=data)

        result = compute.list_floating_ip_pools(self.compute_client)

        self.compute_client.get.assert_called_once_with(
            '/os-floating-ip-pools', microversion='2.1'
        )
        self.assertEqual(data['floating_ip_pools'], result)
