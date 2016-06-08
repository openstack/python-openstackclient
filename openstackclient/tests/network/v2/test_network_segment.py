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

from osc_lib import exceptions

from openstackclient.network.v2 import network_segment
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestNetworkSegment(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkSegment, self).setUp()

        # Enable beta commands.
        self.app.options.os_beta_command = True

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestListNetworkSegment(TestNetworkSegment):
    _network = network_fakes.FakeNetwork.create_one_network()
    _network_segments = \
        network_fakes.FakeNetworkSegment.create_network_segments(count=3)

    columns = (
        'ID',
        'Network',
        'Network Type',
        'Segment',
    )
    columns_long = columns + (
        'Physical Network',
    )

    data = []
    for _network_segment in _network_segments:
        data.append((
            _network_segment.id,
            _network_segment.network_id,
            _network_segment.network_type,
            _network_segment.segmentation_id,
        ))

    data_long = []
    for _network_segment in _network_segments:
        data_long.append((
            _network_segment.id,
            _network_segment.network_id,
            _network_segment.network_type,
            _network_segment.segmentation_id,
            _network_segment.physical_network,
        ))

    def setUp(self):
        super(TestListNetworkSegment, self).setUp()

        # Get the command object to test
        self.cmd = network_segment.ListNetworkSegment(self.app, self.namespace)

        self.network.find_network = mock.Mock(return_value=self._network)
        self.network.segments = mock.Mock(return_value=self._network_segments)

    def test_list_no_option(self):
        arglist = []
        verifylist = [
            ('long', False),
            ('network', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.segments.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_list_no_beta_commands(self):
        self.app.options.os_beta_command = False
        parsed_args = self.check_parser(self.cmd, [], [])
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

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

        self.network.segments.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_list_network(self):
        arglist = [
            '--network',
            self._network.id,
        ]
        verifylist = [
            ('long', False),
            ('network', self._network.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network.segments.assert_called_once_with(
            **{'network_id': self._network.id}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowNetworkSegment(TestNetworkSegment):

    # The network segment to show.
    _network_segment = \
        network_fakes.FakeNetworkSegment.create_one_network_segment()

    columns = (
        'id',
        'network_id',
        'network_type',
        'physical_network',
        'segmentation_id',
    )

    data = (
        _network_segment.id,
        _network_segment.network_id,
        _network_segment.network_type,
        _network_segment.physical_network,
        _network_segment.segmentation_id,
    )

    def setUp(self):
        super(TestShowNetworkSegment, self).setUp()

        self.network.find_segment = mock.Mock(
            return_value=self._network_segment
        )

        # Get the command object to test
        self.cmd = network_segment.ShowNetworkSegment(self.app, self.namespace)

    def test_show_no_options(self):
        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, [], [])

    def test_show_no_beta_commands(self):
        arglist = [
            self._network_segment.id,
        ]
        verifylist = [
            ('network_segment', self._network_segment.id),
        ]
        self.app.options.os_beta_command = False
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_show_all_options(self):
        arglist = [
            self._network_segment.id,
        ]
        verifylist = [
            ('network_segment', self._network_segment.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_segment.assert_called_once_with(
            self._network_segment.id,
            ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
