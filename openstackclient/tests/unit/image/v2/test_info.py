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

from openstackclient.image.v2 import info
from openstackclient.tests.unit.image.v2 import fakes as image_fakes


class TestImportInfo(image_fakes.TestImagev2):
    import_info = image_fakes.create_one_import_info()

    def setUp(self):
        super().setUp()

        self.image_client.get_import_info.return_value = self.import_info

        self.cmd = info.ImportInfo(self.app, None)

    def test_import_info(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        self.cmd.take_action(parsed_args)

        self.image_client.get_import_info.assert_called()
