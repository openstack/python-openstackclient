#   Copyright 2017 Huawei, Inc. All rights reserved.
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

from openstackclient.compute.v2 import server_event
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestServerEvent(compute_fakes.TestComputev2):

    fake_server = compute_fakes.FakeServer.create_one_server()

    def setUp(self):
        super(TestServerEvent, self).setUp()

        self.servers_mock = self.app.client_manager.compute.servers
        self.servers_mock.reset_mock()
        self.events_mock = self.app.client_manager.compute.instance_action
        self.events_mock.reset_mock()

        self.servers_mock.get.return_value = self.fake_server


class TestListServerEvent(TestServerEvent):

    fake_event = compute_fakes.FakeServerEvent.create_one_server_event()

    columns = (
        'Request ID',
        'Server ID',
        'Action',
        'Start Time',
    )
    data = ((
        fake_event.request_id,
        fake_event.instance_uuid,
        fake_event.action,
        fake_event.start_time,
    ), )

    long_columns = (
        'Request ID',
        'Server ID',
        'Action',
        'Start Time',
        'Message',
        'Project ID',
        'User ID',
    )
    long_data = ((
        fake_event.request_id,
        fake_event.instance_uuid,
        fake_event.action,
        fake_event.start_time,
        fake_event.message,
        fake_event.project_id,
        fake_event.user_id,
    ), )

    def setUp(self):
        super(TestListServerEvent, self).setUp()

        self.events_mock.list.return_value = [self.fake_event, ]
        self.cmd = server_event.ListServerEvent(self.app, None)

    def test_server_event_list(self):
        arglist = [
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('long', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_once_with(self.fake_server.name)
        self.events_mock.list.assert_called_once_with(self.fake_server.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_server_event_list_long(self):
        arglist = [
            '--long',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_once_with(self.fake_server.name)
        self.events_mock.list.assert_called_once_with(self.fake_server.id)

        self.assertEqual(self.long_columns, columns)
        self.assertEqual(self.long_data, tuple(data))


class TestShowServerEvent(TestServerEvent):

    fake_event = compute_fakes.FakeServerEvent.create_one_server_event()

    columns = (
        'action',
        'events',
        'instance_uuid',
        'message',
        'project_id',
        'request_id',
        'start_time',
        'user_id',
    )
    data = (
        fake_event.action,
        fake_event.events,
        fake_event.instance_uuid,
        fake_event.message,
        fake_event.project_id,
        fake_event.request_id,
        fake_event.start_time,
        fake_event.user_id,
    )

    def setUp(self):
        super(TestShowServerEvent, self).setUp()

        self.events_mock.get.return_value = self.fake_event
        self.cmd = server_event.ShowServerEvent(self.app, None)

    def test_server_event_show(self):
        arglist = [
            self.fake_server.name,
            self.fake_event.request_id,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('request_id', self.fake_event.request_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_once_with(self.fake_server.name)
        self.events_mock.get.assert_called_once_with(
            self.fake_server.id, self.fake_event.request_id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
