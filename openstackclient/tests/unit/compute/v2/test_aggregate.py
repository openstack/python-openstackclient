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

from unittest import mock
from unittest.mock import call

from openstack import exceptions as sdk_exceptions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.compute.v2 import aggregate
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


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
        self.app.client_manager.sdk_connection = mock.Mock()
        self.app.client_manager.sdk_connection.compute = mock.Mock()
        self.sdk_client = self.app.client_manager.sdk_connection.compute
        self.sdk_client.aggregates = mock.Mock()
        self.sdk_client.find_aggregate = mock.Mock()
        self.sdk_client.create_aggregate = mock.Mock()
        self.sdk_client.update_aggregate = mock.Mock()
        self.sdk_client.update_aggregate = mock.Mock()
        self.sdk_client.set_aggregate_metadata = mock.Mock()
        self.sdk_client.add_host_to_aggregate = mock.Mock()
        self.sdk_client.remove_host_from_aggregate = mock.Mock()


class TestAggregateAddHost(TestAggregate):

    def setUp(self):
        super(TestAggregateAddHost, self).setUp()

        self.sdk_client.find_aggregate.return_value = self.fake_ag
        self.sdk_client.add_host_to_aggregate.return_value = self.fake_ag
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
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.add_host_to_aggregate.assert_called_once_with(
            self.fake_ag.id, parsed_args.host)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestAggregateCreate(TestAggregate):

    def setUp(self):
        super(TestAggregateCreate, self).setUp()

        self.sdk_client.create_aggregate.return_value = self.fake_ag
        self.sdk_client.set_aggregate_metadata.return_value = self.fake_ag
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
        self.sdk_client.create_aggregate.assert_called_once_with(
            name=parsed_args.name)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

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
        self.sdk_client.create_aggregate.assert_called_once_with(
            name=parsed_args.name, availability_zone=parsed_args.zone)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_aggregate_create_with_property(self):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('name', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.sdk_client.create_aggregate.assert_called_once_with(
            name=parsed_args.name)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, parsed_args.properties)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestAggregateDelete(TestAggregate):

    fake_ags = compute_fakes.FakeAggregate.create_aggregates(count=2)

    def setUp(self):
        super(TestAggregateDelete, self).setUp()

        self.sdk_client.find_aggregate = (
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
        self.cmd.take_action(parsed_args)
        self.sdk_client.find_aggregate.assert_called_once_with(
            self.fake_ags[0].id, ignore_missing=False)
        self.sdk_client.delete_aggregate.assert_called_once_with(
            self.fake_ags[0].id, ignore_missing=False)

    def test_delete_multiple_aggregates(self):
        arglist = []
        for a in self.fake_ags:
            arglist.append(a.id)
        verifylist = [
            ('aggregate', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        calls = []
        for a in self.fake_ags:
            calls.append(call(a.id, ignore_missing=False))
        self.sdk_client.find_aggregate.assert_has_calls(calls)
        self.sdk_client.delete_aggregate.assert_has_calls(calls)

    def test_delete_multiple_agggregates_with_exception(self):
        arglist = [
            self.fake_ags[0].id,
            'unexist_aggregate',
        ]
        verifylist = [
            ('aggregate', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.sdk_client.find_aggregate.side_effect = [
            self.fake_ags[0], sdk_exceptions.NotFoundException]
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 aggregates failed to delete.',
                             str(e))

        calls = []
        for a in arglist:
            calls.append(call(a, ignore_missing=False))
        self.sdk_client.find_aggregate.assert_has_calls(calls)
        self.sdk_client.delete_aggregate.assert_called_with(
            self.fake_ags[0].id, ignore_missing=False)


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

        self.sdk_client.aggregates.return_value = [self.fake_ag]
        self.cmd = aggregate.ListAggregate(self.app, None)

    def test_aggregate_list(self):

        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.list_columns, columns)
        self.assertCountEqual(self.list_data, tuple(data))

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
        self.assertCountEqual(self.list_data_long, tuple(data))


class TestAggregateRemoveHost(TestAggregate):

    def setUp(self):
        super(TestAggregateRemoveHost, self).setUp()

        self.sdk_client.find_aggregate.return_value = self.fake_ag
        self.sdk_client.remove_host_from_aggregate.return_value = self.fake_ag
        self.cmd = aggregate.RemoveAggregateHost(self.app, None)

    def test_aggregate_remove_host(self):
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
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.remove_host_from_aggregate.assert_called_once_with(
            self.fake_ag.id, parsed_args.host)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestAggregateSet(TestAggregate):

    def setUp(self):
        super(TestAggregateSet, self).setUp()

        self.sdk_client.find_aggregate.return_value = self.fake_ag
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

        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.assertNotCalled(self.sdk_client.update_aggregate)
        self.assertNotCalled(self.sdk_client.set_aggregate_metadata)
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

        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.update_aggregate.assert_called_once_with(
            self.fake_ag.id, name=parsed_args.name)
        self.assertNotCalled(self.sdk_client.set_aggregate_metadata)
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

        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.update_aggregate.assert_called_once_with(
            self.fake_ag.id, availability_zone=parsed_args.zone)
        self.assertNotCalled(self.sdk_client.set_aggregate_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_property(self):
        arglist = [
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.assertNotCalled(self.sdk_client.update_aggregate)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, parsed_args.properties)
        self.assertIsNone(result)

    def test_aggregate_set_with_no_property_and_property(self):
        arglist = [
            '--no-property',
            '--property', 'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('no_property', True),
            ('properties', {'key2': 'value2'}),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.assertNotCalled(self.sdk_client.update_aggregate)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'key1': None, 'key2': 'value2'})
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
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.assertNotCalled(self.sdk_client.update_aggregate)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'key1': None})
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
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.update_aggregate.assert_called_once_with(
            self.fake_ag.id, availability_zone=parsed_args.zone)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'key1': None})
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

        self.sdk_client.find_aggregate.return_value = self.fake_ag
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
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))


