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

from openstackclient.network.v2 import network_meter_rule
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestMeterRule(network_fakes.TestNetworkV2):
    def setUp(self):
        super(TestMeterRule, self).setUp()
        self.network = self.app.client_manager.network
        self.projects_mock = self.app.client_manager.identity.projects
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateMeterRule(TestMeterRule):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()

    new_rule = (
        network_fakes.FakeNetworkMeterRule.
        create_one_rule()
    )

    columns = (
        'direction',
        'excluded',
        'id',
        'metering_label_id',
        'project_id',
        'remote_ip_prefix',
    )
    data = (
        new_rule.direction,
        new_rule.excluded,
        new_rule.id,
        new_rule.metering_label_id,
        new_rule.project_id,
        new_rule.remote_ip_prefix,
    )

    def setUp(self):
        super(TestCreateMeterRule, self).setUp()
        fake_meter = network_fakes.FakeNetworkMeter.create_one_meter({
            'id': self.new_rule.metering_label_id})

        self.network.create_metering_label_rule = mock.Mock(
            return_value=self.new_rule)
        self.projects_mock.get.return_value = self.project
        self.cmd = network_meter_rule.CreateMeterRule(self.app,
                                                      self.namespace)
        self.network.find_metering_label = mock.Mock(
            return_value=fake_meter)

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.new_rule.metering_label_id,
            "--remote-ip-prefix", self.new_rule.remote_ip_prefix,
        ]
        verifylist = [
            ('meter', self.new_rule.metering_label_id),
            ('remote_ip_prefix', self.new_rule.remote_ip_prefix),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_metering_label_rule.assert_called_once_with(
            **{'direction': 'ingress',
               'metering_label_id': self.new_rule.metering_label_id,
               'remote_ip_prefix': self.new_rule.remote_ip_prefix, }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            "--ingress",
            "--include",
            self.new_rule.metering_label_id,
            "--remote-ip-prefix", self.new_rule.remote_ip_prefix,
        ]
        verifylist = [
            ('ingress', True),
            ('include', True),
            ('meter', self.new_rule.metering_label_id),
            ('remote_ip_prefix', self.new_rule.remote_ip_prefix),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_metering_label_rule.assert_called_once_with(
            **{'direction': self.new_rule.direction,
               'excluded': self.new_rule.excluded,
               'metering_label_id': self.new_rule.metering_label_id,
               'remote_ip_prefix': self.new_rule.remote_ip_prefix, }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteMeterRule(TestMeterRule):
    def setUp(self):
        super(TestDeleteMeterRule, self).setUp()
        self.rule_list = \
            network_fakes.FakeNetworkMeterRule.create_meter_rule(
                count=2
            )
        self.network.delete_metering_label_rule = mock.Mock(return_value=None)

        self.network.find_metering_label_rule = network_fakes \
            .FakeNetworkMeterRule.get_meter_rule(
                meter_rule=self.rule_list
            )

        self.cmd = network_meter_rule.DeleteMeterRule(self.app,
                                                      self.namespace)

    def test_delete_one_rule(self):
        arglist = [
            self.rule_list[0].id,
        ]
        verifylist = [
            ('meter_rule_id', [self.rule_list[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_metering_label_rule.assert_called_once_with(
            self.rule_list[0]
        )
        self.assertIsNone(result)

    def test_delete_multiple_rules(self):
        arglist = []
        for rule in self.rule_list:
            arglist.append(rule.id)
        verifylist = [
            ('meter_rule_id', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for rule in self.rule_list:
            calls.append(call(rule))
        self.network.delete_metering_label_rule.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_rules_exception(self):
        arglist = [
            self.rule_list[0].id,
            'xxxx-yyyy-zzzz',
            self.rule_list[1].id,
        ]
        verifylist = [
            ('meter_rule_id', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        return_find = [
            self.rule_list[0],
            exceptions.NotFound('404'),
            self.rule_list[1],
        ]
        self.network.find_metering_label_rule = mock.Mock(
            side_effect=return_find
        )

        ret_delete = [
            None,
            exceptions.NotFound('404'),
        ]
        self.network.delete_metering_label_rule = mock.Mock(
            side_effect=ret_delete
        )

        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

        calls = [
            call(self.rule_list[0]),
            call(self.rule_list[1]),
        ]
        self.network.delete_metering_label_rule.assert_has_calls(calls)


class TestListMeterRule(TestMeterRule):
    rule_list = \
        network_fakes.FakeNetworkMeterRule.create_meter_rule(
            count=2
        )

    columns = (
        'ID',
        'Excluded',
        'Direction',
        'Remote IP Prefix',
    )

    data = []

    for rule in rule_list:
        data.append((
            rule.id,
            rule.excluded,
            rule.direction,
            rule.remote_ip_prefix,
        ))

    def setUp(self):
        super(TestListMeterRule, self).setUp()

        self.network.metering_label_rules = mock.Mock(
            return_value=self.rule_list
        )

        self.cmd = network_meter_rule.ListMeterRule(self.app,
                                                    self.namespace)

    def test_rule_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.metering_label_rules.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowMeterRule(TestMeterRule):
    new_rule = (
        network_fakes.FakeNetworkMeterRule.
        create_one_rule()
    )

    columns = (
        'direction',
        'excluded',
        'id',
        'metering_label_id',
        'project_id',
        'remote_ip_prefix',
    )

    data = (
        new_rule.direction,
        new_rule.excluded,
        new_rule.id,
        new_rule.metering_label_id,
        new_rule.project_id,
        new_rule.remote_ip_prefix,
    )

    def setUp(self):
        super(TestShowMeterRule, self).setUp()

        self.cmd = network_meter_rule.ShowMeterRule(self.app,
                                                    self.namespace)

        self.network.find_metering_label_rule = \
            mock.Mock(return_value=self.new_rule)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_label_rule_show_option(self):
        arglist = [
            self.new_rule.id,
        ]
        verifylist = [
            ('meter_rule_id', self.new_rule.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_metering_label_rule.assert_called_with(
            self.new_rule.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
