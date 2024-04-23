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

from openstackclient.network.v2 import ndp_proxy
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNDPProxy(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains

        self.router = network_fakes.FakeRouter.create_one_router(
            {'id': 'fake-router-id'}
        )
        self.network_client.find_router = mock.Mock(return_value=self.router)
        self.port = network_fakes.create_one_port()
        self.network_client.find_port = mock.Mock(return_value=self.port)


class TestCreateNDPProxy(TestNDPProxy):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id, 'port_id': self.port.id}
        self.ndp_proxy = network_fakes.create_one_ndp_proxy(attrs)
        self.columns = (
            'created_at',
            'description',
            'id',
            'ip_address',
            'name',
            'port_id',
            'project_id',
            'revision_number',
            'router_id',
            'updated_at',
        )

        self.data = (
            self.ndp_proxy.created_at,
            self.ndp_proxy.description,
            self.ndp_proxy.id,
            self.ndp_proxy.ip_address,
            self.ndp_proxy.name,
            self.ndp_proxy.port_id,
            self.ndp_proxy.project_id,
            self.ndp_proxy.revision_number,
            self.ndp_proxy.router_id,
            self.ndp_proxy.updated_at,
        )
        self.network_client.create_ndp_proxy = mock.Mock(
            return_value=self.ndp_proxy
        )

        # Get the command object to test
        self.cmd = ndp_proxy.CreateNDPProxy(self.app, None)

    def test_create_no_options(self):
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

    def test_create_all_options(self):
        arglist = [
            self.ndp_proxy.router_id,
            '--name',
            self.ndp_proxy.name,
            '--port',
            self.ndp_proxy.port_id,
            '--ip-address',
            self.ndp_proxy.ip_address,
            '--description',
            self.ndp_proxy.description,
        ]
        verifylist = [
            ('name', self.ndp_proxy.name),
            ('router', self.ndp_proxy.router_id),
            ('port', self.ndp_proxy.port_id),
            ('ip_address', self.ndp_proxy.ip_address),
            ('description', self.ndp_proxy.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ndp_proxy.assert_called_once_with(
            **{
                'name': self.ndp_proxy.name,
                'router_id': self.ndp_proxy.router_id,
                'ip_address': self.ndp_proxy.ip_address,
                'port_id': self.ndp_proxy.port_id,
                'description': self.ndp_proxy.description,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNDPProxy(TestNDPProxy):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id, 'port_id': self.port.id}
        self.ndp_proxies = network_fakes.create_ndp_proxies(attrs)
        self.ndp_proxy = self.ndp_proxies[0]
        self.network_client.delete_ndp_proxy = mock.Mock(return_value=None)
        self.network_client.find_ndp_proxy = mock.Mock(
            return_value=self.ndp_proxy
        )

        # Get the command object to test
        self.cmd = ndp_proxy.DeleteNDPProxy(self.app, None)

    def test_delete(self):
        arglist = [self.ndp_proxy.id]
        verifylist = [('ndp_proxy', [self.ndp_proxy.id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network_client.delete_ndp_proxy.assert_called_once_with(
            self.ndp_proxy
        )
        self.assertIsNone(result)

    def test_delete_error(self):
        arglist = [
            self.ndp_proxy.id,
        ]
        verifylist = [('ndp_proxy', [self.ndp_proxy.id])]
        self.network_client.delete_ndp_proxy.side_effect = Exception(
            'Error message'
        )
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_multi_ndp_proxies_delete(self):
        arglist = []
        np_id = []

        for a in self.ndp_proxies:
            arglist.append(a.id)
            np_id.append(a.id)

        verifylist = [
            ('ndp_proxy', np_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_ndp_proxy.assert_has_calls(
            [call(self.ndp_proxy), call(self.ndp_proxy)]
        )
        self.assertIsNone(result)


class TestListNDPProxy(TestNDPProxy):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id, 'port_id': self.port.id}
        ndp_proxies = network_fakes.create_ndp_proxies(attrs, count=3)
        self.columns = (
            'ID',
            'Name',
            'Router ID',
            'IP Address',
            'Project',
        )
        self.data = []
        for np in ndp_proxies:
            self.data.append(
                (
                    np.id,
                    np.name,
                    np.router_id,
                    np.ip_address,
                    np.project_id,
                )
            )

        self.network_client.ndp_proxies = mock.Mock(return_value=ndp_proxies)

        # Get the command object to test
        self.cmd = ndp_proxy.ListNDPProxy(self.app, None)

    def test_ndp_proxy_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ndp_proxies.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        list_data = list(data)
        self.assertEqual(len(self.data), len(list_data))
        for index in range(len(list_data)):
            self.assertEqual(self.data[index], list_data[index])

    def test_ndp_proxy_list_router(self):
        arglist = [
            '--router',
            'fake-router-name',
        ]

        verifylist = [('router', 'fake-router-name')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ndp_proxies.assert_called_once_with(
            **{'router_id': 'fake-router-id'}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_ndp_proxy_list_port(self):
        arglist = [
            '--port',
            self.port.id,
        ]

        verifylist = [('port', self.port.id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ndp_proxies.assert_called_once_with(
            **{'port_id': self.port.id}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_ndp_proxy_list_name(self):
        arglist = [
            '--name',
            'fake-ndp-proxy-name',
        ]

        verifylist = [('name', 'fake-ndp-proxy-name')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ndp_proxies.assert_called_once_with(
            **{'name': 'fake-ndp-proxy-name'}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_ndp_proxy_list_ip_address(self):
        arglist = [
            '--ip-address',
            '2001::1:2',
        ]

        verifylist = [('ip_address', '2001::1:2')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ndp_proxies.assert_called_once_with(
            **{'ip_address': '2001::1:2'}
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_ndp_proxy_list_project(self):
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

        self.network_client.ndp_proxies.assert_called_once_with(
            **{'project_id': project.id}
        )
        self.assertEqual(self.columns, columns)
        self.assertItemsEqual(self.data, list(data))

    def test_ndp_proxy_list_project_domain(self):
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

        self.network_client.ndp_proxies.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertItemsEqual(self.data, list(data))


class TestSetNDPProxy(TestNDPProxy):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id, 'port_id': self.port.id}
        self.ndp_proxy = network_fakes.create_one_ndp_proxy(attrs)
        self.network_client.update_ndp_proxy = mock.Mock(return_value=None)
        self.network_client.find_ndp_proxy = mock.Mock(
            return_value=self.ndp_proxy
        )

        # Get the command object to test
        self.cmd = ndp_proxy.SetNDPProxy(self.app, None)

    def test_set_nothing(self):
        arglist = [
            self.ndp_proxy.id,
        ]
        verifylist = [
            ('ndp_proxy', self.ndp_proxy.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_ndp_proxy.assert_called_once_with(
            self.ndp_proxy
        )
        self.assertIsNone(result)

    def test_set_name(self):
        arglist = [
            self.ndp_proxy.id,
            '--name',
            'fake-name',
        ]
        verifylist = [
            ('ndp_proxy', self.ndp_proxy.id),
            ('name', 'fake-name'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_ndp_proxy.assert_called_once_with(
            self.ndp_proxy, name='fake-name'
        )
        self.assertIsNone(result)

    def test_set_description(self):
        arglist = [
            self.ndp_proxy.id,
            '--description',
            'balala',
        ]
        verifylist = [
            ('ndp_proxy', self.ndp_proxy.id),
            ('description', 'balala'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_ndp_proxy.assert_called_once_with(
            self.ndp_proxy, description='balala'
        )
        self.assertIsNone(result)


class TestShowNDPProxy(TestNDPProxy):
    def setUp(self):
        super().setUp()
        attrs = {'router_id': self.router.id, 'port_id': self.port.id}
        self.ndp_proxy = network_fakes.create_one_ndp_proxy(attrs)

        self.columns = (
            'created_at',
            'description',
            'id',
            'ip_address',
            'name',
            'port_id',
            'project_id',
            'revision_number',
            'router_id',
            'updated_at',
        )

        self.data = (
            self.ndp_proxy.created_at,
            self.ndp_proxy.description,
            self.ndp_proxy.id,
            self.ndp_proxy.ip_address,
            self.ndp_proxy.name,
            self.ndp_proxy.port_id,
            self.ndp_proxy.project_id,
            self.ndp_proxy.revision_number,
            self.ndp_proxy.router_id,
            self.ndp_proxy.updated_at,
        )
        self.network_client.get_ndp_proxy = mock.Mock(
            return_value=self.ndp_proxy
        )
        self.network_client.find_ndp_proxy = mock.Mock(
            return_value=self.ndp_proxy
        )

        # Get the command object to test
        self.cmd = ndp_proxy.ShowNDPProxy(self.app, None)

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

    def test_show_default_options(self):
        arglist = [
            self.ndp_proxy.id,
        ]
        verifylist = [
            ('ndp_proxy', self.ndp_proxy.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_ndp_proxy.assert_called_once_with(
            self.ndp_proxy.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
