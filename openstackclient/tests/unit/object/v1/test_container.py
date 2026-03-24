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

from openstackclient.object.v1 import container
from openstackclient.tests.unit.object.v1 import fakes as object_fakes


class TestContainerDelete(object_fakes.TestObjectV1):
    def setUp(self):
        super().setUp()

        self.object_store_client.container_delete.return_value = None

        # Get the command object to test
        self.cmd = container.DeleteContainer(self.app, None)

    def test_container_delete(self):
        arglist = [
            object_fakes.container_name,
        ]
        verifylist = [
            ('containers', [object_fakes.container_name]),
            ('recursive', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertIsNone(self.cmd.take_action(parsed_args))

        kwargs = {}
        self.object_store_client.container_delete.assert_called_with(
            container=object_fakes.container_name, **kwargs
        )
        self.object_store_client.object_list.assert_not_called()
        self.object_store_client.object_delete.assert_not_called()

    def test_recursive_delete(self):
        self.object_store_client.object_delete.return_value = None
        self.object_store_client.object_list.return_value = [
            object_fakes.OBJECT
        ]

        arglist = [
            '--recursive',
            object_fakes.container_name,
        ]
        verifylist = [
            ('containers', [object_fakes.container_name]),
            ('recursive', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertIsNone(self.cmd.take_action(parsed_args))

        self.object_store_client.container_delete.assert_called_with(
            container=object_fakes.container_name
        )
        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name
        )
        self.object_store_client.object_delete.assert_called_with(
            container=object_fakes.container_name,
            object=object_fakes.OBJECT['name'],
        )

    def test_r_delete(self):
        self.object_store_client.object_delete.return_value = None
        self.object_store_client.object_list.return_value = [
            object_fakes.OBJECT
        ]

        arglist = [
            '-r',
            object_fakes.container_name,
        ]
        verifylist = [
            ('containers', [object_fakes.container_name]),
            ('recursive', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertIsNone(self.cmd.take_action(parsed_args))

        self.object_store_client.container_delete.assert_called_with(
            container=object_fakes.container_name
        )
        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name
        )
        self.object_store_client.object_delete.assert_called_with(
            container=object_fakes.container_name,
            object=object_fakes.OBJECT['name'],
        )


class TestContainerList(object_fakes.TestObjectV1):
    columns = ('Name',)

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = container.ListContainer(self.app, None)

    def test_object_list_containers_no_options(self):
        self.object_store_client.container_list.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
            copy.deepcopy(object_fakes.CONTAINER_2),
        ]

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_list.assert_called_with()

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.container_name,),
            (object_fakes.container_name_3,),
            (object_fakes.container_name_2,),
        )
        self.assertEqual(datalist, tuple(data))

    def test_object_list_containers_prefix(self):
        self.object_store_client.container_list.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--prefix',
            'bit',
        ]
        verifylist = [
            ('prefix', 'bit'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_list.assert_called_with(
            prefix='bit',
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.container_name,),
            (object_fakes.container_name_3,),
        )
        self.assertEqual(datalist, tuple(data))

    def test_object_list_containers_marker(self):
        self.object_store_client.container_list.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--marker',
            object_fakes.container_name,
            '--end-marker',
            object_fakes.container_name_3,
        ]
        verifylist = [
            ('marker', object_fakes.container_name),
            ('end_marker', object_fakes.container_name_3),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_list.assert_called_with(
            marker=object_fakes.container_name,
            end_marker=object_fakes.container_name_3,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.container_name,),
            (object_fakes.container_name_3,),
        )
        self.assertEqual(datalist, tuple(data))

    def test_object_list_containers_limit(self):
        self.object_store_client.container_list.return_value = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]

        arglist = [
            '--limit',
            '2',
        ]
        verifylist = [
            ('limit', 2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_list.assert_called_with(
            limit=2,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.container_name,),
            (object_fakes.container_name_3,),
        )
        self.assertEqual(datalist, tuple(data))

    def test_object_list_containers_long(self):
        self.object_store_client.container_list.return_value = [
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_list.assert_called_with()

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

    def test_object_list_containers_all(self):
        self.object_store_client.container_list.return_value = [
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_list.assert_called_with(
            full_listing=True,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.container_name,),
            (object_fakes.container_name_2,),
            (object_fakes.container_name_3,),
        )
        self.assertEqual(datalist, tuple(data))


class TestContainerShow(object_fakes.TestObjectV1):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = container.ShowContainer(self.app, None)

    def test_container_show(self):
        self.object_store_client.container_show.return_value = copy.deepcopy(
            object_fakes.CONTAINER
        )

        arglist = [
            object_fakes.container_name,
        ]
        verifylist = [
            ('container', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.container_show.assert_called_with(
            container=object_fakes.container_name,
        )

        collist = ('bytes', 'count', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            object_fakes.container_bytes,
            object_fakes.container_count,
            object_fakes.container_name,
        )
        self.assertEqual(datalist, data)
