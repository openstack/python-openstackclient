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

from osc_lib import exceptions

from openstackclient.network.v2 import network_segment
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkSegment(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()


class TestCreateNetworkSegment(TestNetworkSegment):
    # The network segment to create along with associated network.
    _network_segment = network_fakes.create_one_network_segment()
    _network = network_fakes.create_one_network(
        {
            'id': _network_segment.network_id,
        }
    )

    columns = (
        'description',
        'id',
        'name',
        'network_id',
        'network_type',
        'physical_network',
        'segmentation_id',
    )

    data = (
        _network_segment.description,
        _network_segment.id,
        _network_segment.name,
        _network_segment.network_id,
        _network_segment.network_type,
        _network_segment.physical_network,
        _network_segment.segmentation_id,
    )

    def setUp(self):
        super().setUp()

        self.network_client.create_segment = mock.Mock(
            return_value=self._network_segment
        )
        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )

        # Get the command object to test
        self.cmd = network_segment.CreateNetworkSegment(self.app, None)

    def test_create_no_options(self):
        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_create_invalid_network_type(self):
        arglist = [
            '--network',
            self._network_segment.network_id,
            '--network-type',
            'foo',
            self._network_segment.name,
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_create_minimum_options(self):
        arglist = [
            '--network',
            self._network_segment.network_id,
            '--network-type',
            self._network_segment.network_type,
            self._network_segment.name,
        ]
        verifylist = [
            ('network', self._network_segment.network_id),
            ('network_type', self._network_segment.network_type),
            ('name', self._network_segment.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_called_once_with(
            self._network_segment.network_id, ignore_missing=False
        )
        self.network_client.create_segment.assert_called_once_with(
            **{
                'network_id': self._network_segment.network_id,
                'network_type': self._network_segment.network_type,
                'name': self._network_segment.name,
            }
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description',
            self._network_segment.description,
            '--network',
            self._network_segment.network_id,
            '--network-type',
            self._network_segment.network_type,
            '--physical-network',
            self._network_segment.physical_network,
            '--segment',
            str(self._network_segment.segmentation_id),
            self._network_segment.name,
        ]
        verifylist = [
            ('description', self._network_segment.description),
            ('network', self._network_segment.network_id),
            ('network_type', self._network_segment.network_type),
            ('physical_network', self._network_segment.physical_network),
            ('segment', self._network_segment.segmentation_id),
            ('name', self._network_segment.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_network.assert_called_once_with(
            self._network_segment.network_id, ignore_missing=False
        )
        self.network_client.create_segment.assert_called_once_with(
            **{
                'description': self._network_segment.description,
                'network_id': self._network_segment.network_id,
                'network_type': self._network_segment.network_type,
                'physical_network': self._network_segment.physical_network,
                'segmentation_id': self._network_segment.segmentation_id,
                'name': self._network_segment.name,
            }
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkSegment(TestNetworkSegment):
    # The network segments to delete.
    _network_segments = network_fakes.create_network_segments()

    def setUp(self):
        super().setUp()

        self.network_client.delete_segment = mock.Mock(return_value=None)
        self.network_client.find_segment = mock.Mock(
            side_effect=self._network_segments
        )

        # Get the command object to test
        self.cmd = network_segment.DeleteNetworkSegment(self.app, None)

    def test_delete(self):
        arglist = [
            self._network_segments[0].id,
        ]
        verifylist = [
            ('network_segment', [self._network_segments[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_segment.assert_called_once_with(
            self._network_segments[0]
        )
        self.assertIsNone(result)

    def test_delete_multiple(self):
        arglist = []
        for _network_segment in self._network_segments:
            arglist.append(_network_segment.id)
        verifylist = [
            ('network_segment', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for _network_segment in self._network_segments:
            calls.append(call(_network_segment))
        self.network_client.delete_segment.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_with_exception(self):
        arglist = [self._network_segments[0].id, 'doesnotexist']
        verifylist = [
            (
                'network_segment',
                [self._network_segments[0].id, 'doesnotexist'],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._network_segments[0], exceptions.CommandError]
        self.network_client.find_segment = mock.Mock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 network segments failed to delete.', str(e)
            )

        self.network_client.find_segment.assert_any_call(
            self._network_segments[0].id, ignore_missing=False
        )
        self.network_client.find_segment.assert_any_call(
            'doesnotexist', ignore_missing=False
        )
        self.network_client.delete_segment.assert_called_once_with(
            self._network_segments[0]
        )


class TestListNetworkSegment(TestNetworkSegment):
    _network = network_fakes.create_one_network()
    _network_segments = network_fakes.create_network_segments(count=3)

    columns = (
        'ID',
        'Name',
        'Network',
        'Network Type',
        'Segment',
    )
    columns_long = columns + ('Physical Network',)

    data = []
    for _network_segment in _network_segments:
        data.append(
            (
                _network_segment.id,
                _network_segment.name,
                _network_segment.network_id,
                _network_segment.network_type,
                _network_segment.segmentation_id,
            )
        )

    data_long = []
    for _network_segment in _network_segments:
        data_long.append(
            (
                _network_segment.id,
                _network_segment.name,
                _network_segment.network_id,
                _network_segment.network_type,
                _network_segment.segmentation_id,
                _network_segment.physical_network,
            )
        )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = network_segment.ListNetworkSegment(self.app, None)

        self.network_client.find_network = mock.Mock(
            return_value=self._network
        )
        self.network_client.segments = mock.Mock(
            return_value=self._network_segments
        )

    def test_list_no_option(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('network', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.segments.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('network', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.segments.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_list_network(self):
        arglist = [
            '--network',
            self._network.id,
        ]
        verifylist = [('long', False), ('network', self._network.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.segments.assert_called_once_with(
            **{'network_id': self._network.id}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestSetNetworkSegment(TestNetworkSegment):
    # The network segment to show.
    _network_segment = network_fakes.create_one_network_segment()

    def setUp(self):
        super().setUp()

        self.network_client.find_segment = mock.Mock(
            return_value=self._network_segment
        )
        self.network_client.update_segment = mock.Mock(
            return_value=self._network_segment
        )

        # Get the command object to test
        self.cmd = network_segment.SetNetworkSegment(self.app, None)

    def test_set_no_options(self):
        arglist = [
            self._network_segment.id,
        ]
        verifylist = [
            ('network_segment', self._network_segment.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_segment.assert_called_once_with(
            self._network_segment, **{}
        )
        self.assertIsNone(result)

    def test_set_all_options(self):
        arglist = [
            '--description',
            'new description',
            '--name',
            'new name',
            self._network_segment.id,
        ]
        verifylist = [
            ('description', 'new description'),
            ('name', 'new name'),
            ('network_segment', self._network_segment.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {
            'description': 'new description',
            'name': 'new name',
        }
        self.network_client.update_segment.assert_called_once_with(
            self._network_segment, **attrs
        )
        self.assertIsNone(result)


class TestShowNetworkSegment(TestNetworkSegment):
    # The network segment to show.
    _network_segment = network_fakes.create_one_network_segment()

    columns = (
        'description',
        'id',
        'name',
        'network_id',
        'network_type',
        'physical_network',
        'segmentation_id',
    )

    data = (
        _network_segment.description,
        _network_segment.id,
        _network_segment.name,
        _network_segment.network_id,
        _network_segment.network_type,
        _network_segment.physical_network,
        _network_segment.segmentation_id,
    )

    def setUp(self):
        super().setUp()

        self.network_client.find_segment = mock.Mock(
            return_value=self._network_segment
        )

        # Get the command object to test
        self.cmd = network_segment.ShowNetworkSegment(self.app, None)

    def test_show_no_options(self):
        # Missing required args should bail here
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_show_all_options(self):
        arglist = [
            self._network_segment.id,
        ]
        verifylist = [
            ('network_segment', self._network_segment.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_segment.assert_called_once_with(
            self._network_segment.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
