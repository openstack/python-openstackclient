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

import mock
from mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import floating_ip
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


# Tests for Neutron network
#
class TestFloatingIPNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestFloatingIPNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateFloatingIPNetwork(TestFloatingIPNetwork):

    # Fake data for option tests.
    floating_network = network_fakes.FakeNetwork.create_one_network()
    subnet = network_fakes.FakeSubnet.create_one_subnet()
    port = network_fakes.FakePort.create_one_port()

    # The floating ip to be deleted.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip(
        attrs={
            'floating_network_id': floating_network.id,
            'port_id': port.id,
        }
    )

    columns = (
        'description',
        'dns_domain',
        'dns_name',
        'fixed_ip_address',
        'floating_ip_address',
        'floating_network_id',
        'id',
        'port_id',
        'project_id',
        'router_id',
        'status',
    )

    data = (
        floating_ip.description,
        floating_ip.dns_domain,
        floating_ip.dns_name,
        floating_ip.fixed_ip_address,
        floating_ip.floating_ip_address,
        floating_ip.floating_network_id,
        floating_ip.id,
        floating_ip.port_id,
        floating_ip.project_id,
        floating_ip.router_id,
        floating_ip.status,
    )

    def setUp(self):
        super(TestCreateFloatingIPNetwork, self).setUp()

        self.network.create_ip = mock.Mock(return_value=self.floating_ip)

        self.network.find_network = mock.Mock(
            return_value=self.floating_network)
        self.network.find_subnet = mock.Mock(return_value=self.subnet)
        self.network.find_port = mock.Mock(return_value=self.port)

        # Get the command object to test
        self.cmd = floating_ip.CreateFloatingIP(self.app, self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_ip.assert_called_once_with(**{
            'floating_network_id': self.floating_ip.floating_network_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--subnet', self.subnet.id,
            '--port', self.floating_ip.port_id,
            '--floating-ip-address', self.floating_ip.floating_ip_address,
            '--fixed-ip-address', self.floating_ip.fixed_ip_address,
            '--description', self.floating_ip.description,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('subnet', self.subnet.id),
            ('port', self.floating_ip.port_id),
            ('fixed_ip_address', self.floating_ip.fixed_ip_address),
            ('network', self.floating_ip.floating_network_id),
            ('description', self.floating_ip.description),
            ('floating_ip_address', self.floating_ip.floating_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_ip.assert_called_once_with(**{
            'subnet_id': self.subnet.id,
            'port_id': self.floating_ip.port_id,
            'floating_ip_address': self.floating_ip.floating_ip_address,
            'fixed_ip_address': self.floating_ip.fixed_ip_address,
            'floating_network_id': self.floating_ip.floating_network_id,
            'description': self.floating_ip.description,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_floating_ip_create_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_ip.assert_called_once_with(**{
            'floating_network_id': self.floating_ip.floating_network_id,
            'tenant_id': project.id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_floating_ip_create_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        domain = identity_fakes_v3.FakeDomain.create_one_domain()
        self.projects_mock.get.return_value = project
        arglist = [
            "--project", project.name,
            "--project-domain", domain.name,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
            ('project', project.name),
            ('project_domain', domain.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_ip.assert_called_once_with(**{
            'floating_network_id': self.floating_ip.floating_network_id,
            'tenant_id': project.id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteFloatingIPNetwork(TestFloatingIPNetwork):

    # The floating ips to be deleted.
    floating_ips = network_fakes.FakeFloatingIP.create_floating_ips(count=2)

    def setUp(self):
        super(TestDeleteFloatingIPNetwork, self).setUp()

        self.network.delete_ip = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = floating_ip.DeleteFloatingIP(self.app, self.namespace)

    @mock.patch(
        "openstackclient.tests.unit.network.v2.test_floating_ip." +
        "floating_ip._find_floating_ip"
    )
    def test_floating_ip_delete(self, find_floating_ip_mock):
        find_floating_ip_mock.side_effect = [
            (self.floating_ips[0], []),
            (self.floating_ips[1], []),
        ]
        arglist = [
            self.floating_ips[0].id,
        ]
        verifylist = [
            ('floating_ip', [self.floating_ips[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        find_floating_ip_mock.assert_called_once_with(
            mock.ANY,
            [],
            self.floating_ips[0].id,
            ignore_missing=False,
        )
        self.network.delete_ip.assert_called_once_with(self.floating_ips[0])
        self.assertIsNone(result)

    @mock.patch(
        "openstackclient.tests.unit.network.v2.test_floating_ip." +
        "floating_ip._find_floating_ip"
    )
    def test_floating_ip_delete_multi(self, find_floating_ip_mock):
        find_floating_ip_mock.side_effect = [
            (self.floating_ips[0], []),
            (self.floating_ips[1], []),
        ]
        arglist = []
        verifylist = []

        for f in self.floating_ips:
            arglist.append(f.id)
        verifylist = [
            ('floating_ip', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [
            call(
                mock.ANY,
                [],
                self.floating_ips[0].id,
                ignore_missing=False,
            ),
            call(
                mock.ANY,
                [],
                self.floating_ips[1].id,
                ignore_missing=False,
            ),
        ]
        find_floating_ip_mock.assert_has_calls(calls)

        calls = []
        for f in self.floating_ips:
            calls.append(call(f))
        self.network.delete_ip.assert_has_calls(calls)
        self.assertIsNone(result)

    @mock.patch(
        "openstackclient.tests.unit.network.v2.test_floating_ip." +
        "floating_ip._find_floating_ip"
    )
    def test_floating_ip_delete_multi_exception(self, find_floating_ip_mock):
        find_floating_ip_mock.side_effect = [
            (self.floating_ips[0], []),
            exceptions.CommandError,
        ]
        arglist = [
            self.floating_ips[0].id,
            'unexist_floating_ip',
        ]
        verifylist = [
            ('floating_ip',
             [self.floating_ips[0].id, 'unexist_floating_ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 floating_ips failed to delete.', str(e))

        find_floating_ip_mock.assert_any_call(
            mock.ANY,
            [],
            self.floating_ips[0].id,
            ignore_missing=False,
        )
        find_floating_ip_mock.assert_any_call(
            mock.ANY,
            [],
            'unexist_floating_ip',
            ignore_missing=False,
        )
        self.network.delete_ip.assert_called_once_with(
            self.floating_ips[0]
        )


class TestListFloatingIPNetwork(TestFloatingIPNetwork):

    # The floating ips to list up
    floating_ips = network_fakes.FakeFloatingIP.create_floating_ips(count=3)
    fake_network = network_fakes.FakeNetwork.create_one_network({
        'id': 'fake_network_id',
    })
    fake_port = network_fakes.FakePort.create_one_port({
        'id': 'fake_port_id',
    })
    fake_router = network_fakes.FakeRouter.create_one_router({
        'id': 'fake_router_id',
    })

    columns = (
        'ID',
        'Floating IP Address',
        'Fixed IP Address',
        'Port',
        'Floating Network',
        'Project',
    )
    columns_long = columns + (
        'Router',
        'Status',
        'Description',
    )

    data = []
    data_long = []
    for ip in floating_ips:
        data.append((
            ip.id,
            ip.floating_ip_address,
            ip.fixed_ip_address,
            ip.port_id,
            ip.floating_network_id,
            ip.tenant_id,
        ))
        data_long.append((
            ip.id,
            ip.floating_ip_address,
            ip.fixed_ip_address,
            ip.port_id,
            ip.floating_network_id,
            ip.tenant_id,
            ip.router_id,
            ip.status,
            ip.description,
        ))

    def setUp(self):
        super(TestListFloatingIPNetwork, self).setUp()

        self.network.ips = mock.Mock(return_value=self.floating_ips)
        self.network.find_network = mock.Mock(return_value=self.fake_network)
        self.network.find_port = mock.Mock(return_value=self.fake_port)
        self.network.find_router = mock.Mock(return_value=self.fake_router)

        # Get the command object to test
        self.cmd = floating_ip.ListFloatingIP(self.app, self.namespace)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_network(self):
        arglist = [
            '--network', 'fake_network_id',
        ]
        verifylist = [
            ('network', 'fake_network_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with(**{
            'floating_network_id': 'fake_network_id',
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_port(self):
        arglist = [
            '--port', 'fake_port_id',
        ]
        verifylist = [
            ('port', 'fake_port_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with(**{
            'port_id': 'fake_port_id',
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_fixed_ip_address(self):
        arglist = [
            '--fixed-ip-address', self.floating_ips[0].fixed_ip_address,
        ]
        verifylist = [
            ('fixed_ip_address', self.floating_ips[0].fixed_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with(**{
            'fixed_ip_address': self.floating_ips[0].fixed_ip_address,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_long(self):
        arglist = ['--long', ]
        verifylist = [('long', True), ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_floating_ip_list_status(self):
        arglist = [
            '--status', 'ACTIVE',
            '--long',
        ]
        verifylist = [
            ('status', 'ACTIVE'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with(**{
            'status': 'ACTIVE',
        })
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_floating_ip_list_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'tenant_id': project.id,
                   'project_id': project.id, }

        self.network.ips.assert_called_once_with(**filters)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project', project.id,
            '--project-domain', project.domain_id,
        ]
        verifylist = [
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {'tenant_id': project.id,
                   'project_id': project.id, }

        self.network.ips.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_router(self):
        arglist = [
            '--router', 'fake_router_id',
            '--long',
        ]
        verifylist = [
            ('router', 'fake_router_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.ips.assert_called_once_with(**{
            'router_id': 'fake_router_id',
        })
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestShowFloatingIPNetwork(TestFloatingIPNetwork):

    # The floating ip to display.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'description',
        'dns_domain',
        'dns_name',
        'fixed_ip_address',
        'floating_ip_address',
        'floating_network_id',
        'id',
        'port_id',
        'project_id',
        'router_id',
        'status',
    )

    data = (
        floating_ip.description,
        floating_ip.dns_domain,
        floating_ip.dns_name,
        floating_ip.fixed_ip_address,
        floating_ip.floating_ip_address,
        floating_ip.floating_network_id,
        floating_ip.id,
        floating_ip.port_id,
        floating_ip.project_id,
        floating_ip.router_id,
        floating_ip.status,
    )

    def setUp(self):
        super(TestShowFloatingIPNetwork, self).setUp()

        self.network.find_ip = mock.Mock(return_value=self.floating_ip)

        # Get the command object to test
        self.cmd = floating_ip.ShowFloatingIP(self.app, self.namespace)

    @mock.patch(
        "openstackclient.tests.unit.network.v2.test_floating_ip." +
        "floating_ip._find_floating_ip"
    )
    def test_floating_ip_show(self, find_floating_ip_mock):
        find_floating_ip_mock.return_value = (self.floating_ip, [])
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        find_floating_ip_mock.assert_called_once_with(
            mock.ANY,
            [],
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


# Tests for Nova network
#
class TestFloatingIPCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFloatingIPCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestCreateFloatingIPCompute(TestFloatingIPCompute):

    # The floating ip to be deleted.
    floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        floating_ip.fixed_ip,
        floating_ip.id,
        floating_ip.instance_id,
        floating_ip.ip,
        floating_ip.pool,
    )

    def setUp(self):
        super(TestCreateFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.create.return_value = self.floating_ip

        # Get the command object to test
        self.cmd = floating_ip.CreateFloatingIP(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.floating_ip.pool,
        ]
        verifylist = [
            ('network', self.floating_ip.pool),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.create.assert_called_once_with(
            self.floating_ip.pool)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteFloatingIPCompute(TestFloatingIPCompute):

    # The floating ips to be deleted.
    floating_ips = compute_fakes.FakeFloatingIP.create_floating_ips(count=2)

    def setUp(self):
        super(TestDeleteFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.delete.return_value = None

        # Return value of utils.find_resource()
        self.compute.floating_ips.get = (
            compute_fakes.FakeFloatingIP.get_floating_ips(self.floating_ips))

        # Get the command object to test
        self.cmd = floating_ip.DeleteFloatingIP(self.app, None)

    def test_floating_ip_delete(self):
        arglist = [
            self.floating_ips[0].id,
        ]
        verifylist = [
            ('floating_ip', [self.floating_ips[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.delete.assert_called_once_with(
            self.floating_ips[0].id
        )
        self.assertIsNone(result)

    def test_multi_floating_ips_delete(self):
        arglist = []
        verifylist = []

        for f in self.floating_ips:
            arglist.append(f.id)
        verifylist = [
            ('floating_ip', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for f in self.floating_ips:
            calls.append(call(f.id))
        self.compute.floating_ips.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_floating_ips_delete_with_exception(self):
        arglist = [
            self.floating_ips[0].id,
            'unexist_floating_ip',
        ]
        verifylist = [
            ('floating_ip',
             [self.floating_ips[0].id, 'unexist_floating_ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.floating_ips[0], exceptions.CommandError]
        self.compute.floating_ips.get = (
            mock.Mock(side_effect=find_mock_result)
        )
        self.compute.floating_ips.find.side_effect = exceptions.NotFound(None)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 floating_ips failed to delete.', str(e))

        self.compute.floating_ips.get.assert_any_call(
            self.floating_ips[0].id)
        self.compute.floating_ips.get.assert_any_call(
            'unexist_floating_ip')
        self.compute.floating_ips.delete.assert_called_once_with(
            self.floating_ips[0].id
        )


class TestListFloatingIPCompute(TestFloatingIPCompute):

    # The floating ips to be list up
    floating_ips = compute_fakes.FakeFloatingIP.create_floating_ips(count=3)

    columns = (
        'ID',
        'Floating IP Address',
        'Fixed IP Address',
        'Server',
        'Pool',
    )

    data = []
    for ip in floating_ips:
        data.append((
            ip.id,
            ip.ip,
            ip.fixed_ip,
            ip.instance_id,
            ip.pool,
        ))

    def setUp(self):
        super(TestListFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.floating_ips.list.return_value = self.floating_ips

        # Get the command object to test
        self.cmd = floating_ip.ListFloatingIP(self.app, None)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.floating_ips.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFloatingIPCompute(TestFloatingIPCompute):

    # The floating ip to display.
    floating_ip = compute_fakes.FakeFloatingIP.create_one_floating_ip()

    columns = (
        'fixed_ip',
        'id',
        'instance_id',
        'ip',
        'pool',
    )

    data = (
        floating_ip.fixed_ip,
        floating_ip.id,
        floating_ip.instance_id,
        floating_ip.ip,
        floating_ip.pool,
    )

    def setUp(self):
        super(TestShowFloatingIPCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        # Return value of utils.find_resource()
        self.compute.floating_ips.get.return_value = self.floating_ip

        # Get the command object to test
        self.cmd = floating_ip.ShowFloatingIP(self.app, None)

    def test_floating_ip_show(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
