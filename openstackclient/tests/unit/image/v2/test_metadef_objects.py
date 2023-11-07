#   Copyright 2012-2013 OpenStack Foundation
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
