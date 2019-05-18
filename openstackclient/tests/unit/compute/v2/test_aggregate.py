#   Copyright 2016 Huawei, Inc. All rights reserved.
#
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

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.compute.v2 import aggregate
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestAggregate(compute_fakes.TestComputev2):

    fake_ag = compute_fakes.FakeAggregate.create_one_aggregate()

    columns = (
        'availability_zone',
        'hosts',
        'id',
        'name',
        'properties',
    )

    data = (
        fake_ag.availability_zone,
        format_columns.ListColumn(fake_ag.hosts),
        fake_ag.id,
        fake_ag.name,
        format_columns.DictColumn(fake_ag.metadata),
    )

    def setUp(self):
        super(TestAggregate, self).setUp()

        # Get a shortcut to the AggregateManager Mock
        self.aggregate_mock = self.app.client_manager.compute.aggregates
        self.aggregate_mock.reset_mock()


class TestAggregateAddHost(TestAggregate):

    def setUp(self):
        super(TestAggregateAddHost, self).setUp()

        self.aggregate_mock.get.return_value = self.fake_ag
        self.aggregate_mock.add_host.return_value = self.fake_ag
        self.cmd = aggregate.AddAggregateHost(self.app, None)

    def test_aggregate_add_host(self):
        arglist = [
            'ag1',
            'host1',
        ]
        verifylist = [
            ('aggregate', 'ag1'),
            ('host', 'host1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.aggregate_mock.add_host.assert_called_once_with(self.fake_ag,
                                                             parsed_args.host)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)


