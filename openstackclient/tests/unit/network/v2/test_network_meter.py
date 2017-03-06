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
from mock import call

from osc_lib import exceptions

from openstackclient.network.v2 import network_meter
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestMeter(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestMeter, self).setUp()
        self.network = self.app.client_manager.network
        self.projects_mock = self.app.client_manager.identity.projects
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateMeter(TestMeter):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()

    new_meter = (
        network_fakes.FakeNetworkMeter.
        create_one_meter()
    )
    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'shared',
    )

    data = (
        new_meter.description,
        new_meter.id,
        new_meter.name,
        new_meter.project_id,
        new_meter.shared,
    )

    def setUp(self):
        super(TestCreateMeter, self).setUp()
        self.network.create_metering_label = mock.Mock(
            return_value=self.new_meter)
        self.projects_mock.get.return_value = self.project
        self.cmd = network_meter.CreateMeter(self.app, self.namespace)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.new_meter.name,
        ]

        verifylist = [
            ('name', self.new_meter.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_metering_label.assert_called_once_with(
            **{'name': self.new_meter.name}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            "--description", self.new_meter.description,
            "--project", self.new_meter.project_id,
            "--project-domain", self.domain.name,
            "--share",
            self.new_meter.name,
        ]

        verifylist = [
            ('description', self.new_meter.description),
            ('name', self.new_meter.name),
            ('project', self.new_meter.project_id),
            ('project_domain', self.domain.name),
            ('share', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_metering_label.assert_called_once_with(
            **{'description': self.new_meter.description,
               'name': self.new_meter.name,
               'tenant_id': self.project.id,
               'shared': True, }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteMeter(TestMeter):

    def setUp(self):
        super(TestDeleteMeter, self).setUp()

        self.meter_list = \
            network_fakes.FakeNetworkMeter.create_meter(count=2)

        self.network.delete_metering_label = mock.Mock(return_value=None)

        self.network.find_metering_label = network_fakes \
            .FakeNetworkMeter.get_meter(
                meter=self.meter_list
            )

        self.cmd = network_meter.DeleteMeter(self.app, self.namespace)

    def test_delete_one_meter(self):
        arglist = [
            self.meter_list[0].name,
        ]
        verifylist = [
            ('meter', [self.meter_list[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_metering_label.assert_called_once_with(
            self.meter_list[0]
        )
        self.assertIsNone(result)

    def test_delete_multiple_meters(self):
        arglist = []
        for n in self.meter_list:
            arglist.append(n.id)
        verifylist = [
            ('meter', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for n in self.meter_list:
            calls.append(call(n))
        self.network.delete_metering_label.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_meter_exception(self):
        arglist = [
            self.meter_list[0].id,
            'xxxx-yyyy-zzzz',
            self.meter_list[1].id,
        ]
        verifylist = [
            ('meter', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        return_find = [
            self.meter_list[0],
            exceptions.NotFound('404'),
            self.meter_list[1],
        ]
        self.network.find_meter = mock.Mock(side_effect=return_find)

        ret_delete = [
            None,
            exceptions.NotFound('404'),
        ]
        self.network.delete_metering_label = mock.Mock(side_effect=ret_delete)

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        calls = [
            call(self.meter_list[0]),
            call(self.meter_list[1]),
        ]
        self.network.delete_metering_label.assert_has_calls(calls)


class TestListMeter(TestMeter):

    meter_list = \
        network_fakes.FakeNetworkMeter.create_meter(count=2)

    columns = (
        'ID',
        'Name',
        'Description',
        'Shared',
    )

    data = []

    for meters in meter_list:
        data.append((
            meters.id,
            meters.name,
            meters.description,
            meters.shared,
        ))

    def setUp(self):
        super(TestListMeter, self).setUp()

        self.network.metering_labels = mock.Mock(
            return_value=self.meter_list
        )

        self.cmd = network_meter.ListMeter(self.app, self.namespace)

    def test_meter_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.metering_labels.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowMeter(TestMeter):
    new_meter = (
        network_fakes.FakeNetworkMeter.
        create_one_meter()
    )
    columns = (
        'description',
        'id',
        'name',
        'project_id',
        'shared',
    )

    data = (
        new_meter.description,
        new_meter.id,
        new_meter.name,
        new_meter.project_id,
        new_meter.shared,
    )

    def setUp(self):
        super(TestShowMeter, self).setUp()

        self.cmd = network_meter.ShowMeter(self.app, self.namespace)

        self.network.find_metering_label = \
            mock.Mock(return_value=self.new_meter)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_meter_show_option(self):
        arglist = [
            self.new_meter.name,
        ]
        verifylist = [
            ('meter', self.new_meter.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_metering_label.assert_called_with(
            self.new_meter.name, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
