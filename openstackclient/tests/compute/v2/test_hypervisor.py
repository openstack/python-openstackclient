#   Copyright 2016 EasyStack Corporation
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

from openstackclient.common import exceptions
from openstackclient.compute.v2 import hypervisor
from openstackclient.tests.compute.v2 import fakes as compute_fakes


class TestHypervisor(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestHypervisor, self).setUp()

        # Get a shortcut to the compute client hypervisors mock
        self.hypervisors_mock = self.app.client_manager.compute.hypervisors
        self.hypervisors_mock.reset_mock()


class TestHypervisorList(TestHypervisor):

    def setUp(self):
        super(TestHypervisorList, self).setUp()

        # Fake hypervisors to be listed up
        self.hypervisors = compute_fakes.FakeHypervisor.create_hypervisors()
        self.hypervisors_mock.list.return_value = self.hypervisors

        self.columns = (
            "ID",
            "Hypervisor Hostname"
        )
        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].hypervisor_hostname,
            ),
            (
                self.hypervisors[1].id,
                self.hypervisors[1].hypervisor_hostname,
            ),
        )

        # Get the command object to test
        self.cmd = hypervisor.ListHypervisor(self.app, None)

    def test_hypervisor_list_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstractmethod take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.hypervisors_mock.list.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_hypervisor_list_matching_option_found(self):
        arglist = [
            '--matching', self.hypervisors[0].hypervisor_hostname,
        ]
        verifylist = [
            ('matching', self.hypervisors[0].hypervisor_hostname),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake the return value of search()
        self.hypervisors_mock.search.return_value = [self.hypervisors[0]]
        self.data = (
            (
                self.hypervisors[0].id,
                self.hypervisors[0].hypervisor_hostname,
            ),
        )

        # In base command class Lister in cliff, abstractmethod take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.hypervisors_mock.search.assert_called_with(
            self.hypervisors[0].hypervisor_hostname
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

    def test_hypervisor_list_matching_option_not_found(self):
        arglist = [
            '--matching', 'xxx',
        ]
        verifylist = [
            ('matching', 'xxx'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # Fake exception raised from search()
        self.hypervisors_mock.search.side_effect = exceptions.NotFound(None)

        self.assertRaises(exceptions.NotFound,
                          self.cmd.take_action,
                          parsed_args)
