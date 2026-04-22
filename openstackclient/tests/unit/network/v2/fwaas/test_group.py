# Copyright 2016 FUJITSU LIMITED
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import copy
import re
from unittest import mock

from openstack.network.v2 import firewall_group
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.network.v2.fwaas import group as fwaas_group
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as test_utils


CONVERT_MAP = {
    'ingress_firewall_policy': 'ingress_firewall_policy_id',
    'egress_firewall_policy': 'egress_firewall_policy_id',
    'no_ingress_firewall_policy': 'ingress_firewall_policy_id',
    'no_egress_firewall_policy': 'egress_firewall_policy_id',
    'project': 'project_id',
    'port': 'ports',
}


def _generate_response(source=None, data=None):
    source = source if source else {}
    up = {
        'admin_state_up': fwaas_group.AdminStateColumn(
            source['admin_state_up']
        )
    }
    if data:
        up.append(data)
    source.update(up)
    return source


def _generate_req_and_res(verifylist, response):
    request = dict(verifylist)
    for key, val in verifylist:
        del request[key]
        if re.match('^no_', key) and val is True:
            new_value = None
        elif val is True or val is False:
            new_value = val
        elif key in ('name', 'description'):
            new_value = val
        else:
            new_value = val
        converted = CONVERT_MAP.get(key, key)
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestFirewallGroup(network_fakes.TestNetworkV2):
    def check_results(self, headers, data, exp_req, is_list=False):
        if is_list:
            req_body = {self.res_plural: list(exp_req)}
        else:
            req_body = exp_req
        self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))

    def setUp(self):
        super().setUp()

        self.resource = sdk_fakes.generate_fake_resource(
            firewall_group.FirewallGroup
        )

        def _find_resource(*args, **kwargs):
            return self.resource

        self.network_client.find_firewall_group.side_effect = _find_resource
        self.identity_client.projects.get.side_effect = lambda x: mock.Mock(
            id=x
        )
        self.res = 'firewall_group'
        self.res_plural = 'firewall_groups'
        self.list_headers = (
            'ID',
            'Name',
            'Ingress Policy ID',
            'Egress Policy ID',
        )
        self.list_data = (
            self.resource['id'],
            self.resource['name'],
            self.resource['ingress_firewall_policy_id'],
            self.resource['egress_firewall_policy_id'],
        )
        self.headers = tuple(
            (
                *self.list_headers,
                'Description',
                'Status',
                'Ports',
                'State',
                'Shared',
                'Project',
            )
        )
        self.data = _generate_response(self.resource)
        self.ordered_headers = copy.deepcopy(tuple(sorted(self.headers)))
        self.expected_data = (
            self.resource['description'],
            self.resource['egress_firewall_policy_id'],
            self.resource['id'],
            self.resource['ingress_firewall_policy_id'],
            self.resource['name'],
            self.resource['ports'],
            self.resource['project_id'],
            self.resource['shared'],
            fwaas_group.AdminStateColumn(self.resource['admin_state_up']),
            self.resource['status'],
        )
        self.ordered_columns = (
            'description',
            'egress_firewall_policy_id',
            'id',
            'ingress_firewall_policy_id',
            'name',
            'ports',
            'project_id',
            'shared',
            'admin_state_up',
            'status',
        )


