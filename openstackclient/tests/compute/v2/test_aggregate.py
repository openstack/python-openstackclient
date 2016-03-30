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

from openstackclient.compute.v2 import aggregate
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import utils as tests_utils


class TestAggregate(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestAggregate, self).setUp()

        # Get a shortcut to the AggregateManager Mock
        self.aggregate_mock = self.app.client_manager.compute.aggregates
        self.aggregate_mock.reset_mock()


class TestAggregateUnset(TestAggregate):

    fake_ag = compute_fakes.FakeAggregate.create_one_aggregate()

    def setUp(self):
        super(TestAggregateUnset, self).setUp()

        self.aggregate_mock.get.return_value = self.fake_ag
        self.cmd = aggregate.UnsetAggregate(self.app, None)

    def test_aggregate_unset(self):
        arglist = [
            '--property', 'unset_key',
            'ag1'
        ]
        verifylist = [
            ('property', ['unset_key']),
            ('aggregate', 'ag1')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.aggregate_mock.set_metadata.assert_called_once_with(
            self.fake_ag, {'unset_key': None})
        self.assertIsNone(result)

    def test_aggregate_unset_no_property(self):
        arglist = [
            'ag1'
        ]
        verifylist = None
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)