class TestAggregateUnset(TestAggregate):

    def setUp(self):
        super(TestAggregateUnset, self).setUp()

        self.sdk_client.find_aggregate.return_value = self.fake_ag
        self.cmd = aggregate.UnsetAggregate(self.app, None)

    def test_aggregate_unset(self):
        arglist = [
            '--property', 'unset_key',
            'ag1',
        ]
        verifylist = [
            ('properties', ['unset_key']),
            ('aggregate', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'unset_key': None})
        self.assertIsNone(result)

    def test_aggregate_unset_multiple_properties(self):
        arglist = [
            '--property', 'unset_key1',
            '--property', 'unset_key2',
            'ag1',
        ]
        verifylist = [
            ('properties', ['unset_key1', 'unset_key2']),
            ('aggregate', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.sdk_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'unset_key1': None, 'unset_key2': None})
        self.assertIsNone(result)

    def test_aggregate_unset_no_option(self):
        arglist = [
            'ag1',
        ]
        verifylist = [
            ('properties', []),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertNotCalled(self.sdk_client.set_aggregate_metadata)
        self.assertIsNone(result)


class TestAggregateCacheImage(TestAggregate):

    images = image_fakes.FakeImage.create_images(count=2)

    def setUp(self):
        super(TestAggregateCacheImage, self).setUp()

        self.sdk_client.find_aggregate.return_value = self.fake_ag
        self.find_image_mock = mock.Mock(side_effect=self.images)
        self.app.client_manager.sdk_connection.image.find_image = \
            self.find_image_mock

        self.cmd = aggregate.CacheImageForAggregate(self.app, None)

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=False)
    def test_aggregate_not_supported(self, sm_mock):
        arglist = [
            'ag1',
            'im1'
        ]
        verifylist = [
            ('aggregate', 'ag1'),
            ('image', ['im1']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args
        )

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_aggregate_add_single_image(self, sm_mock):
        arglist = [
            'ag1',
            'im1'
        ]
        verifylist = [
            ('aggregate', 'ag1'),
            ('image', ['im1']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.aggregate_precache_images.assert_called_once_with(
            self.fake_ag.id, [self.images[0].id])

    @mock.patch.object(sdk_utils, 'supports_microversion', return_value=True)
    def test_aggregate_add_multiple_images(self, sm_mock):
        arglist = [
            'ag1',
            'im1',
            'im2',
        ]
        verifylist = [
            ('aggregate', 'ag1'),
            ('image', ['im1', 'im2']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.sdk_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False)
        self.sdk_client.aggregate_precache_images.assert_called_once_with(
            self.fake_ag.id, [self.images[0].id, self.images[1].id])
