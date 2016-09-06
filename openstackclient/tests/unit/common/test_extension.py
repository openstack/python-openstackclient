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

from openstackclient.common import extension
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class TestExtension(utils.TestCommand):

    def setUp(self):
        super(TestExtension, self).setUp()

        identity_client = identity_fakes.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity_extensions_mock = identity_client.extensions
        self.identity_extensions_mock.reset_mock()

        compute_client = compute_fakes.FakeComputev2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.compute = compute_client
        compute_client.list_extensions = mock.Mock()
        self.compute_extensions_mock = compute_client.list_extensions
        self.compute_extensions_mock.reset_mock()

        volume_client = volume_fakes.FakeVolumeClient(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.volume = volume_client
        volume_client.list_extensions = mock.Mock()
        self.volume_extensions_mock = volume_client.list_extensions
        self.volume_extensions_mock.reset_mock()

        network_client = network_fakes.FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.network = network_client
        network_client.extensions = mock.Mock()
        self.network_extensions_mock = network_client.extensions
        self.network_extensions_mock.reset_mock()


class TestExtensionList(TestExtension):

    columns = ('Name', 'Alias', 'Description')
    long_columns = ('Name', 'Namespace', 'Description', 'Alias', 'Updated',
                    'Links')

    volume_extension = volume_fakes.FakeExtension.create_one_extension()
    identity_extension = identity_fakes.FakeExtension.create_one_extension()
    compute_extension = compute_fakes.FakeExtension.create_one_extension()
    network_extension = network_fakes.FakeExtension.create_one_extension()

    def setUp(self):
        super(TestExtensionList, self).setUp()

        self.identity_extensions_mock.list.return_value = [
            self.identity_extension]
        self.compute_extensions_mock.show_all.return_value = [
            self.compute_extension]
        self.volume_extensions_mock.show_all.return_value = [
            self.volume_extension]
        self.network_extensions_mock.return_value = [self.network_extension]

        # Get the command object to test
        self.cmd = extension.ListExtension(self.app, None)

    def _test_extension_list_helper(self, arglist, verifylist,
                                    expected_data, long=False):
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        if long:
            self.assertEqual(self.long_columns, columns)
        else:
            self.assertEqual(self.columns, columns)
        self.assertEqual(expected_data, tuple(data))

    def test_extension_list_no_options(self):
        arglist = []
        verifylist = []
        datalist = (
            (
                self.identity_extension.name,
                self.identity_extension.alias,
                self.identity_extension.description,
            ),
            (
                self.compute_extension.name,
                self.compute_extension.alias,
                self.compute_extension.description,
            ),
            (
                self.volume_extension.name,
                self.volume_extension.alias,
                self.volume_extension.description,
            ),
            (
                self.network_extension.name,
                self.network_extension.alias,
                self.network_extension.description,
            ),
        )
        self._test_extension_list_helper(arglist, verifylist, datalist)
        self.identity_extensions_mock.list.assert_called_with()
        self.compute_extensions_mock.show_all.assert_called_with()
        self.volume_extensions_mock.show_all.assert_called_with()
        self.network_extensions_mock.assert_called_with()

    def test_extension_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        datalist = (
            (
                self.identity_extension.name,
                self.identity_extension.namespace,
                self.identity_extension.description,
                self.identity_extension.alias,
                self.identity_extension.updated,
                self.identity_extension.links,
            ),
            (
                self.compute_extension.name,
                self.compute_extension.namespace,
                self.compute_extension.description,
                self.compute_extension.alias,
                self.compute_extension.updated,
                self.compute_extension.links,
            ),
            (
                self.volume_extension.name,
                self.volume_extension.namespace,
                self.volume_extension.description,
                self.volume_extension.alias,
                self.volume_extension.updated,
                self.volume_extension.links,
            ),
            (
                self.network_extension.name,
                self.network_extension.namespace,
                self.network_extension.description,
                self.network_extension.alias,
                self.network_extension.updated,
                self.network_extension.links,
            ),
        )
        self._test_extension_list_helper(arglist, verifylist, datalist, True)
        self.identity_extensions_mock.list.assert_called_with()
        self.compute_extensions_mock.show_all.assert_called_with()
        self.volume_extensions_mock.show_all.assert_called_with()
        self.network_extensions_mock.assert_called_with()

    def test_extension_list_identity(self):
        arglist = [
            '--identity',
        ]
        verifylist = [
            ('identity', True),
        ]
        datalist = ((
            self.identity_extension.name,
            self.identity_extension.alias,
            self.identity_extension.description,
        ), )
        self._test_extension_list_helper(arglist, verifylist, datalist)
        self.identity_extensions_mock.list.assert_called_with()

    def test_extension_list_network(self):
        arglist = [
            '--network',
        ]
        verifylist = [
            ('network', True),
        ]
        datalist = (
            (
                self.network_extension.name,
                self.network_extension.alias,
                self.network_extension.description,
            ),
        )
        self._test_extension_list_helper(arglist, verifylist, datalist)
        self.network_extensions_mock.assert_called_with()

    def test_extension_list_compute(self):
        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        datalist = ((
            self.compute_extension.name,
            self.compute_extension.alias,
            self.compute_extension.description,
        ), )
        self._test_extension_list_helper(arglist, verifylist, datalist)
        self.compute_extensions_mock.show_all.assert_called_with()

    def test_extension_list_volume(self):
        arglist = [
            '--volume',
        ]
        verifylist = [
            ('volume', True),
        ]
        datalist = ((
            self.volume_extension.name,
            self.volume_extension.alias,
            self.volume_extension.description,
        ), )
        self._test_extension_list_helper(arglist, verifylist, datalist)
        self.volume_extensions_mock.show_all.assert_called_with()
