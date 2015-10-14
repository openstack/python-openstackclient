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

from requests_mock.contrib import fixture

from openstackclient.object.v1 import object as object_cmds
from openstackclient.tests.object.v1 import fakes as object_fakes


class TestObjectAll(object_fakes.TestObjectv1):
    def setUp(self):
        super(TestObjectAll, self).setUp()

        self.requests_mock = self.useFixture(fixture.Fixture())


class TestObjectCreate(TestObjectAll):

    def setUp(self):
        super(TestObjectCreate, self).setUp()

        # Get the command object to test
        self.cmd = object_cmds.CreateObject(self.app, None)


class TestObjectList(TestObjectAll):

    def setUp(self):
        super(TestObjectList, self).setUp()

        # Get the command object to test
        self.cmd = object_cmds.ListObject(self.app, None)

    def test_object_list_objects_no_options(self):
        return_body = [
            copy.deepcopy(object_fakes.OBJECT),
            copy.deepcopy(object_fakes.OBJECT_2),
        ]
        self.requests_mock.register_uri(
            'GET',
            object_fakes.ENDPOINT +
            '/' +
            object_fakes.container_name +
            '?format=json',
            json=return_body,
            status_code=200,
        )

        arglist = [
            object_fakes.container_name,
        ]
        verifylist = [
            ('container', object_fakes.container_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Lister.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = [
            (object_fakes.object_name_1, ),
            (object_fakes.object_name_2, ),
        ]
        self.assertEqual(datalist, list(data))

    def test_object_list_objects_prefix(self):
        return_body = [
            copy.deepcopy(object_fakes.OBJECT_2),
        ]
        self.requests_mock.register_uri(
            'GET',
            object_fakes.ENDPOINT +
            '/' +
            object_fakes.container_name_2 +
            '?prefix=floppy&format=json',
            json=return_body,
            status_code=200,
        )

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

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = (
            (object_fakes.object_name_2, ),
        )
        self.assertEqual(datalist, tuple(data))


class TestObjectShow(TestObjectAll):

    def setUp(self):
        super(TestObjectShow, self).setUp()

        # Get the command object to test
        self.cmd = object_cmds.ShowObject(self.app, None)

    def test_object_show(self):
        headers = {
            'content-type': 'text/plain',
            'content-length': '20',
            'last-modified': 'yesterday',
            'etag': '4c4e39a763d58392724bccf76a58783a',
            'x-container-meta-owner': object_fakes.ACCOUNT_ID,
            'x-object-manifest': 'manifest',
        }
        self.requests_mock.register_uri(
            'HEAD',
            '/'.join([
                object_fakes.ENDPOINT,
                object_fakes.container_name,
                object_fakes.object_name_1,
            ]),
            headers=headers,
            status_code=200,
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

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            'account',
            'container',
            'content-length',
            'content-type',
            'etag',
            'last-modified',
            'object',
            'x-object-manifest',
        )
        self.assertEqual(collist, columns)
        datalist = (
            object_fakes.ACCOUNT_ID,
            object_fakes.container_name,
            '20',
            'text/plain',
            '4c4e39a763d58392724bccf76a58783a',
            'yesterday',
            object_fakes.object_name_1,
            'manifest',
        )
        self.assertEqual(datalist, data)
