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

from unittest import mock

import iso8601
from novaclient import api_versions
from osc_lib import exceptions

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

    def test_server_event_list_with_changes_since(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.58')

        arglist = [
            '--changes-since', '2016-03-04T06:27:59Z',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('changes_since', '2016-03-04T06:27:59Z'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_once_with(self.fake_server.name)
        self.events_mock.list.assert_called_once_with(
            self.fake_server.id, changes_since='2016-03-04T06:27:59Z')

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    @mock.patch.object(iso8601, 'parse_date', side_effect=iso8601.ParseError)
    def test_server_event_list_with_changes_since_invalid(
        self, mock_parse_isotime,
    ):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.58')

        arglist = [
            '--changes-since', 'Invalid time value',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('changes_since', 'Invalid time value'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

        self.assertIn(
            'Invalid changes-since value:', str(ex))
        mock_parse_isotime.assert_called_once_with(
            'Invalid time value'
        )

    def test_server_event_list_with_changes_since_pre_v258(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.57')

        arglist = [
            '--changes-since', '2016-03-04T06:27:59Z',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('changes_since', '2016-03-04T06:27:59Z'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

        self.assertIn(
            '--os-compute-api-version 2.58 or greater is required', str(ex))

    def test_server_event_list_with_changes_before(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.66')

        arglist = [
            '--changes-before', '2016-03-04T06:27:59Z',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('changes_before', '2016-03-04T06:27:59Z'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.servers_mock.get.assert_called_once_with(self.fake_server.name)
        self.events_mock.list.assert_called_once_with(
            self.fake_server.id, changes_before='2016-03-04T06:27:59Z')

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    @mock.patch.object(iso8601, 'parse_date', side_effect=iso8601.ParseError)
    def test_server_event_list_with_changes_before_invalid(
        self, mock_parse_isotime,
    ):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.66')

        arglist = [
            '--changes-before', 'Invalid time value',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('changes_before', 'Invalid time value'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

        self.assertIn(
            'Invalid changes-before value:', str(ex))
        mock_parse_isotime.assert_called_once_with(
            'Invalid time value'
        )

    def test_server_event_list_with_changes_before_pre_v266(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.65')

        arglist = [
            '--changes-before', '2016-03-04T06:27:59Z',
            self.fake_server.name,
        ]
        verifylist = [
            ('server', self.fake_server.name),
            ('changes_before', '2016-03-04T06:27:59Z'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

        self.assertIn(
            '--os-compute-api-version 2.66 or greater is required', str(ex))

    def test_server_event_list_with_limit(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.58')

        arglist = [
            '--limit', '1',
            self.fake_server.name,
        ]
        verifylist = [
            ('limit', 1),
            ('server', self.fake_server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.events_mock.list.assert_called_once_with(
            self.fake_server.id, limit=1)

    def test_server_event_list_with_limit_pre_v258(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.57')

        arglist = [
            '--limit', '1',
            self.fake_server.name,
        ]
        verifylist = [
            ('limit', 1),
            ('server', self.fake_server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

        self.assertIn(
            '--os-compute-api-version 2.58 or greater is required', str(ex))

    def test_server_event_list_with_marker(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.58')

        arglist = [
            '--marker', 'test_event',
            self.fake_server.name,
        ]
        verifylist = [
            ('marker', 'test_event'),
            ('server', self.fake_server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.events_mock.list.assert_called_once_with(
            self.fake_server.id, marker='test_event')

    def test_server_event_list_with_marker_pre_v258(self):
        self.app.client_manager.compute.api_version = \
            api_versions.APIVersion('2.57')

        arglist = [
            '--marker', 'test_event',
            self.fake_server.name,
        ]
        verifylist = [
            ('marker', 'test_event'),
            ('server', self.fake_server.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)

        self.assertIn(
            '--os-compute-api-version 2.58 or greater is required', str(ex))


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
