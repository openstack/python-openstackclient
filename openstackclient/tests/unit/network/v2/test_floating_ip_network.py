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

from openstack.network.v2 import floating_ip as _floating_ip
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.network.v2 import floating_ip as fip
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestFloatingIPNetwork(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains


class TestCreateFloatingIPNetwork(TestFloatingIPNetwork):
    # Fake data for option tests.
    floating_network = network_fakes.create_one_network()
    subnet = network_fakes.FakeSubnet.create_one_subnet()
    port = network_fakes.create_one_port()

    # The floating ip created.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip(
        attrs={
            'floating_network_id': floating_network.id,
            'port_id': port.id,
            'dns_domain': 'example.org.',
            'dns_name': 'fip1',
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
        'qos_policy_id',
        'router_id',
        'status',
        'tags',
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
        floating_ip.qos_policy_id,
        floating_ip.router_id,
        floating_ip.status,
        floating_ip.tags,
    )

    def setUp(self):
        super().setUp()

        self.network_client.create_ip = mock.Mock(
            return_value=self.floating_ip
        )
        self.network_client.set_tags = mock.Mock(return_value=None)

        self.network_client.find_network = mock.Mock(
            return_value=self.floating_network
        )
        self.network_client.find_subnet = mock.Mock(return_value=self.subnet)
        self.network_client.find_port = mock.Mock(return_value=self.port)

        # Get the command object to test
        self.cmd = fip.CreateFloatingIP(self.app, None)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ip.assert_called_once_with(
            **{
                'floating_network_id': self.floating_ip.floating_network_id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--subnet',
            self.subnet.id,
            '--port',
            self.floating_ip.port_id,
            '--floating-ip-address',
            self.floating_ip.floating_ip_address,
            '--fixed-ip-address',
            self.floating_ip.fixed_ip_address,
            '--description',
            self.floating_ip.description,
            '--dns-domain',
            self.floating_ip.dns_domain,
            '--dns-name',
            self.floating_ip.dns_name,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('subnet', self.subnet.id),
            ('port', self.floating_ip.port_id),
            ('fixed_ip_address', self.floating_ip.fixed_ip_address),
            ('network', self.floating_ip.floating_network_id),
            ('description', self.floating_ip.description),
            ('dns_domain', self.floating_ip.dns_domain),
            ('dns_name', self.floating_ip.dns_name),
            ('floating_ip_address', self.floating_ip.floating_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ip.assert_called_once_with(
            **{
                'subnet_id': self.subnet.id,
                'port_id': self.floating_ip.port_id,
                'floating_ip_address': self.floating_ip.floating_ip_address,
                'fixed_ip_address': self.floating_ip.fixed_ip_address,
                'floating_network_id': self.floating_ip.floating_network_id,
                'description': self.floating_ip.description,
                'dns_domain': self.floating_ip.dns_domain,
                'dns_name': self.floating_ip.dns_name,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_floating_ip_create_project(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project',
            project.id,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ip.assert_called_once_with(
            **{
                'floating_network_id': self.floating_ip.floating_network_id,
                'project_id': project.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_floating_ip_create_project_domain(self):
        project = identity_fakes_v3.FakeProject.create_one_project()
        domain = identity_fakes_v3.FakeDomain.create_one_domain()
        self.projects_mock.get.return_value = project
        arglist = [
            "--project",
            project.name,
            "--project-domain",
            domain.name,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
            ('project', project.name),
            ('project_domain', domain.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ip.assert_called_once_with(
            **{
                'floating_network_id': self.floating_ip.floating_network_id,
                'project_id': project.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_floating_ip_with_qos(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        arglist = [
            '--qos-policy',
            qos_policy.id,
            self.floating_ip.floating_network_id,
        ]
        verifylist = [
            ('network', self.floating_ip.floating_network_id),
            ('qos_policy', qos_policy.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ip.assert_called_once_with(
            **{
                'floating_network_id': self.floating_ip.floating_network_id,
                'qos_policy_id': qos_policy.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def _test_create_with_tag(self, add_tags=True):
        arglist = [self.floating_ip.floating_network_id]
        if add_tags:
            arglist += ['--tag', 'red', '--tag', 'blue']
        else:
            arglist += ['--no-tag']

        verifylist = [
            ('network', self.floating_ip.floating_network_id),
        ]
        if add_tags:
            verifylist.append(('tags', ['red', 'blue']))
        else:
            verifylist.append(('no_tag', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_ip.assert_called_once_with(
            **{
                'floating_network_id': self.floating_ip.floating_network_id,
            }
        )
        if add_tags:
            self.network_client.set_tags.assert_called_once_with(
                self.floating_ip, tests_utils.CompareBySet(['red', 'blue'])
            )
        else:
            self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_tags(self):
        self._test_create_with_tag(add_tags=True)

    def test_create_with_no_tag(self):
        self._test_create_with_tag(add_tags=False)


class TestDeleteFloatingIPNetwork(TestFloatingIPNetwork):
    # The floating ips to be deleted.
    floating_ips = network_fakes.FakeFloatingIP.create_floating_ips(count=2)

    def setUp(self):
        super().setUp()

        self.network_client.delete_ip = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = fip.DeleteFloatingIP(self.app, None)

    def test_floating_ip_delete(self):
        self.network_client.find_ip.side_effect = [
            self.floating_ips[0],
            self.floating_ips[1],
        ]
        arglist = [
            self.floating_ips[0].id,
        ]
        verifylist = [
            ('floating_ip', [self.floating_ips[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.find_ip.assert_called_once_with(
            self.floating_ips[0].id,
            ignore_missing=False,
        )
        self.network_client.delete_ip.assert_called_once_with(
            self.floating_ips[0]
        )
        self.assertIsNone(result)

    def test_floating_ip_delete_multi(self):
        self.network_client.find_ip.side_effect = [
            self.floating_ips[0],
            self.floating_ips[1],
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
                self.floating_ips[0].id,
                ignore_missing=False,
            ),
            call(
                self.floating_ips[1].id,
                ignore_missing=False,
            ),
        ]
        self.network_client.find_ip.assert_has_calls(calls)

        calls = []
        for f in self.floating_ips:
            calls.append(call(f))
        self.network_client.delete_ip.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_floating_ip_delete_multi_exception(self):
        self.network_client.find_ip.side_effect = [
            self.floating_ips[0],
            exceptions.CommandError,
        ]
        arglist = [
            self.floating_ips[0].id,
            'unexist_floating_ip',
        ]
        verifylist = [
            ('floating_ip', [self.floating_ips[0].id, 'unexist_floating_ip']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 floating_ips failed to delete.', str(e))

        self.network_client.find_ip.assert_any_call(
            self.floating_ips[0].id,
            ignore_missing=False,
        )
        self.network_client.find_ip.assert_any_call(
            'unexist_floating_ip',
            ignore_missing=False,
        )
        self.network_client.delete_ip.assert_called_once_with(
            self.floating_ips[0]
        )


class TestListFloatingIPNetwork(TestFloatingIPNetwork):
    # The floating ips to list up
    floating_ips = network_fakes.FakeFloatingIP.create_floating_ips(count=3)
    fake_network = network_fakes.create_one_network(
        {
            'id': 'fake_network_id',
        }
    )
    fake_port = network_fakes.create_one_port(
        {
            'id': 'fake_port_id',
        }
    )
    fake_router = network_fakes.FakeRouter.create_one_router(
        {
            'id': 'fake_router_id',
        }
    )

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
        'Tags',
        'DNS Name',
        'DNS Domain',
    )

    data = []
    data_long = []
    for ip in floating_ips:
        data.append(
            (
                ip.id,
                ip.floating_ip_address,
                ip.fixed_ip_address,
                ip.port_id,
                ip.floating_network_id,
                ip.project_id,
            )
        )
        data_long.append(
            (
                ip.id,
                ip.floating_ip_address,
                ip.fixed_ip_address,
                ip.port_id,
                ip.floating_network_id,
                ip.project_id,
                ip.router_id,
                ip.status,
                ip.description,
                ip.tags,
                ip.dns_domain,
                ip.dns_name,
            )
        )

    def setUp(self):
        super().setUp()

        self.network_client.ips = mock.Mock(return_value=self.floating_ips)
        self.network_client.find_network = mock.Mock(
            return_value=self.fake_network
        )
        self.network_client.find_port = mock.Mock(return_value=self.fake_port)
        self.network_client.find_router = mock.Mock(
            return_value=self.fake_router
        )

        # Get the command object to test
        self.cmd = fip.ListFloatingIP(self.app, None)

    def test_floating_ip_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_network(self):
        arglist = [
            '--network',
            'fake_network_id',
        ]
        verifylist = [
            ('network', 'fake_network_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'floating_network_id': 'fake_network_id',
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_port(self):
        arglist = [
            '--port',
            'fake_port_id',
        ]
        verifylist = [
            ('port', 'fake_port_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'port_id': 'fake_port_id',
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_fixed_ip_address(self):
        arglist = [
            '--fixed-ip-address',
            self.floating_ips[0].fixed_ip_address,
        ]
        verifylist = [
            ('fixed_ip_address', self.floating_ips[0].fixed_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'fixed_ip_address': self.floating_ips[0].fixed_ip_address,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_floating_ip_address(self):
        arglist = [
            '--floating-ip-address',
            self.floating_ips[0].floating_ip_address,
        ]
        verifylist = [
            ('floating_ip_address', self.floating_ips[0].floating_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'floating_ip_address': self.floating_ips[
                    0
                ].floating_ip_address,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_floating_ip_list_status(self):
        arglist = [
            '--status',
            'ACTIVE',
            '--long',
        ]
        verifylist = [
            ('status', 'ACTIVE'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'status': 'ACTIVE',
            }
        )
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_floating_ip_list_project(self):
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
        filters = {'project_id': project.id}

        self.network_client.ips.assert_called_once_with(**filters)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_project_domain(self):
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

        self.network_client.ips.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_floating_ip_list_router(self):
        arglist = [
            '--router',
            'fake_router_id',
            '--long',
        ]
        verifylist = [
            ('router', 'fake_router_id'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'router_id': 'fake_router_id',
            }
        )
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_list_with_tag_options(self):
        arglist = [
            '--tags',
            'red,blue',
            '--any-tags',
            'red,green',
            '--not-tags',
            'orange,yellow',
            '--not-any-tags',
            'black,white',
        ]
        verifylist = [
            ('tags', ['red', 'blue']),
            ('any_tags', ['red', 'green']),
            ('not_tags', ['orange', 'yellow']),
            ('not_any_tags', ['black', 'white']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.ips.assert_called_once_with(
            **{
                'tags': 'red,blue',
                'any_tags': 'red,green',
                'not_tags': 'orange,yellow',
                'not_any_tags': 'black,white',
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFloatingIPNetwork(TestFloatingIPNetwork):
    def setUp(self):
        super().setUp()

        self.floating_ip = sdk_fakes.generate_fake_resource(
            _floating_ip.FloatingIP
        )
        self.network_client.find_ip = mock.Mock(return_value=self.floating_ip)

        self.columns = (
            'created_at',
            'description',
            'dns_domain',
            'dns_name',
            'fixed_ip_address',
            'floating_ip_address',
            'floating_network_id',
            'id',
            'name',
            'port_details',
            'port_id',
            'project_id',
            'qos_policy_id',
            'revision_number',
            'router_id',
            'status',
            'subnet_id',
            'tags',
            'updated_at',
        )
        self.data = (
            self.floating_ip.created_at,
            self.floating_ip.description,
            self.floating_ip.dns_domain,
            self.floating_ip.dns_name,
            self.floating_ip.fixed_ip_address,
            self.floating_ip.floating_ip_address,
            self.floating_ip.floating_network_id,
            self.floating_ip.id,
            self.floating_ip.name,
            format_columns.DictColumn(self.floating_ip.port_details),
            self.floating_ip.port_id,
            self.floating_ip.project_id,
            self.floating_ip.qos_policy_id,
            self.floating_ip.revision_number,
            self.floating_ip.router_id,
            self.floating_ip.status,
            self.floating_ip.subnet_id,
            self.floating_ip.tags,
            self.floating_ip.updated_at,
        )

        # Get the command object to test
        self.cmd = fip.ShowFloatingIP(self.app, None)

    def test_floating_ip_show(self):
        arglist = [
            self.floating_ip.id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestSetFloatingIP(TestFloatingIPNetwork):
    # Fake data for option tests.
    floating_network = network_fakes.create_one_network()
    subnet = network_fakes.FakeSubnet.create_one_subnet()
    port = network_fakes.create_one_port()

    # The floating ip to be set.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip(
        attrs={
            'floating_network_id': floating_network.id,
            'port_id': port.id,
            'tags': ['green', 'red'],
        }
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_ip = mock.Mock(return_value=self.floating_ip)
        self.network_client.find_port = mock.Mock(return_value=self.port)
        self.network_client.update_ip = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = fip.SetFloatingIP(self.app, None)

    def test_port_option(self):
        arglist = [
            self.floating_ip.id,
            '--port',
            self.floating_ip.port_id,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('port', self.floating_ip.port_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': self.floating_ip.port_id,
        }

        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )

        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def test_fixed_ip_option(self):
        arglist = [
            self.floating_ip.id,
            '--port',
            self.floating_ip.port_id,
            "--fixed-ip-address",
            self.floating_ip.fixed_ip_address,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('port', self.floating_ip.port_id),
            ('fixed_ip_address', self.floating_ip.fixed_ip_address),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': self.floating_ip.port_id,
            'fixed_ip_address': self.floating_ip.fixed_ip_address,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def test_description_option(self):
        arglist = [
            self.floating_ip.id,
            '--port',
            self.floating_ip.port_id,
            '--description',
            self.floating_ip.description,
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('port', self.floating_ip.port_id),
            ('description', self.floating_ip.description),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': self.floating_ip.port_id,
            'description': self.floating_ip.description,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def test_qos_policy_option(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        arglist = [
            "--qos-policy",
            qos_policy.id,
            self.floating_ip.id,
        ]
        verifylist = [
            ('qos_policy', qos_policy.id),
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'qos_policy_id': qos_policy.id,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def test_port_and_qos_policy_option(self):
        qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=qos_policy
        )
        arglist = [
            "--qos-policy",
            qos_policy.id,
            '--port',
            self.floating_ip.port_id,
            self.floating_ip.id,
        ]
        verifylist = [
            ('qos_policy', qos_policy.id),
            ('port', self.floating_ip.port_id),
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'qos_policy_id': qos_policy.id,
            'port_id': self.floating_ip.port_id,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def test_no_qos_policy_option(self):
        arglist = [
            "--no-qos-policy",
            self.floating_ip.id,
        ]
        verifylist = [
            ('no_qos_policy', True),
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'qos_policy_id': None,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def test_port_and_no_qos_policy_option(self):
        arglist = [
            "--no-qos-policy",
            '--port',
            self.floating_ip.port_id,
            self.floating_ip.id,
        ]
        verifylist = [
            ('no_qos_policy', True),
            ('port', self.floating_ip.port_id),
            ('floating_ip', self.floating_ip.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        attrs = {
            'qos_policy_id': None,
            'port_id': self.floating_ip.port_id,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

    def _test_set_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['red', 'blue', 'green']
        else:
            arglist = ['--no-tag']
            verifylist = [('no_tag', True)]
            expected_args = []
        arglist.extend([self.floating_ip.id])
        verifylist.extend([('floating_ip', self.floating_ip.id)])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_ip.called)
        self.network_client.set_tags.assert_called_once_with(
            self.floating_ip, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_set_with_tags(self):
        self._test_set_tags(with_tags=True)

    def test_set_with_no_tag(self):
        self._test_set_tags(with_tags=False)


class TestUnsetFloatingIP(TestFloatingIPNetwork):
    floating_network = network_fakes.create_one_network()
    subnet = network_fakes.FakeSubnet.create_one_subnet()
    port = network_fakes.create_one_port()

    # The floating ip to be unset.
    floating_ip = network_fakes.FakeFloatingIP.create_one_floating_ip(
        attrs={
            'floating_network_id': floating_network.id,
            'port_id': port.id,
            'tags': ['green', 'red'],
        }
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_ip = mock.Mock(return_value=self.floating_ip)
        self.network_client.update_ip = mock.Mock(return_value=None)
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = fip.UnsetFloatingIP(self.app, None)

    def test_floating_ip_unset_port(self):
        arglist = [
            self.floating_ip.id,
            "--port",
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'port_id': None,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

        self.assertIsNone(result)

    def test_floating_ip_unset_qos_policy(self):
        arglist = [
            self.floating_ip.id,
            "--qos-policy",
        ]
        verifylist = [
            ('floating_ip', self.floating_ip.id),
            ('qos_policy', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'qos_policy_id': None,
        }
        self.network_client.find_ip.assert_called_once_with(
            self.floating_ip.id,
            ignore_missing=False,
        )
        self.network_client.update_ip.assert_called_once_with(
            self.floating_ip, **attrs
        )

        self.assertIsNone(result)

    def _test_unset_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['green']
        else:
            arglist = ['--all-tag']
            verifylist = [('all_tag', True)]
            expected_args = []
        arglist.append(self.floating_ip.id)
        verifylist.append(('floating_ip', self.floating_ip.id))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_ip.called)
        self.network_client.set_tags.assert_called_once_with(
            self.floating_ip, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_unset_with_tags(self):
        self._test_unset_tags(with_tags=True)

    def test_unset_with_all_tag(self):
        self._test_unset_tags(with_tags=False)
