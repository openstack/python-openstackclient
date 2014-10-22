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

from openstackclient.api import object_store_v1 as object_store
from openstackclient.object.v1 import container
from openstackclient.tests.object.v1 import fakes as object_fakes


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"


class FakeClient(object):
    def __init__(self, endpoint=None, **kwargs):
        self.endpoint = AUTH_URL
        self.token = AUTH_TOKEN


class TestContainer(object_fakes.TestObjectv1):
    def setUp(self):
        super(TestContainer, self).setUp()
        self.app.client_manager.object_store = object_store.APIv1(
            session=mock.Mock(),
            service_type="object-store",
        )
        self.api = self.app.client_manager.object_store


@mock.patch(
    'openstackclient.api.object_store_v1.APIv1.container_list'
)
class TestContainerList(TestContainer):

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
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
            (object_fakes.container_name_2, ),
        )
        self.assertEqual(datalist, tuple(data))

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
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(datalist, tuple(data))

    def test_object_list_containers_marker(self, c_mock):
        c_mock.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--marker', object_fakes.container_name,
            '--end-marker', object_fakes.container_name_3,
        ]
        verifylist = [
            ('marker', object_fakes.container_name),
            ('end_marker', object_fakes.container_name_3),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': object_fakes.container_name,
            'end_marker': object_fakes.container_name_3,
        }
        c_mock.assert_called_with(
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(datalist, tuple(data))

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
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(datalist, tuple(data))

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
            **kwargs
        )

        collist = ('Name', 'Bytes', 'Count')
        self.assertEqual(collist, columns)
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
        self.assertEqual(datalist, tuple(data))

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
            **kwargs
        )

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = (
            (object_fakes.container_name, ),
            (object_fakes.container_name_2, ),
            (object_fakes.container_name_3, ),
        )
        self.assertEqual(datalist, tuple(data))


@mock.patch(
    'openstackclient.api.object_store_v1.APIv1.container_show'
)
class TestContainerShow(TestContainer):

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
            container=object_fakes.container_name,
            **kwargs
        )

        collist = ('bytes', 'count', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            object_fakes.container_bytes,
            object_fakes.container_count,
            object_fakes.container_name,
        )
        self.assertEqual(datalist, data)
