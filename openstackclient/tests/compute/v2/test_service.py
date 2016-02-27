#   Copyright 2015 Mirantis, Inc.
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

from openstackclient.compute.v2 import service
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes


class TestService(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestService, self).setUp()

        # Get a shortcut to the ServiceManager Mock
        self.service_mock = self.app.client_manager.compute.services
        self.service_mock.reset_mock()


class TestServiceDelete(TestService):

    def setUp(self):
        super(TestServiceDelete, self).setUp()

        self.service_mock.delete.return_value = None

        # Get the command object to test
        self.cmd = service.DeleteService(self.app, None)

    def test_service_delete_no_options(self):
        arglist = [
            compute_fakes.service_binary,
        ]
        verifylist = [
            ('service', compute_fakes.service_binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.delete.assert_called_with(
            compute_fakes.service_binary,
        )
        self.assertIsNone(result)


class TestServiceList(TestService):

    def setUp(self):
        super(TestServiceList, self).setUp()

        self.service_mock.list.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVICE),
            loaded=True,
        )]

        # Get the command object to test
        self.cmd = service.ListService(self.app, None)

    def test_service_list(self):
        arglist = [
            '--host', compute_fakes.service_host,
            '--service', compute_fakes.service_binary,
        ]
        verifylist = [
            ('host', compute_fakes.service_host),
            ('service', compute_fakes.service_binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        self.cmd.take_action(parsed_args)

        self.service_mock.list.assert_called_with(
            compute_fakes.service_host,
            compute_fakes.service_binary,
        )


class TestServiceSet(TestService):

    def setUp(self):
        super(TestServiceSet, self).setUp()

        self.service_mock.enable.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVICE),
            loaded=True,
        )]

        self.service_mock.disable.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(compute_fakes.SERVICE),
            loaded=True,
        )]

        self.cmd = service.SetService(self.app, None)

    def test_service_set_enable(self):
        arglist = [
            compute_fakes.service_host,
            compute_fakes.service_binary,
            '--enable',
        ]
        verifylist = [
            ('host', compute_fakes.service_host),
            ('service', compute_fakes.service_binary),
            ('enabled', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.enable.assert_called_with(
            compute_fakes.service_host,
            compute_fakes.service_binary,
        )
        self.assertIsNone(result)

    def test_service_set_disable(self):
        arglist = [
            compute_fakes.service_host,
            compute_fakes.service_binary,
            '--disable',
        ]
        verifylist = [
            ('host', compute_fakes.service_host),
            ('service', compute_fakes.service_binary),
            ('enabled', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service_mock.disable.assert_called_with(
            compute_fakes.service_host,
            compute_fakes.service_binary,
        )
        self.assertIsNone(result)
