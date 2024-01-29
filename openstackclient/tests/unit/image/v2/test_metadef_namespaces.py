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
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestMetadefNamespaceCreate(image_fakes.TestImagev2):
    _metadef_namespace = image_fakes.create_one_metadef_namespace()

    expected_columns = (
        'created_at',
        'display_name',
        'namespace',
        'owner',
        'visibility',
    )
    expected_data = (
        _metadef_namespace.created_at,
        _metadef_namespace.display_name,
        _metadef_namespace.namespace,
        _metadef_namespace.owner,
        _metadef_namespace.visibility,
    )

    def setUp(self):
        super().setUp()

        self.image_client.create_metadef_namespace.return_value = (
            self._metadef_namespace
        )
        self.cmd = metadef_namespaces.CreateMetadefNamespace(self.app, None)
        self.datalist = self._metadef_namespace

    def test_namespace_create(self):
        arglist = [self._metadef_namespace.namespace]

        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)


class TestMetadefNamespaceDelete(image_fakes.TestImagev2):
    _metadef_namespace = image_fakes.create_one_metadef_namespace()

    def setUp(self):
        super().setUp()

        self.image_client.delete_metadef_namespace.return_value = (
            self._metadef_namespace
        )
        self.cmd = metadef_namespaces.DeleteMetadefNamespace(self.app, None)
        self.datalist = self._metadef_namespace

    def test_namespace_create(self):
        arglist = [self._metadef_namespace.namespace]

        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestMetadefNamespaceList(image_fakes.TestImagev2):
    _metadef_namespace = [image_fakes.create_one_metadef_namespace()]

    columns = ['namespace']

    datalist = []

    def setUp(self):
        super().setUp()

        self.image_client.metadef_namespaces.side_effect = [
            self._metadef_namespace,
            [],
        ]

        # Get the command object to test
        self.image_client.metadef_namespaces.return_value = iter(
            self._metadef_namespace
        )
        self.cmd = metadef_namespaces.ListMetadefNamespace(self.app, None)
        self.datalist = self._metadef_namespace

    def test_namespace_list_no_options(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(getattr(self.datalist[0], 'namespace'), next(data)[0])


class TestMetadefNamespaceSet(image_fakes.TestImagev2):
    _metadef_namespace = image_fakes.create_one_metadef_namespace()

    def setUp(self):
        super().setUp()

        self.image_client.update_metadef_namespace.return_value = (
            self._metadef_namespace
        )
        self.cmd = metadef_namespaces.SetMetadefNamespace(self.app, None)
        self.datalist = self._metadef_namespace

    def test_namespace_set_no_options(self):
        arglist = [self._metadef_namespace.namespace]
        verifylist = [
            ('namespace', self._metadef_namespace.namespace),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestMetadefNamespaceShow(image_fakes.TestImagev2):
    _metadef_namespace = image_fakes.create_one_metadef_namespace()

    expected_columns = (
        'created_at',
        'display_name',
        'namespace',
        'owner',
        'visibility',
    )
    expected_data = (
        _metadef_namespace.created_at,
        _metadef_namespace.display_name,
        _metadef_namespace.namespace,
        _metadef_namespace.owner,
        _metadef_namespace.visibility,
    )

    def setUp(self):
        super().setUp()

        self.image_client.get_metadef_namespace.return_value = (
            self._metadef_namespace
        )
        self.cmd = metadef_namespaces.ShowMetadefNamespace(self.app, None)

    def test_namespace_show_no_options(self):
        arglist = [self._metadef_namespace.namespace]

        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)
