#   Copyright 2013 Nebula Inc.
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

from openstackclient.image.v2 import metadef_namespaces
from openstackclient.tests.unit.image.v2 import fakes as md_namespace_fakes


class TestMetadefNamespaces(md_namespace_fakes.TestMetadefNamespaces):
    def setUp(self):
        super().setUp()

        # Get shortcuts to mocked image client
        self.client = self.app.client_manager.image

        # Get shortcut to the Mocks in identity client
        self.project_mock = self.app.client_manager.identity.projects
        self.project_mock.reset_mock()
        self.domain_mock = self.app.client_manager.identity.domains
        self.domain_mock.reset_mock()


class TestMetadefNamespaceList(TestMetadefNamespaces):

    _metadef_namespace = [md_namespace_fakes.create_one_metadef_namespace()]

    columns = [
        'namespace'
    ]

    datalist = []

    def setUp(self):
        super().setUp()

        self.client.metadef_namespaces.side_effect = [
            self._metadef_namespace, []]

        # Get the command object to test
        self.client.metadef_namespaces.return_value = iter(
            self._metadef_namespace
        )
        self.cmd = metadef_namespaces.ListMetadefNameSpaces(self.app, None)
        self.datalist = self._metadef_namespace

    def test_namespace_list_no_options(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(getattr(self.datalist[0], 'namespace'),
                         next(data)[0])
