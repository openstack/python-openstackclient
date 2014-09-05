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

"""Test Timing pseudo-command"""

import datetime

from openstackclient.common import timing
from openstackclient.tests import fakes
from openstackclient.tests import utils


timing_url = 'GET http://localhost:5000'
timing_elapsed = 0.872809


class FakeGenericClient(object):

    def __init__(self, **kwargs):
        self.auth_token = kwargs['token']
        self.management_url = kwargs['endpoint']


class TestTiming(utils.TestCommand):

    def setUp(self):
        super(TestTiming, self).setUp()

        self.app.timing_data = []

        self.app.client_manager.compute = FakeGenericClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        self.app.client_manager.volume = FakeGenericClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )

        # Get the command object to test
        self.cmd = timing.Timing(self.app, None)

    def test_timing_list_no_data(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('URL', 'Seconds')
        self.assertEqual(collist, columns)
        datalist = [
            ('Total', 0.0,)
        ]
        self.assertEqual(datalist, data)

    def test_timing_list(self):
        self.app.timing_data = [(
            timing_url,
            datetime.timedelta(microseconds=timing_elapsed*1000000),
        )]

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('URL', 'Seconds')
        self.assertEqual(collist, columns)
        datalist = [
            (timing_url, timing_elapsed),
            ('Total', timing_elapsed),
        ]
        self.assertEqual(datalist, data)
