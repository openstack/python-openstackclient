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

from openstackclient.object.v1 import object as obj
from openstackclient.tests.unit.object.v1 import fakes as object_fakes


class TestObjectList(object_fakes.TestObjectV1):
    columns = ('Name',)
    datalist = ((object_fakes.object_name_2,),)

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = obj.ListObject(self.app, None)

    def test_object_list_objects_no_options(self):
        self.object_store_client.object_list.return_value = [
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.object_name_1,),
            (object_fakes.object_name_2,),
        )
        self.assertEqual(datalist, tuple(data))

    def test_object_list_objects_prefix(self):
        self.object_store_client.object_list.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--prefix',
            'floppy',
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('prefix', 'floppy'),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name_2,
            prefix='floppy',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_object_list_objects_delimiter(self):
        self.object_store_client.object_list.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--delimiter',
            '=',
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('delimiter', '='),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name_2,
            delimiter='=',
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_object_list_objects_marker(self):
        self.object_store_client.object_list.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--marker',
            object_fakes.object_name_2,
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('marker', object_fakes.object_name_2),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name_2,
            marker=object_fakes.object_name_2,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_object_list_objects_end_marker(self):
        self.object_store_client.object_list.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--end-marker',
            object_fakes.object_name_2,
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('end_marker', object_fakes.object_name_2),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name_2,
            end_marker=object_fakes.object_name_2,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_object_list_objects_limit(self):
        self.object_store_client.object_list.return_value = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]

        arglist = [
            '--limit',
            '2',
            object_fakes.container_name_2,
        ]
        verifylist = [
            ('limit', 2),
            ('container', object_fakes.container_name_2),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name_2,
            limit=2,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, tuple(data))

    def test_object_list_objects_long(self):
        self.object_store_client.object_list.return_value = [
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name,
        )

        collist = ('Name', 'Bytes', 'Hash', 'Content Type', 'Last Modified')
        self.assertEqual(collist, columns)
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
        self.assertEqual(datalist, tuple(data))

    def test_object_list_objects_all(self):
        self.object_store_client.object_list.return_value = [
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_list.assert_called_with(
            container=object_fakes.container_name,
            full_listing=True,
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            (object_fakes.object_name_1,),
            (object_fakes.object_name_2,),
        )
        self.assertEqual(datalist, tuple(data))


class TestObjectShow(object_fakes.TestObjectV1):
    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = obj.ShowObject(self.app, None)

    def test_object_show(self):
        self.object_store_client.object_show.return_value = copy.deepcopy(
            object_fakes.OBJECT
        )

        arglist = [
            object_fakes.container_name,
            object_fakes.object_name_1,
        ]
        verifylist = [
            ('container', object_fakes.container_name),
            ('object', object_fakes.object_name_1),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class ShowOne in cliff, abstract method take_action()
        # returns a two-part tuple with a tuple of column names and a tuple of
        # data to be shown.
        columns, data = self.cmd.take_action(parsed_args)

        self.object_store_client.object_show.assert_called_with(
            container=object_fakes.container_name,
            object=object_fakes.object_name_1,
        )

        collist = ('bytes', 'content_type', 'hash', 'last_modified', 'name')
        self.assertEqual(collist, columns)
        datalist = (
            object_fakes.object_bytes_1,
            object_fakes.object_content_type_1,
            object_fakes.object_hash_1,
            object_fakes.object_modified_1,
            object_fakes.object_name_1,
        )
        self.assertEqual(datalist, data)
