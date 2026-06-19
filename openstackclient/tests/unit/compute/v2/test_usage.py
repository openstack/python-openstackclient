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

import datetime
from unittest import mock

from openstack.compute.v2 import usage as _usage
from openstack.identity.v3 import project as _project
from openstack.test import fakes as sdk_fakes

from openstackclient.compute.v2 import usage as usage_cmds
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestUsageList(compute_fakes.TestCompute):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.projects.return_value = [self.project]

        self.usages = [
            sdk_fakes.generate_fake_resource(
                _usage.Usage, project_id=self.project.name
            )
        ]
        self.columns = (
            "Project",
            "Servers",
            "RAM MB-Hours",
            "CPU Hours",
            "Disk GB-Hours",
        )
        self.data = [
            (
                usage_cmds.ProjectColumn(self.usages[0].project_id),
                usage_cmds.CountColumn(self.usages[0].server_usages),
                usage_cmds.FloatColumn(self.usages[0].total_memory_mb_usage),
                usage_cmds.FloatColumn(self.usages[0].total_vcpus_usage),
                usage_cmds.FloatColumn(self.usages[0].total_local_gb_usage),
            )
        ]

        self.compute_client.usages.return_value = self.usages

        # Get the command object to test
        self.cmd = usage_cmds.ListUsage(self.app, None)

    def test_usage_list_no_options(self):
        arglist = []
        verifylist = [
            ('start', None),
            ('end', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.projects.assert_called_once()

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), tuple(data))

    def test_usage_list_with_options(self):
        arglist = [
            '--start',
            '2016-11-11',
            '--end',
            '2016-12-20',
        ]
        verifylist = [
            ('start', '2016-11-11'),
            ('end', '2016-12-20'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.projects.assert_called_once()
        self.compute_client.usages.assert_called_with(
            start=datetime.datetime(2016, 11, 11, 0, 0),
            end=datetime.datetime(2016, 12, 20, 0, 0),
            detailed=True,
        )

        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), tuple(data))

    def test_usage_list_with_pagination(self):
        arglist = []
        verifylist = [
            ('start', None),
            ('end', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.identity_sdk_client.projects.assert_called_once()
        self.compute_client.usages.assert_has_calls(
            [mock.call(start=mock.ANY, end=mock.ANY, detailed=True)]
        )
        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), tuple(data))


class TestUsageShow(compute_fakes.TestCompute):
    # Return value of self.usage_mock.list().
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.usage = sdk_fakes.generate_fake_resource(
            _usage.Usage, project_id=self.project.name
        )
        self.compute_client.get_usage.return_value = self.usage

        self.columns = (
            'Project',
            'Servers',
            'RAM MB-Hours',
            'CPU Hours',
            'Disk GB-Hours',
        )
        self.data = (
            usage_cmds.ProjectColumn(self.usage.project_id),
            usage_cmds.CountColumn(self.usage.server_usages),
            usage_cmds.FloatColumn(self.usage.total_memory_mb_usage),
            usage_cmds.FloatColumn(self.usage.total_vcpus_usage),
            usage_cmds.FloatColumn(self.usage.total_local_gb_usage),
        )

        # Get the command object to test
        self.cmd = usage_cmds.ShowUsage(self.app, None)

    def test_usage_show_no_options(self):
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.project_id = self.project.id

        arglist = []
        verifylist = [
            ('project', None),
            ('start', None),
            ('end', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_usage_show_with_options(self):
        arglist = [
            '--project',
            self.project.id,
            '--start',
            '2016-11-11',
            '--end',
            '2016-12-20',
        ]
        verifylist = [
            ('project', self.project.id),
            ('start', '2016-11-11'),
            ('end', '2016-12-20'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.get_usage.assert_called_with(
            project=self.project.id,
            start=datetime.datetime(2016, 11, 11, 0, 0),
            end=datetime.datetime(2016, 12, 20, 0, 0),
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
