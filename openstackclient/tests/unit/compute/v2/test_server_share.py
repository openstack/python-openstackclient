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

import uuid

from osc_lib import exceptions

from openstackclient.compute.v2 import server_share
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestServerShareList(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.97')

        self.server = compute_fakes.create_one_server()
        self.shares = compute_fakes.create_shares()

        self.compute_client.find_server.return_value = self.server
        self.compute_client.share_attachments.return_value = self.shares

        self.cmd = server_share.ListServerShare(self.app, None)

    def test_server_share_list(self):
        arglist = [
            self.server.id,
        ]
        verifylist = [
            ('server', self.server.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(("Share ID", "Status", "Tag"), columns)
        self.assertEqual(
            (
                (
                    self.shares[0].share_id,
                    self.shares[0].status,
                    self.shares[0].tag,
                ),
                (
                    self.shares[1].share_id,
                    self.shares[1].status,
                    self.shares[1].tag,
                ),
            ),
            tuple(data),
        )
        self.compute_client.share_attachments.assert_called_once_with(
            self.server,
        )

    def test_server_share_list_pre_v297(self):
        self.set_compute_api_version('2.96')
        arglist = [self.server.id]
        verifylist = [('server', self.server.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestServerShareShow(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.97')

        self.server = compute_fakes.create_one_server()
        self.share = compute_fakes.create_one_share()

        self.compute_client.find_server.return_value = self.server
        self.compute_client.get_share_attachment.return_value = self.share

        self.shared_file_system_client = (
            self.app.client_manager.sdk_connection.shared_file_system
        )
        self._manila_share_id = uuid.uuid4().hex
        self.shared_file_system_client.find_share.return_value = type(
            'FakeShare', (), {'id': self._manila_share_id}
        )()

        self.cmd = server_share.ShowServerShare(self.app, None)

    def test_server_share_show(self):
        arglist = [
            self.server.id,
            self._manila_share_id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(
            ('Export Location', 'Share ID', 'Status', 'Tag', 'UUID'), columns
        )
        self.assertEqual(
            (
                self.share.export_location,
                self.share.share_id,
                self.share.status,
                self.share.tag,
                self.share.uuid,
            ),
            tuple(data),
        )
        self.shared_file_system_client.find_share.assert_called_once_with(
            self._manila_share_id, ignore_missing=False
        )
        self.compute_client.get_share_attachment.assert_called_once_with(
            self.server, self._manila_share_id
        )

    def test_server_share_show_pre_v297(self):
        self.set_compute_api_version('2.96')
        arglist = [self.server.id, self._manila_share_id]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestServerShareCreate(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.97')

        self.server = compute_fakes.create_one_server()
        self.share = compute_fakes.create_one_share()

        self.compute_client.find_server.return_value = self.server
        self.compute_client.create_share_attachment.return_value = self.share

        self.shared_file_system_client = (
            self.app.client_manager.sdk_connection.shared_file_system
        )
        self._manila_share_id = uuid.uuid4().hex
        self.shared_file_system_client.find_share.return_value = type(
            'FakeShare', (), {'id': self._manila_share_id}
        )()

        self.cmd = server_share.AddServerShare(self.app, None)

    def test_server_share_create(self):
        arglist = [
            self.server.id,
            self._manila_share_id,
            "--tag",
            "my-tag",
        ]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
            ('tag', 'my-tag'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(
            ("Export Location", "Share ID", "Status", "Tag", "UUID"), columns
        )
        self.assertEqual(
            (
                self.share.export_location,
                self.share.share_id,
                self.share.status,
                self.share.tag,
                self.share.uuid,
            ),
            tuple(data),
        )
        self.shared_file_system_client.find_share.assert_called_once_with(
            self._manila_share_id, ignore_missing=False
        )
        self.compute_client.create_share_attachment.assert_called_once_with(
            self.server, self._manila_share_id, tag='my-tag'
        )

    def test_server_share_create_no_tag(self):
        arglist = [
            self.server.id,
            self._manila_share_id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.compute_client.create_share_attachment.assert_called_once_with(
            self.server, self._manila_share_id
        )

    def test_server_share_create_pre_v297(self):
        self.set_compute_api_version('2.96')
        arglist = [self.server.id, self._manila_share_id]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )


class TestServerShareDelete(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.97')

        self.server = compute_fakes.create_one_server()

        self.compute_client.find_server.return_value = self.server

        self.shared_file_system_client = (
            self.app.client_manager.sdk_connection.shared_file_system
        )
        self._manila_share_id = uuid.uuid4().hex
        self.shared_file_system_client.find_share.return_value = type(
            'FakeShare', (), {'id': self._manila_share_id}
        )()

        self.cmd = server_share.RemoveServerShare(self.app, None)

    def test_server_share_delete(self):
        arglist = [
            self.server.id,
            self._manila_share_id,
        ]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.shared_file_system_client.find_share.assert_called_once_with(
            self._manila_share_id, ignore_missing=False
        )
        self.compute_client.delete_share_attachment.assert_called_once_with(
            self.server,
            self._manila_share_id,
        )

    def test_server_share_delete_pre_v297(self):
        self.set_compute_api_version('2.96')
        arglist = [self.server.id, self._manila_share_id]
        verifylist = [
            ('server', self.server.id),
            ('share', self._manila_share_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
