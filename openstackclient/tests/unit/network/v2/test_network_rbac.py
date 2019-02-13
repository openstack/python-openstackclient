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

from openstackclient.network.v2 import network_rbac
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkRBAC(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkRBAC, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects


class TestCreateNetworkRBAC(TestNetworkRBAC):

    network_object = network_fakes.FakeNetwork.create_one_network()
    qos_object = network_fakes.FakeNetworkQosPolicy.create_one_qos_policy()
    sg_object = network_fakes.FakeNetworkSecGroup.create_one_security_group()
    project = identity_fakes_v3.FakeProject.create_one_project()
    rbac_policy = network_fakes.FakeNetworkRBAC.create_one_network_rbac(
        attrs={'tenant_id': project.id,
               'target_tenant': project.id,
               'object_id': network_object.id}
    )

    columns = (
        'action',
        'id',
        'object_id',
        'object_type',
        'project_id',
        'target_project_id',
    )

    data = [
        rbac_policy.action,
        rbac_policy.id,
        rbac_policy.object_id,
        rbac_policy.object_type,
        rbac_policy.tenant_id,
        rbac_policy.target_tenant,
    ]

    def setUp(self):
        super(TestCreateNetworkRBAC, self).setUp()

        # Get the command object to test
        self.cmd = network_rbac.CreateNetworkRBAC(self.app, self.namespace)

        self.network.create_rbac_policy = mock.Mock(
            return_value=self.rbac_policy)
        self.network.find_network = mock.Mock(
            return_value=self.network_object)
        self.network.find_qos_policy = mock.Mock(
            return_value=self.qos_object)
        self.network.find_security_group = mock.Mock(
            return_value=self.sg_object)
        self.projects_mock.get.return_value = self.project

    def test_network_rbac_create_no_type(self):
        arglist = [
            '--action', self.rbac_policy.action,
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('action', self.rbac_policy.action),
            ('rbac_policy', self.rbac_policy.id),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_rbac_create_no_action(self):
        arglist = [
            '--type', self.rbac_policy.object_type,
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('type', self.rbac_policy.object_type),
            ('rbac_policy', self.rbac_policy.id),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_rbac_create_invalid_type(self):
        arglist = [
            '--action', self.rbac_policy.action,
            '--type', 'invalid_type',
            '--target-project', self.rbac_policy.target_tenant,
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('action', self.rbac_policy.action),
            ('type', 'invalid_type'),
            ('target-project', self.rbac_policy.target_tenant),
            ('rbac_policy', self.rbac_policy.id),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_rbac_create_invalid_action(self):
        arglist = [
            '--type', self.rbac_policy.object_type,
            '--action', 'invalid_action',
            '--target-project', self.rbac_policy.target_tenant,
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('type', self.rbac_policy.object_type),
            ('action', 'invalid_action'),
            ('target-project', self.rbac_policy.target_tenant),
            ('rbac_policy', self.rbac_policy.id),
        ]

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_rbac_create(self):
        arglist = [
            '--type', self.rbac_policy.object_type,
            '--action', self.rbac_policy.action,
            '--target-project', self.rbac_policy.target_tenant,
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('type', self.rbac_policy.object_type),
            ('action', self.rbac_policy.action),
            ('target_project', self.rbac_policy.target_tenant),
            ('rbac_object', self.rbac_policy.object_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_rbac_policy.assert_called_with(**{
            'object_id': self.rbac_policy.object_id,
            'object_type': self.rbac_policy.object_type,
            'action': self.rbac_policy.action,
            'target_tenant': self.rbac_policy.target_tenant,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_rbac_create_with_target_all_projects(self):
        arglist = [
            '--type', self.rbac_policy.object_type,
            '--action', self.rbac_policy.action,
            '--target-all-projects',
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('type', self.rbac_policy.object_type),
            ('action', self.rbac_policy.action),
            ('target_all_projects', True),
            ('rbac_object', self.rbac_policy.object_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_rbac_policy.assert_called_with(**{
            'object_id': self.rbac_policy.object_id,
            'object_type': self.rbac_policy.object_type,
            'action': self.rbac_policy.action,
            'target_tenant': '*',
        })

    def test_network_rbac_create_all_options(self):
        arglist = [
            '--type', self.rbac_policy.object_type,
            '--action', self.rbac_policy.action,
            '--target-project', self.rbac_policy.target_tenant,
            '--project', self.rbac_policy.tenant_id,
            '--project-domain', self.project.domain_id,
            '--target-project-domain', self.project.domain_id,
            self.rbac_policy.object_id,
        ]
        verifylist = [
            ('type', self.rbac_policy.object_type),
            ('action', self.rbac_policy.action),
            ('target_project', self.rbac_policy.target_tenant),
            ('project', self.rbac_policy.tenant_id),
            ('project_domain', self.project.domain_id),
            ('target_project_domain', self.project.domain_id),
            ('rbac_object', self.rbac_policy.object_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_rbac_policy.assert_called_with(**{
            'object_id': self.rbac_policy.object_id,
            'object_type': self.rbac_policy.object_type,
            'action': self.rbac_policy.action,
            'target_tenant': self.rbac_policy.target_tenant,
            'tenant_id': self.rbac_policy.tenant_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_rbac_create_qos_object(self):
        self.rbac_policy.object_type = 'qos_policy'
        self.rbac_policy.object_id = self.qos_object.id
        arglist = [
            '--type', 'qos_policy',
            '--action', self.rbac_policy.action,
            '--target-project', self.rbac_policy.target_tenant,
            self.qos_object.name,
        ]
        verifylist = [
            ('type', 'qos_policy'),
            ('action', self.rbac_policy.action),
            ('target_project', self.rbac_policy.target_tenant),
            ('rbac_object', self.qos_object.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_rbac_policy.assert_called_with(**{
            'object_id': self.qos_object.id,
            'object_type': 'qos_policy',
            'action': self.rbac_policy.action,
            'target_tenant': self.rbac_policy.target_tenant,
        })
        self.data = [
            self.rbac_policy.action,
            self.rbac_policy.id,
            self.qos_object.id,
            'qos_policy',
            self.rbac_policy.tenant_id,
            self.rbac_policy.target_tenant,
        ]
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_rbac_create_security_group_object(self):
        self.rbac_policy.object_type = 'security_group'
        self.rbac_policy.object_id = self.sg_object.id
        arglist = [
            '--type', 'security_group',
            '--action', self.rbac_policy.action,
            '--target-project', self.rbac_policy.target_tenant,
            self.sg_object.name,
        ]
        verifylist = [
            ('type', 'security_group'),
            ('action', self.rbac_policy.action),
            ('target_project', self.rbac_policy.target_tenant),
            ('rbac_object', self.sg_object.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_rbac_policy.assert_called_with(**{
            'object_id': self.sg_object.id,
            'object_type': 'security_group',
            'action': self.rbac_policy.action,
            'target_tenant': self.rbac_policy.target_tenant,
        })
        self.data = [
            self.rbac_policy.action,
            self.rbac_policy.id,
            self.sg_object.id,
            'security_group',
            self.rbac_policy.tenant_id,
            self.rbac_policy.target_tenant,
        ]
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestDeleteNetworkRBAC(TestNetworkRBAC):

    rbac_policies = network_fakes.FakeNetworkRBAC.create_network_rbacs(count=2)

    def setUp(self):
        super(TestDeleteNetworkRBAC, self).setUp()
        self.network.delete_rbac_policy = mock.Mock(return_value=None)
        self.network.find_rbac_policy = (
            network_fakes.FakeNetworkRBAC.get_network_rbacs(
                rbac_policies=self.rbac_policies)
        )

        # Get the command object to test
        self.cmd = network_rbac.DeleteNetworkRBAC(self.app, self.namespace)

    def test_network_rbac_delete(self):
        arglist = [
            self.rbac_policies[0].id,
        ]
        verifylist = [
            ('rbac_policy', [self.rbac_policies[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_rbac_policy.assert_called_once_with(
            self.rbac_policies[0].id, ignore_missing=False)
        self.network.delete_rbac_policy.assert_called_once_with(
            self.rbac_policies[0])
        self.assertIsNone(result)

    def test_multi_network_rbacs_delete(self):
        arglist = []
        verifylist = []

        for r in self.rbac_policies:
            arglist.append(r.id)
        verifylist = [
            ('rbac_policy', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for r in self.rbac_policies:
            calls.append(call(r))
        self.network.delete_rbac_policy.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_network_policies_delete_with_exception(self):
        arglist = [
            self.rbac_policies[0].id,
            'unexist_rbac_policy',
        ]
        verifylist = [
            ('rbac_policy',
             [self.rbac_policies[0].id, 'unexist_rbac_policy']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.rbac_policies[0], exceptions.CommandError]
        self.network.find_rbac_policy = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 RBAC policies failed to delete.', str(e))

        self.network.find_rbac_policy.assert_any_call(
            self.rbac_policies[0].id, ignore_missing=False)
        self.network.find_rbac_policy.assert_any_call(
            'unexist_rbac_policy', ignore_missing=False)
        self.network.delete_rbac_policy.assert_called_once_with(
            self.rbac_policies[0]
        )


class TestListNetworkRABC(TestNetworkRBAC):

    # The network rbac policies going to be listed up.
    rbac_policies = network_fakes.FakeNetworkRBAC.create_network_rbacs(count=3)

    columns = (
        'ID',
        'Object Type',
        'Object ID',
    )
    columns_long = (
        'ID',
        'Object Type',
        'Object ID',
        'Action',
    )
    data = []
    for r in rbac_policies:
        data.append((
            r.id,
            r.object_type,
            r.object_id,
        ))
    data_long = []
    for r in rbac_policies:
        data_long.append((
            r.id,
            r.object_type,
            r.object_id,
            r.action,
        ))

    def setUp(self):
        super(TestListNetworkRABC, self).setUp()

        # Get the command object to test
        self.cmd = network_rbac.ListNetworkRBAC(self.app, self.namespace)

        self.network.rbac_policies = mock.Mock(return_value=self.rbac_policies)

    def test_network_rbac_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.rbac_policies.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_rbac_list_type_opt(self):
        arglist = [
            '--type', self.rbac_policies[0].object_type, ]
        verifylist = [
            ('type', self.rbac_policies[0].object_type)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.rbac_policies.assert_called_with(**{
            'object_type': self.rbac_policies[0].object_type
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_rbac_list_action_opt(self):
        arglist = [
            '--action', self.rbac_policies[0].action, ]
        verifylist = [
            ('action', self.rbac_policies[0].action)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.rbac_policies.assert_called_with(**{
            'action': self.rbac_policies[0].action
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_rbac_list_with_long(self):
        arglist = [
            '--long',
        ]

        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.rbac_policies.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestSetNetworkRBAC(TestNetworkRBAC):

    project = identity_fakes_v3.FakeProject.create_one_project()
    rbac_policy = network_fakes.FakeNetworkRBAC.create_one_network_rbac(
        attrs={'target_tenant': project.id})

    def setUp(self):
        super(TestSetNetworkRBAC, self).setUp()

        # Get the command object to test
        self.cmd = network_rbac.SetNetworkRBAC(self.app, self.namespace)

        self.network.find_rbac_policy = mock.Mock(
            return_value=self.rbac_policy)
        self.network.update_rbac_policy = mock.Mock(return_value=None)
        self.projects_mock.get.return_value = self.project

    def test_network_rbac_set_nothing(self):
        arglist = [
            self.rbac_policy.id,
        ]
        verifylist = [
            ('rbac_policy', self.rbac_policy.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_rbac_policy.assert_called_once_with(
            self.rbac_policy.id, ignore_missing=False
        )
        attrs = {}
        self.network.update_rbac_policy.assert_called_once_with(
            self.rbac_policy, **attrs)
        self.assertIsNone(result)

    def test_network_rbac_set(self):
        arglist = [
            '--target-project', self.project.id,
            self.rbac_policy.id,
        ]
        verifylist = [
            ('target_project', self.project.id),
            ('rbac_policy', self.rbac_policy.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_rbac_policy.assert_called_once_with(
            self.rbac_policy.id, ignore_missing=False
        )
        attrs = {'target_tenant': self.project.id}
        self.network.update_rbac_policy.assert_called_once_with(
            self.rbac_policy, **attrs)
        self.assertIsNone(result)


class TestShowNetworkRBAC(TestNetworkRBAC):

    rbac_policy = network_fakes.FakeNetworkRBAC.create_one_network_rbac()

    columns = (
        'action',
        'id',
        'object_id',
        'object_type',
        'project_id',
        'target_project_id',
    )

    data = [
        rbac_policy.action,
        rbac_policy.id,
        rbac_policy.object_id,
        rbac_policy.object_type,
        rbac_policy.tenant_id,
        rbac_policy.target_tenant,
    ]

    def setUp(self):
        super(TestShowNetworkRBAC, self).setUp()

        # Get the command object to test
        self.cmd = network_rbac.ShowNetworkRBAC(self.app, self.namespace)

        self.network.find_rbac_policy = mock.Mock(
            return_value=self.rbac_policy)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_network_rbac_show_all_options(self):
        arglist = [
            self.rbac_policy.id,
        ]
        verifylist = [
            ('rbac_policy', self.rbac_policy.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_rbac_policy.assert_called_with(
            self.rbac_policy.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
