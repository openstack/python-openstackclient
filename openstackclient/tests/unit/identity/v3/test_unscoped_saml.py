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

import copy

from openstackclient.identity.v3 import unscoped_saml
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestUnscopedSAML(identity_fakes.TestFederatedIdentity):

    def setUp(self):
        super(TestUnscopedSAML, self).setUp()

        federation_lib = self.app.client_manager.identity.federation
        self.projects_mock = federation_lib.projects
        self.projects_mock.reset_mock()
        self.domains_mock = federation_lib.domains
        self.domains_mock.reset_mock()


class TestDomainList(TestUnscopedSAML):

    def setUp(self):
        super(TestDomainList, self).setUp()

        self.domains_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.DOMAIN),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = unscoped_saml.ListAccessibleDomains(self.app, None)

    def test_accessible_domains_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.domains_mock.list.assert_called_with()

        collist = ('ID', 'Enabled', 'Name', 'Description')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.domain_id,
            True,
            identity_fakes.domain_name,
            identity_fakes.domain_description,
        ), )
        self.assertEqual(datalist, tuple(data))


class TestProjectList(TestUnscopedSAML):

    def setUp(self):
        super(TestProjectList, self).setUp()

        self.projects_mock.list.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.PROJECT),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = unscoped_saml.ListAccessibleProjects(self.app, None)

    def test_accessible_projects_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.projects_mock.list.assert_called_with()

        collist = ('ID', 'Domain ID', 'Enabled', 'Name')
        self.assertEqual(collist, columns)
        datalist = ((
            identity_fakes.project_id,
            identity_fakes.domain_id,
            True,
            identity_fakes.project_name,
        ), )
        self.assertEqual(datalist, tuple(data))
