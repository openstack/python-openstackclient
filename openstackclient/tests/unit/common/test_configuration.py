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

from openstackclient.common import configuration
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit import utils


class TestConfiguration(utils.TestCommand):
    columns = (
        'auth.password',
        'auth.token',
        'auth.username',
        'identity_api_version',
        'region',
    )
    datalist = (
        configuration.REDACTED,
        configuration.REDACTED,
        fakes.USERNAME,
        fakes.VERSION,
        fakes.REGION_NAME,
    )

    opts = [
        mock.Mock(secret=True, dest="password"),
        mock.Mock(secret=True, dest="token"),
    ]

    @mock.patch(
        "keystoneauth1.loading.base.get_plugin_options", return_value=opts
    )
    def test_show(self, m_get_plugin_opts):
        arglist = []
        verifylist = [('mask', True)]
        cmd = configuration.ShowConfiguration(self.app, None)
        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch(
        "keystoneauth1.loading.base.get_plugin_options", return_value=opts
    )
    def test_show_unmask(self, m_get_plugin_opts):
        arglist = ['--unmask']
        verifylist = [('mask', False)]
        cmd = configuration.ShowConfiguration(self.app, None)

        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        datalist = (
            fakes.PASSWORD,
            fakes.AUTH_TOKEN,
            fakes.USERNAME,
            fakes.VERSION,
            fakes.REGION_NAME,
        )
        self.assertEqual(datalist, data)

    @mock.patch(
        "keystoneauth1.loading.base.get_plugin_options", return_value=opts
    )
    def test_show_mask_with_cloud_config(self, m_get_plugin_opts):
        arglist = ['--mask']
        verifylist = [('mask', True)]
        self.app.client_manager.configuration_type = "cloud_config"
        cmd = configuration.ShowConfiguration(self.app, None)

        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    @mock.patch(
        "keystoneauth1.loading.base.get_plugin_options", return_value=opts
    )
    def test_show_mask_with_global_env(self, m_get_plugin_opts):
        arglist = ['--mask']
        verifylist = [('mask', True)]
        self.app.client_manager.configuration_type = "global_env"
        column_list = (
            'identity_api_version',
            'password',
            'region',
            'token',
            'username',
        )
        datalist = (
            fakes.VERSION,
            configuration.REDACTED,
            fakes.REGION_NAME,
            configuration.REDACTED,
            fakes.USERNAME,
        )

        cmd = configuration.ShowConfiguration(self.app, None)

        parsed_args = self.check_parser(cmd, arglist, verifylist)

        columns, data = cmd.take_action(parsed_args)

        self.assertEqual(column_list, columns)
        self.assertEqual(datalist, data)
