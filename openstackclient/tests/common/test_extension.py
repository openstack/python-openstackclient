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

import copy

from openstackclient.common import extension
from openstackclient.tests import fakes
from openstackclient.tests import utils

from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes


class TestExtension(utils.TestCommand):

    def setUp(self):
        super(TestExtension, self).setUp()

        self.app.client_manager.identity = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.identity_extensions_mock = (
            self.app.client_manager.identity.extensions)
        self.identity_extensions_mock.reset_mock()

        network = network_fakes.FakeNetworkV2Client()
        self.app.client_manager.network = network
        self.network_extensions_mock = network.list_extensions
        self.network_extensions_mock.reset_mock()


class TestExtensionList(TestExtension):

    def setUp(self):
        super(TestExtensionList, self).setUp()

        self.identity_extensions_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.EXTENSION),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = extension.ListExtension(self.app, None)

    def test_extension_list_no_options(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # no args should output from all services
        self.identity_extensions_mock.list.assert_called_with()

        collist = ('Name', 'Alias', 'Description')
        self.assertEqual(collist, columns)
        datalist = (
            (
                identity_fakes.extension_name,
                identity_fakes.extension_alias,
                identity_fakes.extension_description,
            ),
            (
                network_fakes.extension_name,
                network_fakes.extension_alias,
                network_fakes.extension_description,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_extension_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # no args should output from all services
        self.identity_extensions_mock.list.assert_called_with()

        collist = ('Name', 'Namespace', 'Description', 'Alias', 'Updated',
                   'Links')
        self.assertEqual(collist, columns)
        datalist = (
            (
                identity_fakes.extension_name,
                identity_fakes.extension_namespace,
                identity_fakes.extension_description,
                identity_fakes.extension_alias,
                identity_fakes.extension_updated,
                identity_fakes.extension_links,
            ),
            (
                network_fakes.extension_name,
                network_fakes.extension_namespace,
                network_fakes.extension_description,
                network_fakes.extension_alias,
                network_fakes.extension_updated,
                network_fakes.extension_links,
            ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_extension_list_identity(self):
        arglist = [
            '--identity',
        ]
        verifylist = [
            ('identity', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.identity_extensions_mock.list.assert_called_with()

        collist = ('Name', 'Alias', 'Description')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.extension_name,
            identity_fakes.extension_alias,
            identity_fakes.extension_description,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_extension_list_network(self):
        arglist = [
            '--network',
        ]
        verifylist = [
            ('network', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.network_extensions_mock.assert_called_with()

        collist = ('Name', 'Alias', 'Description')
        self.assertEqual(collist, columns)
        datalist = (
            (
                network_fakes.extension_name,
                network_fakes.extension_alias,
                network_fakes.extension_description,
            ),
        )
        self.assertEqual(datalist, tuple(data))
