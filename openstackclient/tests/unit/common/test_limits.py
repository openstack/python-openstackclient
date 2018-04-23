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

from openstackclient.common import limits
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class TestComputeLimits(compute_fakes.TestComputev2):

    absolute_columns = [
        'Name',
        'Value',
    ]

    rate_columns = [
        "Verb",
        "URI",
        "Value",
        "Remain",
        "Unit",
        "Next Available"
    ]

    def setUp(self):
        super(TestComputeLimits, self).setUp()
        self.app.client_manager.volume_endpoint_enabled = False
        self.compute = self.app.client_manager.compute

        self.fake_limits = compute_fakes.FakeLimits()
        self.compute.limits.get.return_value = self.fake_limits

    def test_compute_show_absolute(self):
        arglist = ['--absolute']
        verifylist = [('is_absolute', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        ret_limits = list(data)
        compute_reference_limits = self.fake_limits.absolute_limits()

        self.assertEqual(self.absolute_columns, columns)
        self.assertEqual(compute_reference_limits, ret_limits)
        self.assertEqual(19, len(ret_limits))

    def test_compute_show_rate(self):
        arglist = ['--rate']
        verifylist = [('is_rate', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        ret_limits = list(data)
        compute_reference_limits = self.fake_limits.rate_limits()

        self.assertEqual(self.rate_columns, columns)
        self.assertEqual(compute_reference_limits, ret_limits)
        self.assertEqual(3, len(ret_limits))


class TestVolumeLimits(volume_fakes.TestVolume):
    absolute_columns = [
        'Name',
        'Value',
    ]

    rate_columns = [
        "Verb",
        "URI",
        "Value",
        "Remain",
        "Unit",
        "Next Available"
    ]

    def setUp(self):
        super(TestVolumeLimits, self).setUp()
        self.app.client_manager.compute_endpoint_enabled = False
        self.volume = self.app.client_manager.volume

        self.fake_limits = volume_fakes.FakeLimits()
        self.volume.limits.get.return_value = self.fake_limits

    def test_volume_show_absolute(self):
        arglist = ['--absolute']
        verifylist = [('is_absolute', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        ret_limits = list(data)
        compute_reference_limits = self.fake_limits.absolute_limits()

        self.assertEqual(self.absolute_columns, columns)
        self.assertEqual(compute_reference_limits, ret_limits)
        self.assertEqual(10, len(ret_limits))

    def test_volume_show_rate(self):
        arglist = ['--rate']
        verifylist = [('is_rate', True)]
        cmd = limits.ShowLimits(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        ret_limits = list(data)
        compute_reference_limits = self.fake_limits.rate_limits()

        self.assertEqual(self.rate_columns, columns)
        self.assertEqual(compute_reference_limits, ret_limits)
        self.assertEqual(3, len(ret_limits))
