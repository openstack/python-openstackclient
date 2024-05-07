# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest.mock import call

from osc_lib import exceptions

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_message


class TestVolumeMessage(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()

        self.volume_messages_mock = self.volume_client.messages
        self.volume_messages_mock.reset_mock()


class TestVolumeMessageDelete(TestVolumeMessage):
    fake_messages = volume_fakes.create_volume_messages(count=2)

    def setUp(self):
        super().setUp()

        self.volume_messages_mock.get = volume_fakes.get_volume_messages(
            self.fake_messages,
        )
        self.volume_messages_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_message.DeleteMessage(self.app, None)

    def test_message_delete(self):
        self.set_volume_api_version('3.3')

        arglist = [
            self.fake_messages[0].id,
        ]
        verifylist = [
            ('message_ids', [self.fake_messages[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_messages_mock.delete.assert_called_with(
            self.fake_messages[0].id
        )
        self.assertIsNone(result)

    def test_message_delete_multiple_messages(self):
        self.set_volume_api_version('3.3')

        arglist = [
            self.fake_messages[0].id,
            self.fake_messages[1].id,
        ]
        verifylist = [
            ('message_ids', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for m in self.fake_messages:
            calls.append(call(m.id))
        self.volume_messages_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_message_delete_multiple_messages_with_exception(self):
        self.set_volume_api_version('3.3')

        arglist = [
            self.fake_messages[0].id,
            'invalid_message',
        ]
        verifylist = [
            ('message_ids', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.volume_messages_mock.delete.side_effect = [
            self.fake_messages[0],
            exceptions.CommandError,
        ]

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertEqual('Failed to delete 1 of 2 messages.', str(exc))

        self.volume_messages_mock.delete.assert_any_call(
            self.fake_messages[0].id
        )
        self.volume_messages_mock.delete.assert_any_call('invalid_message')

        self.assertEqual(2, self.volume_messages_mock.delete.call_count)

    def test_message_delete_pre_v33(self):
        self.set_volume_api_version('3.2')

        arglist = [
            self.fake_messages[0].id,
        ]
        verifylist = [
            ('message_ids', [self.fake_messages[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.3 or greater is required', str(exc)
        )


class TestVolumeMessageList(TestVolumeMessage):
    fake_project = identity_fakes.FakeProject.create_one_project()
    fake_messages = volume_fakes.create_volume_messages(count=3)

    columns = (
        'ID',
        'Event ID',
        'Resource Type',
        'Resource UUID',
        'Message Level',
        'User Message',
        'Request ID',
        'Created At',
        'Guaranteed Until',
    )
    data = []
    for fake_message in fake_messages:
        data.append(
            (
                fake_message.id,
                fake_message.event_id,
                fake_message.resource_type,
                fake_message.resource_uuid,
                fake_message.message_level,
                fake_message.user_message,
                fake_message.request_id,
                fake_message.created_at,
                fake_message.guaranteed_until,
            )
        )

    def setUp(self):
        super().setUp()

        self.projects_mock.get.return_value = self.fake_project
        self.volume_messages_mock.list.return_value = self.fake_messages
        # Get the command to test
        self.cmd = volume_message.ListMessages(self.app, None)

    def test_message_list(self):
        self.set_volume_api_version('3.3')

        arglist = []
        verifylist = [
            ('project', None),
            ('marker', None),
            ('limit', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'project_id': None,
        }
        self.volume_messages_mock.list.assert_called_with(
            search_opts=search_opts,
            marker=None,
            limit=None,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_message_list_with_options(self):
        self.set_volume_api_version('3.3')

        arglist = [
            '--project',
            self.fake_project.name,
            '--marker',
            self.fake_messages[0].id,
            '--limit',
            '3',
        ]
        verifylist = [
            ('project', self.fake_project.name),
            ('marker', self.fake_messages[0].id),
            ('limit', 3),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        search_opts = {
            'project_id': self.fake_project.id,
        }
        self.volume_messages_mock.list.assert_called_with(
            search_opts=search_opts,
            marker=self.fake_messages[0].id,
            limit=3,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_message_list_pre_v33(self):
        self.set_volume_api_version('3.2')

        arglist = []
        verifylist = [
            ('project', None),
            ('marker', None),
            ('limit', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.3 or greater is required', str(exc)
        )


class TestVolumeMessageShow(TestVolumeMessage):
    fake_message = volume_fakes.create_one_volume_message()

    columns = (
        'created_at',
        'event_id',
        'guaranteed_until',
        'id',
        'message_level',
        'request_id',
        'resource_type',
        'resource_uuid',
        'user_message',
    )
    data = (
        fake_message.created_at,
        fake_message.event_id,
        fake_message.guaranteed_until,
        fake_message.id,
        fake_message.message_level,
        fake_message.request_id,
        fake_message.resource_type,
        fake_message.resource_uuid,
        fake_message.user_message,
    )

    def setUp(self):
        super().setUp()

        self.volume_messages_mock.get.return_value = self.fake_message
        # Get the command object to test
        self.cmd = volume_message.ShowMessage(self.app, None)

    def test_message_show(self):
        self.set_volume_api_version('3.3')

        arglist = [self.fake_message.id]
        verifylist = [('message_id', self.fake_message.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_messages_mock.get.assert_called_with(self.fake_message.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_message_show_pre_v33(self):
        self.set_volume_api_version('3.2')

        arglist = [self.fake_message.id]
        verifylist = [('message_id', self.fake_message.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.3 or greater is required', str(exc)
        )
