#   Copyright 2017 FUJITSU LIMITED
#   All Rights Reserved
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

from unittest import mock

from openstack.identity.v3 import project as _project
from openstack.network.v2 import vpn_endpoint_group as _vpn_endpoint_group
from openstack.test import fakes as sdk_fakes
from openstackclient.tests.unit import utils as tests_utils
from osc_lib import exceptions

from openstackclient.network.v2.vpnaas import endpoint_group
from openstackclient.tests.unit.network.v2 import fakes as test_fakes
from openstackclient.tests.unit.network.v2.vpnaas import fakes


class TestEndpointGroup(test_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self._endpoint_group = fakes.EndpointGroup().create()

        def _mock_endpoint_group(*args, **kwargs):
            self.network_client.find_vpn_endpoint_group.assert_called_once_with(
                self._endpoint_group['id'], ignore_missing=False
            )
            return {'id': args[0]}

        self.network_client.find_vpn_endpoint_group.side_effect = mock.Mock(
            side_effect=_mock_endpoint_group
        )
        self.headers = (
            'ID',
            'Name',
            'Type',
            'Endpoints',
            'Description',
            'Project',
        )
        self.ordered_headers = (
            'Description',
            'Endpoints',
            'ID',
            'Name',
            'Project',
            'Type',
        )
        self.ordered_data = (
            self._endpoint_group['description'],
            self._endpoint_group['endpoints'],
            self._endpoint_group['id'],
            self._endpoint_group['name'],
            self._endpoint_group['project_id'],
            self._endpoint_group['type'],
        )
        self.ordered_columns = (
            'description',
            'endpoints',
            'id',
            'name',
            'project_id',
            'type',
        )


class TestCreateEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.network_client.create_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )

        self.cmd = endpoint_group.CreateEndpointGroup(self.app, None)

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_all_params_cidr(self):
        self.network_client.create_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )

        arglist = [
            '--description',
            'my-desc',
            '--type',
            'cidr',
            '--value',
            '10.0.0.0/24',
            '--value',
            '20.0.0.0/24',
            '--project',
            self.project.id,
            self._endpoint_group.name,
        ]
        verifylist = [
            ('description', 'my-desc'),
            ('type', 'cidr'),
            ('endpoints', ['10.0.0.0/24', '20.0.0.0/24']),
            ('project', self.project.id),
            ('name', self._endpoint_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.ordered_data = tuple(
            self._endpoint_group[column] for column in self.ordered_columns
        )
        self.network_client.create_vpn_endpoint_group.assert_called_once_with(
            description='my-desc',
            type='cidr',
            endpoints=['10.0.0.0/24', '20.0.0.0/24'],
            project_id=self.project.id,
            name=self._endpoint_group.name,
        )
        self.assertEqual(self.ordered_headers, tuple(sorted(headers)))
        self.assertEqual(self.ordered_data, data)


class TestDeleteEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.cmd = endpoint_group.DeleteEndpointGroup(self.app, None)

    def test_delete_with_one_resource(self):
        self.network_client.find_vpn_endpoint_group.side_effect = [
            self._endpoint_group
        ]

        arglist = [self._endpoint_group.id]
        verifylist = [('endpoint_group', [self._endpoint_group.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_vpn_endpoint_group.assert_called_once_with(
            self._endpoint_group.id
        )
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_e_g(*args, **kwargs):
            return _vpn_endpoint_group.VpnEndpointGroup(**{'id': args[0]})

        self.network_client.find_vpn_endpoint_group.side_effect = _mock_e_g

        arglist = ['target1', 'target2']
        verifylist = [('endpoint_group', ['target1', 'target2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(
            2, self.network_client.delete_vpn_endpoint_group.call_count
        )
        for idx, reference in enumerate(['target1', 'target2']):
            actual = ''.join(
                self.network_client.delete_vpn_endpoint_group.call_args_list[
                    idx
                ][0]
            )
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        arglist = ['target1']
        verifylist = [('endpoint_group', ['target1'])]

        self.network_client.find_vpn_ipsec_policy.side_effect = [
            'target1',
            exceptions.CommandError,
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestListEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()
        self.cmd = endpoint_group.ListEndpointGroup(self.app, None)

        self.short_header = (
            'ID',
            'Name',
            'Type',
            'Endpoints',
        )

        self.short_data = (
            self._endpoint_group['id'],
            self._endpoint_group['name'],
            self._endpoint_group['type'],
            self._endpoint_group['endpoints'],
        )

        self.network_client.vpn_endpoint_groups.return_value = [
            self._endpoint_group
        ]

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_endpoint_groups.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.vpn_endpoint_groups.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertEqual([self.short_data], list(data))


class TestSetEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()

        self.network_client.update_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )
        self.cmd = endpoint_group.SetEndpointGroup(self.app, None)

    def test_set_name(self):
        arglist = [self._endpoint_group.id, '--name', 'foo']
        verifylist = [
            ('endpoint_group', self._endpoint_group['id']),
            ('name', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_endpoint_group.assert_called_once_with(
            self._endpoint_group.id, name='foo'
        )
        self.assertIsNone(result)

    def test_set_description(self):
        arglist = [self._endpoint_group.id, '--description', 'foo']
        verifylist = [
            ('endpoint_group', self._endpoint_group.id),
            ('description', 'foo'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_vpn_endpoint_group.assert_called_once_with(
            self._endpoint_group.id, description='foo'
        )
        self.assertIsNone(result)


class TestShowEndpointGroup(TestEndpointGroup):
    def setUp(self):
        super().setUp()

        self.network_client.find_vpn_endpoint_group.return_value = (
            self._endpoint_group
        )
        self.network_client.find_vpn_endpoint_group.side_effect = None
        self.cmd = endpoint_group.ShowEndpointGroup(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        arglist = [self._endpoint_group.id]
        verifylist = [('endpoint_group', self._endpoint_group.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.find_vpn_endpoint_group.assert_called_once_with(
            self._endpoint_group.id, ignore_missing=False
        )
        self.assertEqual(self.ordered_headers, headers)
        self.assertCountEqual(self.ordered_data, data)
