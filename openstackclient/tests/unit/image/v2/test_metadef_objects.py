#   Copyright 2023 Red Hat
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

from osc_lib import exceptions

from openstackclient.image.v2 import metadef_objects
from openstackclient.tests.unit.image.v2 import fakes


class TestMetadefObjectsCreate(fakes.TestImagev2):
    _metadef_namespace = fakes.create_one_metadef_namespace()
    _metadef_objects = fakes.create_one_metadef_object()

    expected_columns = (
        'created_at',
        'description',
        'name',
        'namespace_name',
        'properties',
        'required',
        'updated_at',
    )
    expected_data = (
        _metadef_objects.created_at,
        _metadef_objects.description,
        _metadef_objects.name,
        _metadef_objects.namespace_name,
        _metadef_objects.properties,
        _metadef_objects.required,
        _metadef_objects.updated_at,
    )

    def setUp(self):
        super().setUp()
        self.image_client.create_metadef_object.return_value = (
            self._metadef_objects
        )
        self.cmd = metadef_objects.CreateMetadefObjects(self.app, None)

    def test_namespace_create(self):
        arglist = [
            '--namespace',
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)


class TestMetadefObjectsShow(fakes.TestImagev2):
    _metadef_namespace = fakes.create_one_metadef_namespace()
    _metadef_objects = fakes.create_one_metadef_object()

    expected_columns = (
        'created_at',
        'description',
        'name',
        'namespace_name',
        'properties',
        'required',
        'updated_at',
    )
    expected_data = (
        _metadef_objects.created_at,
        _metadef_objects.description,
        _metadef_objects.name,
        _metadef_objects.namespace_name,
        _metadef_objects.properties,
        _metadef_objects.required,
        _metadef_objects.updated_at,
    )

    def setUp(self):
        super().setUp()

        self.image_client.get_metadef_object.return_value = (
            self._metadef_objects
        )
        self.cmd = metadef_objects.ShowMetadefObjects(self.app, None)

    def test_object_show(self):
        arglist = [
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)


class TestMetadefObjectDelete(fakes.TestImagev2):
    _metadef_namespace = fakes.create_one_metadef_namespace()
    _metadef_objects = fakes.create_one_metadef_object()

    def setUp(self):
        super().setUp()

        self.image_client.delete_metadef_object.return_value = None
        self.cmd = metadef_objects.DeleteMetadefObject(self.app, None)

    def test_object_delete(self):
        arglist = [
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
        ]

        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestMetadefObjectList(fakes.TestImagev2):
    _metadef_namespace = fakes.create_one_metadef_namespace()
    _metadef_objects = [fakes.create_one_metadef_object()]
    columns = ['name', 'description']

    datalist = []

    def setUp(self):
        super().setUp()

        self.image_client.metadef_objects.side_effect = [
            self._metadef_objects,
            [],
        ]

        # Get the command object to test
        self.image_client.metadef_objects.return_value = iter(
            self._metadef_objects
        )
        self.cmd = metadef_objects.ListMetadefObjects(self.app, None)
        self.datalist = self._metadef_objects

    def test_metadef_objects_list(self):
        arglist = [self._metadef_namespace.namespace]
        parsed_args = self.check_parser(self.cmd, arglist, [])

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(getattr(self.datalist[0], 'name'), next(data)[0])


class TestMetadefObjectSet(fakes.TestImagev2):
    _metadef_namespace = fakes.create_one_metadef_namespace()
    _metadef_objects = fakes.create_one_metadef_object()
    new_metadef_object = fakes.create_one_metadef_object(
        attrs={'name': 'new_object_name'}
    )

    def setUp(self):
        super().setUp()

        self.image_client.update_metadef_object.return_value = None
        self.cmd = metadef_objects.SetMetadefObject(self.app, None)

    def test_object_set_no_options(self):
        arglist = [
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_object_set(self):
        arglist = [
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
            '--name',
            'new_object_name',
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)


class TestMetadefObjectPropertyShow(fakes.TestImagev2):
    _metadef_namespace = fakes.create_one_metadef_namespace()
    _metadef_objects = fakes.create_one_metadef_object()
    md_property = _metadef_objects['properties']['quota:cpu_quota']
    md_property['name'] = 'quota:cpu_quota'

    expected_columns = (
        'description',
        'name',
        'title',
        'type',
    )
    expected_data = (
        md_property['description'],
        md_property['name'],
        md_property['title'],
        md_property['type'],
    )

    def setUp(self):
        super().setUp()

        self.image_client.get_metadef_object.return_value = (
            self._metadef_objects
        )
        self.cmd = metadef_objects.ShowMetadefObjectProperty(self.app, None)

    def test_object_property_show(self):
        arglist = [
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
            'quota:cpu_quota',
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.expected_columns, columns)
        self.assertEqual(self.expected_data, data)

    def test_neg_object_property_show(self):
        arglist = [
            self._metadef_namespace.namespace,
            self._metadef_objects.name,
            'prop1',
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            f'Property {parsed_args.property} not found in object {parsed_args.object}.',
            str(exc),
        )
