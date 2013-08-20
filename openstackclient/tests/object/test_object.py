#   Copyright 2013 OpenStack Foundation
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

import copy
import mock

from openstackclient.common import clientmanager
from openstackclient.object.v1 import object as obj
from openstackclient.tests.object import fakes as object_fakes
from openstackclient.tests import utils


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.endpoint = AUTH_URL
        self.token = AUTH_TOKEN


class TestObject(utils.TestCommand):
    def setUp(self):
        super(TestObject, self).setUp()

        api_version = {"object-store": "1"}
        self.app.client_manager = clientmanager.ClientManager(
            token=AUTH_TOKEN,
            url=AUTH_URL,
            auth_url=AUTH_URL,
            api_version=api_version,
        )


class TestObjectClient(TestObject):

    def test_make_client(self):
        self.assertEqual(self.app.client_manager.object.endpoint, AUTH_URL)
        self.assertEqual(self.app.client_manager.object.token, AUTH_TOKEN)


@mock.patch(
    'openstackclient.object.v1.object.lib_object.list_objects'
)
class TestObjectList(TestObject):

    def setUp(self):
        super(TestObjectList, self).setUp()

        # Get the command object to test
        self.cmd = obj.ListObject(self.app, None)

    def test_object_list_objects_no_options(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT),
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            object_fakes.container_name,
        ]
        verifylist = [
            ('container', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name,
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_1, ),
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_prefix(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--prefix', 'floppy',
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('prefix', 'floppy'),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'prefix': 'floppy',
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name_2,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_delimiter(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--delimiter', '=',
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('delimiter', '='),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'delimiter': '=',
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name_2,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_marker(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--marker', object_fakes.object_name_2,
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('marker', object_fakes.object_name_2),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': object_fakes.object_name_2,
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name_2,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_end_marker(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--end-marker', object_fakes.object_name_2,
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('end_marker', object_fakes.object_name_2),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'end_marker': object_fakes.object_name_2,
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name_2,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_limit(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--limit', '2',
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('limit', 2),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'limit': 2,
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name_2,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_long(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT),
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--long',
            object_fakes.container_name,
        ]
        verifylist = [
            ('long', True),
            ('container', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name,
            **kwargs
        )

        collist = ('Name', 'Bytes', 'Hash', 'Content Type', 'Last Modified')
        self.assertEqual(columns, collist)
        datalist = (
            (
                object_fakes.object_name_1,
                object_fakes.object_bytes_1,
                object_fakes.object_hash_1,
                object_fakes.object_content_type_1,
                object_fakes.object_modified_1,
            ),
            (
                object_fakes.object_name_2,
                object_fakes.object_bytes_2,
                object_fakes.object_hash_2,
                object_fakes.object_content_type_2,
                object_fakes.object_modified_2,
            ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_objects_all(self, o_mock):
        o_mock.return_value = [
            copy.deepcopy(object_fakes.OBJECT),
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--all',
            object_fakes.container_name,
        ]
        verifylist = [
            ('all', True),
            ('container', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'full_listing': True,
        }
        o_mock.assert_called_with(
            self.app.restapi,
            AUTH_URL,
            object_fakes.container_name,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.object_name_1, ),
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)
