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

import mock
from novaclient import api_versions

from openstackclient.compute.v2 import usage
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestUsage(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestUsage, self).setUp()

        self.usage_mock = self.app.client_manager.compute.usage
        self.usage_mock.reset_mock()

        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestUsageList(TestUsage):

    project = identity_fakes.FakeProject.create_one_project()
    # Return value of self.usage_mock.list().
    usages = compute_fakes.FakeUsage.create_usages(
        attrs={'tenant_id': project.name}, count=1)

    columns = (
        "Project",
        "Servers",
        "RAM MB-Hours",
        "CPU Hours",
        "Disk GB-Hours"
    )

    data = [(
        usages[0].tenant_id,
        len(usages[0].server_usages),
        float("%.2f" % usages[0].total_memory_mb_usage),
        float("%.2f" % usages[0].total_vcpus_usage),
        float("%.2f" % usages[0].total_local_gb_usage),
    )]

    def setUp(self):
        super(TestUsageList, self).setUp()

        self.usage_mock.list.return_value = self.usages

        self.projects_mock.list.return_value = [self.project]
        # Get the command object to test
        self.cmd = usage.ListUsage(self.app, None)

    def test_usage_list_no_options(self):

        arglist = []
        verifylist = [
            ('start', None),
            ('end', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.projects_mock.list.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_usage_list_with_options(self):
        arglist = [
            '--start', '2016-11-11',
            '--end', '2016-12-20',
        ]
        verifylist = [
            ('start', '2016-11-11'),
            ('end', '2016-12-20'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.projects_mock.list.assert_called_with()
        self.usage_mock.list.assert_called_with(
            datetime.datetime(2016, 11, 11, 0, 0),
            datetime.datetime(2016, 12, 20, 0, 0),
            detailed=True)

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_usage_list_with_pagination(self):
        arglist = []
        verifylist = [
            ('start', None),
            ('end', None),
        ]

        self.app.client_manager.compute.api_version = api_versions.APIVersion(
            '2.40')
        self.usage_mock.list.reset_mock()
        self.usage_mock.list.side_effect = [self.usages, []]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.projects_mock.list.assert_called_with()
        self.usage_mock.list.assert_has_calls([
            mock.call(mock.ANY, mock.ANY, detailed=True),
            mock.call(mock.ANY, mock.ANY, detailed=True,
                      marker=self.usages[0]['server_usages'][0]['instance_id'])
        ])
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestUsageShow(TestUsage):

    project = identity_fakes.FakeProject.create_one_project()
    # Return value of self.usage_mock.list().
    usage = compute_fakes.FakeUsage.create_one_usage(
        attrs={'tenant_id': project.name})

    columns = (
        'CPU Hours',
        'Disk GB-Hours',
        'RAM MB-Hours',
        'Servers',
    )

    data = (
        float("%.2f" % usage.total_vcpus_usage),
        float("%.2f" % usage.total_local_gb_usage),
        float("%.2f" % usage.total_memory_mb_usage),
        len(usage.server_usages),
    )

    def setUp(self):
        super(TestUsageShow, self).setUp()

        self.usage_mock.get.return_value = self.usage

        self.projects_mock.get.return_value = self.project
        # Get the command object to test
        self.cmd = usage.ShowUsage(self.app, None)

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
            '--project', self.project.id,
            '--start', '2016-11-11',
            '--end', '2016-12-20',
        ]
        verifylist = [
            ('project', self.project.id),
            ('start', '2016-11-11'),
            ('end', '2016-12-20'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.usage_mock.get.assert_called_with(
            self.project.id,
            datetime.datetime(2016, 11, 11, 0, 0),
            datetime.datetime(2016, 12, 20, 0, 0))

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
