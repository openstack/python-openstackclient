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

from openstackclient.network.v2 import security_group
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestSecurityGroupNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestSecurityGroupNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestSecurityGroupCompute(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestSecurityGroupCompute, self).setUp()

        # Get a shortcut to the compute client
        self.compute = self.app.client_manager.compute


class TestCreateSecurityGroupNetwork(TestSecurityGroupNetwork):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    # The security group to be created.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.project_id,
        '',
    )

    def setUp(self):
        super(TestCreateSecurityGroupNetwork, self).setUp()

        self.network.create_security_group = mock.Mock(
            return_value=self._security_group)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, self.namespace)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_min_options(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group.assert_called_once_with(**{
            'description': self._security_group.name,
            'name': self._security_group.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description', self._security_group.description,
            '--project', self.project.name,
            '--project-domain', self.domain.name,
            self._security_group.name,
        ]
        verifylist = [
            ('description', self._security_group.description),
            ('name', self._security_group.name),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_security_group.assert_called_once_with(**{
            'description': self._security_group.description,
            'name': self._security_group.name,
            'tenant_id': self.project.id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestCreateSecurityGroupCompute(TestSecurityGroupCompute):

    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    # The security group to be shown.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.tenant_id,
        '',
    )

    def setUp(self):
        super(TestCreateSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.create.return_value = self._security_group

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, None)

    def test_create_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_create_network_options(self):
        arglist = [
            '--project', self.project.name,
            '--project-domain', self.domain.name,
            self._security_group.name,
        ]
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, arglist, [])

    def test_create_min_options(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_groups.create.assert_called_once_with(
            self._security_group.name,
            self._security_group.name)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description', self._security_group.description,
            self._security_group.name,
        ]
        verifylist = [
            ('description', self._security_group.description),
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_groups.create.assert_called_once_with(
            self._security_group.name,
            self._security_group.description)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security groups to be deleted.
    _security_groups = \
        network_fakes.FakeSecurityGroup.create_security_groups()

    def setUp(self):
        super(TestDeleteSecurityGroupNetwork, self).setUp()

        self.network.delete_security_group = mock.Mock(return_value=None)

        self.network.find_security_group = (
            network_fakes.FakeSecurityGroup.get_security_groups(
                self._security_groups)
        )

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, self.namespace)

    def test_security_group_delete(self):
        arglist = [
            self._security_groups[0].name,
        ]
        verifylist = [
            ('group', [self._security_groups[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_security_group.assert_called_once_with(
            self._security_groups[0])
        self.assertIsNone(result)

    def test_multi_security_groups_delete(self):
        arglist = []
        verifylist = []

        for s in self._security_groups:
            arglist.append(s.name)
        verifylist = [
            ('group', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self._security_groups:
            calls.append(call(s))
        self.network.delete_security_group.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_security_groups_delete_with_exception(self):
        arglist = [
            self._security_groups[0].name,
            'unexist_security_group',
        ]
        verifylist = [
            ('group',
             [self._security_groups[0].name, 'unexist_security_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._security_groups[0], exceptions.CommandError]
        self.network.find_security_group = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 groups failed to delete.', str(e))

        self.network.find_security_group.assert_any_call(
            self._security_groups[0].name, ignore_missing=False)
        self.network.find_security_group.assert_any_call(
            'unexist_security_group', ignore_missing=False)
        self.network.delete_security_group.assert_called_once_with(
            self._security_groups[0]
        )


class TestDeleteSecurityGroupCompute(TestSecurityGroupCompute):

    # The security groups to be deleted.
    _security_groups = \
        compute_fakes.FakeSecurityGroup.create_security_groups()

    def setUp(self):
        super(TestDeleteSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.delete = mock.Mock(return_value=None)

        self.compute.security_groups.get = (
            compute_fakes.FakeSecurityGroup.get_security_groups(
                self._security_groups)
        )

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, None)

    def test_security_group_delete(self):
        arglist = [
            self._security_groups[0].id,
        ]
        verifylist = [
            ('group', [self._security_groups[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.delete.assert_called_once_with(
            self._security_groups[0].id)
        self.assertIsNone(result)

    def test_multi_security_groups_delete(self):
        arglist = []
        verifylist = []

        for s in self._security_groups:
            arglist.append(s.id)
        verifylist = [
            ('group', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for s in self._security_groups:
            calls.append(call(s.id))
        self.compute.security_groups.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_security_groups_delete_with_exception(self):
        arglist = [
            self._security_groups[0].id,
            'unexist_security_group',
        ]
        verifylist = [
            ('group',
             [self._security_groups[0].id, 'unexist_security_group']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._security_groups[0], exceptions.CommandError]
        self.compute.security_groups.get = (
            mock.Mock(side_effect=find_mock_result)
        )
        self.compute.security_groups.find.side_effect = (
            exceptions.NotFound(None))

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 groups failed to delete.', str(e))

        self.compute.security_groups.get.assert_any_call(
            self._security_groups[0].id)
        self.compute.security_groups.get.assert_any_call(
            'unexist_security_group')
        self.compute.security_groups.delete.assert_called_once_with(
            self._security_groups[0].id
        )


class TestListSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be listed.
    _security_groups = \
        network_fakes.FakeSecurityGroup.create_security_groups(count=3)

    columns = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    data = []
    for grp in _security_groups:
        data.append((
            grp.id,
            grp.name,
            grp.description,
            grp.tenant_id,
        ))

    def setUp(self):
        super(TestListSecurityGroupNetwork, self).setUp()

        self.network.security_groups = mock.Mock(
            return_value=self._security_groups)

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, self.namespace)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_groups.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.security_groups.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestListSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be listed.
    _security_groups = \
        compute_fakes.FakeSecurityGroup.create_security_groups(count=3)

    columns = (
        'ID',
        'Name',
        'Description',
    )
    columns_all_projects = (
        'ID',
        'Name',
        'Description',
        'Project',
    )

    data = []
    for grp in _security_groups:
        data.append((
            grp.id,
            grp.name,
            grp.description,
        ))
    data_all_projects = []
    for grp in _security_groups:
        data_all_projects.append((
            grp.id,
            grp.name,
            grp.description,
            grp.tenant_id,
        ))

    def setUp(self):
        super(TestListSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False
        self.compute.security_groups.list.return_value = self._security_groups

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, None)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': False}}
        self.compute.security_groups.list.assert_called_once_with(**kwargs)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {'search_opts': {'all_tenants': True}}
        self.compute.security_groups.list.assert_called_once_with(**kwargs)
        self.assertEqual(self.columns_all_projects, columns)
        self.assertEqual(self.data_all_projects, list(data))


class TestSetSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group to be set.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestSetSecurityGroupNetwork, self).setUp()

        self.network.update_security_group = mock.Mock(return_value=None)

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, self.namespace)

    def test_set_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_set_no_updates(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.update_security_group.assert_called_once_with(
            self._security_group,
            **{}
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        new_name = 'new-' + self._security_group.name
        new_description = 'new-' + self._security_group.description
        arglist = [
            '--name', new_name,
            '--description', new_description,
            self._security_group.name,
        ]
        verifylist = [
            ('description', new_description),
            ('group', self._security_group.name),
            ('name', new_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'description': new_description,
            'name': new_name,
        }
        self.network.update_security_group.assert_called_once_with(
            self._security_group,
            **attrs
        )
        self.assertIsNone(result)


class TestSetSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group to be set.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group()

    def setUp(self):
        super(TestSetSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.update = mock.Mock(return_value=None)

        self.compute.security_groups.get = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, None)

    def test_set_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_set_no_updates(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.update.assert_called_once_with(
            self._security_group,
            self._security_group.name,
            self._security_group.description
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        new_name = 'new-' + self._security_group.name
        new_description = 'new-' + self._security_group.description
        arglist = [
            '--name', new_name,
            '--description', new_description,
            self._security_group.name,
        ]
        verifylist = [
            ('description', new_description),
            ('group', self._security_group.name),
            ('name', new_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute.security_groups.update.assert_called_once_with(
            self._security_group,
            new_name,
            new_description
        )
        self.assertIsNone(result)


class TestShowSecurityGroupNetwork(TestSecurityGroupNetwork):

    # The security group rule to be shown with the group.
    _security_group_rule = \
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    # The security group to be shown.
    _security_group = \
        network_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'security_group_rules': [_security_group_rule._info]}
        )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.project_id,
        security_group._format_network_security_group_rules(
            [_security_group_rule._info]),
    )

    def setUp(self):
        super(TestShowSecurityGroupNetwork, self).setUp()

        self.network.find_security_group = mock.Mock(
            return_value=self._security_group)

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, self.namespace)

    def test_show_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_show_all_options(self):
        arglist = [
            self._security_group.id,
        ]
        verifylist = [
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_security_group.assert_called_once_with(
            self._security_group.id, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestShowSecurityGroupCompute(TestSecurityGroupCompute):

    # The security group rule to be shown with the group.
    _security_group_rule = \
        compute_fakes.FakeSecurityGroupRule.create_one_security_group_rule()

    # The security group to be shown.
    _security_group = \
        compute_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'rules': [_security_group_rule._info]}
        )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.tenant_id,
        security_group._format_compute_security_group_rules(
            [_security_group_rule._info]),
    )

    def setUp(self):
        super(TestShowSecurityGroupCompute, self).setUp()

        self.app.client_manager.network_endpoint_enabled = False

        self.compute.security_groups.get.return_value = self._security_group

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, None)

    def test_show_no_options(self):
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser, self.cmd, [], [])

    def test_show_all_options(self):
        arglist = [
            self._security_group.id,
        ]
        verifylist = [
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute.security_groups.get.assert_called_once_with(
            self._security_group.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