class TestCreateFirewallGroup(TestFirewallGroup):
    def setUp(self):
        super().setUp()
        self.network_client.create_firewall_group.return_value = self.resource
        self.mocked = self.network_client.create_firewall_group
        self.cmd = fwaas_group.CreateFirewallGroup(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_firewall_group.return_value = response
        # Update response(finally returns 'data')
        self.data = _generate_response(source=response)
        self.expected_data = response

    def test_create_with_no_option(self):
        # firewall_group-create with mandatory (none) params.
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))

    def test_create_with_port(self):
        # firewall_group-create with 'port'
        port_id = 'id_for_port'

        def _mock_find(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_port.side_effect = _mock_find
        arglist = ['--port', port_id]
        verifylist = [('port', [port_id])]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_ingress_policy(self):
        ingress_policy = 'my-ingress-policy'

        def _mock_port_fwg(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_policy.side_effect = _mock_port_fwg

        arglist = ['--ingress-firewall-policy', ingress_policy]
        verifylist = [('ingress_firewall_policy', ingress_policy)]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.network_client.find_firewall_policy.assert_called_once_with(
            ingress_policy, ignore_missing=False
        )

        self.check_results(headers, data, request)

    def test_create_with_egress_policy(self):
        egress_policy = 'my-egress-policy'

        def _mock_find(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_group.side_effect = _mock_find
        self.network_client.find_firewall_policy.side_effect = _mock_find

        arglist = ['--egress-firewall-policy', egress_policy]
        verifylist = [('egress_firewall_policy', egress_policy)]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_firewall_policy.assert_called_once_with(
            egress_policy, ignore_missing=False
        )
        self.check_results(headers, data, request)

    def test_create_with_all_params(self):
        name = 'my-name'
        description = 'my-desc'
        ingress_policy = 'my-ingress-policy'
        egress_policy = 'my-egress-policy'

        def _mock_find(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_policy.side_effect = _mock_find
        port = 'port'
        self.network_client.find_port.side_effect = _mock_find
        project_id = 'my-project'
        arglist = [
            '--name',
            name,
            '--description',
            description,
            '--ingress-firewall-policy',
            ingress_policy,
            '--egress-firewall-policy',
            egress_policy,
            '--port',
            port,
            '--project',
            project_id,
            '--share',
            '--disable',
        ]
        verifylist = [
            ('name', name),
            ('description', description),
            ('ingress_firewall_policy', ingress_policy),
            ('egress_firewall_policy', egress_policy),
            ('port', [port]),
            ('shared', True),
            ('project', project_id),
            ('admin_state_up', False),
        ]
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_shared_and_no_share(self):
        arglist = [
            '--share',
            '--no-share',
        ]
        verifylist = [
            ('shared', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_ports_and_no(self):
        port = 'my-port'
        arglist = [
            '--port',
            port,
            '--no-port',
        ]
        verifylist = [
            ('port', [port]),
            ('no_port', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_ingress_policy_and_no(self):
        policy = 'my-policy'
        arglist = [
            '--ingress-firewall-policy',
            policy,
            '--no-ingress-firewall-policy',
        ]
        verifylist = [
            ('ingress_firewall_policy', policy),
            ('no_ingress_firewall_policy', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_egress_policy_and_no(self):
        policy = 'my-policy'
        arglist = [
            '--egress-firewall-policy',
            policy,
            '--no-egress-firewall-policy',
        ]
        verifylist = [
            ('egress_firewall_policy', policy),
            ('no_egress_firewall_policy', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestListFirewallGroup(TestFirewallGroup):
    def setUp(self):
        super().setUp()
        self.network_client.firewall_groups.return_value = [self.resource]
        self.mocked = self.network_client.firewall_groups
        self.cmd = fwaas_group.ListFirewallGroup(self.app, None)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.list_headers), headers)
        self.assertEqual([self.list_data], list(data))

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)


class TestShowFirewallGroup(TestFirewallGroup):
    def setUp(self):
        super().setUp()
        self.network_client.get_firewall_group.return_value = self.resource
        self.mocked = self.network_client.get_firewall_group
        self.cmd = fwaas_group.ShowFirewallGroup(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_group.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)


class TestSetFirewallGroup(TestFirewallGroup):
    def setUp(self):
        super().setUp()
        self.resource['ports'] = ['old_port']
        self.network_client.update_firewall_group.return_value = {
            self.res: self.resource
        }
        self.mocked = self.network_client.update_firewall_group

        def _mock_find_port(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_port.side_effect = _mock_find_port

        self.cmd = fwaas_group.SetFirewallGroup(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response(finally returns 'data')
        self.data = _generate_response(source=response)
        self.ordered_data = tuple(
            response[column] for column in self.ordered_columns
        )

    def test_set_name(self):
        target = self.resource['id']
        update = 'change'
        arglist = [target, '--name', update]
        verifylist = [
            (self.res, target),
            ('name', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'name': update})
        self.assertIsNone(result)

    def test_set_options(self):
        target = self.resource['id']
        updated_desc = 'change-desc'
        arglist = [target, '--description', updated_desc, '--share']
        verifylist = [
            (self.res, target),
            ('description', updated_desc),
            ('shared', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, shared=True, description=updated_desc
        )
        self.assertIsNone(result)

    def test_set_ingress_policy_and_egress_policy(self):
        target = self.resource['id']
        ingress_policy = 'ingress_policy'
        egress_policy = 'egress_policy'

        def _mock_fwg_policy(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_group.side_effect = _mock_fwg_policy
        self.network_client.find_firewall_policy.side_effect = _mock_fwg_policy

        arglist = [
            target,
            '--ingress-firewall-policy',
            ingress_policy,
            '--egress-firewall-policy',
            egress_policy,
        ]
        verifylist = [
            (self.res, target),
            ('ingress_firewall_policy', ingress_policy),
            ('egress_firewall_policy', egress_policy),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target,
            **{
                'ingress_firewall_policy_id': ingress_policy,
                'egress_firewall_policy_id': egress_policy,
            },
        )
        self.assertIsNone(result)

    def test_set_port(self):
        target = self.resource['id']
        port1 = 'additional_port1'
        port2 = 'additional_port2'

        def _mock_port_fwg(*args, **kwargs):
            return mock.Mock(id=args[0], ports=self.resource['ports'])

        self.network_client.find_firewall_group.side_effect = _mock_port_fwg
        self.network_client.find_port.side_effect = _mock_port_fwg

        arglist = [
            target,
            '--port',
            port1,
            '--port',
            port2,
        ]
        verifylist = [
            (self.res, target),
            ('port', [port1, port2]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        expect = {'ports': sorted(self.resource['ports'] + [port1, port2])}
        self.mocked.assert_called_once_with(target, **expect)
        self.assertEqual(2, self.network_client.find_firewall_group.call_count)
        self.assertIsNone(result)

    def test_set_no_port(self):
        # firewall_group-update myid --policy newpolicy.
        target = self.resource['id']
        arglist = [target, '--no-port']
        verifylist = [
            (self.res, target),
            ('no_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'ports': []})
        self.assertIsNone(result)

    def test_set_admin_state(self):
        target = self.resource['id']
        arglist = [target, '--enable']
        verifylist = [
            (self.res, target),
            ('admin_state_up', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'admin_state_up': True})
        self.assertIsNone(result)

    def test_set_shared(self):
        target = self.resource['id']
        arglist = [target, '--share']
        verifylist = [
            (self.res, target),
            ('shared', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': True})
        self.assertIsNone(result)

    def test_set_no_share(self):
        target = self.resource['id']
        arglist = [target, '--no-share']
        verifylist = [
            (self.res, target),
            ('shared', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_set_egress_policy(self):
        target = self.resource['id']
        policy = 'egress_policy'

        def _mock_find_policy(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_policy.side_effect = (
            _mock_find_policy
        )

        arglist = [target, '--egress-firewall-policy', policy]
        verifylist = [
            (self.res, target),
            ('egress_firewall_policy', policy),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'egress_firewall_policy_id': policy}
        )
        self.assertIsNone(result)

    def test_set_no_ingress_policies(self):
        target = self.resource['id']
        arglist = [target, '--no-ingress-firewall-policy']
        verifylist = [
            (self.res, target),
            ('no_ingress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'ingress_firewall_policy_id': None}
        )
        self.assertIsNone(result)

    def test_set_no_egress_policies(self):
        target = self.resource['id']
        arglist = [target, '--no-egress-firewall-policy']
        verifylist = [
            (self.res, target),
            ('no_egress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'egress_firewall_policy_id': None}
        )
        self.assertIsNone(result)

    def test_set_port_and_no_port(self):
        target = self.resource['id']
        port = 'my-port'
        arglist = [
            target,
            '--port',
            port,
            '--no-port',
        ]
        verifylist = [
            (self.res, target),
            ('port', [port]),
            ('no_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, **{'ports': [port]})
        self.assertIsNone(result)

    def test_set_ingress_policy_and_no_ingress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--ingress-firewall-policy',
            'my-ingress',
            '--no-ingress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('ingress_firewall_policy', 'my-ingress'),
            ('no_ingress_firewall_policy', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_egress_policy_and_no_egress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--egress-firewall-policy',
            'my-egress',
            '--no-egress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('egress_firewall_policy', 'my-egress'),
            ('no_egress_firewall_policy', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_and_raises(self):
        self.network_client.update_firewall_group.side_effect = Exception
        target = self.resource['id']
        arglist = [target, '--name', 'my-name']
        verifylist = [(self.res, target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestDeleteFirewallGroup(TestFirewallGroup):
    def setUp(self):
        super().setUp()
        # Mock objects
        self.mocked = self.network_client.delete_firewall_group
        self.cmd = fwaas_group.DeleteFirewallGroup(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_group.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_fwaas(*args, **kwargs):
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_group.side_effect = _mock_fwaas

        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0][0])
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        def _mock_find(*args, **kwargs):
            if args[0] == target2:
                raise Exception('Not found')
            return mock.Mock(id=args[0])

        self.network_client.find_firewall_group.side_effect = _mock_find

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestUnsetFirewallGroup(TestFirewallGroup):
    def setUp(self):
        super().setUp()
        self.resource['ports'] = ['old_port']
        # Mock objects
        self.mocked = self.network_client.update_firewall_group
        self.cmd = fwaas_group.UnsetFirewallGroup(self.app, None)

    def test_unset_shared(self):
        target = self.resource['id']
        arglist = [
            target,
            '--share',
        ]
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_unset_ingress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--ingress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('ingress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, **{'ingress_firewall_policy_id': None}
        )
        self.assertIsNone(result)

    def test_unset_egress_policy(self):
        target = self.resource['id']
        arglist = [
            target,
            '--egress-firewall-policy',
        ]
        verifylist = [
            (self.res, target),
            ('egress_firewall_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, **{'egress_firewall_policy_id': None}
        )
        self.assertIsNone(result)

    def test_unset_enable(self):
        target = self.resource['id']
        arglist = [
            target,
            '--enable',
        ]
        verifylist = [
            (self.res, target),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(
            target, **{'admin_state_up': False}
        )
        self.assertIsNone(result)

    def test_unset_port(self):
        target = self.resource['id']
        port = 'old_port'

        def _mock_port_fwg(*args, **kwargs):
            return mock.Mock(id=args[0], ports=self.resource['ports'])

        self.network_client.find_firewall_group.side_effect = _mock_port_fwg
        self.network_client.find_port.side_effect = _mock_port_fwg

        arglist = [
            target,
            '--port',
            port,
        ]
        verifylist = [
            (self.res, target),
            ('port', [port]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, **{'ports': []})
        self.assertIsNone(result)

    def test_unset_all_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--all-port',
        ]
        verifylist = [
            (self.res, target),
            ('all_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, **{'ports': []})
        self.assertIsNone(result)
