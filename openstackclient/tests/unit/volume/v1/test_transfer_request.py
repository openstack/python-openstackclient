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

from openstackclient.tests.unit.volume.v1 import fakes as transfer_fakes
from openstackclient.volume.v1 import volume_transfer_request


class TestTransfer(transfer_fakes.TestVolumev1):

    def setUp(self):
        super(TestTransfer, self).setUp()

        # Get a shortcut to the TransferManager Mock
        self.transfer_mock = self.app.client_manager.volume.transfers
        self.transfer_mock.reset_mock()

        # Get a shortcut to the VolumeManager Mock
        self.volumes_mock = self.app.client_manager.volume.volumes
        self.volumes_mock.reset_mock()


class TestTransferCreate(TestTransfer):

    volume = transfer_fakes.FakeVolume.create_one_volume()

    columns = (
        'auth_key',
        'created_at',
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super(TestTransferCreate, self).setUp()

        self.volume_transfer = transfer_fakes.FakeTransfer.create_one_transfer(
            attrs={'volume_id': self.volume.id})
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
            self.app, None)

    def test_transfer_create_without_name(self):
        arglist = [
            self.volume.id,
        ]
        verifylist = [
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.transfer_mock.create.assert_called_once_with(
            self.volume.id, None)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_create_with_name(self):
        arglist = [
            '--name', self.volume_transfer.name,
            self.volume.id,
        ]
        verifylist = [
            ('name', self.volume_transfer.name),
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.transfer_mock.create.assert_called_once_with(
            self.volume.id, self.volume_transfer.name,)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


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
