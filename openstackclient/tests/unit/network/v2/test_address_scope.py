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

from openstackclient.network.v2 import address_scope
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestAddressScope(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestAddressScope, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateAddressScope(TestAddressScope):

    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # The new address scope created.
    new_address_scope = (
        network_fakes.FakeAddressScope.create_one_address_scope(
            attrs={
                'tenant_id': project.id,
            }
        ))
    columns = (
        'id',
        'ip_version',
        'name',
        'project_id',
        'shared'
    )
    data = (
        new_address_scope.id,
        new_address_scope.ip_version,
        new_address_scope.name,
        new_address_scope.project_id,
        new_address_scope.shared,
    )

    def setUp(self):
        super(TestCreateAddressScope, self).setUp()
        self.network.create_address_scope = mock.Mock(
            return_value=self.new_address_scope)

        # Get the command object to test
        self.cmd = address_scope.CreateAddressScope(self.app, self.namespace)

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
            self.new_address_scope.name,
        ]
        verifylist = [
            ('project', None),
            ('ip_version', self.new_address_scope.ip_version),
            ('name', self.new_address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_address_scope.assert_called_once_with(**{
            'ip_version': self.new_address_scope.ip_version,
            'name': self.new_address_scope.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--ip-version', str(self.new_address_scope.ip_version),
            '--share',
            '--project', self.project.name,
            '--project-domain', self.domain.name,
            self.new_address_scope.name,
        ]
        verifylist = [
            ('ip_version', self.new_address_scope.ip_version),
            ('share', True),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('name', self.new_address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_address_scope.assert_called_once_with(**{
            'ip_version': self.new_address_scope.ip_version,
            'shared': True,
            'tenant_id': self.project.id,
            'name': self.new_address_scope.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_no_share(self):
        arglist = [
            '--no-share',
            self.new_address_scope.name,
        ]
        verifylist = [
            ('no_share', True),
            ('name', self.new_address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_address_scope.assert_called_once_with(**{
            'ip_version': self.new_address_scope.ip_version,
            'shared': False,
            'name': self.new_address_scope.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteAddressScope(TestAddressScope):

    # The address scope to delete.
    _address_scopes = (
        network_fakes.FakeAddressScope.create_address_scopes(count=2))

    def setUp(self):
        super(TestDeleteAddressScope, self).setUp()
        self.network.delete_address_scope = mock.Mock(return_value=None)
        self.network.find_address_scope = (
            network_fakes.FakeAddressScope.get_address_scopes(
                address_scopes=self._address_scopes)
        )

        # Get the command object to test
        self.cmd = address_scope.DeleteAddressScope(self.app, self.namespace)

    def test_address_scope_delete(self):
        arglist = [
            self._address_scopes[0].name,
        ]
        verifylist = [
            ('address_scope', [self._address_scopes[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_address_scope.assert_called_once_with(
            self._address_scopes[0].name, ignore_missing=False)
        self.network.delete_address_scope.assert_called_once_with(
            self._address_scopes[0])
        self.assertIsNone(result)

    def test_multi_address_scopes_delete(self):
        arglist = []
        verifylist = []

        for a in self._address_scopes:
            arglist.append(a.name)
        verifylist = [
            ('address_scope', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._address_scopes:
            calls.append(call(a))
        self.network.delete_address_scope.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_address_scopes_delete_with_exception(self):
        arglist = [
            self._address_scopes[0].name,
            'unexist_address_scope',
        ]
        verifylist = [
            ('address_scope',
             [self._address_scopes[0].name, 'unexist_address_scope']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._address_scopes[0], exceptions.CommandError]
        self.network.find_address_scope = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 address scopes failed to delete.', str(e))

        self.network.find_address_scope.assert_any_call(
            self._address_scopes[0].name, ignore_missing=False)
        self.network.find_address_scope.assert_any_call(
            'unexist_address_scope', ignore_missing=False)
        self.network.delete_address_scope.assert_called_once_with(
            self._address_scopes[0]
        )


class TestListAddressScope(TestAddressScope):

    # The address scopes to list up.
    address_scopes = (
        network_fakes.FakeAddressScope.create_address_scopes(count=3))
    columns = (
        'ID',
        'Name',
        'IP Version',
        'Shared',
        'Project',
    )
    data = []
    for scope in address_scopes:
        data.append((
            scope.id,
            scope.name,
            scope.ip_version,
            scope.shared,
            scope.project_id,
        ))

    def setUp(self):
        super(TestListAddressScope, self).setUp()
        self.network.address_scopes = mock.Mock(
            return_value=self.address_scopes)

        # Get the command object to test
        self.cmd = address_scope.ListAddressScope(self.app, self.namespace)

    def test_address_scope_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_scopes.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_address_scope_list_name(self):
        arglist = [
            '--name', self.address_scopes[0].name,
        ]
        verifylist = [
            ('name', self.address_scopes[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_scopes.assert_called_once_with(
            **{'name': self.address_scopes[0].name})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_address_scope_list_ip_version(self):
        arglist = [
            '--ip-version', str(4),
        ]
        verifylist = [
            ('ip_version', 4),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_scopes.assert_called_once_with(
            **{'ip_version': 4})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_address_scope_list_project(self):
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

        self.network.address_scopes.assert_called_once_with(
            **{'tenant_id': project.id, 'project_id': project.id})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_address_scope_project_domain(self):
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
        filters = {'tenant_id': project.id, 'project_id': project.id}

        self.network.address_scopes.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_address_scope_list_share(self):
        arglist = [
            '--share',
        ]
        verifylist = [
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_scopes.assert_called_once_with(
            **{'is_shared': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_address_scope_list_no_share(self):
        arglist = [
            '--no-share',
        ]
        verifylist = [
            ('no_share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.address_scopes.assert_called_once_with(
            **{'is_shared': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetAddressScope(TestAddressScope):

    # The address scope to set.
    _address_scope = network_fakes.FakeAddressScope.create_one_address_scope()

    def setUp(self):
        super(TestSetAddressScope, self).setUp()
        self.network.update_address_scope = mock.Mock(return_value=None)
        self.network.find_address_scope = mock.Mock(
            return_value=self._address_scope)

        # Get the command object to test
        self.cmd = address_scope.SetAddressScope(self.app, self.namespace)

    def test_set_nothing(self):
        arglist = [self._address_scope.name, ]
        verifylist = [
            ('address_scope', self._address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_address_scope.assert_called_with(
            self._address_scope, **attrs)
        self.assertIsNone(result)

    def test_set_name_and_share(self):
        arglist = [
            '--name', 'new_address_scope',
            '--share',
            self._address_scope.name,
        ]
        verifylist = [
            ('name', 'new_address_scope'),
            ('share', True),
            ('address_scope', self._address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': "new_address_scope",
            'shared': True,
        }
        self.network.update_address_scope.assert_called_with(
            self._address_scope, **attrs)
        self.assertIsNone(result)

    def test_set_no_share(self):
        arglist = [
            '--no-share',
            self._address_scope.name,
        ]
        verifylist = [
            ('no_share', True),
            ('address_scope', self._address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'shared': False,
        }
        self.network.update_address_scope.assert_called_with(
            self._address_scope, **attrs)
        self.assertIsNone(result)


class TestShowAddressScope(TestAddressScope):

    # The address scope to show.
    _address_scope = (
        network_fakes.FakeAddressScope.create_one_address_scope())
    columns = (
        'id',
        'ip_version',
        'name',
        'project_id',
        'shared',
    )
    data = (
        _address_scope.id,
        _address_scope.ip_version,
        _address_scope.name,
        _address_scope.project_id,
        _address_scope.shared,
    )

    def setUp(self):
        super(TestShowAddressScope, self).setUp()
        self.network.find_address_scope = mock.Mock(
            return_value=self._address_scope)

        # Get the command object to test
        self.cmd = address_scope.ShowAddressScope(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self._address_scope.name,
        ]
        verifylist = [
            ('address_scope', self._address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_address_scope.assert_called_once_with(
            self._address_scope.name, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))
