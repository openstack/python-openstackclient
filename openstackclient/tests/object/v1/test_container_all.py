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

from openstackclient.object.v1 import container as container_cmds
from openstackclient.tests.object.v1 import fakes as object_fakes


class TestContainerAll(object_fakes.TestObjectv1):

    def setUp(self):
        super(TestContainerAll, self).setUp()

        self.requests_mock = self.useFixture(fixture.Fixture())


class TestContainerCreate(TestContainerAll):

    def setUp(self):
        super(TestContainerCreate, self).setUp()

        # Get the command object to test
        self.cmd = container_cmds.CreateContainer(self.app, None)

    def test_object_create_container_single(self):
        self.requests_mock.register_uri(
            'PUT',
            object_fakes.ENDPOINT + '/ernie',
            headers={'x-trans-id': '314159'},
            status_code=200,
        )

        arglist = [
            'ernie',
        ]
        verifylist = [(
            'containers', ['ernie'],
        )]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('account', 'container', 'x-trans-id')
        self.assertEqual(collist, columns)
        datalist = [(
            object_fakes.ACCOUNT_ID,
            'ernie',
            '314159',
        )]
        self.assertEqual(datalist, list(data))

    def test_object_create_container_more(self):
        self.requests_mock.register_uri(
            'PUT',
            object_fakes.ENDPOINT + '/ernie',
            headers={'x-trans-id': '314159'},
            status_code=200,
        )
        self.requests_mock.register_uri(
            'PUT',
            object_fakes.ENDPOINT + '/bert',
            headers={'x-trans-id': '42'},
            status_code=200,
        )

        arglist = [
            'ernie',
            'bert',
        ]
        verifylist = [(
            'containers', ['ernie', 'bert'],
        )]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('account', 'container', 'x-trans-id')
        self.assertEqual(collist, columns)
        datalist = [
            (
                object_fakes.ACCOUNT_ID,
                'ernie',
                '314159',
            ),
            (
                object_fakes.ACCOUNT_ID,
                'bert',
                '42',
            ),
        ]
        self.assertEqual(datalist, list(data))


class TestContainerDelete(TestContainerAll):

    def setUp(self):
        super(TestContainerDelete, self).setUp()

        # Get the command object to test
        self.cmd = container_cmds.DeleteContainer(self.app, None)

    def test_object_delete_container_single(self):
        self.requests_mock.register_uri(
            'DELETE',
            object_fakes.ENDPOINT + '/ernie',
            status_code=200,
        )

        arglist = [
            'ernie',
        ]
        verifylist = [(
            'containers', ['ernie'],
        )]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Command.take_action() returns None
        ret = self.cmd.take_action(parsed_args)
        self.assertIsNone(ret)

    def test_object_delete_container_more(self):
        self.requests_mock.register_uri(
            'DELETE',
            object_fakes.ENDPOINT + '/ernie',
            status_code=200,
        )
        self.requests_mock.register_uri(
            'DELETE',
            object_fakes.ENDPOINT + '/bert',
            status_code=200,
        )

        arglist = [
            'ernie',
            'bert',
        ]
        verifylist = [(
            'containers', ['ernie', 'bert'],
        )]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Command.take_action() returns None
        ret = self.cmd.take_action(parsed_args)
        self.assertIsNone(ret)


class TestContainerList(TestContainerAll):

    def setUp(self):
        super(TestContainerList, self).setUp()

        # Get the command object to test
        self.cmd = container_cmds.ListContainer(self.app, None)

    def test_object_list_containers_no_options(self):
        return_body = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
            copy.deepcopy(object_fakes.CONTAINER_2),
        ]
        self.requests_mock.register_uri(
            'GET',
            object_fakes.ENDPOINT + '?format=json',
            json=return_body,
            status_code=200,
        )

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Lister.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = [
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
            (object_fakes.container_name_2, ),
        ]
        self.assertEqual(datalist, list(data))

    def test_object_list_containers_prefix(self):
        return_body = [
            copy.deepcopy(object_fakes.CONTAINER),
            copy.deepcopy(object_fakes.CONTAINER_3),
        ]
        self.requests_mock.register_uri(
            'GET',
            object_fakes.ENDPOINT + '?format=json&prefix=bit',
            json=return_body,
            status_code=200,
        )

        arglist = [
            '--prefix', 'bit',
        ]
        verifylist = [
            ('prefix', 'bit'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Lister.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = ('Name',)
        self.assertEqual(collist, columns)
        datalist = [
            (object_fakes.container_name, ),
            (object_fakes.container_name_3, ),
        ]
        self.assertEqual(datalist, list(data))


class TestContainerSave(TestContainerAll):

    def setUp(self):
        super(TestContainerSave, self).setUp()

        # Get the command object to test
        self.cmd = container_cmds.SaveContainer(self.app, None)

# TODO(dtroyer): need to mock out object_lib.save_object() to test this
#     def test_object_save_container(self):
#         return_body = [
#             copy.deepcopy(object_fakes.OBJECT),
#             copy.deepcopy(object_fakes.OBJECT_2),
#         ]
#         # Initial container list request
#         self.requests_mock.register_uri(
#             'GET',
#             object_fakes.ENDPOINT + '/oscar?format=json',
#             json=return_body,
#             status_code=200,
#         )
#         # Individual object save requests
#         self.requests_mock.register_uri(
#             'GET',
#             object_fakes.ENDPOINT + '/oscar/' + object_fakes.object_name_1,
#             json=object_fakes.OBJECT,
#             status_code=200,
#         )
#         self.requests_mock.register_uri(
#             'GET',
#             object_fakes.ENDPOINT + '/oscar/' + object_fakes.object_name_2,
#             json=object_fakes.OBJECT_2,
#             status_code=200,
#         )
#
#         arglist = [
#             'oscar',
#         ]
#         verifylist = [(
#             'container', 'oscar',
#         )]
#         parsed_args = self.check_parser(self.cmd, arglist, verifylist)
#
#         # Command.take_action() returns None
#         ret = self.cmd.take_action(parsed_args)
#         self.assertIsNone(ret)


class TestContainerShow(TestContainerAll):

    def setUp(self):
        super(TestContainerShow, self).setUp()

        # Get the command object to test
        self.cmd = container_cmds.ShowContainer(self.app, None)

    def test_object_show_container(self):
        headers = {
            'x-container-meta-owner': object_fakes.ACCOUNT_ID,
            'x-container-object-count': '42',
            'x-container-bytes-used': '123',
            'x-container-read': 'qaz',
            'x-container-write': 'wsx',
            'x-container-sync-to': 'edc',
            'x-container-sync-key': 'rfv',
        }
        self.requests_mock.register_uri(
            'HEAD',
            object_fakes.ENDPOINT + '/ernie',
            headers=headers,
            status_code=200,
        )

        arglist = [
            'ernie',
        ]
        verifylist = [(
            'container', 'ernie',
        )]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            'account',
            'bytes_used',
            'container',
            'object_count',
            'read_acl',
            'sync_key',
            'sync_to',
            'write_acl',
        )
        self.assertEqual(collist, columns)
        datalist = [
            object_fakes.ACCOUNT_ID,
            '123',
            'ernie',
            '42',
            'qaz',
            'rfv',
            'edc',
            'wsx',
        ]
        self.assertEqual(datalist, list(data))
