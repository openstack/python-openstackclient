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

from openstackclient.object.v1 import container
from openstackclient.tests.object.v1 import fakes as object_fakes


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.endpoint = AUTH_URL
        self.token = AUTH_TOKEN


class TestObject(object_fakes.TestObjectv1):
    def setUp(self):
        super(TestObject, self).setUp()


class TestObjectClient(TestObject):

    def test_make_client(self):
        self.assertEqual(
            self.app.client_manager.object_store.endpoint,
            AUTH_URL,
        )
        self.assertEqual(
            self.app.client_manager.object_store.token,
            AUTH_TOKEN,
        )


@mock.patch(
    'openstackclient.object.v1.container.lib_container.list_containers'
)
class TestContainerList(TestObject):

    def setUp(self):
        super(TestContainerList, self).setUp()

        # Get the command object to test
        self.cmd = container.ListContainer(self.app, None)

    def test_object_list_containers_no_options(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
            copy.deepcopy(object_fakes.CONTAINER_2),
        ]

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
            (object_fakes.container_name_2, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_containers_prefix(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--prefix', 'bit',
        ]
        verifylist = [
            ('prefix', 'bit'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'prefix': 'bit',
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_containers_marker(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--marker', object_fakes.container_name,
        ]
        verifylist = [
            ('marker', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': object_fakes.container_name,
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_containers_end_marker(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--end-marker', object_fakes.container_name_3,
        ]
        verifylist = [
            ('end_marker', object_fakes.container_name_3),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'end_marker': object_fakes.container_name_3,
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_containers_limit(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--limit', '2',
        ]
        verifylist = [
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'limit': 2,
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_containers_long(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name', 'Bytes', 'Count')
        self.assertEqual(columns, collist)
        datalist = (
            (
                object_fakes.container_name,
                object_fakes.container_bytes,
                object_fakes.container_count,
            ),
            (
                object_fakes.container_name_3,
                object_fakes.container_bytes * 3,
                object_fakes.container_count * 3,
            ),
        )
        self.assertEqual(tuple(data), datalist)

    def test_object_list_containers_all(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_2),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--all',
        ]
        verifylist = [
            ('all', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'full_listing': True,
        }
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(columns, collist)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_2, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(tuple(data), datalist)


@mock.patch(
    'openstackclient.object.v1.container.lib_container.show_container'
)
class TestContainerShow(TestObject):

    def setUp(self):
        super(TestContainerShow, self).setUp()

        # Get the command object to test
        self.cmd = container.ShowContainer(self.app, None)

    def test_container_show(self, c_mock):
        c_mock.return_value = copy.deepcopy(object_fakes.CONTAINER)

        arglist = [
            object_fakes.container_name,
        ]
        verifylist = [
            ('container', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
        }
        # lib.container.show_container(api, url, container)
        c_mock.assert_called_with(
            self.app.client_manager.session,
            AUTH_URL,
            object_fakes.container_name,
            **kwargs
        )

        collist = ('bytes', 'count', 'name')
        self.assertEqual(columns, collist)
        datalist = (
            object_fakes.container_bytes,
            object_fakes.container_count,
            object_fakes.container_name,
        )
        self.assertEqual(data, datalist)
