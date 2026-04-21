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

from unittest.mock import call

from openstack.identity.v3 import project as _project
from openstack.network.v2 import (
    security_groups_default_statefulness as _sg_default_statefulness,
)
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.network.v2 import security_groups_default_statefulness
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


def _generate_fake_setting(attrs=None):
    setting_attrs = {
        'project_id': None,
        'stateful': False,
        'location': 'MUNCHMUNCHMUNCH',
    }
    if attrs:
        setting_attrs.update(attrs)
    return sdk_fakes.generate_fake_resource(
        _sg_default_statefulness.SecurityGroupsDefaultStatefulness,
        **setting_attrs,
    )


class TestCreateSecurityGroupDefaultStatefulness(
    network_fakes.TestNetworkV2,
):
    expected_columns = (
        'id',
        'project_id',
        'stateful',
    )

    def setUp(self):
        super().setUp()
        self.cmd = security_groups_default_statefulness.CreateSecurityGroupDefaultStatefulness(
            self.app, None
        )

    def test_create_stateless_system_wide(self):
        setting = _generate_fake_setting({'stateful': False})
        self.network_client.create_security_groups_default_statefulness.return_value = setting
        arglist = ['--stateless']
        verifylist = [('stateful', False)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_security_groups_default_statefulness.assert_called_once_with(
            **{'stateful': False, 'project_id': None}
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(
            (setting.id, setting.project_id, setting.stateful), data
        )

    def test_create_stateful_system_wide(self):
        setting = _generate_fake_setting({'stateful': True})
        self.network_client.create_security_groups_default_statefulness.return_value = setting
        arglist = ['--stateful']
        verifylist = [('stateful', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_security_groups_default_statefulness.assert_called_once_with(
            **{'stateful': True, 'project_id': None}
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(
            (setting.id, setting.project_id, setting.stateful), data
        )

    def test_create_per_project(self):
        project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = project
        setting = _generate_fake_setting(
            {'stateful': False, 'project_id': project.id}
        )
        self.network_client.create_security_groups_default_statefulness.return_value = setting
        self.identity_client.projects.get.return_value = project
        arglist = ['--stateless', '--project', project.id]
        verifylist = [
            ('stateful', False),
            ('project', project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_security_groups_default_statefulness.assert_called_once_with(
            **{'stateful': False, 'project_id': project.id}
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(
            (setting.id, setting.project_id, setting.stateful), data
        )

    def test_create_no_statefulness_arg(self):
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            [],
            [],
        )


class TestDeleteSecurityGroupDefaultStatefulness(
    network_fakes.TestNetworkV2,
):
    def setUp(self):
        super().setUp()
        self.network_client.delete_security_groups_default_statefulness.return_value = None
        self.cmd = security_groups_default_statefulness.DeleteSecurityGroupDefaultStatefulness(
            self.app, None
        )
        self._settings = list(
            sdk_fakes.generate_fake_resources(
                _sg_default_statefulness.SecurityGroupsDefaultStatefulness,
                count=2,
                attrs={'stateful': False, 'location': 'MUNCHMUNCHMUNCH'},
            )
        )

    def test_delete_one(self):
        arglist = [self._settings[0].id]
        verifylist = [('setting', [self._settings[0].id])]
        self.network_client.find_security_groups_default_statefulness.return_value = self._settings[
            0
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_security_groups_default_statefulness.assert_called_once_with(
            self._settings[0]
        )
        self.assertIsNone(result)

    def test_delete_multi(self):
        arglist = [s.id for s in self._settings]
        verifylist = [('setting', arglist)]
        self.network_client.find_security_groups_default_statefulness.side_effect = self._settings
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = [call(s) for s in self._settings]
        self.network_client.delete_security_groups_default_statefulness.assert_has_calls(
            calls
        )
        self.assertIsNone(result)

    def test_delete_with_exception(self):
        arglist = [self._settings[0].id, 'nonexistent']
        verifylist = [
            ('setting', [self._settings[0].id, 'nonexistent']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [
            self._settings[0],
            exceptions.CommandError,
        ]
        self.network_client.find_security_groups_default_statefulness.side_effect = find_mock_result

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 default statefulness settings failed to delete.',
                str(e),
            )

        self.network_client.find_security_groups_default_statefulness.assert_any_call(
            self._settings[0].id, ignore_missing=False
        )
        self.network_client.find_security_groups_default_statefulness.assert_any_call(
            'nonexistent', ignore_missing=False
        )
        self.network_client.delete_security_groups_default_statefulness.assert_called_once_with(
            self._settings[0]
        )


class TestListSecurityGroupDefaultStatefulness(
    network_fakes.TestNetworkV2,
):
    def setUp(self):
        super().setUp()
        self._setting_system = _generate_fake_setting(
            {'stateful': False, 'project_id': None}
        )
        self._setting_project = _generate_fake_setting(
            {'stateful': True, 'project_id': 'project-id-1'}
        )
        self.expected_columns = (
            'ID',
            'Project ID',
            'Stateful',
        )
        self.expected_data = [
            (
                self._setting_system.id,
                self._setting_system.project_id,
                self._setting_system.stateful,
            ),
            (
                self._setting_project.id,
                self._setting_project.project_id,
                self._setting_project.stateful,
            ),
        ]
        self._settings = [self._setting_system, self._setting_project]
        self.network_client.security_groups_default_statefulness.return_value = self._settings
        self.cmd = security_groups_default_statefulness.ListSecurityGroupDefaultStatefulness(
            self.app, None
        )

    def test_list_all(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.security_groups_default_statefulness.assert_called_once_with()
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, list(data))


class TestSetSecurityGroupDefaultStatefulness(
    network_fakes.TestNetworkV2,
):
    def setUp(self):
        super().setUp()
        self._setting = _generate_fake_setting({'stateful': False})
        self.network_client.find_security_groups_default_statefulness.return_value = self._setting
        self.network_client.update_security_groups_default_statefulness.return_value = None
        self.cmd = security_groups_default_statefulness.SetSecurityGroupDefaultStatefulness(
            self.app, None
        )

    def test_set_stateful(self):
        arglist = [self._setting.id, '--stateful']
        verifylist = [
            ('setting', self._setting.id),
            ('stateful', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.update_security_groups_default_statefulness.assert_called_once_with(
            self._setting, **{'stateful': True}
        )
        self.assertIsNone(result)

    def test_set_stateless(self):
        arglist = [self._setting.id, '--stateless']
        verifylist = [
            ('setting', self._setting.id),
            ('stateful', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.update_security_groups_default_statefulness.assert_called_once_with(
            self._setting, **{'stateful': False}
        )
        self.assertIsNone(result)

    def test_set_no_statefulness_arg(self):
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            [self._setting.id],
            [],
        )


class TestShowSecurityGroupDefaultStatefulness(
    network_fakes.TestNetworkV2,
):
    expected_columns = (
        'id',
        'project_id',
        'stateful',
    )

    def setUp(self):
        super().setUp()
        self._setting = _generate_fake_setting()
        self.network_client.find_security_groups_default_statefulness.return_value = self._setting
        self.cmd = security_groups_default_statefulness.ShowSecurityGroupDefaultStatefulness(
            self.app, None
        )

    def test_show(self):
        arglist = [self._setting.id]
        verifylist = [('setting', self._setting.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_security_groups_default_statefulness.assert_called_once_with(
            self._setting.id, ignore_missing=False
        )
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(
            (
                self._setting.id,
                self._setting.project_id,
                self._setting.stateful,
            ),
            data,
        )