class TestAggregateCreate(TestAggregate):

    def setUp(self):
        super(TestAggregateCreate, self).setUp()

        self.aggregate_mock.create.return_value = self.fake_ag
        self.aggregate_mock.set_metadata.return_value = self.fake_ag
        self.cmd = aggregate.CreateAggregate(self.app, None)

    def test_aggregate_create(self):
        arglist = [
            'ag1',
        ]
        verifylist = [
            ('name', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.aggregate_mock.create.assert_called_once_with(parsed_args.name,
                                                           None)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_aggregate_create_with_zone(self):
        arglist = [
            '--zone', 'zone1',
            'ag1',
        ]
        verifylist = [
            ('zone', 'zone1'),
            ('name', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.aggregate_mock.create.assert_called_once_with(parsed_args.name,
                                                           parsed_args.zone)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_aggregate_create_with_property(self):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('property', {'key1': 'value1', 'key2': 'value2'}),
            ('name', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.aggregate_mock.create.assert_called_once_with(parsed_args.name,
                                                           None)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, parsed_args.property)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)


class TestAggregateDelete(TestAggregate):

    fake_ags = compute_fakes.FakeAggregate.create_aggregates(count=2)

    def setUp(self):
        super(TestAggregateDelete, self).setUp()

        self.aggregate_mock.get = (
            compute_fakes.FakeAggregate.get_aggregates(self.fake_ags))
        self.cmd = aggregate.DeleteAggregate(self.app, None)

    def test_aggregate_delete(self):
        arglist = [
            self.fake_ags[0].id
        ]
        verifylist = [
            ('aggregate', [self.fake_ags[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(self.fake_ags[0].id)
        self.aggregate_mock.delete.assert_called_once_with(self.fake_ags[0].id)
        self.assertIsNone(result)

    def test_delete_multiple_aggregates(self):
        arglist = []
        for a in self.fake_ags:
            arglist.append(a.id)
        verifylist = [
            ('aggregate', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self.fake_ags:
            calls.append(call(a.id))
        self.aggregate_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_agggregates_with_exception(self):
        arglist = [
            self.fake_ags[0].id,
            'unexist_aggregate',
        ]
        verifylist = [
            ('aggregate', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.fake_ags[0], exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 aggregates failed to delete.',
                                 str(e))

            find_mock.assert_any_call(self.aggregate_mock, self.fake_ags[0].id)
            find_mock.assert_any_call(self.aggregate_mock, 'unexist_aggregate')

            self.assertEqual(2, find_mock.call_count)
            self.aggregate_mock.delete.assert_called_once_with(
                self.fake_ags[0].id
            )


class TestAggregateList(TestAggregate):

    list_columns = (
        "ID",
        "Name",
        "Availability Zone",
    )

    list_columns_long = (
        "ID",
        "Name",
        "Availability Zone",
        "Properties",
    )

    list_data = ((
        TestAggregate.fake_ag.id,
        TestAggregate.fake_ag.name,
        TestAggregate.fake_ag.availability_zone,
    ), )

    list_data_long = ((
        TestAggregate.fake_ag.id,
        TestAggregate.fake_ag.name,
        TestAggregate.fake_ag.availability_zone,
        format_columns.DictColumn({
            key: value
            for key, value in TestAggregate.fake_ag.metadata.items()
            if key != 'availability_zone'
        }),
    ), )

    def setUp(self):
        super(TestAggregateList, self).setUp()

        self.aggregate_mock.list.return_value = [self.fake_ag]
        self.cmd = aggregate.ListAggregate(self.app, None)

    def test_aggregate_list(self):

        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.list_columns, columns)
        self.assertItemEqual(self.list_data, tuple(data))

    def test_aggregate_list_with_long(self):
        arglist = [
            '--long',
        ]
        vertifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, vertifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.list_columns_long, columns)
        self.assertListItemEqual(self.list_data_long, tuple(data))


class TestAggregateRemoveHost(TestAggregate):

    def setUp(self):
        super(TestAggregateRemoveHost, self).setUp()

        self.aggregate_mock.get.return_value = self.fake_ag
        self.aggregate_mock.remove_host.return_value = self.fake_ag
        self.cmd = aggregate.RemoveAggregateHost(self.app, None)

    def test_aggregate_add_host(self):
        arglist = [
            'ag1',
            'host1',
        ]
        verifylist = [
            ('aggregate', 'ag1'),
            ('host', 'host1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.aggregate_mock.remove_host.assert_called_once_with(
            self.fake_ag, parsed_args.host)
        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)


class TestAggregateSet(TestAggregate):

    def setUp(self):
        super(TestAggregateSet, self).setUp()

        self.aggregate_mock.get.return_value = self.fake_ag
        self.cmd = aggregate.SetAggregate(self.app, None)

    def test_aggregate_set_no_option(self):
        arglist = [
            'ag1',
        ]
        verifylist = [
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.assertNotCalled(self.aggregate_mock.update)
        self.assertNotCalled(self.aggregate_mock.set_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_name(self):
        arglist = [
            '--name', 'new_name',
            'ag1',
        ]
        verifylist = [
            ('name', 'new_name'),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.aggregate_mock.update.assert_called_once_with(
            self.fake_ag, {'name': parsed_args.name})
        self.assertNotCalled(self.aggregate_mock.set_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_zone(self):
        arglist = [
            '--zone', 'new_zone',
            'ag1',
        ]
        verifylist = [
            ('zone', 'new_zone'),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.aggregate_mock.update.assert_called_once_with(
            self.fake_ag, {'availability_zone': parsed_args.zone})
        self.assertNotCalled(self.aggregate_mock.set_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_property(self):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('property', {'key1': 'value1', 'key2': 'value2'}),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.assertNotCalled(self.aggregate_mock.update)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, parsed_args.property)
        self.assertIsNone(result)

    def test_aggregate_set_with_no_property_and_property(self):
        arglist = [
            '--no-property',
            '--property', 'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('no_property', True),
            ('property', {'key2': 'value2'}),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.assertNotCalled(self.aggregate_mock.update)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, {'key1': None, 'key2': 'value2'})
        self.assertIsNone(result)

    def test_aggregate_set_with_no_property(self):
        arglist = [
            '--no-property',
            'ag1',
        ]
        verifylist = [
            ('no_property', True),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.assertNotCalled(self.aggregate_mock.update)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, {'key1': None})
        self.assertIsNone(result)

    def test_aggregate_set_with_zone_and_no_property(self):
        arglist = [
            '--zone', 'new_zone',
            '--no-property',
            'ag1',
        ]
        verifylist = [
            ('zone', 'new_zone'),
            ('no_property', True),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)
        self.aggregate_mock.update.assert_called_once_with(
            self.fake_ag, {'availability_zone': parsed_args.zone})
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, {'key1': None})
        self.assertIsNone(result)


class TestAggregateShow(TestAggregate):

    columns = (
        'availability_zone',
        'hosts',
        'id',
        'name',
        'properties',
    )

    data = (
        TestAggregate.fake_ag.availability_zone,
        format_columns.ListColumn(TestAggregate.fake_ag.hosts),
        TestAggregate.fake_ag.id,
        TestAggregate.fake_ag.name,
        format_columns.DictColumn({
            key: value
            for key, value in TestAggregate.fake_ag.metadata.items()
            if key != 'availability_zone'
        }),
    )

    def setUp(self):
        super(TestAggregateShow, self).setUp()

        self.aggregate_mock.get.return_value = self.fake_ag
        self.cmd = aggregate.ShowAggregate(self.app, None)

    def test_aggregate_show(self):
        arglist = [
            'ag1',
        ]
        verifylist = [
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.aggregate_mock.get.assert_called_once_with(parsed_args.aggregate)

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, tuple(data))


class TestAggregateUnset(TestAggregate):

    def setUp(self):
        super(TestAggregateUnset, self).setUp()

        self.aggregate_mock.get.return_value = self.fake_ag
        self.cmd = aggregate.UnsetAggregate(self.app, None)

    def test_aggregate_unset(self):
        arglist = [
            '--property', 'unset_key',
            'ag1',
        ]
        verifylist = [
            ('property', ['unset_key']),
            ('aggregate', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, {'unset_key': None})
        self.assertIsNone(result)

    def test_aggregate_unset_multiple_properties(self):
        arglist = [
            '--property', 'unset_key1',
            '--property', 'unset_key2',
            'ag1',
        ]
        verifylist = [
            ('property', ['unset_key1', 'unset_key2']),
            ('aggregate', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, {'unset_key1': None, 'unset_key2': None})
        self.assertIsNone(result)

    def test_aggregate_unset_no_option(self):
        arglist = [
            'ag1',
        ]
        verifylist = [
            ('property', None),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertNotCalled(self.aggregate_mock.set_metadata)
        self.assertIsNone(result)
