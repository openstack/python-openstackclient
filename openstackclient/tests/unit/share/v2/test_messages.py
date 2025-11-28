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

from manilaclient import api_versions
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient.share.v2 import messages
from openstackclient.tests.unit.share.v2 import fakes as share_fakes
from openstackclient.tests.unit import utils as test_utils

COLUMNS = [
    'ID',
    'Resource Type',
    'Resource ID',
    'Action ID',
    'User Message',
    'Detail ID',
    'Created At',
]


class TestMessage(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.messages_mock = self.share_client.messages
        self.messages_mock.reset_mock()

        self.set_share_api_version(api_versions.MAX_VERSION)


class TestMessageDelete(TestMessage):
    def setUp(self):
        super().setUp()

        self.message = share_fakes.FakeMessage.create_one_message()

        self.messages_mock.get.return_value = self.message

        self.cmd = messages.DeleteMessage(self.app, None)

    def test_message_delete_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_message_delete(self):
        arglist = [self.message.id]
        verifylist = [('message', [self.message.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.messages_mock.delete.assert_called_with(self.message)
        self.assertIsNone(result)

    def test_message_delete_multiple(self):
        messages = share_fakes.FakeMessage.create_messages(count=2)
        arglist = [messages[0].id, messages[1].id]
        verifylist = [('message', [messages[0].id, messages[1].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertEqual(self.messages_mock.delete.call_count, len(messages))
        self.assertIsNone(result)

    def test_message_delete_exception(self):
        arglist = [self.message.id]
        verifylist = [('message', [self.message.id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.messages_mock.delete.side_effect = exceptions.CommandError()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestMessageShow(TestMessage):
    def setUp(self):
        super().setUp()

        self.message = share_fakes.FakeMessage.create_one_message()
        self.messages_mock.get.return_value = self.message

        self.cmd = messages.ShowMessage(self.app, None)

        self.data = self.message._info.values()
        self.columns = self.message._info.keys()

    def test_message_show_missing_args(self):
        arglist = []
        verifylist = []

        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_message_show(self):
        arglist = [self.message.id]
        verifylist = [('message', self.message.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.messages_mock.get.assert_called_with(self.message.id)
        self.assertCountEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)


class TestMessageList(TestMessage):
    def setUp(self):
        super().setUp()

        self.messages = share_fakes.FakeMessage.create_messages(count=2)

        self.messages_mock.list.return_value = self.messages

        self.values = (
            oscutils.get_dict_properties(m._info, COLUMNS)
            for m in self.messages
        )

        self.cmd = messages.ListMessage(self.app, None)

    def test_list_messages(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.messages_mock.list.assert_called_with(
            search_opts={
                'limit': None,
                'request_id': None,
                'resource_type': None,
                'resource_id': None,
                'action_id': None,
                'detail_id': None,
                'message_level': None,
                'created_since': None,
                'created_before': None,
            }
        )

        self.assertEqual(COLUMNS, columns)
        self.assertEqual(list(self.values), list(data))

    def test_list_messages_api_version_exception(self):
        self.set_share_api_version('2.50')

        arglist = [
            '--before',
            '2021-02-06T09:49:58-05:00',
            '--since',
            '2021-02-05T09:49:58-05:00',
        ]
        verifylist = [
            ('before', '2021-02-06T09:49:58-05:00'),
            ('since', '2021-02-05T09:49:58-05:00'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
