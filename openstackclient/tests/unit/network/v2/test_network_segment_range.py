# Copyright (c) 2019, Intel Corporation.
# All Rights Reserved.
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

from osc_lib import exceptions

from openstackclient.network.v2 import network_segment_range
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkSegmentRange(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkSegmentRange, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestCreateNetworkSegmentRange(TestNetworkSegmentRange):

    # The network segment range to create.
    _network_segment_range = network_fakes.FakeNetworkSegmentRange.\
        create_one_network_segment_range()

    columns = (
        'available',
        'default',
        'id',
        'maximum',
        'minimum',
        'name',
        'network_type',
        'physical_network',
        'project_id',
        'shared',
        'used',
    )

    data = (
        ['100-103', '105'],
        _network_segment_range.default,
        _network_segment_range.id,
        _network_segment_range.maximum,
        _network_segment_range.minimum,
        _network_segment_range.name,
        _network_segment_range.network_type,
        _network_segment_range.physical_network,
        _network_segment_range.project_id,
        _network_segment_range.shared,
        {'3312e4ba67864b2eb53f3f41432f8efc': ['104', '106']},
    )

    def setUp(self):
        super(TestCreateNetworkSegmentRange, self).setUp()

        self.network.find_extension = mock.Mock()
        self.network.create_network_segment_range = mock.Mock(
            return_value=self._network_segment_range
        )

        # Get the command object to test
        self.cmd = network_segment_range.CreateNetworkSegmentRange(
            self.app,
            self.namespace
        )

    def test_create_no_options(self):
        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, [], [])

    def test_create_invalid_network_type(self):
        arglist = [
            '--private',
            '--project', self._network_segment_range.project_id,
            '--network-type', 'foo',
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, [])

    def test_create_default_with_project_id(self):
        arglist = [
            '--project', self._network_segment_range.project_id,
            '--network-type', 'vxlan',
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('project', self._network_segment_range.project_id),
            ('network_type', 'vxlan'),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_create_shared_with_project_id(self):
        arglist = [
            '--shared',
            '--project', self._network_segment_range.project_id,
            '--network-type', 'vxlan',
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('shared', True),
            ('project', self._network_segment_range.project_id),
            ('network_type', 'vxlan'),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_create_tunnel_with_physical_network(self):
        arglist = [
            '--shared',
            '--network-type', 'vxlan',
            '--physical-network', self._network_segment_range.physical_network,
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('shared', True),
            ('network_type', 'vxlan'),
            ('physical_network', self._network_segment_range.physical_network),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_create_minimum_options(self):
        arglist = [
            '--network-type', 'vxlan',
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('network_type', 'vxlan'),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network_segment_range.assert_called_once_with(**{
            'shared': True,
            'network_type': 'vxlan',
            'minimum': self._network_segment_range.minimum,
            'maximum': self._network_segment_range.maximum,
            'name': self._network_segment_range.name,
        })

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_private_minimum_options(self):
        arglist = [
            '--private',
            '--project', self._network_segment_range.project_id,
            '--network-type', 'vxlan',
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('shared', False),
            ('project', self._network_segment_range.project_id),
            ('network_type', 'vxlan'),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network_segment_range.assert_called_once_with(**{
            'shared': False,
            'project_id': mock.ANY,
            'network_type': 'vxlan',
            'minimum': self._network_segment_range.minimum,
            'maximum': self._network_segment_range.maximum,
            'name': self._network_segment_range.name,
        })

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_shared_minimum_options(self):
        arglist = [
            '--shared',
            '--network-type', 'vxlan',
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('shared', True),
            ('network_type', 'vxlan'),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network_segment_range.assert_called_once_with(**{
            'shared': True,
            'network_type': 'vxlan',
            'minimum': self._network_segment_range.minimum,
            'maximum': self._network_segment_range.maximum,
            'name': self._network_segment_range.name,
        })

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--private',
            '--project', self._network_segment_range.project_id,
            '--network-type', self._network_segment_range.network_type,
            '--physical-network', self._network_segment_range.physical_network,
            '--minimum', str(self._network_segment_range.minimum),
            '--maximum', str(self._network_segment_range.maximum),
            self._network_segment_range.name,
        ]
        verifylist = [
            ('shared', self._network_segment_range.shared),
            ('project', self._network_segment_range.project_id),
            ('network_type', self._network_segment_range.network_type),
            ('physical_network', self._network_segment_range.physical_network),
            ('minimum', self._network_segment_range.minimum),
            ('maximum', self._network_segment_range.maximum),
            ('name', self._network_segment_range.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network_segment_range.assert_called_once_with(**{
            'shared': self._network_segment_range.shared,
            'project_id': mock.ANY,
            'network_type': self._network_segment_range.network_type,
            'physical_network': self._network_segment_range.physical_network,
            'minimum': self._network_segment_range.minimum,
            'maximum': self._network_segment_range.maximum,
            'name': self._network_segment_range.name,
        })

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkSegmentRange(TestNetworkSegmentRange):

    # The network segment ranges to delete.
    _network_segment_ranges = \
        network_fakes.FakeNetworkSegmentRange.create_network_segment_ranges()

    def setUp(self):
        super(TestDeleteNetworkSegmentRange, self).setUp()

        self.network.find_extension = mock.Mock()
        self.network.delete_network_segment_range = mock.Mock(
            return_value=None)
        self.network.find_network_segment_range = mock.Mock(
            side_effect=self._network_segment_ranges
        )

        # Get the command object to test
        self.cmd = network_segment_range.DeleteNetworkSegmentRange(
            self.app,
            self.namespace
        )

    def test_delete(self):
        arglist = [
            self._network_segment_ranges[0].id,
        ]
        verifylist = [
            ('network_segment_range', [self._network_segment_ranges[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network.delete_network_segment_range.assert_called_once_with(
            self._network_segment_ranges[0]
        )
        self.assertIsNone(result)

    def test_delete_multiple(self):
        arglist = []
        for _network_segment_range in self._network_segment_ranges:
            arglist.append(_network_segment_range.id)
        verifylist = [
            ('network_segment_range', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for _network_segment_range in self._network_segment_ranges:
            calls.append(call(_network_segment_range))
        self.network.delete_network_segment_range.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_with_exception(self):
        arglist = [
            self._network_segment_ranges[0].id,
            'doesnotexist'
        ]
        verifylist = [
            ('network_segment_range',
             [self._network_segment_ranges[0].id, 'doesnotexist']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._network_segment_ranges[0],
                            exceptions.CommandError]
        self.network.find_network_segment_range = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 network segment ranges failed to delete.',
                             str(e))

        self.network.find_network_segment_range.assert_any_call(
            self._network_segment_ranges[0].id, ignore_missing=False)
        self.network.find_network_segment_range.assert_any_call(
            'doesnotexist', ignore_missing=False)
        self.network.delete_network_segment_range.assert_called_once_with(
            self._network_segment_ranges[0]
        )


class TestListNetworkSegmentRange(TestNetworkSegmentRange):
    _network_segment_ranges = network_fakes.FakeNetworkSegmentRange.\
        create_network_segment_ranges(count=3)

    columns = (
        'ID',
        'Name',
        'Default',
        'Shared',
        'Project ID',
        'Network Type',
        'Physical Network',
        'Minimum ID',
        'Maximum ID'
    )
    columns_long = columns + (
        'Used',
        'Available',
    )

    data = []
    for _network_segment_range in _network_segment_ranges:
        data.append((
            _network_segment_range.id,
            _network_segment_range.name,
            _network_segment_range.default,
            _network_segment_range.shared,
            _network_segment_range.project_id,
            _network_segment_range.network_type,
            _network_segment_range.physical_network,
            _network_segment_range.minimum,
            _network_segment_range.maximum,
        ))

    data_long = []
    for _network_segment_range in _network_segment_ranges:
        data_long.append((
            _network_segment_range.id,
            _network_segment_range.name,
            _network_segment_range.default,
            _network_segment_range.shared,
            _network_segment_range.project_id,
            _network_segment_range.network_type,
            _network_segment_range.physical_network,
            _network_segment_range.minimum,
            _network_segment_range.maximum,
            {'3312e4ba67864b2eb53f3f41432f8efc': ['104', '106']},
            ['100-103', '105'],
        ))

    def setUp(self):
        super(TestListNetworkSegmentRange, self).setUp()

        # Get the command object to test
        self.cmd = network_segment_range.ListNetworkSegmentRange(
            self.app, self.namespace)

        self.network.find_extension = mock.Mock()
        self.network.network_segment_ranges = mock.Mock(
            return_value=self._network_segment_ranges)

    def test_list_no_option(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('available', False),
            ('unavailable', False),
            ('used', False),
            ('unused', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.network_segment_ranges.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('available', False),
            ('unavailable', False),
            ('used', False),
            ('unused', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.network_segment_ranges.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestSetNetworkSegmentRange(TestNetworkSegmentRange):

    # The network segment range to set.
    _network_segment_range = network_fakes.FakeNetworkSegmentRange.\
        create_one_network_segment_range()
    # The network segment range updated.
    minimum_updated = _network_segment_range.minimum - 5
    maximum_updated = _network_segment_range.maximum + 5
    available_updated = (list(range(minimum_updated, 104)) + [105] +
                         list(range(107, maximum_updated + 1)))
    _network_segment_range_updated = network_fakes.FakeNetworkSegmentRange.\
        create_one_network_segment_range(
            attrs={'minimum': minimum_updated,
                   'maximum': maximum_updated,
                   'used': {104: '3312e4ba67864b2eb53f3f41432f8efc',
                            106: '3312e4ba67864b2eb53f3f41432f8efc'},
                   'available': available_updated}
        )

    def setUp(self):
        super(TestSetNetworkSegmentRange, self).setUp()

        self.network.find_extension = mock.Mock()
        self.network.find_network_segment_range = mock.Mock(
            return_value=self._network_segment_range
        )

        # Get the command object to test
        self.cmd = network_segment_range.SetNetworkSegmentRange(self.app,
                                                                self.namespace)

    def test_set_no_options(self):
        arglist = [
            self._network_segment_range.id,
        ]
        verifylist = [
            ('network_segment_range', self._network_segment_range.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.network.update_network_segment_range = mock.Mock(
            return_value=self._network_segment_range
        )
        result = self.cmd.take_action(parsed_args)

        self.network.update_network_segment_range.assert_called_once_with(
            self._network_segment_range, **{}
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        arglist = [
            '--name', 'new name',
            '--minimum', str(self.minimum_updated),
            '--maximum', str(self.maximum_updated),
            self._network_segment_range.id,
        ]
        verifylist = [
            ('name', 'new name'),
            ('minimum', self.minimum_updated),
            ('maximum', self.maximum_updated),
            ('network_segment_range', self._network_segment_range.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.network.update_network_segment_range = mock.Mock(
            return_value=self._network_segment_range_updated
        )
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': 'new name',
            'minimum': self.minimum_updated,
            'maximum': self.maximum_updated,
        }
        self.network.update_network_segment_range.assert_called_once_with(
            self._network_segment_range, **attrs
        )
        self.assertIsNone(result)


class TestShowNetworkSegmentRange(TestNetworkSegmentRange):

    # The network segment range to show.
    _network_segment_range = network_fakes.FakeNetworkSegmentRange.\
        create_one_network_segment_range()

    columns = (
        'available',
        'default',
        'id',
        'maximum',
        'minimum',
        'name',
        'network_type',
        'physical_network',
        'project_id',
        'shared',
        'used',
    )

    data = (
        ['100-103', '105'],
        _network_segment_range.default,
        _network_segment_range.id,
        _network_segment_range.maximum,
        _network_segment_range.minimum,
        _network_segment_range.name,
        _network_segment_range.network_type,
        _network_segment_range.physical_network,
        _network_segment_range.project_id,
        _network_segment_range.shared,
        {'3312e4ba67864b2eb53f3f41432f8efc': ['104', '106']},
    )

    def setUp(self):
        super(TestShowNetworkSegmentRange, self).setUp()

        self.network.find_extension = mock.Mock()
        self.network.find_network_segment_range = mock.Mock(
            return_value=self._network_segment_range
        )

        # Get the command object to test
        self.cmd = network_segment_range.ShowNetworkSegmentRange(
            self.app, self.namespace)

    def test_show_no_options(self):
        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, [], [])

    def test_show_all_options(self):
        arglist = [
            self._network_segment_range.id,
        ]
        verifylist = [
            ('network_segment_range', self._network_segment_range.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_network_segment_range.assert_called_once_with(
            self._network_segment_range.id,
            ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
