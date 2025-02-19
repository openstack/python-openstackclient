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

from unittest import mock
from unittest.mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import utils as test_utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_transfer_request


class TestTransfer(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the TransferManager Mock
        self.transfer_mock = self.volume_client.transfers
        self.transfer_mock.reset_mock()

        # Get a shortcut to the VolumeManager Mock
        self.volumes_mock = self.volume_client.volumes
        self.volumes_mock.reset_mock()


class TestTransferAccept(TestTransfer):
    columns = (
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume_transfer = volume_fakes.create_one_transfer()
        self.data = (
            self.volume_transfer.id,
            self.volume_transfer.name,
            self.volume_transfer.volume_id,
        )

        self.transfer_mock.get.return_value = self.volume_transfer
        self.transfer_mock.accept.return_value = self.volume_transfer

        # Get the command object to test
        self.cmd = volume_transfer_request.AcceptTransferRequest(
            self.app, None
        )

    def test_transfer_accept(self):
        arglist = [
            '--auth-key',
            'key_value',
            self.volume_transfer.id,
        ]
        verifylist = [
            ('transfer_request', self.volume_transfer.id),
            ('auth_key', 'key_value'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.transfer_mock.get.assert_called_once_with(
            self.volume_transfer.id,
        )
        self.transfer_mock.accept.assert_called_once_with(
            self.volume_transfer.id,
            'key_value',
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_accept_no_option(self):
        arglist = [
            self.volume_transfer.id,
        ]
        verifylist = [
            ('transfer_request', self.volume_transfer.id),
        ]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestTransferCreate(TestTransfer):
    volume = volume_fakes.create_one_volume()

    columns = (
        'auth_key',
        'created_at',
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume_transfer = volume_fakes.create_one_transfer(
            attrs={
                'volume_id': self.volume.id,
                'auth_key': 'key',
                'created_at': 'time',
            },
        )
        self.data = (
            self.volume_transfer.auth_key,
            self.volume_transfer.created_at,
            self.volume_transfer.id,
            self.volume_transfer.name,
            self.volume_transfer.volume_id,
        )

        self.transfer_mock.create.return_value = self.volume_transfer
        self.volumes_mock.get.return_value = self.volume

        # Get the command object to test
        self.cmd = volume_transfer_request.CreateTransferRequest(
            self.app, None
        )

    def test_transfer_create_without_name(self):
        arglist = [
            self.volume.id,
        ]
        verifylist = [
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.transfer_mock.create.assert_called_once_with(self.volume.id, None)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_create_with_name(self):
        arglist = [
            '--name',
            self.volume_transfer.name,
            self.volume.id,
        ]
        verifylist = [
            ('name', self.volume_transfer.name),
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.transfer_mock.create.assert_called_once_with(
            self.volume.id,
            self.volume_transfer.name,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestTransferDelete(TestTransfer):
    volume_transfers = volume_fakes.create_transfers(count=2)

    def setUp(self):
        super().setUp()

        self.transfer_mock.get = volume_fakes.get_transfers(
            self.volume_transfers,
        )
        self.transfer_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_transfer_request.DeleteTransferRequest(
            self.app, None
        )

    def test_transfer_delete(self):
        arglist = [self.volume_transfers[0].id]
        verifylist = [("transfer_request", [self.volume_transfers[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.transfer_mock.delete.assert_called_with(
            self.volume_transfers[0].id
        )
        self.assertIsNone(result)

    def test_delete_multiple_transfers(self):
        arglist = []
        for v in self.volume_transfers:
            arglist.append(v.id)
        verifylist = [
            ('transfer_request', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for v in self.volume_transfers:
            calls.append(call(v.id))
        self.transfer_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_transfers_with_exception(self):
        arglist = [
            self.volume_transfers[0].id,
            'unexist_transfer',
        ]
        verifylist = [
            ('transfer_request', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.volume_transfers[0], exceptions.CommandError]
        with mock.patch.object(
            utils, 'find_resource', side_effect=find_mock_result
        ) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual(
                    '1 of 2 volume transfer requests failed to delete',
                    str(e),
                )

            find_mock.assert_any_call(
                self.transfer_mock, self.volume_transfers[0].id
            )
            find_mock.assert_any_call(self.transfer_mock, 'unexist_transfer')

            self.assertEqual(2, find_mock.call_count)
            self.transfer_mock.delete.assert_called_once_with(
                self.volume_transfers[0].id,
            )


class TestTransferList(TestTransfer):
    # The Transfers to be listed
    volume_transfers = volume_fakes.create_one_transfer()

    def setUp(self):
        super().setUp()

        self.transfer_mock.list.return_value = [self.volume_transfers]

        # Get the command object to test
        self.cmd = volume_transfer_request.ListTransferRequest(self.app, None)

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
            'Name',
            'Volume',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = (
            (
                self.volume_transfers.id,
                self.volume_transfers.name,
                self.volume_transfers.volume_id,
            ),
        )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list volume_transfers
        self.transfer_mock.list.assert_called_with(
            detailed=True, search_opts={'all_tenants': 0}
        )

    def test_transfer_list_with_argument(self):
        arglist = ["--all-projects"]
        verifylist = [("all_projects", True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'ID',
            'Name',
            'Volume',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = (
            (
                self.volume_transfers.id,
                self.volume_transfers.name,
                self.volume_transfers.volume_id,
            ),
        )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to list volume_transfers
        self.transfer_mock.list.assert_called_with(
            detailed=True, search_opts={'all_tenants': 1}
        )


class TestTransferShow(TestTransfer):
    columns = (
        'created_at',
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume_transfer = volume_fakes.create_one_transfer(
            attrs={'created_at': 'time'},
        )
        self.data = (
            self.volume_transfer.created_at,
            self.volume_transfer.id,
            self.volume_transfer.name,
            self.volume_transfer.volume_id,
        )

        self.transfer_mock.get.return_value = self.volume_transfer

        # Get the command object to test
        self.cmd = volume_transfer_request.ShowTransferRequest(self.app, None)

    def test_transfer_show(self):
        arglist = [
            self.volume_transfer.id,
        ]
        verifylist = [
            ('transfer_request', self.volume_transfer.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.transfer_mock.get.assert_called_once_with(self.volume_transfer.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
