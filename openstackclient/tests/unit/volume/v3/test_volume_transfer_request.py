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

from unittest.mock import call

from openstack.block_storage.v3 import transfer as _transfer
from openstack.block_storage.v3 import volume as _volume
from openstack import exceptions as sdk_exceptions
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit import utils as test_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_transfer_request


class TestTransferAccept(volume_fakes.TestVolume):
    columns = (
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume_transfer = sdk_fakes.generate_fake_resource(
            _transfer.Transfer
        )
        self.data = (
            self.volume_transfer.id,
            self.volume_transfer.name,
            self.volume_transfer.volume_id,
        )

        self.volume_sdk_client.find_transfer.return_value = (
            self.volume_transfer
        )
        self.volume_sdk_client.accept_transfer.return_value = (
            self.volume_transfer
        )

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

        self.volume_sdk_client.find_transfer.assert_called_once_with(
            self.volume_transfer.id, ignore_missing=False
        )
        self.volume_sdk_client.accept_transfer.assert_called_once_with(
            self.volume_transfer.id,
            'key_value',
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_accept_non_admin(self):
        """Non-admin users get ResourceNotFound on find_transfer; we fall back."""
        self.volume_sdk_client.find_transfer.side_effect = (
            sdk_exceptions.ResourceNotFound
        )
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

        self.volume_sdk_client.accept_transfer.assert_called_once_with(
            self.volume_transfer.id,
            'key_value',
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_accept_no_option(self):
        arglist = [self.volume_transfer.id]
        verifylist = [('transfer_request', self.volume_transfer.id)]

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


class TestTransferCreate(volume_fakes.TestVolume):
    columns = (
        'auth_key',
        'created_at',
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume = sdk_fakes.generate_fake_resource(_volume.Volume)
        self.volume_transfer = sdk_fakes.generate_fake_resource(
            _transfer.Transfer, volume_id=self.volume.id
        )
        self.data = (
            self.volume_transfer.auth_key,
            self.volume_transfer.created_at,
            self.volume_transfer.id,
            self.volume_transfer.name,
            self.volume_transfer.volume_id,
        )

        self.volume_sdk_client.find_volume.return_value = self.volume
        self.volume_sdk_client.create_transfer.return_value = (
            self.volume_transfer
        )

        self.cmd = volume_transfer_request.CreateTransferRequest(
            self.app, None
        )

    def test_transfer_create_without_name(self):
        arglist = [self.volume.id]
        verifylist = [('volume', self.volume.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_transfer.assert_called_once_with(
            volume_id=self.volume.id,
            name=None,
        )
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

        self.volume_sdk_client.create_transfer.assert_called_once_with(
            volume_id=self.volume.id,
            name=self.volume_transfer.name,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_create_with_no_snapshots(self):
        self.set_volume_api_version('3.55')

        arglist = [
            '--no-snapshots',
            self.volume.id,
        ]
        verifylist = [
            ('name', None),
            ('snapshots', False),
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_transfer.assert_called_once_with(
            volume_id=self.volume.id,
            name=None,
            no_snapshots=True,
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_transfer_create_pre_v355(self):
        self.set_volume_api_version('3.54')

        arglist = [
            '--no-snapshots',
            self.volume.id,
        ]
        verifylist = [
            ('name', None),
            ('snapshots', False),
            ('volume', self.volume.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.55 or greater is required', str(exc)
        )


class TestTransferDelete(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_transfers = [
            sdk_fakes.generate_fake_resource(_transfer.Transfer),
            sdk_fakes.generate_fake_resource(_transfer.Transfer),
        ]
        self.volume_sdk_client.delete_transfer.return_value = None

        self.cmd = volume_transfer_request.DeleteTransferRequest(
            self.app, None
        )

    def test_transfer_delete(self):
        arglist = [self.volume_transfers[0].id]
        verifylist = [("transfer_request", [self.volume_transfers[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_transfer.assert_called_once_with(
            self.volume_transfers[0].id, ignore_missing=False
        )
        self.assertIsNone(result)

    def test_delete_multiple_transfers(self):
        arglist = [v.id for v in self.volume_transfers]
        verifylist = [('transfer_request', arglist)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = [
            call(v.id, ignore_missing=False) for v in self.volume_transfers
        ]
        self.volume_sdk_client.delete_transfer.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_transfers_with_exception(self):
        arglist = [
            self.volume_transfers[0].id,
            'unexist_transfer',
        ]
        verifylist = [('transfer_request', arglist)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.volume_sdk_client.delete_transfer.side_effect = [
            None,
            exceptions.CommandError,
        ]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 volume transfer requests failed to delete',
                str(e),
            )


class TestTransferList(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_transfers = [
            sdk_fakes.generate_fake_resource(_transfer.Transfer),
        ]
        self.volume_sdk_client.transfers.return_value = self.volume_transfers

        self.cmd = volume_transfer_request.ListTransferRequest(self.app, None)

    def test_transfer_list_without_argument(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.transfers.assert_called_once_with(
            details=True, all_projects=False
        )
        self.assertEqual(('ID', 'Name', 'Volume'), columns)
        self.assertEqual(
            (
                (
                    self.volume_transfers[0].id,
                    self.volume_transfers[0].name,
                    self.volume_transfers[0].volume_id,
                ),
            ),
            tuple(data),
        )

    def test_transfer_list_with_argument(self):
        arglist = ["--all-projects"]
        verifylist = [("all_projects", True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, _data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.transfers.assert_called_once_with(
            details=True, all_projects=True
        )
        self.assertEqual(('ID', 'Name', 'Volume'), columns)


class TestTransferShow(volume_fakes.TestVolume):
    columns = (
        'created_at',
        'id',
        'name',
        'volume_id',
    )

    def setUp(self):
        super().setUp()

        self.volume_transfer = sdk_fakes.generate_fake_resource(
            _transfer.Transfer
        )
        self.data = (
            self.volume_transfer.created_at,
            self.volume_transfer.id,
            self.volume_transfer.name,
            self.volume_transfer.volume_id,
        )

        self.volume_sdk_client.find_transfer.return_value = (
            self.volume_transfer
        )

        self.cmd = volume_transfer_request.ShowTransferRequest(self.app, None)

    def test_transfer_show(self):
        arglist = [self.volume_transfer.id]
        verifylist = [('transfer_request', self.volume_transfer.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_transfer.assert_called_once_with(
            self.volume_transfer.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
