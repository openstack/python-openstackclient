#   Copyright 2021 Huawei, Inc. All rights reserved.
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

from unittest import mock
from unittest.mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import local_ip
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestLocalIP(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains


class TestCreateLocalIP(TestLocalIP):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    local_ip_network = network_fakes.create_one_network()
    port = network_fakes.create_one_port()
    # The new local ip created.
    new_local_ip = network_fakes.create_one_local_ip(
        attrs={
            'project_id': project.id,
            'network_id': local_ip_network.id,
            'local_port_id': port.id,
        }
    )

    columns = (
        'created_at',
        'description',
        'id',
        'name',
        'project_id',
        'local_port_id',
        'network_id',
        'local_ip_address',
        'ip_mode',
        'revision_number',
        'updated_at',
    )
    data = (
        new_local_ip.created_at,
        new_local_ip.description,
        new_local_ip.id,
        new_local_ip.name,
        new_local_ip.project_id,
        new_local_ip.local_port_id,
        new_local_ip.network_id,
        new_local_ip.local_ip_address,
        new_local_ip.ip_mode,
        new_local_ip.revision_number,
        new_local_ip.updated_at,
    )

    def setUp(self):
        super().setUp()
        self.network_client.create_local_ip = mock.Mock(
            return_value=self.new_local_ip
        )
        self.network_client.find_network = mock.Mock(
            return_value=self.local_ip_network
        )
        self.network_client.find_port = mock.Mock(return_value=self.port)

        # Get the command object to test
        self.cmd = local_ip.CreateLocalIP(self.app, None)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

    def test_create_no_options(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_local_ip.assert_called_once_with(**{})
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--project-domain',
            self.domain.name,
            '--description',
            self.new_local_ip.description,
            '--name',
            self.new_local_ip.name,
            '--network',
            self.new_local_ip.network_id,
            '--local-port',
            self.new_local_ip.local_port_id,
            '--local-ip-address',
            '10.0.0.1',
            '--ip-mode',
            self.new_local_ip.ip_mode,
        ]
        verifylist = [
            ('project_domain', self.domain.name),
            ('description', self.new_local_ip.description),
            ('name', self.new_local_ip.name),
            ('network', self.new_local_ip.network_id),
            ('local_port', self.new_local_ip.local_port_id),
            ('local_ip_address', '10.0.0.1'),
            ('ip_mode', self.new_local_ip.ip_mode),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_local_ip.assert_called_once_with(
            **{
                'name': self.new_local_ip.name,
                'description': self.new_local_ip.description,
                'network_id': self.new_local_ip.network_id,
                'local_port_id': self.new_local_ip.local_port_id,
                'local_ip_address': '10.0.0.1',
                'ip_mode': self.new_local_ip.ip_mode,
            }
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, data)


class TestDeleteLocalIP(TestLocalIP):
    # The local ip to delete.
    _local_ips = network_fakes.create_local_ips(count=2)

    def setUp(self):
        super().setUp()
        self.network_client.delete_local_ip = mock.Mock(return_value=None)
        self.network_client.find_local_ip = network_fakes.get_local_ips(
            local_ips=self._local_ips
        )

        # Get the command object to test
        self.cmd = local_ip.DeleteLocalIP(self.app, None)

    def test_local_ip_delete(self):
        arglist = [
            self._local_ips[0].name,
        ]
        verifylist = [
            ('local_ip', [self._local_ips[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.find_local_ip.assert_called_once_with(
            self._local_ips[0].name, ignore_missing=False
        )
        self.network_client.delete_local_ip.assert_called_once_with(
            self._local_ips[0]
        )
        self.assertIsNone(result)

    def test_multi_local_ips_delete(self):
        arglist = []

        for a in self._local_ips:
            arglist.append(a.name)
        verifylist = [
            ('local_ip', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._local_ips:
            calls.append(call(a))
        self.network_client.delete_local_ip.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_local_ips_delete_with_exception(self):
        arglist = [
            self._local_ips[0].name,
            'unexist_local_ip',
        ]
        verifylist = [
            ('local_ip', [self._local_ips[0].name, 'unexist_local_ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._local_ips[0], exceptions.CommandError]
        self.network_client.find_local_ip = mock.Mock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 local IPs failed to delete.', str(e))

        self.network_client.find_local_ip.assert_any_call(
            self._local_ips[0].name, ignore_missing=False
        )
        self.network_client.find_local_ip.assert_any_call(
            'unexist_local_ip', ignore_missing=False
        )
        self.network_client.delete_local_ip.assert_called_once_with(
            self._local_ips[0]
        )


class TestListLocalIP(TestLocalIP):
    # The local ip to list up.
    local_ips = network_fakes.create_local_ips(count=3)
    fake_network = network_fakes.create_one_network({'id': 'fake_network_id'})

    columns = (
        'ID',
        'Name',
        'Description',
        'Project',
        'Local Port ID',
        'Network',
        'Local IP address',
        'IP mode',
    )
    data = []
    for lip in local_ips:
        data.append(
            (
                lip.id,
                lip.name,
                lip.description,
                lip.project_id,
                lip.local_port_id,
                lip.network_id,
                lip.local_ip_address,
                lip.ip_mode,
            )
        )

    def setUp(self):
        super().setUp()
        self.network_client.local_ips = mock.Mock(return_value=self.local_ips)
        self.network_client.find_network = mock.Mock(
            return_value=self.fake_network
        )

        # Get the command object to test
        self.cmd = local_ip.ListLocalIP(self.app, None)

    def test_local_ip_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ips.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_local_ip_list_name(self):
        arglist = [
            '--name',
            self.local_ips[0].name,
        ]
        verifylist = [
            ('name', self.local_ips[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ips.assert_called_once_with(
            **{'name': self.local_ips[0].name}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_local_ip_list_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project',
            project.id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ips.assert_called_once_with(
            **{'project_id': project.id}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_local_ip_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project',
            project.id,
            '--project-domain',
            project.domain_id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'project_id': project.id}

        self.network_client.local_ips.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_local_ip_list_network(self):
        arglist = [
            '--network',
            'fake_network_id',
        ]
        verifylist = [
            ('network', 'fake_network_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ips.assert_called_once_with(
            **{
                'network_id': 'fake_network_id',
            }
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_local_ip_list_local_ip_address(self):
        arglist = [
            '--local-ip-address',
            self.local_ips[0].local_ip_address,
        ]
        verifylist = [
            ('local_ip_address', self.local_ips[0].local_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ips.assert_called_once_with(
            **{
                'local_ip_address': self.local_ips[0].local_ip_address,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_local_ip_list_ip_mode(self):
        arglist = [
            '--ip-mode',
            self.local_ips[0].ip_mode,
        ]
        verifylist = [
            ('ip_mode', self.local_ips[0].ip_mode),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.local_ips.assert_called_once_with(
            **{
                'ip_mode': self.local_ips[0].ip_mode,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetLocalIP(TestLocalIP):
    # The local ip to set.
    _local_ip = network_fakes.create_one_local_ip()

    def setUp(self):
        super().setUp()
        self.network_client.update_local_ip = mock.Mock(return_value=None)
        self.network_client.find_local_ip = mock.Mock(
            return_value=self._local_ip
        )

        # Get the command object to test
        self.cmd = local_ip.SetLocalIP(self.app, None)

    def test_set_nothing(self):
        arglist = [
            self._local_ip.name,
        ]
        verifylist = [
            ('local_ip', self._local_ip.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_local_ip.assert_not_called()
        self.assertIsNone(result)

    def test_set_name_and_description(self):
        arglist = [
            '--name',
            'new_local_ip_name',
            '--description',
            'new_local_ip_description',
            self._local_ip.name,
        ]
        verifylist = [
            ('name', 'new_local_ip_name'),
            ('description', 'new_local_ip_description'),
            ('local_ip', self._local_ip.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': "new_local_ip_name",
            'description': 'new_local_ip_description',
        }
        self.network_client.update_local_ip.assert_called_with(
            self._local_ip, **attrs
        )
        self.assertIsNone(result)


class TestShowLocalIP(TestLocalIP):
    # The local ip to show.
    _local_ip = network_fakes.create_one_local_ip()
    columns = (
        'created_at',
        'description',
        'id',
        'name',
        'project_id',
        'local_port_id',
        'network_id',
        'local_ip_address',
        'ip_mode',
        'revision_number',
        'updated_at',
    )
    data = (
        _local_ip.created_at,
        _local_ip.description,
        _local_ip.id,
        _local_ip.name,
        _local_ip.project_id,
        _local_ip.local_port_id,
        _local_ip.network_id,
        _local_ip.local_ip_address,
        _local_ip.ip_mode,
        _local_ip.revision_number,
        _local_ip.updated_at,
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_local_ip = mock.Mock(
            return_value=self._local_ip
        )

        # Get the command object to test
        self.cmd = local_ip.ShowLocalIP(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_all_options(self):
        arglist = [
            self._local_ip.name,
        ]
        verifylist = [
            ('local_ip', self._local_ip.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_local_ip.assert_called_once_with(
            self._local_ip.name, ignore_missing=False
        )
        self.assertEqual(set(self.columns), set(columns))
        self.assertCountEqual(self.data, list(data))
