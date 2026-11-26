# Copyright 2023 Red Hat.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_lib.cli import format_columns

from openstackclient.image.v2 import info
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestImportInfo(image_fakes.TestImagev2):
    def setUp(self):
        super().setUp()

        self.cmd = info.ImportInfo(self.app, None)

    def test_import_info(self):
        arglist = []

        import_info = image_fakes.create_one_import_info()
        self.image_client.get_import_info.return_value = import_info
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.get_import_info.assert_called_with(detail=False)
        self.assertEqual(('Field', 'Value'), columns)
        self.assertEqual(
            [
                (
                    'import-methods',
                    format_columns.ListColumn(
                        import_info.import_methods['value']
                    ),
                )
            ],
            list(data),
        )

    def test_import_info_detail(self):
        arglist = ['--detail']

        import_info_detail = image_fakes.create_one_import_info(detail=True)
        self.image_client.get_import_info.return_value = import_info_detail
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.get_import_info.assert_called_with(detail=True)
        self.assertEqual(('Field', 'Value', 'Plugins'), columns)
        rows = list(data)
        self.assertEqual(1, len(rows))
        self.assertEqual('import-methods', rows[0][0])
        self.assertEqual(
            format_columns.ListColumn(
                import_info_detail.import_methods['value']
            ),
            rows[0][1],
        )
        self.assertIsInstance(rows[0][2], info.PluginsColumn)
        self.assertEqual(import_info_detail.plugins, rows[0][2]._value)
