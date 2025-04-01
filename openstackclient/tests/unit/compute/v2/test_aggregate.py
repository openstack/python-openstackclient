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

from openstack.compute.v2 import aggregate as _aggregate
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.compute.v2 import aggregate
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestAggregate(compute_fakes.TestComputev2):
    columns = (
        'availability_zone',
        'created_at',
        'deleted_at',
        'hosts',
        'id',
        'is_deleted',
        'name',
        'properties',
        'updated_at',
        'uuid',
    )

    def setUp(self):
        super().setUp()

        self.fake_ag = sdk_fakes.generate_fake_resource(
            _aggregate.Aggregate,
            metadata={'availability_zone': 'ag_zone', 'key1': 'value1'},
        )
        self.data = (
            self.fake_ag.availability_zone,
            self.fake_ag.created_at,
            self.fake_ag.deleted_at,
            format_columns.ListColumn(self.fake_ag.hosts),
            self.fake_ag.id,
            self.fake_ag.is_deleted,
            self.fake_ag.name,
            format_columns.DictColumn(self.fake_ag.metadata),
            self.fake_ag.updated_at,
            self.fake_ag.uuid,
        )


class TestAggregateAddHost(TestAggregate):
    def setUp(self):
        super().setUp()

        self.compute_client.find_aggregate.return_value = self.fake_ag
        self.compute_client.add_host_to_aggregate.return_value = self.fake_ag
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
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.add_host_to_aggregate.assert_called_once_with(
            self.fake_ag.id, parsed_args.host
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestAggregateCreate(TestAggregate):
    def setUp(self):
        super().setUp()

        self.compute_client.create_aggregate.return_value = self.fake_ag
        self.compute_client.set_aggregate_metadata.return_value = self.fake_ag
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
        self.compute_client.create_aggregate.assert_called_once_with(
            name=parsed_args.name
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_aggregate_create_with_zone(self):
        arglist = [
            '--zone',
            'zone1',
            'ag1',
        ]
        verifylist = [
            ('zone', 'zone1'),
            ('name', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.compute_client.create_aggregate.assert_called_once_with(
            name=parsed_args.name, availability_zone=parsed_args.zone
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_aggregate_create_with_property(self):
        arglist = [
            '--property',
            'key1=value1',
            '--property',
            'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('name', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.compute_client.create_aggregate.assert_called_once_with(
            name=parsed_args.name
        )
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, parsed_args.properties
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestAggregateDelete(TestAggregate):
    def setUp(self):
        super().setUp()

        self.fake_ags = list(
            sdk_fakes.generate_fake_resources(_aggregate.Aggregate, 2)
        )

        self.compute_client.find_aggregate = mock.Mock(
            side_effect=[self.fake_ags[0], self.fake_ags[1]]
        )
        self.cmd = aggregate.DeleteAggregate(self.app, None)

    def test_aggregate_delete(self):
        arglist = [self.fake_ags[0].id]
        verifylist = [
            ('aggregate', [self.fake_ags[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.compute_client.find_aggregate.assert_called_once_with(
            self.fake_ags[0].id, ignore_missing=False
        )
        self.compute_client.delete_aggregate.assert_called_once_with(
            self.fake_ags[0].id, ignore_missing=False
        )

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
        self.compute_client.find_aggregate.assert_has_calls(calls)
        self.compute_client.delete_aggregate.assert_has_calls(calls)

    def test_delete_multiple_agggregates_with_exception(self):
        arglist = [
            self.fake_ags[0].id,
            'unexist_aggregate',
        ]
        verifylist = [
            ('aggregate', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_client.find_aggregate.side_effect = [
            self.fake_ags[0],
            sdk_exceptions.NotFoundException,
        ]
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 aggregates failed to delete.', str(e))

        calls = []
        for a in arglist:
            calls.append(call(a, ignore_missing=False))
        self.compute_client.find_aggregate.assert_has_calls(calls)
        self.compute_client.delete_aggregate.assert_called_with(
            self.fake_ags[0].id, ignore_missing=False
        )


class TestAggregateList(TestAggregate):
    def setUp(self):
        super().setUp()

        self.compute_client.aggregates.return_value = [self.fake_ag]
        self.cmd = aggregate.ListAggregate(self.app, None)

    def test_aggregate_list(self):
        self.set_compute_api_version('2.41')

        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "ID",
            "UUID",
            "Name",
            "Availability Zone",
        )
        expected_data = (
            (
                self.fake_ag.id,
                self.fake_ag.uuid,
                self.fake_ag.name,
                self.fake_ag.availability_zone,
            ),
        )

        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))

    def test_aggregate_list_pre_v241(self):
        self.set_compute_api_version('2.40')

        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "ID",
            "Name",
            "Availability Zone",
        )
        expected_data = (
            (
                self.fake_ag.id,
                self.fake_ag.name,
                self.fake_ag.availability_zone,
            ),
        )

        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))

    def test_aggregate_list_with_long(self):
        self.set_compute_api_version('2.41')

        arglist = [
            '--long',
        ]
        vertifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, vertifylist)
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "ID",
            "UUID",
            "Name",
            "Availability Zone",
            "Properties",
            "Hosts",
        )
        expected_data = (
            (
                self.fake_ag.id,
                self.fake_ag.uuid,
                self.fake_ag.name,
                self.fake_ag.availability_zone,
                format_columns.DictColumn(
                    {
                        key: value
                        for key, value in self.fake_ag.metadata.items()
                        if key != 'availability_zone'
                    }
                ),
                format_columns.ListColumn(self.fake_ag.hosts),
            ),
        )

        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))


class TestAggregateRemoveHost(TestAggregate):
    def setUp(self):
        super().setUp()

        self.compute_client.find_aggregate.return_value = self.fake_ag
        self.compute_client.remove_host_from_aggregate.return_value = (
            self.fake_ag
        )
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
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.remove_host_from_aggregate.assert_called_once_with(
            self.fake_ag.id, parsed_args.host
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestAggregateSet(TestAggregate):
    def setUp(self):
        super().setUp()

        self.compute_client.find_aggregate.return_value = self.fake_ag
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

        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.assertNotCalled(self.compute_client.update_aggregate)
        self.assertNotCalled(self.compute_client.set_aggregate_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_name(self):
        arglist = [
            '--name',
            'new_name',
            'ag1',
        ]
        verifylist = [
            ('name', 'new_name'),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.update_aggregate.assert_called_once_with(
            self.fake_ag.id, name=parsed_args.name
        )
        self.assertNotCalled(self.compute_client.set_aggregate_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_zone(self):
        arglist = [
            '--zone',
            'new_zone',
            'ag1',
        ]
        verifylist = [
            ('zone', 'new_zone'),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.update_aggregate.assert_called_once_with(
            self.fake_ag.id, availability_zone=parsed_args.zone
        )
        self.assertNotCalled(self.compute_client.set_aggregate_metadata)
        self.assertIsNone(result)

    def test_aggregate_set_with_property(self):
        arglist = [
            '--property',
            'key1=value1',
            '--property',
            'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.assertNotCalled(self.compute_client.update_aggregate)
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, parsed_args.properties
        )
        self.assertIsNone(result)

    def test_aggregate_set_with_no_property_and_property(self):
        arglist = [
            '--no-property',
            '--property',
            'key2=value2',
            'ag1',
        ]
        verifylist = [
            ('no_property', True),
            ('properties', {'key2': 'value2'}),
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.assertNotCalled(self.compute_client.update_aggregate)
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'key1': None, 'key2': 'value2'}
        )
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
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.assertNotCalled(self.compute_client.update_aggregate)
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'key1': None}
        )
        self.assertIsNone(result)

    def test_aggregate_set_with_zone_and_no_property(self):
        arglist = [
            '--zone',
            'new_zone',
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
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.update_aggregate.assert_called_once_with(
            self.fake_ag.id, availability_zone=parsed_args.zone
        )
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'key1': None}
        )
        self.assertIsNone(result)


class TestAggregateShow(TestAggregate):
    columns = (
        'availability_zone',
        'created_at',
        'deleted_at',
        'hosts',
        'id',
        'is_deleted',
        'name',
        'properties',
        'updated_at',
        'uuid',
    )

    def setUp(self):
        super().setUp()

        self.compute_client.find_aggregate.return_value = self.fake_ag
        self.cmd = aggregate.ShowAggregate(self.app, None)

        self.data = (
            self.fake_ag.availability_zone,
            self.fake_ag.created_at,
            self.fake_ag.deleted_at,
            format_columns.ListColumn(self.fake_ag.hosts),
            self.fake_ag.id,
            self.fake_ag.is_deleted,
            self.fake_ag.name,
            format_columns.DictColumn(self.fake_ag.metadata),
            self.fake_ag.updated_at,
            self.fake_ag.uuid,
        )

    def test_aggregate_show(self):
        arglist = [
            'ag1',
        ]
        verifylist = [
            ('aggregate', 'ag1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, tuple(data))


class TestAggregateUnset(TestAggregate):
    def setUp(self):
        super().setUp()

        self.compute_client.find_aggregate.return_value = self.fake_ag
        self.cmd = aggregate.UnsetAggregate(self.app, None)

    def test_aggregate_unset(self):
        arglist = [
            '--property',
            'unset_key',
            'ag1',
        ]
        verifylist = [
            ('properties', ['unset_key']),
            ('aggregate', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'unset_key': None}
        )
        self.assertIsNone(result)

    def test_aggregate_unset_multiple_properties(self):
        arglist = [
            '--property',
            'unset_key1',
            '--property',
            'unset_key2',
            'ag1',
        ]
        verifylist = [
            ('properties', ['unset_key1', 'unset_key2']),
            ('aggregate', 'ag1'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.compute_client.set_aggregate_metadata.assert_called_once_with(
            self.fake_ag.id, {'unset_key1': None, 'unset_key2': None}
        )
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
        self.assertNotCalled(self.compute_client.set_aggregate_metadata)
        self.assertIsNone(result)


class TestAggregateCacheImage(TestAggregate):
    images = image_fakes.create_images(count=2)

    def setUp(self):
        super().setUp()

        self.compute_client.find_aggregate.return_value = self.fake_ag
        self.find_image_mock = mock.Mock(side_effect=self.images)
        self.app.client_manager.sdk_connection.image.find_image = (
            self.find_image_mock
        )

        self.cmd = aggregate.CacheImageForAggregate(self.app, None)

    def test_aggregate_cache_pre_v281(self):
        self.set_compute_api_version('2.80')

        arglist = ['ag1', 'im1']
        verifylist = [
            ('aggregate', 'ag1'),
            ('image', ['im1']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_aggregate_cache_add_single_image(self):
        self.set_compute_api_version('2.81')

        arglist = ['ag1', 'im1']
        verifylist = [
            ('aggregate', 'ag1'),
            ('image', ['im1']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.aggregate_precache_images.assert_called_once_with(
            self.fake_ag.id, [self.images[0].id]
        )

    def test_aggregate_cache_add_multiple_images(self):
        self.set_compute_api_version('2.81')

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
        self.compute_client.find_aggregate.assert_called_once_with(
            parsed_args.aggregate, ignore_missing=False
        )
        self.compute_client.aggregate_precache_images.assert_called_once_with(
            self.fake_ag.id, [self.images[0].id, self.images[1].id]
        )
