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

from openstackclient.network.v2 import security_group
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestSecurityGroupNetwork(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity_client.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity_client.domains


class TestCreateSecurityGroupNetwork(TestSecurityGroupNetwork):
    project = identity_fakes.FakeProject.create_one_project()
    domain = identity_fakes.FakeDomain.create_one_domain()
    # The security group to be created.
    _security_group = (
        network_fakes.FakeSecurityGroup.create_one_security_group()
    )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
        'stateful',
        'tags',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.project_id,
        security_group.NetworkSecurityGroupRulesColumn([]),
        _security_group.stateful,
        _security_group.tags,
    )

    def setUp(self):
        super().setUp()

        self.network_client.create_security_group = mock.Mock(
            return_value=self._security_group
        )

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = security_group.CreateSecurityGroup(self.app, None)

    def test_create_no_options(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_create_min_options(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('name', self._security_group.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_security_group.assert_called_once_with(
            **{
                'description': self._security_group.name,
                'name': self._security_group.name,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description',
            self._security_group.description,
            '--project',
            self.project.name,
            '--project-domain',
            self.domain.name,
            '--stateful',
            self._security_group.name,
        ]
        verifylist = [
            ('description', self._security_group.description),
            ('name', self._security_group.name),
            ('project', self.project.name),
            ('project_domain', self.domain.name),
            ('stateful', self._security_group.stateful),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_security_group.assert_called_once_with(
            **{
                'description': self._security_group.description,
                'stateful': self._security_group.stateful,
                'name': self._security_group.name,
                'project_id': self.project.id,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def _test_create_with_tag(self, add_tags=True):
        arglist = [self._security_group.name]
        if add_tags:
            arglist += ['--tag', 'red', '--tag', 'blue']
        else:
            arglist += ['--no-tag']

        verifylist = [
            ('name', self._security_group.name),
        ]
        if add_tags:
            verifylist.append(('tags', ['red', 'blue']))
        else:
            verifylist.append(('no_tag', True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_security_group.assert_called_once_with(
            **{
                'description': self._security_group.name,
                'name': self._security_group.name,
            }
        )
        if add_tags:
            self.network_client.set_tags.assert_called_once_with(
                self._security_group, tests_utils.CompareBySet(['red', 'blue'])
            )
        else:
            self.assertFalse(self.network_client.set_tags.called)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_create_with_tags(self):
        self._test_create_with_tag(add_tags=True)

    def test_create_with_no_tag(self):
        self._test_create_with_tag(add_tags=False)


class TestDeleteSecurityGroupNetwork(TestSecurityGroupNetwork):
    # The security groups to be deleted.
    _security_groups = network_fakes.FakeSecurityGroup.create_security_groups()

    def setUp(self):
        super().setUp()

        self.network_client.delete_security_group = mock.Mock(
            return_value=None
        )

        self.network_client.find_security_group = (
            network_fakes.FakeSecurityGroup.get_security_groups(
                self._security_groups
            )
        )

        # Get the command object to test
        self.cmd = security_group.DeleteSecurityGroup(self.app, None)

    def test_security_group_delete(self):
        arglist = [
            self._security_groups[0].name,
        ]
        verifylist = [
            ('group', [self._security_groups[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_security_group.assert_called_once_with(
            self._security_groups[0]
        )
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
        self.network_client.delete_security_group.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_security_groups_delete_with_exception(self):
        arglist = [
            self._security_groups[0].name,
            'unexist_security_group',
        ]
        verifylist = [
            (
                'group',
                [self._security_groups[0].name, 'unexist_security_group'],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._security_groups[0], exceptions.CommandError]
        self.network_client.find_security_group = mock.Mock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 groups failed to delete.', str(e))

        self.network_client.find_security_group.assert_any_call(
            self._security_groups[0].name, ignore_missing=False
        )
        self.network_client.find_security_group.assert_any_call(
            'unexist_security_group', ignore_missing=False
        )
        self.network_client.delete_security_group.assert_called_once_with(
            self._security_groups[0]
        )


class TestListSecurityGroupNetwork(TestSecurityGroupNetwork):
    # The security group to be listed.
    _security_groups = network_fakes.FakeSecurityGroup.create_security_groups(
        count=3
    )

    columns = (
        'ID',
        'Name',
        'Description',
        'Project',
        'Tags',
    )

    data = []
    for grp in _security_groups:
        data.append(
            (
                grp.id,
                grp.name,
                grp.description,
                grp.project_id,
                grp.tags,
            )
        )

    def setUp(self):
        super().setUp()

        self.network_client.security_groups = mock.Mock(
            return_value=self._security_groups
        )

        # Get the command object to test
        self.cmd = security_group.ListSecurityGroup(self.app, None)

    def test_security_group_list_no_options(self):
        arglist = []
        verifylist = [
            ('all_projects', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.security_groups.assert_called_once_with(
            fields=security_group.ListSecurityGroup.FIELDS_TO_RETRIEVE
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_security_group_list_all_projects(self):
        arglist = [
            '--all-projects',
        ]
        verifylist = [
            ('all_projects', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.security_groups.assert_called_once_with(
            fields=security_group.ListSecurityGroup.FIELDS_TO_RETRIEVE
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_security_group_list_project(self):
        project = identity_fakes.FakeProject.create_one_project()
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
        filters = {
            'project_id': project.id,
            'fields': security_group.ListSecurityGroup.FIELDS_TO_RETRIEVE,
        }

        self.network_client.security_groups.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_security_group_list_project_domain(self):
        project = identity_fakes.FakeProject.create_one_project()
        self.projects_mock.get.return_value = project
        arglist = [
            '--project',
            project.id,
            '--project-domain',
            project.domain_id,
        ]
        verifylist = [
            ('project', project.id),
            ('project_domain', project.domain_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        filters = {
            'project_id': project.id,
            'fields': security_group.ListSecurityGroup.FIELDS_TO_RETRIEVE,
        }

        self.network_client.security_groups.assert_called_once_with(**filters)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

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

        self.network_client.security_groups.assert_called_once_with(
            **{
                'tags': 'red,blue',
                'any_tags': 'red,green',
                'not_tags': 'orange,yellow',
                'not_any_tags': 'black,white',
                'fields': security_group.ListSecurityGroup.FIELDS_TO_RETRIEVE,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetSecurityGroupNetwork(TestSecurityGroupNetwork):
    # The security group to be set.
    _security_group = (
        network_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'tags': ['green', 'red']}
        )
    )

    def setUp(self):
        super().setUp()

        self.network_client.update_security_group = mock.Mock(
            return_value=None
        )

        self.network_client.find_security_group = mock.Mock(
            return_value=self._security_group
        )
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = security_group.SetSecurityGroup(self.app, None)

    def test_set_no_options(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_set_no_updates(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_security_group.assert_called_once_with(
            self._security_group, **{}
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        new_name = 'new-' + self._security_group.name
        new_description = 'new-' + self._security_group.description
        arglist = [
            '--name',
            new_name,
            '--description',
            new_description,
            '--stateful',
            self._security_group.name,
        ]
        verifylist = [
            ('description', new_description),
            ('group', self._security_group.name),
            ('stateful', self._security_group.stateful),
            ('name', new_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'description': new_description,
            'name': new_name,
            'stateful': True,
        }
        self.network_client.update_security_group.assert_called_once_with(
            self._security_group, **attrs
        )
        self.assertIsNone(result)

    def _test_set_tags(self, with_tags=True):
        if with_tags:
            arglist = ['--tag', 'red', '--tag', 'blue']
            verifylist = [('tags', ['red', 'blue'])]
            expected_args = ['red', 'blue', 'green']
        else:
            arglist = ['--no-tag']
            verifylist = [('no_tag', True)]
            expected_args = []
        arglist.append(self._security_group.name)
        verifylist.append(('group', self._security_group.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertTrue(self.network_client.update_security_group.called)
        self.network_client.set_tags.assert_called_once_with(
            self._security_group, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_set_with_tags(self):
        self._test_set_tags(with_tags=True)

    def test_set_with_no_tag(self):
        self._test_set_tags(with_tags=False)


class TestShowSecurityGroupNetwork(TestSecurityGroupNetwork):
    # The security group rule to be shown with the group.
    _security_group_rule = (
        network_fakes.FakeSecurityGroupRule.create_one_security_group_rule()
    )

    # The security group to be shown.
    _security_group = (
        network_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'security_group_rules': [_security_group_rule._info]}
        )
    )

    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'rules',
        'stateful',
        'tags',
    )

    data = (
        _security_group.description,
        _security_group.id,
        _security_group.name,
        _security_group.project_id,
        security_group.NetworkSecurityGroupRulesColumn(
            [_security_group_rule._info]
        ),
        _security_group.stateful,
        _security_group.tags,
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_security_group = mock.Mock(
            return_value=self._security_group
        )

        # Get the command object to test
        self.cmd = security_group.ShowSecurityGroup(self.app, None)

    def test_show_no_options(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_show_all_options(self):
        arglist = [
            self._security_group.id,
        ]
        verifylist = [
            ('group', self._security_group.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_security_group.assert_called_once_with(
            self._security_group.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestUnsetSecurityGroupNetwork(TestSecurityGroupNetwork):
    # The security group to be unset.
    _security_group = (
        network_fakes.FakeSecurityGroup.create_one_security_group(
            attrs={'tags': ['green', 'red']}
        )
    )

    def setUp(self):
        super().setUp()

        self.network_client.update_security_group = mock.Mock(
            return_value=None
        )

        self.network_client.find_security_group = mock.Mock(
            return_value=self._security_group
        )
        self.network_client.set_tags = mock.Mock(return_value=None)

        # Get the command object to test
        self.cmd = security_group.UnsetSecurityGroup(self.app, None)

    def test_set_no_options(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_set_no_updates(self):
        arglist = [
            self._security_group.name,
        ]
        verifylist = [
            ('group', self._security_group.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_security_group.called)
        self.assertFalse(self.network_client.set_tags.called)
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
        arglist.append(self._security_group.name)
        verifylist.append(('group', self._security_group.name))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertFalse(self.network_client.update_security_group.called)
        self.network_client.set_tags.assert_called_once_with(
            self._security_group, tests_utils.CompareBySet(expected_args)
        )
        self.assertIsNone(result)

    def test_unset_with_tags(self):
        self._test_unset_tags(with_tags=True)

    def test_unset_with_all_tag(self):
        self._test_unset_tags(with_tags=False)
