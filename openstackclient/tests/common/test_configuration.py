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

from openstackclient.common import configuration
from openstackclient.tests import fakes
from openstackclient.tests import utils


class TestConfiguration(utils.TestCommand):

    def test_show(self):
        arglist = []
        verifylist = [('mask', True)]
        cmd = configuration.ShowConfiguration(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        collist = ('auth.password', 'auth.token', 'auth.username',
                   'identity_api_version', 'region')
        self.assertEqual(collist, columns)
        datalist = (
            configuration.REDACTED,
            configuration.REDACTED,
            fakes.USERNAME,
            fakes.VERSION,
            fakes.REGION_NAME,
        )
        self.assertEqual(datalist, tuple(data))

    def test_show_unmask(self):
        arglist = ['--unmask']
        verifylist = [('mask', False)]
        cmd = configuration.ShowConfiguration(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        collist = ('auth.password', 'auth.token', 'auth.username',
                   'identity_api_version', 'region')
        self.assertEqual(collist, columns)
        datalist = (
            fakes.PASSWORD,
            fakes.AUTH_TOKEN,
            fakes.USERNAME,
            fakes.VERSION,
            fakes.REGION_NAME,
        )
        self.assertEqual(datalist, tuple(data))

    def test_show_mask(self):
        arglist = ['--mask']
        verifylist = [('mask', True)]
        cmd = configuration.ShowConfiguration(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        collist = ('auth.password', 'auth.token', 'auth.username',
                   'identity_api_version', 'region')
        self.assertEqual(collist, columns)
        datalist = (
            configuration.REDACTED,
            configuration.REDACTED,
            fakes.USERNAME,
            fakes.VERSION,
            fakes.REGION_NAME,
        )
        self.assertEqual(datalist, tuple(data))
