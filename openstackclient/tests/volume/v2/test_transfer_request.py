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


from openstackclient.tests.volume.v2 import fakes as transfer_fakes
from openstackclient.volume.v2 import volume_transfer_request


class TestTransfer(transfer_fakes.TestTransfer):

    def setUp(self):
        super(TestTransfer, self).setUp()

        # Get a shortcut to the TransferManager Mock
        self.transfer_mock = self.app.client_manager.volume.transfers
        self.transfer_mock.reset_mock()


class TestTransferList(TestTransfer):

    # The Transfers to be listed
    volume_transfers = transfer_fakes.FakeTransfer.create_one_transfer()

    def setUp(self):
        super(TestTransferList, self).setUp()

        self.transfer_mock.list.return_value = [self.volume_transfers]

        # Get the command object to test
        self.cmd = volume_transfer_request.ListTransferRequests(self.app, None)

    def test_transfer_list_without_argument(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'ID',
            'Volume',
            'Name',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = ((
            self.volume_transfers.id,
            self.volume_transfers.volume_id,
            self.volume_transfers.name,
        ), )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list volume_transfers
        self.transfer_mock.list.assert_called_with(
            detailed=True,
            search_opts={'all_tenants': 0}
        )

    def test_transfer_list_with_argument(self):
        arglist = [
            "--all-projects"
        ]
        verifylist = [
            ("all_projects", True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'ID',
            'Volume',
            'Name',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = ((
            self.volume_transfers.id,
            self.volume_transfers.volume_id,
            self.volume_transfers.name,
        ), )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list volume_transfers
        self.transfer_mock.list.assert_called_with(
            detailed=True,
            search_opts={'all_tenants': 1}
        )
