# Copyright 2023 Red Hat.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstackclient.tests.functional.image import base
from tempest.lib import exceptions


class InfoTests(base.BaseImageTests):
    """Functional tests for Info commands"""

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_image_import_info(self):
        output = self.openstack('image import info', parse_output=True)
        self.assert_table_structure(output, ['Field', 'Value'])
        self.assertEqual('import-methods', output[0]['Field'])
        self.assertIsNotNone(output[0]['Value'])

    def test_image_import_info_detail(self):
        output = self.openstack(
            'image import info --detail',
            parse_output=True,
        )
        self.assert_table_structure(output, ['Field', 'Value', 'Plugins'])
        self.assertEqual('import-methods', output[0]['Field'])
        self.assertIsNotNone(output[0]['Plugins'])

    def test_image_stores_list(self):
        try:
            output = self.openstack(
                'image stores list',
                parse_output=True,
            )
        except exceptions.CommandFailed as e:
            msg = str(e.stdout or '') + str(e.stderr or '')
            if "Multi Backend support not enabled" in msg:
                self.skipTest("Multi Backend support not enabled")
            raise

        self.assertIsInstance(output, list)
        if output:
            self.assert_table_structure(
                output,
                ['ID', 'Description', 'Default'],
            )
