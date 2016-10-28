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

import mock

from openstackclient.network.v2 import network_auto_allocated_topology
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestAutoAllocatedTopology(network_fakes.TestNetworkV2):
    def setUp(self):
        super(TestAutoAllocatedTopology, self).setUp()
        self.network = self.app.client_manager.network
        self.projects_mock = self.app.client_manager.identity.projects


class TestCreateAutoAllocatedTopology(TestAutoAllocatedTopology):
    project = identity_fakes.FakeProject.create_one_project()
    network_object = network_fakes.FakeNetwork.create_one_network()

    topology = network_fakes.FakeAutoAllocatedTopology.create_one_topology(
        attrs={'id': network_object.id,
               'tenant_id': project.id}
    )

    columns = (
        'id',
        'project_id',
    )

    data = (
        network_object.id,
        project.id,
    )

    def setUp(self):
        super(TestCreateAutoAllocatedTopology, self).setUp()

        self.cmd = network_auto_allocated_topology.CreateAutoAllocatedTopology(
            self.app,
            self.namespace)
        self.network.get_auto_allocated_topology = mock.Mock(
            return_value=self.topology)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network.get_auto_allocated_topology.assert_called_with(None)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_project_option(self):
        arglist = [
            '--project', self.project.id,
        ]

        verifylist = [
            ('project', self.project.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network.get_auto_allocated_topology.assert_called_with(
            self.project.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_project_domain_option(self):
        arglist = [
            '--project', self.project.id,
            '--project-domain', self.project.domain_id,
        ]

        verifylist = [
            ('project', self.project.id),
            ('project_domain', self.project.domain_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network.get_auto_allocated_topology.assert_called_with(
            self.project.id
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_or_show_option(self):
        arglist = [
            '--or-show',
        ]

        verifylist = [
            ('or_show', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.network.get_auto_allocated_topology.assert_called_with(None)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestValidateAutoAllocatedTopology(TestAutoAllocatedTopology):
    project = identity_fakes.FakeProject.create_one_project()
    network_object = network_fakes.FakeNetwork.create_one_network()

    topology = network_fakes.FakeAutoAllocatedTopology.create_one_topology(
        attrs={'id': network_object.id,
               'tenant_id': project.id}
    )

    columns = (
        'id',
        'project_id',
    )

    data = (
        network_object.id,
        project.id,
    )

    def setUp(self):
        super(TestValidateAutoAllocatedTopology, self).setUp()

        self.cmd = network_auto_allocated_topology.CreateAutoAllocatedTopology(
            self.app,
            self.namespace)
        self.network.validate_auto_allocated_topology = mock.Mock(
            return_value=self.topology)

    def test_show_dry_run_no_project(self):
        arglist = [
            '--check-resources',
        ]
        verifylist = [
            ('check_resources', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.validate_auto_allocated_topology.assert_called_with(
            None)

    def test_show_dry_run_project_option(self):
        arglist = [
            '--check-resources',
            '--project', self.project.id,
        ]
        verifylist = [
            ('check_resources', True),
            ('project', self.project.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.validate_auto_allocated_topology.assert_called_with(
            self.project.id)

    def test_show_dry_run_project_domain_option(self):
        arglist = [
            '--check-resources',
            '--project', self.project.id,
            '--project-domain', self.project.domain_id,
        ]
        verifylist = [
            ('check_resources', True),
            ('project', self.project.id),
            ('project_domain', self.project.domain_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.validate_auto_allocated_topology.assert_called_with(
            self.project.id)


class TestDeleteAutoAllocatedTopology(TestAutoAllocatedTopology):
    project = identity_fakes.FakeProject.create_one_project()
    network_object = network_fakes.FakeNetwork.create_one_network()

    topology = network_fakes.FakeAutoAllocatedTopology.create_one_topology(
        attrs={'id': network_object.id,
               'tenant_id': project.id}
    )

    def setUp(self):
        super(TestDeleteAutoAllocatedTopology, self).setUp()

        self.cmd = network_auto_allocated_topology.DeleteAutoAllocatedTopology(
            self.app,
            self.namespace)
        self.network.delete_auto_allocated_topology = mock.Mock(
            return_value=None)

    def test_delete_no_project(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_auto_allocated_topology.assert_called_once_with(
            None)

        self.assertIsNone(result)

    def test_delete_project_arg(self):
        arglist = [
            '--project', self.project.id,
        ]
        verifylist = [
            ('project', self.project.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_auto_allocated_topology.assert_called_once_with(
            self.project.id)

        self.assertIsNone(result)

    def test_delete_project_domain_arg(self):
        arglist = [
            '--project', self.project.id,
            '--project-domain', self.project.domain_id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('project_domain', self.project.domain_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_auto_allocated_topology.assert_called_once_with(
            self.project.id)

        self.assertIsNone(result)
