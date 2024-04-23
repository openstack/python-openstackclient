# Copyright (c) 2016, Intel Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from unittest import mock
from unittest.mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import network_qos_policy
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestQosPolicy(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects


class TestCreateNetworkQosPolicy(TestQosPolicy):
    project = identity_fakes_v3.FakeProject.create_one_project()

    # The new qos policy created.
    new_qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy(
        attrs={
            'project_id': project.id,
        }
    )
    columns = (
        'description',
        'id',
        'is_default',
        'name',
        'project_id',
        'rules',
        'shared',
    )

    data = (
        new_qos_policy.description,
        new_qos_policy.id,
        new_qos_policy.is_default,
        new_qos_policy.name,
        new_qos_policy.project_id,
        new_qos_policy.rules,
        new_qos_policy.shared,
    )

    def setUp(self):
        super().setUp()
        self.network_client.create_qos_policy = mock.Mock(
            return_value=self.new_qos_policy
        )

        # Get the command object to test
        self.cmd = network_qos_policy.CreateNetworkQosPolicy(self.app, None)

        self.projects_mock.get.return_value = self.project

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

    def test_create_default_options(self):
        arglist = [
            self.new_qos_policy.name,
        ]
        verifylist = [
            ('project', None),
            ('name', self.new_qos_policy.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_policy.assert_called_once_with(
            **{'name': self.new_qos_policy.name}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--share',
            '--project',
            self.project.name,
            self.new_qos_policy.name,
            '--description',
            'QoS policy description',
            '--default',
        ]
        verifylist = [
            ('share', True),
            ('project', self.project.name),
            ('name', self.new_qos_policy.name),
            ('description', 'QoS policy description'),
            ('default', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_policy.assert_called_once_with(
            **{
                'shared': True,
                'project_id': self.project.id,
                'name': self.new_qos_policy.name,
                'description': 'QoS policy description',
                'is_default': True,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_no_default(self):
        arglist = [self.new_qos_policy.name, '--no-default']
        verifylist = [
            ('project', None),
            ('name', self.new_qos_policy.name),
            ('default', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_qos_policy.assert_called_once_with(
            **{
                'name': self.new_qos_policy.name,
                'is_default': False,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkQosPolicy(TestQosPolicy):
    # The address scope to delete.
    _qos_policies = network_fakes.FakeNetworkQosPolicy.create_qos_policies(
        count=2
    )

    def setUp(self):
        super().setUp()
        self.network_client.delete_qos_policy = mock.Mock(return_value=None)
        self.network_client.find_qos_policy = (
            network_fakes.FakeNetworkQosPolicy.get_qos_policies(
                qos_policies=self._qos_policies
            )
        )

        # Get the command object to test
        self.cmd = network_qos_policy.DeleteNetworkQosPolicy(self.app, None)

    def test_qos_policy_delete(self):
        arglist = [
            self._qos_policies[0].name,
        ]
        verifylist = [
            ('policy', [self._qos_policies[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.find_qos_policy.assert_called_once_with(
            self._qos_policies[0].name, ignore_missing=False
        )
        self.network_client.delete_qos_policy.assert_called_once_with(
            self._qos_policies[0]
        )
        self.assertIsNone(result)

    def test_multi_qos_policies_delete(self):
        arglist = []

        for a in self._qos_policies:
            arglist.append(a.name)
        verifylist = [
            ('policy', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._qos_policies:
            calls.append(call(a))
        self.network_client.delete_qos_policy.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_qos_policies_delete_with_exception(self):
        arglist = [
            self._qos_policies[0].name,
            'unexist_qos_policy',
        ]
        verifylist = [
            ('policy', [self._qos_policies[0].name, 'unexist_qos_policy']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._qos_policies[0], exceptions.CommandError]
        self.network_client.find_qos_policy = mock.MagicMock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 QoS policies failed to delete.', str(e))

        self.network_client.find_qos_policy.assert_any_call(
            self._qos_policies[0].name, ignore_missing=False
        )
        self.network_client.find_qos_policy.assert_any_call(
            'unexist_qos_policy', ignore_missing=False
        )
        self.network_client.delete_qos_policy.assert_called_once_with(
            self._qos_policies[0]
        )


class TestListNetworkQosPolicy(TestQosPolicy):
    # The QoS policies to list up.
    qos_policies = network_fakes.FakeNetworkQosPolicy.create_qos_policies(
        count=3
    )
    columns = (
        'ID',
        'Name',
        'Shared',
        'Default',
        'Project',
    )
    data = []
    for qos_policy in qos_policies:
        data.append(
            (
                qos_policy.id,
                qos_policy.name,
                qos_policy.shared,
                qos_policy.is_default,
                qos_policy.project_id,
            )
        )

    def setUp(self):
        super().setUp()
        self.network_client.qos_policies = mock.Mock(
            return_value=self.qos_policies
        )

        # Get the command object to test
        self.cmd = network_qos_policy.ListNetworkQosPolicy(self.app, None)

    def test_qos_policy_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.qos_policies.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_qos_policy_list_share(self):
        arglist = [
            '--share',
        ]
        verifylist = [
            ('share', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.qos_policies.assert_called_once_with(
            **{'shared': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_qos_policy_list_no_share(self):
        arglist = [
            '--no-share',
        ]
        verifylist = [
            ('no_share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.qos_policies.assert_called_once_with(
            **{'shared': False}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_qos_list_project(self):
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
        self.network_client.qos_policies.assert_called_once_with(
            **{'project_id': project.id}
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetNetworkQosPolicy(TestQosPolicy):
    # The QoS policy to set.
    _qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()

    def setUp(self):
        super().setUp()
        self.network_client.update_qos_policy = mock.Mock(return_value=None)
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self._qos_policy
        )

        # Get the command object to test
        self.cmd = network_qos_policy.SetNetworkQosPolicy(self.app, None)

    def test_set_nothing(self):
        arglist = [
            self._qos_policy.name,
        ]
        verifylist = [
            ('policy', self._qos_policy.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network_client.update_qos_policy.assert_called_with(
            self._qos_policy, **attrs
        )
        self.assertIsNone(result)

    def test_set_name_share_description_default(self):
        arglist = [
            '--name',
            'new_qos_policy',
            '--share',
            '--description',
            'QoS policy description',
            '--default',
            self._qos_policy.name,
        ]
        verifylist = [
            ('name', 'new_qos_policy'),
            ('share', True),
            ('description', 'QoS policy description'),
            ('default', True),
            ('policy', self._qos_policy.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': 'new_qos_policy',
            'description': 'QoS policy description',
            'shared': True,
            'is_default': True,
        }
        self.network_client.update_qos_policy.assert_called_with(
            self._qos_policy, **attrs
        )
        self.assertIsNone(result)

    def test_set_no_share_no_default(self):
        arglist = [
            '--no-share',
            '--no-default',
            self._qos_policy.name,
        ]
        verifylist = [
            ('no_share', True),
            ('no_default', True),
            ('policy', self._qos_policy.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {'shared': False, 'is_default': False}
        self.network_client.update_qos_policy.assert_called_with(
            self._qos_policy, **attrs
        )
        self.assertIsNone(result)


class TestShowNetworkQosPolicy(TestQosPolicy):
    # The QoS policy to show.
    _qos_policy = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
    columns = (
        'description',
        'id',
        'is_default',
        'name',
        'project_id',
        'rules',
        'shared',
    )
    data = (
        _qos_policy.description,
        _qos_policy.id,
        _qos_policy.is_default,
        _qos_policy.name,
        _qos_policy.project_id,
        network_qos_policy.RulesColumn(_qos_policy.rules),
        _qos_policy.shared,
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_qos_policy = mock.Mock(
            return_value=self._qos_policy
        )

        # Get the command object to test
        self.cmd = network_qos_policy.ShowNetworkQosPolicy(self.app, None)

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
            self._qos_policy.name,
        ]
        verifylist = [
            ('policy', self._qos_policy.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_qos_policy.assert_called_once_with(
            self._qos_policy.name, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(list(self.data), list(data))
