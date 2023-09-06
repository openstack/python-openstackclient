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

from openstackclient.image.v2 import metadef_resource_types
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestMetadefResourceTypeList(image_fakes.TestImagev2):
    resource_types = image_fakes.create_resource_types()

    columns = ['Name']

    datalist = [(resource_type.name,) for resource_type in resource_types]

    def setUp(self):
        super().setUp()

        self.image_client.metadef_resource_types.side_effect = [
            self.resource_types,
            [],
        ]

        self.cmd = metadef_resource_types.ListMetadefResourceTypes(
            self.app, None
        )

    def test_resource_type_list_no_options(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.datalist, data)
