# Copyright 2023 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import exceptions as sdk_exceptions
from osc_lib import exceptions

from openstackclient.image.v2 import metadef_properties
from openstackclient.tests.unit.image.v2 import fakes as image_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestMetadefPropertyCreate(image_fakes.TestImagev2):
    _metadef_namespace = image_fakes.create_one_metadef_namespace()
    _metadef_property = image_fakes.create_one_metadef_property()
    expected_columns = (
        'name',
        'title',
        'type',
    )
    expected_data = (
        _metadef_property.name,
        _metadef_property.title,
        _metadef_property.type,
    )

    def setUp(self):
        super().setUp()
        self.image_client.create_metadef_property.return_value = (
            self._metadef_property
        )
        self.cmd = metadef_properties.CreateMetadefProperty(self.app, None)

    def test_metadef_property_create_missing_arguments(self):
        self.assertRaises(
            tests_utils.ParserException, self.check_parser, self.cmd, [], []
        )

    def test_metadef_property_create(self):
        arglist = [
            '--name',
            'cpu_cores',
            '--schema',
            '{}',
            '--title',
            'vCPU Cores',
            '--type',
            'integer',
            self._metadef_namespace.namespace,
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_metadef_property_create_invalid_schema(self):
        arglist = [
            '--name',
            'cpu_cores',
            '--schema',
            '{invalid}',
            '--title',
            'vCPU Cores',
            '--type',
            'integer',
            self._metadef_namespace.namespace,
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestMetadefPropertyDelete(image_fakes.TestImagev2):
    def setUp(self):
        super().setUp()

        self.cmd = metadef_properties.DeleteMetadefProperty(self.app, None)

    def test_metadef_property_delete(self):
        arglist = ['namespace', 'property']
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_metadef_property_delete_missing_arguments(self):
        arglist = []
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

        arglist = ['namespace']
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            [],
        )

    def test_metadef_property_delete_exception(self):
        arglist = ['namespace', 'property']
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.delete_metadef_property.side_effect = (
            sdk_exceptions.ResourceNotFound
        )

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestMetadefPropertyList(image_fakes.TestImagev2):
    _metadef_property = [image_fakes.create_one_metadef_property()]

    columns = ['name', 'title', 'type']

    def setUp(self):
        super().setUp()

        self.image_client.metadef_properties.side_effect = [
            self._metadef_property,
            [],
        ]

        self.cmd = metadef_properties.ListMetadefProperties(self.app, None)
        self.datalist = self._metadef_property

    def test_metadef_property_list(self):
        arglist = ['my-namespace']
        parsed_args = self.check_parser(self.cmd, arglist, [])

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(getattr(self.datalist[0], 'name'), next(data)[0])


class TestMetadefPropertySet(image_fakes.TestImagev2):
    _metadef_property = image_fakes.create_one_metadef_property()

    def setUp(self):
        super().setUp()

        self.cmd = metadef_properties.SetMetadefProperty(self.app, None)
        self.image_client.get_metadef_property.return_value = (
            self._metadef_property
        )

    def test_metadef_property_set(self):
        arglist = ['--title', 'new title', 'namespace', 'property']
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

    def test_metadef_property_set_invalid_schema(self):
        arglist = [
            '--title',
            'new title',
            '--schema',
            '{invalid}',
            'namespace',
            'property',
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestMetadefPropertyShow(image_fakes.TestImagev2):
    _metadef_property = image_fakes.create_one_metadef_property()

    expected_columns = (
        'name',
        'title',
        'type',
    )
    expected_data = (
        _metadef_property.name,
        _metadef_property.title,
        _metadef_property.type,
    )

    def setUp(self):
        super().setUp()

        self.image_client.get_metadef_property.return_value = (
            self._metadef_property
        )

        self.cmd = metadef_properties.ShowMetadefProperty(self.app, None)

    def test_metadef_property_show(self):
        arglist = ['my-namespace', 'my-property']
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)
