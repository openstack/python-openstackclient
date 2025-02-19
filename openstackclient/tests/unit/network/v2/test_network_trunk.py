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
from unittest import mock
from unittest.mock import call

from osc_lib.cli import format_columns
from osc_lib import exceptions
import testtools

from openstackclient.network.v2 import network_trunk
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as test_utils


# Tests for Neutron trunks
#
class TestNetworkTrunk(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains


class TestCreateNetworkTrunk(TestNetworkTrunk):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    trunk_networks = network_fakes.create_networks(count=2)
    parent_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[0]['id']}
    )
    sub_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[1]['id']}
    )

    new_trunk = network_fakes.create_one_trunk(
        attrs={
            'project_id': project.id,
            'port_id': parent_port['id'],
            'sub_ports': {
                'port_id': sub_port['id'],
                'segmentation_id': 42,
                'segmentation_type': 'vlan',
            },
        }
    )

    columns = (
        'description',
        'id',
        'is_admin_state_up',
        'name',
        'port_id',
        'project_id',
        'status',
        'sub_ports',
        'tags',
    )
    data = (
        new_trunk.description,
        new_trunk.id,
        new_trunk.is_admin_state_up,
        new_trunk.name,
        new_trunk.port_id,
        new_trunk.project_id,
        new_trunk.status,
        format_columns.ListDictColumn(new_trunk.sub_ports),
        [],
    )

    def setUp(self):
        super().setUp()
        self.network_client.create_trunk = mock.Mock(
            return_value=self.new_trunk
        )
        self.network_client.find_port = mock.Mock(
            side_effect=[self.parent_port, self.sub_port]
        )

        # Get the command object to test
        self.cmd = network_trunk.CreateNetworkTrunk(self.app, None)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_default_options(self):
        arglist = [
            "--parent-port",
            self.new_trunk['port_id'],
            self.new_trunk['name'],
        ]
        verifylist = [
            ('parent_port', self.new_trunk['port_id']),
            ('name', self.new_trunk['name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_trunk.assert_called_once_with(
            **{
                'name': self.new_trunk['name'],
                'admin_state_up': self.new_trunk['admin_state_up'],
                'port_id': self.new_trunk['port_id'],
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_full_options(self):
        self.new_trunk['description'] = 'foo description'
        subport = self.new_trunk.sub_ports[0]
        arglist = [
            "--disable",
            "--description",
            self.new_trunk.description,
            "--parent-port",
            self.new_trunk.port_id,
            "--subport",
            'port={port},segmentation-type={seg_type},'
            'segmentation-id={seg_id}'.format(
                seg_id=subport['segmentation_id'],
                seg_type=subport['segmentation_type'],
                port=subport['port_id'],
            ),
            self.new_trunk.name,
        ]
        verifylist = [
            ('name', self.new_trunk.name),
            ('description', self.new_trunk.description),
            ('parent_port', self.new_trunk.port_id),
            (
                'add_subports',
                [
                    {
                        'port': subport['port_id'],
                        'segmentation-id': str(subport['segmentation_id']),
                        'segmentation-type': subport['segmentation_type'],
                    }
                ],
            ),
            ('disable', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_trunk.assert_called_once_with(
            **{
                'name': self.new_trunk.name,
                'description': self.new_trunk.description,
                'admin_state_up': False,
                'port_id': self.new_trunk.port_id,
                'sub_ports': [subport],
            }
        )
        self.assertEqual(self.columns, columns)
        data_with_desc = list(self.data)
        data_with_desc[0] = self.new_trunk['description']
        data_with_desc = tuple(data_with_desc)
        self.assertEqual(data_with_desc, data)

    def test_create_trunk_with_subport_invalid_segmentation_id_fail(self):
        subport = self.new_trunk.sub_ports[0]
        arglist = [
            "--parent-port",
            self.new_trunk.port_id,
            "--subport",
            "port={port},segmentation-type={seg_type},"
            "segmentation-id=boom".format(
                seg_type=subport['segmentation_type'],
                port=subport['port_id'],
            ),
            self.new_trunk.name,
        ]
        verifylist = [
            ('name', self.new_trunk.name),
            ('parent_port', self.new_trunk.port_id),
            (
                'add_subports',
                [
                    {
                        'port': subport['port_id'],
                        'segmentation-id': 'boom',
                        'segmentation-type': subport['segmentation_type'],
                    }
                ],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(
                "Segmentation-id 'boom' is not an integer", str(e)
            )

    def test_create_network_trunk_subports_without_optional_keys(self):
        subport = copy.copy(self.new_trunk.sub_ports[0])
        # Pop out the segmentation-id and segmentation-type
        subport.pop('segmentation_type')
        subport.pop('segmentation_id')
        arglist = [
            '--parent-port',
            self.new_trunk.port_id,
            '--subport',
            'port={port}'.format(port=subport['port_id']),
            self.new_trunk.name,
        ]
        verifylist = [
            ('name', self.new_trunk.name),
            ('parent_port', self.new_trunk.port_id),
            ('add_subports', [{'port': subport['port_id']}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_trunk.assert_called_once_with(
            **{
                'name': self.new_trunk.name,
                'admin_state_up': True,
                'port_id': self.new_trunk.port_id,
                'sub_ports': [subport],
            }
        )
        self.assertEqual(self.columns, columns)
        data_with_desc = list(self.data)
        data_with_desc[0] = self.new_trunk['description']
        data_with_desc = tuple(data_with_desc)
        self.assertEqual(data_with_desc, data)

    def test_create_network_trunk_subports_without_required_key_fail(self):
        subport = self.new_trunk.sub_ports[0]
        arglist = [
            '--parent-port',
            self.new_trunk.port_id,
            '--subport',
            'segmentation-type={seg_type},segmentation-id={seg_id}'.format(
                seg_id=subport['segmentation_id'],
                seg_type=subport['segmentation_type'],
            ),
            self.new_trunk.name,
        ]
        verifylist = [
            ('name', self.new_trunk.name),
            ('parent_port', self.new_trunk.port_id),
            (
                'add_subports',
                [
                    {
                        'segmentation_id': str(subport['segmentation_id']),
                        'segmentation_type': subport['segmentation_type'],
                    }
                ],
            ),
        ]

        with testtools.ExpectedException(test_utils.ParserException):
            self.check_parser(self.cmd, arglist, verifylist)


class TestDeleteNetworkTrunk(TestNetworkTrunk):
    # The trunk to be deleted.
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    trunk_networks = network_fakes.create_networks(count=2)
    parent_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[0]['id']}
    )
    sub_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[1]['id']}
    )

    new_trunks = network_fakes.create_trunks(
        attrs={
            'project_id': project.id,
            'port_id': parent_port['id'],
            'sub_ports': {
                'port_id': sub_port['id'],
                'segmentation_id': 42,
                'segmentation_type': 'vlan',
            },
        }
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_trunk = mock.Mock(
            side_effect=[self.new_trunks[0], self.new_trunks[1]]
        )
        self.network_client.delete_trunk = mock.Mock(return_value=None)
        self.network_client.find_port = mock.Mock(
            side_effect=[self.parent_port, self.sub_port]
        )

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = network_trunk.DeleteNetworkTrunk(self.app, None)

    def test_delete_trunkx(self):
        arglist = [
            self.new_trunks[0].name,
        ]
        verifylist = [
            ('trunk', [self.new_trunks[0].name]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.delete_trunk.assert_called_once_with(
            self.new_trunks[0].id
        )
        self.assertIsNone(result)

    def test_delete_trunk_multiple(self):
        arglist = []
        verifylist = []

        for t in self.new_trunks:
            arglist.append(t['name'])
        verifylist = [
            ('trunk', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for t in self.new_trunks:
            calls.append(call(t.id))
        self.network_client.delete_trunk.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_trunk_multiple_with_exception(self):
        arglist = [
            self.new_trunks[0].name,
            'unexist_trunk',
        ]
        verifylist = [
            ('trunk', [self.new_trunks[0].name, 'unexist_trunk']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.network_client.find_trunk = mock.Mock(
            side_effect=[self.new_trunks[0], exceptions.CommandError]
        )
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual('1 of 2 trunks failed to delete.', str(e))
        self.network_client.delete_trunk.assert_called_once_with(
            self.new_trunks[0].id
        )


class TestShowNetworkTrunk(TestNetworkTrunk):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # The trunk to set.
    new_trunk = network_fakes.create_one_trunk()
    columns = (
        'description',
        'id',
        'is_admin_state_up',
        'name',
        'port_id',
        'project_id',
        'status',
        'sub_ports',
        'tags',
    )
    data = (
        new_trunk.description,
        new_trunk.id,
        new_trunk.is_admin_state_up,
        new_trunk.name,
        new_trunk.port_id,
        new_trunk.project_id,
        new_trunk.status,
        format_columns.ListDictColumn(new_trunk.sub_ports),
        [],
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_trunk = mock.Mock(return_value=self.new_trunk)
        self.network_client.get_trunk = mock.Mock(return_value=self.new_trunk)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = network_trunk.ShowNetworkTrunk(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_show_all_options(self):
        arglist = [
            self.new_trunk.id,
        ]
        verifylist = [
            ('trunk', self.new_trunk.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.get_trunk.assert_called_once_with(
            self.new_trunk.id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestListNetworkTrunk(TestNetworkTrunk):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # Create trunks to be listed.
    new_trunks = network_fakes.create_trunks(
        {
            'created_at': '2001-01-01 00:00:00',
            'updated_at': '2001-01-01 00:00:00',
        },
        count=3,
    )

    columns = ('ID', 'Name', 'Parent Port', 'Description')
    columns_long = columns + ('Status', 'State', 'Created At', 'Updated At')
    data = []
    for t in new_trunks:
        data.append((t['id'], t['name'], t['port_id'], t['description']))
    data_long = []
    for t in new_trunks:
        data_long.append(
            (
                t['id'],
                t['name'],
                t['port_id'],
                t['description'],
                t['status'],
                network_trunk.AdminStateColumn(''),
                '2001-01-01 00:00:00',
                '2001-01-01 00:00:00',
            )
        )

    def setUp(self):
        super().setUp()
        self.network_client.trunks = mock.Mock(return_value=self.new_trunks)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = network_trunk.ListNetworkTrunk(self.app, None)

    def test_trunk_list_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.trunks.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_trunk_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.trunks.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestSetNetworkTrunk(TestNetworkTrunk):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    trunk_networks = network_fakes.create_networks(count=2)
    parent_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[0]['id']}
    )
    sub_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[1]['id']}
    )
    # Create trunks to be listed.
    _trunk = network_fakes.create_one_trunk(
        attrs={
            'project_id': project.id,
            'port_id': parent_port['id'],
            'sub_ports': {
                'port_id': sub_port['id'],
                'segmentation_id': 42,
                'segmentation_type': 'vlan',
            },
        }
    )
    columns = (
        'admin_state_up',
        'id',
        'name',
        'description',
        'port_id',
        'project_id',
        'status',
        'sub_ports',
    )
    data = (
        _trunk.id,
        _trunk.name,
        _trunk.description,
        _trunk.port_id,
        _trunk.project_id,
        _trunk.status,
        format_columns.ListDictColumn(_trunk.sub_ports),
    )

    def setUp(self):
        super().setUp()
        self.network_client.update_trunk = mock.Mock(return_value=self._trunk)
        self.network_client.add_trunk_subports = mock.Mock(
            return_value=self._trunk
        )
        self.network_client.find_trunk = mock.Mock(return_value=self._trunk)
        self.network_client.find_port = mock.Mock(
            side_effect=[self.sub_port, self.sub_port]
        )

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = network_trunk.SetNetworkTrunk(self.app, None)

    def _test_set_network_trunk_attr(self, attr, value):
        arglist = [
            f'--{attr}',
            value,
            self._trunk[attr],
        ]
        verifylist = [
            (attr, value),
            ('trunk', self._trunk[attr]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            attr: value,
        }
        self.network_client.update_trunk.assert_called_once_with(
            self._trunk, **attrs
        )
        self.assertIsNone(result)

    def test_set_network_trunk_name(self):
        self._test_set_network_trunk_attr('name', 'trunky')

    def test_set_network_trunk_description(self):
        self._test_set_network_trunk_attr('description', 'description')

    def test_set_network_trunk_admin_state_up_disable(self):
        arglist = [
            '--disable',
            self._trunk['name'],
        ]
        verifylist = [
            ('disable', True),
            ('trunk', self._trunk['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': False,
        }
        self.network_client.update_trunk.assert_called_once_with(
            self._trunk, **attrs
        )
        self.assertIsNone(result)

    def test_set_network_trunk_admin_state_up_enable(self):
        arglist = [
            '--enable',
            self._trunk['name'],
        ]
        verifylist = [
            ('enable', True),
            ('trunk', self._trunk['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'admin_state_up': True,
        }
        self.network_client.update_trunk.assert_called_once_with(
            self._trunk, **attrs
        )
        self.assertIsNone(result)

    def test_set_network_trunk_nothing(self):
        arglist = [
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network_client.update_trunk.assert_called_once_with(
            self._trunk, **attrs
        )
        self.assertIsNone(result)

    def test_set_network_trunk_subports(self):
        subport = self._trunk['sub_ports'][0]
        arglist = [
            '--subport',
            'port={port},segmentation-type={seg_type},'
            'segmentation-id={seg_id}'.format(
                seg_id=subport['segmentation_id'],
                seg_type=subport['segmentation_type'],
                port=subport['port_id'],
            ),
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
            (
                'set_subports',
                [
                    {
                        'port': subport['port_id'],
                        'segmentation-id': str(subport['segmentation_id']),
                        'segmentation-type': subport['segmentation_type'],
                    }
                ],
            ),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.add_trunk_subports.assert_called_once_with(
            self._trunk, [subport]
        )
        self.assertIsNone(result)

    def test_set_network_trunk_subports_without_optional_keys(self):
        subport = copy.copy(self._trunk['sub_ports'][0])
        # Pop out the segmentation-id and segmentation-type
        subport.pop('segmentation_type')
        subport.pop('segmentation_id')
        arglist = [
            '--subport',
            'port={port}'.format(port=subport['port_id']),
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
            ('set_subports', [{'port': subport['port_id']}]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.add_trunk_subports.assert_called_once_with(
            self._trunk, [subport]
        )
        self.assertIsNone(result)

    def test_set_network_trunk_subports_without_required_key_fail(self):
        subport = self._trunk['sub_ports'][0]
        arglist = [
            '--subport',
            'segmentation-type={seg_type},segmentation-id={seg_id}'.format(
                seg_id=subport['segmentation_id'],
                seg_type=subport['segmentation_type'],
            ),
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
            (
                'set_subports',
                [
                    {
                        'segmentation-id': str(subport['segmentation_id']),
                        'segmentation-type': subport['segmentation_type'],
                    }
                ],
            ),
        ]

        with testtools.ExpectedException(test_utils.ParserException):
            self.check_parser(self.cmd, arglist, verifylist)

        self.network_client.add_trunk_subports.assert_not_called()

    def test_set_trunk_attrs_with_exception(self):
        arglist = [
            '--name',
            'reallylongname',
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
            ('name', 'reallylongname'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.network_client.update_trunk = mock.Mock(
            side_effect=exceptions.CommandError
        )
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(
                "Failed to set trunk '{}': ".format(self._trunk['name']),
                str(e),
            )
        attrs = {'name': 'reallylongname'}
        self.network_client.update_trunk.assert_called_once_with(
            self._trunk, **attrs
        )
        self.network_client.add_trunk_subports.assert_not_called()

    def test_set_trunk_add_subport_with_exception(self):
        arglist = [
            '--subport',
            'port=invalid_subport',
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
            ('set_subports', [{'port': 'invalid_subport'}]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.network_client.add_trunk_subports = mock.Mock(
            side_effect=exceptions.CommandError
        )
        self.network_client.find_port = mock.Mock(
            return_value={'id': 'invalid_subport'}
        )
        with testtools.ExpectedException(exceptions.CommandError) as e:
            self.cmd.take_action(parsed_args)
            self.assertEqual(
                "Failed to add subports to trunk '{}': ".format(
                    self._trunk['name']
                ),
                str(e),
            )
        self.network_client.update_trunk.assert_called_once_with(self._trunk)
        self.network_client.add_trunk_subports.assert_called_once_with(
            self._trunk, [{'port_id': 'invalid_subport'}]
        )


class TestListNetworkSubport(TestNetworkTrunk):
    _trunk = network_fakes.create_one_trunk()
    _subports = _trunk['sub_ports']

    columns = (
        'Port',
        'Segmentation Type',
        'Segmentation ID',
    )
    data = []
    for s in _subports:
        data.append(
            (
                s['port_id'],
                s['segmentation_type'],
                s['segmentation_id'],
            )
        )

    def setUp(self):
        super().setUp()

        self.network_client.find_trunk = mock.Mock(return_value=self._trunk)
        self.network_client.get_trunk_subports = mock.Mock(
            return_value={network_trunk.SUB_PORTS: self._subports}
        )

        # Get the command object to test
        self.cmd = network_trunk.ListNetworkSubport(self.app, None)

    def test_subport_list(self):
        arglist = [
            '--trunk',
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.get_trunk_subports.assert_called_once_with(
            self._trunk
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestUnsetNetworkTrunk(TestNetworkTrunk):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    trunk_networks = network_fakes.create_networks(count=2)
    parent_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[0]['id']}
    )
    sub_port = network_fakes.create_one_port(
        attrs={'project_id': project.id, 'network_id': trunk_networks[1]['id']}
    )
    _trunk = network_fakes.create_one_trunk(
        attrs={
            'project_id': project.id,
            'port_id': parent_port['id'],
            'sub_ports': {
                'port_id': sub_port['id'],
                'segmentation_id': 42,
                'segmentation_type': 'vlan',
            },
        }
    )

    columns = (
        'admin_state_up',
        'id',
        'name',
        'port_id',
        'project_id',
        'status',
        'sub_ports',
    )
    data = (
        network_trunk.AdminStateColumn(_trunk['admin_state_up']),
        _trunk['id'],
        _trunk['name'],
        _trunk['port_id'],
        _trunk['project_id'],
        _trunk['status'],
        format_columns.ListDictColumn(_trunk['sub_ports']),
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_trunk = mock.Mock(return_value=self._trunk)
        self.network_client.find_port = mock.Mock(
            side_effect=[self.sub_port, self.sub_port]
        )
        self.network_client.delete_trunk_subports = mock.Mock(
            return_value=None
        )

        # Get the command object to test
        self.cmd = network_trunk.UnsetNetworkTrunk(self.app, None)

    def test_unset_network_trunk_subport(self):
        subport = self._trunk['sub_ports'][0]
        arglist = [
            "--subport",
            subport['port_id'],
            self._trunk['name'],
        ]

        verifylist = [
            ('trunk', self._trunk['name']),
            ('unset_subports', [subport['port_id']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_trunk_subports.assert_called_once_with(
            self._trunk, [{'port_id': subport['port_id']}]
        )
        self.assertIsNone(result)

    def test_unset_subport_no_arguments_fail(self):
        arglist = [
            self._trunk['name'],
        ]
        verifylist = [
            ('trunk', self._trunk['name']),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )
