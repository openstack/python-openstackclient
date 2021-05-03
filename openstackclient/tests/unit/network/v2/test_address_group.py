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

from openstackclient.network.v2 import address_group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestAddressGroup(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestAddressGroup, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateAddressGroup(TestAddressGroup):

    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # The new address group created.
    new_address_group = (
        network_fakes.FakeAddressGroup.create_one_address_group(
            attrs={
                'tenant_id': project.id,
            }
        ))
    columns = (
        'addresses',
        'description',
        'id',
        'name',
        'project_id',
    )
    data = (
        new_address_group.addresses,
        new_address_group.description,
        new_address_group.id,
        new_address_group.name,
        new_address_group.project_id,
    )

    def setUp(self):
        super(TestCreateAddressGroup, self).setUp()
        self.network.create_address_group = mock.Mock(
            return_value=self.new_address_group)

        # Get the command object to test
        self.cmd = address_group.CreateAddressGroup(self.app, self.namespace)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.new_address_group.name,
        ]
        verifylist = [
            ('project', None),
            ('name', self.new_address_group.name),
            ('description', None),
            ('address', []),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_address_group.assert_called_once_with(**{
            'name': self.new_address_group.name,
            'addresses': [],
        })
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--project', self.project.name,
            '--project-domain', self.domain.name,
            '--address', '10.0.0.1',
            '--description', self.new_address_group.description,
            self.new_address_group.name,
        ]
        verifylist = [
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('address', ['10.0.0.1']),
            ('description', self.new_address_group.description),
            ('name', self.new_address_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_address_group.assert_called_once_with(**{
            'addresses': ['10.0.0.1/32'],
            'tenant_id': self.project.id,
            'name': self.new_address_group.name,
            'description': self.new_address_group.description,
        })
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestDeleteAddressGroup(TestAddressGroup):

    # The address group to delete.
    _address_groups = (
        network_fakes.FakeAddressGroup.create_address_groups(count=2))

    def setUp(self):
        super(TestDeleteAddressGroup, self).setUp()
        self.network.delete_address_group = mock.Mock(return_value=None)
        self.network.find_address_group = (
            network_fakes.FakeAddressGroup.get_address_groups(
                address_groups=self._address_groups)
        )

        # Get the command object to test
        self.cmd = address_group.DeleteAddressGroup(self.app, self.namespace)

    def test_address_group_delete(self):
        arglist = [
            self._address_groups[0].name,
        ]
        verifylist = [
            ('address_group', [self._address_groups[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_address_group.assert_called_once_with(
            self._address_groups[0].name, ignore_missing=False)
        self.network.delete_address_group.assert_called_once_with(
            self._address_groups[0])
        self.assertIsNone(result)

    def test_multi_address_groups_delete(self):
        arglist = []

        for a in self._address_groups:
            arglist.append(a.name)
        verifylist = [
            ('address_group', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._address_groups:
            calls.append(call(a))
        self.network.delete_address_group.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_address_groups_delete_with_exception(self):
        arglist = [
            self._address_groups[0].name,
            'unexist_address_group',
        ]
        verifylist = [
            ('address_group',
             [self._address_groups[0].name, 'unexist_address_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._address_groups[0], exceptions.CommandError]
        self.network.find_address_group = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 address groups failed to delete.', str(e))

        self.network.find_address_group.assert_any_call(
            self._address_groups[0].name, ignore_missing=False)
        self.network.find_address_group.assert_any_call(
            'unexist_address_group', ignore_missing=False)
        self.network.delete_address_group.assert_called_once_with(
            self._address_groups[0]
        )


class TestListAddressGroup(TestAddressGroup):

    # The address groups to list up.
    address_groups = (
        network_fakes.FakeAddressGroup.create_address_groups(count=3))
    columns = (
        'ID',
        'Name',
        'Description',
        'Project',
        'Addresses',
    )
    data = []
    for group in address_groups:
        data.append((
            group.id,
            group.name,
            group.description,
            group.project_id,
            group.addresses,
        ))

    def setUp(self):
        super(TestListAddressGroup, self).setUp()
        self.network.address_groups = mock.Mock(
            return_value=self.address_groups)

        # Get the command object to test
        self.cmd = address_group.ListAddressGroup(self.app, self.namespace)

    def test_address_group_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_groups.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_address_group_list_name(self):
        arglist = [
            '--name', self.address_groups[0].name,
        ]
        verifylist = [
            ('name', self.address_groups[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_groups.assert_called_once_with(
            **{'name': self.address_groups[0].name})
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_address_group_list_project(self):
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

        self.network.address_groups.assert_called_once_with(
            project_id=project.id)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_address_group_project_domain(self):
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

        self.network.address_groups.assert_called_once_with(
            project_id=project.id)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))


class TestSetAddressGroup(TestAddressGroup):

    # The address group to set.
    _address_group = network_fakes.FakeAddressGroup.create_one_address_group()

    def setUp(self):
        super(TestSetAddressGroup, self).setUp()
        self.network.update_address_group = mock.Mock(return_value=None)
        self.network.find_address_group = mock.Mock(
            return_value=self._address_group)
        self.network.add_addresses_to_address_group = mock.Mock(
            return_value=self._address_group)
        # Get the command object to test
        self.cmd = address_group.SetAddressGroup(self.app, self.namespace)

    def test_set_nothing(self):
        arglist = [self._address_group.name, ]
        verifylist = [
            ('address_group', self._address_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.update_address_group.assert_not_called()
        self.network.add_addresses_to_address_group.assert_not_called()
        self.assertIsNone(result)

    def test_set_name_and_description(self):
        arglist = [
            '--name', 'new_address_group_name',
            '--description', 'new_address_group_description',
            self._address_group.name,
        ]
        verifylist = [
            ('name', 'new_address_group_name'),
            ('description', 'new_address_group_description'),
            ('address_group', self._address_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': "new_address_group_name",
            'description': 'new_address_group_description',
        }
        self.network.update_address_group.assert_called_with(
            self._address_group, **attrs)
        self.assertIsNone(result)

    def test_set_one_address(self):
        arglist = [
            self._address_group.name,
            '--address', '10.0.0.2',
        ]
        verifylist = [
            ('address_group', self._address_group.name),
            ('address', ['10.0.0.2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.add_addresses_to_address_group.assert_called_once_with(
            self._address_group, ['10.0.0.2/32'])
        self.assertIsNone(result)

    def test_set_multiple_addresses(self):
        arglist = [
            self._address_group.name,
            '--address', '10.0.0.2',
            '--address', '2001::/16',
        ]
        verifylist = [
            ('address_group', self._address_group.name),
            ('address', ['10.0.0.2', '2001::/16']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.add_addresses_to_address_group.assert_called_once_with(
            self._address_group, ['10.0.0.2/32', '2001::/16'])
        self.assertIsNone(result)


class TestShowAddressGroup(TestAddressGroup):

    # The address group to show.
    _address_group = network_fakes.FakeAddressGroup.create_one_address_group()
    columns = (
        'addresses',
        'description',
        'id',
        'name',
        'project_id',
    )
    data = (
        _address_group.addresses,
        _address_group.description,
        _address_group.id,
        _address_group.name,
        _address_group.project_id,
    )

    def setUp(self):
        super(TestShowAddressGroup, self).setUp()
        self.network.find_address_group = mock.Mock(
            return_value=self._address_group)

        # Get the command object to test
        self.cmd = address_group.ShowAddressGroup(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._address_group.name,
        ]
        verifylist = [
            ('address_group', self._address_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_address_group.assert_called_once_with(
            self._address_group.name, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))


class TestUnsetAddressGroup(TestAddressGroup):

    # The address group to unset.
    _address_group = network_fakes.FakeAddressGroup.create_one_address_group()

    def setUp(self):
        super(TestUnsetAddressGroup, self).setUp()
        self.network.find_address_group = mock.Mock(
            return_value=self._address_group)
        self.network.remove_addresses_from_address_group = mock.Mock(
            return_value=self._address_group)
        # Get the command object to test
        self.cmd = address_group.UnsetAddressGroup(self.app, self.namespace)

    def test_unset_nothing(self):
        arglist = [self._address_group.name, ]
        verifylist = [
            ('address_group', self._address_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.remove_addresses_from_address_group.assert_not_called()
        self.assertIsNone(result)

    def test_unset_one_address(self):
        arglist = [
            self._address_group.name,
            '--address', '10.0.0.2',
        ]
        verifylist = [
            ('address_group', self._address_group.name),
            ('address', ['10.0.0.2']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.remove_addresses_from_address_group.\
            assert_called_once_with(self._address_group, ['10.0.0.2/32'])
        self.assertIsNone(result)

    def test_unset_multiple_addresses(self):
        arglist = [
            self._address_group.name,
            '--address', '10.0.0.2',
            '--address', '2001::/16',
        ]
        verifylist = [
            ('address_group', self._address_group.name),
            ('address', ['10.0.0.2', '2001::/16']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.network.remove_addresses_from_address_group.\
            assert_called_once_with(self._address_group,
                                    ['10.0.0.2/32', '2001::/16'])
        self.assertIsNone(result)
