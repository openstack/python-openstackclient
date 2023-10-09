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

from openstackclient.image.v2 import metadef_properties
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


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
